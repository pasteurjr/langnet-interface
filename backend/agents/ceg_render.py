"""Renderiza um Grafo de Causa-Efeito (CEG) como SVG (estilo Fig.5 do artigo):
causas à esquerda, portas ∧/∨/¬ no meio, efeitos à direita; + tabela de decisão."""
from __future__ import annotations
from typing import Any, Dict, List
from agents.ceg_engine import build_decision_table

_GATE = {"and": "∧", "or": "∨", "not": "¬"}


def ceg_to_svg(ceg: dict) -> str:
    causes = ceg.get("causes", [])
    effects = ceg.get("effects", [])
    rules = {r["effect"]: r["expr"] for r in ceg.get("rules", [])}

    W = 1180
    pad_top = 60
    row_h = 86
    n = max(len(causes), len(effects))
    H = pad_top + n * row_h + 40

    cause_x, cause_w = 30, 250
    effect_x, effect_w = W - 300, 270
    gate_r = 16

    cause_y = {c["id"]: pad_top + i * row_h + 24 for i, c in enumerate(causes)}
    effect_y = {e["id"]: pad_top + i * row_h + 24 for i, e in enumerate(effects)}

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" preserveAspectRatio="xMinYMin meet" '
             f'font-family="Inter,Arial,sans-serif">']
    parts.append(f'<rect width="{W}" height="{H}" fill="#f8fafc"/>')
    parts.append(f'<text x="30" y="34" font-size="18" font-weight="700" fill="#1a56db">Grafo de Causa-Efeito — {ceg.get("uc","")}</text>')
    parts.append(f'<text x="{cause_x}" y="{pad_top-12}" font-size="12" font-weight="700" fill="#64748b">CAUSAS (ações do ator)</text>')
    parts.append(f'<text x="{effect_x}" y="{pad_top-12}" font-size="12" font-weight="700" fill="#64748b">EFEITOS (respostas do sistema)</text>')

    edges: List[str] = []
    nodes: List[str] = []
    gate_counter = [0]

    def draw_expr(expr: Any, x: float, y: float) -> Dict[str, float]:
        """Desenha a subárvore da expressão; retorna a âncora (x,y) do nó-raiz."""
        if isinstance(expr, str):  # causa (folha)
            cy = cause_y.get(expr, y)
            return {"x": cause_x + cause_w, "y": cy, "neg": False}
        op = expr.get("op")
        if op == "not":
            child = draw_expr(expr.get("arg"), x - 60, y)
            # bolha de negação
            bx, by = child["x"] + 34, child["y"]
            nodes.append(f'<circle cx="{bx}" cy="{by}" r="9" fill="#fff" stroke="#dc2626" stroke-width="1.5"/>'
                         f'<text x="{bx}" y="{by+4}" font-size="12" text-anchor="middle" fill="#dc2626">¬</text>')
            edges.append(f'<line x1="{child["x"]}" y1="{child["y"]}" x2="{bx-9}" y2="{by}" stroke="#94a3b8"/>')
            return {"x": bx + 9, "y": by, "neg": True}
        # and / or
        gate_counter[0] += 1
        args = expr.get("args", [])
        childs = []
        spread = 30 if len(args) > 1 else 0
        for i, a in enumerate(args):
            yy = y + (i - (len(args) - 1) / 2) * spread
            childs.append(draw_expr(a, x - 90, yy))
        gy = sum(c["y"] for c in childs) / len(childs) if childs else y
        gx = x
        for c in childs:
            edges.append(f'<line x1="{c["x"]}" y1="{c["y"]}" x2="{gx-gate_r}" y2="{gy}" stroke="#94a3b8"/>')
        nodes.append(f'<circle cx="{gx}" cy="{gy}" r="{gate_r}" fill="#eef2ff" stroke="#6366f1" stroke-width="1.5"/>'
                     f'<text x="{gx}" y="{gy+5}" font-size="15" text-anchor="middle" fill="#4338ca">{_GATE.get(op,"?")}</text>')
        return {"x": gx + gate_r, "y": gy, "neg": False}

    # causas
    for c in causes:
        y = cause_y[c["id"]]
        desc = (c["desc"][:40] + "…") if len(c["desc"]) > 40 else c["desc"]
        nodes.append(f'<rect x="{cause_x}" y="{y-16}" width="{cause_w}" height="32" rx="7" fill="#fff" stroke="#cbd5e1"/>'
                     f'<text x="{cause_x+10}" y="{y-2}" font-size="11" font-weight="700" fill="#334155">{c["id"]}</text>'
                     f'<text x="{cause_x+10}" y="{y+12}" font-size="10" fill="#64748b">{_esc(desc)}</text>')

    # efeitos + suas expressões
    for e in effects:
        y = effect_y[e["id"]]
        desc = (e["desc"][:42] + "…") if len(e["desc"]) > 42 else e["desc"]
        nodes.append(f'<rect x="{effect_x}" y="{y-16}" width="{effect_w}" height="32" rx="7" fill="#eff6ff" stroke="#93c5fd"/>'
                     f'<text x="{effect_x+10}" y="{y-2}" font-size="11" font-weight="700" fill="#1d4ed8">{e["id"]}</text>'
                     f'<text x="{effect_x+10}" y="{y+12}" font-size="10" fill="#3b82f6">{_esc(desc)}</text>')
        expr = rules.get(e["id"])
        if expr is not None:
            root = draw_expr(expr, effect_x - 80, y)
            edges.append(f'<line x1="{root["x"]}" y1="{root["y"]}" x2="{effect_x}" y2="{y}" stroke="#94a3b8"/>')

    parts.append("".join(edges))
    parts.append("".join(nodes))
    parts.append("</svg>")
    return "".join(parts)


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def ceg_full_html(ceg: dict) -> str:
    """SVG do grafo + tabela de decisão em HTML."""
    svg = ceg_to_svg(ceg)
    cols = build_decision_table(ceg)
    cause_ids = [c["id"] for c in ceg.get("causes", [])]
    effect_ids = [e["id"] for e in ceg.get("effects", [])]
    def cell(v):
        if v is True: return "1"
        if v is False: return "0"
        return "X"
    header = "".join(f"<th>C{i+1}</th>" for i in range(len(cols)))
    rows = ""
    for cid in cause_ids:
        rows += f"<tr><td class='lbl'>{cid}</td>" + "".join(f"<td>{cell(c['causes'][cid])}</td>" for c in cols) + "</tr>"
    rows += "<tr class='sep'><td colspan='%d'></td></tr>" % (len(cols)+1)
    for eid in effect_ids:
        rows += f"<tr><td class='lbl eff'>{eid}</td>" + "".join(f"<td class='{'on' if c['effects'].get(eid) else ''}'>{'1' if c['effects'].get(eid) else '0'}</td>" for c in cols) + "</tr>"
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>
body{{font-family:Inter,Arial,sans-serif;background:#f1f5f9;margin:0;padding:20px}}
.card{{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-bottom:18px}}
h2{{color:#1a56db;margin:4px 0 12px}}
table{{border-collapse:collapse;font-size:13px}}
th,td{{border:1px solid #cbd5e1;padding:5px 12px;text-align:center}}
td.lbl{{font-weight:700;background:#f8fafc;text-align:left}}
td.eff{{color:#1d4ed8}} td.on{{background:#dcfce7;font-weight:700;color:#166534}}
tr.sep td{{border:none;height:6px}}
</style></head><body>
<div class="card">{svg}</div>
<div class="card"><h2>Tabela de Decisão — {ceg.get('uc','')}</h2>
<table><tr><th></th>{header}</tr>{rows}</table>
<p style="color:#64748b;font-size:12px;margin-top:10px">Cada coluna (C1, C2, …) é um caso de teste. 1=verdadeiro, 0=falso, X=indiferente (don't-care).</p>
</div></body></html>"""
