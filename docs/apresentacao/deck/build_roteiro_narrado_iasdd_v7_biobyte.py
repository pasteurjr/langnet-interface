# -*- coding: utf-8 -*-
"""Roteiro V7 sincronizado com a apresentação V5, agora didática por blocos."""
from pathlib import Path
import re
from markdown import markdown
from weasyprint import HTML

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "roteiro_narrado_iasdd_v6_biobyte.md"
OUT_MD = ROOT / "roteiro_narrado_iasdd_v7_biobyte.md"
OUT_PDF = ROOT / "roteiro_narrado_iasdd_v7_biobyte.pdf"
SHOTS = ROOT / "roteiro_narrado_iasdd_v5_biobyte_slides"


def old_blocks():
    text = SOURCE.read_text(encoding="utf-8")
    out = {}
    for block in re.split(r"(?=<div class=\"slide\" id=\"slide-\d+\"></div>)", text):
        m = re.search(r'^# Slide \d+ — (.+)$', block, re.M)
        body = re.search(r"## Texto integral para ler\n\n(.*?)(?:\n\n\*[^\n]+\*)", block, re.S)
        if m and body: out[m.group(1).strip()] = body.group(1).strip()
    return out


def pdf(text):
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


def build():
    import build_deck_iasdd_v5_biobyte as deck
    deck.build()
    import render_iasdd_v2_slide_previews as previews
    previews.PPTX = deck.OUT; previews.OUT = SHOTS; previews.main()
    old = old_blocks()
    lines = [
        "# Roteiro narrado integral — Engenharia de IA, SDD e BioByte", "",
        "**Versão:** V7, com introdução didática por bloco e conceitos contextualizados",
        "**Duração planejada:** 120 minutos, incluindo intervalo, vídeo de 20 minutos e perguntas",
        "**Velocidade de calibração:** 130 palavras por minuto", "",
        "> Cada seção começa com uma lâmina de orientação. O texto abaixo é a fala integral do narrador e cada lâmina possui sua captura visual.", "",
    ]
    for index, item in enumerate(deck.v4.base.base.META, 1):
        title = item["title"]
        source_title = next((k for k in old if k == title or (title.startswith("DEMO") and k.startswith("DEMO"))), None)
        if title.startswith("BLOCO") or title in {"O que é um modelo de linguagem?", "O que significa contexto para uma IA?", "De modelo para agente", "Por que precisamos de SDD?", "Como adaptar um modelo ao negócio?", "O estudo de caso: BioByte e LangNet"}:
            script = item.get("script", "")
        elif title.startswith("DEMO"):
            script = "Agora começa o vídeo da demonstração do BioByte. Durante os próximos vinte minutos, acompanhe o caminho completo: documento, requisitos, especificação, dados, interface, agentes, tarefas, YAML, ferramentas MCP, sequência, rede de Petri, geração do código, testes, aplicação e gate. A demonstração também mostra uma lacuna registrada, porque uma prova técnica confiável precisa revelar o que ainda está em desenvolvimento. Ao final do vídeo, retomaremos a fala para conectar a execução observada ao método SDD."
        elif title.lower() == "intervalo":
            script = "Neste momento, fazemos uma pausa programada. Retomaremos exatamente do ponto indicado na agenda."
        elif title.lower() == "perguntas":
            script = "Agora abro para perguntas. A tese que orienta a conversa é simples: gerar código ficou acessível, mas especificar, verificar e manter rastreabilidade continuam sendo responsabilidades de engenharia."
        else:
            script = old.get(source_title, item.get("script", "Neste slide, conectamos este conceito ao desenvolvimento de software com inteligência artificial."))
        script = script.replace("quinze minutos", "vinte minutos").replace("15 minutos", "20 minutos")
        timing = "*20 minutos reservados para o vídeo; o texto acima é a introdução.*" if title.startswith("DEMO") else f"*Texto calibrado para aproximadamente {item['minutes']:.2f} minutos a 130 palavras por minuto.*"
        lines += [f'<div class="slide" id="slide-{index}"></div>', f"# Slide {index:02d} — {title}", "",
                  f"**Tempo da lâmina:** {item['minutes']:.2f} minutos", "",
                  f"![Tela da lâmina {index:02d}]({SHOTS.name}/slide_{index:02d}.png)", "",
                  "## Texto integral para ler", "", script, "", timing, ""]
    text = "\n".join(lines)
    OUT_MD.write_text(text, encoding="utf-8"); pdf(text)
    print(f"MD: {OUT_MD} ({OUT_MD.stat().st_size} bytes)")
    print(f"PDF: {OUT_PDF} ({OUT_PDF.stat().st_size} bytes)")
    print(f"slides: {len(deck.v4.base.base.META)} tempo: {sum(x['minutes'] for x in deck.v4.base.base.META):.2f} min")


if __name__ == "__main__": build()
