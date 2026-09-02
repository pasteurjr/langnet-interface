#!/usr/bin/env python3
"""Expande as linhas **TELA:** das cenas 23/24/25 com a lista REAL de capturas em shots/.

As cenas do sistema gerado referenciavam faixas ("86-… … 106-…"), então o PDF embutia só
as duas pontas. Aqui a faixa vira a lista explícita, na ordem numérica — o PDF passa a
mostrar todas. Idempotente: recalcula a partir do diretório a cada execução.
"""
import re
from pathlib import Path

BASE = Path(__file__).parent; SHOTS = BASE / "shots"; SRC = BASE / "narracao_log.md"

def files(pat):
    return sorted((f.name for f in SHOTS.glob("*.png") if re.match(pat, f.name)),
                  key=lambda n: int(n.split("-")[0]))

# grupos: tour das telas, formulários (última rodada = maior faixa), executor Petri
tour  = files(r"\d+-app-(home|tela-)")
forms = files(r"\d+-app-form-")
petri = files(r"\d+-app-petri-")
if forms:                                  # mantém só a rodada FINAL (bloco contíguo mais recente)
    idx = [int(f.split("-")[0]) for f in forms]
    corte = idx[-1] - 23 if len(idx) >= 24 else idx[0]
    forms = [f for f in forms if int(f.split("-")[0]) >= corte]

alvo = {"Cena 23": tour, "Cena 24": forms, "Cena 25": petri}
md = SRC.read_text(encoding="utf-8"); out = []; cena = None
for ln in md.splitlines():
    m = re.match(r"^## (Cena \d+[a-z]?)", ln)
    if m: cena = m.group(1)
    if cena in alvo and ln.startswith("**TELA:**") and alvo[cena]:
        out.append("**TELA:** " + ", ".join(alvo[cena]))
    else:
        out.append(ln)
SRC.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"atualizado — Cena 23: {len(tour)} telas · Cena 24: {len(forms)} · Cena 25: {len(petri)}")
