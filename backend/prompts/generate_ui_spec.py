"""
Geração da UI Spec — uma tela por chamada LLM.

Etapa nova do pipeline LangNet, entre Data Model e Agent-Task Spec. Lê a
Especificação Funcional (casos de uso + wireframes ASCII que a spec já produz)
e o schema_sql do Data Model, e gera, POR TELA:
  - estrutura JSON (rota, entidade, componentes ligados ao schema via bindTo,
    ações ligadas a tasks agênticas ou CRUD)
  - um mockup HTML/CSS standalone (que depois vira esqueleto do React real e é
    renderizado a PNG pra revisão visual)

Estratégia chunked (1 UC por chamada LLM) — mesma que estabilizou o tasks.yaml
com o Qwen2.5-coder-32b local.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple


# UCs cujo verbo indica ação puramente agêntica (sem formulário humano de CRUD).
# Nesses casos a tela vira "disparar + ver resultado" em vez de form ligado a entidade.
_AGENTIC_HINTS = (
    "gerar", "verificar", "classificar", "coletar", "identificar",
    "publicar", "sugest", "sugerir", "monitorar",
)


# ─────────────────────────────────────────────────────────────────────
# PARSING DA SPEC
# ─────────────────────────────────────────────────────────────────────

def parse_uc_blocks(specification_document: str) -> List[Dict[str, str]]:
    """Extrai blocos de caso de uso da spec.

    Cada UC no doc segue o padrão:
      **UC-001: Cadastrar Persona-Alvo**
      | Campo | Detalhe |
      | **Ator Principal** | CEO |
      | **Objetivo** | ... |
      | **RFs Relacionados** | FR-001 |
      #### Fluxo Principal
      | # | Ação do Ator | Resposta do Sistema |
      ...
      #### Wireframe da Interface
      **Tela:** ...
      ```
      <ascii>
      ```
    """
    blocks: List[Dict[str, str]] = []
    # Cada UC começa em **UC-NNN: título** e vai até o próximo **UC- ou fim.
    pattern = re.compile(
        r'\*\*(UC-\d+):\s*(.+?)\*\*(.*?)(?=\*\*UC-\d+:|\Z)',
        re.S,
    )
    for m in pattern.finditer(specification_document):
        uc_id = m.group(1).strip()
        uc_name = m.group(2).strip()
        body = m.group(3)

        uc = {"id": uc_id, "name": uc_name, "raw": body}

        # Campos da tabela de cabeçalho
        for fm in re.finditer(r'\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|', body):
            key = fm.group(1).strip().lower()
            val = fm.group(2).strip()
            if "ator principal" in key:
                uc["actor"] = val
            elif "objetivo" in key:
                uc["objetivo"] = val
            elif key.startswith("rfs") or "rf relacionad" in key or "rfs relacionad" in key:
                uc["rfs"] = val

        # Fluxo principal (ações do ator → respostas) — texto bruto para o LLM
        flow_m = re.search(r'#+\s*Fluxo Principal(.*?)(?=#+\s|\Z)', body, re.S)
        if flow_m:
            uc["flow"] = flow_m.group(1).strip()

        # Wireframe ASCII
        wf_m = re.search(r'#+\s*Wireframe.*?```(.*?)```', body, re.S)
        if wf_m:
            uc["wireframe"] = wf_m.group(1).strip()
        # Nome da tela declarado no wireframe
        tela_m = re.search(r'\*\*Tela:\*\*\s*(.+)', body)
        if tela_m:
            uc["screen_title"] = tela_m.group(1).strip()

        blocks.append(uc)
    return blocks


def parse_schema_tables(schema_sql: str) -> Dict[str, str]:
    """Reaproveita a mesma lógica de generate_single_task_yaml: dict tabela→DDL."""
    tables: Dict[str, str] = {}
    if not schema_sql:
        return tables
    n = len(schema_sql)
    i = 0
    while i < n:
        m = re.match(
            r'\s*CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"]?(\w+)[`"]?\s*\(',
            schema_sql[i:], re.I,
        )
        if m:
            name = m.group(1)
            paren_pos = i + m.end() - 1
            depth = 1
            j = paren_pos + 1
            while j < n and depth > 0:
                if schema_sql[j] == '(':
                    depth += 1
                elif schema_sql[j] == ')':
                    depth -= 1
                j += 1
            end = schema_sql.find(';', j)
            if end < 0:
                end = n
            tables[name] = schema_sql[i:end + 1].strip()
            i = end + 1
        else:
            i += 1
    return tables


def select_relevant_tables(uc: Dict[str, str], tables: Dict[str, str], max_tables: int = 4) -> List[str]:
    """Escolhe as tabelas que a tela provavelmente manipula, casando nomes/colunas
    contra o texto do UC (nome + objetivo + fluxo + wireframe)."""
    if not tables:
        return []
    haystack = " ".join([
        uc.get("name", ""), uc.get("objetivo", ""),
        uc.get("flow", ""), uc.get("wireframe", ""), uc.get("screen_title", ""),
    ]).lower()

    scores: Dict[str, int] = {}
    for name, ddl in tables.items():
        score = 0
        for variant in {name, name.rstrip("s"), name + "s"}:
            if variant.lower() in haystack:
                score += 5
                break
        cols = re.findall(
            r'^\s*[`"]?(\w+)[`"]?\s+(?:CHAR|VARCHAR|TEXT|INT|BIGINT|DECIMAL|DATE|TIMESTAMP|ENUM|GEOMETRY|BOOLEAN|TINYINT|FLOAT|DOUBLE)',
            ddl, re.I | re.M,
        )
        for col in cols:
            if len(col) >= 4 and col.lower() in haystack and col.lower() not in (
                "nome", "id", "status", "created_at", "updated_at", "descricao"
            ):
                score += 1
        if score > 0:
            scores[name] = score
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    return [n for n, _ in ranked[:max_tables]]


def build_sub_schema(picked: List[str], tables: Dict[str, str]) -> str:
    return "\n\n".join(tables[t] for t in picked if t in tables)


def is_agentic_screen(uc: Dict[str, str]) -> bool:
    name = (uc.get("name", "") or "").lower()
    return any(name.startswith(h) or h in name.split()[0:1] for h in _AGENTIC_HINTS) or \
        any(h in name for h in _AGENTIC_HINTS)


# ─────────────────────────────────────────────────────────────────────
# PROMPT (uma tela)
# ─────────────────────────────────────────────────────────────────────

_INSTRUCTIONS = """Você é um designer de produto e engenheiro front-end sênior.

TAREFA: a partir de UM caso de uso (com seu wireframe ASCII) e do schema real do
banco, gere a especificação de UMA tela + um mockup HTML/CSS standalone dessa tela.

Retorne APENAS um objeto JSON válido (sem markdown, sem cercas ```), no formato:

{{
  "id": "kebab-case-da-tela",
  "name": "Nome legível da tela",
  "route": "/rota/sugerida",
  "uc": ["UC-XXX"],
  "entity": "nome_da_tabela_principal_ou_null",
  "layout": "form | table | dashboard | detail",
  "components": [
    {{"type": "text|textarea|number|date|select|multiselect|checkbox|table|readonly",
      "field": "nome_campo", "label": "Rótulo", "required": true|false,
      "bindTo": "tabela.coluna (ou tabela_filha[].coluna para listas), ou null"}}
  ],
  "actions": [
    {{"label": "Salvar", "kind": "task|crud|navigate", "target": "nome_task_ou_rota", "primary": true|false}}
  ],
  "mockup_html": "<!doctype html><html>...página completa e estilizada...</html>"
}}

REGRAS:
1. Os `components` devem refletir os campos REAIS do schema abaixo. Use `bindTo`
   para ligar cada campo à coluna correta. Listas (ex.: canais) que no schema são
   tabela filha → type "multiselect" com bindTo "tabela_filha[].coluna".
2. `actions`: o botão principal de salvar/criar deve ter kind "task" e target no
   formato verbo_objeto snake_case (ex.: cadastrar_persona_alvo), casando com o
   nome provável da task do pipeline. Botões de cancelar/voltar usam kind "navigate".
3. `mockup_html`: HTML COMPLETO e AUTOCONTIDO (com <style> inline), visualmente
   caprichado (cabeçalho, card, campos com labels, botões destacados). Deve refletir
   o wireframe ASCII fornecido, mas renderizado como UI real e limpa. Largura ~900px,
   fonte sans-serif, paleta sóbria (azul #1976d2 pros botões primários). SEM
   JavaScript, SEM libs externas — só HTML + CSS inline.
4. Se a tela for de ação agêntica (gerar/classificar/coletar), o layout pode ser
   "detail" ou "dashboard": mostre os inputs necessários + um botão de disparo + uma
   área de resultado (placeholder).
5. 🔴 DADOS DE EXIBIÇÃO vs CAMPOS DE ENTRADA — regra crítica:
   - Em telas "dashboard" (métricas, estatísticas, relatórios, KPIs), os valores
     numéricos/agregados são EXIBIÇÃO: use type "readonly" e no mockup renderize
     como CARDS ou linhas de leitura com o número em destaque (ex.: "Impressões
     1.240"), NUNCA como <input> vazio pra digitar.
   - Campos de <input>/<textarea>/<select> só aparecem quando o USUÁRIO realmente
     digita/escolhe um valor (formulários de cadastro/edição, filtros de período,
     parâmetros de disparo). Uma métrica que o sistema calcula NÃO é input.
   - Exemplo dashboard de métricas (mockup): grade de cards
     ┌───────────┐ ┌───────────┐ com <div class="card"><span class="valor">1.240</span>
     │Impressões │ │ Curtidas  │ <span class="rotulo">Impressões</span></div>, e no
     │  1.240    │ │    89     │ TOPO um filtro de período (esse sim é input) + botão
     └───────────┘ └───────────┘ "Atualizar/Coletar".

{agentic_note}

## CASO DE USO
ID: {uc_id}
Nome: {uc_name}
Ator: {actor}
Objetivo: {objetivo}
Tela declarada: {screen_title}

### Fluxo Principal (ator → sistema)
{flow}

### Wireframe ASCII (referência visual — reproduza como HTML limpo)
{wireframe}

{schema_block}

Gere agora o JSON da tela (apenas o JSON):"""

_AGENTIC_NOTE = (
    "OBS: esta tela dispara trabalho de um AGENTE de IA (não é CRUD simples). "
    "Modele um botão de disparo (kind 'task') e uma área de resultado."
)


def build_single_screen_prompt(uc: Dict[str, str], sub_schema: str) -> str:
    schema_block = ""
    if sub_schema:
        schema_block = f"## SCHEMA REAL DAS TABELAS RELEVANTES\n\n```sql\n{sub_schema}\n```"
    return _INSTRUCTIONS.format(
        agentic_note=_AGENTIC_NOTE if is_agentic_screen(uc) else "",
        uc_id=uc.get("id", ""),
        uc_name=uc.get("name", ""),
        actor=uc.get("actor", "—"),
        objetivo=uc.get("objetivo", "—"),
        screen_title=uc.get("screen_title", uc.get("name", "")),
        flow=uc.get("flow", "(sem fluxo detalhado)"),
        wireframe=uc.get("wireframe", "(sem wireframe)"),
        schema_block=schema_block,
    )


# ─────────────────────────────────────────────────────────────────────
# SANITIZAÇÃO + VALIDAÇÃO
# ─────────────────────────────────────────────────────────────────────

def strip_json_fences(text: str) -> str:
    if not text:
        return text
    t = text.strip()
    t = re.sub(r'^```(?:json)?\s*\n', '', t)
    t = re.sub(r'\n```\s*$', '', t)
    return t.strip()


def extract_json_object(text: str) -> Optional[str]:
    """Extrai o primeiro objeto JSON balanceado do texto (o LLM às vezes
    adiciona comentário antes/depois)."""
    if not text:
        return None
    text = strip_json_fences(text)
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
    return None


def validate_screen(screen: dict) -> Tuple[bool, str]:
    if not isinstance(screen, dict):
        return False, "não é objeto"
    for k in ("id", "name", "mockup_html"):
        if not screen.get(k):
            return False, f"faltando '{k}'"
    html = screen.get("mockup_html", "")
    if "<" not in html or "style" not in html.lower():
        return False, "mockup_html sem HTML/CSS"
    return True, "ok"
