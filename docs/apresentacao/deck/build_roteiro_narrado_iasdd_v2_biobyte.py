# -*- coding: utf-8 -*-
"""Gera o roteiro narrado, uma pagina por slide, da apresentacao IA+SDD v2 BioByte."""
import html
import re
import sys
from pathlib import Path

from markdown import markdown
from weasyprint import HTML

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_deck_iasdd_v2_biobyte as deck
import render_iasdd_v2_slide_previews as previews

ROOT = HERE.parent
MD_OUT = ROOT / "roteiro_narrado_iasdd_v2_biobyte.md"
PDF_OUT = ROOT / "roteiro_narrado_iasdd_v2_biobyte.pdf"
SLIDES_DIR = ROOT / "roteiro_narrado_iasdd_v2_biobyte_slides"


def clean_script(value):
    value = html.unescape(value or "")
    value = re.sub(r"<b>(.*?)</b>", r"**\1**", value, flags=re.S)
    value = re.sub(r"<i>(.*?)</i>", r"*\1*", value, flags=re.S)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\s*\(~", " (~", value)
    return value


def emphasis(title):
    t = title.lower()
    if "biobyte" in t or "bio byte" in t:
        return "Conecte o slide ao BioByte e deixe claro qual requisito, agente, tarefa ou resultado clínico está sendo mostrado."
    if "crewai" in t:
        return "Ressalte role, goal, tools, traceability e expected_output. Explique que o trecho é baseado no contrato do BioByte."
    if "langgraph" in t:
        return "Ressalte estado explícito, transições, checkpoint e aprovação humana."
    if "autogen" in t:
        return "Ressalte a conversa entre agentes, o revisor, o limite de turnos e o risco de divergência."
    if "mcp" in t or "protocol" in t:
        return "Ressalte o contrato da ferramenta e separe interoperabilidade de governança."
    if "sdd" in t or "especifica" in t or "spec" in t:
        return "Ressalte que a especificação é a fonte primária e que o código e os testes são derivados."
    if "petri" in t:
        return "Ressalte lugares, transições, tokens, sincronização e propriedades verificáveis."
    if "demonstra" in t or "vídeo" in t or "video" in t:
        return "Ressalte que os quinze minutos do vídeo estão dentro dos 120 minutos e que a gravação deve mostrar execução real."
    if "ia na saúde" in t:
        return "Relacione o conceito ao BioByte: prognóstico/Cox, diagnóstico/NHSN-MDR e tratamento/bundle."
    return "Leia o título, conduza a leitura visual e feche com a mensagem de engenharia do slide."


def transition(block):
    transitions = {
        0: "Agora vamos construir a base conceitual necessária para entender a decisão de arquitetura.",
        1: "Com o modelo entendido, passamos ao problema de contexto, evidência e ferramenta.",
        2: "Com contexto e ferramentas definidos, podemos falar de agentes.",
        3: "Agora o problema clínico entra como contrato técnico, não como ilustração.",
        4: "A seguir, veremos como o mesmo contrato é expresso por diferentes tecnologias.",
        5: "Com a especificação definida, ela pode gerar plano, tarefas, código e testes.",
        6: "Agora veremos como o LangNet transforma esses artefatos em execução.",
        7: "A demonstração reúne a teoria e mostra o que realmente foi executado.",
        8: "A seguir, posicionamos os ambientes de desenvolvimento no fluxo.",
        9: "Agora a tese vira um método verificável.",
        10: "Depois do método, discutimos quando adaptar o modelo e quando não adaptar.",
        11: "Este é o momento de mostrar o sistema e a evidência.",
        12: "Vamos fechar retomando a tese e abrindo para perguntas.",
    }
    return transitions.get(block, "Siga para o próximo ponto do roteiro.")


def build():
    deck.build_v2()
    # Gera uma representação visual de cada lâmina diretamente do PPTX para
    # que o PDF de apoio mostre a tela antes do texto que será narrado.
    previews.main()
    meta = deck.base.META
    if len(meta) != 70:
        raise RuntimeError(f"Esperados 70 slides no roteiro; encontrados {len(meta)}")

    lines = [
        "# Roteiro narrado — Engenharia de IA, SDD e BioByte Sentinela",
        "",
        "**Versão:** v2 baseada na apresentação completa de 70 slides",
        "**Duração total:** 120 minutos, incluindo intervalo, vídeo de 15 minutos e perguntas",
        "**Uso:** leitura, memorização e gravação da narração",
        "",
        "> Cada seção corresponde a uma lâmina. O tempo indicado é o tempo acumulado de fala atribuído à lâmina; o slide da demonstração reserva 15 minutos para o vídeo real.",
        "",
    ]

    for index, item in enumerate(meta, start=1):
        title = item["title"]
        minutes = item["minutes"]
        script = clean_script(item["script"])
        lines.extend([
            f'<div class="slide" id="slide-{index}"></div>',
            f"# Slide {index:02d} — {title}",
            "",
            f"**Tempo de fala:** {minutes:.2f} minutos",
            f"**Bloco:** {item['block']}",
            "",
            f"![Captura visual da lâmina {index:02d}](roteiro_narrado_iasdd_v2_biobyte_slides/slide_{index:02d}.png)",
            "",
            "## O que aparece na lâmina",
            "",
            f"O slide apresenta o tema **{title}**. Faça uma leitura visual inicial de aproximadamente dez segundos antes de começar a explicação.",
            "",
            "## Texto para falar",
            "",
            script,
            "",
            "## O que deve ser ressaltado",
            "",
            emphasis(title),
            "",
            "## Transição",
            "",
            transition(item["block"]),
            "",
        ])

    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    body = markdown(MD_OUT.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
    css = """
    body { font-family: DejaVu Sans, sans-serif; font-size: 10.5pt; color:#172033; line-height:1.45; margin:0 1.5cm; }
    h1 { font-size:18pt; color:#263b8f; margin-top:0; border-bottom:1px solid #ccd3e1; padding-bottom:5px; }
    h2 { font-size:13.5pt; color:#324b9b; margin-top:1.1em; }
    p { margin:.5em 0; }
    blockquote { border-left:4px solid #536dce; padding:8px 12px; background:#f0f3fb; }
    code { background:#f2f4f8; padding:1px 3px; }
    pre { background:#f2f4f8; padding:9px; font-size:8.8pt; white-space:pre-wrap; }
    table { border-collapse:collapse; width:100%; font-size:9pt; }
    th, td { border:1px solid #b9c2d3; padding:4px 6px; vertical-align:top; }
    th { background:#e8edf8; }
    .slide { page-break-before: always; }
    .slide:first-child { page-break-before: auto; }
    img { display:block; width:100%; max-height:9.6cm; object-fit:contain; border:1px solid #ccd3e1; margin:8px 0 12px 0; }
    @page { size:A4; margin:1.5cm 1.3cm; }
    """
    HTML(string=f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>", base_url=str(ROOT)).write_pdf(str(PDF_OUT))
    print("MD:", MD_OUT, MD_OUT.stat().st_size, "bytes")
    print("PDF:", PDF_OUT, PDF_OUT.stat().st_size, "bytes")
    print("slides:", len(meta), "tempo:", sum(x["minutes"] for x in meta), "min")


if __name__ == "__main__":
    build()
