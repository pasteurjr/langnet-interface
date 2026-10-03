# -*- coding: utf-8 -*-
"""V12 — NÃO sobrescreve a V11. Conteúdo da V11 + v12_mudancas + v12_falas."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decklib as D
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image

import build_deck_iasdd_v10_biobyte as V10
import build_deck_iasdd_v11_biobyte as V11
import v12_mudancas
import v12_falas

OUT = HERE / "output" / "apresentacao_iasdd_v12_biobyte.pptx"

SLIDES = v12_falas.aplicar(v12_mudancas.aplicar(V11.SLIDES))
TOTAL = len(SLIDES)
V10.TOTAL = TOTAL
V11.TOTAL = TOTAL


def _figura_rotulos(prs, s, n):
    """figura da apresentação-base, com os nomes das camadas escritos acima dela"""
    sl = D._blank(prs); b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    base = V11.BAIXO
    if s.get("rodape"):
        D.callout(sl, b, [(s["rodape"], {"size": 14.5, "color": D.INK})], x=0.6, y=base - 0.78, h=0.78)
        base -= 0.95
    y0, x0, w = 2.55, 0.6, D.SW - 1.2
    h = base - y0
    iw, ih = Image.open(HERE / s["imagem"]).size
    ar = iw / ih
    dw, dh = (w, w / ar) if ar > w / h else (h * ar, h)
    dx = x0 + (w - dw) / 2
    dy = y0 + (h - dh) / 2
    from pptx.util import Inches
    sl.shapes.add_picture(str(HERE / s["imagem"]), Inches(dx), Inches(dy), Inches(dw), Inches(dh))
    for texto, fx in s["rotulos"]:
        cx = dx + fx * dw
        D._rect(sl, cx - 1.35, dy - 0.55, 2.7, 0.42, fill=c3, rounded=True, radius=0.4)
        D._txt(sl, cx - 1.35, dy - 0.55, 2.7, 0.42, [[(texto, {"size": 15, "bold": True, "color": c1})]],
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    D.footer(sl, b, n, TOTAL); D.notes(sl, s.get("fala", ""))
    return sl


PILARES = [("Fundamentos", (1, 4)), ("Engenharia", (5, 9)), ("Método", (10, 12))]


def _agenda(prs, s, n):
    """sumário: os doze blocos, agrupados nos três pilares"""
    sl = D._blank(prs); b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    blocos = {}
    for x in SLIDES:
        if x["tipo"] in ("divisor", "divisor_simples") and x.get("bloco", 0) >= 1 and x["bloco"] not in blocos:
            if x["tipo"] == "divisor_simples" and x["bloco"] != 12:
                continue
            blocos[x["bloco"]] = x["titulo"]
    gap = 0.25
    w = (D.SW - 1.2 - 2 * gap) / 3
    for k, (pilar, (a, z)) in enumerate(PILARES):
        x0 = 0.6 + k * (w + gap)
        cor = D.fam(a)[0]
        D._rect(sl, x0, 2.05, w, 0.55, fill=cor, rounded=True, radius=0.2)
        D._txt(sl, x0, 2.05, w, 0.55, [[(pilar.upper(), {"size": 16, "bold": True, "color": D.WHITE})]],
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        y = 2.78
        for nb in range(a, z + 1):
            f1, f2, f3 = D.fam(nb)
            D._rect(sl, x0, y, w, 0.78, fill=f3, rounded=True, radius=0.12)
            D._rect(sl, x0, y, 0.1, 0.78, fill=f1)
            D._txt(sl, x0 + 0.25, y, 0.55, 0.78, [[("%d" % nb, {"size": 20, "bold": True, "color": f1})]],
                   anchor=MSO_ANCHOR.MIDDLE)
            D._txt(sl, x0 + 0.8, y, w - 0.95, 0.78, [[(blocos.get(nb, ""), {"size": 14.5, "bold": True, "color": D.INK})]],
                   anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0, space_after=0)
            y += 0.87
    D.footer(sl, b, n, TOTAL); D.notes(sl, s.get("fala", ""))
    return sl


DESENHO = dict(V11.DESENHO)
DESENHO["agenda"] = _agenda
DESENHO["figura_rotulos"] = _figura_rotulos


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
    print("palavras de narração: %d  (%.0f min a 135 palavras/min)" % (palavras, palavras / 135.0))
    print("vídeos: %g min" % video)
