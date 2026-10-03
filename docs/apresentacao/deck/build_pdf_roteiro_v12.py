# -*- coding: utf-8 -*-
"""PDF do roteiro V12, com a imagem de cada lâmina ao lado do texto a ser falado."""
from pathlib import Path
import markdown, weasyprint, re

RAIZ = Path(__file__).resolve().parent.parent
MD = RAIZ / "roteiro_narrado_iasdd_v12_biobyte.md"
PDF = RAIZ / "roteiro_narrado_iasdd_v12_biobyte.pdf"

CSS = """
@page { size: A4; margin: 1.3cm 1.4cm 1.1cm 1.4cm;
        @bottom-right { content: counter(page); font-size: 9px; color:#8a93a6; } }
body { font-family:'Liberation Sans','DejaVu Sans',sans-serif; color:#161e33; font-size:10.5px; line-height:1.5; }
h1 { font-size:21px; color:#4f46e5; margin:0 0 6px 0; }
h2 { font-size:15px; color:#161e33; margin:0 0 6px 0; padding:6px 10px;
     background:#eef0fb; border-left:5px solid #6d28d9; border-radius:0 6px 6px 0;
     page-break-after:avoid; page-break-before:auto; }
h3 { font-size:11.5px; color:#6d28d9; margin:10px 0 3px 0; text-transform:uppercase;
     letter-spacing:.4px; page-break-after:avoid; }
h3 + p, h3 + ul { page-break-before:avoid; }
img { width:100%; border-radius:7px; box-shadow:0 2px 7px rgba(20,26,50,.18); margin:5px 0; }
ul { margin:3px 0 6px 0; padding-left:16px; } li { margin-bottom:2px; }
table { border-collapse:collapse; width:100%; font-size:9.5px; margin:5px 0; }
th { background:#6d28d9; color:#fff; padding:4px 6px; text-align:left; }
td { border-bottom:1px solid #e2e7f0; padding:4px 6px; }
pre { background:#121a30; color:#eaeffa; padding:8px 10px; border-radius:6px;
      font-family:'DejaVu Sans Mono',monospace; font-size:8.6px; line-height:1.4; overflow:hidden; }
code { font-family:'DejaVu Sans Mono',monospace; }
blockquote { border-left:4px solid #f59e0b; background:#fdf6e9; margin:6px 0;
             padding:6px 10px; border-radius:0 6px 6px 0; }
hr { border:none; border-top:1px solid #e2e7f0; margin:0; }
.fala { background:#f6f8fd; border-left:4px solid #0f9d58; border-radius:0 7px 7px 0;
        padding:8px 12px; font-size:11.5px; line-height:1.62; margin:3px 0 8px 0; }
"""


def build():
    txt = MD.read_text(encoding="utf-8")
    html = markdown.markdown(txt, extensions=["tables", "fenced_code", "sane_lists"])
    # destaca o parágrafo de fala (o que vem logo depois do cabeçalho da narração)
    html = re.sub(r'(<h3>O que o apresentador fala</h3>\s*)<p>(.*?)</p>',
                  lambda m: m.group(1) + '<div class="fala">' + m.group(2) + '</div>',
                  html, flags=re.S)
    # cada lâmina começa em página nova
    html = html.replace("<h2>", '<h2 style="page-break-before:always">')
    html = html.replace('<h2 style="page-break-before:always">Sumário</h2>', "<h2>Sumário</h2>", 1)
    doc = "<html><head><meta charset='utf-8'><style>%s</style></head><body>%s</body></html>" % (CSS, html)
    weasyprint.HTML(string=doc, base_url=str(RAIZ)).write_pdf(PDF)
    return PDF


if __name__ == "__main__":
    p = build()
    print("gravado: %s (%.1f MB)" % (p, p.stat().st_size / 1e6))
