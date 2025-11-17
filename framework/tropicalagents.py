from crewai import Crew, Agent, Task, Process
from crewai.memory import long_term, short_term
from frameworkmemorylcf import AiTeamMemorySystemFactory
import os
from typing import Any, Dict, List, Union, Optional, Callable
from frameworkagentsadapterv4 import FrameworkAdapterFactory
from pathlib import Path
from langgraph.checkpoint.memory import MemorySaver
import yaml
from pydantic import BaseModel, Field

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
os.environ['OPENAI_API_KEY'] = "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"
os.environ["OPENAI_MODEL_NAME"] = llm
os.environ["SERPER_API_KEY"] = "d46999449953645b87258a752ef428d98ae5970f"
os.environ["SERPAPI_API_KEY"] = "d46999449953645b87258a752ef428d98ae5970f"
os.environ["FIRECRAWL_API_KEY"] ="fc-106ce3c76caf460490ddc3d61f9b6a0b"
os.environ["PHI_API_KEY"] = "phi-E9lVhfcMpamx6JbUc1_4hyx79TqYVsr_hi_hvlO0a6o"

# Warning control
import warnings
warnings.filterwarnings('ignore')

# Carregar configurações YAML
files2 = {
    'agents': 'tropicalagents/config/agentsv3.yaml',
    'tasks': 'tropicalagents/config/tasksv4.yaml'
}

files = {
    'agents': 'tropicalagents/config/agentsteam.yaml',
    'tasks': 'tropicalagents/config/tasksteam.yaml'
}


configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

agents_config = configs['agents']
tasks_config = configs['tasks']

from datetime import datetime
timestamp = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
natural_language_query_tool = ToolClass(
    name="Natural Language Query Tool",
    description="Tool for performing natural language queries in a database",
    tool_type="naturallanguagequerytool"
).create()

json_file_read_tool = ToolClass(
    name="Json read Tool",
    description="Tool for reading  json file content",
    tool_type="fileread",
    tool_config={"file_path": f"jsonqueryresult{timestamp}"}
).create()
from pydantic import BaseModel
db_query_tool = ToolClass(
    name = "DB Query Tool",
    description="Tool for querying a database",
    tool_type="dbquerytool",
    tool_config={
        "host": "camerascasas.no-ip.info",
        "database":"producao_tropical",
        "user":"scadabr",
        "password":"scadabr",
        "port": 3307
        }
).create()


from typing import Any, Optional, Type
json_write_tool = ToolClass(
    name="Json writer Tool",
    description="Write json content to a file",
    tool_type="filewrite",
    tool_config={
        "filename": f"jsonqueryresult{timestamp}.json",
        "directory": "./outputs",
        "overwrite": "True"
    }
).create()


csv_read_tool = ToolClass(
    name="csv_reader",
    description="Read CSV file content",
    tool_type="fileread",
    tool_config={"file_path": f"csvqueryresult{timestamp}"}
).create()
csv_write_tool = ToolClass(
    name="csv writer Tool",
    description="Write csv content to a file",
    tool_type="filewrite",
    tool_config={
        "filename": f"csvqueryresult{timestamp}.csv",
        "directory": "./outputs",
        "overwrite": "True"
    }
).create()

txt_read_tool = ToolClass(
    name="Txt Reader",
    description="Read text  content from a file",
    tool_type="fileread",
    tool_config={"file_path": f"txtqueryresult{timestamp}"}
).create()
md_write_tool = ToolClass(
    name="MD Writer Tool",
    description="Write MD content to a file",
    tool_type="filewrite",
    tool_config={
        "filename": f"mdqueryresult{timestamp}.md",
        "directory": "./outputs",
        "overwrite": "True"
    }
).create()

html_write_tool = ToolClass(
    name="HTML Writer Tool",
    description="Write HTML content to a file",
    tool_type="filewrite",
    tool_config={
        "filename": f"htmlqueryresult{timestamp}.html",
        "directory": "./outputs",
        "overwrite": "True"
    }
).create()


html_analysis_report_write_tool = ToolClass(
    name="HTML Analysis Writer Tool",
    description="Write HTML analysis report content to a file",
    tool_type="filewrite",
    tool_config={
        "filename": f"analysisresult{timestamp}.html",
        "directory": "./outputs",
        "overwrite": "True"
    }
).create()


# Criação dos agentes usando a configuração do arquivo YAML


natural_language_database_searcher_agent = AgentClass(
    name="natural_language_database_searcher",
    config=agents_config['natural_language_database_searcher'],
    llm=llm
)



production_data_verifier = AgentClass(
    name="production_data_verifier",
    config=agents_config['production_data_verifier'],
    verbose=True,
    llm=llm
)

verify_production_data = TaskClass(
    #name="verify_production_data",
    config=tasks_config['verify_production_data'],
    tools = [db_query_tool, html_analysis_report_write_tool],
    
    agent = production_data_verifier    
)


csv_generator_agent = AgentClass(
    name="csv_generator_agent",
    config=agents_config['csv_generator_agent'],
    llm=llm
)

report_generator_agent = AgentClass(
    name="report_generator_agent",
    config=agents_config['report_generator_agent'],
    llm=llm
)

md_report_generator_agent = AgentClass(
    name="md_report_generator_agent",
    config=agents_config['md_report_generator_agent'],
    llm=llm
)



data_analyst_agent = AgentClass(
    name="data_analyst_agent",
    config=agents_config['data_analyst_agent'],
    llm=llm
)


machines_efficiency_database_agent = AgentClass(
    name="machines_efficiency_database_agent",
    config=agents_config['machines_efficiency_database_agent'],
    llm=llm
)

efficiency_analysis_html_report_writer = AgentClass(
    name="efficiency_analysis_html_report_writer",
    config=agents_config['efficiency_analysis_html_report_writer'],
    llm=llm
)


get_machines_efficiency_data = TaskClass(
    #name="get_machines_efficiency_data",
    config=tasks_config['get_machines_efficiency_data'],
    tools = [db_query_tool],
    agent = machines_efficiency_database_agent
)

get_machines_efficiency_analysis = TaskClass(
    #name="get_machines_efficiency_analysis",
    config=tasks_config['get_machines_efficiency_analysis'],
    
    agent = production_data_verifier
)
generate_machines_efficiency_analysis_html_report = TaskClass(
    #name="generate_machines_efficiency_analysis_html_report",
    config=tasks_config['generate_machines_efficiency_analysis_html_report'],
    agent = efficiency_analysis_html_report_writer
)

generate_machines_efficiency_analysis_html_report_saving_to_file = TaskClass(
    #name="generate_machines_efficiency_analysis_html_report",
    config=tasks_config['generate_machines_efficiency_analysis_html_report_saving_to_file'],
    tools = [html_analysis_report_write_tool],
    agent = efficiency_analysis_html_report_writer
)






machines_efficiency_analysis = TaskClass(
    #name="machines_efficiency_analysis",
    config=tasks_config['machines_efficiency_analysis'],
    tools = [html_analysis_report_write_tool],
    agent = production_data_verifier
)

from crewai import Process
import time

production_efficiency_analisys_team = TeamClass(
    #name="eficiencia_analisys_team",
    agents=[ machines_efficiency_database_agent,production_data_verifier, efficiency_analysis_html_report_writer],
    tasks=[get_machines_efficiency_data, get_machines_efficiency_analysis, generate_machines_efficiency_analysis_html_report],
    #memory=True,
    verbose=True,
    memory_system=MemoryFactoryClass().create_memory_system(
            "langchain",  # Por default vamos usar langchain
            "task_verify_production_data",
            "production_monitor_dir",
            api_key="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",
            short_term_capacity = 10000,
            long_term_capacity =  10000
        ),
    process=ProcessClass(ProcessType.SEQUENTIAL)
)
# Função para executar periodicamente o crew
def run_crew_periodically(crew, interval_seconds, iterations):
    """
    Executa o crew a cada `interval_seconds` segundos por um número definido de iterações.
    """
    for i in range(iterations):
        print(f"Executando a iteração {i + 1}/{iterations}")
        input_data = {"memory_system": {},"max_regs":5}
        result = crew.executar(inputs=input_data)
        
        print(f"Resultado da execução: {result}")
        time.sleep(interval_seconds)

production_efficiency_analisys_team = TeamClass(
    #name="eficiencia_analisys_team",
    agents=[ machines_efficiency_database_agent,production_data_verifier, efficiency_analysis_html_report_writer],
    tasks=[get_machines_efficiency_data, get_machines_efficiency_analysis, generate_machines_efficiency_analysis_html_report],
    #memory=True,
    verbose=True,
    memory_system=MemoryFactoryClass().create_memory_system(
            "langchain",  # Por default vamos usar langchain
            "task_verify_production_data",
            "production_monitor_dir",
            api_key="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",
            short_term_capacity = 10000,
            long_term_capacity =  10000
        ),
)

efficiency_analisys_team = TeamClass(
    #name="eficiencia_analisys_team",
    agents=[ machines_efficiency_database_agent,production_data_verifier],
    tasks=[get_machines_efficiency_data, machines_efficiency_analysis],
    #memory=True,
    verbose=True,
    memory_system=MemoryFactoryClass().create_memory_system(
            "langchain",  # Por default vamos usar langchain
            "task_verify_production_data",
            "production_monitor_dir",
            api_key="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",
            short_term_capacity = 10000,
            long_term_capacity =  10000
        ),
)




eficiencia_analisys_team = TeamClass(
    #name="eficiencia_analisys_team",
    agents=[ production_data_verifier],
    tasks=[verify_production_data],
    memory=True,
    verbose=True,
    memory_system=MemoryFactoryClass().create_memory_system(
            "langchain",  # Por default vamos usar langchain
            "task_verify_production_data",
            "production_monitor_dir",
            api_key="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",
            short_term_capacity = 10000,
            long_term_capacity =  10000
        ),
)


from typing import TypedDict, List, Union, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime

# Estado
class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]
    current_phase: str
    natural_language_json_result : str
    csv_content: str
    md_content: str
    html_content: str
    formatted_result: str
    analysis_result: str


def search_db_input(state: AgentState) -> Dict[str, Any]:
    """Extrai a questão natural dos messages"""
    print("entrada do agente search_db_input")
    print(state["messages"][-1].content)
    return {
        "question": state["messages"][-1].content,
    }


def search_db_output(state: AgentState, result: Any) -> AgentState:
    """Formata o resultado da busca com metadados"""
    return {
        "messages": [AIMessage(content=str(result))],
        "current_phase": "searched",
        "natural_language_json_result": str(result),
        "csv_content": "",
        "formatted_result" :"",
        "analysis_result":""
        
    }
import json
def csv_gen_input(state: AgentState) -> Dict[str, Any]:
    """Prepara dados para geração CSV"""
    try:
        json_data = json.loads(state["messages"][-1].content)
        return {
            "natural_language_json_result": json_data["query_results"]
        }
    except Exception as e:
        print(f"Error in csv_gen_input: {e}")
        return {
            "query_results": []
        }
def csv_gen_output(state: AgentState, result: Any) -> AgentState:
    """Atualiza estado com resultado da geração do CSV"""
    # result aqui é o retorno do agente após gerar o CSV
    return {
        "messages": state["messages"] + [AIMessage(content=str(result))],
        "current_phase": "csv_generated",
        "csv_content": str(result)  # Aqui deve vir o path do arquivo gerado
    }



def report_gen_input(state: AgentState) -> Dict[str, Any]:
    """Prepara dados do CSV para geração de relatórios"""
    try:
        return {
            "csv_content": state["csv_content"]
        }
    except Exception as e:
        print(f"Error in report_gen_input: {e}")
        return {
            "csv_content": ""
        }
def report_gen_output(state: AgentState, result: Any) -> AgentState:
    try:
        # Se o resultado for um dicionário com 'description', pega só o conteúdo
        if isinstance(result, dict) and 'description' in result:
            content = result['description']
        else:
            content = str(result)
            
        return {
            "messages": state["messages"] + [AIMessage(content=content)],
            "current_phase": "report_generated",
            "natural_language_json_result": state["natural_language_json_result"],
            "csv_content": state["csv_content"],
            "md_content": "",  # Usa o conteúdo extraído
            "html_content": content,  # Usa o conteúdo extraído
            "formatted_result": "",
            "analysis_result": ""
        }
    except Exception as e:
        print(f"Error in report_gen_output: {e}")
        return state


def md_report_gen_input(state: AgentState) -> Dict[str, Any]:
    """Prepara dados do CSV para geração de relatórios"""
    try:
        return {
            "csv_content": state["csv_content"]
        }
    except Exception as e:
        print(f"Error in md_report_gen_input: {e}")
        return {
            "csv_content": ""
        }
def md_report_gen_output(state: AgentState, result: Any) -> AgentState:
    try:
        # Se o resultado for um dicionário com 'description', pega só o conteúdo
        if isinstance(result, dict) and 'description' in result:
            content = result['description']
        else:
            content = str(result)
            
        return {
            "messages": state["messages"] + [AIMessage(content=content)],
            "current_phase": "md_report_generated",
            "natural_language_json_result": state["natural_language_json_result"],
            "csv_content": state["csv_content"],
            "md_content": content,  # Usa o conteúdo extraído
            "html_content": "",  # Usa o conteúdo extraído
            "formatted_result": "",
            "analysis_result": ""
        }
    except Exception as e:
        print(f"Error in report_gen_output: {e}")
        return state






def analysis_input(state: AgentState) -> Dict[str, Any]:
    """Prepara dados para análise estatística"""
    try:
        return {
            "csv_content": state["csv_content"]
        }
    except Exception as e:
        print(f"Error in md_report_gen_input: {e}")
        return {
            "csv_content": ""
        }


def analysis_output(state: AgentState, result: Any) -> AgentState:
    """
    Processa o resultado da análise e atualiza o estado.
    Organiza o relatório HTML com a análise dos dados.
    """
    try:
        # Se o resultado já é string (HTML), usa diretamente
        print("**********analysis output RESULT")
        print(result)
        '''
        if isinstance(result, str):
            formatted_html = result
        else:
            # Se é dict, extrai os componentes relevantes
            formatted_html = result.get('html_content', str(result))
        '''
        return {
            "messages": state["messages"] + [AIMessage(content=result)],
            "current_phase": "analyzed",
            "csv_content": state["csv_content"],
            "analysis_result": result,
            "formatted_result": result
        }
    except Exception as e:
        print(f"Error in analysis_output: {e}")
        return state

# Tasks atualizadas com as novas funções
search_database_task = TaskClass(
    state_class=AgentState,
    input_func=search_db_input,
    output_func=search_db_output,
    config=tasks_config['search_database_using_natural_language'],
    agent=natural_language_database_searcher_agent,
    tools=[natural_language_query_tool,json_write_tool]
)

execute_sql_query_database_agent = AgentClass(
    name="execute sql query databaseagent",
    config=agents_config['execute_sql_query_database_agent'],
    llm=llm
)

search_database_using_sql_query_task = TaskClass(
    state_class=AgentState,
    
    config=tasks_config['search_database_using_sql_query'],
    agent=execute_sql_query_database_agent,
    tools=[db_query_tool]
)


'''
result= search_database_task.execute({"question":"Retorne todas as movimentações do produto ALCA BOMBONA"})
print("RESULT:")
print(result)
'''
csv_generation_task = TaskClass(
    state_class=AgentState,
    input_func=csv_gen_input,
    output_func=csv_gen_output,
    config=tasks_config['csv_generation'],
    agent=csv_generator_agent,
    tools=[csv_write_tool]
)

# Task atualizada
# Gerar o nome do arquivo
timestamp = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
output_filename = f"query_report{timestamp}"

report_generation_task = TaskClass(
    state_class=AgentState,
    input_func=report_gen_input,
    output_func=report_gen_output,
    config=tasks_config['report_generation'],
    agent=report_generator_agent,
    tools=[html_write_tool],
    #output_file=output_filename  # Nome real do arquivo
)
md_report_generation_task = TaskClass(
    state_class=AgentState,
    input_func=md_report_gen_input,
    output_func=md_report_gen_output,
    config=tasks_config['md_report_generation'],
    agent=md_report_generator_agent,
    tools=[md_write_tool],
    #output_file=output_filename  # Nome real do arquivo
)



data_analysis_task = TaskClass(
    state_class=AgentState,
    input_func=analysis_input,
    output_func=analysis_output,
    config=tasks_config['data_analysis'],
    agent=data_analyst_agent,
    tools=[html_analysis_report_write_tool]
)

data_analysis_task_user = TaskClass(
    state_class=AgentState,
    input_func=analysis_input,
    output_func=analysis_output,
    config=tasks_config['data_analysis_user'],
    agent=data_analyst_agent,
    #tools=[html_analysis_report_write_tool]
)

data_analysis_user_query = TaskClass(
    state_class=AgentState,
    input_func=analysis_input,
    output_func=analysis_output,
    config=tasks_config['data_analysis_user_query'],
    agent=data_analyst_agent,
    
)


# Criar e configurar o time
teamanalysis = TeamClass(
    
    agents=[
        natural_language_database_searcher_agent,
        data_analyst_agent
    ],
    tasks=[
        search_database_task,
        data_analysis_task
    ]
)
teamanalysisuser = TeamClass(
    
    agents=[
        natural_language_database_searcher_agent,
        data_analyst_agent
    ],
    tasks=[
        search_database_task,
        data_analysis_task_user
    ]
)

teamanalysisdbuser = TeamClass(
    
    agents=[
        execute_sql_query_database_agent,
        data_analyst_agent
    ],
    tasks=[
        search_database_using_sql_query_task,
        data_analysis_user_query
    ]
)


teamhtml = TeamClass(
    
    agents=[
        natural_language_database_searcher_agent,
        report_generator_agent
    ],
    tasks=[
        search_database_task,
        report_generation_task
        
    ]
)
teamcsv = TeamClass(
    
    agents=[
        natural_language_database_searcher_agent,
        csv_generator_agent
    ],
    tasks=[
        search_database_task,
        csv_generation_task
        
    ]
)

production_efficiency_analisys_team = TeamClass(
    #name="eficiencia_analisys_team",
    agents=[ machines_efficiency_database_agent,production_data_verifier, efficiency_analysis_html_report_writer],
    tasks=[get_machines_efficiency_data, get_machines_efficiency_analysis, generate_machines_efficiency_analysis_html_report],
    #memory=True,
    verbose=True,
    memory_system=MemoryFactoryClass().create_memory_system(
            "langchain",  # Por default vamos usar langchain
            "task_verify_production_data",
            "production_monitor_dir",
            api_key="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",
            short_term_capacity = 10000,
            long_term_capacity =  10000
        ),
)