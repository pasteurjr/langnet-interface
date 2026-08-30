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
    # Mapa AG-XX -> nome snake_case a partir da tabela de OVERVIEW dos agentes
    # (Seção 1 da ATS: "| AG-01 | consulta_agent | ... |"). O campo Agent por task
    # costuma vir só como "AG-02" (sem o nome), então precisamos resolver aqui — senão
    # o tasks.yaml referencia "AG-02" e o app quebra (agents.yaml usa a chave snake_case).
    agent_map = _parse_agent_overview(agent_task_spec_document)
    # ROSTER de agentes válidos (elenco do ATS, transliterado+_agent) = as chaves que o
    # agents.yaml define. Toda referência de agente nas tasks é resolvida contra ele — assim
    # tasks.yaml e agents.yaml ficam COERENTES (senão o app quebra: agente não encontrado).
    import unicodedata as _ud2

    def _norm_ag(n: str) -> str:
        n = _ud2.normalize('NFKD', n).encode('ascii', 'ignore').decode('ascii').lower()
        n = re.sub(r'[^a-z0-9_]+', '_', n).strip('_')
        return n if n.endswith('_agent') else (f"{n}_agent" if n else n)
    roster = set(_norm_ag(v) for v in agent_map.values() if v)

    blocks = []
    # Split on task section headers (#### T-...) or agent headers (#### AG-)
    pattern = re.compile(
        r'(####\s+T-[\w-]+.*?)(?=####\s+T-|####\s+AG-|\Z)',
        re.S,
    )
    for m in pattern.finditer(agent_task_spec_document):
        raw = m.group(1)
        task = _parse_single_block(raw, agent_map, roster)
        if task and task.get("name"):
            blocks.append(task)
    return blocks


def _parse_agent_overview(doc: str) -> Dict[str, str]:
    """{AG-XX -> nome_snake_case} a partir da tabela de visão geral dos agentes.
    Linha típica: | AG-01 | consulta_agent | Consulta | GPT-4o | Sim |"""
    amap: Dict[str, str] = {}
    for m in re.finditer(r'\|\s*(AG-\d+)\s*\|\s*([A-Za-z_][\w]*)\s*\|', doc):
        amap[m.group(1).strip()] = m.group(2).strip()
    return amap


def _parse_single_block(raw: str, agent_map: Optional[Dict[str, str]] = None,
                        roster: Optional[set] = None) -> Optional[Dict[str, str]]:
    """Extract fields from one task block by matching table rows."""
    fields: Dict[str, str] = {"raw": raw}
    agent_map = agent_map or {}

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
            # Resolve o agente para uma chave que EXISTA no agents.yaml. Bugs corrigidos:
            # (1) "AG-04 (Cálculo Urbano Agent)" caía no fallback e slugificava o título com
            #     acento quebrado (á->_) -> c_lculo_urbano_agent; agora casa o prefixo AG-XX
            #     (mesmo com parênteses) pelo overview.
            # (2) acento transliterado (legislação->legislacao) p/ bater com o agents.yaml.
            # (3) nomes FORA do elenco (inventados pelo laço de cobertura) mapeados ao roster
            #     por similaridade — senão o app quebra (agente não definido).
            import unicodedata as _ud

            def _tl(s: str) -> str:
                return _ud.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
            _agid = re.match(r'^\s*(AG-\d+)', val)  # prefixo: aceita "AG-04 (...)"
            if _agid and agent_map.get(_agid.group(1)):
                _snake = agent_map[_agid.group(1)]
            else:
                _pr = re.search(r'\(([^)]+)\)', val)
                _snake = _tl(_pr.group(1) if _pr else val)
            _snake = re.sub(r'[^a-z0-9_]+', '_', _tl(_snake).lower()).strip('_')
            if _snake and not _snake.endswith('_agent'):
                _snake = f"{_snake}_agent"
            if roster and _snake and _snake not in roster:
                import difflib as _dl
                _c = _dl.get_close_matches(_snake, list(roster), n=1, cutoff=0.4)
                if _c:
                    _snake = _c[0]
            fields["agent_snake"] = _snake
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
        elif "uc" in key and ("relacion" in key or "relacionado" in key or key.strip() in ("uc", "casos de uso")):
            # "UC Relacionado": UC-004 (Consultar...) -> ["UC-004"]
            ucs = re.findall(r'UC-?\d+', val)
            if ucs:
                fields["uc_related"] = ucs
        elif ("rf" in key or "fr" in key) and "relacion" in key:
            # "RF Relacionado" / "FR Relacionado": FR-003, FR-013 -> ["FR-003","FR-013"]
            frs = re.findall(r'(?:FR|RF)-?\d+', val)
            if frs:
                fields["fr_related"] = [f.replace("RF", "FR") for f in frs]

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
       execution: deterministic   # ou 'agent' — classifique pela natureza (ver REGRA 6)
       agent: <agent_snake_case>
       description: >
         <descrição + input format + Process steps numerados>
       expected_output: >
         <descrição textual em prosa dos campos do JSON>
3. Indentação: 2 espaços. Use `>` para blocos multiline.
4. Placeholders: uma chave só ao redor do nome, ex: substitua o nome do
   parametro por chave-abre + nome + chave-fecha, formato CrewAI oficial.
   Nunca use duas ou quatro chaves — o CrewAI trata isso como literal
   e a task quebra em runtime.
6. execution (OBRIGATÓRIO em TODA task): classifique pela NATUREZA da task:
   - `deterministic` → COMPUTAÇÃO ou CRUD de lógica FIXA: consultar/inserir/
     atualizar/excluir dados; cálculo SQL/espacial/matemático EXATO (área,
     sobreposição ST_Intersects/ST_Area, CA/TO, recuos, faixas por regra,
     declividade). Não há julgamento — um algoritmo fixo resolve. Roda em
     CÓDIGO, sem LLM: exato, auditável, reproduzível, barato.
   - `agent` → exige JULGAMENTO/linguagem: classificar por interpretação (ex.:
     classe de impacto COPAM do caso), COMPOR texto (laudo/parecer/narrativa),
     decidir, tratar caso ambíguo, resumir.
   Régua: se um algoritmo FIXO produz a resposta → `deterministic`; se precisa
   "pensar"/redigir/interpretar → `agent`. Em documentos LEGAIS (laudos), os
   CÁLCULOS são SEMPRE `deterministic` (auditáveis); só a COMPOSIÇÃO do texto
   do laudo é `agent`.
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

   d. CONSISTÊNCIA DE NOME DE CAMPO (crítico): os campos que o agente RACIOCINA
      (aparecem no Output Schema, ex.: nivel_urgencia, diagnostico_inicial,
      especialista_sugerido) DEVEM ser gravados no SQL com o MESMO nome. Se o
      Output Schema tem `diagnostico_inicial`, o params usa `{diagnostico_inicial}`
      — NUNCA um sinônimo como `{diagnostico}`. Um nome trocado grava NULL e o
      raciocínio se PERDE. Regra de ouro: todo campo do Output Schema que representa
      uma conclusão do agente deve aparecer num INSERT/UPDATE, com nome IDÊNTICO.

   e. ENTIDADE COMPARTILHADA (ex.: prontuário de um paciente): quando várias tasks
      do fluxo (triagem→pré-diagnóstico→encaminhamento) gravam no MESMO prontuário
      do MESMO paciente, use a FK `id_paciente` como chave e faça
      **UPDATE ... WHERE id_paciente=%s** para ADICIONAR ao registro existente —
      NÃO faça INSERT novo a cada task (gera duplicata/registros soltos). Referencie
      `id_paciente` (propagado pela input), NUNCA invente/confunda com `id_prontuario`.

   f. PROPAGAÇÃO DE ID: se a input traz `id_paciente` (ou o id da entidade corrente),
      USE-O direto no WHERE/params. Não re-derive por SELECT frágil.

   g. VALOR SEMÂNTICO CORRETO: um campo que representa uma CATEGORIA/CLASSIFICAÇÃO
      (ex.: `especialidade_encaminhada`, `nivel_urgencia`) deve receber o VALOR da
      categoria (ex.: "Cardiologia", "alta") — NUNCA o nome de uma instância/pessoa
      (ex.: "Dr. João Silva") nem um id. Se o campo é uma especialidade médica, grave
      a ESPECIALIDADE (Cardiologia, Neurologia…), não o nome do médico.

   h. COMPUTAÇÃO/AGREGAÇÃO — faça a conta DENTRO do SQL, NUNCA em prosa. Quando a
      task calcula um agregado sobre várias linhas (soma de áreas, total, contagem,
      máximo, média, "existe alguma", área de sobreposição total), a AGREGAÇÃO tem de
      estar na própria query (SUM/COUNT/MAX/AVG/BOOL_OR/CASE), com um ALIAS `AS <nome>`,
      e você CAPTURA o escalar com "Guarde o resultado em <nome>". Depois use `{<nome>}`
      no INSERT/UPDATE. Exemplo (área total de sobreposição com APP, espacial):
        1. query="SELECT COALESCE(SUM(ST_Area(ST_Intersection(l.geometria, a.geometria))), 0) AS area_sobreposicao_app
                  FROM lote l JOIN app a ON ST_Intersects(l.geometria, a.geometria) WHERE l.id=%s"
           params=[{lote_id}]
           Guarde o resultado em area_sobreposicao_app.
        2. query="UPDATE laudo SET area_sobreposicao_app=%s WHERE lote_id=%s"
           params=[area_sobreposicao_app, {lote_id}]
      ❌ PROIBIDO descrever acumulação em linguagem natural — o gerador determinístico
      NÃO interpreta prosa. NUNCA escreva "Para cada lote, se a área > 0 some ao total";
      "Determine X como True se houver…"; "acumule na lista". Se precisar de um número,
      ele SAI de um SUM/COUNT/CASE no SQL com AS <nome>. Filtros/condições viram WHERE
      ou CASE WHEN dentro da query (ex.: `SUM(CASE WHEN area>0 THEN area ELSE 0 END)`).
"""

_NO_SQL_RULES = """
5. Esta task NÃO persiste dados (não faz INSERT/UPDATE/DELETE). Descreva as chamadas
   às tools que fará. REGRAS:
   a. Se a task CONSULTA o banco (SELECT) — inclusive para montar dashboards, relatórios
      ou agregações — escreva a consulta SEMPRE no formato canônico, EM LINHAS PRÓPRIAS:
         query="SELECT ... FROM ... WHERE ..."
         params=[{param1}, {param2}]
      NUNCA escreva SQL em prosa (ex.: "execute a consulta: SELECT ..."). O gerador
      determinístico SÓ reconhece o formato query="...". SQL em prosa = task que não faz nada.
   b. AGREGAÇÃO/CONTAGEM/SOMA/MÉDIA: faça a conta DENTRO do SQL (SUM/COUNT/AVG/MAX/
      GROUP BY/CASE), com ALIAS `AS <nome>`, e capture com "Guarde o resultado em <nome>".
      NUNCA descreva a agregação em linguagem natural ("para cada indicador, some os
      valores") — o determinístico não interpreta prosa; o número SAI de um SUM/COUNT no SQL.
      Ex.: query="SELECT tipo, COUNT(*) AS total FROM consulta WHERE municipio_id=%s
                  AND data_hora BETWEEN %s AND %s GROUP BY tipo"
           params=[{municipio_id}, {data_inicial}, {data_final}]
           Guarde o resultado em indicadores.
   c. Para chamadas a tools que NÃO são SQL (api_call_tool, pdf_reader, etc.), descreva
      normalmente — o passo SQL segue o formato acima.
"""

_EXAMPLE_HDR = "EXEMPLO REAL de task com SQL (siga este padrão EXATO):"

_EXAMPLE_SQL = """```
cadastrar_pessoa:
  execution: deterministic
  agent: pessoa_manager_agent
  description: >
    Cadastrar pessoa no banco respeitando o schema normalizado.
    Input data format:
      - nome: String
      - telefones: List[String]

    Process steps:
      1. INSERT: chame database_tool com
         query="INSERT INTO pessoas(nome) VALUES(%s)"
         params=[{nome}]
      2. Capture o id UUID: chame database_tool com
         query="SELECT id FROM pessoas WHERE nome=%s ORDER BY created_at DESC LIMIT 1"
         params=[{nome}]
         Guarde em pessoa_id (NUNCA use LAST_INSERT_ID()).
      3. Para CADA telefone em {telefones}:
         chame database_tool com
         query="INSERT INTO telefones(pessoa_id, numero) VALUES(%s, %s)"
         params=[pessoa_id, telefone]
      4. Retorne pessoa_id + status "sucesso".

  expected_output: >
    Retornar um texto em formato JSON contendo as seguintes keys:
    - pessoa_id: UUID capturado no passo 2
    - status: String (sucesso ou erro)
```

Note o formato dos placeholders acima: exatamente UMA chave por variável.
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

    # Prefer the snake_case agent id extracted from "AG-XX (Human Name)" —
    # the tasks.yaml agent field must reference the agents.yaml key, which
    # is always the snake_case name (never the AG-XX id).
    agent_val = task.get('agent_snake') or task.get('agent', '')

    task_block = f"""## TASK A GERAR

**ID:** {task.get('id', '')}
**Nome (chave YAML):** {task_name}
**Agent (use EXATAMENTE este valor em `agent:`):** {agent_val}
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
