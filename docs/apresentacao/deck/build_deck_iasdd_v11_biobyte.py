# -*- coding: utf-8 -*-
"""V11 — NÃO sobrescreve a V10. Conteúdo da V10 + as alterações de v11_mudancas + falas de v11_falas."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decklib as D
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

import build_deck_iasdd_v10_biobyte as V10
import v11_mudancas

OUT = HERE / "output" / "apresentacao_iasdd_v11_biobyte.pptx"

SLIDES = v11_mudancas.aplicar(V10.SLIDES)
try:
    import v11_falas
    SLIDES = v11_falas.aplicar(SLIDES)
except ImportError:
    pass
TOTAL = len(SLIDES)
V10.TOTAL = TOTAL

# ── título com tamanho que cabe (títulos longos da V11) ──
_header_original = D.header


def _header(slide, block, kicker, title):
    c1, c2, c3 = D.fam(block)
    D._rect(slide, 0, 0, D.SW, D.SH, fill=D.PAPER)
    D._rect(slide, 0, 0, D.SW, 0.18, fill=c1)
    chip_w = 0.5 + 0.108 * len(kicker)
    D._rect(slide, 0.6, 0.5, chip_w, 0.44, fill=c1, rounded=True, radius=0.5)
    D._txt(slide, 0.72, 0.5, chip_w, 0.44, [[(kicker.upper(), {"size": 12.5, "bold": True, "color": D.WHITE})]],
           anchor=MSO_ANCHOR.MIDDLE, wrap=False)
    n = len(title)
    size = 31 if n <= 52 else (26 if n <= 64 else 20)
    D._txt(slide, 0.6, 1.06, D.SW - 1.2, 0.9, [[(title, {"size": size, "bold": True, "color": D.INK})]])
    D._rect(slide, 0.62, 1.78, 2.3, 0.09, fill=c2)
    return (c1, c2, c3)


D.header = _header

BAIXO = D.SH - 0.42   # limite inferior útil (acima do rodapé)


def _img(sl, path, x, y, w, h):
    D.image_center(sl, str(HERE / path), x=x, y=y, w=w, h=h)


def _code(sl, code, x, y, w, h=None, size=11, rotulo=None, block=0):
    c1 = D.fam(block)[0]
    if rotulo:
        D._txt(sl, x, y, w, 0.3, [[(rotulo, {"size": 12, "bold": True, "color": c1, "font": D.MONO})]])
        y += 0.34
    linhas = code.split("\n")
    if h is None:
        h = len(linhas) * size * 1.2 / 72 + 0.62
    D._rect(sl, x, y, w, h, fill=D.CODEBG, rounded=True, radius=0.04)
    for k, cor in enumerate(((0xF2, 0x6D, 0x5B), (0xF4, 0xBF, 0x4F), (0x62, 0xC5, 0x54))):
        D._dot(sl, x + 0.2 + 0.18 * k, y + 0.16, 0.1, D.RGBColor(*cor))
    D._txt(sl, x + 0.25, y + 0.4, w - 0.4, h - 0.45,
           [[(ln if ln else " ", {"font": D.MONO, "size": size, "color": D.CODEFG})] for ln in linhas],
           space_after=0, line_spacing=1.0, wrap=False)
    return y + h


def _faixa(sl, b, itens, y, h=0.78):
    """uma linha de cartões lado a lado"""
    c1, c2, c3 = D.fam(b)
    n = len(itens); gap = 0.18
    w = (D.SW - 1.2 - (n - 1) * gap) / n
    x = 0.6
    for it in itens:
        kind = it[2] if len(it) > 2 else None
        bar = {"good": D.GOOD, "warn": D.WARN}.get(kind, c1)
        tint = {"good": D.RGBColor(0xE6, 0xF6, 0xEC), "warn": D.RGBColor(0xFC, 0xF1, 0xE2)}.get(kind, c3)
        D._rect(sl, x, y, w, h, fill=tint, rounded=True, radius=0.1)
        D._rect(sl, x, y, 0.1, h, fill=bar)
        D._txt(sl, x + 0.28, y, w - 0.4, h,
               [[(it[0], {"size": 14, "bold": True, "color": bar})], [(it[1], {"size": 12.5, "color": D.INK})]],
               anchor=MSO_ANCHOR.MIDDLE, space_after=1, line_spacing=1.0)
        x += w + gap


# ────────────── desenhistas novos ──────────────

def _bio(prs, s, n):
    sl = D._blank(prs); b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    unidades = [2 if len(t) > 112 else 1 for _, t in s["linhas"]]
    uh = (BAIXO - 2.05) / sum(unidades)
    y = 2.05
    for (ano, t), u in zip(s["linhas"], unidades):
        h = uh * u
        D._txt(sl, 0.62, y, 2.2, h, [[(ano, {"size": 13, "bold": True, "color": c1})]], anchor=MSO_ANCHOR.MIDDLE)
        D._txt(sl, 2.95, y, D.SW - 3.6, h, [[(t, {"size": 13, "color": D.INK})]], anchor=MSO_ANCHOR.MIDDLE,
               space_after=0, line_spacing=1.0)
        D._rect(sl, 0.62, y + h - 0.01, D.SW - 1.24, 0.012, fill=D.LINE)
        y += h
    D.footer(sl, b, n, TOTAL); D.notes(sl, s.get("fala", ""))
    return sl


def _divisor_simples(prs, s, n):
    sl = D._blank(prs); b = s["bloco"]
    c1, c2, c3 = D.fam(b)
    D._rect(sl, 0, 0, D.SW, D.SH, fill=c3)
    D._rect(sl, 0, 0, 0.7, D.SH, fill=c1)
    D._rect(sl, 0.7, 0, 0.16, D.SH, fill=c2)
    D._txt(sl, 1.5, 2.6, D.SW - 2.6, 1.3, [[(s["titulo"], {"size": 44, "bold": True, "color": D.INK})]],
           anchor=MSO_ANCHOR.MIDDLE)
    D._rect(sl, 1.53, 4.05, 2.6, 0.09, fill=D.FAM["amber"][0])
    D.footer(sl, b, n, TOTAL); D.notes(sl, s.get("fala", ""))
    return sl


def _figura(prs, s, n):
    sl = D._blank(prs); b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    y = 2.0
    if s.get("destaque"):
        D._txt(sl, 0.62, 1.98, D.SW - 1.3, 0.5, [[(s["destaque"], {"size": 19, "bold": True, "color": c1})]])
        y = 2.55
    base = BAIXO
    if s.get("rodape"):
        D.callout(sl, b, [(s["rodape"], {"size": 14.5, "color": D.INK})], x=0.6, y=base - 0.78, h=0.78)
        base -= 0.9
    if s.get("faixa"):
        _faixa(sl, b, s["faixa"], base - 0.8)
        base -= 0.92
    if s.get("mensagem"):
        D.quote(sl, b, [(s["mensagem"], {"size": 16.5, "bold": True, "color": c1})], x=0.6, y=base - 1.0, w=D.SW - 1.2, h=1.0)
        base -= 1.1
    if s.get("lado", "inteira") == "inteira":
        _img(sl, s["imagem"], 0.6, y, D.SW - 1.2, base - y)
    else:
        lw = s.get("larg", 7.4)
        _img(sl, s["imagem"], 0.6, y, lw, base - y)
        xr = 0.6 + lw + 0.3; wr = D.SW - 0.6 - xr
        if s.get("cartoes"):
            D.cards(sl, b, s["cartoes"], x=xr, y=y + 0.1, w=wr, size=15, ch=1.25)
        if s.get("codigo"):
            yy = _code(sl, s["codigo"], xr, y + 0.1, wr, size=11.5, block=b)
            if s.get("nota"):
                D.callout(sl, b, [(s["nota"], {"size": 14, "color": D.INK})], x=xr, y=yy + 0.2, w=wr, h=1.05)
    D.footer(sl, b, n, TOTAL); D.notes(sl, s.get("fala", ""))
    return sl


def _codigos(prs, s, n):
    sl = D._blank(prs); b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    D._txt(sl, 0.62, 1.98, D.SW - 1.3, 0.5, [[(s["ideia"], {"size": 16, "bold": True, "color": c1})]])
    y = 2.55
    base = BAIXO
    if s.get("nota"):
        D.callout(sl, b, [(s["nota"], {"size": 14, "color": D.INK})], x=0.6, y=base - 0.75, h=0.75)
        base -= 0.87
    x0, x1 = 0.6, D.SW - 0.6
    if s.get("imagem"):
        iw = 5.6
        if s.get("imagem_esq"):
            _img(sl, s["imagem"], x0, y, iw, base - y); x0 += iw + 0.3
        else:
            _img(sl, s["imagem"], x1 - iw, y, iw, base - y); x1 -= iw + 0.3
    pn = s["paineis"]; gap = 0.22
    w = (x1 - x0 - (len(pn) - 1) * gap) / len(pn)
    maxl = max(len(c.split("\n")) for _, c in pn)
    maxc = max(len(l) for _, c in pn for l in c.split("\n"))
    alt = base - y - 0.34
    size = min(12.5, (alt - 0.62) * 72 / (1.2 * maxl), (w - 0.45) * 72 / (0.62 * maxc))
    for rot, cod in pn:
        _code(sl, cod, x0, y, w, h=alt, size=size, rotulo=rot, block=b)
        x0 += w + gap
    D.footer(sl, b, n, TOTAL); D.notes(sl, s.get("fala", ""))
    return sl


def _recursos(prs, s, n):
    sl = D._blank(prs); b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    D._txt(sl, 0.62, 1.98, D.SW - 1.3, 0.5, [[(s["intro"], {"size": 16, "color": D.INK})]])
    y = 2.55
    _code(sl, s["codigo"], 0.6, y, 5.3, h=BAIXO - y, size=10.5, block=b)
    xs = 6.15; cw = (D.SW - 0.6 - xs - 0.18) / 2
    rh = (BAIXO - y - 2 * 0.16) / 3
    for k, (nome, desc) in enumerate(s["recursos"]):
        cx = xs + (k % 2) * (cw + 0.18); cy = y + (k // 2) * (rh + 0.16)
        D._rect(sl, cx, cy, cw, rh, fill=c3, rounded=True, radius=0.1)
        D._rect(sl, cx, cy, cw, 0.1, fill=c1)
        D._txt(sl, cx + 0.22, cy + 0.12, cw - 0.4, rh - 0.15,
               [[(nome, {"size": 15.5, "bold": True, "color": c1})], [(desc, {"size": 13, "color": D.INK})]],
               anchor=MSO_ANCHOR.MIDDLE, space_after=3, line_spacing=1.02)
    D.footer(sl, b, n, TOTAL); D.notes(sl, s.get("fala", ""))
    return sl


def _video(prs, s, n):
    sl = D._blank(prs); b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s.get("chapeu", "Demonstração"), s["titulo"])
    D._rect(sl, 0.6, 1.98, D.SW - 1.2, 0.8, fill=c1, rounded=True, radius=0.1)
    D._txt(sl, 0.95, 1.98, D.SW - 1.9, 0.8,
           [[("▶  VÍDEO  ·  %g minutos   " % s["minutos"], {"size": 20, "bold": True, "color": D.WHITE}),
             (s["resumo"], {"size": 16, "color": D.WHITE})]], anchor=MSO_ANCHOR.MIDDLE)
    itens = [("%d." % (i + 1), t) for i, t in enumerate(s["percurso"])]
    D.cards(sl, b, itens, x=0.6, y=2.98, size=15.5)
    D.footer(sl, b, n, TOTAL); D.notes(sl, s.get("fala", ""))
    return sl


def _encerramento_limpo(prs, s, n):
    sl = D._blank(prs); b = s["bloco"]
    c1, c2, c3 = D.fam(b)
    D._rect(sl, 0, 0, D.SW, D.SH, fill=D.PAPER)
    D._rect(sl, 0, 0, D.SW, 0.18, fill=c1)
    D._txt(sl, 1.4, 2.2, D.SW - 2.8, 1.8, [[(s["frase"], {"size": 30, "bold": True, "color": c1})]],
           align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.1)
    D._rect(sl, D.SW / 2 - 1.3, 4.35, 2.6, 0.08, fill=D.FAM["amber"][0])
    D._txt(sl, 1.4, 4.75, D.SW - 2.8, 0.7, [[("Obrigado.", {"size": 24, "bold": True, "color": D.INK})]],
           align=PP_ALIGN.CENTER)
    D._txt(sl, 1.4, 5.45, D.SW - 2.8, 0.5, [[("Pasteur Ottoni de Miranda Júnior  ·  Perguntas", {"size": 15, "color": D.MUTED})]],
           align=PP_ALIGN.CENTER)
    D.notes(sl, s.get("fala", ""))
    return sl


def _etapa(prs, s, n):
    """como a V10, com rótulo menor na trilha (não quebra 'Especificação')"""
    sl = D._blank(prs); b = s["bloco"]
    c1, c2, c3 = D.header(sl, b, s["chapeu"], s["titulo"])
    passos = s["trilha"]; atual = s["atual"]
    x = 0.6; larg = (D.SW - 1.2 - (len(passos) - 1) * 0.08) / len(passos)
    for i, p in enumerate(passos):
        aceso = (i + 1) in atual if isinstance(atual, (list, tuple)) else (i + 1) == atual
        D._rect(sl, x, 2.0, larg, 0.52, fill=(c1 if aceso else c3), rounded=True, radius=0.1)
        D._txt(sl, x + 0.03, 2.0, larg - 0.06, 0.52,
               [[(p, {"size": 9.5, "bold": aceso, "color": (D.WHITE if aceso else D.MUTED)})]],
               anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        x += larg + 0.08
    D.cards(sl, b, s["cartoes"], x=0.6, y=2.78, size=s.get("corpo", 16.5))
    D.footer(sl, b, n, TOTAL); D.notes(sl, s.get("fala", ""))
    return sl


DESENHO = dict(V10.DESENHO)
DESENHO.update({"bio": _bio, "divisor_simples": _divisor_simples, "figura": _figura, "codigos": _codigos,
                "recursos": _recursos, "video": _video, "etapa": _etapa, "encerramento_limpo": _encerramento_limpo})


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
