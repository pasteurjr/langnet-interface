from crewai import Crew, Agent, Task, Process
import os
from typing import Any, Dict, List, Union, Optional, Callable
from frameworkagentsadapterv4 import FrameworkAdapterFactory
from pathlib import Path
import yaml
from pydantic import BaseModel, Field
import json

# Obter os adaptadores da factory
adapters = FrameworkAdapterFactory.get_framework_adapters(version="crewai")
ToolClass = adapters["tool"]
AgentClass = adapters["agent"]
TaskClass = adapters["task"] 
TeamClass = adapters["team"]
PipelineClass = adapters["pipeline"]
GraphClass = adapters["graph"]
MemorySystemClass = adapters["memory_system"]
MemoryFactoryClass = adapters["memory_factory"]
ProcessClass = adapters["process"]
ProcessType = adapters["processtype"]

llm = 'gpt-4o-mini'
# Configuração de ambiente
from dotenv import load_dotenv
import os
load_dotenv(override=True)

# Warning control
import warnings
warnings.filterwarnings('ignore')

# Carregar configurações YAML
files = {
    'agents': 'agents.yaml',
    'tasks': 'tasks.yaml'
}

configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

agents_config = configs['agents']
tasks_config = configs['tasks']

from datetime import datetime
timestamp = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

# Criando instância das ferramentas
email_fetch_tool = ToolClass(
    name = "Email Fetch Tool",
    description = "This tool connects to an IMAP email server and fetches unread emails.",
    tool_type = "emailfetchtool",
    tool_config={
        "server" : os.getenv("SMTP_HOST"),
        "email": os.getenv("EMAIL_USERNAME"),
        "password":os.getenv("EMAIL_PASSWORD"),
    }
).create()

email_send_tool = ToolClass(
    name = "Email Send Tool",
    description="This tool connects to SMTP server and sends emails.",
    tool_type = "emailsendtool",
    tool_config={
        "server" : os.getenv("IMAP_HOST"),
        "email": os.getenv("EMAIL_USERNAME"),
        "password":os.getenv("EMAIL_PASSWORD"),
    }
).create()

natural_language_query_stock_tool = ToolClass(
    name="Natural Language Query Stock Tool",
    description="This tool receives a question about product stock in natural language, transforms it to SQL query and execute the query, returning the results",
    tool_type="naturallanguagestockcheckertool"
).create()

# Criação dos agentes usando a configuração do arquivo YAML
email_reader_agent = AgentClass(
    name="email_reader_agent",
    config=agents_config['email_reader_agent'],
    verbose=True,
    llm=llm
)

classifier_agent = AgentClass(
    name="classifier_agent",
    config=agents_config['classifier_agent'],
    verbose=True,
    llm=llm
)

stock_checker_agent = AgentClass(
    name="stock_checker_agent",
    config=agents_config['stock_checker_agent'],
    verbose=True,
    llm=llm
)

response_generator_agent = AgentClass(
    name="response_generator_agent",  
    config=agents_config['response_generator_agent'],
    verbose=True,
    llm=llm
)

# Instâncias das Tasks
read_email_task = TaskClass(
    config=tasks_config['read_email'],
    tools=[email_fetch_tool],
    agent=email_reader_agent
)

classify_message_task = TaskClass(
    config=tasks_config['classify_message'],
    tools=[],
    agent=classifier_agent
)

check_stock_availability_task = TaskClass(
    config=tasks_config['check_stock_availability'],
    tools=[natural_language_query_stock_tool],
    agent=stock_checker_agent
)

generate_response_task = TaskClass(
    config=tasks_config['generate_response'],
    tools=[email_send_tool],
    agent=response_generator_agent
)

# =============================================
# INDIVIDUAL TASK EXECUTION FOR PETRI NET
# =============================================

# Registry de tasks individuais para uso na Petri Net
individual_tasks = {
    "read_email": {
        "task": read_email_task,
        "agent": email_reader_agent,
        "tools": [email_fetch_tool]
    },
    "classify_message": {
        "task": classify_message_task,
        "agent": classifier_agent,
        "tools": []
    },
    "check_stock_availability": {
        "task": check_stock_availability_task,
        "agent": stock_checker_agent,
        "tools": [natural_language_query_stock_tool]
    },
    "generate_response": {
        "task": generate_response_task,
        "agent": response_generator_agent,
        "tools": [email_send_tool]
    }
}

def execute_individual_task(task_name: str, input_data: dict = None, verbose_callback: Callable[[str], None] = None) -> dict:
    """
    Executa uma task individual para uso na Petri Net
    
    Args:
        task_name: Nome da task (read_email, classify_message, etc.)
        input_data: Dados de entrada (JSON da task anterior ou None para read_email)
        verbose_callback: Função callback para verbose em tempo real
        
    Returns:
        dict: Resultado da execução da task
    """
    if task_name not in individual_tasks:
        raise ValueError(f"Task {task_name} não encontrada. Tasks disponíveis: {list(individual_tasks.keys())}")
    
    task_info = individual_tasks[task_name]
    
    try:
        if verbose_callback:
            verbose_callback(f"Iniciando execução da task: {task_name}")
            verbose_callback(f"Input data: {json.dumps(input_data, indent=2) if input_data else 'None'}")
        
        # Cria crew com apenas 1 agent e 1 task para execução isolada
        single_crew = TeamClass(
            agents=[task_info["agent"]],
            tasks=[task_info["task"]],
            verbose=True
        )
        
        if verbose_callback:
            verbose_callback(f"Crew criado para task {task_name}")
            verbose_callback(f"Agent: {task_info['agent'].name}")
            verbose_callback(f"Tools: {[tool.name if hasattr(tool, 'name') else str(tool) for tool in task_info['tools']]}")
        
        # Prepara inputs baseado no tipo de task
        inputs = {}
        
        if task_name == "read_email":
            # read_email não precisa de input_data, usa email_fetch_tool diretamente
            if input_data and "max_emails" in input_data:
                inputs["max_emails"] = input_data["max_emails"]
            else:
                inputs["max_emails"] = 10  # default
        else:
            # Outras tasks recebem o JSON completo da task anterior
            if input_data:
                # Passa o JSON como string para que a task possa processá-lo
                inputs["input_json"] = json.dumps(input_data) if isinstance(input_data, dict) else input_data
            else:
                raise ValueError(f"Task {task_name} requer input_data da task anterior")
        
        if verbose_callback:
            verbose_callback(f"Inputs preparados: {inputs}")
            verbose_callback(f"Executando task {task_name}...")
        
        # Executa a task individual
        result = single_crew.kickoff(inputs=inputs)
        
        if verbose_callback:
            verbose_callback(f"Task {task_name} executada com sucesso")
            verbose_callback(f"Resultado: {result}")
        
        # Processa o resultado baseado no tipo de task
        if task_name == "generate_response":
            # generate_response retorna Markdown, não JSON
            return {
                "task_name": task_name,
                "result_type": "markdown",
                "result": result
            }
        else:
            # Outras tasks retornam JSON
            try:
                # Tenta parsear como JSON se for string
                if isinstance(result, str):
                    parsed_result = json.loads(result)
                else:
                    parsed_result = result
                    
                return {
                    "task_name": task_name,
                    "result_type": "json", 
                    "result": parsed_result
                }
            except json.JSONDecodeError:
                # Se não conseguir parsear, retorna como string
                return {
                    "task_name": task_name,
                    "result_type": "string",
                    "result": result
                }
                
    except Exception as e:
        error_msg = f"Erro na execução da task {task_name}: {str(e)}"
        if verbose_callback:
            verbose_callback(error_msg)
        raise Exception(error_msg)

def get_task_chain_info() -> dict:
    """
    Retorna informações sobre a cadeia de tasks para debugging
    """
    return {
        "task_order": ["read_email", "classify_message", "check_stock_availability", "generate_response"],
        "input_requirements": {
            "read_email": "None ou {max_emails: int}",
            "classify_message": "JSON completo de read_email",
            "check_stock_availability": "JSON completo de classify_message", 
            "generate_response": "JSON completo de check_stock_availability"
        },
        "output_types": {
            "read_email": "JSON com emails brutos",
            "classify_message": "JSON com emails classificados",
            "check_stock_availability": "JSON com estoque verificado (apenas pedidos)",
            "generate_response": "Markdown com relatório final"
        }
    }

# =============================================
# TEAMS ORIGINAIS (MANTIDOS PARA COMPATIBILIDADE)
# =============================================

email_reader_team = TeamClass(
    agents=[email_reader_agent],
    tasks=[read_email_task],
    verbose=True
)

email_classifier_team = TeamClass(
    agents=[email_reader_agent, classifier_agent],
    tasks=[read_email_task, classify_message_task],
    verbose=True
)

stock_check_team = TeamClass(
    agents=[email_reader_agent, classifier_agent, stock_checker_agent],
    tasks=[read_email_task, classify_message_task, check_stock_availability_task],
    verbose=True
)

response_generator_team = TeamClass(
    agents=[email_reader_agent, classifier_agent, stock_checker_agent, response_generator_agent],
    tasks=[read_email_task, classify_message_task, check_stock_availability_task, generate_response_task],
    verbose=True
)

email_processing_crew = TeamClass(
    agents=[email_reader_agent, classifier_agent, stock_checker_agent, response_generator_agent],
    tasks=[read_email_task, classify_message_task, check_stock_availability_task, generate_response_task],
    verbose=True
)

# =============================================
# TESTE DAS FUNÇÕES INDIVIDUAIS
# =============================================

def test_individual_execution():
    """
    Testa a execução das tasks individuais em sequência
    """
    print("=== TESTE DE EXECUÇÃO INDIVIDUAL ===")
    
    try:
        # 1. read_email
        print("\n1. Executando read_email...")
        result1 = execute_individual_task("read_email", {"max_emails": 5})
        print(f"Resultado read_email: {result1}")
        
        # 2. classify_message (recebe resultado de read_email)
        print("\n2. Executando classify_message...")
        result2 = execute_individual_task("classify_message", result1["result"])
        print(f"Resultado classify_message: {result2}")
        
        # 3. check_stock_availability (recebe resultado de classify_message)
        print("\n3. Executando check_stock_availability...")
        result3 = execute_individual_task("check_stock_availability", result2["result"])
        print(f"Resultado check_stock_availability: {result3}")
        
        # 4. generate_response (recebe resultado de check_stock_availability)
        print("\n4. Executando generate_response...")
        result4 = execute_individual_task("generate_response", result3["result"])
        print(f"Resultado generate_response: {result4}")
        
        print("\n=== TESTE CONCLUÍDO COM SUCESSO ===")
        return True
        
    except Exception as e:
        print(f"\n=== ERRO NO TESTE: {e} ===")
        return False

if __name__ == "__main__":
    # Exibe informações sobre as tasks
    chain_info = get_task_chain_info()
    print("Informações da cadeia de tasks:")
    print(json.dumps(chain_info, indent=2))
    
    # Executa teste se executado diretamente
    # test_individual_execution()