# -*- coding: utf-8 -*-
"""V11 — as 33 alterações pedidas, aplicadas sobre o conteúdo da V10 (que não é alterado).

Cada função recebe a lista da V10 (já com os cortes da V10) e devolve a lista da V11.
As falas definitivas da V11 ficam em v11_falas.py (roteiro reescrito por inteiro).
"""
import copy

DG = "diagrams_v11/"

BIO = [
    ("1988", "Graduado em Engenharia Mecânica Aeronáutica pelo ITA."),
    ("1989–1991", "Engenheiro de Sistemas na Embraer."),
    ("1991", "Analista de Sistemas na Mannesmann."),
    ("1991–2006", "Sócio-diretor da Teses."),
    ("1991–2022", "Professor Adjunto da PUC Minas."),
    ("1997", "Mestre em Ciência da Computação pela UFMG."),
    ("1999–2019", "Coordenador do curso de especialização em Engenharia de Software do IEC PUC Minas."),
    ("2001", "Criador do software ComoVou, primeiro mapa na web do Brasil, com cálculo de rotas e aplicação de técnicas clássicas de Inteligência Artificial, precursor do Waze."),
    ("2006–2017", "Sócio-diretor da Intertreck, desenvolvedora de software para rastreamento veicular."),
    ("2019", "Doutor em Tratamento da Informação Espacial pela PUC Minas."),
    ("2023–atual", "Sócio-diretor da Quântica.ai."),
    ("Ao longo da carreira", "Consultor independente para diversas empresas nas áreas de Engenharia de Software, Desenvolvimento de Software e Inteligência Artificial."),
]


def _acha(S, titulo):
    for i, s in enumerate(S):
        if s.get("titulo") == titulo:
            return i
    raise KeyError(titulo)


def _depois(S, titulo, novos):
    i = _acha(S, titulo)
    S[i + 1:i + 1] = novos


def _antes(S, titulo, novos):
    i = _acha(S, titulo)
    S[i:i] = novos


def _troca(S, titulo, novo):
    S[_acha(S, titulo)] = novo


def _mexe(S, alvo, **kw):
    s = S[_acha(S, alvo)]
    s.update(kw)
    return s


def aplicar(v10):
    S = copy.deepcopy(v10)

    # 1. biografia depois da capa
    S.insert(1, {"tipo": "bio", "bloco": 0, "chapeu": "Apresentação",
                 "titulo": "Pasteur Ottoni de Miranda Júnior", "linhas": BIO, "fala": ""})

    # 2. Machine Learning: divisor próprio + chapéu
    _antes(S, "Aprendizado supervisionado e não supervisionado",
           [{"tipo": "divisor_simples", "bloco": 1, "titulo": "Machine Learning", "fala": ""}])
    i0 = _acha(S, "Aprendizado supervisionado e não supervisionado")
    i1 = _acha(S, "O pipeline de Machine Learning, do início ao fim")
    for s in S[i0:i1 + 1]:
        s["chapeu"] = "Machine Learning"

    # 3 e 4. neurônio e rede de camadas, cada um com a sua figura
    _troca(S, "Do neurônio artificial à rede de camadas", {
        "tipo": "figura", "bloco": 3, "chapeu": "Deep Learning", "titulo": "O neurônio artificial",
        "imagem": DG + "neuronio.png", "lado": "esquerda", "larg": 7.4,
        "cartoes": [("Entradas e pesos", "cada entrada x é multiplicada pelo seu peso w."),
                    ("Soma e ativação", "a soma passa pela função f, que decide a saída y."),
                    ("O limite de um só", "um neurônio só separa o que uma reta separa.", "warn")],
        "fala": ""})
    _depois(S, "O neurônio artificial", [{
        "tipo": "figura", "bloco": 3, "chapeu": "Deep Learning", "titulo": "A rede de múltiplas camadas",
        "imagem": DG + "mlp.png", "lado": "inteira",
        "rodape": "Empilhar neurônios em camadas resolve o que um neurônio sozinho não resolve: fronteiras de qualquer formato.",
        "fala": ""}])

    # 5. CNN: a figura carrega a lâmina
    _troca(S, "Redes convolucionais: o caminho da imagem", {
        "tipo": "figura", "bloco": 3, "chapeu": "Deep Learning", "titulo": "Redes convolucionais: o caminho da imagem",
        "imagem": DG + "cnn_caminho.png", "lado": "inteira",
        "rodape": "Um filtro pequeno varre a imagem inteira. As primeiras camadas acham bordas; as seguintes, partes; as últimas, o objeto.",
        "fala": ""})

    # 6. Transfer Learning com a pilha de camadas
    _troca(S, "Transfer Learning: reaproveitar uma rede treinada", {
        "tipo": "figura", "bloco": 3, "chapeu": "Deep Learning", "titulo": "Transfer Learning: reaproveitar uma rede treinada",
        "imagem": DG + "transfer.png", "lado": "esquerda", "larg": 9.2,
        "cartoes": [("Congela", "as camadas que já sabem ver."),
                    ("Troca e treina", "só as finais, com os seus dados."),
                    ("Centenas, não milhões", "de imagens rotuladas.", "good")],
        "fala": ""})

    # vídeos: o chapéu passa a ser o tema do bloco
    for s in S:
        if s["tipo"] == "video":
            s["chapeu"] = {1: "Machine Learning", 2: "IA na saúde", 3: "Deep Learning", 4: "Modelos de linguagem",
                           5: "Agentes", 11: "LangNet"}.get(s["bloco"], "Demonstração")

    # 8. O Transformer — arquitetura visual
    _antes(S, "De onde veio o Transformer", [{
        "tipo": "figura", "bloco": 4, "chapeu": "Modelos de linguagem", "titulo": "O Transformer",
        "imagem": DG + "transformer.png", "lado": "inteira", "fala": ""}])

    # 7. Mistura de Especialistas por extenso
    s = S[_acha(S, "Escala, e o que veio com ela")]
    s["cartoes"] = [(("Mistura de Especialistas (MoE — Mixture of Experts)" if c[0] == "Mistura de especialistas" else c[0]),) + tuple(c[1:])
                    for c in s["cartoes"]]
    for k, c in enumerate(s["cartoes"]):
        if c[0].startswith("Mistura"):
            s["cartoes"][k] = (c[0], "um roteador ativa só alguns especialistas por token: trilhões de parâmetros no total, dezenas de bilhões ativos.")

    # 9. vídeo do Transformer
    _troca(S, "Tokens, atenção e geração, por dentro", {
        "tipo": "video", "bloco": 4, "chapeu": "Modelos de linguagem", "minutos": 8,
        "titulo": "Criação da estrutura de um Transformer",
        "resumo": "montando, peça por peça, a arquitetura da lâmina anterior",
        "percurso": ["Tokenização: o texto virando números",
                     "Embeddings e posição: cada token vira um vetor que sabe onde está",
                     "O bloco de atenção: consulta, chave, valor e a matriz de atenção",
                     "Rede feed-forward, soma e normalização, e os blocos empilhados",
                     "A camada de saída: a distribuição do próximo token",
                     "A estrutura pronta gerando texto, token a token"],
        "fala": ""})

    # 10. padrões de composição com diagrama
    _troca(S, "Os padrões de composição", {
        "tipo": "figura", "bloco": 5, "chapeu": "Agentes", "titulo": "Os padrões de composição",
        "imagem": DG + "padroes.png", "lado": "inteira", "alt": 4.0,
        "faixa": [("Orquestrador e executores", "um planeja, vários executam"),
                  ("Avaliador e otimizador", "um produz, outro critica"),
                  ("Autonomia com portão", "o agente decide, o código confere")],
        "fala": ""})

    # 11. RAG por extenso
    _mexe(S, "Recuperação aumentada por geração",
          titulo="Recuperação Aumentada por Geração (RAG — Retrieval-Augmented Generation)")

    # 12. tipos e técnicas de RAG
    _depois(S, "Recuperação Aumentada por Geração (RAG — Retrieval-Augmented Generation)", [{
        "tipo": "figura", "bloco": 6, "chapeu": "Contexto e RAG", "titulo": "Tipos e técnicas de RAG",
        "imagem": DG + "rag_tipos.png", "lado": "inteira", "alt": 4.1,
        "faixa": [("FAISS", "biblioteca para busca eficiente de similaridade entre vetores"),
                  ("Estratégias", "simples · multiconsulta · por grafo · agêntica"),
                  ("RAG não é uma receita única", "cada peça se escolhe pelo problema")],
        "fala": ""}])

    # 13. RAG na prática, fluxo explícito
    _troca(S, "RAG na prática, com LangChain e Qdrant", {
        "tipo": "codigo", "bloco": 6, "chapeu": "Contexto e RAG", "titulo": "RAG na prática",
        "intro": "documentos → embeddings e índice → busca → contexto → modelo → resposta",
        "codigo": '# 1. documentos\ndocs    = carregar("protocolos/")\npedacos = fatiar(docs)\n\n# 2. embeddings e indexação\nindice = FAISS.from_documents(pedacos, embeddings)\n\n# 3. busca\ntrechos = indice.similarity_search(pergunta, k=4)\n\n# 4. contexto  5. modelo  6. resposta\ncontexto = "\\n".join(t.page_content for t in trechos)\nresposta = llm.invoke(\n    f"Responda só com este contexto:\\n{contexto}\\n\\n{pergunta}")',
        "explicacao": "Cada bloco do código é uma seta do fluxo. O FAISS guarda os vetores e acha os vizinhos da pergunta; o modelo só recebe os trechos encontrados. Trocar FAISS por Qdrant ou pgvector muda uma linha.",
        "fonte": 11, "fala": ""})

    # 14 a 18. exemplos concretos de frameworks
    _depois(S, "Comparativo, e a opinião contrária", [
        {"tipo": "codigos", "bloco": 7, "chapeu": "Frameworks", "titulo": "CrewAI: papéis, tarefas e equipe",
         "ideia": "Ideia central: uma equipe de agentes com papéis, cada um recebendo tarefas, declarados em YAML.",
         "paineis": [
             ("config/agents.yaml", 'triador:\n  role: Triador de casos\n  goal: >\n    Classificar o caso pelo\n    critério da norma\n  backstory: >\n    Enfermeiro de controle\n    de infecção\n\nredator:\n  role: Redator de alertas\n  goal: Redigir o alerta\n  backstory: Comunica a equipe'),
             ("config/tasks.yaml", 'classificar:\n  description: >\n    Classifique o caso\n    {caso} pela norma\n  expected_output: >\n    JSON com critério\n    e justificativa\n  agent: triador\n\nalertar:\n  description: >\n    Redija o alerta\n  expected_output: Texto\n  agent: redator'),
             ("crew.py", '@CrewBase\nclass Vigilancia:\n  @agent\n  def triador(self):\n    return Agent(config=\n      self.agents_config["triador"])\n\n  @crew\n  def crew(self):\n    return Crew(\n      agents=self.agents,\n      tasks=self.tasks,\n      process=Process.sequential)')],
         "fala": ""},
        {"tipo": "codigos", "bloco": 7, "chapeu": "Frameworks", "titulo": "LangGraph: estado, nós e arestas",
         "ideia": "Ideia central: o fluxo é um grafo — nós são funções, arestas são transições, e o estado passa de nó em nó.",
         "paineis": [
             ("grafo.py", 'class Estado(TypedDict):\n    caso: dict\n    risco: str\n\ng = StateGraph(Estado)\ng.add_node("classificar", classificar)\ng.add_node("alertar", alertar)\ng.add_node("registrar", registrar)\n\ng.add_edge(START, "classificar")\ng.add_conditional_edges("classificar",\n    lambda e: e["risco"],          # condição\n    {"alto": "alertar", "baixo": "registrar"})\ng.add_edge("alertar", END)\ng.add_edge("registrar", END)\n\napp = g.compile()\napp.invoke({"caso": caso})')],
         "imagem": DG + "langgraph.png", "fala": ""},
        {"tipo": "codigos", "bloco": 7, "chapeu": "Frameworks", "titulo": "AutoGen: agentes que conversam",
         "ideia": "Ideia central: colaborar é conversar — um agente manda, o outro responde, até alguém encerrar.",
         "paineis": [
             ("conversa.py", 'from autogen import AssistantAgent\n\nredator = AssistantAgent("redator",\n    system_message="Escreva o resumo do caso.",\n    llm_config=cfg)\n\nrevisor = AssistantAgent("revisor",\n    system_message="Critique. Se estiver bom,\\n"\n                   "responda TERMINATE.",\n    llm_config=cfg)\n\nredator.initiate_chat(revisor,\n    message="Resumo do caso 2023-001: ...",\n    max_turns=4)')],
         "imagem": DG + "autogen.png", "fala": ""},
        {"tipo": "codigos", "bloco": 7, "chapeu": "Frameworks", "titulo": "Outros: OpenAI Agents SDK e Claude Agent SDK",
         "ideia": "O mesmo princípio: um agente com instruções e ferramentas, e um laço que roda até a resposta.",
         "paineis": [
             ("OpenAI Agents SDK", 'from agents import Agent, Runner, function_tool\n\n@function_tool\ndef escore_risco(caso_id: str) -> dict:\n    return servico.calcular(caso_id)\n\nagente = Agent(\n    name="Vigilância",\n    instructions="Avalie o risco do caso.",\n    tools=[escore_risco])\n\nr = Runner.run_sync(agente, "Caso 2023-001")\nprint(r.final_output)'),
             ("Claude Agent SDK", 'from claude_agent_sdk import query, ClaudeAgentOptions\n\nopcoes = ClaudeAgentOptions(\n    system_prompt="Avalie o risco do caso.",\n    allowed_tools=["Read", "Grep"],\n    mcp_servers={"hospital": servidor_mcp})\n\nasync for msg in query(\n        prompt="Caso 2023-001",\n        options=opcoes):\n    print(msg)')],
         "fala": ""},
    ])

    # 19. Claude Code: recursos em destaque
    _troca(S, "Claude Code: sessão de engenharia no terminal", {
        "tipo": "recursos", "bloco": 8, "chapeu": "Ambientes", "titulo": "Claude Code: sessão de engenharia no terminal",
        "intro": "O terminal vira uma sessão com contexto sobre o repositório inteiro.",
        "codigo": 'claude                  # abre a sessão\nclaude -c               # continua a última\nclaude -r <id>          # retoma uma sessão\nclaude -p "rode os testes"\n                        # não interativo\nclaude mcp add ...      # liga ferramentas\n\n/help   /compact   /resume',
        "recursos": [("Skills", "capacidades, instruções e fluxos reutilizáveis"),
                     ("Subagents", "agentes especializados para tarefas delegadas"),
                     ("Agent Teams", "conjunto de agentes e sessões coordenados"),
                     ("MCP — Model Context Protocol", "conecta ferramentas, serviços, bancos e APIs"),
                     ("Cross-session messaging", "comunicação entre sessões independentes"),
                     ("Modo não interativo", "comando, script, automação e pipeline")],
        "fala": ""})

    # 20. Codex na mesma organização
    _troca(S, "Codex: execução, revisão e saída verificável", {
        "tipo": "recursos", "bloco": 8, "chapeu": "Ambientes", "titulo": "Codex: execução, revisão e saída verificável",
        "intro": "O mesmo agente serve à exploração interativa e à automação reproduzível.",
        "codigo": 'codex                          # sessão interativa\ncodex exec "inspecione o repo" # automação\ncodex exec --json "rode as checagens"\ncodex exec --output-schema s.json "avalie"\n\n/init       # cria o AGENTS.md\n/review     # revisão do código',
        "recursos": [("AGENTS.md", "convenções do repositório como contexto reutilizável"),
                     ("Skills", "fluxos reutilizáveis ($skill-creator cria uma)"),
                     ("MCP — Model Context Protocol", "conecta ferramentas e serviços externos"),
                     ("Modo exec", "não interativo: script, automação e pipeline"),
                     ("Saída verificável", "eventos em JSON e resposta presa a um esquema"),
                     ("Sandbox e aprovações", "o que o agente pode fazer sem pedir licença")],
        "fala": ""})

    # 21. mapa com OKF no eixo horizontal
    _troca(S, "O mapa: vertical e horizontal", {
        "tipo": "figura", "bloco": 9, "chapeu": "Protocolos", "titulo": "O mapa: vertical e horizontal",
        "imagem": DG + "protocolos_okf.png", "lado": "inteira", "fala": ""})

    # 22. SDD por extenso
    _mexe(S, "Desenvolvimento Orientado a Especificação",
          titulo="Specification-Driven Development (SDD)",
          mensagem="Desenvolvimento Orientado a Especificação: especificar antes de delegar. A especificação é o que se versiona; o código é o que se regenera.")

    # 23. Vibe Coding × SDD
    _troca(S, "O problema", {
        "tipo": "figura", "bloco": 10, "chapeu": "SDD", "titulo": "O problema: Vibe Coding",
        "imagem": DG + "vibe_sdd.png", "lado": "inteira", "alt": 3.75,
        "mensagem": "O SDD permite utilizar a velocidade e a produtividade do desenvolvimento assistido por IA sem transformar o desenvolvimento em um Vibe Coding desorganizado.",
        "fala": ""})

    # 24. rastreabilidade sem identificadores artificiais
    _troca(S, "Da especificação ao código, e a rastreabilidade", {
        "tipo": "figura", "bloco": 10, "chapeu": "SDD", "titulo": "Da especificação ao código, e a rastreabilidade",
        "imagem": DG + "rastreabilidade.png", "lado": "inteira", "alt": 3.6,
        "faixa": [("O teste nasce do critério", "não do código — por isso não herda os defeitos dele"),
                  ("Mudou o requisito?", "o rastro mostra tudo o que precisa ser refeito")],
        "fala": ""})

    # 25. título do bloco 11
    _mexe(S, "LangNet e BioByte", titulo="LangNet: um framework para SDD automatizado",
          mensagem="O processo do bloco anterior, implementado e automatizado — e um exemplo completo produzido por ele.")

    # 26. fábrica e máquina
    _troca(S, "Dois lados: a fábrica e a máquina", {
        "tipo": "figura", "bloco": 11, "chapeu": "LangNet", "titulo": "Dois lados: a fábrica e a máquina",
        "destaque": "O LangNet é uma aplicação que fabrica aplicações dentro do padrão SDD.",
        "imagem": DG + "fabrica_maquina.png", "lado": "inteira", "alt": 3.3,
        "faixa": [("O que liga os dois", "a rede de Petri sai da fábrica e vira o plano de execução"),
                  ("Defeito se corrige na fábrica", "e se regera — nunca no artefato final", "warn")],
        "fala": ""})

    # 27. documento aos requisitos
    _troca(S, "Do documento aos requisitos", {
        "tipo": "figura", "bloco": 11, "chapeu": "Etapas", "titulo": "Do documento aos requisitos",
        "imagem": DG + "requisitos.png", "lado": "inteira", "alt": 4.1,
        "faixa": [("Explícitos", "extraídos do que está escrito"),
                  ("Inferidos", "o que o sistema precisa e ninguém escreveu"),
                  ("Procedência", "cada requisito diz de onde veio", "good")],
        "fala": ""})

    # ferramentas: tira a menção antecipada ao exemplo
    s = S[_acha(S, "Ferramentas, agentes e tarefas")]
    s["cartoes"] = [c if c[0] != "No BioByte" else
                    ("Serviço externo", "uma ferramenta pode ser um serviço publicado por um servidor MCP, com contrato de entrada e saída.")
                    for c in s["cartoes"]]

    # 28. Petri, visual
    _troca(S, "A rede de Petri: a orquestração verificável", {
        "tipo": "figura", "bloco": 11, "chapeu": "Etapas", "titulo": "A rede de Petri: a orquestração verificável",
        "imagem": DG + "petri.png", "lado": "inteira", "alt": 4.55,
        "rodape": "A rede representa e sincroniza as tarefas: dependências, paralelismo e pontos de encontro. O token caminha e mostra onde a execução está.",
        "fala": ""})

    # 29. testes: grafo de causa-efeito + caso gerado
    _troca(S, "Casos de teste e geração do código", {
        "tipo": "codigos", "bloco": 11, "chapeu": "Etapas", "titulo": "Casos de teste e geração do código",
        "ideia": "Causas são o que chega; efeitos, o que o sistema responde. Cada combinação vira um caso de teste.",
        "imagem": DG + "causa_efeito.png", "imagem_esq": True,
        "paineis": [("caso de teste gerado", 'TC-UC-011-03   (caso de uso UC-011)\n\ndado que\n  c1 antibiograma disponível        = sim\n  c4 lista de antimicrobianos       = sim\n  c6 agente interpreta sem falha    = sim\n  c7 3 ou mais classes resistentes  = sim\n\nentão\n  e3 Multirresistente = Sim,\n     com as classes e a contagem')],
        "nota": "Depois dos testes, a geração: telas, backend, banco, agentes, ferramentas e o executor da rede — e o portão confere se cada tarefa chegou ao código.",
        "fala": ""})

    # 30. introdução do exemplo BioByte
    _troca(S, "O que foi medido, e o que ainda é lacuna", {
        "tipo": "cartoes", "bloco": 11, "chapeu": "Exemplo", "titulo": "O exemplo: BioByte",
        "destaque": "Vigilância de infecção hospitalar, do documento do cliente à aplicação rodando.",
        "cartoes": [("Contexto", "a comissão de controle de infecção acompanha pacientes com cateter e resultados de hemocultura, ainda à mão."),
                    ("A especificação", "casos de uso para cadastrar o caso, importar o antibiograma, classificar pela norma, identificar multirresistência e alertar."),
                    ("Requisitos gerais", "cadastros e relatórios convencionais; decisões clínicas feitas por agentes, sempre com a justificativa gravada."),
                    ("Escopo", "microbiologia e escore de risco por serviços externos; alerta à equipe; relatório para a comissão."),
                    ("O que vamos ver", "o LangNet percorrendo as etapas com esse documento, até a aplicação rodando.", "good")],
        "corpo": 15.5, "fala": ""})
    s = S[_acha(S, "O pipeline completo do LangNet, do documento à aplicação")]
    s["percurso"] = [p.replace("O documento do hospital entrando", "O documento do BioByte entrando") for p in s["percurso"]]

    # 31. fechamento limpo
    _mexe(S, "Fechamento", tipo="divisor_simples")
    s = S[_acha(S, "As três conclusões")]
    s["cartoes"] = [c for c in s["cartoes"] if c[0] != "Por onde começar"]
    for s in S:
        if s["tipo"] == "encerramento":
            s["tipo"] = "encerramento_limpo"
    return S
