# frameworkagentsadapter.py - Parte 1: Imports e início do sistema de memória

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union, Optional, Callable, Type
from pathlib import Path
from collections import deque
from datetime import datetime
import pickle
import traceback
from pydantic import BaseModel
import inspect
import os


# Imports LangChain
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
)

from frameworkmemory import LangChainAgentMemorySystem,LangChainLongTermAdapter,LangChainMemorySystemFactory,LangChainContextAdapter 
from frameworkmemorylcf import AiTeamMemorySystemFactory,LangChainFullTaskMemorySystem, LangChainFullContextAdapter,LangChainFullLongTermAdapter,LangChainFullShortTermAdapter


# Imports CrewAI - CORRIGIDO
# Imports CrewAI
from crewai import Agent as CrewAgent
from crewai import Task as CrewTask
from crewai import Crew
from langchain.tools import BaseTool
from crewai import Process as CrewProcess
from crewai_tools import (
    SerperDevTool,
    ScrapeWebsiteTool,
    WebsiteSearchTool,
    FileReadTool,
    MDXSearchTool,
    # BrowserbaseWebLoader,
    # CodeDocsRAGSearch,
    # FirecrawlSearch,
    # GithubSearch,
)
import crewai

# Imports do nosso framework
from frameworkagents import (
    MemoryStore,
    ShortTermMemory,
    LongTermMemory,
    ContextManager,
    TaskMemorySystem,
    Agent,
    Task,
    Tool,
    Team,
    ProcessingStrategy,
    AgentObserver,
    Observable,
    Process,
    ProcessType,
)

from crewai_tools import FileWriterTool
from pydantic import BaseModel


# Começando com as classes de memória


class AiTeamToolant(Tool):
    """Adapter para ferramentas do CrewAI"""

    def __init__(
        self,
        name: str,
        description: str,
        tool_type: str,
        tool_config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name=name, description=description)
        self.crewai_tool = self._create_tool(tool_type, tool_config or {})

    def _create_tool(self, tool_type: str, config: Dict[str, Any]) -> Any:
        """Cria a ferramenta CrewAI apropriada baseado no tipo"""
        tool_type = tool_type.lower()

        if tool_type == "scrapewebsite":
            if "website_url" not in config:
                raise ValueError("website_url é obrigatório para ScrapeWebsiteTool")
            return ScrapeWebsiteTool(website_url=config["website_url"])

        elif tool_type == "serperdev":
            return SerperDevTool()

        elif tool_type == "websitesearch":
            if "url" not in config:
                raise ValueError("url é obrigatório para WebsiteSearchTool")
            return WebsiteSearchTool(url=config["url"])

        elif tool_type == "browserloader":
            if "urls" not in config:
                raise ValueError("urls é obrigatório para BrowserbaseWebLoader")
            return BrowserbaseWebLoader(urls=config["urls"])

        elif tool_type == "searchcode":
            if "docs_url" not in config:
                raise ValueError("docs_url é obrigatório para CodeDocsRAGSearch")
            return CodeDocsRAGSearch(docs_url=config["docs_url"])

        elif tool_type == "firecrawlsearch":
            if "search_id" not in config:
                raise ValueError("search_id é obrigatório para FirecrawlSearch")
            return FirecrawlSearch(search_id=config["search_id"])

        elif tool_type == "githubsearch":
            if "query" not in config:
                raise ValueError("query é obrigatório para GithubSearch")
            return GithubSearch(query=config["query"])

        else:
            raise ValueError(f"Tipo de ferramenta não suportado: {tool_type}")

    def execute(self, **kwargs) -> Any:
        if not self.crewai_tool:
            raise ValueError("Nenhuma ferramenta CrewAI configurada")
        return self.crewai_tool.execute(**kwargs)


"""
class AiTeamProcess(Process):
    def __init__(self, process_type: ProcessType):
        super().__init__(process_type)
        if process_type == ProcessType.HIERARCHICAL:
            self.crew_process = crewai.Process.hierarchical
        elif process_type == ProcessType.PARALLEL:
            self.crew_process = crewai.Process.parallel
        else:
            self.crew_process = crewai.Process.sequential

    def execute(self, crew: Any) -> Any:
        return self.crew_process
"""


class AiTeamProcess(Process):
    def __init__(self, process_type: ProcessType):
        super().__init__(process_type)

    def cria_instancia(self) -> Any:
        if self.process_type == ProcessType.HIERARCHICAL:
            print(f"PROCESSO HIERARQUICO")
            return CrewProcess.hierarchical
        elif self.process_type == ProcessType.PARALLEL:
            return CrewProcess.parallel
        return CrewProcess.sequential


class AiTeamProcessingStrategyant(ProcessingStrategy):
    """Estratégia de processamento para tarefas do CrewAI"""

    def __init__(self, crewai_task: CrewTask):
        self.crewai_task = crewai_task
        self.execution_log = []

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            start_time = datetime.now()
            self._log_execution(
                "process_start",
                {"context": str(context), "timestamp": start_time.isoformat()},
            )

            # Executa tarefa do CrewAI
            result = self.crewai_task.execute(context)

            self._log_execution(
                "process_complete",
                {
                    "result": result,
                    "execution_time": (datetime.now() - start_time).total_seconds(),
                },
            )

            return {
                "result": result,
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "status": "completed",
            }

        except Exception as e:
            self._log_execution(
                "process_error", {"error": str(e), "traceback": traceback.format_exc()}
            )
            raise

    def _log_execution(self, action: str, data: Dict[str, Any]):
        """Registra ações de execução"""
        self.execution_log.append(
            {"timestamp": datetime.now().isoformat(), "action": action, "data": data}
        )


class AiTeamBaseTool(Tool):
    def __init__(
        self,
        name: str,
        description: str,
        tool_config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name=name, description=description, tool_config=tool_config)

    @abstractmethod
    def _run(self) -> Any:
        pass

    def cria_instancia(self) -> BaseTool:
        class CrewAITool(BaseTool):
            def __init__(self_tool):
                # Passa name e description para o construtor do BaseTool
                super().__init__(name=self.name, description=self.description)

            def _run(self_tool, **kwargs) -> Any:
                return self._run()

        return CrewAITool()

    def cria_instanciax3(self) -> BaseTool:
        class CrewAITool(BaseTool):
            def __init__(self_tool):
                super().__init__()
                self_tool.name = self.name
                self_tool.description = self.description

            def _run(self_tool, **kwargs) -> Any:
                return self._run()

        return CrewAITool()

    def cria_instanciax2(self) -> BaseTool:
        # Apenas os atributos que o BaseTool do CrewAI espera
        tool_attributes = {
            "name": self.name,
            "description": self.description,
            "_run": self._run,
        }

        # Cria a nova classe apenas com os atributos necessários
        CrewAITool = type("CrewAITool", (BaseTool,), tool_attributes)

        return CrewAITool()

    def cria_instanciax(self) -> BaseTool:
        # Captura os atributos da instância atual
        tool_attributes = {
            key: value for key, value in vars(self).items() if not key.startswith("_")
        }

        # Captura também os atributos de classe
        class_attributes = {
            key: value
            for key, value in type(self).__dict__.items()
            if not key.startswith("_")
        }

        # Combina os atributos
        all_attributes = {
            **tool_attributes,
            **class_attributes,
            "name": self.name,
            "description": self.description,
            "_run": self._run,
        }

        # Cria a nova classe com todos os atributos
        CrewAITool = type("CrewAITool", (BaseTool,), all_attributes)

        return CrewAITool()
from crewai.tools import BaseTool
import mindsdb_sdk

def MindsDbQuery(question:str) -> str:
    from dotenv import load_dotenv
    load_dotenv()
    
    # Conecta ao servidor MindsDB correto
    server = mindsdb_sdk.connect(
        url=f"http://{os.getenv('MINDSDB_HOST', 'camerascasas.no-ip.info')}:{os.getenv('MINDSDB_PORT', '47334')}"
    )
    agent = server.agents.get('natural_language_database_searcher')
    print(f"Executing NaturalLanguageQueryTool with query: {question}")
    answer = agent.completion([{'question': f'{question}'}])
    return answer.content

#ATUALIZE
def MindsDbProductStock(question:str) -> str:
    from dotenv import load_dotenv
    load_dotenv()
    
    # Conecta ao servidor MindsDB correto
    server = mindsdb_sdk.connect(
        url=f"http://{os.getenv('MINDSDB_HOST', 'camerascasas.no-ip.info')}:{os.getenv('MINDSDB_PORT', '47334')}"
    )
    agent = server.agents.get('natural_language_check_stock')
    print(f"Executando mindsdb para checagem de estoque: {question}")
    answer = agent.completion([{'question': f'{question}'}])
    return answer.content

#ATUALIZE
class NaturalLanguageStockCheckerTool(BaseTool):
    name: str = "Natural Language Stock Checker Tool"
    description: str = "This tool receives a question about product stock in natural language, transforms it to SQL query and execute the query, returning the product name and stock quantity"

    def __init__(self):
        
        super().__init__()
        
    def _run(self, product_name: str) -> str:
        stock_query = f"""
        Para o produto '{product_name}', retorne apenas:
        1. Nome exato do produto mais similar
        2. Quantidade em estoque
        3. Se houver outros produtos similares, liste no máximo 2
        Formato da resposta: PRODUTO: [nome], ESTOQUE: [quantidade]
        """
        
        return MindsDbProductStock(stock_query)







class NaturalLanguageQuery(BaseTool):
    name: str = "Natural Language Query Tool"
    description: str = "This tool receives a question in natural language, transforms it to SQL query and execute the query, returning the results"

    def __init__(self):
        """
        Inicializa a ferramenta com as configurações de conexão ao banco de dados.
        """
        super().__init__()
        
    def _run(self, query: str) -> str:
        print("Rodando NATLANGUAGEQUERY")
        
        return MindsDbQuery(query)






import mysql.connector
from mysql.connector import Error
from langchain.tools import BaseTool


import mysql.connector
from mysql.connector import Error
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class DBQueryTool(BaseTool, BaseModel):
    name: str = "Database Query Tool"
    description: str = "This tool connects to a MySQL database, executes queries, and returns the query results."

    # Declaração explícita dos campos
    host: str = Field(..., description="Hostname do banco de dados")
    database: str = Field(..., description="Nome do banco de dados")
    user: str = Field(..., description="Usuário do banco de dados")
    password: str = Field(..., description="Senha do banco de dados")
    port: int = Field(3306, description="Porta para conexão (padrão: 3306)")

    def _run(self, query: str) -> str:
        """
        Executa uma query SQL no banco de dados MySQL e retorna os resultados.

        Args:
            query (str): A query SQL para ser executada.

        Returns:
            str: O resultado da query em formato de string ou uma mensagem de erro.
        """
        try:
            # Conexão com o banco de dados MySQL
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )

            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute(query)

                # Processar resultados
                if query.strip().lower().startswith("select"):
                    results = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]
                    output = [dict(zip(column_names, row)) for row in results]
                    return f"Query Results: {output}"
                else:
                    connection.commit()
                    return "Query executed successfully (no results returned)."

        except Error as e:
            return f"Error while connecting to MySQL: {str(e)}"

        finally:
            # Fechar cursor e conexão
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()

class TextFileWriterToolant(BaseTool):
    name: str = "Text File Writer Tool"
    description: str = "This tool receives content in any text format (txt, csv, json, sql,md, etc) and writes to a file"
    filename: str  # Campo Pydantic
    directory: str = "./"  # Campo Pydantic com valor default
    overwrite: str = "True"  # Campo Pydantic com valor 
    def _run(self, content: str) -> str:
        try:
            # Create directory if it doesn't exist
            if not os.path.exists(self.directory):
                os.makedirs(self.directory)
            
            # Construct full path
            filepath = os.path.join(self.directory, self.filename)
            
            # Write content to file
            mode = 'w' if self.overwrite.lower() == "true" else 'x'
            with open(filepath, mode) as file:
                file.write(content)
            
            return f"Content successfully written to {filepath}"
        except Exception as e:
            return f"Error writing to file: {str(e)}"

class TextFileWriterTool(BaseTool):
    name: str = "Text File Writer Tool"
    description: str = "This tool writes content directly to a file. The content must be provided as a plain string."
    filename: str  # Campo Pydantic
    directory: str = "./"  # Campo Pydantic com valor default
    overwrite: str = "True"  # Campo Pydantic com valor default

    def _run(self, content: str) -> str:
        """
        Write content to a file. Content must be a string.
        
        Args:
            content (str): The text content to write to the file
            
        Returns:
            str: Success/error message
        """
        try:
            # Create directory if it doesn't exist
            if not os.path.exists(self.directory):
                os.makedirs(self.directory)
            
            # Construct full path
            filepath = os.path.join(self.directory, self.filename)
            
            # Write content to file
            mode = 'w' if self.overwrite.lower() == "true" else 'x'
            with open(filepath, mode) as file:
                # Ensure content is a string
                if not isinstance(content, str):
                    raise ValueError("Content must be a string")
                file.write(content)
            
            return f"Content successfully written to {filepath}"
        except Exception as e:
            return f"Error writing to file: {str(e)}"
        
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import requests

class URLFetchTool(BaseTool, BaseModel):
    name: str = "URL Fetch Tool"
    description: str = "This tool fetches content from a given URL using an HTTP GET request and returns the response content."

    

    def _run(self, url: str) -> str:
        """
        Fetches the content of a given URL using a GET request.

        Args:
            url (str): The URL to fetch content from.

        Returns:
            str: The content of the response or an error message.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise error for HTTP 4xx/5xx statuses
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error fetching URL content: {str(e)}"

    def _arun(self, url: str) -> str:
        """
        Asynchronous method is not implemented for this tool.

        Args:
            url (str): The URL to fetch content from.

        Returns:
            str: NotImplementedError message.
        """
        raise NotImplementedError("Asynchronous operation is not supported for this tool.")



#ATUALIZE
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional

class EmailSendTool587(BaseTool, BaseModel):
   name: str = "Email Send Tool"
   description: str = "This tool connects to SMTP server and sends emails."

   server: str = Field(..., description="SMTP server address")
   port: int = Field(587, description="SMTP port (default: 587)")
   email: str = Field(..., description="Email address")
   password: str = Field(..., description="Email password or app password")

   def _run(
       self, 
       to_email: str,
       subject: str,
       content: str,
       cc: Optional[str] = None,
       bcc: Optional[str] = None
   ) -> Dict:
       """
       Envia um email via SMTP.

       Args:
           to_email (str): Email do destinatário
           subject (str): Assunto do email
           content (str): Conteúdo do email
           cc (str, opcional): Email em cópia
           bcc (str, opcional): Email em cópia oculta

       Returns:
           Dict: Resultado do envio contendo:
               - success: bool indicando se enviou
               - message: mensagem de sucesso ou erro
               - timestamp: hora do envio
       """
       try:
           # Cria a mensagem
           msg = MIMEMultipart()
           msg['From'] = self.email
           msg['To'] = to_email
           msg['Subject'] = subject
           
           if cc:
               msg['Cc'] = cc
           if bcc:
               msg['Bcc'] = bcc

           # Adiciona o conteúdo
           msg.attach(MIMEText(content, 'plain'))

           # Conecta ao servidor SMTP
           smtp = smtplib.SMTP(self.server, self.port)
           smtp.starttls()
           smtp.login(self.email, self.password)
           
           # Envia o email
           recipients = [to_email]
           if cc:
               recipients.extend(cc.split(','))
           if bcc:
               recipients.extend(bcc.split(','))
               
           smtp.send_message(msg, self.email, recipients)
           
           return {
               "success": True,
               "message": "Email enviado com sucesso",
               "timestamp": datetime.now().isoformat()
           }

       except Exception as e:
           return {
               "success": False,
               "message": f"Erro ao enviar email: {str(e)}",
               "timestamp": datetime.now().isoformat()
           }
           
       finally:
           if 'smtp' in locals():
               smtp.quit()

   async def _arun(
       self, 
       to_email: str,
       subject: str,
       content: str,
       cc: Optional[str] = None,
       bcc: Optional[str] = None
   ) -> Dict:
       """Async version of the tool"""
       return self._run(to_email, subject, content, cc, bcc)

from datetime import datetime
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import imaplib
import email
from email.header import decode_header
from typing import List, Dict

class EmailFetchTool(BaseTool, BaseModel):
   name: str = "Email Fetch Tool"
   description: str = "This tool connects to an IMAP email server and fetches unread emails."

   server: str = Field(..., description="Email server address (IMAP)")
   port: int = Field(993, description="IMAP port (default: 993)")
   email: str = Field(..., description="Email address")
   password: str = Field(..., description="Email password or app password")
   folder: str = Field("INBOX", description="Email folder to check")

   def _run(self, max_emails: int = 5) -> List[Dict]:
       try:
           imap = imaplib.IMAP4_SSL(self.server, self.port)
           imap.login(self.email, self.password)
           imap.select(self.folder)

           # Busca emails não lidos desde o início do ano
           _, messages = imap.search(None, '(UNSEEN) (SINCE "01-Jan-2024")')
           email_ids = messages[0].split()
           email_ids = sorted(email_ids, reverse=True)  # Mais recentes primeiro
           email_ids = email_ids[:max_emails]

           print(f"Encontrados {len(email_ids)} emails não lidos")
           
           emails = []
           for e_id in email_ids:
               print(f"Processando email ID: {e_id}")
               _, msg = imap.fetch(e_id, '(RFC822)')
               email_body = msg[0][1]
               email_message = email.message_from_bytes(email_body)
               
               # Processa Subject
               raw_subject = decode_header(email_message["Subject"])[0][0]
               if isinstance(raw_subject, bytes):
                   try:
                       subject = raw_subject.decode()
                   except:
                       subject = raw_subject.decode('ascii', errors='replace')
               else:
                   subject = str(raw_subject)
               
               # Processa From
               raw_sender = decode_header(email_message["From"])[0][0]
               if isinstance(raw_sender, bytes):
                   try:
                       sender = raw_sender.decode()
                   except:
                       sender = raw_sender.decode('ascii', errors='replace')
               else:
                   sender = str(raw_sender)
               
               # Processa conteúdo
               content = ""
               if email_message.is_multipart():
                   for part in email_message.walk():
                       if part.get_content_type() == "text/plain":
                           try:
                               payload = part.get_payload(decode=True)
                               charset = part.get_content_charset() or 'utf-8'
                               content = payload.decode(charset, errors='replace')
                               break
                           except Exception as e:
                               print(f"Erro decodificando parte multipart: {e}")
                               content = payload.decode('ascii', errors='replace')
               else:
                   try:
                       payload = email_message.get_payload(decode=True)
                       charset = email_message.get_content_charset() or 'utf-8'
                       content = payload.decode(charset, errors='replace')
                   except Exception as e:
                       print(f"Erro decodificando conteúdo: {e}")
                       content = payload.decode('ascii', errors='replace')
               
               print(f"Email processado - Assunto: {subject}")
               
               emails.append({
                   "sender": sender,
                   "subject": subject,
                   "content": content,
                   "date": email_message["Date"]
               })

           return emails

       except Exception as e:
           print(f"Erro ao buscar emails: {e}")
           return [{
               "error": True,
               "message": f"Error fetching emails: {str(e)}",
               "timestamp": datetime.now().isoformat()
           }]
       
       finally:
           if 'imap' in locals():
               try:
                   imap.close()
                   imap.logout()
               except:
                   pass

   async def _arun(self, max_emails: int = 10) -> List[Dict]:
       return self._run(max_emails)

from datetime import datetime
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional

class EmailSendTool(BaseTool, BaseModel):
    name: str = "Email Send Tool"
    description: str = "This tool connects to SMTP server and sends emails."

    server: str = Field(..., description="SMTP server address")
    port: int = Field(465, description="SMTP SSL port (default: 465)")
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Email password or app password")

    def _run(
        self, 
        to_email: str,
        subject: str,
        content: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> Dict:
        """
        Envia um email via SMTP SSL.

        Args:
            to_email (str): Email do destinatário
            subject (str): Assunto do email
            content (str): Conteúdo do email
            cc (str, opcional): Email em cópia
            bcc (str, opcional): Email em cópia oculta

        Returns:
            Dict: Resultado do envio contendo:
                - success: bool indicando se enviou
                - message: mensagem de sucesso ou erro
                - timestamp: hora do envio
        """
        try:
            # Cria a mensagem
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = cc
            if bcc:
                msg['Bcc'] = bcc

            # Adiciona o conteúdo
            msg.attach(MIMEText(content, 'plain'))

            # Conecta ao servidor SMTP usando SSL
            smtp = smtplib.SMTP_SSL(self.server, self.port)
            smtp.login(self.email, self.password)
            
            # Envia o email
            recipients = [to_email]
            if cc:
                recipients.extend(cc.split(','))
            if bcc:
                recipients.extend(bcc.split(','))
                
            smtp.send_message(msg, self.email, recipients)
            
            return {
                "success": True,
                "message": "Email enviado com sucesso",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao enviar email: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            if 'smtp' in locals():
                smtp.quit()

    async def _arun(
        self, 
        to_email: str,
        subject: str,
        content: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> Dict:
        """Async version of the tool"""
        return self._run(to_email, subject, content, cc, bcc)




class AiTeamTool(Tool):
    def __init__(
        self,
        name: str,
        description: str,
        tool_type: str,
        tool_config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name=name, description=description, tool_config=tool_config)
        self.tool_type = tool_type

    def cria_instancia(self) -> Any:
        print(f"********CRIANDO CREWAI TOOL {self.tool_type}")
        tool_type = self.tool_type.lower()

        if tool_type == "scrapewebsite":
            if "website_url" in self.tool_config:
                return ScrapeWebsiteTool(website_url=self.tool_config["website_url"])
            else:
                return ScrapeWebsiteTool()

        elif tool_type == "serperdev":
            return SerperDevTool()

        elif tool_type == "fileread":  # Novo
            if "file_path" not in self.tool_config:
                raise ValueError("file_path é obrigatório para FileReadTool")
            return FileReadTool(file_path=self.tool_config["file_path"])
        elif tool_type == "filewrite":
            print("Creating TextFileWriterTool")
            return TextFileWriterTool(
                name = self.name,
                description= self.description,
                filename=self.tool_config.get("filename"),
                directory=self.tool_config.get("directory", "./"),
                overwrite=self.tool_config.get("overwrite", "True")
            )
        elif tool_type == "fetchurl":
            
            return URLFetchTool(
                name = self.name,
                description= self.description,
                
            )
        
        
        

        elif tool_type == "websitesearch":
            
            #return WebsiteSearchTool(url=self.tool_config["url"])
            return WebsiteSearchTool()
        elif tool_type == "mdxsearch":  # Novo
            if "mdx" not in self.tool_config:
                raise ValueError("mdx é obrigatório para MDXSearchTool")
            return MDXSearchTool(mdx=self.tool_config["mdx"])
        elif tool_type == "dbquerytool":
            db_config = self.tool_config
            if not db_config:
                raise ValueError("db_config é obrigatório para DBQueryTool")
            return DBQueryTool(
                name = self.name,
                description= self.description,
                host=db_config["host"],
                database=db_config["database"],
                user=db_config["user"],
                password=db_config["password"],
                port=db_config.get("port", 3306)
            )
        elif tool_type == "naturallanguagequerytool":
            print("Retornando NLQ")
            return NaturalLanguageQuery()
        #ATUALIZE
        elif tool_type == "naturallanguagestockcheckertool":
            print("Retornando NLQ STOCK")
            return NaturalLanguageStockCheckerTool()
        #ATUALIZE
        elif tool_type == "emailfetchtool":
            config = self.tool_config
            if not config:
                raise ValueError("db_config é obrigatório para Natural Language Stock Tool")
    
            return EmailFetchTool(
                    server = config["server"],
                    email  = config["email"],
                    password = config["password"]

            )
        #ATUALIZE
        elif tool_type == "emailsendtool":
            config = self.tool_config
            if not config:
                raise ValueError("db_config é obrigatório para Natural Language Stock Tool")
    
            return EmailSendTool(
                    server = config["server"],
                    email  = config["email"],
                    password = config["password"]

            )
        else:
            raise ValueError(f"Tipo de ferramenta não suportado: {self.tool_type}")

class AiTeamAgentx(Agent):
    def __init__(
        self,
        name: str,
        role: str = None,
        goal: str = None,
        backstory: Optional[str] = None,
        tools: Optional[List[Tool]] = None,
        allow_delegation: bool = True,
        verbose: bool = False,
        config: Optional[Dict[str, Any]] = None,
        allow_code_execution:bool=False,
        llm: str = None

    ):
        super().__init__(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            allow_delegation=allow_delegation,
            verbose=verbose,
            config=config,
            allow_code_execution=allow_code_execution, 
            llm=llm
        )
        # Separar ferramentas CrewAI e Phidata
        crewai_tools = []
        phidata_tools = []
        if self.profile.tools:
            for tool in self.profile.tools:
                _, phi_tool = tool.create()  # O método 'create()' retorna ambas as instâncias
                phidata_tools.append(phi_tool)

        

        # Base configuration
        base_config = {
            "name": self.name,
            "role": self.profile.role,
            "goal": self.profile.goal,
            "backstory": self.profile.backstory,
            "tools": crewai_tools,
            "allow_delegation": self.profile.allow_delegation,
            "verbose": self.profile.verbose,
            "allow_code_execution": self.profile.allow_code_execution,
            "llm": self.profile.llm,
        }

        # If there's additional config, merge it with base_config
        if self.profile.config:
            # Remove None values from config to avoid overwriting base_config
            filtered_config = {
                k: v for k, v in self.profile.config.items() if v is not None
            }
            # Merge configs, letting filtered_config override base_config if there are conflicts
            self.final_config = {**base_config, **filtered_config}
            self.crewaiagent = CrewAgent(**self.final_config)
        else:
            self.final_config = {**base_config}
            self.crewaiagent = CrewAgent(**base_config)

    def execute(self, input_data: Any) -> Dict[str, Any]:
        return self.create().execute(input_data)

    def cria_instancia(self) -> CrewAgent:
        return self.crewaiagent
class AiTeamAgent(Agent):
    def __init__(
        self,
        name: str,
        role: str = None,
        goal: str = None,
        backstory: Optional[str] = None,
        tools: Optional[List[Tool]] = None,
        allow_delegation: bool = True,
        verbose: bool = False,
        config: Optional[Dict[str, Any]] = None,
        allow_code_execution:bool=False,
        llm: str = "gpt-4o"

    ):
        super().__init__(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            allow_delegation=allow_delegation,
            verbose=verbose,
            config=config,
            allow_code_execution=allow_code_execution, 
            llm=llm
        )
        crewai_tools = (
            [tool for tool in self.profile.tools] if self.profile.tools else []
        )

        # Base configuration
        base_config = {
            "name": self.name,
            "role": self.profile.role,
            "goal": self.profile.goal,
            "backstory": self.profile.backstory,
            "tools": crewai_tools,
            "allow_delegation": self.profile.allow_delegation,
            "verbose": self.profile.verbose,
            "allow_code_execution": self.profile.allow_code_execution,
            "llm": self.profile.llm,
        }

        # If there's additional config, merge it with base_config
        if self.profile.config:
            # Remove None values from config to avoid overwriting base_config
            filtered_config = {
                k: v for k, v in self.profile.config.items() if v is not None
            }
            # Merge configs, letting filtered_config override base_config if there are conflicts
            self.final_config = {**base_config, **filtered_config}
            self.crewaiagent= CrewAgent(**self.final_config)
        else:  
            self.final_config = {**base_config}
            self.crewaiagent= CrewAgent(**base_config)

    def execute(self, input_data: Any) -> Dict[str, Any]:
        return self.create().execute(input_data)

    def cria_instancia(self) -> CrewAgent:
        return self.crewaiagent
        


class AiTeamAgentant(Agent):
    def __init__(
        self,
        name: str,
        role: str = None,
        goal: str = None,
        backstory: Optional[str] = None,
        tools: Optional[List[Tool]] = None,
        allow_delegation: bool = True,
        verbose: bool = False,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            allow_delegation=allow_delegation,
            verbose=verbose,
            config=config,
        )

    def execute(self, input_data: Any) -> Dict[str, Any]:
        return self.create().execute(input_data)

    def cria_instancia(self) -> CrewAgent:
        crewai_tools = (
            [tool.create() for tool in self.profile.tools] if self.profile.tools else []
        )
        if not self.profile.config:
            return CrewAgent(
                name=self.name,
                role=self.profile.role,
                goal=self.profile.goal,
                backstory=self.profile.backstory,
                tools=crewai_tools,
                allow_delegation=self.profile.allow_delegation,
                verbose=self.profile.verbose,
                config=self.profile.config if self.profile.config else {},
            )
        else:
            return CrewAgent(
                config=self.profile.config,
                tools=crewai_tools,
            )
            """
            return CrewAgent(
                name=self.name,
                tools=crewai_tools,
                **(self.profile.config or {})
            )
            """


class AiTeamProcessingStrategyx(ProcessingStrategy):
    def __init__(
        self,
        complexity_level: str = "default",  # simple, default, complex
        formality_level: str = "default",  # casual, default, formal
        technical_level: str = "default",  # basic, default, technical
        tone: str = "default",  # friendly, default, professional
        detail_level: str = "default",  # concise, default, detailed
    ):
        self.complexity_level = complexity_level
        self.formality_level = formality_level
        self.technical_level = technical_level
        self.tone = tone
        self.detail_level = detail_level

    @abstractmethod
    def process(self, context: Dict[str, Any]) -> CrewTask:
        pass


class AiTeamProcessingStrategy(ProcessingStrategy):
    # Definições de prompts para cada nível
    COMPLEXITY_PROMPTS = {
        "simple": [
            "Break down complex concepts into simple terms",
            "Use basic explanations",
            "Focus on fundamental concepts",
        ],
        "default": [
            "Balance technical and basic concepts",
            "Use moderate level of detail",
            "Explain key concepts when needed",
        ],
        "complex": [
            "Use advanced terminology",
            "Explore complex interactions",
            "Deep dive into technical details",
        ],
    }

    FORMALITY_PROMPTS = {
        "casual": [
            "Use conversational language",
            "Write in a relaxed style",
            "Keep tone informal but professional",
        ],
        "default": [
            "Maintain balanced formality",
            "Use clear professional language",
            "Keep appropriate tone",
        ],
        "formal": [
            "Use formal documentation style",
            "Follow technical writing conventions",
            "Maintain strict professional tone",
        ],
    }

    TECHNICAL_PROMPTS = {
        "basic": [
            "Avoid technical jargon",
            "Use general terms",
            "Focus on practical understanding",
        ],
        "default": [
            "Include relevant technical terms",
            "Balance technical and practical aspects",
            "Provide moderate technical detail",
        ],
        "technical": [
            "Use technical specifications",
            "Include implementation details",
            "Cover architectural aspects",
        ],
    }

    TONE_PROMPTS = {
        "friendly": [
            "Be warm and approachable",
            "Show empathy and understanding",
            "Use encouraging language",
        ],
        "default": [
            "Keep neutral, professional tone",
            "Balance warmth and professionalism",
            "Maintain appropriate distance",
        ],
        "professional": [
            "Maintain strict professionalism",
            "Use formal business tone",
            "Focus on objectivity",
        ],
    }

    DETAIL_PROMPTS = {
        "concise": ["Focus on key points", "Be brief but clear", "Stick to essentials"],
        "default": [
            "Provide balanced detail",
            "Include necessary information",
            "Cover main aspects thoroughly",
        ],
        "detailed": [
            "Include comprehensive details",
            "Cover all aspects thoroughly",
            "Provide extensive information",
        ],
    }

    def __init__(
        self,
        complexity_level: str = "default",  # simple, default, complex
        formality_level: str = "default",  # casual, default, formal
        technical_level: str = "default",  # basic, default, technical
        tone: str = "default",  # friendly, default, professional
        detail_level: str = "default",  # concise, default, detailed
    ):
        self.complexity_level = complexity_level
        self.formality_level = formality_level
        self.technical_level = technical_level
        self.tone = tone
        self.detail_level = detail_level

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        guidelines = []
        guidelines.extend(self.COMPLEXITY_PROMPTS[self.complexity_level])
        guidelines.extend(self.FORMALITY_PROMPTS[self.formality_level])
        guidelines.extend(self.TECHNICAL_PROMPTS[self.technical_level])
        guidelines.extend(self.TONE_PROMPTS[self.tone])
        guidelines.extend(self.DETAIL_PROMPTS[self.detail_level])

        description = (
            f"{context['description']}\n\n"
            f"Guidelines:\n"
            f"{chr(10).join(f'- {g}' for g in guidelines)}"
        )

        output_requirements = [
            f"Complexity: {self.complexity_level}",
            f"Formality: {self.formality_level}",
            f"Technical Level: {self.technical_level}",
            f"Tone: {self.tone}",
            f"Detail Level: {self.detail_level}",
        ]

        expected_output = (
            f"{context['expected_output']}\n\n"
            f"Output Requirements:\n"
            f"{chr(10).join(f'- {r}' for r in output_requirements)}"
        )

        return {"description": description, "expected_output": expected_output}


class AiTeamTask(Task):
    def __init__(
        self,
        description: str = None,
        expected_output: str = None,
        tools: Optional[List[Tool]] = None,
        output_json: Optional[Type[BaseModel]] = None,
        output_file: Optional[str] = None,
        human_input: bool = False,
        async_execution: bool = False,
        context: Optional[List[Task]] = None,  # Novo
        agent: Optional[Agent] = None,
        strategy: Optional[ProcessingStrategy] = None,
        config: Optional[Dict[str, Any]] = None,
        output_pydantic: Optional[Type[BaseModel]] = None,
    ):
        if not agent:
            raise ValueError("Agent é obrigatório para CrewAI Task")
        self.crewai_tools = (
            [tool for tool in tools] if tools else []
        )
        super().__init__(
            description=description,
            expected_output=expected_output,
            tools=self.crewai_tools,
            output_json=output_json,
            output_file=output_file,
            human_input=human_input,
            async_execution=async_execution,
            context=context,  # Novo
            strategy=strategy,
            config=config,
            output_pydantic=output_pydantic,
        )
        if not agent:
            raise ValueError("Agent é obrigatório para CrewAI Task")
        self.agent = agent

        if self.config.strategy:
            context = {
                "description": self.config.description,
                "expected_output": self.config.expected_output,
            }
            processed = self.config.strategy.process(context)
            self.config.description = processed["description"]
            self.config.expected_output = processed["expected_output"]

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print("Na Task:")
        print(self.config.description)
        print(context)
        # Execute the crew
        crew = Crew(
            agents=[self.agent.create()],
            tasks=[self.create()],
            verbose=True
        )

        result = crew.kickoff(context)

        return result
    def cria_instancia(self) -> CrewTask:
        
        print(self.crewai_tools)
        crewai_agent = self.agent.create()

        # Converter context tasks para CrewTasks
        context_tasks = None
        if self.config.context:
            context_tasks = [task.create() for task in self.config.context]

        if not self.config.config:
            # Criar dicionário base sem output_file
            task_args = {
                "description": self.config.description,
                "expected_output": self.config.expected_output,
                "tools": self.crewai_tools,
                "output_json": self.config.output_json,
                "human_input": self.config.human_input,
                "async_execution": self.config.async_execution,
                "context": context_tasks,
                "agent": crewai_agent,
                "config": self.config.config if self.config.config else {},
                "output_pydantic": self.config.output_pydantic,
            }
            
            # Adicionar output_file apenas se não for None
            if self.config.output_file is not None:
                task_args["output_file"] = self.config.output_file

            return CrewTask(**task_args)
        else:
            print("CONFIG")
            print(self.config.config)
            self.config.config["tools"]=self.crewai_tools
            print("TOOLS")
            print(self.crewai_tools)
            self.config.config["agent"]=crewai_agent
            task=CrewTask(
                **self.config.config
            )
            '''
            task=CrewTask(
                tools= self.crewai_tools,
                config=self.config.config,
                agent=crewai_agent,
            )
            '''
            print("TOOLS")
            print(task.tools)
            return task

    def cria_instanciav0(self) -> CrewTask:

        crewai_tools = (
            [tool.create() for tool in self.config.tools] if self.config.tools else []
        )
        crewai_agent = self.agent.create()

        # Converter context tasks para CrewTasks

        context_tasks = None
        if self.config.context:
            context_tasks = [task.create() for task in self.config.context]
        if not self.config.config:
            return CrewTask(
                description=self.config.description,
                expected_output=self.config.expected_output,
                tools=crewai_tools,
                output_json=self.config.output_json,
                output_file=self.config.output_file,
                human_input=self.config.human_input,
                async_execution=self.config.async_execution,
                context=context_tasks,  # Passa a lista de CrewTasks
                agent=crewai_agent,
                config=self.config.config if self.config.config else {},
                output_pydantic=self.config.output_pydantic,
            )
        else:
            return CrewTask(
                config=self.config.config,
                agent=crewai_agent,
            )
import json
from datetime import datetime


class AiTeamTeam(Team):
    """Team corrigido com melhor manipulação de resultados"""

    def __init__(
        self,
        agents: List[Agent],
        tasks: List[Task],
        manager_llm: Optional[Any] = None,
        process: Optional[Process] = None,
        memory: bool = False,
        
        verbose: Union[bool, int] = False,
        nome : str = None,
        memory_system: LangChainFullTaskMemorySystem = None,
    ):
        super().__init__(
            agents=agents,
            tasks=tasks,
            manager_llm=manager_llm,
            process=process,
            memory=memory,
            verbose=verbose,
            nome = nome
        )
        self.memory_system = memory_system
        print("Criando crew context...")
        created_tasks = [task.create() for task in tasks]
        created_agents = [agent.create() for agent in agents]


        self.crew_context = {
            "agents": created_agents,
            "tasks": created_tasks,
            "verbose": verbose,
        }

        if process:
            self.crew_context["process"] = process.create()
        if manager_llm:
            self.crew_context["manager_llm"] = manager_llm
        if memory:
            self.crew_context["memory"] = memory

        self.crew = Crew(**self.crew_context)
        print(self.crew.agents)
        print(self.crew.tasks)
        print(self.crew)

    def executar(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execução genérica do crew que sempre retorna no formato team_result"""
        
        if not self.memory_system:
            print(f"Executing crew with inputs: {inputs}")
            result = self.crew.kickoff(inputs)
            print(f"Crew result: {result}")
            texto = f"{result}" 
            # Garante que o resultado sempre tenha o formato team_result
            if result is not None:
                return {"team_result": texto}
            return result
        else:
            # 1. Se existe sistema de memória, adiciona histórico ao contexto
            if self.memory_system:
                print("EXISTE MEMORY SYSTEM")
                # Busca histórico de execuções por tipo de task
                task_name = self.memory_system.task_name
                print(F"BUSCANDO POR CHAVE {task_name}")
                task_history = self.memory_system.recall(
                    key=f"{task_name}",
                    search_long_term=True
                  
                )
                if (task_history is not None) and isinstance(task_history, list):
                    max_records = inputs.get("max_regs", 10)  # Default 10 se não especificado
                    task_history = sorted(task_history, key=lambda x: x['timestamp'], reverse=True)[:max_records]
                    print(f"Número de Memórias enviadas : {len(task_history)}")
                print(f"task history encontrada e passada ao contexto:{task_history}")
                print("DEPOIS DE TASK HISTORY")
                
                # Adiciona histórico ao contexto para uso na task
                print(f"antes:{inputs}")
                memory_value = task_history if task_history is not None else "NO_HISTORY"
                inputs['memory_system'] = memory_value
                #inputs['memory_system'] = task_history or "Vazio"
            print(f"DEPOIS:{inputs}")
            
            # 2. Executa a task
            result = self.crew.kickoff(inputs)
            print("depois da execucao")

            # 3. Se o resultado contiver formato padrão de task, salva na memória
            #if isinstance(result, dict) and 'task' in result and 'timestamp' in result:
            print("**********SALVANDO NO MEMORY SYSTEM*********")
            
            if self.memory_system:
                print("TIPO:")
                print(type(result))  # Verifica o tipo do objeto
                print("ATRIBUTOS:")
                print(dir(result))   # Lista os atributos e métodos disponíveis no objeto
            



                print(f"result===>{result}")
                result_str = str(result)
                print(f"result_str===>{result_str}")
                # Extrai os valores das chaves
                result_dict = json.loads(result_str)
                html_report = result_dict.get("html", None)  # Relatório em HTML
                json_data = result_dict.get("json", None)
                
                
                print("JSON_DATA")
                print(json_data)

                
                
                
                
                # Converte `json_data` para string e manipula como JSON
                #result_str = str(json_data)
                json_str = json_data.replace("```json", "").replace("```", "").strip()
                result_dict = json.loads(json_str)
                print(f"result_jsonstr===>{result_dict}")
                
                '''
                if isinstance(result, str):
                    result_dict = json.loads(result)
                else:
                    result_dict = json.loads(str(result))                   
                '''
                
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                memory_key = f"{task_name}_{current_timestamp}"
                
                # Formata registro da task
                task_record = {
                    'task': task_name,
                    'timestamp': current_timestamp,
                    'results': result_dict.get('results', [])
                }
                print(f"RECORD A SER SALVO===>:{task_record}")

                
                # Salva histórico atualizado
                
                self.memory_system.remember(
                    key=memory_key,
                    value=task_record,
                    long_term=True
                )


            # Garante retorno consistente no formato team_result (igual ao caso sem memory)
            texto = f"{result}"
            if result is not None:
                return {"team_result": texto}
            return result              
                
                
                

        

    def executaranterior(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execução genérica do crew que sempre retorna no formato team_result"""
        try:
            if not self.memory_system:
                print(f"Executing crew with inputs: {inputs}")
                result = self.crew.kickoff(inputs)
                print(f"Crew result: {result}")
                texto =f"{result}" 
                # Garante que o resultado sempre tenha o formato team_result
                if result is not None:
                    return {"team_result": texto}
                    #return {"team_result": result}
                return result
            else:
                try:
                    # 1. Se existe sistema de memória, adiciona histórico ao contexto
                    if self.memory_system:
                        print("EXISTE MEMORY SYSTEM")
                        # Busca histórico de execuções por tipo de task
                        task_name = self.memory_system.task_name
                        task_history = self.memory_system.recall(
                            key=f"{task_name}",
                            search_long_term=True
                        )
                        print("DEPOIS DE TASK HISTORY")
                        # Adiciona histórico ao contexto para uso na task
                        print(f"antes:{inputs}")
                        # Correção: Garante que o valor não seja uma string vazia
                        memory_value = task_history if task_history is not None else {}
                        inputs['memory_system'] = memory_value
                        #inputs['memory_system'] = task_history or "Vazio"
                    print(f"DEPOIS:{inputs}")
                    # 2. Executa a task
                    result = self.crew.kickoff(inputs)
                    print("depois da execucao")

                    # 3. Se o resultado contiver formato padrão de task, salva na memória
                    if isinstance(result, dict) and 'task' in result and 'timestamp' in result:
                        if self.memory_system:
                            memory_key = f"{task_name}"
                            
                            # Recupera histórico existente
                            
                            
                            # Formata registro da task
                            task_record = {
                                'task': result['task'],
                                'timestamp': result['timestamp'],
                                'results': result.get('results', [])
                            }
                            
                            
                            
                            # Salva histórico atualizado
                            self.memory_system.remember(
                                key=memory_key,
                                value=task_record,
                                long_term=True
                            )

                    return result
                
                except Exception as e:
                    print(f"Erro na execução da task: {str(e)}")
                    traceback.print_exc()
                    return {
                        "error": str(e),
                        "status": "failed",
                        "task_id": self.task_id
                    }
                

        except Exception as e:
            print(f"Error executing team: {str(e)}")
            raise

    def executarespec(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execução corrigida com formatação consistente dos resultados"""
        try:
            print(f"Executing crew with inputs: {inputs}")

            # Garante que inputs esteja no formato esperado
            if isinstance(inputs, dict) and "leads" in inputs:
                crew_inputs = inputs
            else:
                crew_inputs = {
                    "leads": inputs if isinstance(inputs, list) else [inputs]
                }

            result = self.crew.kickoff(crew_inputs)
            print(f"Crew result: {result}")

            # Garante resultado formatado
            if result is not None:
                if not isinstance(result, dict):
                    result = {"team_result": result}
                if "team_result" in result and not isinstance(
                    result["team_result"], list
                ):
                    result["team_result"] = [result["team_result"]]

            return result

        except Exception as e:
            print(f"Error executing team: {str(e)}")
            raise

    def cria_instancia(self) -> Crew:
        return self.crew

    def usage_metrics(self):
        return self.crew.usage_metrics
    def test(self, n_iterations: int = 1, openai_model_name: str = None) -> Dict[str, Any]:
        """Utiliza o método test do Crew"""
        # Como self.crew já é uma instância de Crew, podemos usar seu método test diretamente
        return self.crew.test(n_iterations=n_iterations, openai_model_name=openai_model_name)

    def train(self, n_iterations: int = 1, filename: str = None) -> Dict[str, Any]:
        """Utiliza o método train do Crew"""
        # Da mesma forma, usamos o método train do Crew diretamente
        return self.crew.train(n_iterations=n_iterations, filename=filename)


class AiTeamTeamv0(Team):
    def __init__(
        self,
        agents: List[Agent],
        tasks: List[Task],
        manager_llm: Optional[Any] = None,
        process: Optional[Process] = None,
        memory: bool = False,
        verbose: int = 0,
    ):
        super().__init__(
            agents=agents,
            tasks=tasks,
            manager_llm=manager_llm,
            process=process,
            memory=memory,
            verbose=verbose,
        )

        print("Criando crew context...")
        # Criar as tasks uma única vez
        created_tasks = [task.create() for task in tasks]
        created_agents = [agent.create() for agent in agents]

        # Usar as mesmas tasks criadas
        self.crew_context = {
            "agents": created_agents,
            "tasks": created_tasks,
            "verbose": verbose,
        }

        if process:
            self.crew_context["process"] = process.create()
        if manager_llm:
            self.crew_context["manager_llm"] = manager_llm
        if memory:
            self.crew_context["memory"] = memory

        self.crew = Crew(**self.crew_context)

    def cria_instancia(self) -> Crew:
        return self.crew

    def usage_metrics(self):
        return self.crew.usage_metrics

    def executar(self, inputs: Dict[str, Any]) -> Dict[str, Any]:

        return {"team_result": self.crew.kickoff(inputs)}


from frameworkagents import Pipeline
from typing import List, Dict, Any, Optional, Union, Callable
from enum import Enum
from abc import ABC, abstractmethod


class OperationType(Enum):
    START = "start"
    LISTEN = "listen"
    ROUTER = "router"


class PipelineCommand(ABC):
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        pass


class PipelineStep:
    def __init__(
        self,
        operation: PipelineCommand,
        operation_type: OperationType,
        dependencies: List["PipelineStep"] = None,
        paths: List[str] = None,
    ):
        self.operation = operation
        self.operation_type = operation_type
        self.dependencies = dependencies or []
        self.paths = paths or []
        self.observers: List["PipelineStep"] = []

    def add_observer(self, observer: "PipelineStep"):
        self.observers.append(observer)

    def notify_observers(self, result: Any):
        for observer in self.observers:
            observer.operation.execute(result)


class AndCommand(PipelineCommand):
    def __init__(self, operations, name):
        self.operations = operations
        self.name = name

    def execute(self, input_data=None):
        results = [operation(input_data) for operation in self.operations]
        return all(results)


class OrCommand(PipelineCommand):
    def __init__(self, operations, name):
        self.operations = operations
        self.name = name

    def execute(self, input_data=None):
        results = [operation(input_data) for operation in self.operations]
        return any(results)


class AiTeamPipelinex(Pipeline):
    def __init__(self):
        super().__init__()
        self.step_counter = 0
        self.routes = {}
        self.state = {}

    def _generate_step_name(self, prefix: str = "step") -> str:
        self.step_counter += 1
        return f"{prefix}_{self.step_counter}"

    def _normalize_crew_result(self, result: Any) -> Any:
        """Normaliza resultados do CrewAI mantendo formato consistente"""
        if isinstance(result, dict):
            if "team_result" in result:
                result = result["team_result"]
                if result and not isinstance(result, list):
                    result = [result]
        return result

    def _store_step_result(self, step_name: str, result: Any):
        """Armazena resultado no estado de forma segura"""
        if result is not None:
            normalized = self._normalize_crew_result(result)
            self.state[step_name] = (
                normalized if isinstance(normalized, list) else [normalized]
            )

    def add_step(
        self,
        name: str,
        operation: Callable,
        operation_type: OperationType,
        dependencies: List[str] = None,
        paths: List[str] = None,
    ):
        def wrapped_operation(input_data):
            try:
                # Normaliza input se vier do CrewAI
                if isinstance(input_data, dict) and "team_result" in input_data:
                    input_data = input_data["team_result"]

                result = operation(input_data)

                # Armazena resultado normalizado
                self._store_step_result(name, result)

                return result
            except Exception as e:
                print(f"Error in step {name}: {str(e)}")
                raise

        command = type(
            f"{name}Command",
            (PipelineCommand,),
            {"execute": lambda self, input_data: wrapped_operation(input_data)},
        )()

        step = PipelineStep(
            operation=command,
            operation_type=operation_type,
            dependencies=[self.steps[dep] for dep in (dependencies or [])],
            paths=paths,
        )

        if operation_type == OperationType.START:
            self.start_step = step

        self.steps[name] = step

        if dependencies:
            for dep in dependencies:
                if dep in self.steps:
                    self.steps[dep].add_observer(step)

        return step

    def start(self):
        def decorator(func):
            def wrapped_func(input_data=None):
                try:
                    result = func()
                    # Garante que resultado inicial está em formato adequado
                    if result is not None and not isinstance(result, dict):
                        result = {"initial_data": result}
                    return result
                except Exception as e:
                    print(f"Error in start step: {str(e)}")
                    raise

            return self.add_step(func.__name__, wrapped_func, OperationType.START)

        return decorator

    def listen(self, *dependencies):
        def decorator(func):
            dep_names = []
            for dep in dependencies:
                if isinstance(dep, str):
                    if dep in self.routes:
                        dep_names.append(dep)
                    continue
                elif isinstance(dep, PipelineStep):
                    for name, step in self.steps.items():
                        if step == dep:
                            dep_names.append(name)
                            break
                else:
                    dep_names.append(dep.__name__)

            return self.add_step(
                func.__name__, func, OperationType.LISTEN, dependencies=dep_names
            )

        return decorator

    def router(self, dependency, paths: List[str]):
        def decorator(func):
            step_name = func.__name__
            self.routes[step_name] = paths

            dep_name = None
            if isinstance(dependency, PipelineStep):
                for name, step in self.steps.items():
                    if step == dependency:
                        dep_name = name
                        break
            elif isinstance(dependency, (AndCommand, OrCommand)):
                dep_name = self._generate_step_name("router_dep")
                self.add_step(dep_name, dependency.execute, OperationType.LISTEN)
            else:
                dep_name = dependency.__name__

            return self.add_step(
                step_name,
                func,
                OperationType.ROUTER,
                dependencies=[dep_name] if dep_name else None,
                paths=paths,
            )

        return decorator

    def and_(self, *operations) -> PipelineCommand:
        step_name = self._generate_step_name("and")
        command = AndCommand(operations, step_name)
        self.add_step(step_name, command.execute, OperationType.LISTEN)
        return command

    def or_(self, *operations) -> PipelineCommand:
        step_name = self._generate_step_name("or")
        command = OrCommand(operations, step_name)
        self.add_step(step_name, command.execute, OperationType.LISTEN)
        return command

    def execute(self) -> Any:
        if not self.start_step:
            raise ValueError("No start step defined")

        try:
            result = self.start_step.operation.execute(None)
            if result is not None:
                self._store_step_result("start_result", result)
            self.start_step.notify_observers(result)
            return result
        except Exception as e:
            print(f"Error executing pipeline: {str(e)}")
            raise

    def get_step_result(self, step_name: str, index: int = None) -> Any:
        """Acesso seguro aos resultados de um step"""
        try:
            results = self.state.get(step_name, [])
            if not results:
                return None
            if index is not None:
                return results[index] if 0 <= index < len(results) else None
            return results
        except Exception as e:
            print(f"Error accessing step result {step_name}: {str(e)}")
            return None

    def cria_instancia(self) -> "AiTeamPipeline":
        if not hasattr(self, "steps"):
            self.steps = {}
        if not hasattr(self, "start_step"):
            self.start_step = None
        if not hasattr(self, "state"):
            self.state = {}
        return self


class AiTeamPipeline(Pipeline):
    def __init__(self):
        super().__init__()
        self.step_counter = 0
        self.routes = {}
        self.state = {}

    def _generate_step_name(self, prefix: str = "step") -> str:
        self.step_counter += 1
        return f"{prefix}_{self.step_counter}"

    def add_step(
        self,
        name: str,
        operation: Callable,
        operation_type: OperationType,
        dependencies: List[str] = None,
        paths: List[str] = None,
    ):
        def wrapped_operation(input_data):
            # Se for método start, não passa parâmetro
            if operation_type == OperationType.START:
                return operation()
            # Para outros métodos, passa o input_data
            return operation(input_data)

        command = type(
            f"{name}Command",
            (PipelineCommand,),
            {"execute": lambda self, input_data: wrapped_operation(input_data)},
        )()

        step = PipelineStep(
            operation=command,
            operation_type=operation_type,
            dependencies=[self.steps[dep] for dep in (dependencies or [])],
            paths=paths,
        )

        if operation_type == OperationType.START:
            self.start_step = step

        self.steps[name] = step

        if dependencies:
            for dep in dependencies:
                if dep in self.steps:
                    self.steps[dep].add_observer(step)

        return step

    def start(self):
        def decorator(func):
            return self.add_step(func.__name__, func, OperationType.START)

        return decorator

    def listen(self, *dependencies):
        def decorator(func):
            dep_names = []
            for dep in dependencies:
                if isinstance(dep, str):
                    if dep in self.routes:
                        # Se for uma rota, usa o nome dela
                        dep_names.append(dep)
                    continue
                elif isinstance(dep, PipelineStep):
                    for name, step in self.steps.items():
                        if step == dep:
                            dep_names.append(name)
                            break
                else:
                    dep_names.append(dep.__name__)

            return self.add_step(
                func.__name__, func, OperationType.LISTEN, dependencies=dep_names
            )

        return decorator

    def and_(self, *operations) -> PipelineStep:
        step_name = self._generate_step_name("and")

        def and_operation(input_data):
            results = []
            for op in operations:
                if isinstance(op, PipelineStep):
                    result = op.operation.execute(input_data)
                else:
                    result = op(input_data)
                results.append(result)
            return results if all(results) else None

        deps = []
        for op in operations:
            if isinstance(op, PipelineStep):
                for name, step in self.steps.items():
                    if step == op:
                        deps.append(name)
                        break
            else:
                deps.append(op.__name__)

        step = self.add_step(
            step_name, and_operation, OperationType.LISTEN, dependencies=deps
        )
        return step

    def or_(self, *operations) -> PipelineStep:
        step_name = self._generate_step_name("or")

        def or_operation(input_data):
            for op in operations:
                if isinstance(op, PipelineStep):
                    result = op.operation.execute(input_data)
                else:
                    result = op(input_data)
                if result:
                    return result
            return None

        deps = []
        for op in operations:
            if isinstance(op, PipelineStep):
                for name, step in self.steps.items():
                    if step == op:
                        deps.append(name)
                        break
            else:
                deps.append(op.__name__)

        step = self.add_step(
            step_name, or_operation, OperationType.LISTEN, dependencies=deps
        )
        return step

    def router(self, dependency, paths: List[str]):
        def decorator(func):
            step_name = func.__name__
            self.routes[step_name] = paths

            dep_name = None
            if isinstance(dependency, PipelineStep):
                for name, step in self.steps.items():
                    if step == dependency:
                        dep_name = name
                        break
            else:
                dep_name = dependency.__name__

            return self.add_step(
                step_name,
                func,
                OperationType.ROUTER,
                dependencies=[dep_name] if dep_name else None,
            )

        return decorator

    def execute(self) -> Any:
        if not self.start_step:
            raise ValueError("No start step defined")

        result = self.start_step.operation.execute(None)
        self.start_step.notify_observers(result)
        return result

    def cria_instancia(self) -> "AiTeamPipeline":
        if not hasattr(self, "steps"):
            self.steps = {}
        if not hasattr(self, "start_step"):
            self.start_step = None
        return self


class AiTeamPipelinev0(Pipeline):
    def __init__(self):
        super().__init__()
        self.step_counter = 0

    def _generate_step_name(self, prefix: str = "step") -> str:
        self.step_counter += 1
        return f"{prefix}_{self.step_counter}"

    def add_step(
        self,
        name: str,
        operation: Callable,
        operation_type: OperationType,
        dependencies: List[str] = None,
        paths: List[str] = None,
    ):
        def wrapped_operation(input_data):
            try:
                return operation(input_data)
            except TypeError:
                return operation()

        command = type(
            f"{name}Command",
            (PipelineCommand,),
            {"execute": lambda self, input_data: wrapped_operation(input_data)},
        )()

        step = PipelineStep(
            operation=command,
            operation_type=operation_type,
            dependencies=[self.steps[dep] for dep in (dependencies or [])],
            paths=paths,
        )

        if operation_type == OperationType.START:
            self.start_step = step

        self.steps[name] = step

        if dependencies:
            for dep in dependencies:
                self.steps[dep].add_observer(step)

        return step

    def start(self):
        def decorator(func):
            return self.add_step(func.__name__, func, OperationType.START)

        return decorator

    def listen(self, *dependencies):
        def decorator(func):
            dep_names = []
            for dep in dependencies:
                if isinstance(dep, PipelineStep):
                    for name, step in self.steps.items():
                        if step == dep:
                            dep_names.append(name)
                            break
                elif isinstance(dep, (AndCommand, OrCommand)):
                    step_name = self._generate_step_name("composite")
                    self.add_step(step_name, dep.execute, OperationType.LISTEN)
                    dep_names.append(step_name)
                else:
                    dep_names.append(dep.__name__)

            return self.add_step(
                func.__name__, func, OperationType.LISTEN, dependencies=dep_names
            )

        return decorator

    def and_(self, *operations) -> PipelineCommand:
        return AndCommand(operations, self._generate_step_name("and"))

    def or_(self, *operations) -> PipelineCommand:
        return OrCommand(operations, self._generate_step_name("or"))

    def router(self, dependency, paths: List[str]):
        def decorator(func):
            dep_name = None
            if isinstance(dependency, PipelineStep):
                for name, step in self.steps.items():
                    if step == dependency:
                        dep_name = name
                        break
            elif isinstance(dependency, (AndCommand, OrCommand)):
                dep_name = self._generate_step_name("router_dep")
                self.add_step(dep_name, dependency.execute, OperationType.LISTEN)
            else:
                dep_name = dependency.__name__

            if dep_name is None:
                raise ValueError("Dependency not found in pipeline steps")

            return self.add_step(
                func.__name__,
                func,
                OperationType.ROUTER,
                dependencies=[dep_name],
                paths=paths,
            )

        return decorator

    def execute(self) -> Any:
        if not self.start_step:
            raise ValueError("No start step defined")

        result = self.start_step.operation.execute(None)
        self.start_step.notify_observers(result)
        return result

    def cria_instancia(self) -> "AiTeamPipeline":
        if not hasattr(self, "steps"):
            self.steps = {}
        if not hasattr(self, "start_step"):
            self.start_step = None
        if not hasattr(self, "state"):
            self.state = {}
        return self




# Finalizando com a Factory principal
class FrameworkAdapterFactory:
    """Factory para selecionar conjunto de adaptadores do framework"""

    @staticmethod
    def get_framework_adapters(version: str = "crewai", api_key: Optional[str] = None):
        """
        Retorna as classes de adaptadores do framework na versão especificada

        Args:
            version: Versão do framework adapter ("crewai", "default", etc)
            api_key: API key para serviços que necessitem
        """
        if version == "crewai":
            return {
                "memory_system": LangChainFullTaskMemorySystem,
                "agent": AiTeamAgent,
                "task": AiTeamTask,
                "team": AiTeamTeam,
                "tool": AiTeamTool,
                "strategy": AiTeamProcessingStrategy,
                "process": AiTeamProcess,
                "processtype": ProcessType,
                "basetool": AiTeamBaseTool,
                "pipeline": AiTeamPipeline,
                "memory_factory": AiTeamMemorySystemFactory,
            }

        elif version == "default":
            from framework import (
                AgentMemorySystem,
                Agent,
                Task,
                Tool,
                Team,
                ProcessingStrategy,
                Process,
            )

            return {
                "memory_system": AgentMemorySystem,
                "agent": Agent,
                "task": Task,
                "team": Team,
                "tool": Tool,
                "strategy": ProcessingStrategy,
                "process": Process,
            }

        else:
            raise ValueError(f"Versão de framework adapter desconhecida: {version}")
