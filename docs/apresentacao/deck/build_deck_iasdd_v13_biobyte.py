# -*- coding: utf-8 -*-
"""V13 — NÃO sobrescreve a V12. A V12 inteira + duas lâminas de infraestrutura (v13_mudancas)."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decklib as D
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

import build_deck_iasdd_v10_biobyte as V10
import build_deck_iasdd_v11_biobyte as V11
import build_deck_iasdd_v12_biobyte as V12
import v13_mudancas
import v13_falas

OUT = HERE / "output" / "apresentacao_iasdd_v13_biobyte.pptx"

SLIDES = v13_falas.aplicar(v13_mudancas.aplicar(V12.SLIDES))
TOTAL = len(SLIDES)
V10.TOTAL = V11.TOTAL = V12.TOTAL = TOTAL
V12.SLIDES = SLIDES   # o sumário (agenda) lê os blocos daqui


def _maquinas(prs, s, n):
    """duas máquinas lado a lado: configuração e para que serve"""
    sl = D._blank(prs); b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    gap = 0.3
    w = (D.SW - 1.2 - gap) / 2
    y0, h = 2.05, 3.85
    for k, (nome, papel, specs, uso) in enumerate(s["maquinas"]):
        x0 = 0.6 + k * (w + gap)
        D._rect(sl, x0, y0, w, h, fill=c3, rounded=True, radius=0.06)
        D._rect(sl, x0, y0, w, 0.62, fill=c1, rounded=True, radius=0.2)
        D._txt(sl, x0 + 0.3, y0, w - 0.6, 0.62,
               [[(nome, {"size": 18, "bold": True, "color": D.WHITE}),
                 ("   " + papel, {"size": 14, "color": D.WHITE})]], anchor=MSO_ANCHOR.MIDDLE)
        linhas = [[("▸  " + t, {"size": 15.5, "color": D.INK})] for t in specs]
        D._txt(sl, x0 + 0.35, y0 + 0.85, w - 0.6, 1.9, linhas, space_after=5)
        D._rect(sl, x0 + 0.3, y0 + 2.75, w - 0.6, 0.012, fill=D.LINE)
        D._txt(sl, x0 + 0.35, y0 + 2.85, w - 0.6, 0.95,
               [[("Para quê  ", {"size": 14.5, "bold": True, "color": c1}), (uso, {"size": 14.5, "color": D.INK})]],
               anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.05)
    D.callout(sl, b, [(s["nota"], {"size": 14.5, "color": D.INK})], x=0.6, y=y0 + h + 0.18, h=0.82, kind="good")
    D.footer(sl, b, n, TOTAL); D.notes(sl, s.get("fala", ""))
    return sl


DESENHO = dict(V12.DESENHO)
DESENHO["maquinas"] = _maquinas


def build():
    prs = D.new_prs()
    for i, s in enumerate(SLIDES, start=1):
        fn = DESENHO[s["tipo"]]
        if s["tipo"] == "capa":
            fn(prs, s)
        else:
            fn(prs, s, i)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    return OUT


if __name__ == "__main__":
    caminho = build()
    palavras = sum(len(s.get("fala", "").split()) for s in SLIDES)
    video = sum(s.get("minutos", 0) for s in SLIDES if s["tipo"] == "video")
    print("gravado: %s" % caminho)
    print("lâminas: %d" % TOTAL)
    print("palavras de narração: %d  (%.1f min a 135 palavras/min)" % (palavras, palavras / 135.0))
    print("vídeos: %g min" % video)
