"""
LangNet — Módulo de Modelo de Dados

Nova etapa do pipeline entre Specification e Agent-Task Spec.
Recebe uma especificação (§7 Entidades e Relacionamentos) e produz:

- data_model.yaml : descritor canônico das entidades/atributos/relações
- schema.sql       : DDL MySQL/PostgreSQL/SQLite
- models.py        : classes SQLAlchemy + Pydantic
- alembic migration: script inicial Alembic

Segue o mesmo padrão de get_llm() usado em langnetagents.py.
"""
from __future__ import annotations

import os
import json
import re
import yaml
from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI


# ────────────────────────────────────────────────────────────────────────
# LLM (reusa mesmo padrão do langnetagents.get_llm)
# ────────────────────────────────────────────────────────────────────────
_llm_cache: Dict[str, Any] = {}


def _get_llm():
    key = "datamodel"
    if key in _llm_cache:
        return _llm_cache[key]

    from crewai import LLM as CrewLLM
    provider = (os.getenv("LLM_PROVIDER") or "deepseek").lower()

    if provider == "lmstudio":
        lm_model = os.getenv("LMSTUDIO_MODEL_NAME", "openai/deepseek-r1-distill-qwen-32b")
        if lm_model and not lm_model.startswith("openai/") and "/" not in lm_model:
            lm_model = f"openai/{lm_model}"
        _llm_cache[key] = CrewLLM(
            model=lm_model,
            api_key=os.getenv("LMSTUDIO_API_KEY", "lm-studio"),
            base_url=os.getenv("LMSTUDIO_API_BASE", "http://192.168.1.115:1234/v1"),
            temperature=0.2,
            max_tokens=int(os.getenv("LMSTUDIO_MAX_TOKENS", "16000")),
        )
        return _llm_cache[key]

    # Default: DeepSeek cloud
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY não configurada.")

    model = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-v4-flash")
    if not model.startswith("deepseek/"):
        model = f"deepseek/{model}"

    _llm_cache[key] = CrewLLM(
        model=model,
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
        temperature=0.2,
        max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "32768")),
        extra_body={"reasoning": {"enabled": False}},
    )
    return _llm_cache[key]


# ────────────────────────────────────────────────────────────────────────
# Prompts
# ────────────────────────────────────────────────────────────────────────
_EXTRACT_ENTITIES_PROMPT = """Você é um arquiteto de dados sênior.

Sua tarefa é ler o documento de ESPECIFICAÇÃO abaixo e extrair TODAS as entidades
de negócio e seus relacionamentos, produzindo um modelo conceitual completo.

Regras:
1. Extraia SOMENTE entidades explicitamente mencionadas ou fortemente implícitas.
2. Cada entidade deve ter atributos com tipo semântico (string/int/date/uuid/enum/etc).
3. Identifique chaves primárias (PK) e chaves estrangeiras (FK).
4. Documente relacionamentos: 1:1, 1:N, N:M com nome da relação.
5. Não invente entidades que não estão na spec.
6. Se a spec mencionar tabela específica, use esse nome.

ESPECIFICAÇÃO:
------
{specification_document}
------

Retorne SOMENTE um JSON válido no formato:
{{
  "entities": [
    {{
      "name": "leads",
      "description": "Leads captados pelo sistema",
      "attributes": [
        {{"name": "id", "type": "uuid", "pk": true, "nullable": false, "description": "..."}},
        {{"name": "nome", "type": "varchar(200)", "nullable": false}},
        {{"name": "score", "type": "integer", "nullable": false, "default": 0}}
      ]
    }}
  ],
  "relationships": [
    {{"from": "interacoes", "to": "leads", "cardinality": "N:1", "fk_column": "lead_id", "on_delete": "CASCADE"}}
  ]
}}
"""

_NORMALIZE_SCHEMA_PROMPT = """Você é um arquiteto de dados especialista em normalização (3FN).

Receba o modelo conceitual abaixo e produza um modelo LÓGICO normalizado até 3FN:
- Elimine dependências parciais e transitivas
- Introduza tabelas de associação para relações N:M
- Adicione colunas técnicas (id UUID PK, created_at, updated_at) em todas as tabelas
- Sugira índices para: FKs, colunas usadas em filtros comuns, colunas únicas
- Marque colunas ENUM com valores possíveis explícitos

MODELO CONCEITUAL:
------
{conceptual_model_json}
------

Retorne SOMENTE um JSON válido no formato:
{{
  "tables": [
    {{
      "name": "leads",
      "description": "...",
      "columns": [
        {{"name": "id", "type": "UUID", "pk": true, "nullable": false, "default": "uuid_generate_v4()"}},
        {{"name": "nome", "type": "VARCHAR(200)", "nullable": false}},
        {{"name": "status", "type": "ENUM", "values": ["novo","qualificado","contatado","descartado"], "nullable": false, "default": "'novo'"}},
        {{"name": "created_at", "type": "TIMESTAMP", "nullable": false, "default": "CURRENT_TIMESTAMP"}}
      ],
      "indexes": [
        {{"name": "idx_leads_email", "columns": ["email"], "unique": true}}
      ]
    }}
  ],
  "foreign_keys": [
    {{"table": "interacoes", "column": "lead_id", "references": "leads(id)", "on_delete": "CASCADE"}}
  ]
}}
"""

_GENERATE_DDL_PROMPT = """Você é um DBA {dbms} experiente.

Receba o modelo lógico abaixo e produza o SQL DDL completo para {dbms}, incluindo:
1. Criação de todas as tabelas com colunas, tipos NATIVOS do {dbms}, constraints
2. Chaves primárias e estrangeiras
3. Índices (inclusive únicos)
4. Comentários (COMMENT ON) quando útil
5. Sequences/UUID conforme o {dbms} suporta

MODELO LÓGICO:
------
{logical_model_json}
------

Retorne SOMENTE o SQL, sem explicações. Comece direto com CREATE TABLE ..."""


_GENERATE_MODELS_PY_PROMPT = """Gere um arquivo Python `models.py` com:

1. Classes SQLAlchemy 2.0+ (DeclarativeBase, Mapped, mapped_column) para cada tabela
2. Classes Pydantic (BaseModel) equivalentes para input/output em APIs
3. Configuração de metadata da Base
4. Imports necessários no topo

MODELO LÓGICO:
------
{logical_model_json}
------

Retorne SOMENTE o código Python, sem comentários de bloco extras nem markdown.
Comece com `from sqlalchemy...`."""


_GENERATE_ALEMBIC_PROMPT = """Gere um script Alembic de migração INICIAL (`0001_initial.py`)
correspondente ao modelo lógico abaixo. Use `op.create_table`, `op.create_index`,
`op.create_foreign_key` conforme necessário.

O script deve ter:
- revision = "0001_initial"
- down_revision = None
- Função upgrade() que cria todas as tabelas na ordem correta (respeitando FKs)
- Função downgrade() que dropa todas na ordem inversa

MODELO LÓGICO:
------
{logical_model_json}
------

Retorne SOMENTE o código Python do arquivo de migração."""


_VALIDATE_QUALITY_PROMPT = """Você é um auditor de banco de dados.

Analise o SCHEMA SQL abaixo e o relatório desejado abaixo dele. Retorne um JSON
com problemas encontrados classificados por severidade.

SCHEMA:
------
{schema_sql}
------

Verifique:
1. Todas as FKs têm índice na coluna
2. Colunas de busca/filtro têm índice
3. Nomes seguem convenção snake_case
4. Todas as tabelas têm PK
5. Tipos são apropriados (VARCHAR com tamanho, DECIMAL com escala)
6. Constraints NOT NULL onde necessário

Retorne SOMENTE JSON:
{{
  "score": 0-100,
  "issues": [
    {{"severity": "high|medium|low", "table": "leads", "issue": "FK 'user_id' sem índice"}}
  ],
  "suggestions": ["..."]
}}"""


# ────────────────────────────────────────────────────────────────────────
# Utilities
# ────────────────────────────────────────────────────────────────────────
def _strip_code_fence(text: str) -> str:
    """Remove fences de código markdown ```json ... ``` etc."""
    if not text:
        return ""
    t = text.strip()
    m = re.match(r"^```(?:json|yaml|sql|python|py)?\s*\n(.*)\n```\s*$", t, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return t


def _safe_json_parse(text: str) -> Any:
    """Tolera prefixos/sufixos em torno do JSON."""
    if not text:
        return None
    t = _strip_code_fence(text)
    # tenta direto
    try:
        return json.loads(t)
    except Exception:
        pass
    # tenta extrair o primeiro bloco {...} ou [...]
    first = min([i for i in [t.find("{"), t.find("[")] if i >= 0], default=-1)
    if first >= 0:
        last = max(t.rfind("}"), t.rfind("]"))
        if last > first:
            try:
                return json.loads(t[first:last + 1])
            except Exception:
                pass
    return None


def _call_llm(prompt: str, temperature: float = 0.2) -> str:
    """Chamada síncrona à LLM (CrewAI LLM)."""
    llm = _get_llm()
    try:
        return llm.call([{"role": "user", "content": prompt}])
    except Exception:
        # fallback pra chamada mais simples
        return llm.call(prompt)


# ────────────────────────────────────────────────────────────────────────
# Pipeline steps
# ────────────────────────────────────────────────────────────────────────
def extract_entities(specification_document: str) -> Dict[str, Any]:
    """Passo 1: extrai entidades do texto da specification."""
    prompt = _EXTRACT_ENTITIES_PROMPT.format(specification_document=specification_document[:60000])
    raw = _call_llm(prompt)
    parsed = _safe_json_parse(raw)
    if not parsed or "entities" not in parsed:
        raise RuntimeError(f"Extração de entidades falhou. Resposta bruta:\n{raw[:500]}")
    return parsed


def normalize_schema(conceptual_model: Dict[str, Any]) -> Dict[str, Any]:
    """Passo 2: normaliza para 3FN e adiciona colunas técnicas + índices."""
    prompt = _NORMALIZE_SCHEMA_PROMPT.format(conceptual_model_json=json.dumps(conceptual_model, ensure_ascii=False, indent=2))
    raw = _call_llm(prompt)
    parsed = _safe_json_parse(raw)
    if not parsed or "tables" not in parsed:
        raise RuntimeError(f"Normalização falhou. Resposta bruta:\n{raw[:500]}")
    return parsed


def generate_ddl(logical_model: Dict[str, Any], dbms: str = "mysql") -> str:
    """Passo 3: gera SQL DDL do dialeto escolhido."""
    prompt = _GENERATE_DDL_PROMPT.format(
        dbms=dbms,
        logical_model_json=json.dumps(logical_model, ensure_ascii=False, indent=2),
    )
    raw = _call_llm(prompt)
    return _strip_code_fence(raw)


def generate_models_py(logical_model: Dict[str, Any]) -> str:
    """Passo 4: gera arquivo models.py com SQLAlchemy + Pydantic."""
    prompt = _GENERATE_MODELS_PY_PROMPT.format(
        logical_model_json=json.dumps(logical_model, ensure_ascii=False, indent=2),
    )
    raw = _call_llm(prompt)
    return _strip_code_fence(raw)


def generate_alembic_migration(logical_model: Dict[str, Any]) -> str:
    """Passo 5: gera 0001_initial.py do Alembic."""
    prompt = _GENERATE_ALEMBIC_PROMPT.format(
        logical_model_json=json.dumps(logical_model, ensure_ascii=False, indent=2),
    )
    raw = _call_llm(prompt)
    return _strip_code_fence(raw)


def validate_quality(schema_sql: str) -> Dict[str, Any]:
    """Passo 6: valida qualidade do schema."""
    prompt = _VALIDATE_QUALITY_PROMPT.format(schema_sql=schema_sql[:40000])
    raw = _call_llm(prompt)
    parsed = _safe_json_parse(raw) or {"score": 0, "issues": [], "suggestions": []}
    return parsed


def build_yaml_descriptor(logical_model: Dict[str, Any], dbms: str) -> str:
    """Monta o YAML canônico consumido pelo code-gen downstream."""
    doc = {
        "version": 1,
        "dbms": dbms,
        "tables": logical_model.get("tables", []),
        "foreign_keys": logical_model.get("foreign_keys", []),
    }
    return yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, default_flow_style=False)


# ────────────────────────────────────────────────────────────────────────
# Workflow orquestrador principal
# ────────────────────────────────────────────────────────────────────────
def execute_data_model_workflow(
    specification_document: str,
    target_dbms: str = "mysql",
    progress_cb=None,
) -> Dict[str, Any]:
    """Executa o pipeline completo de Data Model.

    Args:
        specification_document: texto do doc de especificação (final_output)
        target_dbms: mysql | postgresql | sqlite
        progress_cb: callable opcional (step_name, percent) para feedback

    Returns:
        dict com data_model_yaml, schema_sql, models_py, alembic_migration,
        entities_json, validation_report
    """
    def _tick(step, pct):
        if progress_cb:
            try:
                progress_cb(step, pct)
            except Exception:
                pass

    _tick("extract_entities", 5)
    conceptual = extract_entities(specification_document)

    _tick("normalize_schema", 25)
    logical = normalize_schema(conceptual)

    _tick("generate_ddl", 50)
    schema_sql = generate_ddl(logical, dbms=target_dbms)

    _tick("generate_models_py", 65)
    models_py = generate_models_py(logical)

    _tick("generate_alembic", 80)
    alembic = generate_alembic_migration(logical)

    _tick("validate_quality", 92)
    validation = validate_quality(schema_sql)

    _tick("build_descriptor", 97)
    data_model_yaml = build_yaml_descriptor(logical, target_dbms)

    _tick("done", 100)

    return {
        "data_model_yaml": data_model_yaml,
        "schema_sql": schema_sql,
        "models_py": models_py,
        "alembic_migration": alembic,
        "entities_json": json.dumps(logical, ensure_ascii=False, indent=2),
        "conceptual_json": json.dumps(conceptual, ensure_ascii=False, indent=2),
        "validation_report": json.dumps(validation, ensure_ascii=False, indent=2),
        "target_dbms": target_dbms,
    }


def refine_data_model(
    current_yaml: str,
    user_message: str,
    target_dbms: str = "mysql",
) -> Dict[str, Any]:
    """Refina um Data Model existente com base em pedido do usuário via chat."""
    prompt = f"""Você é um arquiteto de dados. O usuário tem o seguinte Data Model
(em YAML) e quer aplicar a modificação abaixo. Retorne o YAML COMPLETO atualizado,
sem explicações.

DATA MODEL ATUAL:
```yaml
{current_yaml}
```

PEDIDO DO USUÁRIO:
{user_message}

Retorne SOMENTE o YAML final."""
    raw = _call_llm(prompt)
    new_yaml = _strip_code_fence(raw)

    # Regenera artefatos a partir do YAML novo
    try:
        parsed = yaml.safe_load(new_yaml)
        logical = {"tables": parsed.get("tables", []), "foreign_keys": parsed.get("foreign_keys", [])}
        schema_sql_new = generate_ddl(logical, dbms=target_dbms)
        validation = validate_quality(schema_sql_new)
        return {
            "data_model_yaml": new_yaml,
            "schema_sql": schema_sql_new,
            "models_py": generate_models_py(logical),
            "alembic_migration": generate_alembic_migration(logical),
            "entities_json": json.dumps(logical, ensure_ascii=False, indent=2),
            "validation_report": json.dumps(validation, ensure_ascii=False, indent=2),
            "target_dbms": target_dbms,
        }
    except Exception as e:
        raise RuntimeError(f"YAML refinado inválido: {e}")
