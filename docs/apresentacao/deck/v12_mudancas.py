# -*- coding: utf-8 -*-
"""V12 — alterações incrementais sobre a V11 (que não é alterada).

1. saem as duas lâminas de abertura ("O caminho de hoje" e "A tese"); entra o sumário com os doze
   blocos; o histórico da IA ("Setenta anos em um minuto") vem logo depois, em Fundamentos;
2. o bloco de IA na saúde passa para depois de Deep Learning (os números dos blocos 2 e 3 trocam);
3. a rede de múltiplas camadas usa a figura da apresentação-base (slide 118, Backpropagation – Simulação);
4. "De onde veio o Transformer" antes de "O Transformer";
5. Bloco 8 passa a se chamar "Agentes para produção de código";
6. volta a lâmina que explica os protocolos um a um (conteúdo da V10 + OKF), antes do mapa;
7. o mapa fica como está;
+ o vídeo final do LangNet passa a ter 10 minutos (roteiro v11 do vídeo).
"""
import copy

B8 = "Agentes para produção de código"


def _acha(S, titulo):
    for i, s in enumerate(S):
        if s.get("titulo") == titulo:
            return i
    raise KeyError(titulo)


def _s(S, titulo):
    return S[_acha(S, titulo)]


def aplicar(v11):
    S = copy.deepcopy(v11)

    # 1. abertura: saem "O caminho de hoje" e "A tese"; entra o sumário da apresentação;
    #    "Setenta anos em um minuto" (o histórico da IA) vem logo depois, em Fundamentos,
    #    antes do Bloco 1; "Onde fica a fronteira" continua abrindo o Bloco 1.
    for t in ("O caminho de hoje", "A tese"):
        del S[_acha(S, t)]
    hist = S.pop(_acha(S, "Setenta anos em um minuto"))
    hist["chapeu"] = "Fundamentos"
    hist["bloco"] = 0
    i = _acha(S, "Pasteur Ottoni de Miranda Júnior")
    S[i + 1:i + 1] = [{"tipo": "agenda", "bloco": 0, "chapeu": "Apresentação",
                       "titulo": "Conteúdo da apresentação", "fala": ""}, hist]

    # 2. IA na saúde depois de Deep Learning (bloco 3 vira 2, bloco 2 vira 3)
    a = _acha(S, "Inteligência Artificial na saúde")
    b = _acha(S, "Classificação e apoio à decisão em saúde")
    saude = S[a:b + 1]
    del S[a:b + 1]
    fim_dl = _acha(S, "Treinamento e Transfer Learning")
    S[fim_dl + 1:fim_dl + 1] = saude
    for s in S:
        if s.get("bloco") == 2:
            s["bloco"] = -3
        elif s.get("bloco") == 3:
            s["bloco"] = 2
    for s in S:
        if s.get("bloco") == -3:
            s["bloco"] = 3

    # 3. rede de múltiplas camadas com a figura da apresentação-base
    m = _s(S, "A rede de múltiplas camadas")
    m.update({"tipo": "figura_rotulos", "imagem": "diagrams_v12/mlp_original.png",
              "rotulos": [("Camada de entrada", 0.21), ("Camadas ocultas", 0.53), ("Camada de saída", 0.86)],
              "rodape": "Entradas à esquerda, duas camadas ocultas no meio, a saída à direita. Cada seta é uma conexão com o seu peso (W¹, W², W³)."})

    # 4. "De onde veio o Transformer" antes de "O Transformer"
    t = S.pop(_acha(S, "De onde veio o Transformer"))
    S.insert(_acha(S, "O Transformer"), t)

    # 5. Bloco 8
    d = _s(S, "Ambientes de geração de código")
    d["titulo"] = B8
    for s in S:
        if s.get("bloco") == 8 and s.get("chapeu") == "Ambientes":
            s["chapeu"] = B8

    # 6. protocolos explicados um a um, antes do mapa (conteúdo da V10 + OKF)
    S.insert(_acha(S, "O mapa: vertical e horizontal"), {
        "tipo": "cartoes", "bloco": 9, "chapeu": "Protocolos", "titulo": "Os protocolos: MCP, A2A e OKF",
        "destaque": "Três contratos abertos: com ferramentas, com outros agentes e com o conhecimento.",
        "cartoes": [
            ("MCP — Model Context Protocol", "liga agentes e modelos a ferramentas, dados, sistemas e APIs. Um servidor MCP publica cada ferramenta com nome, parâmetros e esquema de retorno."),
            ("A2A — Agent2Agent", "comunicação e interoperabilidade entre agentes: descoberta de capacidades, delegação de tarefa e acompanhamento."),
            ("OKF — Open Knowledge Format", "formato aberto para estruturar e trocar conhecimento, legível por agentes e por pessoas."),
            ("Por que isso importa", "a ferramenta, o agente e o conhecimento deixam de ser código colado e passam a ser serviços com contrato, reaproveitáveis e versionáveis.", "good")],
        "corpo": 15.5, "fala": ""})

    # vídeo final do LangNet: 10 minutos, roteiro v11 do vídeo
    v = _s(S, "O pipeline completo do LangNet, do documento à aplicação")
    v["minutos"] = 10
    v["resumo"] = "todas as etapas do pipeline, e o sistema gerado rodando"
    v["percurso"] = ["O documento do cliente e o documento de requisitos, com a procedência de cada item",
                     "A especificação: o caso de uso, as exceções, o esquema da tela — e a versão dois",
                     "O modelo de dados corrigido por conversa, e a comparação entre versões",
                     "A tela e o protótipo, editados e vistos ao mesmo tempo",
                     "Agentes, ferramentas, YAML, sequência, rede de Petri, código e testes",
                     "O sistema gerado: a tela do agente, a rede de Petri executando e a tela da tarefa"]
    return S
