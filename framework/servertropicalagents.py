import json
import os
from flask import Flask
from flask_socketio import SocketIO, emit
import torch
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from openai import OpenAI
from datetime import datetime
import uuid
from flask_cors import CORS
from tropicalagents import teamanalysisdbuser,production_efficiency_analisys_team,teamanalysisuser,teamanalysisdbuser
from tropicalagentssales import response_generator_team

from flask import Flask, jsonify, request

from celery_app import celery_app
import time

# Configurações
DEEPSEEK_KEY = "sk-6bd3d09d2fd441c0a14f767e38d9a3c5"
FAISS_INDEX_PATH = "faiss_index_tropical"

# Inicializar Flask e SocketIO
app = Flask(__name__)
CORS(app)









# Carregar embeddings e índice FAISS
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
)
vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)

# Configurar cliente +
# +-
# +pSeek
client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")

# Dicionário para armazenar sessões em memória
sessoes = {}

# Função para enviar mensagens ao DeepSeek e atualizar a memória
def deepseek_chat(prompt, memory, model="deepseek-chat", temperature=0.7, max_tokens=2048):
    try:
        # Adiciona a mensagem do usuário ao histórico
        memory.append({"role": "user", "content": prompt})

        # Envia o histórico completo para o DeepSeek
        response = client.chat.completions.create(
            model=model,
            messages=memory,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )

        # Adiciona a resposta do assistente ao histórico
        assistant_reply = response.choices[0].message.content
        memory.append({"role": "assistant", "content": assistant_reply})

        return assistant_reply
    except Exception as e:
        return f"Erro ao chamar a API do DeepSeek: {e}"

# Configuração dos agentes
def agente_tropical(data, memory):
    question = data.get("question")
    if not question:
        return "Erro: Este agente requer o parâmetro 'question'."
    
    # Busca documentos relevantes
    docs = vectorstore.similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Formata o prompt com o contexto e a pergunta
    prompt_template = """
    Você é um assistente especializado em responder perguntas relacionadas à empresa Plásticos Tropical.

    1. Compare a pergunta {question} com todas as instructions fornecidas no contexto.
    2. Priorize correspondências exatas ou altamente similares na identificação da instruction relevante.
    3. Retorne a response correspondente à instruction mais similar.
    4. Caso não encontre uma correspondência exata ou próxima nas instructions, compare a pergunta com as responses, buscando similaridades que possam ajudá-lo a formular a resposta
    4. Caso não encontre uma correspondência exata ou próxima no contexto, responda com base na sua base de conhecimento, fora dos embeddings.
    5. Responda de forma objetiva e clara, não énecessário tecer observações informando que a resposta tem ou não tem correspondência exata com o contexto da empresa, portanto forneça apenas a resposta.
    6- A resposta pode estar também em Instructions, portanto, se não encontrar correspondência, responda analisando as instructions. Por exemplo, perguntas envolvendo nomes de moldes, de produtos da tropical, máquinas, podem ser obtidas pela análise das instructions
    7. Responda também a perguntas que não tenham a ver com o contexto da empresa Plásticos Tropical
    8. Se for solicitado em {question},produza a resposta em formato markdown, bem formatada e estruturada, mas sem a marcação ```markdown
    Contexto:
    {context}

    Pergunta: {question}
    Resposta:
    """
    formatted_prompt = prompt_template.format(context=context, question=question)
    
    # Obtém a resposta usando a função deepseek_chat
    resposta = deepseek_chat(formatted_prompt, memory)
    
    return resposta

def agente_generico(data, memory):
    question = data.get("question", "Consulta genérica")
    prompt = f"Responda a seguinte pergunta de forma genérica: {question}"
    return deepseek_chat(prompt, memory)


@celery_app.task
def agente_monitoramento_emails():
    try:
        input_data = {"max_emails": 5}
        result = response_generator_team.executar(inputs=input_data)
        result_str = str(result).replace("'", '"')
        print(f"*****RESULTSTR={str(result_str)}")
        result_dict = json.loads(result_str)
        return result_dict['team_result']
    except Exception as e:
        return f"Erro ao processar monitoramento de emails: {e}"




@celery_app.task
def agente_monitoramento_eficiencia():
    """Agente que monitora a eficiência da produção"""
    print("*********AGENTE MONITORAMENTO EFICIENCIA************")
    try:
        # Simula a execução do crew (substitua pelo seu código real)
        input_data = {"memory_system": {}, "max_regs": 5}
        result = production_efficiency_analisys_team.executar(inputs=input_data)
        result_str = str(result)
        print(f"*****RESULTSTR={result_str}")

        # Extrai os valores das chaves
        result_dict = json.loads(result_str)
        print(f"*****RESULdict={result_dict}")
        html_report = result_dict.get("html", None)

        return html_report
    except Exception as e:
        return f"Erro ao processar monitoramento: {e}"

@celery_app.task
def agente_teamanalysisuser(question, analises):
    
    print("*********AGENTE CONSULTA POR LINGUAGEM NATURAL E FAZ ANALISE SOLICITADA PELO USUÁRIO************")
    try:
        result = teamanalysisuser.executar({
            "question": question,
            "analises_a_fazer": analises
        })
        

        return result
    except Exception as e:
        return f"Erro ao processar agente: {e}"

@celery_app.task
def agente_teamanalysisdbuser(query, analises):
    
    print("*********AGENTE EXECUTA QUERY E FAZ ANALISE SOLICITADA PELO USUÁRIO************")
    try:
        result = teamanalysisdbuser.executar({
            "query": query,
            "analises_a_fazer": analises
        })
        

        return result
    except Exception as e:
        return f"Erro ao processar agente: {e}"


# Adicione no início do arquivo, após os imports
#Agora apenas os web services

# Agente de teste
@celery_app.task
def agente_teste():
    """Agente de teste que retorna um código HTML fixo."""
    html_fixo = """
    <div style="border: 1px solid #ccc; padding: 10px; margin: 10px;">
        <h3>Resposta do Agente de Teste</h3>
        <p>Este é um exemplo de resposta HTML fixa.</p>
    </div>
    """
    return html_fixo

# Rota HTTP para processar tarefas
@app.route("/processar", methods=["POST"])
def processar():
    print("**********´PROCESSANDO***********")
    # Envia a tarefa para o Celery
    task = agente_teste.delay()
    
    # Retorna o ID da tarefa para o cliente
    return jsonify({"task_id": task.id}), 202

@app.route("/processar_monitoramento", methods=["POST"])
def processar_monitoramento():
    print("**********PROCESSANDO MONITORAMENTO***********")
    # Dados para a tarefa (pode ser ajustado conforme necessário)
    

    # Envia a tarefa para o Celery
    task = agente_monitoramento_eficiencia.delay()
    
    # Retorna o ID da tarefa para o cliente
    return jsonify({"task_id": task.id}), 202


@app.route("/processar_emails", methods=["POST"])
def processar_emails():
    print("**********PROCESSANDO MONITORAMENTO***********")
    # Dados para a tarefa (pode ser ajustado conforme necessário)
    

    # Envia a tarefa para o Celery
    task = agente_monitoramento_emails.delay()
    
    # Retorna o ID da tarefa para o cliente
    return jsonify({"task_id": task.id}), 202

@app.route("/processar_agente_teamanalysisuser", methods=["GET"])
def processar_agente_teamanalysisuser():
    print("**********PROCESSANDO ANALISE NL***********")
    # Dados para a tarefa (pode ser ajustado conforme necessário)
    question = request.args.get("question")
    analises = request.args.get("analises")
    if not question or not analises:
        return jsonify({"error": "Os parâmetros 'question' e 'analises' são obrigatórios"}), 400
    
    

    # Envia a tarefa para o Celery
    task = agente_teamanalysisuser.delay(question, analises)
    
    # Retorna o ID da tarefa para o cliente
    return jsonify({"task_id": task.id}), 202

@app.route("/processar_agente_teamanalysisdbsuser", methods=["GET"])
def processar_agente_teamanalysisdbuser():
    print("**********PROCESSANDO ANALISE NL***********")
    # Dados para a tarefa (pode ser ajustado conforme necessário)
    query = request.args.get("query")
    analises = request.args.get("analises")
    if not query or not analises:
        return jsonify({"error": "Os parâmetros 'query' e 'analises' são obrigatórios"}), 400
    
    

    # Envia a tarefa para o Celery
    task = agente_teamanalysisdbuser.delay(query, analises)
    
    # Retorna o ID da tarefa para o cliente
    return jsonify({"task_id": task.id}), 202

# Rota HTTP para verificar o status da tarefa
from celery.result import AsyncResult
@app.route("/status/<task_id>", methods=["GET"])
def status(task_id):
    print(f"*****************************************TASK ID={task_id}")
    # Obtém o resultado da tarefa
    task = AsyncResult(task_id)
    if task.ready():
        return jsonify({"status": "completed", "result": task.result})
    else:
        return jsonify({"status": "pending"})





from threading import Event
background_tasks = {}
#Web Sockets


socketio = SocketIO(app, cors_allowed_origins="*")
# Adicione uma função para limpar quando a sessão terminar
@socketio.on('disconnect')
def handle_disconnect():
    for session_id in background_tasks:
        background_tasks[session_id].set()
    background_tasks.clear()
    
agents = {
    0: {"name": "Monitor de Eficiência", "process": agente_monitoramento_eficiencia},
    1: {"name": "Chat Tropical", "process": agente_tropical},
    2: {"name": "Agente Genérico", "process": agente_generico},
}


@socketio.on("iniciar_sessao")
def iniciar_sessao():
    print("*********INICIOU SESSAO************")
    session_id = str(uuid.uuid4())
    sessoes[session_id] = {
        "memory": [],
        "ultimo_acesso": datetime.now(),
        "agent_id": None
    }
    emit("sessao_iniciada", {"session_id": session_id})

@socketio.on("selecionar_agente")
def selecionar_agente(data):
    print("*********SELECIONAR AGENTE************")
    session_id = data.get("session_id")
    print(f"*****************Session_id={session_id}")
    agent_id = data.get("agent_id")
    print(f"*****************Agent_id={agent_id}")

    if session_id is None or agent_id is None:
        print(f"erro session_id e agent_id são obrigatórios")
        emit("erro", {"mensagem": "session_id e agent_id são obrigatórios"})
        return

    if session_id not in sessoes:
        print("erro Sessão não encontrada")
        emit("erro", {"mensagem": "Sessão não encontrada"})
        return

    if agent_id not in agents:
        print("erro: Agente nao encontrado")
        emit("erro", {"mensagem": "Agente não encontrado"})
        return

    sessoes[session_id]["agent_id"] = agent_id
    print(f"agente_selecionado:{agent_id}")
    emit("agente_selecionado", {"agent_id": agent_id})

@socketio.on("processar_agente")
def processar_agente(data):
    print("*********PROCESSAR AGENTE************")
    session_id = data.get("session_id")

    if  session_id is None:
        emit("erro", {"mensagem": "session_id é obrigatório"})
        return

    if session_id not in sessoes:
        emit("erro", {"mensagem": "Sessão não encontrada"})
        return

    agent_id = sessoes[session_id].get("agent_id")
    print(f"*********AGENT ID={agent_id}")
    if  agent_id is None or agent_id not in agents:
        emit("erro", {"mensagem": "Agente não selecionado ou inválido"})
        return

    # Processa a mensagem com o agente apropriado
    agent = agents[agent_id]
    
    if agent_id == 1:
        question = data.get("question")
        if not question:
            emit("erro", {"mensagem": "question é obrigatório para este agente"})
            return
        resposta = agent["process"](data, sessoes[session_id]["memory"])

    # Atualiza o último acesso
    sessoes[session_id]["ultimo_acesso"] = datetime.now()
    
    emit("nova_resposta", {"resposta": resposta})







if __name__ == "__main__":
    print("Servidor rodando em http://127.0.0.1:6064")
    socketio.run(app, host='127.0.0.1', port=6064, debug=True)