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
from dotenv import load_dotenv
import os
load_dotenv(override=True)
'''
os.environ['OPENAI_API_KEY'] = "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"
os.environ["OPENAI_MODEL_NAME"] = llm
os.environ["SERPER_API_KEY"] = "d46999449953645b87258a752ef428d98ae5970f"
os.environ["SERPAPI_API_KEY"] = "d46999449953645b87258a752ef428d98ae5970f"
os.environ["FIRECRAWL_API_KEY"] ="fc-106ce3c76caf460490ddc3d61f9b6a0b"
os.environ["PHI_API_KEY"] = "phi-E9lVhfcMpamx6JbUc1_4hyx79TqYVsr_hi_hvlO0a6o"
'''
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

# Criando instância da ferramenta
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

# Cria o TeamClass
email_reader_team = TeamClass(
    agents=[
        email_reader_agent,
        
    ],
    tasks=[
        read_email_task,
        
    ],
    verbose=True
)
email_classifier_team = TeamClass(
    agents=[
        email_reader_agent,
        classifier_agent
        
    ],
    tasks=[
        read_email_task,
        classify_message_task
        
    ],
    verbose=True
)

stock_check_team = TeamClass(
    agents=[
        email_reader_agent,
        classifier_agent,
        stock_checker_agent
        
    ],
    tasks=[
        read_email_task,
        classify_message_task,
        check_stock_availability_task
        
    ],
    verbose=True
)

response_generator_team = TeamClass(
    agents=[
        email_reader_agent,
        classifier_agent,
        stock_checker_agent,
        response_generator_agent
        
    ],
    tasks=[
        read_email_task,
        classify_message_task,
        check_stock_availability_task,
        generate_response_task
        
    ],
    verbose=True
)




# Cria o TeamClass
email_processing_crew = TeamClass(
    agents=[
        email_reader_agent,
        classifier_agent,
        stock_checker_agent,
        response_generator_agent
    ],
    tasks=[
        read_email_task,
        classify_message_task,
        check_stock_availability_task,
        generate_response_task
    ],
    verbose=True
)



















