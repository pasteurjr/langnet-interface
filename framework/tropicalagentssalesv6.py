# tropicalagentssalesv6.py
# v6: Adaptado para Context State List da Petri Net colorida  
#     Baseado no tropicalagentssalesv5.py com modificações para suportar context_state_list
#
# Principais mudanças V5 → V6:
#   - Context State List aware: Funciona com lista de states da Petri Net
#   - Input/Output functions adaptadas para extrair dados da lista
#   - Compatível com WebSocket V3 genérico
#   - Mantém TropicalSalesState como base, mas acessa via context_state_list

from __future__ import annotations
import os
import sys
import json
import yaml
from pathlib import Path
from typing import TypedDict, Optional, Callable, Any, Dict, List
from datetime import datetime

# Caminho do framework
sys.path.append('../framework')
sys.path.append('/home/pasteurjr/progpython/valep1/visualtasksexec/framework')

from frameworkagentsadapterv4 import FrameworkAdapterFactory

# Dotenv (opcional)
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except Exception:
    pass

# ---------------------------------------------------------------------
# 1) Adapters e aliases do framework CrewAI  
# ---------------------------------------------------------------------
adapters = FrameworkAdapterFactory.get_framework_adapters(version="crewai")
ToolClass = adapters["tool"]

# Importar CrewAI diretamente
from crewai import Agent as AgentClass
from crewai import Task as TaskClass
from crewai import Crew as TeamClass

# Modelo de LLM padrão
DEFAULT_LLM = os.getenv("DEFAULT_LLM", "gpt-4o-mini")

# 🎭 MOCK MODE: Usar verificação de estoque mock (sem MindsDB) ou real
# True = Mock (sempre retorna estoque disponível 1000)
# False = Real (usa MindsDB com natural_language_check_stock agent)
USARMOCKESTOQUE = True

# ---------------------------------------------------------------------
# 2) Carregamento de YAMLs
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
agents_config = yaml.safe_load((BASE_DIR / "agents.yaml").read_text())
tasks_config  = yaml.safe_load((BASE_DIR / "tasks.yaml").read_text())

# ---------------------------------------------------------------------
# 3) Context State para TropicalSales (INALTERADO - Base do LangGraph)
# ---------------------------------------------------------------------
class TropicalSalesState(TypedDict, total=False):
    # Configuração inicial
    max_emails: int
    
    # Task outputs (JSONs das tasks)
    emails_json: str                    # read_email output
    classified_json: str                # classify_message output  
    stock_checked_json: str             # check_stock_availability output
    response_report_md: str             # generate_response output
    
    # Dados estruturados (para facilitar parsing)
    emails_data: Dict[str, Any]         # Parsed emails_json
    classification_data: Dict[str, Any]  # Parsed classified_json
    stock_data: Dict[str, Any]          # Parsed stock_checked_json
    response_data: Dict[str, Any]       # Parsed response_report_md
    
    # Metadados de execução
    execution_log: List[Dict[str, Any]]
    current_task: Optional[str]
    timestamp: str

# ---------------------------------------------------------------------
# 4) Ferramentas (Tools) - INALTERADO
# ---------------------------------------------------------------------
email_fetch_tool = ToolClass(
    name="Email Fetch Tool",
    description="Connects to IMAP and fetches unread emails.",
    tool_type="emailfetchtool",
    tool_config={
        "server":   os.getenv("SMTP_HOST"),
        "email":    os.getenv("EMAIL_USERNAME"),
        "password": os.getenv("EMAIL_PASSWORD"),
    },
).create()[0]

email_send_tool = ToolClass(
    name="Email Send Tool",
    description="Sends email replies via SMTP.",
    tool_type="emailsendtool",
    tool_config={
        "server":   os.getenv("SMTP_HOST"),
        "email":    os.getenv("EMAIL_USERNAME"),
        "password": os.getenv("EMAIL_PASSWORD"),
    },
).create()[0]

# 🎭 Condicional: Mock ou Real baseado em USARMOCKESTOQUE
if USARMOCKESTOQUE:
    print("⚠️ [MOCK MODE] Usando verificação de estoque MOCK (sem MindsDB)")
    natural_language_query_stock_tool = ToolClass(
        name="Natural Language Query Stock Tool (MOCK)",
        description="This tool receives a question about product stock in natural language and returns mock stock availability (always available with 1000 units)",
        tool_type="naturallanguagestockcheckertoolmock",
        tool_config={},
    ).create()[0]
else:
    print("✅ [REAL MODE] Usando verificação de estoque com MindsDB")
    natural_language_query_stock_tool = ToolClass(
        name="Natural Language Query Stock Tool",
        description="This tool receives a question about product stock in natural language, transforms it to SQL query and execute the query, returning the results",
        tool_type="naturallanguagestockcheckertool",
        tool_config={
            "database_url": os.getenv("DATABASE_URL", "sqlite:///tropical_stock.db"),
            "table_name": "products",
        },
    ).create()[0]

# Classification será feita via LLM do agent, não precisa de tool específica
classification_tool = None

# ---------------------------------------------------------------------
# 5) Agentes - INALTERADO
# ---------------------------------------------------------------------
def get_llm_instance():
    """Retorna instância do LLM baseado na configuração"""
    return DEFAULT_LLM

email_reader_agent = AgentClass(
    config=agents_config['email_reader_agent'],
    llm=get_llm_instance(),
    verbose=True,
    allow_delegation=False
)

classifier_agent = AgentClass(
    config=agents_config['classifier_agent'],
    llm=get_llm_instance(),
    verbose=True,
    allow_delegation=False
)

stock_checker_agent = AgentClass(
    config=agents_config['stock_checker_agent'],
    llm=get_llm_instance(),
    verbose=True,
    allow_delegation=False
)

response_generator_agent = AgentClass(
    config=agents_config['response_generator_agent'],
    llm=get_llm_instance(),
    verbose=True,
    allow_delegation=False
)

# ---------------------------------------------------------------------
# 6) Input/Output Functions V6 - ADAPTADAS PARA CONTEXT STATE LIST
# ---------------------------------------------------------------------

def read_email_input_func(state: TropicalSalesState) -> Dict[str, Any]:
    """V6: Extrai max_emails do context state (primeira task - configuração inicial)"""
    return {"max_emails": state.get("max_emails", 5)}

def read_email_output_func(state: TropicalSalesState, result: Any) -> TropicalSalesState:
    """V6: Atualiza context state com resultado do read_email"""
    # Parse do resultado
    if isinstance(result, dict):
        emails_json = result.get("raw_output", json.dumps(result, ensure_ascii=False))
        emails_data = result
    else:
        emails_json = str(result)
        try:
            emails_data = json.loads(emails_json)
        except:
            emails_data = {"emails": [], "error": "Failed to parse emails"}
    
    # Atualizar log de execução
    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "read_email",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "emails_count": len(emails_data.get("emails", []))
    })
    
    return {
        **state,
        "emails_json": emails_json,
        "emails_data": emails_data,
        "execution_log": execution_log,
        "current_task": "read_email",
        "timestamp": datetime.now().isoformat()
    }

def classify_message_input_func(state: TropicalSalesState) -> Dict[str, Any]:
    """V6: Extrai emails_json do context state acumulativo"""
    return {"input_json": state.get("emails_json", "{}")}

def classify_message_output_func(state: TropicalSalesState, result: Any) -> TropicalSalesState:
    """V6: Atualiza context state com resultado do classify_message"""
    if isinstance(result, dict):
        classified_json = result.get("raw_output", json.dumps(result, ensure_ascii=False))
        classification_data = result
    else:
        classified_json = str(result)
        try:
            classification_data = json.loads(classified_json)
        except:
            classification_data = {"classifications": [], "error": "Failed to parse classifications"}
    
    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "classify_message",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "classifications_count": len(classification_data.get("emails", []))
    })
    
    return {
        **state,
        "classified_json": classified_json,
        "classification_data": classification_data,
        "execution_log": execution_log,
        "current_task": "classify_message",
        "timestamp": datetime.now().isoformat()
    }

def check_stock_input_func(state: TropicalSalesState) -> Dict[str, Any]:
    """V6: Extrai classified_json do context state acumulativo"""
    return {"input_json": state.get("classified_json", "{}")}

def check_stock_output_func(state: TropicalSalesState, result: Any) -> TropicalSalesState:
    """V6: Atualiza context state com resultado do check_stock_availability"""
    if isinstance(result, dict):
        stock_checked_json = result.get("raw_output", json.dumps(result, ensure_ascii=False))
        stock_data = result
    else:
        stock_checked_json = str(result)
        try:
            stock_data = json.loads(stock_checked_json)
        except:
            stock_data = {"stock_checks": [], "error": "Failed to parse stock data"}
    
    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "check_stock_availability",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "stock_checks_count": len(stock_data.get("emails", []))
    })
    
    return {
        **state,
        "stock_checked_json": stock_checked_json,
        "stock_data": stock_data,
        "execution_log": execution_log,
        "current_task": "check_stock_availability",
        "timestamp": datetime.now().isoformat()
    }

def generate_response_input_func(state: TropicalSalesState) -> Dict[str, Any]:
    """V6: Extrai stock_checked_json do context state acumulativo"""
    return {"input_json": state.get("stock_checked_json", "{}")}

def generate_response_output_func(state: TropicalSalesState, result: Any) -> TropicalSalesState:
    """V6: Atualiza context state com resultado do generate_response"""
    if isinstance(result, dict):
        response_report_md = result.get("raw_output", str(result))
        response_data = result
    else:
        response_report_md = str(result)
        try:
            response_data = json.loads(response_report_md) if response_report_md.startswith("{") else {"report": response_report_md}
        except:
            response_data = {"report": response_report_md}
    
    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "generate_response",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "report_length": len(response_report_md)
    })
    
    return {
        **state,
        "response_report_md": response_report_md,
        "response_data": response_data,
        "execution_log": execution_log,
        "current_task": "generate_response",
        "timestamp": datetime.now().isoformat()
    }

# ---------------------------------------------------------------------
# 7) TASK_REGISTRY V6 - Adaptado para Context State List
# ---------------------------------------------------------------------
TASK_REGISTRY = {
    "read_email": {
        "input_func": read_email_input_func,
        "output_func": read_email_output_func,
        "requires": [],  # Primeira task - apenas configuração inicial
        "produces": ["emails_json", "emails_data"],
        "agent": email_reader_agent,
        "tools": [email_fetch_tool],
        "description": "Lê emails não lidos e estrutura dados"
    },
    "classify_message": {
        "input_func": classify_message_input_func,
        "output_func": classify_message_output_func,
        "requires": ["emails_json"],  # Precisa do resultado do read_email
        "produces": ["classified_json", "classification_data"],
        "agent": classifier_agent,
        "tools": [],
        "description": "Classifica emails em categorias"
    },
    "check_stock_availability": {
        "input_func": check_stock_input_func,
        "output_func": check_stock_output_func,
        "requires": ["classified_json"],  # Precisa do resultado do classify_message
        "produces": ["stock_checked_json", "stock_data"],
        "agent": stock_checker_agent,
        "tools": [natural_language_query_stock_tool],
        "description": "Verifica disponibilidade em estoque"
    },
    "generate_response": {
        "input_func": generate_response_input_func,
        "output_func": generate_response_output_func,
        "requires": ["stock_checked_json"],  # Precisa do resultado do check_stock_availability
        "produces": ["response_report_md", "response_data"],
        "agent": response_generator_agent,
        "tools": [email_send_tool],
        "description": "Gera e envia respostas por email"
    }
}

# ---------------------------------------------------------------------
# 8) Executor Principal V6 - COMPATÍVEL COM WEBSOCKET V3
# ---------------------------------------------------------------------
def execute_task_with_context(task_name: str, context_state: TropicalSalesState, verbose: Optional[Callable[[str], None]] = None) -> TropicalSalesState:
    """
    V6: Executa uma task usando context state (compatível com WebSocket V3)
    
    Args:
        task_name: Nome da task
        context_state: Estado atual do contexto (vem do WebSocket V3)
        verbose: Função de callback para logs
        
    Returns:
        Novo context state atualizado
    """
    if task_name not in TASK_REGISTRY:
        raise ValueError(f"Task '{task_name}' não encontrada no TASK_REGISTRY")
    
    task_config = TASK_REGISTRY[task_name]
    
    if verbose:
        verbose(f"🚀 V6: Iniciando execução da task '{task_name}'")
        verbose(f"📋 Context State recebido: {len(context_state)} campos")
    
    try:
        # 1. EXTRAIR INPUT: Input function seleciona dados necessários do context state
        task_input = task_config["input_func"](context_state)
        
        if verbose:
            verbose(f"📥 Input extraído: {list(task_input.keys())}")
        
        # 2. CRIAR TASK: Configurar task do CrewAI
        task_obj = TaskClass(
            description=tasks_config[task_name]['description'].format(**task_input),
            expected_output=tasks_config[task_name]['expected_output'],
            agent=task_config["agent"],
            tools=task_config["tools"]
        )
        
        # 3. EXECUTAR: CrewAI team executa a task
        crew = TeamClass(
            agents=[task_config["agent"]],
            tasks=[task_obj],
            verbose=False  # Controlar verbose via callback
        )
        
        if verbose:
            verbose(f"🎯 Executando CrewAI team para '{task_name}'...")
        
        result = crew.kickoff(inputs=task_input)
        
        if verbose:
            verbose(f"✅ Task '{task_name}' executada com sucesso")
        
        # 4. ATUALIZAR CONTEXT: Output function atualiza o context state
        updated_context = task_config["output_func"](context_state, result)
        
        if verbose:
            verbose(f"📤 Context state atualizado: {len(updated_context)} campos")
            
        return updated_context
        
    except Exception as e:
        if verbose:
            verbose(f"❌ Erro na execução da task '{task_name}': {e}")
        
        # Retornar context state com erro registrado
        error_log = context_state.get("execution_log", [])
        error_log.append({
            "task": task_name,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        })
        
        return {
            **context_state,
            "execution_log": error_log,
            "current_task": task_name,
            "timestamp": datetime.now().isoformat()
        }

# ---------------------------------------------------------------------
# 9) Funções de Teste e Validação V6
# ---------------------------------------------------------------------
def execute_tropical_sales_flow(max_emails=5, verbose=True) -> TropicalSalesState:
    """V6: Executa fluxo completo TropicalSales com Context State"""
    
    def verbose_callback(msg):
        if verbose:
            print(msg)
    
    # Context state inicial
    context_state = {
        "max_emails": max_emails,
        "execution_log": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # Sequência de tasks
    tasks_sequence = ["read_email", "classify_message", "check_stock_availability", "generate_response"]
    
    print(f"🎯 V6: Iniciando fluxo completo TropicalSales")
    print(f"📧 Max emails: {max_emails}")
    print(f"📋 Tasks: {len(tasks_sequence)}")
    print()
    
    for i, task_name in enumerate(tasks_sequence, 1):
        print(f"📍 [{i}/{len(tasks_sequence)}] Executando {task_name}...")
        context_state = execute_task_with_context(task_name, context_state, verbose_callback)
        print(f"✅ {task_name} concluída")
        print()
    
    print(f"🎉 Fluxo completo concluído!")
    print(f"📊 Total de logs: {len(context_state.get('execution_log', []))}")
    
    return context_state

# ---------------------------------------------------------------------
# 10) Compatibilidade V2 (Opcional)
# ---------------------------------------------------------------------
def execute_individual_task(task_name: str, input_data=None, verbose_callback=None) -> dict:
    """V6: Compatibilidade com WebSocket V2 (converte para V6)"""
    
    # Converter input_data V2 para context_state V6
    context_state = {
        "execution_log": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if task_name == "read_email" and isinstance(input_data, dict):
        context_state["max_emails"] = input_data.get("max_emails", 5)
    elif input_data:
        # Para outras tasks, assumir que input_data é resultado da task anterior
        if task_name == "classify_message":
            context_state["emails_json"] = json.dumps(input_data) if isinstance(input_data, dict) else str(input_data)
        elif task_name == "check_stock_availability":
            context_state["classified_json"] = json.dumps(input_data) if isinstance(input_data, dict) else str(input_data)
        elif task_name == "generate_response":
            context_state["stock_checked_json"] = json.dumps(input_data) if isinstance(input_data, dict) else str(input_data)
    
    # Executar com V6
    result_context = execute_task_with_context(task_name, context_state, verbose_callback)
    
    # Retornar no formato V2 esperado
    return {
        "task_name": task_name,
        "result": result_context,
        "execution_status": "completed",
        "timestamp": result_context.get("timestamp")
    }

# ---------------------------------------------------------------------
# 11) Teste Principal
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("🧪 TESTE TROPICALAGENTSSALESV6 - Context State List Compatible")
    print("=" * 70)
    
    try:
        # Teste básico do fluxo
        result = execute_tropical_sales_flow(max_emails=5, verbose=True)
        
        print("\n📊 RESULTADO FINAL:")
        print(f"   🔢 Max emails: {result.get('max_emails')}")
        print(f"   📧 Emails processados: {len(result.get('emails_data', {}).get('emails', []))}")
        print(f"   🏷️ Classificações: {len(result.get('classification_data', {}).get('emails', []))}")
        print(f"   📦 Verificações estoque: {len(result.get('stock_data', {}).get('emails', []))}")
        print(f"   📝 Relatório gerado: {len(result.get('response_report_md', ''))}")
        print(f"   📊 Logs de execução: {len(result.get('execution_log', []))}")
        
        print("\n✅ TESTE V6 CONCLUÍDO COM SUCESSO!")
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()