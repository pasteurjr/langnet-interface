# -*- coding: utf-8 -*-
"""Gera a V3 do roteiro: fala integral, calibrada por lâmina, com imagens."""
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
MD_OUT = ROOT / "roteiro_narrado_iasdd_v4_biobyte.md"
PDF_OUT = ROOT / "roteiro_narrado_iasdd_v4_biobyte.pdf"
WPM = 130


def didactic_context(index, title):
    """Abertura falada que situa a lâmina antes dos detalhes técnicos."""
    t = title.lower()
    if index == 1:
        return "Sejam bem-vindos. Antes de entrar nas ferramentas, eu quero apresentar a pergunta que organiza esta conversa: como usar inteligência artificial para desenvolver software crítico sem perder compreensão, controle e rastreabilidade."
    if "agenda" in t:
        return "Antes de começar os detalhes, vamos localizar o percurso. Esta agenda foi montada para sair dos fundamentos, passar pelas tecnologias e chegar a um sistema real, o BioByte, em que essas ideias podem ser observadas funcionando."
    if t == "a tese":
        return "Este é o argumento central da apresentação. Tudo o que veremos nos próximos blocos serve para examinar esta tese por ângulos diferentes: o modelo produz, os agentes organizam, a especificação orienta e os gates verificam."
    if "linha do tempo" in t:
        return "Para entender por que o desenvolvimento mudou, precisamos primeiro enxergar a sequência histórica. A tecnologia não apareceu pronta: cada salto aumentou a unidade de trabalho que o profissional consegue delegar à máquina."
    if "ia na saúde (1/3)" in t:
        return "Agora vamos trazer a inteligência artificial para o domínio médico. Neste primeiro slide, o foco é o prognóstico: usar dados disponíveis para estimar a probabilidade ou o tempo até um evento clínico. A finalidade não é substituir a decisão médica, mas organizar evidências para que o risco seja percebido mais cedo e de maneira mensurável."
    if "ia na saúde (2/3)" in t:
        return "Depois de estimar risco, passamos à segunda pergunta clínica: o que está acontecendo agora. Este slide introduz o diagnóstico, isto é, a classificação ou identificação de uma condição a partir de imagens, exames e sinais registrados no sistema."
    if "ia na saúde (3/3)" in t:
        return "A terceira pergunta é o que fazer depois de reconhecer o risco ou o diagnóstico. Por isso, este slide apresenta a IA aplicada ao tratamento: comparar intervenções, medir efeitos e apoiar condutas sem confundir correlação com benefício clínico."
    if "transformer" in t:
        return "Antes de falar em agentes e ferramentas, precisamos entender o motor que produz a linguagem. Este slide abre a caixa do Transformer e mostra, em termos técnicos, como uma sequência de tokens passa por atenção, camadas e probabilidades até resultar no próximo token."
    if "modelo" in t or "escala" in t or "moe" in t or "inferência" in t or "contexto longo" in t:
        return "Depois da arquitetura, precisamos entender quais escolhas de modelo afetam o sistema que vamos construir. Este slide trata de uma dimensão prática dos modelos de linguagem: capacidade, custo, memória, contexto e comportamento durante a inferência."
    if "rag" in t or "chunking" in t or "saída estruturada" in t or "avaliação" in t:
        return "Um modelo de linguagem sozinho não conhece automaticamente os documentos da organização nem oferece uma resposta auditável. Neste bloco, vamos ver como fornecer contexto, recuperar evidências e exigir uma saída que possa ser conferida por uma pessoa e por um teste."
    if "agente" in t or "tool use" in t or "composição" in t:
        return "Até aqui falamos do modelo como gerador de uma resposta. Agora mudamos a unidade de análise: um agente é um componente que recebe um objetivo, escolhe ou chama ferramentas, mantém um estado e participa de um fluxo de trabalho."
    if "protocol" in t or "mcp" in t or "a2a" in t or "okf" in t:
        return "Quando vários componentes colaboram, a integração não pode depender de convenções escondidas no prompt. Este slide apresenta os protocolos e formatos como contratos: eles definem como uma capacidade é descoberta, chamada, registrada e compartilhada."
    if "crewai" in t or "langgraph" in t or "autogen" in t or "framework" in t:
        return "Agora podemos comparar os frameworks com um critério comum. Não estamos escolhendo uma biblioteca pela aparência da API; estamos perguntando que parte do trabalho ela controla: a conversa, o estado, as ferramentas, os limites e a aprovação humana."
    if "ambiente" in t or "claude code" in t or "cursor" in t or "codex" in t:
        return "Além do framework que executa agentes, existe o ambiente em que a equipe projeta, inspeciona e altera o software. Este slide situa as ferramentas de desenvolvimento e mostra que contexto do repositório, permissões e verificações fazem parte do processo."
    if "vibe coding" in t or "inversão" in t or "ciclo sdd" in t or "spec" in t or "sdd" in t or "rastreabilidade" in t or "antipadr" in t:
        return "Chegamos ao problema de engenharia que conecta todos os blocos anteriores. Se a IA consegue produzir código rapidamente, a pergunta passa a ser como garantir que esse código corresponde ao que o sistema deveria fazer. É nesse ponto que entra o desenvolvimento orientado à especificação, o SDD."
    if "adaptação" in t or "sft" in t or "lora" in t or "rlhf" in t or "treinar" in t:
        return "Depois de entender o processo de desenvolvimento, podemos discutir se o próprio modelo precisa ser adaptado. A pergunta correta não é começar pelo treinamento, mas identificar qual limitação existe e escolher o menor mecanismo capaz de corrigi-la."
    if "biobyte" in t or "langnet" in t or "petri" in t or "evidência" in t:
        return "Agora vamos sair do conceito e acompanhar o caso BioByte. O objetivo desta parte é mostrar como uma especificação clínica se transforma em agentes, tarefas, ferramentas, lugares, transições, código e evidência de execução."
    if "co-scientist" in t:
        return "Antes de concluir, vamos olhar um segundo exemplo de orquestração multiagente. O AI Co-Scientist é útil aqui porque mostra que agentes podem gerar, criticar, ranquear e evoluir hipóteses quando existe uma função explícita de avaliação."
    if "conclus" in t or "pergunta" in t or "referência" in t:
        return "Estamos chegando ao fechamento. Este slide retoma a pergunta inicial e transforma o percurso em uma orientação prática para uma equipe que pretende usar IA em software real."
    return f"Neste slide, introduzimos {title.lower()}. Ele aparece neste ponto para ligar o conceito anterior ao próximo passo do processo de desenvolvimento."


def curated_script(index):
    """Textos curados para a sequência médica, que precisa ser didática e não
    pode perder o sentido por causa do corte automático de tempo."""
    return {
        5: ("Agora vamos trazer a inteligência artificial para o domínio médico. Neste primeiro slide, começamos pelo prognóstico, que significa estimar a probabilidade ou o tempo até um evento clínico. Um escore de risco combina fatores em um valor compreensível. A regressão logística estima a probabilidade de ocorrência. A análise de sobrevivência considera o tempo até o evento. O modelo de Cox mede como cada fator altera o risco ao longo do tempo. E o índice de concordância avalia se o modelo ordena corretamente pacientes de maior e menor risco. No BioByte, isso pode apoiar o risco de infecção relacionada à assistência, a densidade por dia de dispositivo e a definição de prioridades para bundles. A decisão clínica continua sendo humana, mas passa a ter evidências mensuráveis."),
        6: ("Depois de estimar o risco, precisamos responder à segunda pergunta: o que está acontecendo agora. Este slide introduz o diagnóstico, ou seja, a classificação de uma condição a partir de imagens, exames e sinais registrados no sistema. Redes neurais convolucionais podem analisar imagens; a U-Net pode segmentar uma lesão e medir sua extensão. Para dados tabulares, florestas aleatórias, máquinas de vetores de suporte, k-vizinhos e árvores de decisão oferecem formas diferentes de classificar. No contexto do BioByte, isso se relaciona à leitura de culturas, à identificação de multirresistência e à definição auditável de um caso. O resultado não deve ser apenas uma etiqueta: precisa indicar os critérios e as evidências que sustentam a classificação."),
        7: ("A terceira pergunta é o que fazer depois de reconhecer o risco ou o diagnóstico. Por isso, este slide apresenta a inteligência artificial aplicada ao tratamento. Um ensaio clínico randomizado compara grupos de forma controlada. A redução de risco absoluta mede a diferença observada entre eles. A inferência causal procura separar o efeito da intervenção de outras características dos pacientes, e o efeito médio do tratamento resume esse benefício na população estudada. No BioByte, a pergunta pode ser se um bundle reduz a ocorrência de IRAS ou se uma estratégia de stewardship altera a resistência antimicrobiana. Esses métodos não autorizam uma conduta automática: eles organizam a evidência para que a equipe compreenda o efeito e decida com responsabilidade."),
    }.get(index)


def plain(value):
    value = html.unescape(value or "")
    value = re.sub(r"<b>(.*?)</b>", r"\1", value, flags=re.S)
    value = re.sub(r"<i>(.*?)</i>", r"\1", value, flags=re.S)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\([^)]*~[^)]*\)", "", value)
    return re.sub(r"\s+", " ", value).strip()


def spoken(value, title):
    """Converte anotações de apresentação em prosa de locução."""
    text = plain(value)
    replacements = [
        (r"\bBoas-vindas e capa\.?", "Sejam bem-vindos"),
        (r"\bem cerca de 20 segundos, citando seus 40 anos de engenharia — e não volte mais ao assunto; a autoridade já está estabelecida\.?", "Eu trabalho há quarenta anos com engenharia de software"),
        (r"\be não volte mais ao assunto; a autoridade já está estabelecida\.?", ""),
        (r"\bMostre a agenda inteira\.?", "A agenda está organizada em três movimentos"),
        (r"\bLeia a frase da tese devagar e deixe-a no ar por um segundo\.?", "A frase da tese deve ser lida devagar"),
        (r"\bDepois enuncie as três consequências como promessas que você vai cumprir:\s*", "A tese tem três consequências: "),
        (r"\bNão desenvolva agora; só plante as três sementes\.?", "Essas três ideias orientarão o restante da apresentação."),
        (r"\bLeitura guiada — este é o slide que amarra a história\.?", "Este slide amarra a história da tecnologia."),
        (r"\bPrimeira das três frentes — aterrisse no domínio da plateia\.?", "Esta é a primeira das três frentes, o prognóstico aplicado ao domínio da plateia."),
        (r"\bSegunda frente — diagnóstico é decidir", "A segunda frente é o diagnóstico, que significa decidir"),
        (r"\bTerceira frente — tratamento é medir", "A terceira frente é o tratamento, que significa medir"),
        (r"\bLeia as cinco na tela:\s*", "As cinco regras são: "),
        (r"\bcom estas palavras:\s*", "a aplicação direta é esta: "),
        (r"\bfaça a ressalva obrigatória em voz alta:\s*", "é importante registrar a seguinte ressalva: "),
        (r"\breconfira estes valores na semana da palestra\.?", "esses valores precisam ser verificados na semana da palestra"),
        (r"\buse os exemplos deles a palestra inteira\.?", "os exemplos da palestra serão sempre desse domínio"),
        (r"\bmostro a curva no S28\.?", "a curva aparece no slide 28"),
        (r"\bfaçam a mesma pergunta a todos:\s*", "a pergunta comum para todos é: "),
        (r"\bAvise que\s+", "É importante entender que "),
        (r"\bPare ~40 s na caixa de 2017, o Transformer \(destacada\):\s*", "Em 2017, o Transformer aparece como a invenção que viabilizou tudo depois: "),
        (r"\bEntão — e aqui está o argumento real, ~60 s — desça para a raia de baixo: o que o desenvolvedor fazia\.\s*", "O argumento central aparece na raia de baixo, que mostra como mudou o trabalho do desenvolvedor. "),
        (r"\bA conclusão é apontando a última caixa:\s*", "A última caixa resume a conclusão: "),
        (r"\bPara eles:\s*", "No domínio hospitalar, isso permite "),
        (r"\bA frase da tese deve ser lida devagar\s*", "A tese é a seguinte: "),
        (r"\bA frase subtítulo em voz alta, porque ele anuncia a tese:\s*", "O subtítulo anuncia a tese: "),
        (r"\bSejam bem-vindos Eu começo me apresentando:\s*", "Sejam bem-vindos. Eu começo me apresentando: "),
        (r"\bsoftware A frase subtítulo", "software. O subtítulo"),
        (r"\bmovimentos A ideia é que", "movimentos. A ideia é que"),
        (r"\bA tese é a seguinte: A tese tem três consequências:\s*", "A tese tem três consequências: "),
        (r"\bA conclusão é apontando a última caixa:\s*", "A última caixa mostra a conclusão: "),
        (r"\binvenção que viabilizou tudo depois: a invenção que viabilizou tudo depois", "invenção que viabilizou tudo depois"),
        (r"\bUm minuto[^.]*\.\s*", ""),
        (r"\b90 segundos[^.]*\.\s*", ""),
        (r"\bDois minutos[^.]*\.\s*", ""),
        (r"\bTrês minutos[^.]*\.\s*", ""),
        (r"\bDois minutos e meio[^.]*\.\s*", ""),
        (r"\bUm minuto e meio[^.]*\.\s*", ""),
        (r"\bAqui vemos que 'usar ferramentas'", "Usar ferramentas"),
        (r"\bDê tempo[^.]*\.\s*", ""),
        (r"\bDê peso[^.]*\.\s*", ""),
        (r"\bvá devagar\.?", ""),
        (r"\brepare,?\s*", "o detalhe importante é que "),
        (r"\bque é o slide que a plateia mais vai fotografar —\s*", ""),
        (r"\bque é uma das ideias mais acionáveis da palestra\.\s*", ""),
        (r"\bMostre (?:o|a|os|as) ", "Aqui vemos "),
        (r"\bMostre\s+", "Aqui vemos "),
        (r"\bLeia (?:a|o) ", "A frase "),
        (r"\bApresente-se\s+", "Eu começo me apresentando: "),
        (r"\bApresente cada algoritmo pelo nome por extenso:\s*", "Aqui estão os algoritmos mais importantes: "),
        (r"\bExplique que\s+", "Isso significa que "),
        (r"\bExplique\s+", "O ponto é que "),
        (r"\bAponte\s+", "A imagem destaca "),
        (r"\bPercorra\s+", "O diagrama percorre "),
        (r"\bGaste\s+[^.]+\.\s*", ""),
        (r"\bDiga com todas as letras:\s*", "A formulação é direta: "),
        (r"\bDiga a frase:\s*", "A frase central é: "),
        (r"\bDiga a verdade incômoda:\s*", "A verdade incômoda é esta: "),
        (r"\bFeche com a frase[^:]*:\s*", "A conclusão é: "),
        (r"\bFeche com\s+", "A conclusão é "),
        (r"\bAgora faça a conexão explícita com\s+", "Isso se conecta diretamente com "),
        (r"\bAgora\s+aponte\s+", "A imagem destaca "),
        (r"\bAgora\s+", "Neste ponto, "),
        (r"\bPegue\s+", "Consideremos "),
        (r"\bDeixe o slide[^.]*\.\s*", ""),
        (r"\bPAUSE\.?", ""),
        (r"\bRespire\s+", ""),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\bDiga que\s+", "A ideia é que ", text, flags=re.I)
    text = re.sub(r"\bDiga tamb[eé]m que\s+", "Também é importante que ", text, flags=re.I)
    text = re.sub(r"\bDiga\s+", "", text, flags=re.I)
    text = re.sub(r"\bMostre\s+", "Aqui vemos ", text, flags=re.I)
    text = re.sub(r"\bExplique\s+", "O ponto é que ", text, flags=re.I)
    text = re.sub(r"\bAponte\s+", "A imagem destaca ", text, flags=re.I)
    text = re.sub(r"\bFeche\s+", "A conclusão é ", text, flags=re.I)
    text = re.sub(r"\bSiga\s+", "A sequência segue ", text, flags=re.I)
    text = re.sub(r"\bNão desenvolva agora;[^.]*\.\s*", "", text, flags=re.I)
    text = re.sub(r"\bA frase subtítulo em voz alta, porque ele anuncia a tese:\s*", "O subtítulo anuncia a tese: ", text, flags=re.I)
    text = re.sub(r"\bA conclusão é apontando a última caixa:\s*", "A última caixa mostra a conclusão: ", text, flags=re.I)
    text = re.sub(r"\bSejam bem-vindos\s+Eu começo", "Sejam bem-vindos. Eu começo", text, flags=re.I)
    text = re.sub(r"\bengenharia de software\s+O subtítulo", "engenharia de software. O subtítulo", text, flags=re.I)
    text = re.sub(r"\bmovimentos\s+A ideia é que", "movimentos. A ideia é que", text, flags=re.I)
    text = re.sub(r"\bA tese é a seguinte:\s+A tese tem", "A tese tem", text, flags=re.I)
    text = re.sub(r"\binvenção que viabilizou tudo depois:\s+a invenção que viabilizou tudo depois", "invenção que viabilizou tudo depois", text, flags=re.I)
    text = text.replace("a frase frase", "a frase")
    text = text.replace("Neste ponto, Aqui vemos", "Neste ponto, vemos")
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = text.replace("aparece no slide 28 (3)", "aparece no slide 28. (3)")
    if not text:
        text = f"Neste slide, tratamos de {title.lower()} e de sua importância para o desenvolvimento de software com inteligência artificial."
    return text[0].upper() + text[1:]


def words(text):
    return re.findall(r"\b[\wÀ-ÿ]+(?:[-'][\wÀ-ÿ]+)?\b", text)


def sentences(text):
    # Só considerar unidades encerradas por ponto/interrogação/exclamação.
    # Assim o roteiro nunca termina em uma enumeração ou em uma oração após
    # ponto e vírgula, o que seria inadequado para leitura em voz alta.
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def calibrate(text, minutes, title):
    target = max(20, round(minutes * WPM))
    result = []
    count = 0
    for sentence in sentences(text):
        n = len(words(sentence))
        if count + n <= target:
            result.append(sentence)
            count += n
        elif count < target:
            remaining = target - count
            pieces = sentence.split()
            # Mantemos a última unidade sem truncá-la no meio: o documento é
            # um texto para leitura, não uma lista de anotações cortadas.
            if remaining > 0 and n <= max(remaining + 18, round(target * .12)):
                result.append(sentence); count += n
            break
    additions = [
        "Essa mudança não elimina a responsabilidade humana; ela muda o lugar onde essa responsabilidade precisa aparecer.",
        "A equipe continua decidindo o significado do requisito, os limites do sistema e a evidência necessária para aceitar o resultado.",
        "O ganho de engenharia vem de tornar essas decisões explícitas, versionadas e verificáveis por outras pessoas.",
        "No BioByte, essa preocupação aparece quando uma decisão clínica precisa voltar ao requisito, ao dado utilizado e ao agente que a produziu.",
        "Por isso, a tecnologia só é útil quando permanece ligada ao contexto do domínio e a um mecanismo claro de validação.",
        "Essa é a linha que percorre a apresentação: capacidade de geração, contexto adequado, execução controlada e prova do resultado.",
    ]
    if count < round(target * .95):
        for sentence in additions * 3:
            n = len(words(sentence))
            result.append(sentence); count += n
            if count >= target * .95:
                break
    return " ".join(result), target, count


def build():
    deck.build_v2()
    previews.main()
    meta = deck.base.META
    if len(meta) != 70:
        raise RuntimeError(f"Esperados 70 slides; encontrados {len(meta)}")

    lines = [
        "# Roteiro narrado integral — Engenharia de IA, SDD e BioByte",
        "",
        "**Versão:** V4, texto didático e literal para leitura em voz alta",
        "**Duração planejada:** 120 minutos, incluindo intervalo, vídeo de 15 minutos e perguntas",
        "**Velocidade de calibração:** 130 palavras por minuto",
        "",
        "> O texto abaixo é a fala do narrador. Não são instruções de apresentação. As lâminas do vídeo e do intervalo estão identificadas como tempo reservado, pois não são fala contínua do narrador.",
        "",
    ]
    report = []
    for index, item in enumerate(meta, start=1):
        title = item["title"]
        minutes = item["minutes"]
        if title.startswith("DEMO"):
            script = ("Agora começa o vídeo da demonstração do BioByte. Durante os próximos quinze minutos, acompanhe o caminho completo: "
                      "o documento de agentes e tarefas, a especificação, os dados, a interface, os agentes, as tarefas, o YAML, "
                      "o registro das ferramentas MCP, a sequência, a rede de Petri, a geração do código, os testes, a aplicação e o gate. "
                      "A demonstração também mostra uma lacuna registrada, porque uma prova técnica confiável precisa revelar o que ainda está em desenvolvimento. "
                      "Ao final do vídeo, retomaremos a fala para conectar a execução observada ao método SDD.")
            count = len(words(script)); target = count
            timing = "15 minutos reservados para o vídeo; o texto é a introdução e não uma narração sobreposta ao vídeo."
        elif title.lower() in {"intervalo", "perguntas"}:
            script = ("Neste momento, fazemos uma pausa programada. Retomaremos exatamente do ponto indicado na agenda." if title.lower() == "intervalo" else
                      "Agora abro para perguntas. A tese que orienta a conversa é simples: gerar código ficou acessível, mas especificar, verificar e manter rastreabilidade continuam sendo responsabilidades de engenharia.")
            target = len(words(script)); timing = "Tempo reservado para interação; não é fala contínua pré-gravada."
        else:
            raw = curated_script(index) or (didactic_context(index, title) + " " + spoken(item["script"], title))
            script, target, count = calibrate(raw, minutes, title)
            timing = f"{count} palavras calibradas para aproximadamente {minutes:.2f} minutos a {WPM} palavras por minuto."
        lines.extend([
            f'<div class="slide" id="slide-{index}"></div>',
            f"# Slide {index:02d} — {title}", "",
            f"**Tempo da lâmina:** {minutes:.2f} minutos", "",
            f"![Tela da lâmina {index:02d}](roteiro_narrado_iasdd_v2_biobyte_slides/slide_{index:02d}.png)", "",
            "## Texto integral para ler", "", script, "",
            f"*{timing}*", "",
        ])
        report.append((index, minutes, len(words(script))))

    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    body = markdown(MD_OUT.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
    css = """
    body { font-family: DejaVu Sans, sans-serif; font-size:10.5pt; color:#172033; line-height:1.45; margin:0 1.5cm; }
    h1 { font-size:18pt; color:#263b8f; margin-top:0; border-bottom:1px solid #ccd3e1; padding-bottom:5px; }
    h2 { font-size:13.5pt; color:#324b9b; margin-top:1.1em; }
    p { margin:.5em 0; } blockquote { border-left:4px solid #536dce; padding:8px 12px; background:#f0f3fb; }
    img { display:block; width:100%; max-height:9.6cm; object-fit:contain; border:1px solid #ccd3e1; margin:8px 0 12px; }
    .slide { page-break-before:always; } .slide:first-child { page-break-before:auto; }
    @page { size:A4; margin:1.5cm 1.3cm; }
    """
    HTML(string=f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>", base_url=str(ROOT)).write_pdf(str(PDF_OUT))
    print("MD:", MD_OUT, MD_OUT.stat().st_size, "bytes")
    print("PDF:", PDF_OUT, PDF_OUT.stat().st_size, "bytes")
    print("slides:", len(meta), "tempo:", sum(x[1] for x in report), "min", "fala calibrada:", sum(x[2] for x in report), "palavras")


if __name__ == "__main__":
    build()
