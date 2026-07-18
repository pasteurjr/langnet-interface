"""
Motor determinístico do Grafo de Causa-Efeito (CEG).

Implementa o método do Pasteur Ottoni ("Testes de Caixa Branca e Caixa-Preta",
seção 5.2): a partir de um grafo causa-efeito (causas = ações do ator, efeitos =
respostas do sistema, ligados por portas ~/^/v e restrições S/E/C/M), gera a
TABELA DE DECISÃO minimizada — "para cada efeito, gerar combinações entre causas
que façam com que ele seja ativado" — e daí um caso de teste por coluna.

Esta parte é 100% determinística (álgebra booleana), sem LLM.

Formato do CEG (dict):
{
  "uc": "UC-001",
  "causes":  [{"id":"c1","desc":"..."}, ...],
  "effects": [{"id":"e1","desc":"..."}, ...],
  "rules":   [{"effect":"e1","expr": <expr>}, ...],   # expr de ativação do efeito
  "constraints": [{"type":"E","causes":["c1","c2"]}, ...]
}

expr := "cX" | {"op":"not","arg":<expr>}
             | {"op":"and","args":[<expr>,...]}
             | {"op":"or","args":[<expr>,...]}

Restrições intercausas (notação do artigo):
  S (Simultâneas)        — todas as causas do grupo têm o MESMO valor
  E (Mutuamente Exclus.) — no máximo UMA verdadeira
  O (Uma e só uma)       — exatamente uma verdadeira (variante de E+I)
  C (Consequentes)       — se a 1ª é verdadeira, as demais também (requires)
  M (Mascaradas)         — máscara entre EFEITOS (um efeito mascara outro)
"""
from __future__ import annotations
from itertools import product
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────────────────────
# Avaliação de expressão booleana
# ─────────────────────────────────────────────────────────────
def eval_expr(expr: Any, assign: Dict[str, bool]) -> bool:
    if isinstance(expr, str):
        return bool(assign.get(expr, False))
    if not isinstance(expr, dict):
        return False
    op = expr.get("op")
    if op == "not":
        return not eval_expr(expr.get("arg"), assign)
    if op == "and":
        return all(eval_expr(a, assign) for a in expr.get("args", []))
    if op == "or":
        return any(eval_expr(a, assign) for a in expr.get("args", []))
    if op in ("id", "identity"):
        return eval_expr(expr.get("arg"), assign)
    return False


def eval_expr3(expr: Any, assign: Dict[str, Optional[bool]]) -> Optional[bool]:
    """Avaliação de 3 valores: True / False / None(indeterminado). Causa don't-care
    entra como None. Um efeito só 'dispara' se resultar definitivamente True."""
    if isinstance(expr, str):
        return assign.get(expr, None)
    if not isinstance(expr, dict):
        return None
    op = expr.get("op")
    if op == "not":
        v = eval_expr3(expr.get("arg"), assign)
        return None if v is None else (not v)
    if op == "and":
        vals = [eval_expr3(a, assign) for a in expr.get("args", [])]
        if any(v is False for v in vals):
            return False
        if any(v is None for v in vals):
            return None
        return True
    if op == "or":
        vals = [eval_expr3(a, assign) for a in expr.get("args", [])]
        if any(v is True for v in vals):
            return True
        if any(v is None for v in vals):
            return None
        return False
    if op in ("id", "identity"):
        return eval_expr3(expr.get("arg"), assign)
    return None


def expr_causes(expr: Any, acc: Optional[set] = None) -> set:
    """Causas (folhas cX) que aparecem numa expressão."""
    if acc is None:
        acc = set()
    if isinstance(expr, str):
        acc.add(expr)
    elif isinstance(expr, dict):
        if "arg" in expr:
            expr_causes(expr["arg"], acc)
        for a in expr.get("args", []):
            expr_causes(a, acc)
    return acc


# ─────────────────────────────────────────────────────────────
# Restrições entre causas
# ─────────────────────────────────────────────────────────────
def _cause_constraints_ok(assign: Dict[str, bool], constraints: List[dict]) -> bool:
    for c in constraints or []:
        t = (c.get("type") or "").upper()
        cs = [x for x in c.get("causes", []) if x in assign]
        if not cs:
            continue
        vals = [assign[x] for x in cs]
        if t == "E":  # mutuamente exclusivas: no máximo uma verdadeira
            if sum(vals) > 1:
                return False
        elif t == "O":  # uma e só uma
            if sum(vals) != 1:
                return False
        elif t == "S":  # simultâneas: todas iguais
            if len(set(vals)) > 1:
                return False
        elif t == "C":  # consequentes: cs[0] verdadeira ⇒ demais verdadeiras
            if vals[0] and not all(vals[1:]):
                return False
    return True


def _effect_mask(effects_val: Dict[str, bool], constraints: List[dict]) -> Dict[str, bool]:
    """Aplica máscara M entre efeitos: se o 1º está ativo, mascara (força falso) os demais."""
    out = dict(effects_val)
    for c in constraints or []:
        if (c.get("type") or "").upper() == "M":
            grp = c.get("effects") or c.get("causes") or []
            if grp and out.get(grp[0]):
                for e in grp[1:]:
                    out[e] = False
    return out


# ─────────────────────────────────────────────────────────────
# Geração da tabela de decisão (passo 2 do método)
# ─────────────────────────────────────────────────────────────
def build_decision_table(ceg: dict) -> List[dict]:
    """Para CADA efeito, gera as combinações de causas (sobre as causas envolvidas
    na sua expressão) que o ativam, respeitando as restrições. Causas não
    envolvidas ficam como 'X' (don't-care). Cada combinação vira uma coluna.

    Retorna lista de colunas:
      {"target": "eX", "causes": {cid: True|False|"X"}, "effects": {eid: bool}}
    """
    cause_ids = [c["id"] for c in ceg.get("causes", [])]
    effect_ids = [e["id"] for e in ceg.get("effects", [])]
    constraints = ceg.get("constraints", [])
    rules = {r["effect"]: r["expr"] for r in ceg.get("rules", [])}

    columns: List[dict] = []
    seen = set()

    for eid in effect_ids:
        expr = rules.get(eid)
        if expr is None:
            continue
        involved = [c for c in cause_ids if c in expr_causes(expr)]
        if not involved:
            continue
        # enumera só as causas envolvidas; demais = don't-care
        for combo in product([True, False], repeat=len(involved)):
            partial = dict(zip(involved, combo))
            # completa as não-envolvidas como False só para avaliar restrições/efeitos
            full = {c: partial.get(c, False) for c in cause_ids}
            if not _cause_constraints_ok(full, constraints):
                continue
            if not eval_expr(expr, full):
                continue  # combinação não ativa o efeito
            # efeitos com lógica de 3 valores: don't-care = None (indeterminado).
            # Assim um efeito só marca 1 se for definitivamente verdadeiro com as
            # causas SETADAS — evita coativação espúria (fiel ao método).
            assign3 = {c: (partial[c] if c in partial else None) for c in cause_ids}
            ev = {x: eval_expr3(rules.get(x), assign3) for x in effect_ids}
            ev = _effect_mask(ev, constraints)
            causes_col = {c: (partial[c] if c in partial else "X") for c in cause_ids}
            key = (eid, tuple(sorted((k, str(v)) for k, v in causes_col.items())))
            if key in seen:
                continue
            seen.add(key)
            columns.append({"target": eid, "causes": causes_col, "effects": ev})
    return columns


def decision_table_to_cases(ceg: dict, columns: List[dict]) -> List[dict]:
    """Converte cada coluna num caso de teste legível."""
    cdesc = {c["id"]: c["desc"] for c in ceg.get("causes", [])}
    edesc = {e["id"]: e["desc"] for e in ceg.get("effects", [])}
    uc = ceg.get("uc", "UC")
    cases = []
    for i, col in enumerate(columns, 1):
        entradas = []
        for cid, val in col["causes"].items():
            if val == "X":
                continue
            entradas.append({"causa": cid, "desc": cdesc.get(cid, cid), "verdadeira": bool(val)})
        esperado = {"efeito": col["target"], "desc": edesc.get(col["target"], col["target"])}
        cases.append({
            "id": f"TC-{uc}-{i:02d}",
            "uc": uc,
            "entradas": entradas,          # condições de entrada (ações do ator)
            "efeito_esperado": esperado,   # resposta do sistema esperada
            "causes": col["causes"],
            "effects": col["effects"],
        })
    return cases


def generate_test_cases(ceg: dict) -> dict:
    cols = build_decision_table(ceg)
    cases = decision_table_to_cases(ceg, cols)
    return {"uc": ceg.get("uc"), "decision_table": cols, "test_cases": cases,
            "n_causes": len(ceg.get("causes", [])), "n_effects": len(ceg.get("effects", [])),
            "n_cases": len(cases)}
