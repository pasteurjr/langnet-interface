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
7. 🔴 CONSISTÊNCIA DE NOMES (crítico p/ as etapas seguintes): use EXATAMENTE os nomes de
   entidades e de campos que aparecem na spec — na seção de Modelo de Dados (§6) E nos
   CAMPOS DOS WIREFRAMES dos casos de uso (ex.: se um wireframe tem o campo "Segmento",
   a coluna deve ser "segmento"). NÃO renomeie, traduza nem pluralize de forma diferente
   da spec. As telas do protótipo ligam seus campos a estas colunas pelo nome — nomes
   divergentes quebram esse vínculo. Prefira os nomes já usados na spec ao inventar sinônimos.
8. 🔴 RESULTADOS AGÊNTICOS = COLUNAS DEDICADAS (crítico p/ persistir o raciocínio): quando
   uma entidade ACUMULA os resultados de passos/tarefas agênticas distintas (ex.: um
   prontuário/ficha/registro que recebe a triagem, depois o pré-diagnóstico, depois o
   encaminhamento), cada atributo raciocinado deve ser sua PRÓPRIA coluna tipada, com o
   nome do atributo tal como a spec o descreve (ex.: `nivel_urgencia` ENUM, `diagnostico_inicial`
   TEXT, `especialidade_encaminhada` VARCHAR, `data_triagem` DATETIME). NÃO colapse esses
   atributos distintos num único campo-texto genérico (`detalhes`, `observacoes`, `dados`),
   pois isso impede consultar/atualizar cada resultado por nome e faz um passo sobrescrever
   o outro. Um campo-texto livre pode COEXISTIR, mas apenas para narrativa/observações
   adicionais — nunca como o único destino dos resultados estruturados. Cada campo que a
   spec diz ser "produzido/preenchido pelo agente X" na entidade Y ⇒ uma coluna em Y.

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
- 🔴 TODA coluna de data/hora de CRIAÇÃO (ex.: `data_criacao`, `data_registro`, `data_cadastro`,
  `created_at`) deve ter `"default": "CURRENT_TIMESTAMP"`. Uma coluna de criação NOT NULL SEM
  default quebra qualquer INSERT que a omita (erro "Field doesn't have a default value") — o que
  acontece nos INSERTs parciais/UPSERT das tasks. Se for NOT NULL, é OBRIGATÓRIO ter default.
- 🔴 PRESERVE colunas dedicadas de resultados agênticos: se o modelo conceitual traz colunas
  distintas para atributos raciocinados por passos diferentes (ex.: `nivel_urgencia`,
  `diagnostico_inicial`, `especialidade_encaminhada`), MANTENHA-AS como colunas separadas.
  NÃO as funda num único campo-texto genérico em nome da normalização — são atributos
  semânticos distintos da mesma entidade (não violam 3FN). Marque como ENUM as que tiverem
  domínio fechado (ex.: `nivel_urgencia` = baixa|media|alta|critica).

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
    # LM Studio local: chamada DIRETA em streaming (evita o estol do litellm do CrewAI
    # em respostas longas — mesmo fix do executor principal e do LLMClient).
    import os as _os
    if (_os.getenv("LLM_PROVIDER", "openai") or "").lower() == "lmstudio":
        from agents.langnetagents import _direct_llm_complete
        return _direct_llm_complete(prompt)
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


def _sql_type(col: Dict[str, Any], dbms: str = "mysql") -> str:
    """Mapeia o tipo lógico -> tipo nativo do dbms (determinístico)."""
    t = (col.get("type") or "VARCHAR(255)").strip()
    tu = t.upper()
    if tu == "UUID":
        return "CHAR(36)"
    if tu.startswith("ENUM"):
        vals = col.get("values") or []
        if not vals:  # ENUM sem valores -> vira VARCHAR (evita SQL inválido)
            return "VARCHAR(50)"
        return "ENUM(" + ", ".join("'%s'" % str(v).replace("'", "''") for v in vals) + ")"
    if tu in ("SERIAL", "BIGSERIAL"):
        return "BIGINT AUTO_INCREMENT"
    if tu == "BOOLEAN":
        return "TINYINT(1)"
    if tu in ("JSONB",):
        return "JSON"
    return t


def _default_clause(col: Dict[str, Any]) -> str:
    """Cláusula DEFAULT determinística. Colunas de data de CRIAÇÃO NOT NULL sem
    default ganham CURRENT_TIMESTAMP (senão INSERTs parciais quebram)."""
    d = col.get("default")
    name = (col.get("name") or "").lower()
    typ = (col.get("type") or "").upper()
    is_creation_ts = typ in ("TIMESTAMP", "DATETIME") and any(
        k in name for k in ("criacao", "cadastro", "registro", "created_at", "data_hora"))
    if d is None or (isinstance(d, str) and not d.strip()):
        if not col.get("nullable", True) and is_creation_ts:
            return " DEFAULT CURRENT_TIMESTAMP"
        return ""
    d = str(d).strip()
    if d in ("uuid_generate_v4()", "gen_random_uuid()", "(UUID())", "UUID()"):
        return " DEFAULT (UUID())"
    if d.upper() in ("CURRENT_TIMESTAMP", "NOW()"):
        return " DEFAULT CURRENT_TIMESTAMP"
    if d.startswith("'") and d.endswith("'"):
        return " DEFAULT " + d
    if d.replace(".", "", 1).lstrip("-").isdigit():
        return " DEFAULT " + d
    return " DEFAULT '%s'" % d.replace("'", "''")


def _topo_sort_tables(tables: List[Dict], fks: List[Dict]) -> List[str]:
    """Ordena as tabelas por dependência de FK: referenciada ANTES de quem referencia.
    Evita 'errno 150' quando uma FK aponta para tabela definida mais abaixo."""
    names = [t["name"] for t in tables]
    nameset = set(names)
    def _ref(fk):
        r = (fk.get("references") or "")
        return (r.split("(")[0].strip().strip('`"') if "(" in r else r.strip())
    deps: Dict[str, set] = {n: set() for n in names}
    for fk in fks:
        tbl = fk.get("table"); rt = _ref(fk)
        if tbl in deps and rt in nameset and rt != tbl:
            deps[tbl].add(rt)
    ordered: List[str] = []
    seen: set = set()
    def visit(n, stack):
        if n in seen or n in stack:
            return
        for d in sorted(deps.get(n, ())):
            visit(d, stack | {n})
        seen.add(n); ordered.append(n)
    for n in names:
        visit(n, set())
    return ordered


def _emit_ddl_deterministic(logical_model: Dict[str, Any], dbms: str = "mysql") -> str:
    """Emissor de DDL DETERMINÍSTICO (sem LLM). O LLM decide o modelo (entidades/colunas/
    FKs); ESTE código escreve o SQL — sempre com sintaxe válida: COMMENT depois do ')',
    tabelas ordenadas por dependência de FK (+ SET FOREIGN_KEY_CHECKS=0 como cinto), ENUM
    com os valores exatos do modelo, e default de data de criação. Elimina a variância do
    LLM (COMMENT/ordem/ENUM) que quebrava o deploy."""
    tables = logical_model.get("tables") or []
    fks = logical_model.get("foreign_keys") or []
    if not tables:
        raise ValueError("modelo lógico sem tabelas")
    by_name = {t["name"]: t for t in tables}
    fks_by_table: Dict[str, List[Dict]] = {}
    for fk in fks:
        fks_by_table.setdefault(fk.get("table"), []).append(fk)
    order = _topo_sort_tables(tables, fks)

    out: List[str] = ["SET FOREIGN_KEY_CHECKS=0;", ""]
    for name in order:
        t = by_name[name]
        body: List[str] = []
        for col in t.get("columns", []):
            cn = col["name"]
            typ = _sql_type(col, dbms)
            deff = _default_clause(col)
            if col.get("pk"):
                line = "    `%s` %s PRIMARY KEY%s" % (cn, typ, deff)
            else:
                notnull = "" if col.get("nullable", True) else " NOT NULL"
                on_update = ""
                if cn.lower() in ("updated_at", "atualizado_em") and typ.upper() in ("TIMESTAMP", "DATETIME"):
                    if "DEFAULT" not in deff:
                        deff = " DEFAULT CURRENT_TIMESTAMP"
                    on_update = " ON UPDATE CURRENT_TIMESTAMP"
                line = "    `%s` %s%s%s%s" % (cn, typ, notnull, deff, on_update)
            body.append(line)
        # índices
        for idx in (t.get("indexes") or []):
            cols = ", ".join("`%s`" % c for c in (idx.get("columns") or []))
            if not cols:
                continue
            uniq = "UNIQUE " if idx.get("unique") else ""
            iname = idx.get("name") or ("idx_%s_%s" % (name.lower(), "_".join(idx.get("columns") or [])))
            body.append("    %sINDEX `%s` (%s)" % (uniq, iname, cols))
        # foreign keys
        for fk in fks_by_table.get(name, []):
            ref = fk.get("references") or ""
            col = fk.get("column")
            if not col or "(" not in ref:
                continue
            on_del = (fk.get("on_delete") or "").upper()
            on_clause = (" ON DELETE %s" % on_del) if on_del in ("CASCADE", "SET NULL", "RESTRICT", "NO ACTION") else ""
            body.append("    FOREIGN KEY (`%s`) REFERENCES %s%s" % (col, ref, on_clause))
        # COMMENT SEMPRE depois do ')'
        desc = (t.get("description") or "").replace("'", "''")
        comment = (" COMMENT='%s'" % desc) if desc else ""
        out.append("CREATE TABLE `%s` (\n%s\n)%s;" % (name, ",\n".join(body), comment))
        out.append("")
    out.append("SET FOREIGN_KEY_CHECKS=1;")
    return "\n".join(out) + "\n"


def generate_ddl(logical_model: Dict[str, Any], dbms: str = "mysql") -> str:
    """Passo 3: gera SQL DDL. DETERMINÍSTICO (sem LLM) a partir do modelo lógico —
    sintaxe sempre válida. Só cai no LLM se o modelo estiver inutilizável."""
    try:
        return _emit_ddl_deterministic(logical_model, dbms=dbms)
    except Exception as _e:
        print(f"[DATA-MODEL] emissor determinístico falhou ({_e}); fallback LLM")
        prompt = _GENERATE_DDL_PROMPT.format(
            dbms=dbms,
            logical_model_json=json.dumps(logical_model, ensure_ascii=False, indent=2),
        )
        raw = _call_llm(prompt)
        return _strip_code_fence(raw)


def _class_name(table: str) -> str:
    """PACIENTE / paciente_agente -> Paciente / PacienteAgente (CamelCase)."""
    return "".join(p.capitalize() for p in re.split(r"[_\s]+", table.lower()) if p) or "Tabela"


def _sa_type(col: Dict[str, Any]) -> str:
    t = (col.get("type") or "String").upper()
    if t == "UUID":
        return "String(36)"
    m = re.match(r"VARCHAR\((\d+)\)", t)
    if m:
        return "String(%s)" % m.group(1)
    if t in ("TEXT", "LONGTEXT", "MEDIUMTEXT"):
        return "Text"
    if t in ("INTEGER", "INT", "BIGINT", "SMALLINT", "SERIAL", "BIGSERIAL"):
        return "Integer"
    if t in ("TIMESTAMP", "DATETIME"):
        return "DateTime"
    if t == "DATE":
        return "Date"
    if t == "BOOLEAN":
        return "Boolean"
    if t.startswith("DECIMAL") or t.startswith("NUMERIC") or t.startswith("FLOAT") or t.startswith("DOUBLE"):
        return "Numeric"
    if t.startswith("ENUM"):
        vals = col.get("values") or []
        return ("SAEnum(%s)" % ", ".join(repr(str(v)) for v in vals)) if vals else "String(50)"
    if t in ("JSON", "JSONB"):
        return "JSON"
    return "String(255)"


_PY_TYPE = {"String": "str", "Text": "str", "Integer": "int", "DateTime": "datetime",
            "Date": "date", "Boolean": "bool", "Numeric": "float", "JSON": "dict", "SAEnum": "str"}


def _emit_models_py_deterministic(logical_model: Dict[str, Any]) -> str:
    """models.py DETERMINÍSTICO: SQLAlchemy 2.0 (DeclarativeBase/Mapped) + Pydantic,
    a partir do modelo lógico. Sem LLM."""
    tables = logical_model.get("tables") or []
    fks = logical_model.get("foreign_keys") or []
    fk_map: Dict[tuple, str] = {}
    for fk in fks:
        ref = fk.get("references") or ""
        if fk.get("table") and fk.get("column") and "(" in ref:
            fk_map[(fk["table"], fk["column"])] = ref
    lines = [
        '"""models.py — gerado deterministicamente pelo LangNet (SQLAlchemy 2.0 + Pydantic)."""',
        "from __future__ import annotations",
        "from datetime import datetime, date",
        "from typing import Optional",
        "from sqlalchemy import String, Text, Integer, DateTime, Date, Boolean, Numeric, JSON, ForeignKey",
        "from sqlalchemy import Enum as SAEnum",
        "from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column",
        "from pydantic import BaseModel",
        "",
        "class Base(DeclarativeBase):",
        "    pass",
        "",
    ]
    for t in tables:
        cls = _class_name(t["name"])
        lines.append("class %s(Base):" % cls)
        lines.append("    __tablename__ = %r" % t["name"])
        for col in t.get("columns", []):
            cn = col["name"]
            sat = _sa_type(col)
            pyt = _PY_TYPE.get(sat.split("(")[0], "str")
            args = [sat]
            fkref = fk_map.get((t["name"], cn))
            if fkref:
                args.append("ForeignKey(%r)" % fkref)
            if col.get("pk"):
                args.append("primary_key=True")
            nullable = col.get("nullable", True)
            args.append("nullable=%s" % ("True" if nullable else "False"))
            mapped = ("Optional[%s]" % pyt) if nullable and not col.get("pk") else pyt
            lines.append("    %s: Mapped[%s] = mapped_column(%s)" % (cn, mapped, ", ".join(args)))
        lines.append("")
    # Pydantic schemas
    for t in tables:
        cls = _class_name(t["name"])
        lines.append("class %sSchema(BaseModel):" % cls)
        for col in t.get("columns", []):
            pyt = _PY_TYPE.get(_sa_type(col).split("(")[0], "str")
            opt = col.get("nullable", True) and not col.get("pk")
            lines.append("    %s: %s = None" % (col["name"], "Optional[%s]" % pyt) if opt else "    %s: %s" % (col["name"], pyt))
        lines.append("    class Config:")
        lines.append("        from_attributes = True")
        lines.append("")
    return "\n".join(lines) + "\n"


def generate_models_py(logical_model: Dict[str, Any]) -> str:
    """Passo 4: models.py. DETERMINÍSTICO (sem LLM); LLM só como fallback."""
    try:
        return _emit_models_py_deterministic(logical_model)
    except Exception as _e:
        print(f"[DATA-MODEL] models.py determinístico falhou ({_e}); fallback LLM")
        raw = _call_llm(_GENERATE_MODELS_PY_PROMPT.format(
            logical_model_json=json.dumps(logical_model, ensure_ascii=False, indent=2)))
        return _strip_code_fence(raw)


def _emit_alembic_deterministic(logical_model: Dict[str, Any]) -> str:
    """0001_initial.py DETERMINÍSTICO: op.create_table na ordem topológica de FK,
    downgrade dropa na ordem inversa. Sem LLM."""
    tables = logical_model.get("tables") or []
    fks = logical_model.get("foreign_keys") or []
    by_name = {t["name"]: t for t in tables}
    order = _topo_sort_tables(tables, fks)
    fk_map: Dict[tuple, str] = {}
    for fk in fks:
        ref = fk.get("references") or ""
        if fk.get("table") and fk.get("column") and "(" in ref:
            fk_map[(fk["table"], fk["column"])] = ref

    def _op_type(col):
        sat = _sa_type(col)
        base = sat.split("(")[0]
        m = {"String": "sa.String", "Text": "sa.Text", "Integer": "sa.Integer",
             "DateTime": "sa.DateTime", "Date": "sa.Date", "Boolean": "sa.Boolean",
             "Numeric": "sa.Numeric", "JSON": "sa.JSON", "SAEnum": "sa.String"}
        if base == "String" and "(" in sat:
            return "sa.String(length=%s)" % sat.split("(")[1].rstrip(")")
        if base == "SAEnum":
            return "sa.String(length=50)"
        return m.get(base, "sa.String(length=255)")

    lines = [
        '"""0001_initial — gerado deterministicamente pelo LangNet."""',
        "from alembic import op",
        "import sqlalchemy as sa",
        "",
        'revision = "0001_initial"',
        "down_revision = None",
        "branch_labels = None",
        "depends_on = None",
        "",
        "def upgrade():",
    ]
    for name in order:
        t = by_name[name]
        lines.append("    op.create_table(")
        lines.append("        %r," % name)
        for col in t.get("columns", []):
            cn = col["name"]
            colargs = ["%r" % cn, _op_type(col)]
            fkref = fk_map.get((name, cn))
            if fkref:
                colargs.append("sa.ForeignKey(%r)" % fkref)
            if col.get("pk"):
                colargs.append("primary_key=True")
            colargs.append("nullable=%s" % ("True" if col.get("nullable", True) else "False"))
            lines.append("        sa.Column(%s)," % ", ".join(colargs))
        lines.append("    )")
    lines.append("")
    lines.append("def downgrade():")
    for name in reversed(order):
        lines.append("    op.drop_table(%r)" % name)
    lines.append("")
    return "\n".join(lines) + "\n"


def generate_alembic_migration(logical_model: Dict[str, Any]) -> str:
    """Passo 5: 0001_initial.py. DETERMINÍSTICO (sem LLM); LLM só como fallback."""
    try:
        return _emit_alembic_deterministic(logical_model)
    except Exception as _e:
        print(f"[DATA-MODEL] alembic determinístico falhou ({_e}); fallback LLM")
        raw = _call_llm(_GENERATE_ALEMBIC_PROMPT.format(
            logical_model_json=json.dumps(logical_model, ensure_ascii=False, indent=2)))
        return _strip_code_fence(raw)


def _validate_schema_executable(schema_sql: str, dbms: str = "mysql") -> Optional[Dict[str, Any]]:
    """Validação EXECUTÁVEL: aplica o schema num banco TEMPORÁRIO e retorna erros REAIS
    (não heurística de LLM). Best-effort — devolve None se não houver DB/driver."""
    if dbms != "mysql" or not (schema_sql or "").strip():
        return None
    try:
        import uuid as _uuid
        import mysql.connector
        from app.database import DB_CONFIG  # mesmas creds do backend (com defaults)
    except Exception:
        return None
    host = DB_CONFIG.get("host"); user = DB_CONFIG.get("user")
    if not (host and user):
        return None
    tmpdb = "_ddlval_" + _uuid.uuid4().hex[:12]
    errors: List[str] = []
    conn = None
    try:
        conn = mysql.connector.connect(
            host=host, port=int(DB_CONFIG.get("port", 3306)),
            user=user, password=DB_CONFIG.get("password", ""))
        cur = conn.cursor()
        cur.execute("CREATE DATABASE `%s` CHARACTER SET utf8mb4" % tmpdb)
        cur.execute("USE `%s`" % tmpdb)
        for stmt in [s.strip() for s in schema_sql.split(";") if s.strip()]:
            try:
                cur.execute(stmt)
            except Exception as _se:
                errors.append(str(_se))
        cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=%s", (tmpdb,))
        ntables = cur.fetchone()[0]
        cur.execute("DROP DATABASE `%s`" % tmpdb)
        conn.commit(); cur.close()
        return {"applied": len(errors) == 0, "tables_created": int(ntables), "errors": errors[:5]}
    except Exception as _e:
        try:
            if conn:
                _c2 = conn.cursor(); _c2.execute("DROP DATABASE IF EXISTS `%s`" % tmpdb); conn.commit(); _c2.close()
        except Exception:
            pass
        return {"applied": False, "tables_created": 0, "errors": [str(_e)]}
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass


def validate_quality(schema_sql: str) -> Dict[str, Any]:
    """Passo 6: valida o schema. AUTORITATIVO por execução real (aplica num banco
    temporário) + sugestões do LLM como complemento. Se o schema não aplica, rebaixa o
    score e injeta o erro REAL — em vez de o validador LLM 'achar' que está bom."""
    prompt = _VALIDATE_QUALITY_PROMPT.format(schema_sql=schema_sql[:40000])
    raw = _call_llm(prompt)
    parsed = _safe_json_parse(raw) or {"score": 0, "issues": [], "suggestions": []}
    exe = _validate_schema_executable(schema_sql)
    if exe is not None:
        parsed["executable"] = exe
        if exe["applied"]:
            parsed["applied_ok"] = True
        else:
            parsed.setdefault("issues", [])
            _msg = exe["errors"][0] if exe["errors"] else "erro desconhecido ao aplicar"
            parsed["issues"].insert(0, {
                "severity": "high", "table": "(schema)",
                "issue": "O SCHEMA NÃO APLICA no MySQL: " + _msg[:300]})
            parsed["score"] = min(int(parsed.get("score", 100) or 100), 25)
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

🔴 PRESERVAÇÃO OBRIGATÓRIA: aplique SOMENTE a mudança pedida. TODAS as tabelas, colunas,
tipos, chaves e relacionamentos que o pedido NÃO menciona devem permanecer IDÊNTICOS (mesmos
nomes, mesma ordem). NÃO remova, renomeie nem "otimize" nada que não foi pedido. O resultado
deve ser o modelo atual + a alteração — nunca uma reescrita que perca tabelas/colunas.

DATA MODEL ATUAL:
```yaml
{current_yaml}
```

PEDIDO DO USUÁRIO:
{user_message}

Retorne SOMENTE o YAML final (completo, com tudo que já existia + a mudança)."""
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


def review_petri_net(petri_json: str) -> str:
    """Usa o LLM para revisar a Rede de Petri (NÃO modifica nada). Analisa corretude
    do workflow: deadlocks/lugares inalcançáveis, transições sem entrada ou saída,
    cobertura das tasks/agentes, marcação inicial/final, e boas práticas. Robusto a falha."""
    try:
        snippet = (petri_json or "").strip()[:22000]
        if not snippet:
            return "Não há Rede de Petri para revisar."
        prompt = (
            "Você é um especialista em Redes de Petri e modelagem de workflows de sistemas "
            "multi-agente. Abaixo está uma Rede de Petri (JSON com lugares, transições, arcos "
            "e agentes). Analise criticamente e liste sugestões objetivas: possíveis DEADLOCKS "
            "ou lugares inalcançáveis, transições sem arco de entrada ou de saída, marcação "
            "inicial/final coerente (início e fim do fluxo), COBERTURA (toda task/agente do "
            "sistema aparece como transição?), paralelismo/sincronização adequados, e boas "
            "práticas de nomeação. NÃO reescreva a rede — apenas recomende. Responda em "
            "português, em tópicos.\n\n"
            "REDE DE PETRI (JSON):\n```json\n" + snippet + "\n```\n"
        )
        out = _call_llm(prompt)
        return (out or "").strip() or "O agente não retornou sugestões."
    except Exception as e:
        return (
            f"Não foi possível gerar sugestões automáticas no momento ({e}). "
            "Revise manualmente: deadlocks, alcançabilidade, cobertura de tasks e marcação inicial/final."
        )


def review_data_model(
    data_model_yaml: str,
    schema_sql: str = "",
    validation_report: str = "",
) -> str:
    """Usa o LLM para sugerir melhorias no Modelo de Dados (NÃO modifica nada).

    Recebe o YAML canônico + o DDL (e, opcionalmente, o relatório de validação) e
    devolve um texto com sugestões objetivas de melhoria. Robusto a falhas: em erro,
    retorna uma mensagem útil ao invés de estourar.
    """
    try:
        yaml_snippet = (data_model_yaml or "").strip()[:20000]
        sql_snippet = (schema_sql or "").strip()[:20000]
        val_snippet = (validation_report or "").strip()[:6000]
        if not yaml_snippet and not sql_snippet:
            return "Não há Modelo de Dados para revisar."
        prompt = (
            "Você é um arquiteto de dados sênior. Abaixo está o Modelo de Dados de um "
            "sistema (descritor YAML e/ou DDL SQL). Analise criticamente e liste "
            "sugestões objetivas de melhoria: normalização, integridade referencial "
            "(chaves estrangeiras faltantes), índices ausentes para consultas prováveis, "
            "tipos de dados inadequados, colunas de auditoria (created_at/updated_at), "
            "restrições (NOT NULL, UNIQUE, CHECK) faltantes, nomes inconsistentes e "
            "possíveis problemas de desempenho. NÃO reescreva o modelo — apenas "
            "recomende. Responda em português, em tópicos.\n\n"
            "DATA MODEL (YAML):\n```yaml\n" + yaml_snippet + "\n```\n\n"
            "SCHEMA (SQL):\n```sql\n" + sql_snippet + "\n```\n"
        )
        if val_snippet:
            prompt += "\nRELATÓRIO DE VALIDAÇÃO:\n" + val_snippet + "\n"
        out = _call_llm(prompt)
        return (out or "").strip() or "O agente não retornou sugestões."
    except Exception as e:
        return (
            f"Não foi possível gerar sugestões automáticas no momento ({e}). "
            "Revise manualmente: normalização, chaves estrangeiras, índices e restrições."
        )
