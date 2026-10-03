# -*- coding: utf-8 -*-
"""V5 didática: abre cada bloco e define os conceitos antes dos exemplos."""
from pathlib import Path
import re
from pptx import Presentation

HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "apresentacao_iasdd_v5_biobyte.pptx"
import sys
sys.path.insert(0, str(HERE))
import build_deck_iasdd_v4_biobyte as v4

D = v4.D
TOTAL = 86


def divider(prs, block, number, title, subtitle, message):
    s = D._blank(prs)
    c1, c2, c3 = D.FAM["violet"]
    D._rect(s, 0, 0, D.SW, D.SH, fill=c3)
    D._rect(s, 0, 0, .22, D.SH, fill=c1)
    D._txt(s, .85, 1.0, 11.5, .45, [[(f"BLOCO {number}", {"size": 17, "bold": True, "color": c1})]])
    D._txt(s, .85, 2.0, 11.2, 1.0, [[(title, {"size": 30, "bold": True, "color": D.INK})]])
    D._txt(s, .88, 3.25, 10.8, .65, [[(subtitle, {"size": 19, "color": c1})]])
    D.callout(s, block, [(message, {"size": 17, "color": D.INK})], y=4.65, h=1.05)
    D.footer(s, block, 0, TOTAL)
    v4.register(f"BLOCO {number} — {title}", .35,
                f"Agora começa o bloco {number}, {title.lower()}. {message}")


def concept(prs, block, title, definition, why, example, minutes, script):
    s = D._blank(prs)
    D.header(s, block, f"Bloco {block} · Conceito", title)
    D._txt(s, .7, 1.85, 11.8, .85, [[(definition, {"size": 21, "bold": True, "color": D.FAM['violet'][0]})]])
    D.cards(s, block, [("O QUE É", definition), ("POR QUE IMPORTA", why), ("NO BIOBYTE", example)], x=.7, y=3.0, size=14)
    D.footer(s, block, 0, TOTAL)
    v4.register(title, minutes, script)


def llm_intro(prs):
    concept(prs, 2, "O que é um modelo de linguagem?",
            "Um modelo de linguagem aprende padrões para prever e gerar sequências de tokens.",
            "Ele não é ainda um agente nem uma aplicação: é o motor probabilístico que produz a próxima parte da resposta.",
            "No BioByte, ele interpreta documentos, propõe requisitos e ajuda a gerar artefatos, sempre dentro de um fluxo controlado.", 1.0,
            "Antes de abrir a anatomia do Transformer, precisamos definir o objeto. Um modelo de linguagem aprende padrões em grandes conjuntos de texto e usa esses padrões para prever o próximo token. Isso explica sua capacidade de escrever, resumir e transformar informação, mas não o transforma automaticamente em agente ou aplicação. No BioByte, o modelo é o motor que interpreta documentos e ajuda a produzir artefatos; o processo, as ferramentas, os limites e a validação ainda precisam ser construídos ao redor dele.")


def context_intro(prs):
    concept(prs, 4, "O que significa contexto para uma IA?",
            "Contexto é a informação disponível para o modelo produzir uma resposta situada.",
            "Ele combina instruções, histórico, documentos recuperados, estado da tarefa e resultados de ferramentas.",
            "Um agente do BioByte precisa saber o requisito vigente, o caso clínico, as regras NHSN e a evidência consultada.", 1.0,
            "Agora que sabemos o que é um modelo, precisamos perguntar de que informação ele dispõe em cada chamada. Contexto é tudo aquilo que orienta a resposta: instruções, histórico, documentos, estado da tarefa e resultados de ferramentas. Em um agente, contexto não é apenas uma janela de texto; é a visão operacional do problema. No BioByte, essa visão pode incluir o requisito vigente, o caso clínico, as regras NHSN e a evidência retornada pela microbiologia.")


def agent_intro(prs):
    concept(prs, 5, "De modelo para agente",
            "Um agente usa um modelo dentro de um ciclo de objetivo, contexto, ferramenta, estado e verificação.",
            "A diferença está na execução: o agente decide o próximo passo e observa o resultado antes de continuar.",
            "O agente de vigilância consulta dados, aplica critérios, registra evidências e devolve uma classificação rastreável.", 1.0,
            "Até aqui falamos do modelo e do contexto. Um agente surge quando esse modelo participa de um ciclo de execução: recebe um objetivo, observa o contexto, escolhe ou chama uma ferramenta, atualiza o estado e verifica o resultado. Portanto, agente não é apenas um prompt comprido. É um componente com responsabilidade, limites e evidência. No BioByte, o agente de vigilância consulta dados, aplica critérios e devolve uma classificação rastreável.")


def sdd_intro(prs):
    concept(prs, 9, "Por que precisamos de SDD?",
            "Se a IA gera artefatos rapidamente, a especificação precisa orientar e verificar essa geração.",
            "SDD transforma intenção em contratos rastreáveis antes de transformar contratos em código.",
            "No LangNet, requisitos, especificação, agentes, tarefas, Petri, código e testes formam uma cadeia de evidências.", 1.0,
            "Chegamos ao problema de engenharia. Se a IA consegue gerar código, telas e tarefas rapidamente, como sabemos que o resultado corresponde ao que deveria ser feito? O SDD responde deslocando o centro do processo para a especificação. A especificação define contratos, rastreabilidade e critérios de aceitação antes da implementação. No LangNet, isso aparece como uma cadeia que liga requisitos, agentes, tarefas, rede de Petri, código e testes.")


def finetune_intro(prs):
    concept(prs, 10, "Como adaptar um modelo ao negócio?",
            "Prompt, contexto, RAG e fine-tuning são mecanismos diferentes de adaptação.",
            "A escolha depende de onde está o problema: instrução, conhecimento, comportamento ou capacidade.",
            "No BioByte, RAG pode fornecer documentos e fine-tuning pode ajustar estilo ou tarefa, sem substituir a validação.", 1.0,
            "Depois de definir o processo, podemos perguntar se o modelo precisa ser adaptado. Prompt organiza uma instrução; contexto fornece informação; RAG recupera conhecimento externo; fine-tuning altera o comportamento aprendido a partir de exemplos. São mecanismos diferentes e não devem ser tratados como sinônimos. No BioByte, documentos clínicos podem entrar por recuperação, enquanto exemplos cuidadosamente preparados poderiam ajustar estilo ou tarefa. Em qualquer caso, a validação continua sendo necessária.")


def biobyte_intro(prs):
    concept(prs, 11, "O estudo de caso: BioByte e LangNet",
            "Agora vamos acompanhar a passagem dos conceitos para uma aplicação executável.",
            "O pipeline transforma uma especificação em artefatos, execução e evidência — não apenas em código.",
            "A demonstração percorre documentos, requisitos, agentes, tarefas, Petri, código, testes e aplicação.", .8,
            "Depois de construir os conceitos, vamos acompanhar um caso concreto. O BioByte mostra como uma especificação de saúde pode atravessar o LangNet e se transformar em artefatos executáveis. A demonstração não será apenas uma tela de código: ela percorrerá documentos, requisitos, agentes, tarefas, rede de Petri, geração, testes, aplicação e evidência. É essa cadeia que conecta a teoria ao sistema real.")


def build():
    v4.base.base.META = []
    prs = v4.base.base.D.new_prs()
    f = v4.base.base
    funcs = [
        f.s1, f.s2, f.s3,
        lambda p: divider(p, 1, 1, "Da IA clássica ao desenvolvimento com IA", "dados, modelos e a mudança da unidade de trabalho", "Primeiro estabelecemos o terreno: como modelos aprendem, como são avaliados e por que isso importa para software."),
        f.s4, f.s5, f.s5b, f.s5c, v4.ml_pipeline, v4.ml_evaluation, v4.ml_algorithms,
        lambda p: divider(p, 2, 2, "Modelos de linguagem", "o motor probabilístico por trás das aplicações atuais", "Antes da arquitetura, definimos o que é um modelo de linguagem e qual problema o Transformer resolve."),
        llm_intro, f.s6, f.s7, f.s8, f.s9, f.s10, f.s11, f.s12, f.s13,
        lambda p: divider(p, 3, 3, "O que muda quando o modelo ganha escala", "capacidade, custo, memória e limites", "Agora conectamos arquitetura e escala às decisões práticas de engenharia."),
        f.s14, f.s15,
        lambda p: divider(p, 4, 4, "Contexto, RAG e informação externa", "como o modelo recebe conhecimento situado", "Um modelo sem contexto não conhece automaticamente os documentos e o estado do sistema."),
        context_intro, f.s16, f.s17, f.s18, f.s19, f.s20,
        lambda p: divider(p, 5, 5, "Agentes e execução", "do texto gerado ao trabalho coordenado", "Agora definimos agente, ferramentas, estado, laço e composição."),
        agent_intro, f.s21, f.s22b, f.s23, f.s24, f.s25, f.s26, f.s27, f.s28,
        lambda p: divider(p, 6, 6, "Protocolos e contratos entre componentes", "como capacidades são descobertas e integradas", "A colaboração entre componentes precisa de contratos, formatos e rastros."),
        f.s29, f.s30, f.s31, f.s32, f.s33,
        f.s_intervalo,
        lambda p: divider(p, 7, 7, "Frameworks e SDKs", "diferentes formas de orquestrar agentes", "Só depois de definir agente e contratos faz sentido comparar frameworks."),
        f.s34, f.s35, f.s36, f.s37, v4.base.s38, v4.base.s39, f.s40, f.s41, f.s42, f.s43,
        lambda p: divider(p, 8, 8, "Ambientes de desenvolvimento com IA", "ferramentas para projetar, inspecionar e alterar software", "O ambiente também participa do processo: contexto do repositório, permissões e verificações."),
        f.s44, f.s45, f.s46,
        lambda p: divider(p, 9, 9, "SDD: especificar antes de delegar", "da intenção ao artefato verificável", "Agora reunimos modelo, contexto, agentes e ferramentas em um método de engenharia."),
        sdd_intro, f.s47, f.s48, f.s49, f.s50, f.s51, f.s52, f.s53, f.s54, f.s55,
        lambda p: divider(p, 10, 10, "Adaptação e fine-tuning", "quando prompt, RAG ou treinamento são a resposta", "Fine-tuning é uma escolha de engenharia, não o primeiro recurso para qualquer problema."),
        finetune_intro, f.s56, f.s57, f.s58, f.s59, f.s60,
        lambda p: divider(p, 11, 11, "BioByte: da especificação à execução", "o caso completo no LangNet", "Agora observamos a cadeia real e a evidência produzida em cada etapa."),
        biobyte_intro, v4.base.s60, v4.base.s61, f.s62, f.s63, f.s64, f.s65, f.s66,
        lambda p: divider(p, 12, 12, "Fechamento", "o que levar para a prática", "Encerramos retomando a tese e abrindo espaço para perguntas."),
        f.s67,]
    for fn in funcs: fn(prs)
    # Mantém os mesmos blocos de duração da V4; as novas lâminas comprimem
    # a fala dentro de cada bloco, sem aumentar os 120 minutos.
    targets = {0: 3.0, 1: 10.0, 2: 9.0, 3: 2.0, 4: 8.0, 5: 11.0, 6: 9.0,
               7: 9.0, 8: 3.0, 9: 16.0, 10: 4.0, 11: 31.0, 12: 5.0}
    for block, target in targets.items():
        rows = [x for x in f.META if x["block"] == block]
        if not rows: continue
        if block == 11:
            video = [x for x in rows if x["title"].startswith("DEMO")]
            other = [x for x in rows if x not in video]
            if video: video[0]["minutes"] = 20.0; video[0]["title"] = "DEMO BioByte: 20 minutos"
            factor = (target - 20.0) / sum(x["minutes"] for x in other)
            for x in other: x["minutes"] *= factor
        else:
            factor = target / sum(x["minutes"] for x in rows)
            for x in rows: x["minutes"] *= factor
    acum = 0.0
    for x in f.META: acum += x["minutes"]; x["acum"] = acum
    prs.save(str(OUT))
    v4.fix_text_and_numbers(OUT)
    print(f"PPTX: {OUT} slides: {len(prs.slides)} tempo: {sum(x['minutes'] for x in f.META):.2f} min")


if __name__ == "__main__": build()
