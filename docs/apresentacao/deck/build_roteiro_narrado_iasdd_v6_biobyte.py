# -*- coding: utf-8 -*-
"""Gera o roteiro V6 sincronizado com o deck V4 de 73 slides."""
from pathlib import Path
import re
from markdown import markdown
from weasyprint import HTML

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "roteiro_narrado_iasdd_v5_biobyte.md"
OUT_MD = ROOT / "roteiro_narrado_iasdd_v6_biobyte.md"
OUT_PDF = ROOT / "roteiro_narrado_iasdd_v6_biobyte.pdf"
SHOTS = ROOT / "roteiro_narrado_iasdd_v4_biobyte_slides"

NEW_SCRIPTS = {
    "Pipeline de Machine Learning": "Antes de escolher um algoritmo, precisamos entender o pipeline. Primeiro visualizamos os dados para conhecer sua distribuição e suas relações. Depois limpamos, transformamos e normalizamos os fatores. Em seguida separamos treinamento, validação e teste. Só então escolhemos o modelo e seus hiperparâmetros, treinamos com os dados de desenvolvimento e avaliamos em dados que o modelo ainda não viu. A ideia central é simples: Machine Learning é um processo de dados, modelo e evidência; o algoritmo é apenas uma etapa.",
    "Treinamento e avaliação": "Treinar não é provar que o modelo funciona. O conjunto de treinamento mostra se ele aprendeu os exemplos; o conjunto de teste mostra se ele generaliza para dados novos. Precisamos observar overfitting, quando o modelo memoriza o treinamento, e underfitting, quando ele não aprende o suficiente. A matriz de confusão organiza falsos positivos, falsos negativos, verdadeiros positivos e verdadeiros negativos. A métrica depende do risco: em diagnóstico, recall pode ser mais importante que acurácia; em outras situações, precisão, F-score, ROC e AUC podem ser mais adequados.",
    "Principais algoritmos de Machine Learning": "Com o pipeline claro, podemos situar os algoritmos. A regressão linear prevê valores numéricos; a regressão logística classifica e estima probabilidades. Árvores de decisão expressam regras legíveis, e Random Forest combina várias árvores para ganhar robustez. Máquinas de vetores de suporte procuram uma boa fronteira entre classes, enquanto K-vizinhos classifica por similaridade. Redes neurais e redes convolucionais aprendem padrões complexos em textos, imagens e sinais. K-Means agrupa dados sem rótulos. A escolha deve partir do problema, dos dados, da necessidade de explicação e do custo do erro.",
}


def old_blocks():
    text = SOURCE.read_text(encoding="utf-8")
    result = {}
    for block in re.split(r"(?=<div class=\"slide\" id=\"slide-\d+\"></div>)", text):
        m = re.search(r'^# Slide \d+ — (.+)$', block, re.M)
        if not m: continue
        body = re.search(r"## Texto integral para ler\n\n(.*?)(?:\n\n\*[^\n]+\*)", block, re.S)
        if body: result[m.group(1).strip()] = body.group(1).strip()
    return result


def render_pdf(text):
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
    import build_deck_iasdd_v4_biobyte as deck
    deck.build()
    import render_iasdd_v2_slide_previews as previews
    previews.PPTX = deck.OUT
    previews.OUT = SHOTS
    previews.main()
    old = old_blocks()
    lines = [
        "# Roteiro narrado integral — Engenharia de IA, SDD e BioByte",
        "", "**Versão:** V6, com pipeline de Machine Learning e vídeo de 20 minutos",
        "**Duração planejada:** 120 minutos, incluindo intervalo, vídeo de 20 minutos e perguntas",
        "**Velocidade de calibração:** 130 palavras por minuto", "",
        "> O texto abaixo é a fala do narrador. Cada lâmina contém a captura visual correspondente e o texto integral para leitura.", "",
    ]
    for index, item in enumerate(deck.base.base.META, 1):
        title = item["title"]
        old_title = next((k for k in old if k == title or (title.startswith("DEMO") and k.startswith("DEMO"))), None)
        if title in NEW_SCRIPTS:
            script = NEW_SCRIPTS[title]
        elif title.startswith("DEMO"):
            script = "Agora começa o vídeo da demonstração do BioByte. Durante os próximos vinte minutos, acompanhe o caminho completo: o documento de agentes e tarefas, a especificação, os dados, a interface, os agentes, as tarefas, o YAML, o registro das ferramentas MCP, a sequência, a rede de Petri, a geração do código, os testes, a aplicação e o gate. A demonstração também mostra uma lacuna registrada, porque uma prova técnica confiável precisa revelar o que ainda está em desenvolvimento. Ao final do vídeo, retomaremos a fala para conectar a execução observada ao método SDD."
        elif title.lower() == "intervalo":
            script = "Neste momento, fazemos uma pausa programada. Retomaremos exatamente do ponto indicado na agenda."
        elif title.lower() == "perguntas":
            script = "Agora abro para perguntas. A tese que orienta a conversa é simples: gerar código ficou acessível, mas especificar, verificar e manter rastreabilidade continuam sendo responsabilidades de engenharia."
        else:
            script = old.get(old_title, item.get("script", "Neste slide, conectamos este conceito ao desenvolvimento de software com inteligência artificial."))
        script = script.replace("quinze minutos", "vinte minutos").replace("15 minutos", "20 minutos")
        lines += [f'<div class="slide" id="slide-{index}"></div>', f"# Slide {index:02d} — {title}", "",
                  f"**Tempo da lâmina:** {item['minutes']:.2f} minutos", "",
                  f"![Tela da lâmina {index:02d}]({SHOTS.name}/slide_{index:02d}.png)", "",
                  "## Texto integral para ler", "", script, "",
                  ("*20 minutos reservados para o vídeo; o texto acima é a introdução.*" if title.startswith("DEMO") else
                   f"*Texto calibrado para aproximadamente {item['minutes']:.2f} minutos a 130 palavras por minuto.*"), ""]
    text = "\n".join(lines)
    OUT_MD.write_text(text, encoding="utf-8")
    render_pdf(text)
    print(f"MD: {OUT_MD} ({OUT_MD.stat().st_size} bytes)")
    print(f"PDF: {OUT_PDF} ({OUT_PDF.stat().st_size} bytes)")
    print(f"slides: {len(deck.base.base.META)} tempo: {sum(x['minutes'] for x in deck.base.base.META):.2f} min")


if __name__ == "__main__": build()
