# -*- coding: utf-8 -*-
"""V7: ordem conceitual corrigida e exemplos de código."""
from pathlib import Path
import sys
from pptx import Presentation
HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "apresentacao_iasdd_v7_biobyte.pptx"
sys.path.insert(0, str(HERE))
import build_deck_iasdd_v5_biobyte as old
D = old.D
f = old.v4.base.base
TOTAL = 99

def code_slide(prs, block, title, intro, code, explanation, minutes, script):
    s = D._blank(prs)
    D.header(s, block, f"Bloco {block} · Exemplo executável", title)
    D._txt(s, .65, 1.75, 12.0, .55, [[(intro, {"size": 15, "color": D.INK})]])
    D.code_block(s, code, x=.7, y=2.4, w=7.0, size=10.5)
    D.callout(s, block, [(explanation, {"size": 14, "color": D.INK})], x=8.0, y=2.45, w=4.8, h=2.8)
    D.footer(s, block, 0, TOTAL)
    old.v4.register(title, minutes, script)

def transfer(prs):
    code_slide(prs, 1, "Transfer Learning em imagens médicas",
               "Reutilizar uma rede treinada e ajustar apenas a tarefa clínica.",
               "\n".join(["base = ResNet50(weights=\"IMAGENET1K_V2\", include_top=False)",
                          "base.trainable = False", "",
                          "model = Sequential([", "    base,", "    GlobalAveragePooling2D(),",
                          "    Dense(2, activation=\"softmax\")", "])",
                          "model.fit(images, labels, epochs=10)"]),
               "A rede aprende padrões gerais; a camada final aprende a classificação específica. Depois, algumas camadas podem ser descongeladas para fine-tuning.",
               1.5,
               "Antes dos modelos de linguagem, precisamos fechar a ponte com Deep Learning. Transfer Learning reutiliza uma rede já treinada, congela suas camadas gerais e acrescenta uma cabeça específica para o problema. Em imagens médicas, isso reduz o volume de dados necessário. Depois, podemos descongelar parte da rede e fazer fine-tuning. É importante separar esse conceito do fine-tuning de modelos de linguagem, que veremos mais adiante.")

def agent_definition(prs):
    code_slide(prs, 5, "Agente: entrada, tarefa e saída",
               "Um agente é um componente que realiza uma tarefa e devolve um resultado verificável.",
               "\n".join(["result = agent.run(", "    task=\"classify_case_nhsn\",",
                          "    input={\"case_id\": \"CAS-2023-001\",", "           \"clinical_data\": case}", ")",
                          "", "assert result[\"classification\"]", "assert result[\"evidence\"]"]),
               "Modelo, contexto e tools são meios para executar a tarefa. Autonomia e laços podem existir, mas não definem sozinhos o conceito de agente.",
               1.5,
               "Aqui está a definição operacional que usaremos. Um agente recebe uma entrada, executa uma tarefa e produz uma saída verificável. Para fazer isso, ele pode usar um modelo, contexto, ferramentas e estado. Um agente não precisa ser um sistema autônomo com vários ciclos; esse é um caso mais elaborado. No BioByte, a tarefa é classificar um caso segundo critérios NHSN e devolver a classificação junto com suas evidências.")

def rag_code(prs):
    code_slide(prs, 4, "RAG com LangChain e Qdrant",
               "RAG constrói contexto externo para o agente sem alterar os pesos do modelo.",
               "\n".join(["chunks = splitter.split_documents(protocols)", "",
                          "store = Qdrant.from_documents(", "    chunks, embeddings,",
                          "    url=\"http://localhost:6333\",",
                          "    collection_name=\"protocolos_iras\"", ")", "",
                          "retriever = store.as_retriever(search_kwargs={\"k\": 4})",
                          "docs = retriever.invoke(question)",
                          "answer = chain.invoke({\"context\": docs,", "                       \"question\": question})"]),
               "LangChain compõe o pipeline; Qdrant armazena e busca vetores; os documentos recuperados entram no contexto antes da geração.",
               2.0,
               "Agora implementamos a parte de RAG. Primeiro dividimos os protocolos em unidades lógicas e geramos embeddings. O Qdrant armazena os vetores e seus metadados. Na consulta, o retriever busca os trechos mais relevantes. O LangChain conecta essa recuperação ao prompt e ao modelo. O resultado não é simplesmente uma resposta: o agente recebe documentos que podem ser citados, filtrados e validados.")

def tool_code(prs):
    code_slide(prs, 5, "Tools: ação real dentro do contexto",
               "Uma tool permite que o agente consulte ou altere um sistema externo.",
               "\n".join(["@tool", "def consultar_microbiologia(paciente_id: str,", "                            janela_dias: int) -> dict:",
                          "    \"\"\"Consulta dados microbiológicos.\"\"\"", "    return repository.find(paciente_id, janela_dias)", "",
                          "llm_with_tools = llm.bind_tools([consultar_microbiologia])"]),
               "RAG recupera conhecimento; a tool executa uma operação. O resultado da tool volta ao estado do agente.",
               1.5,
               "A tool é diferente do RAG. O RAG recupera conhecimento; a tool executa uma operação real, como consultar a microbiologia de um paciente. O contrato descreve nome, parâmetros e saída. O modelo pode solicitar a tool, mas quem a executa é o sistema. O resultado retorna ao contexto do agente, que então pode concluir a tarefa ou solicitar outra ação.")

def build():
    f.META = []
    prs = f.D.new_prs()
    funcs = [
        f.s1, f.s2, f.s3,
        lambda p: old.divider(p,1,1,"IA, Machine Learning e Deep Learning","da aprendizagem em dados à aplicação","Começamos pelo contexto mínimo necessário para entender os modelos atuais."),
        f.s4, f.s5, f.s5b, f.s5c, old.v4.ml_pipeline, old.v4.ml_evaluation, old.v4.ml_algorithms, transfer,
        lambda p: old.divider(p,2,2,"Modelos de linguagem e Transformer","o motor das aplicações generativas","Agora passamos do aprendizado em dados tabulares e imagens para a linguagem."),
        old.llm_intro, f.s6, f.s7, f.s8, f.s9, f.s10, f.s11, f.s12, f.s13, f.s14, f.s15,
        lambda p: old.divider(p,3,3,"Agentes, contexto e execução","entrada, tarefa, ferramentas e saída","Primeiro definimos agente; depois mostramos como seu contexto é construído."),
        agent_definition, old.agent_intro, f.s21, f.s22b, f.s23, f.s24, f.s25, f.s26, f.s27, f.s28,
        lambda p: old.divider(p,4,4,"Contexto, RAG e Qdrant","conhecimento externo dentro da execução","RAG é um mecanismo que alimenta o contexto do agente."),
        old.context_intro, f.s16, rag_code, f.s17, f.s18, f.s19, f.s20,
        lambda p: old.divider(p,6,6,"LangChain, LangGraph, CrewAI e AutoGen","quatro formas de compor e controlar agentes","Agora comparamos as tecnologias sobre o mesmo caso do BioByte."),
        f.s_intervalo, f.s29, f.s30, f.s31, f.s32, f.s33, f.s34, f.s35, f.s36, f.s37,
        old.v4.base.s38, old.v4.base.s39, f.s40, f.s41, f.s42, f.s43, tool_code,
        lambda p: old.divider(p,8,8,"Ambientes de desenvolvimento com IA","ferramentas que operam sobre o repositório","O ambiente muda a unidade de trabalho do desenvolvedor."),
        f.s44, f.s45, f.s46,
        lambda p: old.divider(p,9,9,"Adaptação de modelos e fine-tuning","depois do modelo de linguagem","Prompt, RAG e fine-tuning resolvem problemas diferentes."),
        old.finetune_intro, f.s56, f.s57, f.s58, f.s59, f.s60,
        lambda p: old.divider(p,10,10,"SDD: especificar antes de delegar","da intenção ao artefato verificável","A especificação organiza agentes, código, testes e rastreabilidade."),
        old.sdd_intro, f.s47, f.s48, f.s49, f.s50, f.s51, f.s52, f.s53, f.s54, f.s55,
        lambda p: old.divider(p,11,11,"BioByte, LangNet e Redes de Petri","o caso completo em execução","Agora conectamos todos os conceitos na aplicação real."),
        old.biobyte_intro, old.v4.base.s60, old.v4.base.s61, f.s62, f.s63, f.s64, f.s65, f.s66,
        lambda p: old.divider(p,12,12,"Fechamento","o que levar para a prática","A palestra termina retomando o método e abrindo para perguntas."), f.s67]
    for fn in funcs: fn(prs)
    targets={0:3,1:10,2:9,3:2,4:10,5:12,6:11,7:3,8:3,9:16,10:5,11:31,12:5}
    for block,target in targets.items():
        rows=[x for x in f.META if x["block"]==block]
        if not rows: continue
        if block==11:
            video=[x for x in rows if x["title"].startswith("DEMO")]; other=[x for x in rows if x not in video]
            if video: video[0]["minutes"]=20.0; video[0]["title"]="DEMO BioByte: 20 minutos"
            factor=(target-20)/sum(x["minutes"] for x in other)
            for x in other: x["minutes"]*=factor
        else:
            factor=target/sum(x["minutes"] for x in rows)
            for x in rows: x["minutes"]*=factor
    total=0
    for x in f.META: total+=x["minutes"]; x["acum"]=total
    prs.save(str(OUT)); old.v4.fix_text_and_numbers(OUT)
    print(f"PPTX: {OUT} slides: {len(prs.slides)} tempo: {sum(x['minutes'] for x in f.META):.2f} min")

if __name__ == "__main__": build()
