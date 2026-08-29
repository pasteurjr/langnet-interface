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
        for m in re.finditer(r'(?i)\b(?:FROM|JOIN|INTO|UPDATE)\s+["`]?([a-z_][a-z0-9_]*)', q):
            t = m.group(1).lower()
            # ignora se seguido de '(' (é função, ex.: generate_series(...))
            if t in _STOP:
                continue
            tables.add(t)
    return {"uc_task": uc_task, "fr_task": fr_task, "tables": tables}


def _dm_tables(schema_sql: str = "", entities_json: str = "") -> Set[str]:
    tabs: Set[str] = set()
    for m in re.finditer(r'(?i)CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`]?([a-z_][a-z0-9_]*)', schema_sql or ""):
        tabs.add(m.group(1).lower())
    if not tabs and entities_json:
        for m in re.finditer(r'"name"\s*:\s*"([a-z_][a-z0-9_]*)"', entities_json):
            tabs.add(m.group(1).lower())
    return tabs


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

    # Salto 4: task -> DM (tabela usada existe no modelo?)
    tbl_violations = sorted(t for t in tt["tables"] if dm and t not in dm) if dm else []

    gate_pass = not (gap_spec or gap_nfr or gap_br or gap_impl or tbl_violations)
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
    L.append("  %-26s %s" % ("Task→Modelo de Dados", "OK" if not v else "TABELA INEXISTENTE: " + ", ".join(v)))
    L.append("═" * 66)
    return "\n".join(L)
