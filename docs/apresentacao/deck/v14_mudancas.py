# -*- coding: utf-8 -*-
"""V14 — incremental sobre a V13 (que não é alterada).

1. "Setenta anos em um minuto" ganha uma seção própria, "Histórico da IA" (divisor só com título);
2. sai o divisor "Introdução e Machine Learning"; Machine Learning passa a ser o Bloco 1 numerado
   e sai "Onde fica a fronteira"; os demais blocos mantêm a numeração;
3. "A nossa infraestrutura" passa a se chamar "Exemplo de infraestrutura de desenvolvimento de IA local";
4. Bloco 6 passa a se chamar "Engenharia de contexto";
5. nova lâmina "Busca convencional × busca vetorial", depois da definição de RAG;
6. nova lâmina de LangChain, a primeira dos exemplos de frameworks.
"""
import copy

B6 = "Engenharia de contexto"


def _acha(S, titulo):
    for i, s in enumerate(S):
        if s.get("titulo") == titulo:
            return i
    raise KeyError(titulo)


def _s(S, titulo):
    return S[_acha(S, titulo)]


def aplicar(v13):
    S = copy.deepcopy(v13)

    # 1 e 2. Histórico da IA como seção; Machine Learning vira o Bloco 1
    del S[_acha(S, "Introdução e Machine Learning")]
    h = _acha(S, "Setenta anos em um minuto")
    S[h]["chapeu"] = "Histórico da IA"
    S.insert(h, {"tipo": "divisor_simples", "bloco": 0, "titulo": "Histórico da IA", "fala": ""})
    del S[_acha(S, "Onde fica a fronteira")]   # removida a pedido (30/09)
    ml = _acha(S, "Machine Learning")
    S[ml] = {"tipo": "divisor", "bloco": 1, "titulo": "Machine Learning",
             "mensagem": "O que é aprendizado de máquina, como se monta um projeto do início ao fim, e um algoritmo por lâmina.",
             "fala": ""}

    # 3. título da lâmina de infraestrutura local
    _s(S, "A nossa infraestrutura")["titulo"] = "Exemplo de infraestrutura de desenvolvimento de IA local"

    # 4. Bloco 6
    _s(S, "Contexto e recuperação de documentos")["titulo"] = B6
    for s in S:
        if s.get("bloco") == 6 and s.get("chapeu") == "Contexto e RAG":
            s["chapeu"] = B6

    # 5. busca convencional × busca vetorial
    r = _acha(S, "Recuperação Aumentada por Geração (RAG — Retrieval-Augmented Generation)")
    S.insert(r + 1, {
        "tipo": "figura", "bloco": 6, "chapeu": B6, "titulo": "Busca convencional × busca vetorial",
        "imagem": "diagrams_v14/busca_vetorial.png", "lado": "inteira",
        "rodape": "No RAG, o texto vira um vetor de números (embedding) e a busca é por proximidade de sentido, não por palavra igual.",
        "fala": ""})

    # 6. LangChain, antes do CrewAI
    c = _acha(S, "CrewAI: papéis, tarefas e equipe")
    S.insert(c, {
        "tipo": "codigos", "bloco": 7, "chapeu": "Frameworks", "titulo": "LangChain: peças prontas, encadeadas",
        "ideia": "Ideia central: peças prontas (prompt, modelo, recuperador, ferramenta) ligadas numa cadeia com |.",
        "paineis": [
            ("cadeia.py", 'from langchain_core.prompts import ChatPromptTemplate\nfrom langchain_core.output_parsers import StrOutputParser\nfrom langchain_openai import ChatOpenAI\n\nprompt = ChatPromptTemplate.from_template(\n    "Resuma o caso {caso} em três linhas.")\nmodelo = ChatOpenAI(model="gpt-4o-mini", temperature=0)\n\ncadeia = prompt | modelo | StrOutputParser()\nprint(cadeia.invoke({"caso": "2023-001"}))'),
            ("rag.py", 'from langchain_community.vectorstores import FAISS\nfrom langchain_core.runnables import RunnablePassthrough\n\nrecuperador = FAISS.from_documents(\n    pedacos, embeddings).as_retriever()\n\nrag = ({"contexto": recuperador,\n        "pergunta": RunnablePassthrough()}\n       | prompt_rag | modelo | StrOutputParser())\n\nrag.invoke("Qual o critério de ICS?")')],
        "fala": ""})
    # 7. panoramas atualizados (pesquisa de 29/09/2026)
    p = _s(S, "Panorama: modelos proprietários")
    p["colunas"] = ["Fabricante", "Modelo de topo", "Demais modelos da linha", "Lançamento"]
    p["linhas"] = [
        ["*OpenAI", "GPT-6 Astra", "GPT-6 Sol e GPT-6 Luna · GPT-5.6 Sol, Terra e Luna", "set/2026"],
        ["*Anthropic", "Claude Fable 5.1", "Claude Opus 5.5 · Sonnet 5.5 · Haiku 4.5 · Mythos 5.1 (acesso restrito)", "set/2026"],
        ["*Google", "Gemini 3.1 Pro", "Gemini 3 Deep Think · 3.8 Flash · 3.5 Flash-Lite · Gemini 4 anunciado", "fev e set/2026"],
        ["*xAI (Elon Musk)", "Grok 4.7", "Grok 4.6", "set/2026"],
    ]
    p["fonte"] = 13
    p["larguras"] = [2.1, 2.2, 6.3, 1.53]
    p["nota"] = ("Situação em 29 de setembro de 2026 — esta lista muda todo mês. O desempenho divulgado pelo fabricante "
                 "e o de uma medição independente divergem, às vezes muito: cite sempre a fonte e a data.")
    a = _s(S, "Panorama: modelos abertos")
    a["linhas"] = [
        ["*DeepSeek-V4.1-Flash", "552B / 8 a 16B ativos · visão", "1M", "MIT", "servidor médio"],
        ["*DeepSeek-V4-Pro", "1,6T / 49B ativos", "1M", "MIT", "cluster"],
        ["*Qwen3.8-Max (2.4T-A95B)", "2,4T / 95B ativos · multimodal", "1M", "licença própria", "cluster"],
        ["*Qwen3.8-27B", "denso 27,8B · multimodal", "262K", "Apache-2.0", "24 GB de vídeo"],
        ["*Kimi K3", "2,8T / 104B ativos", "1M", "pesos abertos", "infraestrutura séria"],
        ["*MiniMax M3", "428B / 23B ativos", "1M", "comunitária ⚠", "ver a licença"],
    ]
    return S
