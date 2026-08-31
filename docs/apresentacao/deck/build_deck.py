# -*- coding: utf-8 -*-
"""Deck — Blocos 0,1,2 (S1–S13). Estilo vibrante (cor por bloco, cartões). .pptx + PDF roteiro."""
import os
import decklib as D
import diagrams as DG
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

DECK_TITLE = "Engenharia de IA e Desenvolvimento de Software Orientado a Especificação"
TOTAL = 68
META = []

def reg(n, block, title, minutes, acum, script, label=None):
    META.append({"n": n, "block": block, "title": title, "minutes": minutes, "acum": acum,
                 "script": script, "label": label})


# ===================== BLOCO 0 =====================
def s1(prs):
    s = D._blank(prs)
    D.cover(s, DECK_TITLE,
            "Do modelo à spec: como times de software crítico incorporam IA sem perder auditabilidade.",
            "120 minutos · desenvolvedores sêniores · sistemas de controle de infecção hospitalar (IRAS)")
    D.notes(s, "Abertura.")
    reg(1, 0, "Capa", 0.5, 0.5,
        "<b>Boas-vindas e capa.</b> Apresente-se em cerca de 20 segundos, citando seus 40 anos de engenharia — "
        "e não volte mais ao assunto; a autoridade já está estabelecida. Leia o subtítulo em voz alta, porque "
        "ele anuncia a tese: a palestra não é sobre 'a IA que escreve código', é sobre <b>como incorporar IA em "
        "software crítico sem perder auditabilidade</b>. A sigla IRAS — Infecções Relacionadas à Assistência à "
        "Saúde — é o domínio da plateia; use os exemplos deles a palestra inteira. <i>(~30 s)</i>")


def s2(prs):
    s = D._blank(prs); D.header(s, 0, "Bloco 0 · Abertura", "Agenda: doze blocos, três pilares")
    rows = [
        ["0", "Abertura e agenda", "3"],
        ["1", "Linha do tempo: do Perceptron aos agentes", "3,5"],
        ["*2", "*MODELOS DE LINGUAGEM (LLMs) — arquitetura e panorama", "14"],
        ["3", "O que mudou para quem escreve software", "2"],
        ["4", "Engenharia de contexto e RAG", "8"],
        ["5", "Agentes: anatomia, ferramentas, padrões, falhas", "14"],
        ["6", "Protocolos e formatos de interoperabilidade", "7,5"],
        ["*9", "*DESENVOLVIMENTO ORIENTADO A ESPECIFICAÇÃO (SDD)", "19"],
        ["*11", "*OS SISTEMAS: LangNet, demonstração, AI Co-Scientist, Redes de Petri", "15,5"],
    ]
    D.table(s, 0, ["Bloco", "Tema", "min"], rows, x=0.6, y=2.0, w=8.7, fsize=13.5, header_fs=13)
    for i, (num, name, desc, col) in enumerate([
        ("①", "LLMs", "o motor: o que o modelo é e o que não é", "indigo"),
        ("②", "SDD", "o método: especificar e verificar", "violet"),
        ("③", "Sistemas", "a prova: nossos sistemas rodando", "sky")]):
        c1, c2, c3 = D.FAM[col]; yy = 2.0 + i*1.45
        D._rect(s, 9.65, yy, 3.1, 1.3, fill=c3, rounded=True, radius=0.09)
        D._rect(s, 9.65, yy, 0.12, 1.3, fill=c1)
        D._txt(s, 9.85, yy+0.12, 2.8, 0.5, [[(num+"  ", {"size": 22, "bold": True, "color": c1}),
               (name, {"size": 19, "bold": True, "color": c1})]])
        D._txt(s, 9.85, yy+0.68, 2.8, 0.55, [[(desc, {"size": 12.5, "color": D.INK})]], line_spacing=1.05)
    D.footer(s, 0, 2, TOTAL)
    reg(2, 0, "Agenda", 1.5, 2.0,
        "<b>Agenda em uma tela.</b> Mostre os doze blocos com o tempo ao lado, mas não leia todos — aponte para "
        "os <b>três pilares</b> à direita, que são o esqueleto da palestra: <b>LLMs</b> (o Bloco 2, o motor — o "
        "que o modelo de linguagem de grande porte realmente é), <b>SDD</b> (o Bloco 9, o método — "
        "Desenvolvimento de Software Orientado a Especificação, do inglês <i>Spec-Driven Development</i>) e "
        "<b>Sistemas</b> (o Bloco 11, a prova, com os nossos dois sistemas rodando). Diga que a agenda reaparece "
        "destacada na abertura dos blocos 5, 9 e 11 — é o mapa para a plateia não se perder em duas horas. "
        "<i>(~1 min)</i>")


def s3(prs):
    s = D._blank(prs); D.header(s, 0, "Bloco 0 · Abertura", "A tese central da palestra")
    D.quote(s, 0, [("“O gargalo deixou de ser escrever código.  ", {"size": 25, "bold": True, "color": D.FAM['indigo'][0]}),
                   ("Passou a ser especificar e verificar.”", {"size": 25, "bold": True, "color": D.FAM['sky'][0]})],
            y=2.05, h=1.5)
    D.cards(s, 0, [
        ("Capacidade virou mercadoria comum (commodity).",
         "Qualquer um chama uma API e gera código; o que separa os times é o método — não o acesso ao modelo."),
        ("Agente sem portão de verificação degrada de forma previsível.",
         "Sem um “gate” (portão que confere cada passo), a taxa de erro cai de um jeito que a matemática prevê — mostramos a curva no S28."),
        ("Especificação executável é o que torna código de IA auditável.",
         "Condição inegociável em software de saúde: sem spec verificável, não há como provar conformidade."),
    ], x=0.6, y=3.85, size=17.5)
    D.footer(s, 0, 3, TOTAL)
    reg(3, 0, "A tese", 1.0, 3.0,
        "<b>Este é o slide-âncora; ele reaparece no fechamento (S65).</b> Leia a frase da tese devagar e "
        "deixe-a no ar por um segundo. Depois enuncie as três consequências como <b>promessas que você vai "
        "cumprir</b>: (1) gerar código virou mercadoria comum — qualquer um chama uma interface de programação; "
        "o que separa os times é o método de especificar e verificar. (2) Um agente sem <i>gate</i> — sem um "
        "portão que verifica cada passo — não falha de forma aleatória: ele degrada de um jeito que a matemática "
        "prevê, e mostro a curva no S28. (3) A especificação executável é o que transforma código de IA em algo "
        "auditável — e para quem vende software médico, auditabilidade não é luxo, é a diferença entre "
        "conformidade e não conformidade. Não desenvolva agora; só plante as três sementes. <i>(~1 min)</i>")


# ===================== BLOCO 1 =====================
def s4(prs):
    s = D._blank(prs); D.header(s, 1, "Bloco 1 · Linha do tempo", "Do Perceptron ao desenvolvimento agêntico")
    D.image_center(s, os.path.join("diagrams", "s4_timeline.png"), x=0.5, y=1.95, w=D.SW-1.0, h=D.SH-2.45, block=1)
    D.footer(s, 1, 4, TOTAL)
    reg(4, 1, "Linha do tempo: Perceptron → agentes", 3.0, 6.0,
        "<b>Leitura guiada — este é o slide que amarra a história.</b> Gaste ~30 s indo de 1958 a 2012 na raia "
        "de cima e diga a frase que resume tudo: <i>'a ideia da rede neural é de 1958; o que mudou não foi a "
        "teoria, foi a capacidade de processamento e a quantidade de dados'</i>. Pare ~40 s na caixa de "
        "<b>2017, o Transformer</b> (destacada): a invenção que viabilizou tudo depois. Siga a seta curva até "
        "2020 e diga <i>'a mesma arquitetura, só que maior'</i> — o GPT-3 não é uma ideia nova, é escala. Gaste "
        "~40 s no salto de 2022 (o ChatGPT e o alinhamento a instruções). Então — e aqui está o argumento real, "
        "~60 s — desça para a <b>raia de baixo: o que o desenvolvedor fazia</b>. A unidade de trabalho mudou "
        "cinco vezes: projetar características à mão, treinar o próprio modelo, fazer <i>ajuste fino</i> "
        "(fine-tune) sobre um modelo pronto, chamar uma interface de programação (API), e hoje — <b>orquestrar, "
        "especificar e verificar</b>. Feche apontando a última caixa: 'é aqui que estamos, e é sobre isso a "
        "palestra'. Siglas: MLP = perceptron de múltiplas camadas; CNN = rede neural convolucional; LSTM = rede "
        "de memória de longo-curto prazo. <i>(~3 min)</i>")


def s5(prs):
    s = D._blank(prs); D.header(s, 1, "Bloco 1 · Linha do tempo", "Onde a IA já está na área de vocês")
    colw = (D.SW-1.2-0.4)/2
    b, t = D.panel(s, 0.6, 2.05, colw, 3.5, block=12 if False else 1)  # antes: cinza
    D._rect(s, 0.6, 2.05, colw, 3.5, fill=D.FAM['slate'][2], rounded=True, radius=0.06)
    D._rect(s, 0.6, 2.05, 0.12, 3.5, fill=D.FAM['slate'][0])
    D._txt(s, 0.9, 2.2, colw-0.5, 0.5, [[("ANTES", {"size": 15, "bold": True, "color": D.FAM['slate'][0]})]])
    D.bullets(s, [
        (0, [("escores de risco tabulares e preditivos de sepse", "n")]),
        (0, [("redes convolucionais (CNN) em imagem médica", "n")]),
        (0, [("alertas disparados por ", "n"), ("regra fixa", "b")]),
    ], x=0.9, y=2.85, w=colw-0.6, size=16, block=12 if False else 1)
    x2 = 0.6+colw+0.4
    D._rect(s, x2, 2.05, colw, 3.5, fill=D.FAM['violet'][2], rounded=True, radius=0.06)
    D._rect(s, x2, 2.05, 0.12, 3.5, fill=D.FAM['violet'][0])
    D._txt(s, x2+0.3, 2.2, colw-0.5, 0.5, [[("AGORA", {"size": 15, "bold": True, "color": D.FAM['violet'][0]})]])
    D.bullets(s, [
        (0, [("extração ", "b"), ("estruturada", "n"), (" de texto clínico livre", "n")]),
        (0, [("critérios de caso sobre a ", "n"), ("evolução narrativa", "b"), (" do prontuário", "n")]),
        (0, [("agentes com ferramentas sobre as ", "n"), ("bases hospitalares", "b")]),
    ], x=x2+0.3, y=2.85, w=colw-0.6, size=16, block=1)
    D.callout(s, 1, [("O que mudou foi o acesso ao ", {"size": 18, "color": D.INK}),
                     ("texto livre do prontuário", {"size": 18, "bold": True, "color": D.FAM['violet'][0]}),
                     (" — antes ilegível para a máquina, agora estruturável.", {"size": 18, "color": D.INK})],
              y=5.75, h=1.0)
    D.footer(s, 1, 5, TOTAL)
    reg(5, 1, "Onde a IA já está na área de vocês", 0.5, 6.5,
        "<b>Aterrisse no domínio da plateia — rápido, 30 s.</b> A IA já estava no hospital: escores de risco, "
        "preditivos de sepse, redes convolucionais lendo raio-X, alertas por regra. O que mudou de qualidade "
        "não foi 'ter IA' — foi passar a <b>ler o texto livre do prontuário</b>, que sempre foi a maior fonte de "
        "informação clínica e a mais inacessível para a máquina. Diga a frase de fecho: 'o que mudou foi o "
        "acesso ao texto livre' — e é isso que abre a porta para tudo que vem depois na palestra. <i>(~30 s)</i>")


# ===================== BLOCO 2 — LLMs =====================
def s6(prs):
    s = D._blank(prs); D.header(s, 2, "Bloco 2 · LLMs", "Anatomia do Transformer")
    D.image_center(s, os.path.join("diagrams", "s6_transformer.png"), x=0.6, y=1.95, w=6.0, h=D.SH-2.45, block=2)
    D.cards(s, 2, [
        ("Q, K, V (consulta, chave, valor).",
         "Cada token faz uma pergunta; todos anunciam o que têm; a semelhança decide de quem ele copia informação."),
        ("Multi-cabeça.",
         "Várias relações capturadas em paralelo, cada cabeça olhando um aspecto diferente."),
        ("O ponto de engenharia: a atenção é O(n²).",
         "Custo por token, tamanho da janela e toda a economia de contexto nascem dessa quadrática.", "warn"),
    ], x=6.9, y=2.05, w=D.SW-7.5, size=15.5)
    D.footer(s, 2, 6, TOTAL)
    reg(6, 2, "Anatomia do Transformer", 3.0, 9.5,
        "<b>Único slide de arquitetura em que vale gastar 3 minutos — tudo depois é engenharia em cima desta "
        "caixa.</b> Suba o diagrama de baixo para cima: o texto vira <b>tokens</b> (pedaços de palavra), os "
        "tokens viram <b>embeddings</b> (vetores) com a posição codificada (RoPE, codificação posicional "
        "rotativa). Aí entra o bloco que se repete N vezes: <b>atenção multi-cabeça</b>, soma residual e "
        "normalização, rede <i>feed-forward</i>, de novo soma e normalização. No topo, uma projeção vira "
        "<b>logits</b>, o <b>softmax</b> vira probabilidade sobre o vocabulário, e a amostragem escolhe o "
        "próximo token. Explique Q, K, V em 40 s com a analogia de busca: cada token faz uma pergunta "
        "(<i>query</i>), todos anunciam o que têm (<i>keys</i>), e a semelhança decide de quem ele copia "
        "informação (<i>value</i>); várias 'cabeças' fazem isso em paralelo. <b>O ponto que a plateia tem que "
        "levar:</b> a atenção custa O(n²) — cresce com o quadrado do tamanho da entrada. É daí que vêm o custo "
        "por token, o limite de janela e toda a indústria de 'contexto longo' que veremos no S13. "
        "<i>(~3 min)</i>")


def s7(prs):
    s = D._blank(prs); D.header(s, 2, "Bloco 2 · LLMs", "Por que o Transformer venceu")
    D.cards(s, 2, [
        ("Recorrência (LSTM) é sequencial no treino.",
         "Uma palavra depois da outra — não aproveita a placa de vídeo."),
        ("Atenção é paralelizável.",
         "Todos os tokens de uma vez, na GPU. Foi isso que mudou o jogo."),
        ("Não venceu por qualidade por token — venceu por VAZÃO de treinamento.",
         "Deu para treinar modelos muito maiores em tempo viável. Escala, não elegância."),
        ("A arquitetura de hoje: decoder-only, autorregressiva, objetivo único.",
         "Um só alvo de treino: prever o próximo token."),
    ], x=0.6, y=2.05, size=16.5)
    D.footer(s, 2, 7, TOTAL)
    reg(7, 2, "Por que o Transformer venceu", 1.0, 10.5,
        "<b>Um minuto, uma ideia contraintuitiva.</b> A LSTM — a rede recorrente que dominava sequências — "
        "processa palavra por palavra, em ordem, então o treino é sequencial e não aproveita a placa de vídeo. "
        "A atenção olha todos os tokens ao mesmo tempo, então <b>paraleliza</b>. O Transformer não ganhou por "
        "ser melhor 'por palavra'; ganhou por <b>vazão</b> (throughput): deu para treinar modelos muito maiores "
        "em tempo viável. E feche com a frase que desmistifica tudo: os modelos que vocês usam são "
        "<b>decoder-only</b>, autorregressivos, com um único objetivo de treino — prever o próximo token. Diga "
        "com todas as letras: <i>'não existe um módulo de raciocínio, nem um módulo de código; existe previsão "
        "de próximo token, e o raciocínio e o código emergiram dela'</i>. Isso reposiciona a plateia: o modelo é "
        "um previsor estatístico, não um pensador — e é por isso que precisamos de portões de verificação. "
        "<i>(~1 min)</i>")


def s8(prs):
    s = D._blank(prs); D.header(s, 2, "Bloco 2 · LLMs", "Escala e o que emerge dela")
    D.cards(s, 2, [
        ("Leis de escala.",
         "Mais dados + mais parâmetros + mais processamento → menos erro, de forma previsível. Foi o que justificou o investimento."),
        ("O salto de 2020: aprendizado no contexto (in-context learning).",
         "O modelo aprende a tarefa na hora da resposta, pelos exemplos do próprio prompt, sem tocar nos pesos."),
        ("Consequência: prompt e RAG passam a funcionar.",
         "E o ajuste fino (fine-tuning) deixou de ser o caminho obrigatório."),
        ("Deslocamento recente: do processamento no TREINO para o processamento na RESPOSTA.",
         "O modelo “pensa mais” na hora — volta idêntico no AI Co-Scientist (S62)."),
    ], x=0.6, y=2.05, size=16)
    D.footer(s, 2, 8, TOTAL)
    reg(8, 2, "Escala e o que emerge dela", 1.5, 12.0,
        "<b>90 segundos sobre o que a escala trouxe de graça.</b> As <b>leis de escala</b> são a descoberta de "
        "que o erro cai de forma previsível conforme você aumenta dados, parâmetros e capacidade de "
        "processamento — foi isso que justificou o investimento bilionário. Mas o salto conceitual de 2020 foi o "
        "<b>aprendizado no contexto</b> (in-context learning): o modelo passa a aprender a tarefa a partir dos "
        "exemplos que você põe no próprio prompt, na hora da resposta, <b>sem retreinar</b>. É esse fenômeno que "
        "faz a engenharia de prompt e o RAG funcionarem — e que tirou o <i>ajuste fino</i> de ser o caminho "
        "obrigatório. Termine marcando um ponto que volta mais tarde: a fronteira recente deslocou o "
        "processamento do <b>treino</b> para a <b>resposta</b> — modelos que 'pensam mais' antes de responder. "
        "No S62, o AI Co-Scientist da Google usa exatamente isso: mais processamento na hora da resposta produz "
        "hipóteses melhores. <i>(~1,5 min)</i>")


def s9(prs):
    s = D._blank(prs); D.header(s, 2, "Bloco 2 · LLMs", "MoE: mistura de especialistas")
    D.image_center(s, os.path.join("diagrams", "s9_moe.png"), x=0.6, y=1.95, w=D.SW-1.2, h=D.SH-3.1, block=2)
    D.callout(s, 2, [("MoE = ", {"size": 15, "bold": True, "color": D.FAM['sky'][0]}),
                     ("Mixture of Experts", {"size": 15, "italic": True, "color": D.MUTED}),
                     (" (mistura de especialistas). Ex.: DeepSeek-V4-Pro tem 1,6 trilhão de parâmetros totais, mas só 49 bilhões ativos por token.",
                      {"size": 15, "color": D.INK})], y=5.9, h=0.85)
    D.footer(s, 2, 9, TOTAL)
    reg(9, 2, "MoE e arquiteturas esparsas", 1.5, 13.5,
        "<b>90 segundos, e o ponto é prático, não teórico.</b> MoE — mistura de especialistas — é uma "
        "arquitetura onde um <b>roteador</b> escolhe, para cada token, apenas <b>k</b> especialistas de um total "
        "de <b>N</b>. Então o modelo tem duas contagens de parâmetros bem diferentes: os <b>totais</b> e os "
        "<b>ativos por token</b>. Exemplo: o DeepSeek-V4-Pro tem 1,6 trilhão total, mas só 49 bilhões ativos. "
        "Aqui está a consequência que a plateia — que hospeda os próprios modelos — precisa ouvir: a sua conta "
        "de <b>VRAM</b> (memória da placa de vídeo) é ditada pelos parâmetros <b>totais</b>, porque todos "
        "precisam estar carregados; já o custo e a velocidade dependem só dos <b>ativos</b>. Traduzindo: um MoE "
        "gigante barateia a resposta <b>na nuvem</b> e <b>não ajuda quem roda em casa</b>. E o contrário também "
        "vale — um modelo <b>denso</b> pequeno pode superar um MoE muito maior; a linha Qwen de 27 bilhões "
        "(densa) fez isso. É a deixa perfeita para o S12. <i>(~1,5 min)</i>")


def s10(prs):
    s = D._blank(prs); D.header(s, 2, "Bloco 2 · LLMs", "Inferência: os parâmetros que importam")
    D.cards(s, 2, [
        ("Temperatura e top-p.", "Controlam se a amostragem é mais criativa ou mais determinística."),
        ("Cache de chaves-valores (KV cache) e cache de prefixo.", "Reaproveitam contas já feitas — menos custo, menos espera."),
        ("Quantização.", "Reduz a precisão dos pesos (ex.: 4 bits) para caber em menos memória de vídeo."),
        ("Decodificação especulativa.", "Um modelo pequeno adianta tokens; o grande confere."),
    ], x=0.6, y=2.05, w=6.05, size=15.5)
    D.code_block(s, "# a MESMA chamada, dois resultados\n\nresp = modelo.gerar(prompt,\n        temperatura=0.0)\n# código / extração: baixa\n\nresp = modelo.gerar(prompt,\n        temperatura=1.0)\n# exploração: alta",
                 x=6.95, y=2.05, w=D.SW-7.55, size=13.5)
    D.callout(s, 2, [("Regra prática: ", {"size": 16, "bold": True, "color": D.FAM['sky'][0]}),
                     ("código e extração estruturada pedem temperatura baixa; exploração de hipóteses pede o contrário — gancho para o S62.",
                      {"size": 16, "color": D.INK})], y=5.85, h=0.9)
    D.footer(s, 2, 10, TOTAL)
    reg(10, 2, "Inferência: os parâmetros que importam", 1.5, 15.0,
        "<b>90 segundos sobre os botões que vocês realmente vão girar.</b> A <b>temperatura</b> (e o top-p) "
        "controla se a amostragem é mais criativa ou mais determinística. Mostre o trecho de código: a mesma "
        "chamada com temperatura 0 e com temperatura 1 dá resultados diferentes — e a <b>regra prática</b> é o "
        "que importa: para <b>gerar código e extrair dados estruturados</b> use temperatura baixa (você quer "
        "previsibilidade); para <b>explorar hipóteses</b>, alta. O <b>cache de chaves-valores</b> e o cache de "
        "prefixo reaproveitam contas e cortam custo e espera. A <b>quantização</b> reduz a precisão dos pesos "
        "para caber em menos memória — é o que permite rodar um modelo de 27 bilhões em 24 GB. Feche com o "
        "gancho: essa escolha de temperatura volta no S62, porque o AI Co-Scientist usa temperatura alta para "
        "gerar hipóteses e baixa para avaliá-las. <i>(~1,5 min)</i>")


def s11(prs):
    s = D._blank(prs); D.header(s, 2, "Bloco 2 · LLMs", "Panorama: modelos proprietários")
    rows = [
        ["*GPT-5.6 Sol", "OpenAI", "*~96%", "Vals AI (independente)"],
        ["*Claude Fable 5", "Anthropic", "*~95%", "medição independente"],
        ["*Gemini 3.1 Pro", "Google", "agrupamento superior", "—"],
    ]
    D.table(s, 2, ["Modelo", "Fabricante", "SWE-bench Verified", "Fonte da medição"], rows,
            x=0.6, y=2.15, w=D.SW-1.2, fsize=16, header_fs=13.5, h=2.4)
    D.callout(s, 2, [("Ressalva obrigatória: ", {"size": 17, "bold": True, "color": D.WARN}),
                     ("o número do fabricante e o de uma medição independente divergem, às vezes muito. Cite sempre a fonte.",
                      {"size": 17, "color": D.INK})], y=5.05, h=1.0, kind="warn")
    D._txt(s, 0.6, 6.25, D.SW-1.2, 0.5,
           [[("SWE-bench Verified = teste de correção de bugs reais de software (%% de tarefas resolvidas).   ", {"size": 12.5, "italic": True, "color": D.MUTED}),
             ("Última verificação: __ / __ / ____", {"size": 12.5, "bold": True, "color": D.MUTED})]])
    D.footer(s, 2, 11, TOTAL)
    reg(11, 2, "Panorama: modelos proprietários", 1.0, 16.0,
        "<b>Um minuto, e cuidado: este slide envelhece em semanas.</b> Mostre a fronteira dos modelos fechados "
        "em <b>SWE-bench Verified</b> — um teste que mede resolução de bugs reais de software, então é o mais "
        "relevante para dev. Os números de meados de 2026 põem GPT-5.6, Claude Fable 5 e Gemini 3.1 no topo. Mas "
        "faça a <b>ressalva obrigatória em voz alta</b>: o número que o fabricante publica e o número que uma "
        "medição independente (como a Vals AI) encontra <b>divergem</b>, às vezes muito — então sempre diga a "
        "fonte. Aponte o rodapé 'última verificação': reconfira estes valores na semana da palestra; dado errado "
        "na frente de gente sênior custa credibilidade. <i>(~1 min)</i>")


def s12(prs):
    s = D._blank(prs); D.header(s, 2, "Bloco 2 · LLMs", "Panorama: modelos abertos para código")
    rows = [
        ["Kimi K3", "2,8T / 104B ativos", "1M", "pesos abertos", "infra séria"],
        ["*DeepSeek-V4-Pro", "1,6T / 49B ativos", "1M", "*MIT", "cluster"],
        ["DeepSeek-V4-Flash", "284B / 13B ativos", "1M", "*MIT", "servidor médio"],
        ["GLM-5.2", "MoE", "longo", "*MIT", "servidor"],
        ["*Qwen3.8-27B", "denso 27,8B · multimodal", "262K→1M", "*Apache-2.0", "*24 GB VRAM"],
        ["Qwen3.6-27B", "denso 27B", "longo", "*Apache-2.0", "1 GPU consumo"],
        ["Muse Glimmer 30B", "denso · multimodal", "131K", "*Apache-2.0", "24 GB quantiz."],
        ["MiniMax M3", "428B / 23B ativos", "1M", "comunitária ⚠", "ver licença"],
    ]
    D.table(s, 2, ["Modelo", "Arquitetura", "Contexto", "Licença", "Onde roda"], rows,
            x=0.6, y=1.95, w=D.SW-1.2, fsize=12.5, header_fs=12, h=3.5)
    b, t = D.panel(s, 0.6, 5.6, D.SW-1.2, 1.15, block=2)
    D._txt(s, 0.95, 5.68, D.SW-1.6, 1.0, [
        [("O caso que importa para vocês:  ", {"size": 15, "bold": True, "color": D.FAM['sky'][0]}),
         ("Qwen3.8-27B — denso, multimodal, Apache-2.0, roda em 24 GB e, em SWE-bench Pro, supera o Claude Opus 4.6 Max.",
          {"size": 15, "color": D.INK})],
        [("Alerta jurídico:  ", {"size": 13.5, "bold": True, "color": D.WARN}),
         ("“pesos abertos” ≠ “código aberto”. MIT e Apache-2.0 são livres; a licença do MiniMax é não comercial por padrão.   ·   Última verificação: __/__/____",
          {"size": 13, "color": D.INK})],
    ], anchor=MSO_ANCHOR.MIDDLE, space_after=7)
    D.footer(s, 2, 12, TOTAL)
    reg(12, 2, "Panorama: modelos abertos para código", 2.5, 18.5,
        "<b>É o slide que a plateia mais vai fotografar — dê tempo (2,5 min) e estrutura.</b> Primeiro leia a "
        "tabela em diagonal: modelos gigantes de nuvem no topo (Kimi K3, DeepSeek-V4-Pro), e desça até a linha "
        "que interessa a quem hospeda: <b>Qwen3.8-27B</b>. Agora o 'slide dentro do slide': este modelo, denso "
        "de 27 bilhões, multimodal, licença Apache-2.0 (livre até para uso comercial), <b>roda em 24 GB de "
        "memória de vídeo</b> — uma placa de estação. Contra a geração anterior, ele deu saltos de dois dígitos "
        "em tarefas de agente <b>sem aumentar de tamanho</b>. E o número que cala a sala: em <b>SWE-bench "
        "Pro</b> ele supera o Claude Opus 4.6 Max. Mas seja honesto — <i>'a fronteira não caiu, ficou "
        "irregular'</i>: ele ainda perde em outros testes. Duas ressalvas ditas de propósito: (1) esses números "
        "são do cartão do modelo, do fabricante — mas por ser aberto, qualquer um repete, o que é argumento <b>a "
        "favor</b>; (2) os pesos são o piso, não o total — o cache de chaves-valores vem por cima e pode dobrar "
        "a memória com contexto longo. E o <b>alerta jurídico</b>, para uma empresa que vende software: 'pesos "
        "abertos' não é 'código aberto'; MIT e Apache são livres, mas a licença do MiniMax é não comercial por "
        "padrão — decisão jurídica, não técnica. <i>(~2,5 min)</i>")


def s13(prs):
    s = D._blank(prs); D.header(s, 2, "Bloco 2 · LLMs", "Contexto longo: o número anunciado é o menos útil")
    D.cards(s, 2, [
        ("Anúncios de 1 a 10 milhões de tokens.",
         "Vários modelos anunciam janelas gigantes — sem um teste publicado que sustente qualidade perto disso."),
        ("Degradação do contexto (“context rot”).",
         "A capacidade efetiva fica em 60–70% do anunciado; e a queda não é gradual — segura até um limiar e despenca. Uma janela de 1M pode degradar já em 50 mil.", "warn"),
        ("Resultado contraintuitivo (testes da Chroma).",
         "Os modelos foram melhores com texto embaralhado do que coerente: texto coerente cria viés de recência — sobrepesa o fim e esquece o começo."),
        ("Custo.",
         "Encher 1 milhão de tokens vai de centavos a dezenas de dólares — diferença de dezenas de vezes entre modelos."),
    ], x=0.6, y=2.05, size=15.5)
    D.callout(s, 2, [("Contexto menor e curado supera contexto grande e velho. ", {"size": 15.5, "bold": True, "color": D.FAM['sky'][0]}),
                     ("Pior em domínio regulado: quando a janela estoura, o modelo corta em silêncio — sem registro do que se perdeu.",
                      {"size": 15, "color": D.INK})], y=6.55, h=0.7, kind="warn")
    D.footer(s, 2, 13, TOTAL)
    reg(13, 2, "Contexto longo: o número anunciado é o menos útil", 2.0, 20.5,
        "<b>Dois minutos que fecham o bloco de LLMs e derrubam um mito de marketing.</b> Todo fabricante anuncia "
        "janelas gigantes — 1 milhão, 10 milhões de tokens. Diga a verdade incômoda: esse número é o <b>menos "
        "útil</b> da ficha técnica. Existe um fenômeno medido, a <b>degradação do contexto</b> (context rot): a "
        "capacidade <b>efetiva</b> costuma ser 60 a 70% do anunciado, e pior, a queda não é suave — o modelo "
        "segura a qualidade até um limiar e então <b>despenca</b>; uma janela de 1 milhão pode começar a "
        "degradar já em 50 mil. Conte o resultado contraintuitivo dos testes da Chroma: os modelos foram "
        "<b>melhores com o texto embaralhado do que coerente</b>, porque texto coerente cria um viés de "
        "recência — o modelo dá peso demais ao final e esquece o começo. Toque no custo: encher 1 milhão de "
        "tokens custa de centavos a dezenas de dólares dependendo do modelo. Feche com a frase-tese do bloco: "
        "<i>'contexto menor e curado supera contexto grande e velho'</i>. E o agravante para software de saúde, "
        "que volta no S51: quando a janela estoura, o modelo <b>corta em silêncio</b> — não fica registro do que "
        "foi perdido, e num sistema auditável isso é inaceitável. <i>(~2 min)</i>")


# ===================== BLOCO 3 — o que mudou p/ quem escreve software =====================
def s14(prs):
    s = D._blank(prs); D.header(s, 3, "Bloco 3 · Software", "A escada de abstração")
    D.cards(s, 3, [
        ("Assembly → linguagem de alto nível.", "Objeção da época: “vai gerar código lento e sem controle”. Consolidou-se com o COMPILADOR."),
        ("Alto nível → frameworks.", "Objeção: “esconde o que importa, vira mágica”. Consolidou-se com o VERIFICADOR DE TIPOS e os TESTES."),
        ("Frameworks → especificação + verificação.", "É o degrau de agora. A mesma objeção — “não dá para confiar” — e a mesma resposta: uma verificação nova."),
        ("O padrão nunca muda.", "Cada degrau sobe o nível do que você escreve — e só se firma quando ganha a sua camada de verificação automática.", "good"),
    ], x=0.6, y=2.05, size=16.5)
    D.footer(s, 3, 14, TOTAL)
    reg(14, 3, "A escada de abstração", 1.0, 21.5,
        "<b>Um minuto para desarmar o ceticismo com história.</b> Toda subida de abstração enfrentou a mesma "
        "objeção e venceu do mesmo jeito. Do assembly para a linguagem de alto nível, diziam 'vai gerar código "
        "ruim' — e o <b>compilador</b> resolveu. Da linguagem para os frameworks, diziam 'esconde o que importa' "
        "— e o <b>verificador de tipos e os testes</b> resolveram. Agora estamos no degrau seguinte: dos "
        "frameworks para <b>especificar e verificar</b>. A objeção é idêntica ('não dá para confiar em código de "
        "IA') e a resposta será idêntica: uma nova camada de verificação — que é exatamente o que o Bloco 9 vai "
        "mostrar. Diga a frase: 'cada degrau só se firmou quando ganhou a sua verificação'. <i>(~1 min)</i>")


def s15(prs):
    s = D._blank(prs); D.header(s, 3, "Bloco 3 · Software", "O que a IA faz bem e mal em código")
    colw = (D.SW-1.2-0.4)/2
    D._rect(s, 0.6, 2.05, colw, 3.4, fill=D.FAM['emerald'][2], rounded=True, radius=0.06)
    D._rect(s, 0.6, 2.05, 0.12, 3.4, fill=D.FAM['emerald'][0])
    D._txt(s, 0.9, 2.18, colw-0.5, 0.5, [[("FAZ BEM", {"size": 15, "bold": True, "color": D.FAM['emerald'][0]})]])
    D.bullets(s, [
        (0, [("código de fronteira ", "n"), ("bem especificado", "b")]),
        (0, [("traduzir entre representações", "n")]),
        (0, [("gerar ", "n"), ("testes a partir de critérios explícitos", "b")]),
        (0, [("refatoração mecânica", "n")]),
    ], x=0.9, y=2.8, w=colw-0.6, size=15.5, block=4)
    x2 = 0.6+colw+0.4
    D._rect(s, x2, 2.05, colw, 3.4, fill=D.FAM['rose'][2], rounded=True, radius=0.06)
    D._rect(s, x2, 2.05, 0.12, 3.4, fill=D.FAM['rose'][0])
    D._txt(s, x2+0.3, 2.18, colw-0.5, 0.5, [[("FAZ MAL", {"size": 15, "bold": True, "color": D.FAM['rose'][0]})]])
    D.bullets(s, [
        (0, [("decisão arquitetural com ", "n"), ("trade-off implícito", "b")]),
        (0, [("corretude que depende de ", "n"), ("contexto não escrito", "b")]),
        (0, [("invariantes ", "n"), ("não declarados", "b")]),
        (0, [("regras que “todo mundo sabe” e ninguém anotou", "n")]),
    ], x=x2+0.3, y=2.8, w=colw-0.6, size=15.5, block=6)
    D.callout(s, 3, [("A coluna da direita é toda ela ", {"size": 17, "color": D.INK}),
                     ("falta de especificação", {"size": 17, "bold": True, "color": D.FAM['rose'][0]}),
                     (".   Custo típico: 50 mil a 500 mil tokens por tarefa; o português gasta ~1,5× mais tokens que o inglês.",
                      {"size": 15, "color": D.INK})], y=5.65, h=1.0)
    D.footer(s, 3, 15, TOTAL)
    reg(15, 3, "O que a IA faz bem e mal, e quanto custa", 1.0, 22.5,
        "<b>Um minuto, e o fecho é o gancho da palestra inteira.</b> A IA é ótima no que está <b>bem "
        "especificado</b>: gerar código de um problema bem descrito, traduzir entre representações, escrever "
        "testes a partir de critérios explícitos, refatorar. E é ruim exatamente onde <b>falta especificação</b>: "
        "decisões de arquitetura com compromissos implícitos, corretude que depende de contexto que ninguém "
        "escreveu, invariantes não declarados. Aponte a coluna da direita e diga a frase: <i>'isto tudo é falta "
        "de especificação'</i> — plantando o Bloco 9. Feche com o custo, para eles terem noção de escala: uma "
        "tarefa de agente gasta de 50 mil a 500 mil tokens, e o português consome cerca de 1,5 vez mais tokens "
        "que o inglês — importa na conta. <i>(~1 min)</i>")


# ===================== BLOCO 4 — Contexto e RAG =====================
def s16(prs):
    s = D._blank(prs); D.header(s, 4, "Bloco 4 · Contexto e RAG", "De “prompt” para “engenharia de contexto”")
    D.callout(s, 4, [("O trabalho não é mais escrever uma frase esperta. É ", {"size": 18, "color": D.INK}),
                     ("decidir o que ocupa a janela", {"size": 18, "bold": True, "color": D.FAM['emerald'][0]}),
                     (" — o espaço de atenção é finito e caro (lembre do O(n²) e do S13).", {"size": 18, "color": D.INK})],
              y=2.05, h=1.15)
    segs = [("instruções", 2.1, D.FAM['indigo']), ("ferramentas", 1.9, D.FAM['sky']),
            ("histórico", 3.2, D.FAM['violet']), ("documentos (RAG)", 3.4, D.FAM['emerald']),
            ("saída", 1.5, D.FAM['amber'])]
    total = sum(seg[1] for seg in segs); x = 0.6; y = 4.0; W = D.SW-1.2; H = 1.15
    for name, wv, col in segs:
        ww = W*wv/total
        D._rect(s, x, y, ww-0.05, H, fill=col[2], rounded=True, radius=0.08)
        D._rect(s, x, y, ww-0.05, 0.12, fill=col[0])
        D._txt(s, x, y+0.1, ww-0.1, H-0.15, [[(name, {"size": 13.5, "bold": True, "color": col[0]})]],
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        x += ww
    D._txt(s, 0.6, 5.35, W, 0.4, [[("A “janela de contexto”: um orçamento fixo a ser gasto com disciplina.",
           {"size": 14, "italic": True, "color": D.MUTED})]], align=PP_ALIGN.CENTER)
    D.footer(s, 4, 16, TOTAL)
    reg(16, 4, "De prompt para contexto", 0.5, 23.0,
        "<b>30 segundos para reposicionar o trabalho.</b> Com o S13 fresco na cabeça, diga: o ofício deixou de "
        "ser 'achar o prompt mágico' e virou <b>engenharia de contexto</b> — decidir, com disciplina, o que "
        "entra na janela. Mostre a barra: a janela é um <b>orçamento fixo</b> dividido entre instruções, "
        "ferramentas, histórico, documentos recuperados (o RAG) e o espaço da saída. Cada token gasto num lugar "
        "é um token a menos em outro — e, pelo O(n²), cada token custa. <i>(~30 s)</i>")


def s17(prs):
    s = D._blank(prs); D.header(s, 4, "Bloco 4 · Contexto e RAG", "RAG: como funciona, e onde quebra")
    D.image_center(s, os.path.join("diagrams", "s17_rag.png"), x=0.5, y=1.95, w=D.SW-1.0, h=D.SH-2.45, block=4)
    D.footer(s, 4, 17, TOTAL)
    reg(17, 4, "RAG: o diagrama", 2.5, 25.5,
        "<b>Dois minutos e meio no diagrama — é o slide técnico central do bloco.</b> RAG significa geração "
        "aumentada por recuperação (Retrieval-Augmented Generation): em vez de o modelo 'saber' tudo, você "
        "<b>busca os trechos certos e os entrega no contexto</b>. São dois trilhos. O de cima, a <b>ingestão</b>, "
        "roda uma vez: o documento é fatiado em pedaços (chunking), cada pedaço vira um vetor (embedding) e vai "
        "para um índice. O de baixo, a <b>consulta</b>, roda a cada pergunta: reescreve a pergunta, faz busca "
        "híbrida (por palavra e por significado), <b>reordena</b> os resultados (reranking), monta o contexto e "
        "gera a resposta com citação da fonte. Agora aponte os três pontos em vermelho — é onde o RAG morre: "
        "<b>fatiar mal, recuperar o trecho errado, e não reordenar</b>. E diga a frase que a plateia vai "
        "reconhecer da própria dor: <i>'RAG raramente falha na geração; ele falha na recuperação, e o time gasta "
        "semanas ajustando o prompt achando que o problema é outro'</i>. <i>(~2,5 min)</i>")


def s18(prs):
    s = D._blank(prs); D.header(s, 4, "Bloco 4 · Contexto e RAG", "Por que fatiar mal destrói um critério de IRAS")
    D.cards(s, 4, [
        ("O critério de definição de caso (ICSAC) ocupa três parágrafos.", "Critério clínico + critério laboratorial + janela temporal — os três precisam ser lidos JUNTOS."),
        ("Em pedaços de 512 tokens, o laboratorial se separa da janela.", "A recuperação devolve metade da regra; o modelo completa o resto sozinho — e notifica um FALSO POSITIVO.", "warn"),
        ("A correção: fatiar pela unidade lógica, não por tamanho fixo.", "Chunking semântico pela regra inteira + metadados por tipo de infecção + expansão de janela ao redor do trecho.", "good"),
    ], x=0.6, y=2.05, size=16.5)
    D.footer(s, 4, 18, TOTAL)
    reg(18, 4, "Chunking ingênuo destrói um critério de IRAS", 1.5, 27.0,
        "<b>90 segundos com um exemplo do domínio deles — é o que faz o conceito grudar.</b> Pegue um critério "
        "de definição de caso da vigilância — a sigla ICSAC, os critérios que definem quando uma infecção conta "
        "como caso. O enunciado tem três parágrafos: o <b>critério clínico</b>, o <b>critério laboratorial</b> e "
        "a <b>janela temporal</b>. Os três só fazem sentido lidos juntos. Se você fatia o documento em pedaços "
        "de 512 tokens — o padrão preguiçoso — o critério laboratorial se separa da janela temporal. A busca "
        "devolve metade da regra, o modelo 'completa' o resto por conta própria, e o resultado é uma "
        "<b>notificação falsa</b> — num sistema de vigilância, um custo real. A correção é fatiar pela "
        "<b>unidade lógica</b> (a regra inteira num pedaço só), pôr metadados por tipo de infecção e expandir a "
        "janela ao redor do trecho recuperado. <i>(~1,5 min)</i>")


def s19(prs):
    s = D._blank(prs); D.header(s, 4, "Bloco 4 · Contexto e RAG", "Saída estruturada como contrato")
    D.code_block(s, '{\n  "criterio": "ICSAC-corrente-sanguinea",\n  "atendido": true,\n  "evidencia_textual":\n     "hemocultura + para S. aureus em 12/03",\n  "data_referencia": "2026-03-12",\n  "confianca": 0.91\n}',
                 x=0.6, y=2.1, w=6.1, size=13.5)
    D.cards(s, 4, [
        ("Um esquema (schema) por critério.", "Booleano do resultado, o trecho literal que o justifica, a data de referência e a confiança."),
        ("Todo booleano vem com a evidência citada.", "Sem o trecho literal não há revisão humana viável nem trilha de auditoria.", "good"),
        ("Não peça parecer. Peça formulário preenchido.", "“Formulário com evidência citada”, não “texto livre opinando”.", "warn"),
    ], x=6.95, y=2.1, w=D.SW-7.55, size=15.5)
    D.footer(s, 4, 19, TOTAL)
    reg(19, 4, "Saída estruturada como contrato", 2.0, 29.0,
        "<b>Dois minutos — e é uma das ideias mais acionáveis da palestra.</b> Mostre o esquema (schema) na "
        "esquerda: para cada critério de IRAS extraído do texto livre, o modelo devolve quatro campos — se o "
        "critério foi <b>atendido</b> (booleano), o <b>trecho literal</b> do prontuário que justifica, a "
        "<b>data de referência</b> e um grau de <b>confiança</b>. O ponto central: <b>todo booleano vem "
        "acompanhado da evidência textual que o sustenta</b>. Sem isso, não existe revisão humana viável — o "
        "infectologista não tem como conferir — nem trilha de auditoria. Diga a frase que resume tudo: <i>'não "
        "peçam um parecer ao modelo; peçam um formulário preenchido, com a evidência citada'</i>. Isso "
        "transforma uma saída opaca num contrato verificável. <i>(~2 min)</i>")


def s20(prs):
    s = D._blank(prs); D.header(s, 4, "Bloco 4 · Contexto e RAG", "Avaliação e proteções (guardrails)")
    rows = [
        ["Estratificação", "sensibilidade e especificidade POR tipo de infecção", "o custo do erro muda por infecção"],
        ["Conjunto dourado", "casos revisados por infectologista, versionado", "verdade de referência estável"],
        ["Gatilho de CI", "roda a cada mudança de prompt, MODELO ou base", "trocar versão = mudança controlada"],
        ["Asserção", "um teste com assert sobre o conjunto dourado", "o portão é código, não opinião"],
    ]
    D.table(s, 4, ["Eixo", "O que medir", "Por quê"], rows, x=0.6, y=2.05, w=D.SW-1.2, fsize=13.5, header_fs=13, h=2.9)
    D.callout(s, 4, [("Acurácia agregada é inútil aqui: ", {"size": 15.5, "bold": True, "color": D.FAM['emerald'][0]}),
                     ("falso negativo e falso positivo têm custos assimétricos e diferentes por infecção. Guardrails: menor privilégio, anonimizar antes de sair, e cuidado com injeção vinda do próprio prontuário (LGPD).",
                      {"size": 14.5, "color": D.INK})], y=5.2, h=1.15)
    D.footer(s, 4, 20, TOTAL)
    reg(20, 4, "Avaliação e guardrails", 1.5, 30.5,
        "<b>90 segundos — e este slide é a recomendação nº 1 do fechamento, então dê peso.</b> A primeira coisa: "
        "acurácia agregada é <b>inútil</b> em IRAS, porque um falso negativo (deixar passar uma infecção) e um "
        "falso positivo (notificar à toa) têm custos <b>assimétricos</b> e diferentes por tipo de infecção. "
        "Então meça pela matriz: <b>sensibilidade e especificidade estratificadas</b> por infecção; um "
        "<b>conjunto dourado</b> de casos revisados por infectologista, versionado; um <b>gatilho de integração "
        "contínua</b> que roda esse conjunto a cada mudança de prompt, de modelo ou de base; e uma "
        "<b>asserção</b> — um teste com <i>assert</i> — para que o portão seja código e não opinião. Feche com a "
        "frase forte: <i>'trocar a versão do modelo sem esse conjunto rodando é mudança não controlada em "
        "software de saúde'</i>. E cite as proteções: menor privilégio, anonimizar antes de qualquer chamada "
        "externa, e o risco de injeção de comandos vinda do próprio texto do prontuário — tudo sob a LGPD. "
        "<i>(~1,5 min)</i>")


# ===================== BLOCO 5 — Agentes =====================
def s21(prs):
    s = D._blank(prs); D.header(s, 5, "Bloco 5 · Agentes", "Definição operacional (sem misticismo)")
    D.quote(s, 5, [("Um agente é um modelo em laço, com ferramentas, sobre um ambiente, com critério de parada.",
                    {"size": 21, "bold": True, "color": D.FAM['amber'][0]})], y=2.05, h=1.25)
    D.cards(s, 5, [
        ("O que NÃO é agente:", "fluxo de caminho fixo com o modelo nos nós. Isso é um workflow — e quase sempre é a escolha certa."),
    ], x=0.6, y=3.55, size=16.5, ch=0.95)
    lv = [("determinístico", D.FAM['emerald']), ("roteado por modelo", D.FAM['teal']),
          ("agente com ferramentas", D.FAM['amber']), ("autônomo", D.FAM['rose'])]
    x = 0.6; y = 4.9; W = D.SW-1.2; ww = (W-0.3)/4
    for i, (name, col) in enumerate(lv):
        D._rect(s, x, y, ww-0.1, 0.75, fill=col[2], rounded=True, radius=0.1)
        D._rect(s, x, y, ww-0.1, 0.1, fill=col[0])
        D._txt(s, x, y+0.08, ww-0.1, 0.6, [[(name, {"size": 12.5, "bold": True, "color": col[0]})]],
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        if i < 3:
            D._txt(s, x+ww-0.28, y+0.1, 0.4, 0.5, [[("→", {"size": 18, "bold": True, "color": D.MUTED})]])
        x += ww
    D.callout(s, 5, [("Eixo da autonomia: ", {"size": 15.5, "bold": True, "color": D.FAM['amber'][0]}),
                     ("da esquerda para a direita, mais poder e mais risco. Autonomia é custo, não virtude — escolha o mínimo que resolve.",
                      {"size": 15, "color": D.INK})], y=5.85, h=0.85)
    D.footer(s, 5, 21, TOTAL)
    reg(21, 5, "Definição operacional", 1.5, 32.0,
        "<b>90 segundos para tirar o misticismo da palavra 'agente'.</b> Leia a definição operacional, devagar: "
        "<b>um modelo em laço, com ferramentas, sobre um ambiente, com critério de parada</b>. Só isso. E diga o "
        "que <b>não</b> é agente: um fluxo de caminho fixo com o modelo em alguns nós — isso é um <i>workflow</i>, "
        "e na maioria dos casos é a escolha <b>certa</b>, mais simples e mais depurável. Mostre o eixo da "
        "autonomia: determinístico, roteado por modelo, agente com ferramentas, autônomo — e martele a frase: "
        "<i>'autonomia é custo e risco, não virtude; use o mínimo que resolve o problema'</i>. Isso prepara o "
        "S28 (por que agentes falham) e o S50 (como os gates domam isso). <i>(~1,5 min)</i>")


def s22b(prs):
    s = D._blank(prs); D.header(s, 5, "Bloco 5 · Agentes", "O laço agêntico")
    D.image_center(s, os.path.join("diagrams", "s22_loop.png"), x=0.6, y=1.95, w=D.SW-1.2, h=D.SH-2.45, block=5)
    D.footer(s, 5, 22, TOTAL)
    reg(22, 5, "O laço agêntico", 2.0, 34.0,
        "<b>Dois minutos no ciclo — é o coração do bloco.</b> Percorra o laço: parte de um <b>objetivo</b>, o "
        "modelo <b>raciocina</b> sobre o que fazer, executa uma <b>ação</b> (chama uma ferramenta), recebe uma "
        "<b>observação</b> do ambiente, e <b>repete</b> até bater o critério de parada — aí devolve a resposta. É "
        "isso, e é só isso. Agora aponte os <b>três pontos de controle</b> — porque é onde você, engenheiro, "
        "realmente atua: <b>quais ferramentas existem</b> (o que o agente pode fazer), <b>o que volta como "
        "observação</b> (o que ele enxerga) e <b>quando o laço para</b> (senão ele roda para sempre ou gasta "
        "dinheiro sem controle). Guarde: quase todo problema de agente em produção é um desses três mal "
        "definidos. <i>(~2 min)</i>")


def s23(prs):
    s = D._blank(prs); D.header(s, 5, "Bloco 5 · Agentes", "“Tool use”: usar ferramentas sem framework nenhum")
    D.code_block(s, '# 1. você DESCREVE a ferramenta (isto é prompt!)\nferramenta = {\n  "nome": "consultar_microbiologia",\n  "parametros": {"paciente_id": "str",\n                 "janela_dias": "int"}\n}\n# 2. o modelo responde pedindo a chamada (tool_use)\n# 3. VOCÊ executa e devolve o resultado (tool_result)\n# 4. repete num while explícito até a resposta',
                 x=0.6, y=2.1, w=6.6, size=12.5)
    D.cards(s, 5, [
        ("O laço agêntico tem trinta linhas.", "Tudo que vem depois — os frameworks do Bloco 7 — é conveniência, não mágica."),
        ("A descrição da ferramenta É prompt.", "Descrição ruim de ferramenta causa mais falha do que prompt de sistema ruim.", "warn"),
    ], x=7.45, y=2.1, w=D.SW-8.05, size=16)
    D.footer(s, 5, 23, TOTAL)
    reg(23, 5, "Tool use sem framework", 3.0, 37.0,
        "<b>Três minutos, e é o slide que dá confiança técnica à plateia sênior.</b> Mostre que 'usar "
        "ferramentas' (tool use) não tem mágica nenhuma. Quatro passos: (1) você <b>descreve</b> a ferramenta "
        "num esquema — nome e parâmetros — por exemplo <i>consultar_microbiologia(paciente_id, janela_dias)</i>; "
        "(2) o modelo, em vez de responder texto, devolve um pedido de chamada (tool_use); (3) <b>você</b> "
        "executa a função de verdade e devolve o resultado (tool_result); (4) isso roda num <i>while</i> "
        "explícito até o modelo dar a resposta final. Diga a frase que desarma o hype: <i>'o laço agêntico tem "
        "trinta linhas; tudo que vem depois é conveniência'</i>. E o insight prático que eles vão usar na "
        "segunda-feira: <b>a descrição da ferramenta é prompt</b> — uma descrição ruim de ferramenta causa mais "
        "falha do que um prompt de sistema ruim. <i>(~3 min)</i>")


def s24(prs):
    s = D._blank(prs); D.header(s, 5, "Bloco 5 · Agentes", "Componentes de um agente")
    D.cards(s, 5, [
        ("Memória curta × longa.", "Curta = a conversa atual; longa = o que persiste entre execuções."),
        ("Planejamento.", "Quebrar o objetivo em passos antes de agir."),
        ("Reflexão.", "Criticar o próprio resultado e tentar de novo."),
        ("Memória longa em arquivo versionado costuma superar a vetorial em regras estáveis.", "É auditável e comparável em diff — gancho direto para o formato OKF do S31.", "good"),
    ], x=0.6, y=2.05, size=16.5)
    D.footer(s, 5, 24, TOTAL)
    reg(24, 5, "Componentes", 0.5, 37.5,
        "<b>30 segundos, rápido.</b> Um agente combina: <b>memória curta</b> (a conversa atual) e <b>longa</b> "
        "(o que persiste entre execuções), <b>planejamento</b> (quebrar em passos) e <b>reflexão</b> (criticar o "
        "próprio trabalho). Deixe um gancho para depois: para <b>regras estáveis</b> — como os critérios de IRAS "
        "— a memória longa em <b>arquivo versionado</b> costuma superar a memória vetorial, porque é auditável e "
        "você vê a diferença num diff. Isso volta no formato OKF, no S31. <i>(~30 s)</i>")


def s25(prs):
    s = D._blank(prs); D.header(s, 5, "Bloco 5 · Agentes", "Os seis padrões de composição")
    D.image_center(s, os.path.join("diagrams", "s25_patterns.png"), x=0.5, y=1.95, w=D.SW-1.0, h=D.SH-2.45, block=5)
    D.footer(s, 5, 25, TOTAL)
    reg(25, 5, "Os seis padrões de composição", 3.0, 40.5,
        "<b>Três minutos — é o catálogo que a plateia vai querer fotografar.</b> São seis maneiras de compor "
        "agentes, da mais simples à mais arriscada: <b>encadeamento</b> (a saída de um vira a entrada do "
        "próximo), <b>roteamento</b> (classifica e manda ao especialista certo), <b>paralelização</b> (secciona "
        "o trabalho, ou faz vários resolverem e <b>vota</b>), <b>orquestrador-trabalhadores</b> (um coordena, "
        "vários executam isolados), <b>avaliador-otimizador</b> (um gera, outro critica e manda refazer) e o "
        "<b>agente autônomo</b> (decide os próprios passos — mais poder, mais risco). Diga a regra de ouro: "
        "<i>'comecem pelo mais simples que resolve'</i>. E destaque os dois <b>mais subutilizados e mais úteis "
        "para reduzir falso positivo aqui</b>: a <b>votação</b> e o <b>avaliador-otimizador</b> — os dois "
        "destacados. Guarde-os: eles reaparecem no AI Co-Scientist, no S62. <i>(~3 min)</i>")


def s26(prs):
    s = D._blank(prs); D.header(s, 5, "Bloco 5 · Agentes", "O mesmo caso resolvido de três formas")
    D.callout(s, 5, [("Caso: ", {"size": 15.5, "bold": True, "color": D.FAM['amber'][0]}),
                     ("agente de vigilância de IRAS — varre microbiologia, prescrição e evolução; aplica os critérios; propõe a notificação; e PARA em revisão humana.",
                      {"size": 15, "color": D.INK})], y=2.0, h=0.9)
    cols = [("Encadeado", D.FAM['emerald'], "passos fixos em sequência; simples, mas rígido"),
            ("Orquestrador-\ntrabalhadores", D.FAM['teal'], "um trabalhador por tipo de infecção, contexto isolado"),
            ("Avaliador-\notimizador", D.FAM['amber'], "um crítico contesta contra o critério normativo: menos falso positivo, ~2× tokens")]
    cw = (D.SW-1.2-0.6)/3; x = 0.6
    for name, col, desc in cols:
        D._rect(s, x, 3.15, cw, 3.2, fill=col[2], rounded=True, radius=0.07)
        D._rect(s, x, 3.15, cw, 0.6, fill=col[0])
        D._txt(s, x+0.15, 3.2, cw-0.3, 0.55, [[(name, {"size": 15, "bold": True, "color": D.WHITE})]],
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        D._txt(s, x+0.25, 3.95, cw-0.5, 2.2, [[(desc, {"size": 14.5, "color": D.INK})]], line_spacing=1.15)
        x += cw + 0.3
    D.footer(s, 5, 26, TOTAL)
    reg(26, 5, "O mesmo caso de três formas", 2.0, 42.5,
        "<b>Dois minutos, e é onde a teoria vira decisão de arquitetura.</b> Fixe um caso concreto: um "
        "<b>agente de vigilância de IRAS</b> que varre microbiologia, prescrição e evolução clínica, aplica os "
        "critérios de caso, propõe a notificação e <b>para em revisão humana</b> (nunca notifica sozinho). Agora "
        "resolva-o de três jeitos. <b>Encadeado</b>: passos fixos em sequência — simples, mas rígido. "
        "<b>Orquestrador-trabalhadores</b>: um trabalhador por tipo de infecção, cada um com contexto isolado — "
        "escala e evita contaminação. <b>Avaliador-otimizador</b>: um agente crítico contesta cada proposta "
        "contra o critério normativo — isso <b>reduz falso positivo</b>, ao custo de cerca do dobro de tokens. A "
        "lição: a arquitetura é uma escolha de compromisso, e você a faz de olho no custo do erro. <i>(~2 min)</i>")


def s27(prs):
    s = D._blank(prs); D.header(s, 5, "Bloco 5 · Agentes", "Multiagente: quando compensa (e quando não)")
    D.cards(s, 5, [
        ("Só compensa com subtarefas paralelizáveis E contextos isolados.", "Se as partes não são independentes, o custo explode sem ganho."),
        ("Em fluxo linear: 4 a 15× mais tokens para reimplementar um “if”.", "Vários agentes conversando para decidir o que um condicional resolveria.", "warn"),
        ("A passagem de contexto entre agentes é “lossy”.", "Cada repasse perde informação — como fotocópia de fotocópia."),
    ], x=0.6, y=2.05, size=16.5)
    D.footer(s, 5, 27, TOTAL)
    reg(27, 5, "Multiagente: quando compensa", 0.5, 43.0,
        "<b>30 segundos de contrapeso, importante.</b> Depois de mostrar o poder do multiagente, segure o "
        "entusiasmo: ele <b>só compensa</b> quando há subtarefas de fato paralelizáveis <b>e</b> contextos que "
        "podem ficar isolados. Num fluxo linear, montar vários agentes custa de 4 a 15 vezes mais tokens para "
        "<b>reimplementar o que um simples 'if' resolveria</b>. E lembre: a passagem de contexto entre agentes é "
        "<i>lossy</i> — perde informação a cada repasse, como fotocópia de fotocópia. A moral: multiagente é "
        "ferramenta cara; use quando o problema pede, não por elegância. <i>(~30 s)</i>")


def s28(prs):
    s = D._blank(prs); D.header(s, 5, "Bloco 5 · Agentes", "Por que agentes falham em produção")
    D.image_center(s, os.path.join("diagrams", "s28_error.png"), x=0.6, y=1.9, w=7.3, h=D.SH-2.35, block=5)
    D.cards(s, 5, [
        ("Erro composto.", "95% de acerto por passo, 20 passos → só 36% de sucesso fim a fim."),
        ("Modos de falha:", "laço infinito, ferramenta alucinada, contexto contaminado, custo imprevisto — e o pior, a FALHA SILENCIOSA.", "warn"),
        ("A saída não é “prompt melhor”.", "É reduzir o número de passos NÃO verificados. Guardem esta frase para o Bloco 9.", "good"),
    ], x=8.0, y=2.05, w=D.SW-8.6, size=15)
    D.footer(s, 5, 28, TOTAL)
    reg(28, 5, "Por que agentes falham em produção", 1.5, 44.5,
        "<b>90 segundos, e este é o slide que arma o núcleo da palestra (o Bloco 9).</b> A causa raiz é "
        "matemática: o <b>erro composto</b>. Mostre a curva — se cada passo acerta 95% das vezes, vinte passos "
        "em sequência dão só <b>36% de sucesso</b> fim a fim, porque as probabilidades se multiplicam. Aponte as "
        "três linhas (90, 95, 99% por passo) para mostrar como a confiabilidade por passo é decisiva. Liste os "
        "modos de falha — laço infinito, ferramenta alucinada, contexto contaminado, custo imprevisto — e "
        "destaque o mais perigoso em software de saúde: a <b>falha silenciosa</b>, quando o agente erra e "
        "ninguém percebe. E então a conclusão que vale a palestra inteira: <i>'confiabilidade não vem de um "
        "prompt melhor; vem de reduzir o número de passos não verificados'</i> — que é exatamente o que os "
        "gates do SDD fazem. <i>(~1,5 min)</i>")


# ===================== BLOCO 6 — Protocolos =====================
def s29(prs):
    s = D._blank(prs); D.header(s, 6, "Bloco 6 · Protocolos", "O mapa: vertical (MCP) × horizontal (A2A)")
    D.image_center(s, os.path.join("diagrams", "s29_protocols.png"), x=0.5, y=1.95, w=D.SW-1.0, h=D.SH-2.45, block=6)
    D.footer(s, 6, 29, TOTAL)
    reg(29, 6, "O mapa: vertical × horizontal", 2.0, 46.5,
        "<b>Dois minutos, e a analogia final é o que fica.</b> Dois protocolos abertos organizam o ecossistema. "
        "O <b>MCP</b> (Protocolo de Contexto de Modelo, da Anthropic) é o eixo <b>vertical</b>: liga o agente às "
        "suas <b>ferramentas</b> — servidores que expõem Tools, Resources e Prompts. O limite dele: é "
        "hub-and-spoke, ou seja, <b>dois servidores MCP não conversam entre si</b>. O <b>A2A</b> "
        "(Agente-para-Agente, do Google) é o eixo <b>horizontal</b>: liga um agente a <b>outros agentes</b>, cada "
        "um publicando um cartão de capacidades (AgentCard) e trocando tarefas com estados bem definidos. Feche "
        "com a analogia que a plateia vai levar: <i>'o MCP é o USB-C das ferramentas; o A2A é o HTTP da "
        "colaboração entre agentes — e em produção você usa os dois'</i>. <i>(~2 min)</i>")


def s30(prs):
    s = D._blank(prs); D.header(s, 6, "Bloco 6 · Protocolos", "A família A2A e as alternativas")
    D.cards(s, 6, [
        ("Extensões oficiais do A2A.", "Secure Passport (identidade), Timestamp, Traceability (rastreabilidade), Agent Gateway."),
        ("A família: AP2, UCP, A2UI.", "Pagamentos iniciados por agente, comércio com consentimento criptográfico, e interface."),
        ("Alternativas: ACP (IBM) e ANP.", "ACP herda a tradição FIPA-ACL com performativas tipadas; ANP aposta em identidade descentralizada."),
        ("A crítica que dá valor ao slide: nenhum protocolo expressa GOVERNANÇA.", "Registram quem chamou quem — não sob qual política nem com que base legal. Em saúde, essa camada sobra para VOCÊS.", "warn"),
    ], x=0.6, y=2.05, size=16)
    D.footer(s, 6, 30, TOTAL)
    reg(30, 6, "A2Family e alternativas", 1.5, 48.0,
        "<b>90 segundos, e o remate é o gancho comercial.</b> Em volta do A2A cresceu uma família: extensões "
        "oficiais (passaporte seguro, carimbo de tempo, rastreabilidade, portão de agentes) e protocolos "
        "irmãos — AP2 para pagamentos iniciados por agente, UCP para comércio com consentimento criptográfico, "
        "A2UI para interface. Há alternativas: o ACP da IBM, que herda a tradição acadêmica FIPA-ACL com "
        "mensagens tipadas (propor, aceitar, recusar), e o ANP, com identidade descentralizada. Mas o ponto que "
        "valoriza o slide é a <b>crítica</b>: pesquisa recente mostra que <b>nenhum desses protocolos expressa "
        "governança</b> — eles registram quem chamou quem, mas não sob qual política nem com que base legal. Em "
        "software de saúde, essa camada de governança <b>sobra para a arquitetura de vocês</b>. Isso volta no "
        "S51 e no S65. <i>(~1,5 min)</i>")


def s31(prs):
    s = D._blank(prs); D.header(s, 6, "Bloco 6 · Protocolos", "OKF: um formato aberto de conhecimento")
    D.cards(s, 6, [
        ("① Um pacote (bundle) é um diretório de arquivos markdown.", "Nada de banco de dados, nada de servidor."),
        ("② Cada arquivo é um conceito; o caminho do arquivo é o identificador.", ""),
        ("③ Cada arquivo abre com frontmatter YAML — único campo obrigatório: type.", ""),
        ("④ Arquivos se referenciam por links markdown comuns.", "O que transforma o diretório num GRAFO, não numa lista."),
        ("⑤ Dois nomes reservados: index.md (listagem) e log.md (histórico).", ""),
    ], x=0.6, y=2.0, w=7.4, size=14.5, gap=0.11)
    b, t = D.panel(s, 8.15, 2.0, D.SW-8.75, D.SH-2.55, block=6)
    D._txt(s, 8.45, 2.2, D.SW-9.3, D.SH-2.9, [
        [("Para vocês, direto:", {"size": 15, "bold": True, "color": D.FAM['rose'][0]})],
        [("um pacote OKF com as definições de caso de IRAS, as fórmulas dos indicadores e os runbooks da CCIH.",
          {"size": 14, "color": D.INK})],
        [("Legível por agente, revisável por infectologista, com log.md de histórico e “git blame” de autoria —",
          {"size": 14, "color": D.INK})],
        [("metade do que uma auditoria já pede.", {"size": 14, "bold": True, "color": D.FAM['rose'][0]})],
        [("Ressalva: é v0.1 — padroniza o contêiner, não a semântica clínica.", {"size": 12.5, "italic": True, "color": D.WARN})],
    ], anchor=MSO_ANCHOR.TOP, space_after=8, line_spacing=1.12)
    D.footer(s, 6, 31, TOTAL)
    reg(31, 6, "OKF: Open Knowledge Format", 2.0, 50.0,
        "<b>Dois minutos num formato simples que resolve um problema real de vocês.</b> Enquanto os protocolos "
        "definem <b>comunicação</b>, o OKF (Formato Aberto de Conhecimento, do Google Cloud) define "
        "<b>conhecimento</b> — e a especificação inteira cabe em cinco regras. Leia as cinco na tela: um pacote é "
        "um diretório de arquivos markdown (sem banco, sem servidor); cada arquivo é um conceito e o caminho é o "
        "identificador; cada arquivo abre com um cabeçalho YAML cujo único campo obrigatório é o <i>type</i>; os "
        "arquivos se referenciam por links markdown, o que faz do diretório um <b>grafo</b>; e há dois nomes "
        "reservados, <i>index.md</i> e <i>log.md</i>. Agora a aplicação direta, e diga com estas palavras: um "
        "pacote OKF com as <b>definições de caso de IRAS</b>, as <b>fórmulas dos indicadores</b> (densidade de "
        "incidência, taxa de uso de dispositivo) e os <b>runbooks da comissão de controle de infecção</b> é "
        "exatamente o conhecimento que hoje vive em PDF, planilha e na cabeça das pessoas. Em OKF ele fica "
        "legível por agente, revisável por infectologista, com histórico em <i>log.md</i> e autoria por "
        "<i>git blame</i> — que é metade do que uma auditoria pede. Ressalva honesta: é versão 0.1, padroniza o "
        "recipiente, não a semântica clínica — se adotarem, vocês definem o vocabulário. <i>(~2 min)</i>")


def s32(prs):
    s = D._blank(prs); D.header(s, 6, "Bloco 6 · Protocolos", "Os outros formatos em markdown")
    D.cards(s, 6, [
        ("AGENTS.md.", "Contexto do projeto para agentes de código: comandos de build e teste, convenções, decisões. Markdown puro."),
        ("DESIGN.md.", "Identidade visual: tokens de design em YAML mais o racional em prosa."),
        ("Agent Skills.", "Capacidade empacotada como uma pasta com um arquivo markdown, com registros públicos."),
        ("O padrão por trás dos três: markdown versionado no repositório.", "A única coisa que humano e máquina leem, que o git versiona e que o revisor audita num diff.", "good"),
    ], x=0.6, y=2.05, size=16)
    D.footer(s, 6, 32, TOTAL)
    reg(32, 6, "Os outros formatos em markdown", 1.0, 51.0,
        "<b>Um minuto para revelar um padrão maior.</b> Além do OKF, três formatos viraram convenção: o "
        "<b>AGENTS.md</b>, que dá ao agente o contexto do projeto (como buildar, como testar, as convenções); o "
        "<b>DESIGN.md</b>, para identidade visual; e as <b>Agent Skills</b>, capacidades empacotadas como pasta "
        "com um markdown. O ponto não são os três — é o <b>padrão por trás deles</b>: o setor convergiu, sem "
        "combinar, para <b>markdown versionado no repositório</b> como o formato de contexto para agente. E não "
        "foi por elegância: é a única coisa que humano e máquina leem, que o git versiona e que o revisor "
        "consegue auditar num diff. Guarde essa frase — ela é a ponte para o SDD. <i>(~1 min)</i>")


def s33(prs):
    s = D._blank(prs); D.header(s, 6, "Bloco 6 · Protocolos", "A ponte para o SDD")
    cols = [("Especificação (SDD)", D.FAM['indigo'], "o QUE o sistema deve fazer"),
            ("AGENTS.md", D.FAM['sky'], "COMO se trabalha no repositório"),
            ("Pacote OKF", D.FAM['rose'], "o DOMÍNIO que ele modela")]
    cw = (D.SW-1.2-0.6)/3; x = 0.6
    for name, col, desc in cols:
        D._rect(s, x, 2.2, cw, 2.4, fill=col[2], rounded=True, radius=0.07)
        D._rect(s, x, 2.2, cw, 0.62, fill=col[0])
        D._txt(s, x+0.15, 2.26, cw-0.3, 0.55, [[(name, {"size": 15.5, "bold": True, "color": D.WHITE})]],
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        D._txt(s, x+0.2, 3.15, cw-0.4, 1.3, [[(desc, {"size": 15, "color": D.INK})]],
               align=PP_ALIGN.CENTER, line_spacing=1.15)
        x += cw + 0.3
    D.callout(s, 6, [("São a MESMA ideia em escopos diferentes: ", {"size": 17, "bold": True, "color": D.FAM['rose'][0]}),
                     ("conhecimento formalizado em markdown versionado, consumido por agente e revisável por humano. Os três convivem no mesmo repositório — e é isso que constrói a rastreabilidade (guardem para o S49).",
                      {"size": 15, "color": D.INK})], y=5.0, h=1.3)
    D.footer(s, 6, 33, TOTAL)
    reg(33, 6, "A ponte para o SDD", 1.0, 52.0,
        "<b>Um minuto que costura o bloco todo e abre o núcleo da palestra.</b> Mostre os três lado a lado e diga "
        "que são a <b>mesma ideia</b> em escopos diferentes: a <b>especificação</b> do SDD descreve <i>o que</i> "
        "o sistema deve fazer; o <b>AGENTS.md</b> descreve <i>como</i> se trabalha no repositório; o <b>pacote "
        "OKF</b> descreve o <i>domínio</i> que ele modela. Os três são conhecimento formalizado em markdown "
        "versionado, consumido por agente e revisável por humano. Termine com a frase que reaparece no S49: "
        "<i>'os três convivem no mesmo repositório, e é isso que constrói a rastreabilidade'</i>. É a deixa "
        "perfeita para o intervalo e para o mergulho no SDD. <i>(~1 min)</i>")


def s_intervalo(prs):
    s = D._blank(prs)
    c1, c2, c3 = D.FAM['rose']
    D._rect(s, 0, 0, D.SW, D.SH, fill=c1)
    D._dot(s, -1.2, -1.2, 3.4, c2); D._dot(s, D.SW-2.0, D.SH-2.2, 4.0, c2)
    D._txt(s, 1.0, 2.7, D.SW-2, 1.2, [[("INTERVALO", {"size": 54, "bold": True, "color": D.WHITE})]],
           align=PP_ALIGN.CENTER)
    D._txt(s, 1.0, 4.1, D.SW-2, 0.8, [[("5 minutos", {"size": 26, "color": D.WHITE})]], align=PP_ALIGN.CENTER)
    D._txt(s, 1.0, 5.1, D.SW-2, 0.8,
           [[("Na volta: frameworks, ambientes agênticos e o núcleo — o SDD.", {"size": 17, "italic": True, "color": D.WHITE})]],
           align=PP_ALIGN.CENTER)
    D.notes(s, "Intervalo de 5 minutos.")
    reg(None, 6, "Intervalo", 5.0, 57.0,
        "<b>Intervalo de 5 minutos.</b> Anuncie o horário exato de retorno em voz alta e escreva no canto do "
        "quadro se possível. Avise que a volta começa pelos frameworks e caminha para o coração da palestra, o "
        "SDD. Use o intervalo para conferir se a demonstração gravada (S61) está pronta para tocar.",
        label="INTERVALO")


# ===================== BLOCO 7 — Frameworks e SDKs =====================
def s34(prs):
    s = D._blank(prs); D.header(s, 7, "Bloco 7 · Frameworks", "Critério de leitura para os cinco")
    D.quote(s, 7, [("A pergunta única para cada framework: ", {"size": 21, "bold": True, "color": D.FAM['indigo'][0]}),
                   ("o que ele controla por mim — o laço, o estado, ou nenhum dos dois?",
                    {"size": 21, "bold": True, "color": D.FAM['sky'][0]})], y=2.1, h=1.5)
    D.cards(s, 7, [
        ("O mesmo agente do S26 aparece nos cinco.", "Para comparar o custo da abstração — não a sintaxe."),
        ("Frameworks não são mágica; são conveniência sobre o laço de 30 linhas do S23.", "A pergunta certa não é “qual é mais bonito”, é “o que ele assume por você e o que ele esconde”.", "good"),
    ], x=0.6, y=4.0, size=16.5)
    D.footer(s, 7, 34, TOTAL)
    reg(34, 7, "Critério de leitura", 0.5, 57.5,
        "<b>30 segundos para dar à plateia uma lente única.</b> Em vez de decorar a interface de programação (a "
        "API) de cada framework, façam a mesma pergunta a todos: <b>o que este framework controla por mim — o "
        "laço, o estado, ou nenhum dos dois?</b> Avise que você vai usar o <b>mesmo agente do S26</b> nos cinco, "
        "de propósito, para comparar o custo da abstração e não a sintaxe. E lembre o S23: no fundo, todos "
        "embrulham o mesmo laço de trinta linhas — a pergunta é o que cada um assume por você e o que esconde. "
        "<i>(~30 s)</i>")


def s35(prs):
    s = D._blank(prs); D.header(s, 7, "Bloco 7 · Frameworks", "OpenAI Agents SDK")
    D.cards(s, 7, [
        ("Peças: Agent, handoffs, guardrails, sessions.", "Repasse entre agentes (handoff), proteções e sessões, com rastreamento embutido."),
        ("Modelo de controle: o SDK controla o laço; o estado vive na sessão.", ""),
        ("Rastreamento (tracing) de primeira linha — porém acoplado ao provedor.", "Ótima observabilidade, ao custo de amarrar você à OpenAI.", "warn"),
    ], x=0.6, y=2.05, w=6.5, size=16)
    D.code_block(s, "# triagem -> especialista por infecção\ntriagem = Agent(\n  name=\"triagem\",\n  handoffs=[uti_agent,\n           cirurgia_agent])\n# o SDK cuida do laço e do repasse",
                 x=7.25, y=2.05, w=D.SW-7.85, size=13)
    D.footer(s, 7, 35, TOTAL)
    reg(35, 7, "OpenAI Agents SDK", 2.0, 59.5,
        "<b>Dois minutos.</b> O SDK de Agentes da OpenAI dá quatro peças: <b>Agent</b>, <b>handoffs</b> (o "
        "repasse de uma conversa para um agente especialista), <b>guardrails</b> (proteções) e <b>sessions</b> "
        "(sessões), com rastreamento embutido. Mostre o trecho: uma triagem que faz <i>handoff</i> para o "
        "especialista por tipo de infecção. O modelo de controle: <b>o SDK controla o laço; o estado vive na "
        "sessão</b>. O rastreamento é excelente — mas <b>acoplado ao provedor</b>, então é ótima observabilidade "
        "ao custo de amarrar você à OpenAI. Boa porta de entrada; pense na dependência. <i>(~2 min)</i>")


def s36(prs):
    s = D._blank(prs); D.header(s, 7, "Bloco 7 · Frameworks", "Anthropic Claude Agent SDK")
    D.cards(s, 7, [
        ("O laço do Claude Code exposto como biblioteca.", "Busca agêntica no sistema de arquivos SEM indexação prévia, subagentes com contexto isolado, hooks."),
        ("Sistema de permissões + MCP nativo + modo headless.", "Controle fino do que o agente pode fazer, e execução sem interface para rodar em CI."),
        ("Diferencial: projetado em torno de CÓDIGO e ARQUIVOS, não de conversa.", "É o mais relevante para o Bloco 9 (o SDD roda sobre arquivos versionados).", "good"),
    ], x=0.6, y=2.05, size=16.5)
    D.footer(s, 7, 36, TOTAL)
    reg(36, 7, "Anthropic Claude Agent SDK", 2.0, 61.5,
        "<b>Dois minutos.</b> O SDK de Agente da Anthropic é o próprio laço do Claude Code exposto como "
        "biblioteca: <b>busca agêntica no sistema de arquivos sem indexação prévia</b> (ele explora o "
        "repositório na hora), <b>subagentes</b> com contexto isolado, <b>hooks</b> (ganchos para rodar "
        "verificações dentro do laço), um <b>sistema de permissões</b>, suporte nativo ao MCP e um <b>modo "
        "headless</b> para rodar em integração contínua. O diferencial, e é o que importa para o Bloco 9: ele é "
        "projetado em torno de <b>código e arquivos</b>, não de conversa — que é exatamente o terreno do SDD. "
        "<i>(~2 min)</i>")


def s37(prs):
    s = D._blank(prs); D.header(s, 7, "Bloco 7 · Frameworks", "LangChain e LangGraph")
    D.image_center(s, os.path.join("diagrams", "s37_langgraph.png"), x=0.6, y=1.95, w=7.4, h=D.SH-2.5, block=7)
    D.cards(s, 7, [
        ("LangChain compõe componentes; LangGraph é máquina de estados.", ""),
        ("Estado durável (checkpointer) + parada para aprovação (interrupt).", "Nativos — e decisivos aqui."),
        ("Para IRAS: a notificação NÃO sai sem aprovação, e o processo sobrevive a reinício.", "", "good"),
    ], x=8.15, y=2.05, w=D.SW-8.75, size=15)
    D.footer(s, 7, 37, TOTAL)
    reg(37, 7, "LangChain e LangGraph", 2.0, 63.5,
        "<b>Dois minutos, e é o framework que mais importa para software regulado.</b> Separe as duas coisas: o "
        "<b>LangChain</b> é uma biblioteca para compor componentes; o <b>LangGraph</b> é uma <b>máquina de "
        "estados</b>. Mostre o grafo: nós (coletar evidência, avaliar critério), <b>arestas condicionais</b> "
        "(conforme? sim/não), um <b>checkpointer</b> que torna o estado <b>durável</b> — sobrevive a reinício — "
        "e uma <b>interrupção</b> para <b>aprovação humana</b> antes de agir. Diga por que isso é decisivo em "
        "IRAS: a <b>notificação não sai sem a aprovação</b> do infectologista, e o processo precisa <b>sobreviver "
        "a um reinício</b> do servidor sem perder onde estava. Durabilidade e humano-no-laço nativos: é o "
        "argumento que vende o LangGraph para produção regulada. <i>(~2 min)</i>")


def s38(prs):
    s = D._blank(prs); D.header(s, 7, "Bloco 7 · Frameworks", "CrewAI")
    D.cards(s, 7, [
        ("Modelo mental: organização, não grafo.", "Agent com papel, objetivo e história; Task com saída esperada; Crew reunindo; Process sequencial ou hierárquico."),
        ("Onde brilha: protótipo e demonstração.", "A menor curva de entrada; decompor por papel força o time a escrever o que cada agente faz — meio caminho para uma spec."),
        ("Onde dói: a metáfora de papéis ESCONDE o laço.", "Quando falha, você depura uma abstração, não uma sequência de chamadas. Estado e durabilidade fracos vs. LangGraph.", "warn"),
        ("Veredito: ótimo para levantar um piloto numa tarde.", "Pense duas vezes antes de pôr em produção regulada. (É o framework do nosso LangNet — Bloco 11.)", "good"),
    ], x=0.6, y=2.05, size=15.5)
    D.footer(s, 7, 38, TOTAL)
    reg(38, 7, "CrewAI", 2.0, 65.5,
        "<b>Dois minutos, com honestidade — é o framework que o nosso LangNet usa.</b> O modelo mental do CrewAI "
        "é uma <b>organização</b>, não um grafo: cada <i>Agent</i> tem papel, objetivo e história; cada "
        "<i>Task</i> tem uma saída esperada; a <i>Crew</i> reúne os agentes; o <i>Process</i> é sequencial ou "
        "hierárquico. <b>Onde brilha:</b> protótipo e demonstração — é a menor curva de entrada do grupo, e "
        "decompor por papel <b>força o time a escrever o que cada agente faz</b>, o que sem querer é meio caminho "
        "para uma especificação. <b>Onde dói, e diga:</b> a metáfora de papéis <b>esconde o laço</b> — quando "
        "falha, você depura uma abstração, não uma sequência de chamadas; a 'história' do agente é prompt "
        "disfarçado; e estado e durabilidade são fracos comparados ao LangGraph. <b>Veredito:</b> ótimo para "
        "levantar um piloto numa tarde e mostrar à direção; pense duas vezes antes de produção regulada. E o que "
        "aprendemos apanhando dele é o que o Bloco 11 mostra resolvido com portão determinístico. <i>(~2 min)</i>")


def s39(prs):
    s = D._blank(prs); D.header(s, 7, "Bloco 7 · Frameworks", "AutoGen / AG2")
    D.cards(s, 7, [
        ("Modelo mental: conversa entre agentes.", "ConversableAgent como unidade; GroupChat com um gerente que escolhe quem fala; executor de código embutido."),
        ("Humano-no-laço nativo e granular.", "O modo de intervenção é configurável por agente (sempre, nunca, só ao terminar) — direto no gate de notificação de vocês.", "good"),
        ("Onde brilha: exploração e pesquisa, caminho não conhecido de antemão.", "É o parente mais próximo do AI Co-Scientist (S62)."),
        ("Onde dói: comportamento emergente — a conversa pode divergir e gastar tokens sem convergir.", "E cuidado com a linhagem: Microsoft × fork comunitário AG2, exemplos incompatíveis.", "warn"),
    ], x=0.6, y=2.05, size=15.5)
    D.footer(s, 7, 39, TOTAL)
    reg(39, 7, "AutoGen / AG2", 2.0, 67.5,
        "<b>Dois minutos — o mais interessante e o mais arriscado.</b> O modelo mental do AutoGen é uma "
        "<b>conversa entre agentes</b>: a unidade é o <i>ConversableAgent</i>, um <i>GroupChat</i> tem um gerente "
        "que decide quem fala em seguida, há um ponto de entrada humano e um <b>executor de código</b> embutido "
        "— o agente escreve, roda e vê o resultado. O grande trunfo para vocês: o <b>humano-no-laço é nativo e "
        "granular</b> — dá para configurar por agente quando ele pede intervenção (sempre, nunca, só ao "
        "terminar), o que encaixa direto no portão de aprovação da notificação. <b>Onde brilha:</b> exploração e "
        "pesquisa, quando o caminho não é conhecido — é o parente mais próximo do AI Co-Scientist do S62. "
        "<b>Onde dói:</b> comportamento emergente — a conversa pode divergir, repetir e gastar tokens sem "
        "convergir. E uma nota prática: o projeto se dividiu entre a linha da Microsoft e o fork comunitário AG2, "
        "então confira a linhagem antes de copiar exemplo. <i>(~2 min)</i>")


def s40(prs):
    s = D._blank(prs); D.header(s, 7, "Bloco 7 · Frameworks", "Comparativo e a opinião contrária")
    rows = [
        ["OpenAI SDK", "controla o laço", "sessão", "guardrails", "produtos OpenAI"],
        ["Claude Agent SDK", "controla o laço", "arquivos", "hooks + permissões", "código / arquivos"],
        ["*LangGraph", "*máquina de estados", "*durável", "*nativo (interrupt)", "*produção regulada"],
        ["CrewAI", "esconde o laço", "fraco", "limitado", "protótipo rápido"],
        ["AutoGen / AG2", "conversa", "fraco", "granular", "exploração / pesquisa"],
        ["laço próprio", "você controla", "você faz", "você faz", "70% dos casos"],
    ]
    D.table(s, 7, ["Framework", "Controle do laço", "Estado", "Humano-no-laço", "Caso ideal"], rows,
            x=0.6, y=2.05, w=D.SW-1.2, fsize=13, header_fs=12.5, h=3.4)
    D.callout(s, 7, [("A opinião contrária: ", {"size": 16, "bold": True, "color": D.WARN}),
                     ("para uns 70% dos casos, o laço direto é mais simples de depurar. Framework se justifica por durabilidade, observabilidade e humano-no-laço — não por elegância. “Não adotem framework antes de ter o eval do S20.”",
                      {"size": 15, "color": D.INK})], y=5.6, h=1.1, kind="warn")
    D.footer(s, 7, 40, TOTAL)
    reg(40, 7, "Tabela comparativa e a opinião contrária", 1.5, 69.0,
        "<b>90 segundos — leia em voz alta só a última coluna da tabela.</b> Passe o olho pelas linhas, mas "
        "leia mesmo só o <b>caso ideal</b> de cada um: OpenAI SDK para quem vive no ecossistema deles; Claude "
        "Agent SDK para código e arquivos; <b>LangGraph para produção regulada</b> (durável, humano-no-laço "
        "nativo); CrewAI para protótipo rápido; AutoGen para exploração; e o <b>laço próprio</b> para a maioria "
        "dos casos. Aí venha com a <b>opinião contrária</b>, que dá honestidade à palestra: para uns 70% dos "
        "casos, o laço direto é mais fácil de depurar; framework se justifica por <b>durabilidade, "
        "observabilidade e humano-no-laço</b>, não por elegância. E feche com a regra: <i>'não adotem framework "
        "antes de ter o conjunto de avaliação do S20'</i>. <i>(~1,5 min)</i>")


# ===================== BLOCO 8 — Ambientes =====================
def s41(prs):
    s = D._blank(prs); D.header(s, 8, "Bloco 8 · Ambientes", "Mudou a unidade de trabalho")
    D.quote(s, 8, [("Do autocompletar de uma linha para a ", {"size": 21, "bold": True, "color": D.FAM['teal'][0]}),
                   ("tarefa sobre o repositório inteiro.", {"size": 21, "bold": True, "color": D.FAM['teal'][0]})],
            y=2.2, h=1.4)
    D.cards(s, 8, [
        ("A revisão passa a ser de um diff inteiro, não de uma sugestão de linha.", "Isso muda o code review do time — e é uma mudança de processo, não de ferramenta.", "warn"),
    ], x=0.6, y=4.1, size=17, ch=1.1)
    D.footer(s, 8, 41, TOTAL)
    reg(41, 8, "Mudança de unidade de trabalho", 1.0, 70.0,
        "<b>Um minuto de enquadramento.</b> Os ambientes agênticos de código mudaram a <b>unidade de "
        "trabalho</b>: saímos do autocompletar de uma linha para a <b>tarefa sobre o repositório inteiro</b> — "
        "'implemente este requisito', não 'complete esta linha'. A consequência prática, e é de processo: a "
        "revisão do time passa a ser de um <b>diff inteiro</b> gerado por IA, não de uma sugestãozinha. Isso "
        "muda como o code review funciona — e é bom avisar o time antes, não depois. <i>(~1 min)</i>")


def s42(prs):
    s = D._blank(prs); D.header(s, 8, "Bloco 8 · Ambientes", "Claude Code")
    D.cards(s, 8, [
        ("CLI com busca agêntica sem indexação prévia.", "Explora o repositório na hora, em vez de manter um índice que envelhece."),
        ("CLAUDE.md, subagentes, skills, MCP, modo headless para CI.", "O contexto do projeto e as capacidades ficam versionados no repositório."),
        ("Hooks são o mecanismo de PORTÃO.", "Lint, teste e política rodam DENTRO do laço — não depois. É o gate do Bloco 9 acontecendo na prática.", "good"),
    ], x=0.6, y=2.05, size=16.5)
    D.footer(s, 8, 42, TOTAL)
    reg(42, 8, "Claude Code", 2.0, 72.0,
        "<b>Dois minutos.</b> O Claude Code é uma ferramenta de linha de comando com <b>busca agêntica sem "
        "indexação prévia</b> — ele explora o repositório na hora, então nunca trabalha com um índice "
        "desatualizado. Traz o <b>CLAUDE.md</b> (o contexto do projeto versionado), subagentes, skills, MCP e um "
        "<b>modo headless</b> para rodar em integração contínua. Mas o que interessa para a tese da palestra são "
        "os <b>hooks</b>: eles são o <b>mecanismo de portão</b>. Lint, teste e verificação de política rodam "
        "<b>dentro do laço</b>, não depois — ou seja, é o <i>gate</i> do Bloco 9 acontecendo já aqui, na "
        "ferramenta. <i>(~2 min)</i>")


def s43(prs):
    s = D._blank(prs); D.header(s, 8, "Bloco 8 · Ambientes", "Cursor e o panorama")
    D.cards(s, 8, [
        ("Cursor: IDE com indexação prévia, Composer/Agent, regras de projeto.", "Indexa antes (rápido, mas o índice pode ficar defasado)."),
        ("O trade-off de fundo:", "indexação prévia (rápida, risco de índice velho) × exploração sob demanda (lenta, sempre atual)."),
        ("O resto do panorama, numa linha:", "Copilot, Windsurf, Aider, Codex, Devin — variações do mesmo tema."),
    ], x=0.6, y=2.05, size=16.5)
    D.footer(s, 8, 43, TOTAL)
    reg(43, 8, "Cursor e o panorama", 1.0, 73.0,
        "<b>Um minuto para fechar o bloco.</b> O <b>Cursor</b> é um ambiente de desenvolvimento (IDE) com "
        "<b>indexação prévia</b>: ele monta um índice do código antes, o que deixa a busca rápida — ao risco de "
        "o índice ficar defasado. Esse é o trade-off de fundo do bloco: <b>indexar antes</b> (rápido, mas pode "
        "envelhecer) versus <b>explorar sob demanda</b> como o Claude Code (mais lento, sempre atual). E o resto "
        "do panorama numa linha só — Copilot, Windsurf, Aider, Codex, Devin — são variações do mesmo tema. "
        "<i>(~1 min)</i>")


# ===================== BLOCO 9 — SDD (núcleo) =====================
def s44(prs):
    s = D._blank(prs); D.header(s, 9, "Bloco 9 · SDD", "O problema: “vibe coding”")
    D.cards(s, 9, [
        ("Programar “no feeling” funciona no protótipo e colapsa no sistema.", "Enquanto é pequeno, tudo bem. Quando cresce, ninguém mais segura na cabeça."),
        ("O sintoma:", "o código existe, funciona — e ninguém sabe qual requisito ele atende, nem se ainda atende."),
        ("Em domínio regulado, isso tem outro nome: NÃO CONFORMIDADE.", "Não é dívida técnica; é risco regulatório.", "warn"),
    ], x=0.6, y=2.05, size=17)
    D.footer(s, 9, 44, TOTAL)
    reg(44, 9, "O problema (vibe coding)", 1.5, 74.5,
        "<b>90 segundos para nomear a dor.</b> O 'vibe coding' — programar no feeling, pedindo pedaços à IA e "
        "colando — funciona lindamente no protótipo e <b>colapsa no sistema</b>. O sintoma é traiçoeiro: o "
        "código <b>existe e funciona</b>, mas ninguém sabe <b>qual requisito ele atende</b> nem se ainda atende. "
        "Num sistema comum isso é dívida técnica. Em <b>domínio regulado</b> — software de saúde — isso tem outro "
        "nome, e diga com todas as letras: <b>não conformidade</b>. É a transição perfeita para mostrar a "
        "alternativa. <i>(~1,5 min)</i>")


def s45(prs):
    s = D._blank(prs); D.header(s, 9, "Bloco 9 · SDD", "A inversão")
    D._rect(s, 0.6, 2.05, D.SW-1.2, 1.35, fill=D.FAM['rose'][2], rounded=True, radius=0.06)
    D._rect(s, 0.6, 2.05, 0.12, 1.35, fill=D.FAM['rose'][0])
    D._txt(s, 0.95, 2.15, D.SW-1.7, 1.2, [
        [("(a) O jeito de hoje:  ", {"size": 16, "bold": True, "color": D.FAM['rose'][0]}),
         ("requisito informal → código → documentação que já nasce desatualizada.", {"size": 16, "color": D.INK})]],
        anchor=MSO_ANCHOR.MIDDLE)
    D._rect(s, 0.6, 3.6, D.SW-1.2, 1.35, fill=D.FAM['emerald'][2], rounded=True, radius=0.06)
    D._rect(s, 0.6, 3.6, 0.12, 1.35, fill=D.FAM['emerald'][0])
    D._txt(s, 0.95, 3.7, D.SW-1.7, 1.2, [
        [("(b) O SDD:  ", {"size": 16, "bold": True, "color": D.FAM['emerald'][0]}),
         ("especificação PRIMÁRIA → plano → tarefas → código DERIVADO.", {"size": 16, "color": D.INK})]],
        anchor=MSO_ANCHOR.MIDDLE)
    D.quote(s, 9, [("A spec é o que se versiona, revisa e mantém. O código é o que se regenera. ",
                    {"size": 18, "bold": True, "color": D.FAM['indigo'][0]}),
                   ("“É a relação entre código-fonte e binário — ninguém revisa o binário.”",
                    {"size": 18, "italic": True, "color": D.INK})], y=5.2, h=1.35)
    D.footer(s, 9, 45, TOTAL)
    reg(45, 9, "A inversão", 2.0, 76.5,
        "<b>Dois minutos para a ideia mais importante do bloco.</b> Contraste os dois fluxos. Hoje (a): um "
        "requisito informal vira código, e a documentação nasce atrás, desatualizada. No SDD (b): a "
        "<b>especificação é primária</b> — dela derivam o plano, as tarefas e o <b>código</b>. A inversão é essa: "
        "<b>a spec é o que se versiona, revisa e mantém; o código é o que se regenera</b>. E a analogia que faz a "
        "ficha cair na plateia de dev: <i>'é a mesma relação entre código-fonte e binário — ninguém revisa o "
        "binário; você revisa a fonte e recompila'</i>. No SDD, a spec é a fonte e o código é o binário. "
        "<i>(~2 min)</i>")


def s46(prs):
    s = D._blank(prs); D.header(s, 9, "Bloco 9 · SDD", "O ciclo SDD")
    D.image_center(s, os.path.join("diagrams", "s46_sdd.png"), x=0.5, y=1.95, w=D.SW-1.0, h=D.SH-2.45, block=9)
    D.footer(s, 9, 46, TOTAL)
    reg(46, 9, "O ciclo SDD", 2.5, 79.0,
        "<b>Dois minutos e meio no diagrama central da palestra.</b> O ciclo é: <b>Intenção → Especificação → "
        "Plano → Tarefas → Implementação → Verificação</b>. O que muda tudo são os <b>portões (gates)</b> entre "
        "cada etapa: nada avança sem passar num portão, e em caso de falha, <b>volta</b>. Os portões podem ser "
        "aprovação humana, teste automatizado, verificação de política ou verificação formal. Agora faça a "
        "conexão explícita com o S28: lá vimos que 20 passos não verificados dão 36% de sucesso. <b>Cada portão "
        "aqui corta um elo não verificado dessa cadeia</b> — é assim, mecanicamente, que se derruba a curva do "
        "erro composto. O SDD não é burocracia; é a resposta de engenharia ao erro que se multiplica. "
        "<i>(~2,5 min)</i>")


def s47(prs):
    s = D._blank(prs); D.header(s, 9, "Bloco 9 · SDD", "Anatomia de uma especificação útil")
    D.cards(s, 9, [
        ("Contexto e escopo · NÃO-objetivos · requisitos em EARS.", "Dizer o que está fora é tão importante quanto o que está dentro."),
        ("Critérios de aceitação verificáveis · contratos · invariantes · referências normativas.", ""),
    ], x=0.6, y=2.05, w=6.4, size=15.5, ch=1.15)
    b, t = D.panel(s, 7.15, 2.05, D.SW-7.75, 3.9, block=9)
    D._txt(s, 7.45, 2.2, D.SW-8.35, 3.6, [
        [("Requisito em EARS (bom):", {"size": 14.5, "bold": True, "color": D.FAM['emerald'][0]})],
        [("“Quando uma hemocultura positiva for registrada, o sistema deve avaliar os critérios de ICSAC dentro de 48 h e produzir um parecer com evidência citada.”",
          {"size": 14, "color": D.INK})],
        [("Requisito ruim (não verificável):", {"size": 14.5, "bold": True, "color": D.WARN})],
        [("“O sistema deve detectar infecções corretamente.”", {"size": 14, "italic": True, "color": D.INK})],
    ], anchor=MSO_ANCHOR.TOP, space_after=10, line_spacing=1.15)
    D.footer(s, 9, 47, TOTAL)
    reg(47, 9, "Anatomia de uma spec útil", 2.0, 81.0,
        "<b>Dois minutos, e o exemplo faz o serviço.</b> Uma spec útil tem: contexto e escopo, os "
        "<b>não-objetivos</b> (o que está fora — tão importante quanto o que está dentro), requisitos escritos em "
        "<b>EARS</b> (uma sintaxe padronizada de requisito), critérios de aceitação <b>verificáveis</b>, "
        "contratos, invariantes e referências normativas. Mostre o contraste na tela: o requisito bom é "
        "<i>'quando uma hemocultura positiva for registrada, o sistema deve avaliar os critérios de ICSAC dentro "
        "de 48 horas e produzir um parecer com evidência citada'</i> — tem gatilho, prazo e saída verificável. O "
        "ruim é <i>'o sistema deve detectar infecções corretamente'</i> — impossível de testar. A diferença "
        "entre os dois é a diferença entre uma spec que gera teste e uma frase de efeito. <i>(~2 min)</i>")


def s48(prs):
    s = D._blank(prs); D.header(s, 9, "Bloco 9 · SDD", "Exemplo ponta a ponta: da spec ao código")
    cols = [("SPEC", D.FAM['indigo'], "critério ICSAC +\njanela de 48 h\n(requisito R-014)"),
            ("TESTE gerado", D.FAM['emerald'], "test_r014_janela_48h\nconfere as bordas\nda janela"),
            ("IMPLEMENTAÇÃO", D.FAM['sky'], "avaliar_icsac()\nderivada da spec,\nnão o contrário")]
    cw = (D.SW-1.2-0.6)/3; x = 0.6
    for name, col, desc in cols:
        D._rect(s, x, 2.15, cw, 3.0, fill=col[2], rounded=True, radius=0.07)
        D._rect(s, x, 2.15, cw, 0.6, fill=col[0])
        D._txt(s, x+0.1, 2.2, cw-0.2, 0.55, [[(name, {"size": 15, "bold": True, "color": D.WHITE})]],
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        D._txt(s, x+0.2, 3.05, cw-0.4, 1.9, [[(desc, {"size": 14, "font": D.MONO, "color": D.INK})]],
               align=PP_ALIGN.CENTER, line_spacing=1.25)
        if x < 8: D._txt(s, x+cw-0.15, 3.3, 0.4, 0.6, [[("→", {"size": 22, "bold": True, "color": D.MUTED})]])
        x += cw + 0.3
    D.callout(s, 9, [("Rastreabilidade: ", {"size": 16, "bold": True, "color": D.FAM['indigo'][0]}),
                     ("R-014 → test_r014_janela_48h → avaliar_icsac().  O teste nasceu do CRITÉRIO, não do código — por isso não herda os bugs da implementação.",
                      {"size": 15, "color": D.INK})], y=5.35, h=1.1, kind="good")
    D.footer(s, 9, 48, TOTAL)
    reg(48, 9, "Exemplo ponta a ponta", 3.0, 84.0,
        "<b>Três minutos — é a prova concreta do SDD, então vá devagar.</b> Três painéis. No primeiro, um trecho "
        "da <b>spec</b>: o critério de ICSAC com a janela de 48 horas, identificado como requisito R-014. No "
        "segundo, o <b>teste gerado a partir do critério</b> — repare, ele confere exatamente as bordas da "
        "janela. No terceiro, a <b>implementação</b>, a função <i>avaliar_icsac()</i>, que é <b>derivada</b> da "
        "spec. Agora mostre a linha de <b>rastreabilidade</b>: R-014 aponta para o teste, que aponta para a "
        "função. E diga a frase que é o coração do método: <i>'o teste nasceu do critério, não do código; por "
        "isso ele não herda os bugs da implementação'</i>. Um teste escrito a partir do código só confirma o que "
        "o código faz — inclusive os erros. Um teste escrito a partir do critério confere o que o sistema "
        "<b>deveria</b> fazer. <i>(~3 min)</i>")


def s49(prs):
    s = D._blank(prs); D.header(s, 9, "Bloco 9 · SDD", "Ferramental de SDD")
    D.cards(s, 9, [
        ("GitHub Spec Kit.", "Comandos /specify, /plan, /tasks, /implement — o ciclo do S46 como fluxo de trabalho."),
        ("Kiro.", "Organiza requirements.md, design.md e tasks.md no repositório."),
        ("Tessl.", "Outra aposta no mesmo princípio: a spec como artefato primário."),
        ("Feche a promessa do S33: specs/ + AGENTS.md + pacote OKF no MESMO repositório.", "O que o sistema faz, como se trabalha nele e o domínio que ele modela — tudo markdown versionado.", "good"),
    ], x=0.6, y=2.05, size=16)
    D.footer(s, 9, 49, TOTAL)
    reg(49, 9, "Ferramental", 2.0, 86.0,
        "<b>Dois minutos, e aqui você fecha um arco que abriu antes do intervalo.</b> O ferramental já existe: o "
        "<b>GitHub Spec Kit</b>, com comandos que são o próprio ciclo do S46 — /specify, /plan, /tasks, "
        "/implement; o <b>Kiro</b>, que organiza requirements, design e tasks em markdown; e o <b>Tessl</b>. Mas "
        "o ponto alto é cumprir a promessa do S33: numa árvore de projeto, a pasta <b>specs/</b> fica ao lado do "
        "<b>AGENTS.md</b> e do <b>pacote OKF</b> — <b>o que</b> o sistema deve fazer, <b>como</b> se trabalha "
        "nele, e o <b>domínio</b> que ele modela, tudo markdown versionado no mesmo repositório. É essa "
        "convivência que constrói a rastreabilidade — e a rastreabilidade é o que o próximo slide transforma em "
        "argumento comercial. <i>(~2 min)</i>")


def s50(prs):
    s = D._blank(prs); D.header(s, 9, "Bloco 9 · SDD", "Onde o SDD encontra os agentes")
    chain = [("Especificador", D.FAM['indigo']), ("Arquiteto", D.FAM['sky']),
             ("Implementador", D.FAM['teal']), ("Verificador", D.FAM['emerald'])]
    cw = 2.55; gate = 0.7; x = 0.65; y = 2.3
    for i, (name, col) in enumerate(chain):
        D._rect(s, x, y, cw, 1.3, fill=col[2], rounded=True, radius=0.1)
        D._rect(s, x, y, cw, 0.16, fill=col[0])
        D._txt(s, x, y+0.35, cw, 0.7, [[(name, {"size": 15, "bold": True, "color": col[0]})]],
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        x += cw
        if i < 3:
            D._rect(s, x+0.05, y+0.4, gate-0.1, 0.5, fill=D.FAM['emerald'][2], rounded=True, radius=0.2)
            D._txt(s, x+0.02, y+0.42, gate, 0.45, [[("GATE", {"size": 8.5, "bold": True, "color": D.FAM['emerald'][0]})]],
                   align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            x += gate
    D.cards(s, 9, [
        ("Contexto isolado por etapa, e o GATE em código DETERMINÍSTICO — não em outro modelo.", "Verificar com um segundo LLM só empilha incerteza; o portão tem que ser código que passa ou não passa."),
        ("Feche o S28: o monólito de 20 passos tem 36% de sucesso; a cadeia com gate se comporta de forma inteiramente diferente — o erro não se propaga.", "", "good"),
        ("É isto que vou mostrar rodando no Bloco 11: um gerador cujo portão determinístico pega o erro do agente ANTES do deploy.", "", "warn"),
    ], x=0.6, y=4.1, size=15)
    D.footer(s, 9, 50, TOTAL)
    reg(50, 9, "Onde SDD encontra agentes", 2.5, 88.5,
        "<b>Dois minutos e meio — é onde os dois grandes temas da palestra se encontram.</b> Em vez de um agente "
        "monolítico fazendo 20 passos, você monta uma <b>cadeia</b>: especificador, arquiteto, implementador, "
        "verificador — com <b>contexto isolado</b> em cada etapa e um <b>portão entre cada um</b>. E o detalhe "
        "que é a chave de tudo: o portão tem que ser <b>código determinístico</b>, não outro modelo de "
        "linguagem. Verificar um LLM com outro LLM só empilha incerteza; o portão precisa ser código que passa "
        "ou não passa. Faça a matemática do S28 fechar: o monólito de 20 passos tem 36% de sucesso; a cadeia de "
        "4 agentes com portão determinístico se comporta de forma <b>inteiramente diferente</b>, porque o erro "
        "não se propaga — ele para no portão. E anuncie o Bloco 11: <i>'vou mostrar isto rodando — um gerador "
        "cujo portão determinístico pega o erro do agente antes do deploy'</i>. <i>(~2,5 min)</i>")


def s51(prs):
    s = D._blank(prs); D.header(s, 9, "Bloco 9 · SDD", "O SDD entrega o artefato regulatório de graça")
    D.cards(s, 9, [
        ("Software de saúde exige rastreabilidade requisito → projeto → teste → código.", "Mais gestão de risco documentada e ciclo de vida controlado: IEC 62304, ISO 14971 e a RDC da ANVISA."),
        ("Quem faz SDD JÁ TEM a matriz de rastreabilidade — como subproduto, versionada, com autoria e histórico.", "", "good"),
        ("A inversão da objeção: o SDD é o que torna código gerado por IA AUDITÁVEL.", "O que NÃO é auditável é código escrito à mão sem especificação.", "warn"),
    ], x=0.6, y=2.05, size=16.5)
    D.footer(s, 9, 51, TOTAL)
    reg(51, 9, "SDD produz o artefato regulatório de graça", 3.0, 91.5,
        "<b>Três minutos — é o pico comercial da palestra. Depois da última frase, PAUSE.</b> Software para saúde "
        "exige, por norma, rastreabilidade de requisito até projeto, teste e código, gestão de risco documentada "
        "e ciclo de vida controlado — as normas IEC 62304, ISO 14971 e a regulamentação da ANVISA para software "
        "como dispositivo médico (confira o número da RDC vigente na semana). Aqui está a virada: <b>quem faz "
        "SDD já tem a matriz de rastreabilidade como subproduto</b> — versionada, com autoria e histórico, "
        "porque ela cai fora do processo naturalmente. Agora inverta a objeção que está na cabeça deles. Eles "
        "pensam 'IA generativa em software regulado é risco'. A resposta é: <b>o SDD é justamente o que torna "
        "código gerado por IA auditável</b>. E o golpe final, diga devagar: <i>'o que não é auditável é código "
        "escrito à mão, sem especificação'</i>. Complemente com o S30 e o S13: os protocolos não expressam "
        "governança e a janela que estoura corta em silêncio — então política de autorização e controle de "
        "contexto são responsabilidade da arquitetura de vocês. <b>Pause depois dessa frase.</b> <i>(~3 min)</i>")


def s52(prs):
    s = D._blank(prs); D.header(s, 9, "Bloco 9 · SDD", "Antipadrões: como o SDD morre na prática")
    D.cards(s, 9, [
        ("Spec inflada.", "Escreve o que não vai verificar. Antídoto: só entra o que tem critério de aceitação."),
        ("Spec envelhecida.", "Código andou, spec não. Antídoto: CI que falha quando o código diverge da spec."),
        ("Gate humano virado carimbo.", "Aprova sem ler. Antídoto: o revisor assina o diff, não o PDF."),
        ("Spec gerada por IA e aprovada sem leitura — a PIOR.", "Produz aparência de rastreabilidade sem substância. Se ninguém leu, não há SDD, há teatro.", "warn"),
    ], x=0.6, y=2.05, size=16)
    D.footer(s, 9, 52, TOTAL)
    reg(52, 9, "Antipadrões", 0.5, 92.0,
        "<b>30 segundos, rápido mas afiado — é onde o sênior vai te testar.</b> Cinco maneiras de o SDD morrer na "
        "prática: <b>spec inflada</b> (escreve o que não vai verificar; antídoto: só entra o que tem critério de "
        "aceitação); <b>spec envelhecida</b> (o código andou e a spec não; antídoto: integração contínua que "
        "falha quando divergem); <b>critério não executável</b>; <b>gate humano virado carimbo</b> (aprova sem "
        "ler; antídoto: assinar o diff, não o PDF); e a <b>pior</b> — <b>spec gerada por IA e aprovada sem "
        "leitura</b>, que produz <b>aparência de rastreabilidade sem substância</b>. Diga a frase: 'se ninguém "
        "leu, não há SDD, há teatro'. <i>(~30 s)</i>")


# ===================== BLOCO 10 — Adaptação =====================
def s53(prs):
    s = D._blank(prs); D.header(s, 10, "Bloco 10 · Adaptação", "A escada da adaptação")
    D.cards(s, 10, [
        ("Os degraus, do mais barato ao mais caro:", "prompt → poucos exemplos (few-shot) → RAG → ajuste fino / LoRA → aprendizado por reforço → pré-treino contínuo."),
        ("Só suba um degrau quando o anterior falhar COM EVIDÊNCIA MEDIDA.", "E a evidência é o conjunto de avaliação do S20 — não o “achismo”.", "warn"),
        ("Retome a seta do S4:", "é aqui que se faz “o transplante em cima do modelo pronto” que prometi no começo."),
    ], x=0.6, y=2.05, size=16.5)
    D.footer(s, 10, 53, TOTAL)
    reg(53, 10, "A escada de adaptação", 1.5, 93.5,
        "<b>90 segundos para organizar as opções de personalização.</b> Existe uma escada, do mais barato ao "
        "mais caro: <b>prompt</b>, depois <b>poucos exemplos</b> no prompt (few-shot), depois <b>RAG</b>, depois "
        "<b>ajuste fino</b> ou LoRA, depois <b>aprendizado por reforço</b>, e no topo <b>pré-treino contínuo</b>. "
        "A regra de ouro, e martele: <b>só suba um degrau quando o de baixo falhar com evidência medida</b> — e "
        "a evidência é o conjunto de avaliação do S20. A maioria dos times quer treinar um modelo quando o "
        "problema se resolvia com melhor recuperação. Retome a seta do S4: é aqui que se faz o 'transplante em "
        "cima do modelo pronto'. <i>(~1,5 min)</i>")


def s54(prs):
    s = D._blank(prs); D.header(s, 10, "Bloco 10 · Adaptação", "Ajuste fino (SFT) e os dados")
    D.code_block(s, '{"messages": [\n  {"role": "system",\n   "content": "Você classifica critérios de IRAS."},\n  {"role": "user",\n   "content": "<evolução clínica...>"},\n  {"role": "assistant",\n   "content": "{criterio: ..., atendido: true}"}\n]}',
                 x=0.6, y=2.1, w=6.6, size=12.5)
    D.cards(s, 10, [
        ("Ajuste fino supervisionado = ensinar por exemplos rotulados.", "O formato é JSONL: cada linha é uma conversa completa (sistema, usuário, resposta)."),
        ("500 a 5.000 exemplos BEM curados superam 100 mil sujos.", "Qualidade vence quantidade — de longe.", "good"),
        ("O custo real de um dataset clínico é tempo de infectologista, não GPU.", "", "warn"),
    ], x=7.35, y=2.1, w=D.SW-7.95, size=14.5)
    D.footer(s, 10, 54, TOTAL)
    reg(54, 10, "SFT e os dados", 1.0, 94.5,
        "<b>Um minuto, e a mensagem é contraintuitiva.</b> Ajuste fino supervisionado (SFT) é ensinar o modelo "
        "por <b>exemplos rotulados</b> — o formato é JSONL, cada linha uma conversa completa. O que a plateia "
        "precisa ouvir: <b>500 a 5.000 exemplos bem curados superam 100 mil exemplos sujos</b>. Qualidade vence "
        "quantidade de longe. E a consequência de gestão: o custo real de um conjunto de dados clínico não é "
        "GPU, é <b>tempo de infectologista</b> rotulando — planeje por aí. <i>(~1 min)</i>")


def s55(prs):
    s = D._blank(prs); D.header(s, 10, "Bloco 10 · Adaptação", "LoRA e QLoRA: ajuste fino que cabe numa GPU")
    D.code_block(s, "LoraConfig(\n  r=16,            # posto: quão “grande” é o remendo\n  lora_alpha=32,\n  lora_dropout=0.05,\n  target_modules=[\"q_proj\",\"k_proj\",\n                  \"v_proj\",\"o_proj\"],\n  task_type=\"CAUSAL_LM\")",
                 x=0.6, y=2.1, w=6.7, size=13)
    D.cards(s, 10, [
        ("A ideia: congela o modelo W e treina só um remendo pequeno (ΔW = B·A).", "Treina 0,1–1% dos parâmetros — daí caber numa GPU de consumo."),
        ("QLoRA: base em 4 bits + adaptadores em precisão maior.", "É o que permite ajustar um modelo grande em 24 GB."),
        ("Vantagem operacional: adaptadores são arquivos de dezenas de MB — versionáveis e trocáveis em runtime.", "Um adaptador por especialidade, a MESMA base (pode ser o Qwen3.8-27B do S12).", "good"),
    ], x=7.45, y=2.1, w=D.SW-8.05, size=14),
    D.footer(s, 10, 55, TOTAL)
    reg(55, 10, "LoRA e QLoRA", 2.5, 97.0,
        "<b>Dois minutos e meio — o degrau técnico do bloco.</b> LoRA (adaptação de baixo posto) resolve o "
        "problema de custo do ajuste fino: em vez de retreinar o modelo inteiro, você <b>congela os pesos "
        "originais</b> e treina só um <b>remendo pequeno</b> — matematicamente, uma matriz de baixo posto que se "
        "soma aos pesos. Você treina de 0,1 a 1% dos parâmetros, e por isso cabe numa GPU de consumo. Explique o "
        "trecho: o <i>r</i> é o 'tamanho' do remendo, os <i>target_modules</i> são as camadas de atenção que ele "
        "modifica. O <b>QLoRA</b> vai além: mantém a base em 4 bits e os adaptadores em precisão maior — é o que "
        "permite ajustar um modelo grande em 24 GB. E a vantagem operacional que vende a ideia: os adaptadores "
        "são <b>arquivos de dezenas de megabytes</b>, versionáveis e trocáveis em tempo de execução — um "
        "adaptador por especialidade médica, todos sobre a <b>mesma base</b>, que pode ser o Qwen3.8-27B do S12. "
        "<i>(~2,5 min)</i>")


def s56(prs):
    s = D._blank(prs); D.header(s, 10, "Bloco 10 · Adaptação", "RLHF e sucessores")
    D.cards(s, 10, [
        ("RLHF = aprendizado por reforço com feedback humano.", "Comparações humanas → modelo de recompensa → otimização por reforço (PPO)."),
        ("Sucessores: DPO (sem modelo de recompensa), GRPO (raciocínio), RLAIF / IA Constitucional.", ""),
        ("Por que importa mesmo sem treinar: explica o comportamento do modelo que vocês CONSOMEM.", "Bajulação, recusa e excesso de ressalvas são artefatos do alinhamento — não do pré-treino.", "good"),
    ], x=0.6, y=2.05, size=16.5)
    D.footer(s, 10, 56, TOTAL)
    reg(56, 10, "RLHF e sucessores", 1.0, 98.0,
        "<b>Um minuto, e o valor é explicar o modelo que eles já usam.</b> RLHF — aprendizado por reforço com "
        "feedback humano — é como se alinha um modelo: humanos comparam respostas, isso treina um <b>modelo de "
        "recompensa</b>, e o modelo é otimizado para agradá-lo. Os sucessores simplificam: DPO dispensa o modelo "
        "de recompensa, GRPO foca raciocínio, o RLAIF usa a própria IA como avaliadora. Mas o motivo de estar na "
        "palestra mesmo sem vocês treinarem: <b>isso explica o comportamento do modelo que vocês consomem</b> — a "
        "bajulação, as recusas exageradas, o excesso de ressalvas são <b>artefatos do alinhamento</b>, não do "
        "pré-treino. Saber disso ajuda a domar o modelo por prompt. <i>(~1 min)</i>")


def s57(prs):
    s = D._blank(prs); D.header(s, 10, "Bloco 10 · Adaptação", "Quando NÃO treinar, e o modelo local")
    D.cards(s, 10, [
        ("Não treine com conhecimento volátil (protocolo muda → use RAG), tarefa que muda toda semana, ou sem avaliação.", "Custos ocultos: esquecimento catastrófico e manutenção perpétua do modelo derivado.", "warn"),
        ("O modelo LOCAL (retomando o S12): quantização (GGUF, AWQ) + runtimes (LM Studio, vLLM, Ollama).", ""),
        ("Três argumentos que fecham a palestra técnica:", "o dado do paciente não sai da rede · custo marginal previsível · independência de fornecedor.", "good"),
    ], x=0.6, y=2.05, size=16)
    D.footer(s, 10, 57, TOTAL)
    reg(57, 10, "Quando NÃO treinar, e o modelo local", 1.0, 99.0,
        "<b>Um minuto para fechar a adaptação com equilíbrio.</b> Diga quando <b>não</b> treinar: se o "
        "conhecimento é volátil (um protocolo que muda — use RAG, não ajuste fino), se a tarefa muda toda "
        "semana, ou se você não tem avaliação para medir o ganho. E avise dos custos ocultos: o <b>esquecimento "
        "catastrófico</b> (o modelo perde capacidades ao aprender a nova) e a <b>manutenção perpétua</b> do "
        "modelo derivado. Feche com o <b>modelo local</b>, retomando o S12: quantização e runtimes como LM "
        "Studio, vLLM e Ollama permitem rodar em casa. E os três argumentos que importam para saúde: <b>o dado "
        "do paciente não sai da rede</b>, o custo marginal é previsível, e você não depende de um fornecedor. É "
        "a ponte perfeita para o Bloco 11, onde os nossos sistemas rodam exatamente assim — localmente. "
        "<i>(~1 min)</i>")


# ===================== BLOCO 11 — Os sistemas =====================
def s58(prs):
    s = D._blank(prs); D.header(s, 11, "Bloco 11 · Sistemas", "Ponte: o Co-Scientist e o domínio de vocês")
    D.cards(s, 11, [
        ("O AI Co-Scientist da Google foi validado em laboratório (Nature, 2026) em três cenários.", "Repurposing de fármaco para leucemia · alvos para fibrose hepática · e um mecanismo de RESISTÊNCIA ANTIMICROBIANA."),
        ("O caso de RAM, nas palavras deles:", "com pouca informação de fundo, o sistema propôs — sozinho — que os cf-PICIs carregam genes de resistência entre espécies, incluindo E. coli e K. pneumoniae."),
        ("Isso recapitulou um achado experimental AINDA NÃO PUBLICADO — uma década de bancada.", "O segundo sistema que vou mostrar foi validado, na origem, exatamente no problema de vocês.", "good"),
    ], x=0.6, y=2.05, size=15.5)
    D.footer(s, 11, 58, TOTAL)
    reg(58, 11, "Ponte com o domínio deles", 1.0, 100.0,
        "<b>Um minuto para conectar o segundo sistema ao coração do trabalho deles.</b> O AI Co-Scientist da "
        "Google foi validado em laboratório e publicado na Nature em 2026, em três cenários biomédicos: "
        "repurposing de fármaco para leucemia, alvos novos para fibrose hepática, e — o que importa aqui — um "
        "<b>mecanismo de resistência antimicrobiana</b>. E o caso é impressionante para esta plateia: com "
        "informação de fundo mínima, o sistema propôs sozinho a hipótese, melhor ranqueada, de que os cf-PICIs "
        "(ilhas cromossômicas induzíveis por fago) carregam <b>genes de resistência a antibióticos entre "
        "espécies — incluindo E. coli e Klebsiella pneumoniae</b>, os patógenos da CCIH deles. E isso "
        "<b>recapitulou um achado experimental que ainda não tinha sido publicado</b>, fruto de uma década de "
        "bancada. Diga a frase: <i>'o segundo sistema que vou mostrar foi validado, na origem, exatamente no "
        "problema que vocês enfrentam. Chego nele — antes, o de engenharia.'</i> <i>(~1 min)</i>")


def s59(prs):
    s = D._blank(prs); D.header(s, 11, "Bloco 11 · Sistemas", "LangNet: arquitetura")
    pipe = ["Intenção", "Especificação", "Plano", "Geração de código", "Verificação"]
    cw = 2.3; gap = 0.28; x = 0.6; y = 2.15
    for i, st in enumerate(pipe):
        hot = st == "Verificação"
        col = D.FAM['emerald'] if hot else D.FAM['violet']
        D._rect(s, x, y, cw, 1.15, fill=col[2], rounded=True, radius=0.1)
        D._rect(s, x, y, cw, 0.14, fill=col[0])
        D._txt(s, x+0.1, y+0.3, cw-0.2, 0.7, [[(st, {"size": 13.5, "bold": True, "color": col[0]})]],
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        x += cw
        if i < len(pipe)-1:
            D._txt(s, x-0.02, y+0.32, gap+0.1, 0.5, [[("→", {"size": 18, "bold": True, "color": D.MUTED})]])
            x += gap
    D.cards(s, 11, [
        ("Modelo local no centro: Qwen2.5-Coder-32B via LM Studio, contexto de 64 mil tokens; framework CrewAI.", "Com avaliação em curso do Qwen3.8-27B — por visão, uso de ferramentas e raciocínio, sem perder geração de código."),
        ("Amarre com o S12: o modelo em avaliação roda em 24 GB e é o melhor denso multimodal da faixa.", "O argumento inteiro do LangNet só existe porque essa faixa chegou a esse patamar em 2026.", "good"),
    ], x=0.6, y=3.7, size=16)
    D.footer(s, 11, 59, TOTAL)
    reg(59, 11, "LangNet: arquitetura", 3.0, 103.0,
        "<b>Três minutos apresentando o primeiro sistema.</b> O LangNet implementa o ciclo do S46: da intenção à "
        "especificação, ao plano, à <b>geração de código</b> e à <b>verificação</b> — com um <b>modelo local no "
        "centro</b>. A pilha real, e diga que confere com o repositório: <b>Qwen2.5-Coder-32B rodando no LM "
        "Studio, com 64 mil tokens de contexto</b>, framework CrewAI, e uma <b>avaliação em curso do "
        "Qwen3.8-27B</b> como substituto — motivada por visão, uso de ferramentas e raciocínio num modelo menor, "
        "sob o critério de não perder capacidade de geração de código. Amarre com o S12: o modelo que estamos "
        "avaliando saiu há semanas e é o melhor denso multimodal que roda em 24 GB — <b>o argumento inteiro do "
        "LangNet só existe porque essa faixa de hardware chegou a esse patamar em 2026</b>. Isso é evidência de "
        "método, não de sorte. <i>(~3 min)</i>")


def s60(prs):
    s = D._blank(prs); D.header(s, 11, "Bloco 11 · Sistemas", "LangNet: evidência medida")
    D.cards(s, 11, [
        ("Cobertura de rastreabilidade: 100%.", "Todos os requisitos funcionais atravessam Spec → Modelo de Dados → Implementação, medido por PORTÃO DETERMINÍSTICO — não por confiança no modelo."),
        ("Suíte de tarefas geradas: 100% executando ponta a ponta.", "Contra banco real — núcleo determinístico + tarefas com agente (laudo, extração de documento)."),
        ("~10 defeitos do gerador capturados pelo portão ANTES do deploy.", "Variável indefinida, coluna inexistente, junção espacial faltante — cada um com o salto exato onde quebrava.", "good"),
    ], x=0.6, y=2.05, size=16)
    D.callout(s, 11, [("O número não é a taxa de acerto do modelo — é a taxa em que o portão ", {"size": 15.5, "color": D.INK}),
                      ("pega o erro antes de virar produção", {"size": 15.5, "bold": True, "color": D.FAM['violet'][0]}),
                      (". É o S50 acontecendo. (Remeça no exemplo clínico do vídeo.)", {"size": 15.5, "color": D.INK})],
              y=6.5, h=0.75)
    D.footer(s, 11, 60, TOTAL)
    reg(60, 11, "LangNet: evidência medida", 1.5, 104.5,
        "<b>90 segundos — e é o número que separa a apresentação de um pitch, então diga com firmeza.</b> São "
        "medições reais da validação do LangNet, não estimativa. <b>Cobertura de rastreabilidade: 100%</b> — "
        "todos os requisitos funcionais atravessam da especificação ao modelo de dados e à implementação, e isso "
        "é medido por um <b>portão determinístico</b>, não por confiança no modelo. <b>Suíte de tarefas geradas: "
        "100% rodando ponta a ponta</b> contra um banco real, incluindo tarefas determinísticas e tarefas com "
        "agente. E o mais importante: <b>cerca de dez defeitos do gerador foram capturados pelo portão antes do "
        "deploy</b> — variável indefinida, coluna que não existe, junção espacial faltando — cada um com o ponto "
        "exato onde quebraria. Diga a frase que reposiciona o número: <i>'isto não é a taxa de acerto do modelo; "
        "é a taxa em que o portão pega o erro do modelo antes de virar produção'</i> — é o S50 acontecendo de "
        "verdade. Nota: remeça esse número no exemplo clínico que for ao vídeo, para casar com o domínio deles. "
        "<i>(~1,5 min)</i>")


def s61(prs):
    s = D._blank(prs); D.header(s, 11, "Bloco 11 · Sistemas", "DEMONSTRAÇÃO GRAVADA: da spec à aplicação")
    c1, c2, c3 = D.FAM['violet']
    D._rect(s, 0.6, 2.1, 5.6, 3.9, fill=c3, rounded=True, radius=0.06)
    D._rect(s, 0.6, 2.1, 5.6, 0.5, fill=c1)
    D._txt(s, 0.6, 2.14, 5.6, 0.45, [[("▶  VÍDEO — até 3 min, sem áudio, legendas grandes", {"size": 13, "bold": True, "color": D.WHITE})]],
           align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    D._dot(s, 2.95, 3.55, 1.0, c1)
    D._txt(s, 0.6, 5.5, 5.6, 0.4, [[("(inserir a gravação da tela do LangNet)", {"size": 12, "italic": True, "color": D.MUTED})]],
           align=PP_ALIGN.CENTER)
    D.bullets(s, [
        (0, [("1. você escreve uma spec curta (15–20 linhas) — deixe na tela para ler", "n")]),
        (0, [("2. geração do plano e das tarefas", "n")]),
        (0, [("3. app completo: modelo de dados, lógica, API e ", "n"), ("interface", "b")]),
        (0, [("4. execução da suíte derivada dos critérios", "n")]),
        (0, [("5. uma falha de teste e a correção — ", "n"), ("não corte", "w")]),
        (0, [("6. a aplicação rodando com a interface", "n")]),
        (0, [("7. volta à spec, com o ", "n"), ("portão de rastreabilidade VERDE", "g")]),
    ], x=6.55, y=2.15, w=D.SW-7.15, size=15, block=11)
    D.footer(s, 11, 61, TOTAL)
    reg(61, 11, "DEMO gravada: da especificação à aplicação", 3.0, 107.5,
        "<b>Três minutos — é o ponto mais alto de prova da palestra. Deixe o vídeo falar.</b> Toque a gravação "
        "(até 3 minutos, sem áudio, legendas grandes; acelere as esperas de 2 a 4 vezes com o tempo real na "
        "legenda). O roteiro do vídeo, que mapeia um-para-um o que o LangNet faz: (1) você escreve uma spec "
        "curta, de 15 a 20 linhas — <b>deixe na tela tempo de ser lida</b>; (2) ele gera o plano e as tarefas; "
        "(3) gera o <b>aplicativo completo</b> — modelo de dados, lógica, API e <b>interface</b>; (4) roda a "
        "suíte de testes derivada dos critérios; (5) <b>uma falha de teste e a correção — não corte essa "
        "parte</b>, é o que prova que é real; (6) a aplicação rodando com a interface; (7) volta à spec, com o "
        "<b>portão de rastreabilidade verde na tela</b> — fechando o arco do S48 e do S51. Ao fim, 30 segundos "
        "seus: diga o tempo real, os tokens gastos e o que você corrigiu à mão. <i>(~3 min)</i>")


def s62(prs):
    s = D._blank(prs); D.header(s, 11, "Bloco 11 · Sistemas", "Como funciona o AI Co-Scientist (Nature, 2026)")
    D.image_center(s, os.path.join("diagrams", "s62_coscientist.png"), x=0.5, y=1.9, w=D.SW-1.0, h=D.SH-2.4, block=11)
    D.footer(s, 11, 62, TOTAL)
    reg(62, 11, "Como funciona o AI Co-Scientist", 2.5, 110.0,
        "<b>Dois minutos e meio no sistema multiagente mais elegante que existe hoje.</b> É da Google DeepMind, "
        "sobre o Gemini 2.0, publicado na Nature em 2026. O objetivo não é 'pesquisa profunda' — é <b>gerar "
        "hipóteses novas e testáveis</b> a partir de um objetivo em linguagem natural. Percorra o diagrama: um "
        "<b>Supervisor</b> decompõe o objetivo e gerencia a fila; e seis agentes trabalham em três fases. "
        "<b>Gerar</b>: o Generation propõe hipóteses via debate consigo mesmo, o Proximity as agrupa num grafo. "
        "<b>Debater</b>: o Reflection critica como revisor por pares, e o Ranking roda um <b>torneio Elo</b> — "
        "cada hipótese entra com nota 1200 e disputa par a par em debate. <b>Evoluir</b>: o Evolution refina as "
        "melhores (e cria novas, em vez de mutar), e o Meta-review <b>realimenta os prompts</b> das rodadas "
        "seguintes. Agora os quatro insights que valem mais que a lista: (1) o Elo é a <b>função de aptidão</b> "
        "do sistema; (2) o grafo decide quais duelos valem a pena; (3) a evolução <b>cria em vez de mutar</b>, "
        "para não destruir o que já passou no torneio; (4) a meta-revisão é <b>aprendizado sem gradiente</b> — o "
        "sistema melhora sem ajustar um único peso, só realimentando o contexto. Amarre com o S8 (é processamento "
        "na resposta), o S25 (reconheçam os padrões: avaliador-otimizador, votação, orquestrador) e o S39 (é o "
        "AutoGen com uma função de aptidão explícita — a diferença é o Elo). <i>(~2,5 min)</i>")


def s63(prs):
    s = D._blank(prs); D.header(s, 11, "Bloco 11 · Sistemas", "A nossa replicação: QuanticaResearch")
    D.cards(s, 11, [
        ("O que MANTIVEMOS do paper (no código).", "Os 6 agentes + Supervisor em LangGraph; torneio Elo (nota inicial 1200, K=32), debate multi-turno guiado pelo grafo de proximidade; meta-revisão realimentando os prompts."),
        ("O que MUDAMOS, e por quê (aqui está a engenharia).", "LLM agnóstico de fornecedor — inclusive LOCAL (Ollama, LM Studio) — no lugar do “só Gemini”; fila durável própria (FastAPI + MariaDB) no lugar do agendador do Google; grafo de proximidade com NetworkX + Louvain."),
        ("Resultado exercitado (run UC-10).", "Rodou ponta a ponta: revisão de literatura + 4 hipóteses + 1º torneio + 1ª meta-revisão, em ~2,8 h com DeepSeek.", "good"),
        ("Honestidade: réplica funcional PRONTA PARA PILOTO, não produção.", "A sincronização com o banco ainda tem um bug conhecido (alfa).", "warn"),
    ], x=0.6, y=2.05, size=14.5)
    D.footer(s, 11, 63, TOTAL)
    reg(63, 11, "AI Co-Scientist: a sua replicação", 2.0, 112.0,
        "<b>Dois minutos mostrando que isto não é slide de PowerPoint — é sistema que roda.</b> O "
        "QuanticaResearch é uma plataforma full-stack (React, FastAPI, MariaDB) sobre um motor multiagente em "
        "LangGraph. Estruture a fala em três partes — o que você <b>manteve</b>, o que <b>mudou</b>, e o "
        "<b>porquê</b> — porque o porquê é o que demonstra engenharia, não reprodução. <b>Mantivemos</b> os seis "
        "agentes e o supervisor, o torneio Elo com nota inicial 1200, o debate par a par multi-turno guiado pelo "
        "grafo de proximidade, e a meta-revisão realimentando os prompts. <b>Mudamos</b>, e é aqui que está o "
        "trabalho: o paper é <b>exclusivamente Gemini</b> e roda no agendador interno do Google; a nossa camada "
        "de modelo é <b>agnóstica de fornecedor e roda inclusive local</b> (Ollama, LM Studio), a fila é durável "
        "e própria (FastAPI mais MariaDB), e a proximidade usa NetworkX com detecção de comunidades. E há "
        "resultado: o experimento UC-10 rodou <b>ponta a ponta</b> — literatura, quatro hipóteses, torneio e "
        "meta-revisão — em cerca de 2 horas e 48 minutos com o DeepSeek. Seja honesto sobre a maturidade: o motor "
        "roda fim a fim, mas a sincronização com o banco ainda tem um bug conhecido; apresente como <b>réplica "
        "pronta para piloto, não produção</b>. Isso é credibilidade, não fraqueza. <i>(~2 min)</i>")


def s64(prs):
    s = D._blank(prs); D.header(s, 11, "Bloco 11 · Sistemas", "A camada que amarra tudo: Redes de Petri")
    D.cards(s, 11, [
        ("VisualTasksExec: sincroniza agentes com propriedades VERIFICÁVEIS.", "Ausência de deadlock (travamento), alcançabilidade, invariantes de estado — provados na estrutura, não testados por amostragem."),
        ("Feche o arco inteiro da palestra:", "o S28 mostrou que agentes degradam de forma previsível; o S50, que gates cortam a cadeia; o S30, que nenhum protocolo expressa governança; o S62, um sistema que se autoavalia por Elo."),
        ("Mas o Elo mede qualidade de HIPÓTESE, não corretude de EXECUÇÃO.", "As Redes de Petri mostram que a estrutura da orquestração pode ser VERIFICADA FORMALMENTE — não apenas testada ou pontuada.", "good"),
    ], x=0.6, y=2.05, size=15.5)
    D.footer(s, 11, 64, TOTAL)
    reg(64, 11, "Validação por Redes de Petri", 2.5, 114.5,
        "<b>Dois minutos e meio para fechar o arco técnico da palestra inteira — deixe o argumento falar, não "
        "vire pitch.</b> As Redes de Petri são um formalismo matemático para modelar processos concorrentes. O "
        "VisualTasksExec usa isso para sincronizar agentes com <b>propriedades verificáveis</b>: ausência de "
        "travamento (deadlock), alcançabilidade de estados, invariantes — coisas que você <b>prova na "
        "estrutura</b>, não descobre testando. Agora costure o arco inteiro: o S28 mostrou que agentes degradam "
        "de forma previsível; o S50, que os portões cortam a cadeia; o S30, que nenhum protocolo do mercado "
        "expressa governança; o S62, um sistema que se autoavalia por Elo. Mas — e aqui está o remate — <b>o Elo "
        "mede qualidade de hipótese, não corretude de execução</b>. Este slide mostra que a estrutura da "
        "orquestração pode ser <b>verificada formalmente</b>, não apenas testada ou pontuada. É o nível mais alto "
        "de garantia, e é onde a engenharia de vocês pode ir além do estado da arte. <i>(~2,5 min)</i>")


# ===================== BLOCO 12 — Fechamento =====================
def s65(prs):
    s = D._blank(prs); D.header(s, 12, "Bloco 12 · Fechamento", "As três conclusões")
    D.cards(s, 12, [
        ("① A capacidade virou mercadoria comum; o método, não.", "O que separa os times é especificar e verificar — não o acesso ao modelo."),
        ("② Agente sem portão degrada de forma previsível.", "Confiabilidade vem de reduzir passos não verificados (S28, S50)."),
        ("③ A especificação executável é o que torna código de IA auditável.", "E, em software de saúde, entrega o artefato regulatório de graça (S51)."),
        ("Recomendação acionável, uma só: construam PRIMEIRO o conjunto de avaliação (S20).", "Antes de framework, antes de agente, antes de trocar de modelo.", "good"),
    ], x=0.6, y=2.05, size=16)
    D.footer(s, 12, 65, TOTAL)
    reg(65, 12, "As três conclusões", 1.5, 116.0,
        "<b>90 segundos de fechamento — retome a tese do S3 e amarre tudo.</b> Três conclusões: (1) a capacidade "
        "de gerar código virou <b>mercadoria comum</b>; o que diferencia um time é o <b>método</b>. (2) Um agente "
        "sem portão de verificação <b>degrada de forma previsível</b> — e confiabilidade vem de reduzir os "
        "passos não verificados. (3) A <b>especificação executável</b> é o que torna código de IA auditável, e "
        "em software de saúde ela entrega o artefato regulatório de graça. E então dê a eles <b>uma única "
        "recomendação acionável</b>, para saírem da sala sabendo o que fazer na segunda-feira: <b>construam "
        "primeiro o conjunto de avaliação do S20</b> — antes de escolher framework, antes de montar agente, "
        "antes de trocar de modelo. Sem esse conjunto, todo o resto é chute. <i>(~1,5 min)</i>")


def s66(prs):
    s = D._blank(prs); D.header(s, 12, "Bloco 12 · Fechamento", "Referências e contato")
    D.cards(s, 12, [
        ("Papers e specs.", "Co-Scientist: Gottweis et al., Nature 2026 (s41586-026-10644-y) / arXiv 2502.18864. Specs: MCP, A2A, OKF, GitHub Spec Kit."),
        ("Modelos.", "A tabela do S12, com os links — reconferida na semana da palestra."),
        ("Repositórios e contato.", "QR do repositório do LangNet e do QuanticaResearch; seu e-mail e perfil.", "good"),
    ], x=0.6, y=2.05, size=16.5)
    D.footer(s, 12, 66, TOTAL)
    reg(66, 12, "Referências e contato", 0.5, 116.5,
        "<b>30 segundos.</b> Deixe o slide de referências no ar enquanto respira: um QR para o repositório, os "
        "papers (o Co-Scientist na Nature), as especificações (MCP, A2A, OKF, Spec Kit), a tabela de modelos do "
        "S12 com os links, e o seu contato. Avise que os slides e o roteiro ficam disponíveis. <i>(~30 s)</i>")


def s67(prs):
    s = D._blank(prs)
    c1, c2, c3 = D.FAM['slate']
    D._rect(s, 0, 0, D.SW, D.SH, fill=c1)
    D._dot(s, -1.4, D.SH-2.2, 4.0, c2); D._dot(s, D.SW-2.2, -1.4, 3.6, c2)
    D._txt(s, 1.0, 2.6, D.SW-2, 1.4, [[("Perguntas", {"size": 52, "bold": True, "color": D.WHITE})]],
           align=PP_ALIGN.CENTER)
    D._txt(s, 1.0, 4.3, D.SW-2, 0.9,
           [[("“O gargalo deixou de ser escrever código. Passou a ser especificar e verificar.”",
              {"size": 19, "italic": True, "color": D.WHITE})]], align=PP_ALIGN.CENTER)
    D._txt(s, 1.0, 6.4, D.SW-2, 0.5, [[("Obrigado.", {"size": 16, "color": D.WHITE})]], align=PP_ALIGN.CENTER)
    D.notes(s, "Perguntas — 3,5 min.")
    reg(67, 12, "Perguntas", 3.5, 120.0,
        "<b>Três minutos e meio de perguntas — e você tem o Anexo A do planejamento com as respostas curtas "
        "prováveis.</b> Deixe a tese no rodapé do slide como âncora. Se a plateia travar, provoque com uma das "
        "perguntas frequentes (qual modelo aberto usar, CrewAI ou LangGraph, contexto de 1 milhão resolve o "
        "prontuário). Feche agradecendo e lembrando que os slides e o roteiro ficam disponíveis. <i>(~3,5 min)</i>")


def build():
    prs = D.new_prs()
    for fn in [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13,
               s14, s15, s16, s17, s18, s19, s20,
               s21, s22b, s23, s24, s25, s26, s27, s28,
               s29, s30, s31, s32, s33, s_intervalo,
               s34, s35, s36, s37, s38, s39, s40,
               s41, s42, s43,
               s44, s45, s46, s47, s48, s49, s50, s51, s52,
               s53, s54, s55, s56, s57,
               s58, s59, s60, s61, s62, s63, s64,
               s65, s66, s67]:
        fn(prs)
    out_pptx = os.path.join("output", "apresentacao_iasdd.pptx")
    prs.save(out_pptx)
    print("PPTX:", out_pptx, "slides:", len(prs.slides._sldIdLst))
    out_pdf, npng = D.render_companion_pdf(out_pptx, META,
                                           os.path.join("output", "apresentacao_iasdd_roteiro.pdf"),
                                           os.path.join("output", "_work"))
    print("PDF roteiro:", out_pdf, "paginas:", npng)


if __name__ == "__main__":
    build()
