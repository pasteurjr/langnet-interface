# -*- coding: utf-8 -*-
"""Nova apresentação: BioByte como fio condutor de IA, SDD e LangNet."""
import os
import decklib as D
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

TOTAL = 36
META = []

def reg(n, block, title, minutes, script):
    META.append({"n": n, "block": block, "title": title, "minutes": minutes,
                 "acum": sum(x["minutes"] for x in META) + minutes,
                 "script": script})

def slide(prs, block, title, kicker):
    s = D._blank(prs); D.header(s, block, kicker, title); return s

def codebox(s, code, x=0.8, y=2.1, w=11.7, h=3.7, block=0, fs=14):
    D._rect(s, x, y, w, h, fill=D.CODEBG, rounded=True, radius=0.06)
    D._txt(s, x+0.3, y+0.25, w-0.6, h-0.5,
           [[(code, {"font": D.MONO, "size": fs, "color": D.CODEFG})]],
           line_spacing=1.08)

def note(s, text): D.notes(s, text)

def s1(prs):
    s=D._blank(prs); D.cover(s, "Engenharia de IA, SDD e BioByte Sentinela",
        "Do modelo à aplicação auditável: tecnologias de IA aplicadas à vigilância de IRAS.",
        "120 minutos · desenvolvedores · especificação, agentes, tarefas, Petri nets e execução real")
    note(s, "Abertura. O BioByte será o caso condutor da palestra inteira.")
    reg(1,0,"Capa",0.5,"Apresente a tese e anuncie que as tecnologias serão demonstradas sobre o BioByte.")

def s2(prs):
    s=slide(prs,0,"A tese e o método da palestra","Bloco 0 · Abertura")
    D.quote(s,0,[("O gargalo deixou de ser escrever código. ",{"size":25,"bold":True,"color":D.FAM['indigo'][0]}),("Passou a ser especificar, orquestrar e verificar.",{"size":25,"bold":True,"color":D.FAM['sky'][0]})],y=2.1,h=1.4)
    D.cards(s,0,[("1. Entender", "modelos, contexto, ferramentas e agentes."),("2. Aplicar", "cada tecnologia ao mesmo caso BioByte."),("3. Provar", "LangNet, Rede de Petri, testes e rastreabilidade.")],y=3.9,size=18)
    note(s,"Explique a estrutura em três movimentos: fundamentos, aplicação ao BioByte e prova real.")
    reg(2,0,"Tese",2.0,"A tese organiza todo o percurso.")

def s3(prs):
    s=slide(prs,0,"Mapa da apresentação","Bloco 0 · Abertura")
    D.table(s,0,["Parte","Pergunta","Tempo"],[["1","O que são os modelos?","14 min"],["2","Como contexto e ferramentas funcionam?","12 min"],["3","Qual problema o BioByte resolve?","12 min"],["4","Como os frameworks implementam o caso?","20 min"],["5","Como o SDD organiza o desenvolvimento?","18 min"],["6","Como o LangNet executa e verifica?","17 min"],["7","O que foi demonstrado?","17 min"]],x=.8,y=2.05,w=11.7,fsize=14)
    note(s,"Não leia tudo. Mostre que haverá primeiro tecnologia, depois BioByte, depois pipeline real.")
    reg(3,0,"Mapa",2.5,"Apresente o mapa de 120 minutos.")

def s4(prs):
    s=slide(prs,1,"Transformer: a caixa que sustenta o restante","Bloco 1 · LLMs")
    D.cards(s,1,[("tokens", "texto quebrado em unidades processáveis"),("atenção", "cada posição decide de quais outras posições precisa"),("decoder-only", "o modelo prevê o próximo token"),("engenharia", "contexto, custo, latência e qualidade nascem dessa caixa")],y=2.0,size=17.5)
    note(s,"Explique apenas o necessário para conectar atenção, janela de contexto e custo.")
    reg(4,1,"Transformer",4.5,"Fundamento técnico, sem transformar a palestra em curso de arquitetura.")

def s5(prs):
    s=slide(prs,1,"Inferência também é engenharia","Bloco 1 · LLMs")
    codebox(s,'response = model.generate(\n    prompt=context + request,\n    temperature=0.0,\n    response_format=NHSNClassification\n)',w=7.0,h=2.6,fs=15)
    D.cards(s,1,[("temperatura baixa", "extração e código mais determinísticos"),("prefix caching", "reaproveita texto comum e reduz custo"),("modelo local/API", "decisão depende de privacidade, latência e operação")],x=8.15,y=2.15,w=4.2,size=14.5)
    note(s,"Conecte ao DeepSeek e ao controle de custo usado no trabalho real; confirme números no ensaio.")
    reg(5,1,"Inferência",4.0,"Mostre que o modelo é uma peça configurada, não uma caixa mágica.")

def s6(prs):
    s=slide(prs,1,"Modelos abertos, APIs e contexto","Bloco 1 · LLMs")
    D.table(s,1,["Decisão","Pergunta de engenharia","Efeito"],[["Modelo","local, API ou híbrido?","privacidade e dependência"],["Contexto","o que entra na janela?","custo e qualidade"],["Saída","texto livre ou schema?","verificabilidade"],["Adaptação","prompt, RAG ou fine-tuning?","manutenção"]],x=.8,y=2.05,w=11.7,fsize=15)
    D.callout(s,1,[("Regra: ",{"size":18,"bold":True,"color":D.FAM['sky'][0]}),("não escolha o modelo antes de definir a avaliação.",{"size":18,"color":D.INK})],y=5.5,h=.85)
    reg(6,1,"Decisões",5.5,"Resuma modelos sem transformar a palestra em ranking volátil.")

def s7(prs):
    s=slide(prs,2,"Contexto, RAG e evidência","Bloco 2 · Contexto e ferramentas")
    D._txt(s,.8,2.05,11.7,1.0,[[("documento clínico → recuperação → critério NHSN → classificação com evidência",{"size":26,"bold":True,"color":D.FAM['teal'][0]})]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    D.cards(s,2,[("RAG", "recupera a regra relevante, não um volume indiscriminado"),("evidência", "todo booleano precisa apontar para o trecho que o justifica"),("falha", "ausência de evidência é diferente de serviço indisponível")],y=3.6,size=17)
    reg(7,2,"RAG",4.0,"Use ICSAC/NHSN como exemplo de recuperação semântica com evidência.")

def s8(prs):
    s=slide(prs,2,"Saída estruturada como contrato","Bloco 2 · Contexto e ferramentas")
    codebox(s,'class NHSNClassification(BaseModel):\n    classification: Literal["confirmed", "discarded", "pending"]\n    evidence: list[str]\n    justification: str\n    confidence: float',w=8.2,h=3.0,fs=14)
    D.cards(s,2,[("não pedir", "“dê um parecer”"),("pedir", "classificação + evidência + justificativa + confiança")],x=9.3,y=2.25,w=3.1,size=14.5)
    reg(8,2,"Schema",4.0,"O schema cria uma fronteira verificável entre modelo e sistema.")

def s9(prs):
    s=slide(prs,2,"MCP: a ferramenta tem contrato","Bloco 2 · Contexto e ferramentas")
    codebox(s,'{\n  "name": "consultar_microbiologia",\n  "inputSchema": {\n    "type": "object",\n    "properties": {"paciente_id": {"type": "string"}},\n    "required": ["paciente_id"]\n  }\n}',w=7.0,h=3.5,fs=14)
    D.cards(s,2,[("modelo", "pede a chamada"),("servidor", "valida parâmetros e executa"),("sistema", "registra resultado, erro e latência")],x=8.3,y=2.2,w=4.0,size=14.5)
    reg(9,2,"MCP",4.0,"Explique MCP como interoperabilidade de ferramentas; governança continua sendo responsabilidade arquitetural.")

def s10(prs):
    s=slide(prs,3,"BioByte Sentinela: o problema real","Bloco 3 · BioByte")
    D._txt(s,.75,2.05,11.9,.75,[[("Vigilância de IRAS — foco em ICSAC",{"size":29,"bold":True,"color":D.FAM['teal'][0]})]],align=PP_ALIGN.CENTER)
    D.cards(s,3,[("risco", "priorizar pacientes com escore de Cox"),("microbiologia", "consultar hemocultura e antibiograma"),("NHSN/ICSAC", "classificar o caso com evidências"),("MDR e conduta", "alertar, recomendar bundle e registrar")],y=3.05,size=17)
    note(s,"Deixe claro: IRAS é a categoria; ICSAC é o foco clínico deste BioByte.")
    reg(10,3,"BioByte",3.5,"Apresente o domínio antes de mostrar qualquer framework.")

def s11(prs):
    s=slide(prs,3,"O fluxo clínico do BioByte","Bloco 3 · BioByte")
    D._txt(s,.8,2.1,11.7,3.2,[[("fatores de risco",{"size":21,"bold":True,"color":D.FAM['teal'][0]}),("  →  microbiologia  →  NHSN/ICSAC  →  MDR\n",{"size":21,"color":D.INK}),("  →  alerta  →  bundle/conduta  →  risco de Cox\n",{"size":21,"color":D.INK}),("  →  relatório e dashboard",{"size":21,"bold":True,"color":D.FAM['teal'][0]})]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    D.callout(s,3,[("Caso condutor: ",{"size":18,"bold":True,"color":D.FAM['teal'][0]}),("classificar um caso segundo NHSN e registrar a justificativa para revisão da CCIH.",{"size":18,"color":D.INK})],y=5.6,h=.8)
    reg(11,3,"Fluxo",3.0,"Mostre o ciclo completo, incluindo risco, microbiologia e conduta.")

def s12(prs):
    s=slide(prs,3,"UC-004 — Classificar caso segundo NHSN","Bloco 3 · BioByte")
    D.table(s,3,["Entrada","Processamento","Saída"],[["paciente, evolução, hemocultura, cateter e datas","consultar microbiologia; aplicar critérios; localizar evidências","confirmada, descartada ou pendente; justificativa e confiança"]],x=.8,y=2.25,w=11.7,h=1.35,fsize=15)
    D.cards(s,3,[("Fonte", "documento de requisitos/especificação do BioByte"),("Critério", "a saída só é válida se trouxer evidência citada"),("Próximo passo", "o mesmo contrato será implementado em vários frameworks")],y=4.15,size=17)
    reg(12,3,"Caso de uso",5.5,"Este contrato será reutilizado nos exemplos técnicos.")

def s13(prs):
    s=slide(prs,4,"O laço agêntico mínimo","Bloco 4 · Agentes")
    codebox(s,'while not done:\n    context = observe(state)\n    decision = llm(context, tools, schema)\n    if decision.calls_tool:\n        state = execute(decision.tool_call)\n    else:\n        return validate(decision.output)',w=8.1,h=3.3,fs=14)
    D.cards(s,4,[("agente", "modelo + ferramentas + ambiente"),("risco", "passos não verificados"),("controle", "schema, limite, retry e aprovação")],x=9.2,y=2.25,w=3.1,size=14.3)
    reg(13,4,"Agente",2.5,"Defina agente operacionalmente antes dos frameworks.")

def s14(prs):
    s=slide(prs,4,"LangChain no UC-004","Bloco 4 · Frameworks")
    codebox(s,'chain = (\n    prompt\n    | llm.with_structured_output(NHSNClassification)\n)\nresult = chain.invoke({\n    "patient": patient,\n    "microbiology": microbiology,\n    "criteria": icsac_criteria\n})',w=8.5,h=3.5,fs=14)
    D.cards(s,4,[("controla", "composição de componentes"),("não resolve sozinho", "durabilidade e governança"),("BioByte", "retriever + modelo + schema")],x=9.5,y=2.25,w=2.8,size=13.7)
    D.callout(s,4,[("EXEMPLO DIDÁTICO — ",{"size":14,"bold":True,"color":D.WARN}),("não é afirmação de que esta chamada isolada seja o runtime completo.",{"size":14,"color":D.INK})],y=6.0,h=.55)
    reg(14,4,"LangChain",3.0,"Mostre composição e saída estruturada.")

def s15(prs):
    s=slide(prs,4,"LangGraph no UC-004","Bloco 4 · Frameworks")
    codebox(s,'graph.add_node("consultar_microbiologia", fetch_microbiology)\ngraph.add_node("classificar_icsac", classify_case)\ngraph.add_node("validar_evidencias", validate_evidence)\ngraph.add_node("aprovar", human_review)\n\ngraph.add_edge("consultar_microbiologia", "classificar_icsac")\ngraph.add_edge("classificar_icsac", "validar_evidencias")\ngraph.add_edge("validar_evidencias", "aprovar")',w=8.5,h=3.8,fs=13.5)
    D.cards(s,4,[("controla", "estado e transições"),("ganho", "checkpoint e interrupção humana"),("BioByte", "classificação não sai sem revisão")],x=9.5,y=2.35,w=2.8,size=13.7)
    reg(15,4,"LangGraph",3.5,"Mostre o valor do estado explícito e do human-in-the-loop.")

def s16(prs):
    s=slide(prs,4,"CrewAI: agente e tarefa do BioByte","Bloco 4 · Frameworks")
    codebox(s,'nhsn_classifier_agent:\n  role: Especialista em classificação de ICSAC\n  goal: Classificar casos segundo NHSN com evidências\n\nclassify_case_nhsn:\n  agent: nhsn_classifier_agent\n  execution: agent\n  traceability: {uc: UC-004, fr: [FR-003]}\n  expected_output: classificação + evidências + justificativa',w=8.8,h=3.8,fs=13.5)
    D.cards(s,4,[("modelo mental", "organização por papéis"),("valor", "role, goal, task e expected_output"),("limite", "backstory não substitui contrato")],x=9.8,y=2.25,w=2.5,size=13.2)
    D.callout(s,4,[("EXEMPLO BASEADO NO CONTRATO DO BIOBYTE — ",{"size":13,"bold":True,"color":D.WARN}),("validar no artefato gerado antes de chamar de execução real.",{"size":13,"color":D.INK})],y=6.0,h=.55)
    reg(16,4,"CrewAI",4.0,"Este é o trecho que responde diretamente ao pedido de mostrar agent e task.")

def s17(prs):
    s=slide(prs,4,"AutoGen/AG2: classificador, revisor e humano","Bloco 4 · Frameworks")
    codebox(s,'classifier = AssistantAgent(\n  name="nhsn_classifier",\n  system_message="Classifique e cite evidências."\n)\nreviewer = AssistantAgent(\n  name="evidence_reviewer",\n  system_message="Verifique a justificativa."\n)\n\nteam = GroupChat([classifier, reviewer, human])',w=8.5,h=3.5,fs=14)
    D.cards(s,4,[("forte", "exploração e revisão conversacional"),("risco", "divergência, repetição e custo"),("controle", "limite de turnos e aprovação explícita")],x=9.5,y=2.35,w=2.8,size=13.4)
    reg(17,4,"AutoGen",3.0,"Mostre o padrão conversacional, sem sugerir que ele é automaticamente o runtime do BioByte.")

def s18(prs):
    s=slide(prs,4,"Mesmo caso, diferentes controles","Bloco 4 · Comparação")
    D.table(s,4,["Tecnologia","Controla principalmente","No UC-004"],[["LangChain","componentes","prompt + schema + retriever"],["LangGraph","estado e transições","checkpoint + aprovação"],["CrewAI","papéis e tarefas","agent + task + output"],["AutoGen/AG2","conversa","classificador + revisor"],["MCP","ferramenta","microbiologia com contrato"]],x=.65,y=2.0,w=12.0,fsize=13.5)
    D.callout(s,4,[("Pergunta correta: ",{"size":17,"bold":True,"color":D.FAM['amber'][0]}),("o que a tecnologia controla por mim e o que ela deixa para a minha arquitetura?",{"size":17,"color":D.INK})],y=5.6,h=.8)
    reg(18,4,"Comparação",2.0,"Faça a comparação pelo controle, não pela sintaxe.")

def s19(prs):
    s=slide(prs,4,"Ambientes: Claude Code, Codex e repositório","Bloco 4 · Ambientes")
    D._txt(s,.8,2.0,11.7,2.6,[[("desenvolvedor",{"size":20,"bold":True,"color":D.FAM['indigo'][0]}),("  →  Claude Code / Codex",{"size":20,"bold":True,"color":D.FAM['violet'][0]}),("  →  repositório + instruções + ferramentas\n",{"size":20,"color":D.INK}),("  →  diff + testes + hooks + revisão humana",{"size":20,"bold":True,"color":D.FAM['teal'][0]})]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    D.cards(s,4,[("unidade de trabalho", "tarefa sobre o repositório inteiro"),("não confundir", "ambiente de desenvolvimento não é o workflow clínico"),("BioByte", "ler spec, alterar artefatos e validar o resultado")],y=4.8,size=16.5)
    reg(19,4,"Ambientes",2.0,"Posicione Claude Code e Codex na camada correta.")

def s20(prs):
    s=slide(prs,5,"Intervalo","Pausa")
    D._txt(s,.8,2.4,11.7,1.2,[[ ("5 minutos",{"size":36,"bold":True,"color":D.FAM['indigo'][0]}) ]],align=PP_ALIGN.CENTER)
    D._txt(s,.8,4.0,11.7,1.0,[[ ("Na volta: a especificação do BioByte vira o contrato do pipeline.",{"size":22,"color":D.INK}) ]],align=PP_ALIGN.CENTER)
    reg(20,5,"Intervalo",5.0,"Intervalo. Conferir vídeo e conexão antes do retorno.")

def s21(prs):
    s=slide(prs,5,"Vibe coding versus SDD","Bloco 5 · SDD")
    D.table(s,5,["Sem SDD","Com SDD"],[["requisito informal → código","spec primária → plano"],["documentação atrasada","tarefas rastreáveis"],["teste pensado depois","teste derivado do critério"],["aprovação subjetiva","gate e evidência"]],x=1.0,y=2.2,w=11.2,fsize=16)
    reg(21,5,"Problema",3.0,"Retome a tese: o problema não é gerar, é provar.")

def s22(prs):
    s=slide(prs,5,"A especificação do BioByte é a fonte","Bloco 5 · SDD")
    codebox(s,'Quando uma hemocultura positiva for registrada,\no sistema deve avaliar os critérios ICSAC/NHSN\ndentro da janela definida, produzir evidência textual\ne interromper para revisão da CCIH.',w=10.8,h=2.1,fs=17)
    D.cards(s,5,[("escopo", "classificação, risco, MDR, conduta e relatório"),("não-objetivo", "aprovar automaticamente uma notificação clínica"),("aceite", "resultado reproduzível, evidência citada e revisão")],y=4.7,size=16.5)
    reg(22,5,"Spec",5.0,"Mostre um trecho real ou claramente identificado como síntese fiel da especificação.")

def s23(prs):
    s=slide(prs,5,"Do requisito ao teste","Bloco 5 · SDD")
    D._txt(s,.7,2.15,12,2.8,[[("FR/UC",{"size":22,"bold":True,"color":D.FAM['indigo'][0]}),(" → ",{"size":22,"color":D.INK}),("task",{"size":22,"bold":True,"color":D.FAM['violet'][0]}),(" → ",{"size":22,"color":D.INK}),("tool/função",{"size":22,"bold":True,"color":D.FAM['teal'][0]}),(" → ",{"size":22,"color":D.INK}),("teste",{"size":22,"bold":True,"color":D.FAM['amber'][0]}),(" → ",{"size":22,"color":D.INK}),("gate",{"size":22,"bold":True,"color":D.FAM['rose'][0]})]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    D.callout(s,5,[("Exemplo: ",{"size":18,"bold":True,"color":D.FAM['indigo'][0]}),("UC-004 → classify_case_nhsn → consultar_microbiologia → teste de evidência → revisão CCIH.",{"size":18,"color":D.INK})],y=5.5,h=.9)
    reg(23,5,"Rastreabilidade",5.0,"Demonstre a cadeia completa, não apenas o documento final.")

def s24(prs):
    s=slide(prs,5,"UI Spec e protótipo também derivam da spec","Bloco 5 · SDD")
    D.cards(s,5,[("tela", "classificação e evidências"),("estado", "loading, vazio, sucesso, erro e falha externa"),("ação", "aprovar, rejeitar, tentar novamente"),("critério", "a CCIH entende por que o sistema classificou")],y=2.1,size=18)
    D.callout(s,5,[("Heurística de experiência: ",{"size":17,"bold":True,"color":D.FAM['indigo'][0]}),("a tela deve apoiar a decisão, não apenas exibir campos.",{"size":17,"color":D.INK})],y=5.55,h=.85)
    reg(24,5,"UI Spec",5.0,"Conecte o plano de heurísticas ao pipeline sem criar uma etapa isolada de Design Thinking.")

def s25(prs):
    s=slide(prs,6,"Agents.yaml e tasks.yaml","Bloco 6 · LangNet")
    codebox(s,'nhsn_classifier_agent:\n  role: Especialista em classificação de ICSAC\n  goal: Classificar com evidências NHSN\n\nclassify_case_nhsn:\n  traceability: {uc: UC-004, fr: [FR-003]}\n  execution: agent\n  expected_output: NHSNClassification',w=8.5,h=3.8,fs=14)
    D.cards(s,6,[("agente", "papel e objetivo"),("tarefa", "contrato executável"),("rastro", "UC/FR e saída esperada")],x=9.5,y=2.35,w=2.8,size=13.8)
    reg(25,6,"Agentes e tarefas",3.5,"Mostre os artefatos reais quando disponíveis; este slide também sustenta o exemplo CrewAI.")

def s26(prs):
    s=slide(prs,6,"A Rede de Petri organiza a execução","Bloco 6 · LangNet")
    D._txt(s,.7,2.15,12,2.8,[[("P0: dados disponíveis",{"size":20,"bold":True,"color":D.FAM['indigo'][0]}),("  →  T1: consultar_microbiologia",{"size":20,"color":D.INK}),("  →  P1: microbiologia disponível\n",{"size":20,"color":D.INK}),("  →  T2: classify_case_nhsn",{"size":20,"color":D.INK}),("  →  P2: aguardando revisão CCIH",{"size":20,"bold":True,"color":D.FAM['rose'][0]})]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    D.cards(s,6,[("lugar", "estado ou sincronização"),("transição", "tarefa executável"),("token", "estado corrente do fluxo")],y=5.1,size=16.5)
    reg(26,6,"Petri",4.0,"Explique por que Petri é mais do que um desenho de workflow.")

def s27(prs):
    s=slide(prs,6,"Como um lugar chama o agente","Bloco 6 · LangNet")
    codebox(s,'Lugar / lógica JavaScript\n  → invoca tarefa ou agente\n  → backend Python\n  → WebSocket\n  → atualiza estado e interface\n  → libera a próxima transição',w=8.0,h=2.8,fs=17)
    D.cards(s,6,[("interface", "acompanha em tempo real"),("execução", "Python e ferramentas externas"),("controle", "estado, erro e retomada")],x=9.1,y=2.25,w=3.1,size=14.5)
    reg(27,6,"Execução",3.0,"Este é o alinhamento operacional que precisava aparecer na apresentação.")

def s28(prs):
    s=slide(prs,6,"Gates e rastreabilidade","Bloco 6 · LangNet")
    D._txt(s,.7,2.1,12,2.8,[[("spec",{"size":20,"bold":True,"color":D.FAM['indigo'][0]}),(" → gate → ",{"size":20,"color":D.INK}),("agentes/tarefas",{"size":20,"bold":True,"color":D.FAM['violet'][0]}),(" → gate → ",{"size":20,"color":D.INK}),("código",{"size":20,"bold":True,"color":D.FAM['teal'][0]}),(" → gate → ",{"size":20,"color":D.INK}),("teste/publicação",{"size":20,"bold":True,"color":D.FAM['rose'][0]})]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    D.cards(s,6,[("determinístico", "não confiar em outro LLM para validar tudo"),("visível", "erro tem salto e artefato identificável"),("auditável", "versão, autor, critério e resultado")],y=5.1,size=16.5)
    reg(28,6,"Gates",3.5,"Conecte a confiabilidade ao controle do pipeline.")

def s29(prs):
    s=slide(prs,6,"A arquitetura atual do ambiente","Bloco 6 · LangNet")
    D._txt(s,.6,2.0,12.1,3.7,[[("Claude Code / Codex",{"size":18,"bold":True,"color":D.FAM['indigo'][0]}),("  →  repositório + documentos\n",{"size":18,"color":D.INK}),("LangNet / Playwright",{"size":18,"bold":True,"color":D.FAM['violet'][0]}),("  →  interface, geração e execução\n",{"size":18,"color":D.INK}),("Rede de Petri",{"size":18,"bold":True,"color":D.FAM['rose'][0]}),("  →  lugares, transições e tokens\n",{"size":18,"color":D.INK}),("JavaScript → Python/WebSocket",{"size":18,"bold":True,"color":D.FAM['teal'][0]}),("  →  agentes e tarefas\n",{"size":18,"color":D.INK}),("DeepSeek / Cloud Code API",{"size":18,"bold":True,"color":D.FAM['amber'][0]}),("  →  modelo, custo e cache",{"size":18,"color":D.INK})]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    D.callout(s,6,[("Confirmar no ensaio: ",{"size":15,"bold":True,"color":D.WARN}),("modelo, endpoint/porta e métrica real antes de apresentar como fato operacional.",{"size":15,"color":D.INK})],y=6.0,h=.55)
    reg(29,6,"Ambiente atual",3.0,"Atualize este slide com os valores operacionais efetivamente usados no dia da palestra.")

def s30(prs):
    s=slide(prs,7,"O que é real e o que é demonstração didática","Bloco 7 · Prova")
    D.table(s,7,["Real no pipeline","Exemplo comparativo"],[["spec, agents/tasks, UI, Petri, código e testes BioByte","LangChain isolado"],["execução LangNet e interface","LangGraph conceitual"],["WebSocket, ferramentas e gates","CrewAI/AutoGen como alternativas"],["vídeo e rastreabilidade","trechos para explicar abstrações"]],x=.8,y=2.2,w=11.7,fsize=15)
    D.callout(s,7,[("Honestidade técnica: ",{"size":17,"bold":True,"color":D.FAM['rose'][0]}),("um exemplo de código não prova que aquela tecnologia foi usada na execução real.",{"size":17,"color":D.INK})],y=5.7,h=.8)
    reg(30,7,"Honestidade",2.0,"Evite a confusão entre alternativa didática e runtime efetivo.")

def s31(prs):
    s=slide(prs,7,"Demonstração: da especificação ao BioByte","Bloco 7 · Prova")
    D.cards(s,7,[("1", "documento de requisitos e especificação"),("2", "agentes, tarefas e UI Spec"),("3", "Rede de Petri e execução"),("4", "interface, evidência, alerta e relatório"),("5", "teste, falha real e correção"),("6", "gate de rastreabilidade")],y=2.0,size=17)
    D.callout(s,7,[("Vídeo: ",{"size":18,"bold":True,"color":D.FAM['rose'][0]}),("deixar a especificação e o gate visíveis tempo suficiente para leitura.",{"size":18,"color":D.INK})],y=5.85,h=.75)
    reg(31,7,"Vídeo",4.0,"O vídeo prova o arco completo; não inserir apenas uma tela bonita do protótipo.")

def s32(prs):
    s=slide(prs,7,"O que a demonstração precisa provar","Bloco 7 · Prova")
    D.cards(s,7,[("fonte", "a aplicação começa em uma especificação"),("execução", "as tarefas realmente rodam e atualizam estados"),("produto", "há interface, dados e resultado"),("controle", "falha e recuperação são visíveis"),("rastro", "requisito → task → código → teste")],y=2.0,size=17)
    reg(32,7,"Critério da demo",2.0,"Use estes cinco critérios para revisar o vídeo antes da palestra.")

def s33(prs):
    s=slide(prs,7,"Conclusões","Bloco 7 · Fechamento")
    D.cards(s,7,[("1", "modelos são capacidade; método é engenharia"),("2", "agentes sem gates propagam erro"),("3", "a especificação torna o código gerado rastreável"),("4", "BioByte mostra tecnologia aplicada a um problema real")],y=2.0,size=19)
    D.callout(s,7,[("Recomendação: ",{"size":18,"bold":True,"color":D.FAM['rose'][0]}),("defina primeiro o conjunto de avaliação e o contrato de saída.",{"size":18,"color":D.INK})],y=5.6,h=.8)
    reg(33,7,"Conclusões",2.0,"Retome a tese e deixe uma ação prática.")

def s34(prs):
    s=slide(prs,7,"Referências e materiais de apoio","Bloco 7 · Fechamento")
    D.cards(s,7,[("BioByte", "requisitos, casos de uso, agentes, tarefas, UI e validação"),("Tecnologias", "LangChain, LangGraph, CrewAI, AutoGen/AG2, MCP"),("Método", "SDD, rastreabilidade, gates e Redes de Petri"),("Ambientes", "Claude Code, Codex e execução pela interface")],y=2.0,size=17)
    reg(34,7,"Referências",1.0,"Apresente os materiais e indique que os detalhes ficam nos slides de backup.")

def s35(prs):
    s=slide(prs,7,"Perguntas","Bloco 7 · Fechamento")
    D._txt(s,.8,2.4,11.7,1.0,[[ ("Perguntas e discussão",{"size":34,"bold":True,"color":D.FAM['rose'][0]}) ]],align=PP_ALIGN.CENTER)
    D._txt(s,.8,4.0,11.7,1.0,[[ ("BioByte · SDD · agentes · frameworks · LangNet",{"size":21,"color":D.INK}) ]],align=PP_ALIGN.CENTER)
    reg(35,7,"Perguntas",6.0,"Reserve tempo para perguntas técnicas. Use os slides de backup conforme a direção da conversa.")

def s36(prs):
    s=slide(prs,7,"Backup: tecnologias e detalhes","Bloco 7 · Backup")
    D.cards(s,7,[("modelos", "benchmarks, licenças, DeepSeek, Qwen e modelos locais"),("protocolos", "MCP, A2A e formatos de conhecimento"),("frameworks", "detalhes adicionais de SDKs e AutoGen/AG2"),("adaptação", "RAG, SFT, LoRA, QLoRA, RLHF e DPO" )],y=2.0,size=17)
    reg(36,7,"Backup",0.0,"Slides de apoio; não entram no tempo principal salvo necessidade.")

def build():
    prs=D.new_prs()
    for fn in [s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,s14,s15,s16,s17,s18,s19,s20,s21,s22,s23,s24,s25,s26,s27,s28,s29,s30,s31,s32,s33,s34,s35,s36]:
        fn(prs)
    out=os.path.join("output","apresentacao_biobyte_sdd_v1.pptx")
    prs.save(out)
    print("PPTX:",out,"slides:",len(prs.slides),"tempo registrado:",sum(x["minutes"] for x in META),"min")
    try:
        pdf,_=D.render_companion_pdf(out,META,os.path.join("output","apresentacao_biobyte_sdd_v1_roteiro.pdf"),os.path.join("output","_work_biobyte_v1"))
        print("PDF roteiro:",pdf)
    except Exception as exc:
        print("PDF roteiro não gerado nesta máquina:", exc)

if __name__ == "__main__": build()
