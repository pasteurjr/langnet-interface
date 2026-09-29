"""Gera o PDF do roteiro narrado, com a miniatura da tela ao lado de cada cena."""
import os, re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                Table, TableStyle, PageBreak)

RAIZ = "/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v6"
MD = os.path.join(RAIZ, "roteiro_narrado_v6_biobyte.md")
PDF = os.path.join(RAIZ, "roteiro_narrado_v6_biobyte.pdf")

est = getSampleStyleSheet()
h1 = ParagraphStyle('h1', parent=est['Heading1'], fontSize=17, spaceAfter=10, textColor=colors.HexColor('#1f3a5f'))
h2 = ParagraphStyle('h2', parent=est['Heading2'], fontSize=13.5, spaceBefore=14, spaceAfter=7, textColor=colors.HexColor('#2b5a8c'))
h3 = ParagraphStyle('h3', parent=est['Heading3'], fontSize=11.5, spaceBefore=10, spaceAfter=5, textColor=colors.HexColor('#333'))
corpo = ParagraphStyle('corpo', parent=est['BodyText'], fontSize=9.6, leading=14)
fala = ParagraphStyle('fala', parent=corpo, leftIndent=12, textColor=colors.HexColor('#111'),
                      backColor=colors.HexColor('#f2f6fb'), borderPadding=7, spaceBefore=4, spaceAfter=6, fontSize=10.2, leading=15)
prod = ParagraphStyle('prod', parent=corpo, textColor=colors.HexColor('#555'), fontSize=8.8)

def limpo(t):
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'`(.+?)`', r'<font face="Courier">\1</font>', t)
    return t.replace('&', '&amp;').replace('<b>', '\x01').replace('</b>', '\x02') \
            .replace('<font face="Courier">', '\x03').replace('</font>', '\x04') \
            .replace('<', '&lt;').replace('>', '&gt;') \
            .replace('\x01', '<b>').replace('\x02', '</b>') \
            .replace('\x03', '<font face="Courier">').replace('\x04', '</font>')

fluxo = []
pend_telas = []

def despeja_telas():
    global pend_telas
    for cam in pend_telas:
        abs_ = os.path.join(RAIZ, cam)
        if os.path.exists(abs_):
            try:
                img = Image(abs_); r = img.imageHeight / float(img.imageWidth)
                larg = 15.5 * cm
                fluxo.append(Image(abs_, width=larg, height=min(larg * r, 12 * cm)))
                fluxo.append(Paragraph(f"<i>{cam}</i>", prod)); fluxo.append(Spacer(1, 7))
            except Exception as e:
                fluxo.append(Paragraph(f"[tela não pôde ser embutida: {cam}]", prod))
    pend_telas = []

for ln in open(MD, encoding='utf-8').read().splitlines():
    t = ln.rstrip()
    if t.startswith('# '):   fluxo.append(Paragraph(limpo(t[2:]), h1))
    elif t.startswith('## '):
        despeja_telas(); fluxo.append(Paragraph(limpo(t[3:]), h2))
    elif t.startswith('### '):
        despeja_telas(); fluxo.append(Paragraph(limpo(t[4:]), h3))
    elif t.startswith('> '): fluxo.append(Paragraph(limpo(t[2:]), fala))
    elif t.startswith('**Tela') or t.startswith('**Telas'):
        pend_telas += re.findall(r'`(telas/[^`]+\.png)`', t)
        fluxo.append(Paragraph(limpo(t), prod))
    elif t.startswith('**Produção'):
        fluxo.append(Paragraph(limpo(t), prod)); despeja_telas()
    elif t.startswith('---'): fluxo.append(Spacer(1, 6))
    elif t.strip(): fluxo.append(Paragraph(limpo(t), corpo))

despeja_telas()
SimpleDocTemplate(PDF, pagesize=A4, topMargin=1.6*cm, bottomMargin=1.6*cm,
                  leftMargin=2*cm, rightMargin=2*cm,
                  title="Roteiro narrado — LangNet, pipeline SDD (v6)").build(fluxo)
print("PDF:", PDF, os.path.getsize(PDF)//1024, "KB")
