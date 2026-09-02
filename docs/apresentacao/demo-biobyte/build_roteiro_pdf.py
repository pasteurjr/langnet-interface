#!/usr/bin/env python3
"""Monta o ROTEIRO DE VÍDEO em PDF a partir de narracao_log.md, com as telas embutidas.

Cada cena vira uma seção: NARRAÇÃO (destacada, é a fala do locutor), PRODUÇÃO (o que
mostrar), TELA(s) (imagens embutidas quando o arquivo existe em shots/) e NOTA.
Uso: python3 build_roteiro_pdf.py  →  ROTEIRO-VIDEO-biobyte.pdf
"""
import re, base64, html
from pathlib import Path

BASE = Path(__file__).parent
SHOTS = BASE / "shots"
SRC = BASE / "narracao_log.md"
OUT = BASE / "ROTEIRO-VIDEO-biobyte.pdf"

def img_tag(name: str) -> str:
    f = SHOTS / name.strip()
    if not f.exists():
        return f'<div class="missing">[tela não capturada: {html.escape(name)}]</div>'
    b64 = base64.b64encode(f.read_bytes()).decode()
    return (f'<figure><img src="data:image/png;base64,{b64}"/>'
            f'<figcaption>{html.escape(f.name)}</figcaption></figure>')

def inline(t: str) -> str:
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    return t

md = SRC.read_text(encoding="utf-8")
head, *rest = re.split(r"(?m)^## ", md)
parts = []
m = re.search(r"^# (.+)", head)
title = m.group(1) if m else "Roteiro"
subtitle = "\n".join(l for l in head.splitlines()[1:] if l.strip() and not l.startswith("---"))

for block in rest:
    lines = block.splitlines()
    scene = lines[0].strip()
    body, shots, in_code = [], [], False
    for ln in lines[1:]:
        if ln.strip().startswith("```"):
            in_code = not in_code
            body.append("<pre>" if in_code else "</pre>")
            continue
        if in_code:
            body.append(html.escape(ln)); continue
        mm = re.match(r"\*\*(NARRAÇÃO|PRODUÇÃO|TELA|TELAS|NOTA[^:]*|TRECHO[^:]*):\*\*\s*(.*)", ln.strip())
        if mm:
            tag, txt = mm.group(1), mm.group(2)
            if tag.startswith("TELA"):
                shots += [x.strip() for x in txt.split(",") if x.strip() and x.strip().endswith(".png")]
                body.append(f'<p class="telas"><span class="lbl">TELAS</span> {inline(txt)}</p>')
            else:
                cls = {"NARRAÇÃO": "narr", "PRODUÇÃO": "prod"}.get(tag, "nota")
                body.append(f'<p class="{cls}"><span class="lbl">{tag}</span> {inline(txt)}</p>')
        elif ln.strip():
            body.append(f"<p>{inline(ln.strip())}</p>")
    imgs = "".join(img_tag(s) for s in shots)
    parts.append(f'<section><h2>{inline(scene)}</h2>{"".join(body)}{imgs}</section>')

CSS = """
@page { size: A4; margin: 16mm 14mm; @bottom-center { content: counter(page); font: 9pt Helvetica; color:#888; } }
body { font: 10.5pt/1.5 Helvetica, Arial, sans-serif; color:#1a1a1a; }
h1 { font-size: 22pt; color:#4338ca; margin:0 0 4px; }
.sub { color:#555; font-size:9.5pt; margin-bottom:18px; }
section { break-before: page; }
section:first-of-type { break-before: avoid; }
h2 { font-size: 13pt; color:#4338ca; border-bottom:2px solid #e0e7ff; padding-bottom:4px; margin:0 0 10px; }
.lbl { display:inline-block; font-size:7.5pt; font-weight:700; letter-spacing:.6px; padding:1px 6px; border-radius:3px; margin-right:6px; vertical-align:1px; }
.narr { background:#f5f3ff; border-left:4px solid #7c3aed; padding:8px 10px; margin:6px 0; font-size:11pt; }
.narr .lbl { background:#7c3aed; color:#fff; }
.prod { background:#f8fafc; border-left:4px solid #64748b; padding:7px 10px; margin:6px 0; font-size:9.5pt; }
.prod .lbl { background:#64748b; color:#fff; }
.telas { font-size:8.5pt; color:#555; margin:4px 0; }
.telas .lbl { background:#0ea5e9; color:#fff; }
.nota { background:#fffbeb; border-left:4px solid #f59e0b; padding:7px 10px; margin:6px 0; font-size:9pt; }
.nota .lbl { background:#f59e0b; color:#fff; }
figure { margin:10px 0; break-inside: avoid; }
img { width:100%; border:1px solid #d4d4d8; border-radius:4px; }
figcaption { font-size:7.5pt; color:#888; text-align:center; margin-top:2px; }
pre { background:#0f172a; color:#e2e8f0; padding:8px; border-radius:4px; font-size:8pt; white-space:pre-wrap; }
code { background:#eef2ff; padding:1px 3px; border-radius:3px; font-size:9pt; }
.missing { font-size:8pt; color:#b91c1c; font-style:italic; }
"""
htmldoc = (f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
           f"<h1>{html.escape(title)}</h1><div class='sub'>{inline(subtitle).replace(chr(10),'<br/>')}</div>"
           + "".join(parts) + "</body></html>")
from weasyprint import HTML
HTML(string=htmldoc, base_url=str(BASE)).write_pdf(str(OUT))
n_img = htmldoc.count("<figure>")
print(f"PDF: {OUT}  ({OUT.stat().st_size//1024} KB) · {len(parts)} cenas · {n_img} telas embutidas")
