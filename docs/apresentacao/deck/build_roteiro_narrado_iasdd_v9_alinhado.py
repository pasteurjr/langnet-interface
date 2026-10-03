# -*- coding: utf-8 -*-
"""Gera o roteiro V9 a partir do mesmo META usado para construir o PPTX V9."""
from pathlib import Path
import re
from markdown import markdown
from weasyprint import HTML

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PPTX = HERE / "output" / "apresentacao_iasdd_v9_biobyte.pptx"
OUT_MD = ROOT / "roteiro_narrado_iasdd_v9_biobyte.md"
OUT_PDF = ROOT / "roteiro_narrado_iasdd_v9_biobyte.pdf"
SHOTS = ROOT / "roteiro_narrado_iasdd_v9_biobyte_slides"

def spoken(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def build():
    import build_deck_iasdd_v9_biobyte as deck
    deck.build()
    import render_iasdd_v2_slide_previews as previews
    previews.PPTX = PPTX
    previews.OUT = SHOTS
    previews.main()
    meta = deck.f.META
    lines = [
        "# Roteiro de locução — Engenharia de IA, SDD e BioByte",
        "", "**Versão:** V9 alinhada ao PowerPoint V9", "",
        "**Duração:** aproximadamente 58 minutos de lâminas, cinco vídeos de 8 minutos e demonstração final de 20 minutos.", "",
        "> Cada seção abaixo corresponde exatamente a uma lâmina do PowerPoint V9. O texto é a fala literal da narradora.", ""
    ]
    for n, item in enumerate(meta, 1):
        title = item["title"]
        script = spoken(item.get("script", ""))
        if title.startswith("Demonstração"):
            script = script or f"Agora começa a demonstração em vídeo: {title}."
        lines += [f'<div class="slide" id="slide-{n}"></div>', f"# Slide {n:02d} — {title}", "",
                  f"**Tempo previsto:** {item['minutes']:.2f} minutos", "",
                  f"![Imagem do slide {n:02d}](roteiro_narrado_iasdd_v9_biobyte_slides/slide_{n:02d}.png)", "",
                  "## Texto para a narradora ler", "", script, ""]
    text = "\n".join(lines)
    OUT_MD.write_text(text, encoding="utf-8")
    body = markdown(text, extensions=["tables", "fenced_code"])
    css = """body{font-family:DejaVu Sans,sans-serif;font-size:10.5pt;color:#172033;line-height:1.45;margin:0 1.5cm}
    h1{font-size:18pt;color:#263b8f;border-bottom:1px solid #ccd3e1;padding-bottom:5px}
    h2{font-size:13.5pt;color:#324b9b;margin-top:1.1em}
    img{display:block;width:100%;max-height:9.6cm;object-fit:contain;border:1px solid #ccd3e1;margin:8px 0 12px}
    .slide{page-break-before:always}.slide:first-child{page-break-before:auto}
    @page{size:A4;margin:1.5cm 1.3cm}"""
    HTML(string=f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>", base_url=str(ROOT)).write_pdf(str(OUT_PDF))
    print(f"PPTX: {PPTX} ({len(meta)} slides)")
    print(f"MD: {OUT_MD}")
    print(f"PDF: {OUT_PDF}")

if __name__ == "__main__": build()
