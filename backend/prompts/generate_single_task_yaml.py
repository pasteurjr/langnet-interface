"""
Chunked generation of tasks.yaml — one task per LLM call, with focused sub-schema.

Strategy:
  1. Parse the agent_task_spec_document Markdown into per-task blocks.
  2. Parse schema_sql into individual CREATE TABLE statements.
  3. For each task: build a sub-schema (only tables relevant to that task) + prompt
     focused on generating ONLY that task's YAML block.
  4. Validate — if task name implies persistence (cadastrar/criar/etc.) but the
     Process steps have no INSERT INTO / UPDATE / DELETE, retry once with an
     explicit "you forgot the SQL" hint.
  5. Concatenate all successful task YAMLs into the final tasks.yaml content.

Fallback: if too many tasks fail after retry, caller should use the legacy
single-shot generator.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple


PERSISTENCE_VERBS = (
    "cadastrar", "criar", "registrar", "salvar", "inserir", "adicionar",
    "importar", "atualizar", "editar", "modificar", "deletar", "remover",
    "gerar_e_salvar", "persist",
)


# ─────────────────────────────────────────────────────────────────────
# PARSING
# ─────────────────────────────────────────────────────────────────────

def parse_task_blocks(agent_task_spec_document: str) -> List[Dict[str, str]]:
    """
    Extract per-task blocks from the ATS markdown document.

    ATS format for each task:
      #### T-XXX-YYY: Human readable title
      | Atributo | Especificação |
      | **Nome** | task_name_snake_case |
      | **Descrição** | ... |
      | **Agent** | AG-01 (Agent Name) |
      | **Tools** | tool1, tool2 |
      | **Input Schema** | ... |
      | **Output Schema** | ... |
      | **Módulo** | ... |
      ---
    """
    blocks = []
    # Split on task section headers (#### T-...) or agent headers (#### AG-)
    pattern = re.compile(
        r'(####\s+T-[\w-]+.*?)(?=####\s+T-|####\s+AG-|\Z)',
        re.S,
    )
    for m in pattern.finditer(agent_task_spec_document):
        raw = m.group(1)
        task = _parse_single_block(raw)
        if task and task.get("name"):
            blocks.append(task)
    return blocks


def _parse_single_block(raw: str) -> Optional[Dict[str, str]]:
    """Extract fields from one task block by matching table rows."""
    fields: Dict[str, str] = {"raw": raw}

    header_m = re.search(r'####\s+(T-[\w-]+):\s*(.+)', raw)
    if header_m:
        fields["id"] = header_m.group(1).strip()
        fields["title"] = header_m.group(2).strip()

    # Table rows: | **Field** | value |
    for m in re.finditer(r'\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|', raw):
        key = m.group(1).strip().lower().replace(" ", "_")
        val = m.group(2).strip()
        # unescape \n typography
        val = val.replace("\\n", "\n").strip()
        if key == "nome":
            fields["name"] = val
        elif "descri" in key:
            fields["description"] = val
        elif key == "agent":
            fields["agent"] = val
        elif key == "tools":
            fields["tools"] = val
        elif "input" in key and "schema" in key:
            fields["input_schema"] = val
        elif "output" in key and "schema" in key:
            fields["output_schema"] = val
        elif "módulo" in key or "modulo" in key:
            fields["module"] = val
        elif "rationale" in key:
            fields["rationale"] = val

    return fields if fields.get("name") else None


def parse_schema_tables(schema_sql: str) -> Dict[str, str]:
    """
    Parse CREATE TABLE statements into {table_name: full_ddl}.
    """
    tables: Dict[str, str] = {}
    # Match: CREATE TABLE [IF NOT EXISTS] `?name`? ( ... );  (respecting nested parens)
    depth = 0
    i = 0
    current_start = -1
    n = len(schema_sql)
    while i < n:
        if current_start < 0:
            m = re.match(r'\s*CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"]?(\w+)[`"]?\s*\(',
                         schema_sql[i:], re.I)
            if m:
                current_start = i
                current_name = m.group(1)
                # advance past the opening paren
                paren_pos = i + m.end() - 1
                depth = 1
                j = paren_pos + 1
                while j < n and depth > 0:
                    if schema_sql[j] == '(':
                        depth += 1
                    elif schema_sql[j] == ')':
                        depth -= 1
                    j += 1
                # capture until next ';' or end
                end = schema_sql.find(';', j)
                if end < 0:
                    end = n
                tables[current_name] = schema_sql[current_start:end + 1].strip()
                i = end + 1
                current_start = -1
                continue
        i += 1
    return tables


# ─────────────────────────────────────────────────────────────────────
# SUB-SCHEMA SELECTION
# ─────────────────────────────────────────────────────────────────────

def select_relevant_tables(
    task: Dict[str, str],
    tables: Dict[str, str],
    max_tables: int = 6,
) -> List[str]:
    """
    Pick tables likely used by this task.

    Heuristic:
      - Match table names against words in description + input/output schemas
        + task name (case-insensitive, singular/plural stripped).
      - Match field names against column names.
    """
    if not tables:
        return []

    haystack = " ".join([
        task.get("name", ""),
        task.get("description", ""),
        task.get("input_schema", ""),
        task.get("output_schema", ""),
        task.get("title", ""),
    ]).lower()

    scores: Dict[str, int] = {}
    for table_name, ddl in tables.items():
        score = 0
        # table name match (singular + plural naive)
        for variant in {table_name, table_name.rstrip("s"), table_name + "s"}:
            if variant.lower() in haystack:
                score += 5
                break
        # column names inside DDL
        cols = re.findall(r'^\s*[`"]?(\w+)[`"]?\s+(?:CHAR|VARCHAR|TEXT|INT|BIGINT|DECIMAL|DATE|TIMESTAMP|ENUM|GEOMETRY|BOOLEAN|TINYINT|FLOAT|DOUBLE)',
                          ddl, re.I | re.M)
        for col in cols:
            if len(col) >= 4 and col.lower() in haystack and col.lower() not in {"nome", "id", "status", "created_at", "updated_at", "descricao"}:
                score += 1
        if score > 0:
            scores[table_name] = score

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    picked = [name for name, _ in ranked[:max_tables]]
    return picked


def build_sub_schema(picked_tables: List[str], tables: Dict[str, str]) -> str:
    if not picked_tables:
        return ""
    return "\n\n".join(tables[t] for t in picked_tables if t in tables)


# ─────────────────────────────────────────────────────────────────────
# PERSISTENCE DETECTION + VALIDATION
# ─────────────────────────────────────────────────────────────────────

def needs_persistence(task: Dict[str, str]) -> bool:
    name = (task.get("name", "") or "").lower()
    for verb in PERSISTENCE_VERBS:
        if name.startswith(verb + "_") or verb in name:
            return True
    # Output schema mentions an entity id / uuid → probably a CREATE
    out = (task.get("output_schema", "") or "").lower()
    if re.search(r'\b\w+_id\s*:\s*(uuid|string)', out):
        return True
    if re.search(r'\b(uuid|created_at|inserted|criado|gerado)', out):
        return True
    # Description mentions "armazena" / "salva" / "grava"
    desc = (task.get("description", "") or "").lower()
    if re.search(r'\b(armazena|salva|grava|persiste|cadastra|cria\s+(?:novo|um))', desc):
        return True
    return False


def validate_task_yaml(task_name: str, task_yaml: str, needs_sql: bool) -> Tuple[bool, str]:
    """
    Basic sanity check for a single-task YAML block.
    """
    if not task_yaml or task_name not in task_yaml:
        return False, f"missing task_name '{task_name}'"
    if "description:" not in task_yaml or "expected_output:" not in task_yaml:
        return False, "missing description or expected_output"
    if needs_sql:
        # accept INSERT, UPDATE, DELETE, or explicit SELECT-after-INSERT pattern
        sql_ops = ("INSERT INTO", "UPDATE ", "DELETE FROM")
        if not any(op in task_yaml for op in sql_ops):
            return False, "persistence task has no INSERT/UPDATE/DELETE"
    return True, "ok"


# ─────────────────────────────────────────────────────────────────────
# PROMPT
# ─────────────────────────────────────────────────────────────────────

_BASE_INSTRUCTIONS = """Você é especialista em CrewAI e YAML. Gere APENAS o bloco YAML de UMA task.

REGRAS ABSOLUTAS:
1. Retorne SOMENTE o YAML da task solicitada. Sem markdown fences. Sem explicações.
   Começa em `{task_name}:` e termina antes da próxima chave top-level.
2. Formato:
     {task_name}:
       agent: <agent_snake_case>
       description: >
         <descrição + input format + Process steps numerados>
       expected_output: >
         <descrição textual em prosa dos campos do JSON>
3. Indentação: 2 espaços. Use `>` para blocos multiline.
4. Placeholders: {{{{variavel}}}} (chaves duplas).
"""

_SQL_RULES = """
5. Esta task PERSISTE DADOS. Os Process steps DEVEM conter SQL EXPLÍCITO
   contra o schema abaixo. Não escreva "usar database_tool para salvar" —
   escreva o INSERT/UPDATE literal. Regras SQL:

   a. Para INSERT numa tabela com PK CHAR(36) DEFAULT UUID(), o padrão é:
        1. Chame database_tool com
           query="INSERT INTO <tabela>(<colunas>) VALUES(<placeholders>)"
           params=[<valores>]
        2. Capture o id gerado:
           query="SELECT id FROM <tabela> WHERE <coluna_unica>=%s ORDER BY created_at DESC LIMIT 1"
           params=[<valor_unico>]
        3. Guarde o id numa variável (ex.: registro_id).
        LAST_INSERT_ID() é INÚTIL com PK UUID — NUNCA use.

   b. Para listas na input (ex.: canais: List[str]) que viram tabela filha:
        Para CADA item, INSERT INTO <tabela_filha>(<fk_id>, <coluna>) VALUES(%s, %s)
        params=[registro_id, item]

   c. Use nomes EXATOS de tabela e coluna do schema. NÃO invente colunas.
"""

_NO_SQL_RULES = """
5. Esta task NÃO persiste dados. Descreva as chamadas às tools (database_tool,
   sql_query_tool, api_call_tool, etc.) que serão feitas. Se ela consulta o
   banco (SELECT), pode escrever a query, mas não é obrigatório.
"""

_EXAMPLE_HDR = "EXEMPLO REAL de task com SQL (siga este padrão EXATO):"

_EXAMPLE_SQL = """```
cadastrar_pessoa:
  agent: pessoa_manager_agent
  description: >
    Cadastrar pessoa no banco respeitando o schema normalizado.
    Input data format:
      - nome: String
      - telefones: List[String]

    Process steps:
      1. INSERT: chame database_tool com
         query="INSERT INTO pessoas(nome) VALUES(%s)"
         params=[{{nome}}]
      2. Capture o id UUID: chame database_tool com
         query="SELECT id FROM pessoas WHERE nome=%s ORDER BY created_at DESC LIMIT 1"
         params=[{{nome}}]
         Guarde em pessoa_id (NUNCA use LAST_INSERT_ID()).
      3. Para CADA telefone em {{telefones}}:
         chame database_tool com
         query="INSERT INTO telefones(pessoa_id, numero) VALUES(%s, %s)"
         params=[pessoa_id, telefone]
      4. Retorne pessoa_id + status "sucesso".

  expected_output: >
    Retornar um texto em formato JSON contendo as seguintes keys:
    - pessoa_id: UUID capturado no passo 2
    - status: String (sucesso ou erro)
```

⚠️ ATENÇÃO CRÍTICA: use EXATAMENTE duas chaves `{{nome}}` — nem uma, nem quatro.
"""


def build_single_task_prompt(
    task: Dict[str, str],
    sub_schema: str,
    persistence: bool,
    retry_hint: Optional[str] = None,
) -> str:
    task_name = task.get("name", "")
    header = _BASE_INSTRUCTIONS.format(task_name=task_name)

    if persistence:
        rules = _SQL_RULES
        example = f"{_EXAMPLE_HDR}\n\n{_EXAMPLE_SQL}\n"
    else:
        rules = _NO_SQL_RULES
        example = ""

    schema_block = ""
    if sub_schema and persistence:
        schema_block = f"\n## SCHEMA REAL DAS TABELAS QUE ESTA TASK USA\n\n```sql\n{sub_schema}\n```\n"

    retry_block = ""
    if retry_hint:
        retry_block = f"\n⚠️ RETRY — na tentativa anterior você esqueceu: {retry_hint}\nCorrija agora.\n"

    task_block = f"""## TASK A GERAR

**ID:** {task.get('id', '')}
**Nome (chave YAML):** {task_name}
**Agent:** {task.get('agent', '')}
**Descrição (do ATS):** {task.get('description', '')}
**Input Schema:** {task.get('input_schema', '')}
**Output Schema:** {task.get('output_schema', '')}
**Tools:** {task.get('tools', '')}
"""

    return f"{header}\n{rules}\n{schema_block}\n{example}\n{task_block}\n{retry_block}\nGere agora o YAML de `{task_name}`:"


# ─────────────────────────────────────────────────────────────────────
# SANITIZATION
# ─────────────────────────────────────────────────────────────────────

def strip_yaml_fences(text: str) -> str:
    """Remove leading ```yaml ... ``` fences if the LLM added them."""
    if not text:
        return text
    t = text.strip()
    t = re.sub(r'^```(?:yaml|yml)?\s*\n', '', t)
    t = re.sub(r'\n```\s*$', '', t)
    return t.strip()


def extract_task_block(task_name: str, generated: str) -> str:
    """
    Isolate just this task's YAML block. Handles the case where the LLM
    also emitted unrelated tasks or wrapper commentary.
    """
    if not generated:
        return ""
    generated = strip_yaml_fences(generated)
    # find the line "task_name:" at column 0
    pattern = re.compile(rf'^{re.escape(task_name)}\s*:\s*$', re.M)
    m = pattern.search(generated)
    if not m:
        # allow inline (task_name: on a line with other content) as fallback
        pattern2 = re.compile(rf'^{re.escape(task_name)}:\s', re.M)
        m = pattern2.search(generated)
        if not m:
            return generated  # give it back and let validation decide
    start = m.start()
    # end = start of next top-level key OR end of text
    tail = generated[start + len(task_name) + 1:]
    next_top = re.search(r'^\S[\w-]*\s*:\s*$', tail, re.M)
    end = start + len(task_name) + 1 + (next_top.start() if next_top else len(tail))
    return generated[start:end].rstrip() + "\n"
