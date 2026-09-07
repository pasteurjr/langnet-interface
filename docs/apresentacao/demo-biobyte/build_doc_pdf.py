#!/usr/bin/env python3
"""Gera o PDF de um documento Markdown desta pasta (relatórios de validação e requisito×realidade).
Uso: python3 build_doc_pdf.py VALIDACAO-SISTEMA-biobyte.md  →  VALIDACAO-SISTEMA-biobyte.pdf (mesmo nome, .pdf)
Nunca sobrescreve outro arquivo: a saída é sempre o próprio nome do .md com a extensão trocada."""
import sys, markdown
from pathlib import Path
from weasyprint import HTML
src = Path(sys.argv[1]); out = src.with_suffix(".pdf")
corpo = markdown.markdown(src.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
css = """body{font-family:'DejaVu Sans',sans-serif;font-size:10.5pt;color:#111;line-height:1.45;margin:0 1.4cm}
h1{font-size:19pt;margin-top:0} h2{font-size:14pt;margin-top:1.3em;border-bottom:1px solid #ccc;padding-bottom:2px}
h3{font-size:11.5pt;margin-top:1.1em} table{border-collapse:collapse;width:100%;font-size:9pt;margin:.6em 0}
th,td{border:1px solid #bbb;padding:4px 6px;vertical-align:top} th{background:#eef} code{font-size:9pt;background:#f4f4f4;padding:0 3px}
pre{background:#f4f4f4;padding:8px;font-size:8.5pt;white-space:pre-wrap} @page{size:A4;margin:1.6cm 1.2cm}"""
HTML(string=f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{corpo}</body></html>").write_pdf(str(out))
print(out.name, out.stat().st_size, "bytes")
