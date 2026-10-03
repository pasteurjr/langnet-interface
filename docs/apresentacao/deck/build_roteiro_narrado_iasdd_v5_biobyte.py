# -*- coding: utf-8 -*-
"""Gera a V5 do roteiro narrado usando a apresentação V3 e suas imagens."""
from pathlib import Path
import re
import shutil

from markdown import markdown
from weasyprint import HTML

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE_MD = ROOT / "roteiro_narrado_iasdd_v4_biobyte.md"
OUT_MD = ROOT / "roteiro_narrado_iasdd_v5_biobyte.md"
OUT_PDF = ROOT / "roteiro_narrado_iasdd_v5_biobyte.pdf"
SOURCE_SHOTS = ROOT / "roteiro_narrado_iasdd_v2_biobyte_slides"
OUT_SHOTS = ROOT / "roteiro_narrado_iasdd_v3_biobyte_slides"


def add_source_notes(text):
    notes = {
        5: "**Fonte do conteúdo:** *Algoritmos Inteligentes3.pptx*, slides 155–237 — prognóstico, risco, sobrevivência, Cox e C-Index.",
        6: "**Fonte do conteúdo:** *Algoritmos Inteligentes3.pptx*, slides 238–284 — diagnóstico, CNN, COVID-19 em tomografia, U-Net e segmentação.",
        7: "**Fonte do conteúdo:** *Algoritmos Inteligentes3.pptx*, slides 285–339 — tratamento, ensaios clínicos e inferência causal.",
    }
    blocks = re.split(r"(?=<div class=\"slide\" id=\"slide-\d+\"></div>)", text)
    for i, block in enumerate(blocks):
        match = re.search(r'id="slide-(\d+)"', block)
        if match and int(match.group(1)) in notes:
            block = block.replace("## Texto integral para ler\n\n", "## Texto integral para ler\n\n" + notes[int(match.group(1))] + "\n\n", 1)
            blocks[i] = block
    return "".join(blocks)


def build():
    import build_deck_iasdd_v3_biobyte as deck
    deck.build()
    import render_iasdd_v2_slide_previews as previews
    previews.PPTX = deck.OUT
    previews.OUT = OUT_SHOTS
    previews.main()
    OUT_SHOTS.mkdir(parents=True, exist_ok=True)
    text = SOURCE_MD.read_text(encoding="utf-8")
    text = text.replace("V4, texto didático", "V5, texto didático e fonte da IA na saúde identificada")
    text = text.replace("roteiro_narrado_iasdd_v2_biobyte_slides", OUT_SHOTS.name)
    text = add_source_notes(text)
    OUT_MD.write_text(text, encoding="utf-8")
    body = markdown(text, extensions=["tables", "fenced_code"])
    css = """
    body { font-family: DejaVu Sans, sans-serif; font-size:10.5pt; color:#172033; line-height:1.45; margin:0 1.5cm; }
    h1 { font-size:18pt; color:#263b8f; border-bottom:1px solid #ccd3e1; padding-bottom:5px; }
    h2 { font-size:13.5pt; color:#324b9b; margin-top:1.1em; }
    img { display:block; width:100%; max-height:9.6cm; object-fit:contain; border:1px solid #ccd3e1; margin:8px 0 12px; }
    .slide { page-break-before:always; } .slide:first-child { page-break-before:auto; }
    @page { size:A4; margin:1.5cm 1.3cm; }
    """
    HTML(string=f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>", base_url=str(ROOT)).write_pdf(str(OUT_PDF))
    print(f"MD: {OUT_MD} ({OUT_MD.stat().st_size} bytes)")
    print(f"PDF: {OUT_PDF} ({OUT_PDF.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
