# -*- coding: utf-8 -*-
"""V10 — versão revista. NÃO sobrescreve a V9.

Mudanças em relação à V9:
  * um algoritmo por lâmina, com ideia central / para que serve / onde é mais adequado
  * o processo de Machine Learning passa etapa a etapa
  * bloco de Deep Learning com conteúdo real (neurônio, MLP, backprop, CNN, transfer)
  * bloco do LangNet percorre as etapas reais do pipeline
  * lâminas leves: teto de 95 palavras por lâmina
  * narração literal (o que a narradora fala), não instrução de palco
  * fechamento depois do vídeo final
  * sem lâminas duplicadas e sem referências penduradas a numeração antiga
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decklib as D
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.text import MSO_ANCHOR

OUT = HERE / "output" / "apresentacao_iasdd_v10_biobyte.pptx"

import v10_conteudo_a as ca
import v10_conteudo_b as cb
import v10_conteudo_c as cc
import v10_conteudo_d as cd

import v10_cortes
SLIDES = v10_cortes.aplicar(ca.SLIDES + cb.SLIDES + cc.SLIDES + cd.SLIDES)
TOTAL = len(SLIDES)


# ────────────────────────────── desenhistas ──────────────────────────────

def _cover(prs, s):
    sl = D._blank(prs)
    D.cover(sl, s["titulo"], s["subtitulo"], s["rodape"])
    return sl


def _divisor(prs, s, n):
    sl = D._blank(prs)
    b = s["bloco"]
    c1, c2, c3 = D.fam(b)
    D._rect(sl, 0, 0, D.SW, D.SH, fill=c3)
    D._rect(sl, 0, 0, 0.7, D.SH, fill=c1)
    D._rect(sl, 0.7, 0, 0.16, D.SH, fill=c2)
    D._txt(sl, 1.5, 2.1, D.SW - 2.6, 0.7,
           [[("BLOCO %d" % b, {"size": 17, "bold": True, "color": c1})]])
    D._txt(sl, 1.5, 2.75, D.SW - 2.6, 1.5,
           [[(s["titulo"], {"size": 40, "bold": True, "color": D.INK})]], line_spacing=1.03)
    D._rect(sl, 1.53, 4.35, 2.6, 0.09, fill=D.FAM["amber"][0])
    D._txt(sl, 1.5, 4.7, D.SW - 3.0, 1.2,
           [[(s["mensagem"], {"size": 18, "italic": True, "color": D.MUTED})]], line_spacing=1.12)
    D.footer(sl, b, n, TOTAL)
    return sl


def _cartoes(prs, s, n):
    sl = D._blank(prs)
    b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    y = 2.0
    if s.get("destaque"):
        D._txt(sl, 0.62, 1.98, D.SW - 1.3, 0.62,
               [[(s["destaque"], {"size": 19, "bold": True, "color": c1})]])
        y = 2.72
    D.cards(sl, b, s["cartoes"], x=0.6, y=y, size=s.get("corpo", 16.5))
    D.footer(sl, b, n, TOTAL)
    D.notes(sl, s["fala"])
    return sl


def _algoritmo(prs, s, n):
    """Lâmina de algoritmo: ideia central destacada + três cartões."""
    sl = D._blank(prs)
    b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    D._rect(sl, 0.6, 1.98, D.SW - 1.2, 0.78, fill=c3, rounded=True, radius=0.08)
    D._rect(sl, 0.6, 1.98, 0.12, 0.78, fill=D.FAM["amber"][0])
    D._txt(sl, 0.95, 1.98, D.SW - 1.6, 0.78,
           [[("Ideia central   ", {"size": 15, "bold": True, "color": D.MUTED}),
             (s["ideia"], {"size": 19, "bold": True, "color": c1})]],
           anchor=MSO_ANCHOR.MIDDLE)
    D.cards(sl, b, [("Como funciona", s["como"]),
                    ("Para que se presta", s["serve"]),
                    ("Onde é mais adequado", s["onde"])],
            x=0.6, y=2.95, size=16.5)
    D.footer(sl, b, n, TOTAL)
    D.notes(sl, s["fala"])
    return sl


def _etapa(prs, s, n):
    """Lâmina de etapa do pipeline: trilha numerada no topo + cartões."""
    sl = D._blank(prs)
    b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    passos = s["trilha"]
    atual = s["atual"]
    x = 0.6
    larg = (D.SW - 1.2 - (len(passos) - 1) * 0.08) / len(passos)
    for i, p in enumerate(passos):
        aceso = (i + 1) in atual if isinstance(atual, (list, tuple)) else (i + 1) == atual
        D._rect(sl, x, 2.0, larg, 0.52, fill=(c1 if aceso else c3), rounded=True, radius=0.1)
        D._txt(sl, x + 0.06, 2.0, larg - 0.12, 0.52,
               [[(p, {"size": 10.5, "bold": aceso, "color": (D.WHITE if aceso else D.MUTED)})]],
               anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        x += larg + 0.08
    D.cards(sl, b, s["cartoes"], x=0.6, y=2.78, size=s.get("corpo", 16.5))
    D.footer(sl, b, n, TOTAL)
    D.notes(sl, s["fala"])
    return sl


def _codigo(prs, s, n):
    sl = D._blank(prs)
    b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    D._txt(sl, 0.62, 1.96, D.SW - 1.3, 0.5,
           [[(s["intro"], {"size": 16, "color": D.INK})]])
    D.code_block(sl, s["codigo"], x=0.62, y=2.52, w=7.1, size=s.get("fonte", 11))
    D.callout(sl, b, [(s["explicacao"], {"size": 14.5, "color": D.INK})],
              x=8.0, y=2.52, w=4.7, h=3.1)
    D.footer(sl, b, n, TOTAL)
    D.notes(sl, s["fala"])
    return sl


def _tabela(prs, s, n):
    sl = D._blank(prs)
    b = s["bloco"]
    D.header(sl, b, s["chapeu"], s["titulo"])
    D.table(sl, b, s["colunas"], s["linhas"], x=0.6, y=2.05,
            fsize=s.get("fonte", 12.5), header_fs=12.5)
    if s.get("nota"):
        D.callout(sl, b, [(s["nota"], {"size": 14.5, "color": D.INK})], x=0.6, h=0.9)
    D.footer(sl, b, n, TOTAL)
    D.notes(sl, s["fala"])
    return sl


def _citacao(prs, s, n):
    sl = D._blank(prs)
    b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    D.quote(sl, b, [(s["frase"], {"size": 26, "bold": True, "color": c1})],
            x=0.6, y=2.1, w=D.SW - 1.2, h=1.9)
    D.cards(sl, b, s["cartoes"], x=0.6, y=4.25, size=16.5)
    D.footer(sl, b, n, TOTAL)
    D.notes(sl, s["fala"])
    return sl


def _video(prs, s, n):
    sl = D._blank(prs)
    b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, "Demonstração em vídeo", s["titulo"])
    D._rect(sl, 0.6, 1.98, D.SW - 1.2, 0.8, fill=c1, rounded=True, radius=0.1)
    D._txt(sl, 0.95, 1.98, D.SW - 1.9, 0.8,
           [[("▶  VÍDEO  ·  %g minutos   " % s["minutos"], {"size": 20, "bold": True, "color": D.WHITE}),
             (s["resumo"], {"size": 16, "color": D.WHITE})]],
           anchor=MSO_ANCHOR.MIDDLE)
    itens = [("%d." % (i + 1), t) for i, t in enumerate(s["percurso"])]
    D.cards(sl, b, itens, x=0.6, y=2.98, size=15.5)
    D.footer(sl, b, n, TOTAL)
    D.notes(sl, s["fala"])
    return sl


def _encerramento(prs, s, n):
    sl = D._blank(prs)
    b = s["bloco"]
    c1, c2, c3 = D.fam(b)
    D._rect(sl, 0, 0, D.SW, D.SH, fill=D.PAPER)
    D._rect(sl, 0, 0, D.SW, 0.18, fill=c1)
    D.quote(sl, b, [(s["frase"], {"size": 27, "bold": True, "color": c1})],
            x=1.1, y=2.3, w=D.SW - 2.2, h=2.1)
    D._txt(sl, 1.1, 4.7, D.SW - 2.2, 0.8,
           [[(s["assinatura"], {"size": 17, "color": D.MUTED})]], align=PP_ALIGN.CENTER)
    D.footer(sl, b, n, TOTAL)
    D.notes(sl, s["fala"])
    return sl


DESENHO = {"capa": _cover, "divisor": _divisor, "cartoes": _cartoes, "algoritmo": _algoritmo,
           "etapa": _etapa, "codigo": _codigo, "tabela": _tabela, "citacao": _citacao,
           "video": _video, "encerramento": _encerramento}


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
    print("palavras de narração: %d" % palavras)
    print("lâminas faladas: %.0f min (a 135 palavras/min)" % (palavras / 135.0))
    print("vídeos: %g min" % video)
    print("TOTAL: %.0f min" % (palavras / 135.0 + video))
