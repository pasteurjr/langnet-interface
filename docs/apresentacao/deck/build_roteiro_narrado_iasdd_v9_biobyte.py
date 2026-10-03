# -*- coding: utf-8 -*-
"""Gera o roteiro V9 como texto literal de locução, com imagens independentes."""
from pathlib import Path
import re
from markdown import markdown
from weasyprint import HTML

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "roteiro_narrado_iasdd_v8_biobyte.md"
OUT_MD = ROOT / "roteiro_narrado_iasdd_v9_biobyte.md"
OUT_PDF = ROOT / "roteiro_narrado_iasdd_v9_biobyte.pdf"
SHOTS = ROOT / "roteiro_narrado_iasdd_v7_biobyte_slides"
WPM = 130

def words(text):
    return re.findall(r"\b[\wÀ-ÿ]+(?:[-'][\wÀ-ÿ]+)?\b", text)

def parse_blocks(text):
    out = []
    for block in re.split(r"(?=<div class=\"slide\" id=\"slide-\d+\"></div>)", text):
        h = re.search(r'^# Slide (\d+) — (.+)$', block, re.M)
        tm = re.search(r"\*\*Tempo da lâmina:\*\* ([0-9.]+) minutos", block)
        body = re.search(r"## Texto integral para ler\n\n(.*?)(?:\n\n\*.*?\*)", block, re.S)
        if h and tm and body:
            out.append({"number": int(h.group(1)), "title": h.group(2).strip(),
                        "minutes": float(tm.group(1)), "script": body.group(1).strip()})
    return out

def clean_spoken(text):
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"\([^)]*~[^)]*\)", "", text)
    replacements = [
        (r"\bMostre\s+", "Nesta tela, vemos "),
        (r"\bExplique que\s+", "Isso significa que "),
        (r"\bExplique\s+", "O ponto é que "),
        (r"\bDiga que\s+", "A ideia é que "),
        (r"\bDiga também que\s+", "Também é importante entender que "),
        (r"\bDiga tamb[eé]m que\s+", "Também é importante entender que "),
        (r"\bDiga\s+", "A ideia é que "),
        (r"\bAponte\s+", "A imagem apresenta "),
        (r"\bLeia\s+", "O texto apresenta "),
        (r"\bApresente-se\s+", "Eu começo me apresentando: "),
        (r"\bApresente\s+", "Aqui temos "),
        (r"\bFeche com\s+", "A conclusão é "),
        (r"\bFeche\s+", "A conclusão é "),
        (r"\bObserve que\s+", "É importante perceber que "),
        (r"\bAgora faça a conexão explícita com\s+", "Isso se conecta diretamente com "),
        (r"\bNão desenvolva agora;[^.]*\.\s*", ""),
        (r"\bDê tempo[^.]*\.\s*", ""),
        (r"\bDê peso[^.]*\.\s*", ""),
        (r"\bPAUSE\.?", ""),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\.\s*\.", ".", text)
    return text

def prefix(title, text):
    low = title.lower()
    if title.startswith("BLOCO"):
        return f"Agora iniciamos {title.lower()}. {text}"
    if title.startswith("DEMO"):
        return text
    if low in {"intervalo", "perguntas"}:
        return text
    if text.lower().startswith(("nesta tela", "agora ", "antes ", "depois ", "a terceira", "a segunda", "a primeira")):
        return text
    return f"Nesta tela, vamos tratar de {title.lower()}. {text}"

def calibrate(text, minutes):
    target = max(25, round(minutes * WPM))
    if len(words(text)) <= target:
        endings = [
            "Essa distinção será importante quando chegarmos ao BioByte.",
            "É esse vínculo entre conceito e execução que orienta a apresentação.",
            "A responsabilidade de validar o resultado continua sendo da equipe.",
        ]
        i = 0
        while len(words(text)) < int(target * .92) and i < len(endings):
            text += " " + endings[i]; i += 1
        return text
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    kept=[]; count=0
    for sentence in sentences:
        n=len(words(sentence))
        if count+n <= target or not kept:
            kept.append(sentence); count += n
        else:
            break
    return " ".join(kept)

def build():
    import build_deck_iasdd_v7_biobyte as deck
    deck.build()
    import render_iasdd_v2_slide_previews as previews
    previews.PPTX = deck.OUT
    previews.OUT = SHOTS
    previews.main()
    slides = parse_blocks(SOURCE.read_text(encoding="utf-8"))
    lines = [
        "# Roteiro de locução — Engenharia de IA, SDD e BioByte",
        "",
        "**Versão:** V9 — texto literal para leitura em voz alta",
        "**Duração planejada:** 120 minutos, incluindo vídeo de 20 minutos e perguntas",
        f"**Velocidade de referência:** {WPM} palavras por minuto",
        "",
        "> Cada seção abaixo corresponde a uma imagem existente na pasta de lâminas. O texto sob a imagem é a fala da narradora; não são instruções de apresentação.",
        "",
    ]
    for item in slides:
        script = prefix(item["title"], clean_spoken(item["script"]))
        if item["title"] == "Capa":
            script = ("Sejam bem-vindos. Eu trabalho há quarenta anos com engenharia de software e, nesta apresentação, "
                      "vou discutir como usar inteligência artificial para desenvolver software crítico sem perder compreensão, "
                      "controle e rastreabilidade. A tese central é que gerar código ficou acessível, mas especificar e verificar "
                      "o resultado continuam sendo responsabilidades de engenharia.")
        elif item["title"] == "Agenda":
            script = ("Antes de entrar nos detalhes, vamos localizar o percurso. A apresentação começa com uma introdução a "
                      "Machine Learning, modelos de linguagem, agentes e frameworks. Depois, apresenta o SDD e chega ao BioByte "
                      "como estudo de caso. No final, o vídeo acompanha a transformação de uma especificação em agentes, tarefas, "
                      "rede de Petri, código, testes e aplicação executável.")
        elif "De “prompt” para" in item["title"] or "De prompt para" in item["title"]:
            script = ("Até aqui, vimos que o modelo precisa de informação para responder. O trabalho deixou de ser procurar "
                      "uma frase mágica e passou a ser engenharia de contexto: decidir, com disciplina, o que entra na janela. "
                      "Essa janela reúne instruções, ferramentas, histórico, documentos recuperados por RAG e o espaço reservado "
                      "para a resposta.")
        if item["title"].startswith("DEMO"):
            script = ("Agora começa o vídeo da demonstração do BioByte. Durante os próximos vinte minutos, "
                      "vamos acompanhar o caminho completo: documento, requisitos, especificação, dados, interface, "
                      "agentes, tarefas, YAML, ferramentas MCP, sequência, rede de Petri, geração do código, testes, "
                      "aplicação e gate. Ao final do vídeo, retomaremos a fala para conectar a execução observada ao método SDD.")
            timing = "*Os vinte minutos seguintes são ocupados pelo vídeo; este texto é a introdução da demonstração.*"
        elif item["title"].lower() in {"intervalo", "perguntas"}:
            timing = "*Tempo reservado para interação; não é locução contínua pré-gravada.*"
        else:
            script = calibrate(script, item["minutes"])
            timing = f"*{len(words(script))} palavras para aproximadamente {item['minutes']:.2f} minutos a {WPM} palavras por minuto.*"
        image_name = f"slide_{item['number']:02d}.png"
        lines += [
            f'<div class="slide" id="slide-{item["number"]}"></div>',
            f"# Slide {item['number']:02d} — {item['title']}",
            "",
            f"**Tempo previsto:** {item['minutes']:.2f} minutos",
            "",
            f"![Imagem do slide {item['number']:02d}]({SHOTS.name}/{image_name})",
            "",
            "## Texto para a narradora ler",
            "",
            script,
            "",
            timing,
            "",
        ]
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
    print(f"MD: {OUT_MD} ({OUT_MD.stat().st_size} bytes)")
    print(f"PDF: {OUT_PDF} ({OUT_PDF.stat().st_size} bytes)")
    print(f"imagens: {SHOTS} ({len(list(SHOTS.glob('slide_*.png')))} arquivos)")

if __name__ == "__main__":
    build()
