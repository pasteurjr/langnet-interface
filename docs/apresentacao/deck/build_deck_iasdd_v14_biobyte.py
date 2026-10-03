# -*- coding: utf-8 -*-
"""V14 — NÃO sobrescreve a V13. A V13 + v14_mudancas + v14_falas."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decklib as D
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

import build_deck_iasdd_v10_biobyte as V10
import build_deck_iasdd_v11_biobyte as V11
import build_deck_iasdd_v12_biobyte as V12
import build_deck_iasdd_v13_biobyte as V13
import v14_mudancas
import v14_falas

OUT = HERE / "output" / "apresentacao_iasdd_v14_biobyte.pptx"

SLIDES = v14_falas.aplicar(v14_mudancas.aplicar(V13.SLIDES))
TOTAL = len(SLIDES)
V10.TOTAL = V11.TOTAL = V12.TOTAL = V13.TOTAL = TOTAL
V12.SLIDES = SLIDES   # o sumário (agenda) lê os blocos daqui


def _agenda(prs, s, n):
    """sumário: o histórico e os doze blocos, agrupados nos três pilares"""
    sl = D._blank(prs); b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    blocos = {}
    for x in SLIDES:
        if x["tipo"] == "divisor" or (x["tipo"] == "divisor_simples" and x.get("bloco") == 12):
            blocos.setdefault(x["bloco"], x["titulo"])
    pilares = [("Fundamentos", ["H", 1, 2, 3, 4]), ("Engenharia", [5, 6, 7, 8, 9]), ("Método", [10, 11, 12])]
    gap = 0.25
    w = (D.SW - 1.2 - 2 * gap) / 3
    for k, (pilar, itens) in enumerate(pilares):
        x0 = 0.6 + k * (w + gap)
        cor = D.fam(itens[0] if itens[0] != "H" else 1)[0]
        D._rect(sl, x0, 2.0, w, 0.52, fill=cor, rounded=True, radius=0.2)
        D._txt(sl, x0, 2.0, w, 0.52, [[(pilar.upper(), {"size": 16, "bold": True, "color": D.WHITE})]],
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        y = 2.66
        for nb in itens:
            f1, f2, f3 = D.fam(0 if nb == "H" else nb)
            D._rect(sl, x0, y, w, 0.76, fill=f3, rounded=True, radius=0.12)
            D._rect(sl, x0, y, 0.1, 0.76, fill=f1)
            D._txt(sl, x0 + 0.25, y, 0.55, 0.76, [[("•" if nb == "H" else "%d" % nb, {"size": 20, "bold": True, "color": f1})]],
                   anchor=MSO_ANCHOR.MIDDLE)
            D._txt(sl, x0 + 0.8, y, w - 0.95, 0.76,
                   [[("Histórico da IA" if nb == "H" else blocos.get(nb, ""), {"size": 14.5, "bold": True, "color": D.INK})]],
                   anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0, space_after=0)
            y += 0.85
    D.footer(sl, b, n, TOTAL); D.notes(sl, s.get("fala", ""))
    return sl


def _tabela(prs, s, n):
    """tabela da V10, com larguras de coluna opcionais ("larguras", em polegadas)"""
    sl = V10._tabela(prs, s, n)
    if s.get("larguras"):
        from pptx.util import Inches
        tb = [sh for sh in sl.shapes if sh.has_table][-1].table
        for k, w in enumerate(s["larguras"]):
            tb.columns[k].width = Inches(w)
    return sl


DESENHO = dict(V13.DESENHO)
DESENHO["tabela"] = _tabela
DESENHO["agenda"] = _agenda


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
