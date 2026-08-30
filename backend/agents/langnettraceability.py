"""
GUARDRAIL DE RASTREABILIDADE (LangNet) — portão determinístico que mede, salto a
salto do pipeline, se TODO requisito (FR/NFR/BR) chega à Especificação, ao ATS, ao
tasks.yaml (implementação) e se cada task usa tabela que existe no Modelo de Dados.

Motivação (cobrado pelo user 28/08/2026): a cascata "funcionava" (o calculador
rodava) mas 19/37 FR do uso-do-solo v3 NÃO tinham nenhuma task — sumiam no
caminho — e nada reclamava. O único guardrail existente era "≥1 task por UC"; não
havia "≥1 task por FR". Este módulo fecha isso: é chamável na geração (para
SURFAR as lacunas) e como CLI (tools/langnet_trace_gate.py).

100% determinístico (regex/estrutura), sem LLM. Tolerante a YAML inválido.
"""
from __future__ import annotations
import re
from typing import Dict, List, Set, Any

_FR = r'\bFR-\d{2,3}\b'
_NFR = r'\bNFR-\d{2,3}\b'
_BR = r'\b(?:BR|RN)-\d{2,3}\b'
_UC = r'\bUC-\d{2,3}\b'


def _ids(text: str, pat: str) -> List[str]:
    seen = {}
    for m in re.findall(pat, text or ""):
        seen[m] = True
    return sorted(seen, key=lambda x: (len(x), x))


def _fr_uc_from_matrix(spec_md: str) -> Dict[str, Set[str]]:
    """FR->{UC} a partir da matriz de rastreabilidade da spec: qualquer linha que
    co-localize um ou mais FR e um ou mais UC vira aresta(s)."""
    fr2uc: Dict[str, Set[str]] = {}
    for ln in (spec_md or "").splitlines():
        frs = re.findall(_FR, ln)
        ucs = re.findall(_UC, ln)
        if frs and ucs:
            for f in frs:
                fr2uc.setdefault(f, set()).update(ucs)
    return fr2uc


def _task_traceability(tasks_yaml: str) -> Dict[str, Any]:
    """Extrai, por task, os UC/FR do bloco `traceability:` e as tabelas usadas em
    SQL. Tolerante a YAML inválido (regex, não yaml.safe_load)."""
    uc_task: Set[str] = set()
    fr_task: Set[str] = set()
    # blocos traceability: uc: ... / fr: ...
    for m in re.finditer(r'traceability:\s*\n\s*uc:\s*(.+)\n\s*fr:\s*(.+)', tasks_yaml or ""):
        uc_task.update(re.findall(_UC, m.group(1)))
        fr_task.update(re.findall(_FR, m.group(2)))

    # QUALIDADE: conjunto de FR citados por cada task (nome de topo -> {FR}). Usado para
    # medir cobertura EXCLUSIVA (quantos FR uma task é a ÚNICA a cobrir): stuffing REAL é
    # uma task que SOZINHA implementa muitos FR — não uma que apenas super-cita FR que já
    # têm task focada própria (isso é poluição de citação, não lump de implementação).
    per_task: Dict[str, Set[str]] = {}
    for m in re.finditer(r'(?m)^([a-z_][a-z0-9_]*):\s*$', tasks_yaml or ""):
        name = m.group(1)
        start = m.end()
        nxt = re.search(r'(?m)^[a-z_][a-z0-9_]*:\s*$', (tasks_yaml or "")[start:])
        body = (tasks_yaml or "")[start:start + (nxt.start() if nxt else len(tasks_yaml or ""))]
        fset = set(re.findall(_FR, body))
        if fset:
            per_task[name] = fset
    # tabelas citadas em SQL — SÓ dentro de query="..." (evita pegar prose/PT) e com
    # stoplist de keywords/funções/aliases, senão o portão gera falso-positivo (com, em,
    # na, set, generate_series, subqueries...). Também ignora alias após o nome da tabela.
    _STOP = {
        "com", "em", "na", "no", "set", "as", "on", "and", "or", "where", "select",
        "values", "using", "lateral", "generate_series", "unnest", "cast", "coalesce",
        "st_intersection", "st_contains", "st_intersects", "st_area", "st_dwithin",
        "only", "distinct", "all", "case", "when", "then", "else", "end", "null",
    }
    tables: Set[str] = set()
    for q in re.findall(r'query="([^"]+)"', tasks_yaml or ""):
        # nomes de CTE (WITH x AS (...), , y AS (...)) NÃO são tabelas do modelo
        cte = set(m.group(1).lower() for m in re.finditer(r'(?i)(?:WITH|,)\s+([a-z_][a-z0-9_]*)\s+AS\s*\(', q))
        for m in re.finditer(r'(?i)\b(?:FROM|JOIN|INTO|UPDATE)\s+["`]?([a-z_][a-z0-9_]*)', q):
            t = m.group(1).lower()
            if t in _STOP or t in cte:
                continue
            tables.add(t)
    return {"uc_task": uc_task, "fr_task": fr_task, "tables": tables, "per_task_fr": per_task}


def _dm_tables(schema_sql: str = "", entities_json: str = "") -> Set[str]:
    tabs: Set[str] = set()
    for m in re.finditer(r'(?i)CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`]?([a-z_][a-z0-9_]*)', schema_sql or ""):
        tabs.add(m.group(1).lower())
    if not tabs and entities_json:
        for m in re.finditer(r'"name"\s*:\s*"([a-z_][a-z0-9_]*)"', entities_json):
            tabs.add(m.group(1).lower())
    return tabs


def _dm_columns(schema_sql: str = "") -> Dict[str, Set[str]]:
    """{tabela -> {colunas}} a partir do DDL. Base do check Task→DM de COLUNA (uma coluna
    citada num query= tem de existir em alguma tabela do FROM/JOIN — senão o SQL quebra no
    runtime, como o `SELECT area_construida FROM imoveis` que só descobrimos no E2E)."""
    cols: Dict[str, Set[str]] = {}
    for blk in re.split(r'(?i)\bCREATE\s+TABLE\s+', schema_sql or "")[1:]:
        m = re.match(r'["`]?([a-z_]\w*)', blk)
        if not m:
            continue
        cset: Set[str] = set()
        body = blk[blk.find('('):] if '(' in blk else ''
        for line in body.split('\n'):
            cm = re.match(r'\s*["`]?([a-z_]\w*)["`]?\s+[A-Za-z]', line.strip())
            if cm and cm.group(1).upper() not in ('FOREIGN', 'PRIMARY', 'UNIQUE', 'CHECK', 'CONSTRAINT'):
                cset.add(cm.group(1).lower())
        cols[m.group(1).lower()] = cset
    return cols


def _query_column_violations(tasks_yaml: str, dm_cols: Dict[str, Set[str]]) -> List:
    """Para cada query= das tasks, valida que as colunas da lista do SELECT existem em
    alguma tabela do FROM/JOIN. Conservador: ignora funções (col(...)), '*', apelidos AS e
    literais — só marca coluna nua fora do schema. Devolve [(tabela_from, coluna)]."""
    if not dm_cols:
        return []
    import difflib as _dl
    real = set(dm_cols.keys())

    def _resolve(t: str) -> str:
        t = t.lower()
        if t in real:
            return t
        cand = [d for d in real if t in d or d in t] or _dl.get_close_matches(t, list(real), n=1, cutoff=0.6)
        return cand[0] if cand else ''
    viol = []
    for q in re.findall(r'query="([^"]+)"', tasks_yaml or ""):
        tabs = [_resolve(m.group(1)) for m in re.finditer(r'(?i)\b(?:FROM|JOIN)\s+["`]?([a-z_]\w*)', q)]
        tabs = [t for t in tabs if t]
        if not tabs:
            continue
        valid = set()
        for t in tabs:
            valid |= dm_cols.get(t, set())
        if not valid:
            continue
        ms = re.search(r'(?is)\bSELECT\b(.+?)\bFROM\b', q)
        if not ms:
            continue
        seg = ms.group(1)
        parts, depth, cur = [], 0, ''
        for ch in seg:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            if ch == ',' and depth == 0:
                parts.append(cur); cur = ''
            else:
                cur += ch
        parts.append(cur)
        for c in parts:
            c = c.strip()
            if not c or '(' in c or '*' in c or ' as ' in c.lower():
                continue
            c = c.split('.')[-1].strip().strip('"`')
            if re.match(r'^[a-z_]\w*$', c) and c not in valid:
                viol.append((tabs[0], c))
    # dedup preservando ordem
    seen = set()
    return [x for x in viol if not (x in seen or seen.add(x))]


def _query_join_violations(tasks_yaml: str) -> List:
    """Query que referencia `alias.col` com o alias FORA do FROM/JOIN (ex.: spatial
    ST_Intersects(a.geometria, i.geometria) com `i` = imoveis nunca juntado). O SQL
    quebra no runtime ("missing FROM-clause entry for table i"). Determinístico."""
    _KW = {"on", "where", "join", "left", "right", "inner", "outer", "cross", "full",
           "group", "order", "limit", "having", "using", "and", "or", "as", "natural",
           "select", "from", "set", "values", "into"}
    def _add_tbl(present, item):
        item = re.split(r'(?i)\bON\b', item.strip())[0].strip()  # tira "ON <cond>"
        tm = re.match(r'["`]?(\w+)["`]?(?:\s+(?:AS\s+)?["`]?([a-zA-Z_]\w*)["`]?)?', item)
        if tm:
            present.add(tm.group(1).lower())
            if tm.group(2) and tm.group(2).lower() not in _KW:
                present.add(tm.group(2).lower())

    viol = []
    for q in re.findall(r'query="([^"]+)"', tasks_yaml or ""):
        present = set()
        # UPDATE/INTO
        for m in re.finditer(r'(?i)\b(?:UPDATE|INTO)\s+["`]?(\w+)["`]?', q):
            present.add(m.group(1).lower())
        # cláusula FROM ... (até WHERE/GROUP/ORDER/LIMIT/HAVING) — tabelas separadas por
        # vírgula (cross join clássico `FROM a, b`) E por JOIN. Sem isso o portão dava
        # falso-positivo em `FROM apps a, imoveis i` (achava `i` fora do FROM).
        fm = re.search(r'(?is)\bFROM\b(.+?)(?:\bWHERE\b|\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|\bHAVING\b|$)', q)
        if fm:
            for part in re.split(r'(?i)(?:\b(?:INNER|LEFT|RIGHT|FULL|CROSS|OUTER|NATURAL)\b\s*)*\bJOIN\b|,', fm.group(1)):
                _add_tbl(present, part)
        if not present:
            continue
        for al in set(re.findall(r'\b([a-zA-Z_]\w*)\.\w+', q)):
            if al.lower() not in present and al.lower() not in _KW:
                viol.append((al, q[:48]))
    seen = set()
    return [x for x in viol if not (x in seen or seen.add(x))]


def complete_matrix(spec_md: str, requirements_md: str):
    """GARANTE deterministicamente que TODO FR tenha linha na matriz FR→UC. Para cada
    FR órfão (sem UC na matriz), mapeia ao UC de MAIOR sobreposição de palavras (grounded
    no texto do próprio UC — não é chute cego). Devolve (spec_aumentada, added) com
    added=[(fr, uc, titulo)]. É o passo que transforma "prompt que às vezes esquece" em
    garantia — o LLM leva a 31/37, este passo fecha os 6 restantes → 37/37."""
    fr = _ids(requirements_md, _FR)
    fr2uc = _fr_uc_from_matrix(spec_md)
    orphans = [f for f in fr if f not in fr2uc]
    if not orphans:
        return spec_md, []
    ucs = _ids(spec_md, _UC)
    # bloco de texto por UC (para medir sobreposição temática)
    uc_blocks: Dict[str, str] = {}
    parts = re.split(r'(UC-\d{2,3})', spec_md)
    for i in range(1, len(parts) - 1, 2):
        uc_blocks[parts[i]] = uc_blocks.get(parts[i], '') + ' ' + parts[i + 1][:800]

    def _words(s: str) -> Set[str]:
        return set(re.findall(r'[a-zà-ÿ]{4,}', (s or '').lower()))

    added = []
    rows = []
    for f in orphans:
        m = re.search(re.escape(f) + r'\s*\|[^\|]*\|\s*([^\|]+)\|', requirements_md)
        title = m.group(1).strip() if m else f
        fw = _words(title)
        best, best_sc = (ucs[0] if ucs else 'UC-001'), -1
        for uc, body in uc_blocks.items():
            sc = len(fw & _words(body))
            if sc > best_sc:
                best, best_sc = uc, sc
        added.append((f, best, title))
        rows.append("| %s | %s | %s | — |" % (f, title[:40], best))
    block = ("\n\n### 13.2 Completude de rastreabilidade (determinística)\n"
             "Linhas garantidas pelo guardrail para que TODO FR tenha ≥1 UC "
             "(mapeamento por maior sobreposição temática com o texto do UC):\n\n"
             "| Requisito | Título | UC que o realiza | RN |\n|---|---|---|---|\n"
             + "\n".join(rows) + "\n")
    return spec_md + block, added


def audit(requirements_md: str, spec_md: str = "", ats_md: str = "",
          tasks_yaml: str = "", schema_sql: str = "", entities_json: str = "") -> Dict[str, Any]:
    """Roda a auditoria de rastreabilidade e devolve estrutura com cobertura por
    salto, lacunas e o veredito do portão (gate_pass)."""
    fr = _ids(requirements_md, _FR)
    nfr = _ids(requirements_md, _NFR)
    br = _ids(requirements_md, _BR)

    fr_spec = set(_ids(spec_md, _FR))
    nfr_spec = set(_ids(spec_md, _NFR))
    br_spec = set(_ids(spec_md, _BR))
    fr2uc = _fr_uc_from_matrix(spec_md)

    tt = _task_traceability(tasks_yaml)
    uc_task, fr_task = tt["uc_task"], tt["fr_task"]
    dm = _dm_tables(schema_sql, entities_json)

    def titulo(fid: str) -> str:
        m = re.search(re.escape(fid) + r'\s*\|[^\|]*\|\s*([^\|]+)\|', requirements_md or "")
        return (m.group(1).strip()[:60] if m else "")

    # Salto 1: req -> spec (presença textual)
    gap_spec = [f for f in fr if f not in fr_spec]
    gap_nfr = [x for x in nfr if x not in nfr_spec]
    gap_br = [x for x in br if x not in br_spec]

    # Salto 2: FR na MATRIZ da spec (mapeado a UC)
    gap_matrix = [f for f in fr if f not in fr2uc]

    # Salto 3: FR -> implementação (task direto OU via UC->task)
    def implemented(f: str) -> bool:
        return f in fr_task or any(u in uc_task for u in fr2uc.get(f, set()))
    gap_impl = [f for f in fr if not implemented(f)]

    # QUALIDADE de implementação: stuffing REAL = task que SOZINHA cobre muitos FR (é o único
    # lugar que implementa N features). Super-citação (task lista FR que já têm task própria)
    # não conta — mede-se cobertura EXCLUSIVA. Limite = 6.
    _STUFF = 6
    _per_task = tt.get("per_task_fr", {})
    _cov_count: Dict[str, int] = {}
    for _fs in _per_task.values():
        for _f in _fs:
            _cov_count[_f] = _cov_count.get(_f, 0) + 1
    _sole = {n: [f for f in fs if _cov_count.get(f) == 1] for n, fs in _per_task.items()}
    stuffing = sorted(((n, len(s)) for n, s in _sole.items() if len(s) > _STUFF), key=lambda x: -x[1])

    # Salto 4: task -> DM (tabela usada existe no modelo?). Tolera near-match: o code-gen
    # canoniza nomes contra o DM (zonas→zoneamentos, elevacoes→mde_elevacoes), então só é
    # violação REAL se a tabela não existe E não casa (contenção/fuzzy) com nenhuma do DM.
    import difflib as _dl

    def _resolves(t: str) -> bool:
        if t in dm:
            return True
        if any(t in d or d in t for d in dm):
            return True
        return bool(_dl.get_close_matches(t, list(dm), n=1, cutoff=0.6))
    tbl_violations = sorted(t for t in tt["tables"] if dm and not _resolves(t)) if dm else []

    # Salto 4b: task -> DM no nível de COLUNA (o SQL cita coluna que não existe no schema).
    col_violations = _query_column_violations(tasks_yaml, _dm_columns(schema_sql))
    # Salto 4c: query referencia alias.col com o alias fora do FROM/JOIN (JOIN espacial faltante).
    join_violations = _query_join_violations(tasks_yaml)

    gate_pass = not (gap_spec or gap_nfr or gap_br or gap_impl or tbl_violations or stuffing or col_violations or join_violations)
    return {
        "inventory": {"FR": fr, "NFR": nfr, "BR": br, "UC_spec": _ids(spec_md, _UC)},
        "hops": {
            "req_to_spec_FR": {"cov": len(fr) - len(gap_spec), "total": len(fr), "gaps": gap_spec},
            "req_to_spec_NFR": {"cov": len(nfr) - len(gap_nfr), "total": len(nfr), "gaps": gap_nfr},
            "req_to_spec_BR": {"cov": len(br) - len(gap_br), "total": len(br), "gaps": gap_br},
            "spec_matrix_FR_UC": {"cov": len(fr) - len(gap_matrix), "total": len(fr), "gaps": gap_matrix},
            "FR_to_impl": {"cov": len(fr) - len(gap_impl), "total": len(fr),
                           "gaps": [(f, titulo(f)) for f in gap_impl]},
            "task_to_DM": {"violations": tbl_violations},
            "task_to_DM_columns": {"violations": col_violations},
            "task_query_joins": {"violations": join_violations},
            "task_stuffing": {"tasks": stuffing},
        },
        "gate_pass": gate_pass,
    }


def format_report(res: Dict[str, Any]) -> str:
    h = res["hops"]
    inv = res["inventory"]
    L = []
    L.append("═" * 66)
    L.append("  PORTÃO DE RASTREABILIDADE — %s" % ("✅ PASSOU" if res["gate_pass"] else "❌ REPROVADO"))
    L.append("═" * 66)
    L.append("Inventário: %d FR · %d NFR · %d BR · %d UC(spec)" %
             (len(inv["FR"]), len(inv["NFR"]), len(inv["BR"]), len(inv["UC_spec"])))

    def line(nome, hop, show=None):
        g = hop["gaps"]
        L.append("  %-26s %d/%d   %s" % (
            nome, hop["cov"], hop["total"],
            ("GAP: " + ", ".join(str(x) for x in g[:show]) + (" …+%d" % (len(g) - show) if show and len(g) > show else "")) if g else "OK"))

    line("Req→Spec (FR)", h["req_to_spec_FR"])
    line("Req→Spec (NFR)", h["req_to_spec_NFR"])
    line("Req→Spec (BR)", h["req_to_spec_BR"])
    line("Matriz FR→UC (spec)", h["spec_matrix_FR_UC"], show=99)
    imp = h["FR_to_impl"]
    L.append("  %-26s %d/%d   %s" % ("FR→Implementação (task)", imp["cov"], imp["total"],
                                     "OK" if not imp["gaps"] else "GAP (não implementados):"))
    for f, t in imp["gaps"]:
        L.append("       %-8s %s" % (f, t))
    v = h["task_to_DM"]["violations"]
    L.append("  %-26s %s" % ("Task→DM (tabela)", "OK" if not v else "TABELA INEXISTENTE: " + ", ".join(v)))
    cv = h.get("task_to_DM_columns", {}).get("violations") or []
    L.append("  %-26s %s" % ("Task→DM (coluna)",
                             "OK" if not cv else "COLUNA INEXISTENTE: "
                             + ", ".join("%s.%s" % (t, c) for t, c in cv[:8])))
    jv = h.get("task_query_joins", {}).get("violations") or []
    L.append("  %-26s %s" % ("Task→DM (JOIN/FROM)",
                             "OK" if not jv else "ALIAS FORA DO FROM: " + ", ".join(a for a, _ in jv[:8])))
    st = h.get("task_stuffing", {}).get("tasks") or []
    L.append("  %-26s %s" % ("Qualidade (FR por task)",
                             "OK" if not st else "STUFFING (task catch-all): "
                             + ", ".join("%s=%dFR" % (n, k) for n, k in st)))
    L.append("═" * 66)
    return "\n".join(L)
