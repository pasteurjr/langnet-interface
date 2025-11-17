# frameworkagentsadapter.py - Parte 1: Imports e início do sistema de memória
from frameworkagentsadapter import (
AiTeamAgent, AiTeamTask,AiTeamBaseTool, AiTeamProcess, 
AiTeamPipeline, AiTeamTeam, AiTeamTool,AiTeamProcessingStrategy,
)
from frameworkmemory import LangChainAgentMemorySystem,LangChainLongTermAdapter,LangChainMemorySystemFactory,LangChainContextAdapter 
from frameworkmemorylcf import AiTeamMemorySystemFactory,LangChainFullTaskMemorySystem, LangChainFullContextAdapter,LangChainFullLongTermAdapter,LangChainFullShortTermAdapter

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union, Optional, Callable,Type
from pathlib import Path
from collections import deque
from datetime import datetime
import pickle
import traceback
from pydantic import BaseModel
import inspect
import os
import frameworkagentsadapter
# Imports LangChain
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
)
from langchain_openai import OpenAI

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
from phi.agent import Agent as PhiAgent
from phi.model.openai import OpenAIChat


from phi.tools.firecrawl import FirecrawlTools  # Ferramenta para scraping de websites
from phi.tools.website import WebsiteTools  # Ferramenta para busca e leitura de websites
from phi.tools.file import FileTools  # Ferramenta para manipulação de arquivos
from phi.tools.duckduckgo import DuckDuckGo  # Ferramenta para buscas na web
from phi.tools.serpapi_tools import SerpApiTools

import os
# Utilização da ferramenta
from phi.agent import Agent
from phi.tools import Toolkit

from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools

from crewai_tools import MDXSearchTool

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



class MDXSearchToolkit(Toolkit):
    def __init__(self, mdx_path: str):
        super().__init__(name="mdx_search_toolkit")
        self.mdx_path = mdx_path
        self.register(self.semantic_search_resume)

    def semantic_search_resume(self, search_query: str):
        """
        Realiza uma busca semântica em um arquivo MDX usando o MDXSearchTool do CrewAI.

        Args:
            search_query (str): Termo de busca.

        Returns:
            str: Resultados formatados da busca como string.
        """
        print(f"mdx_path utilizado: {self.mdx_path}")
        print(f"search_query recebido: {search_query}")

        if not self.mdx_path:
            raise ValueError("O caminho para o arquivo MDX é obrigatório.")

        if not os.path.isfile(self.mdx_path):
            raise FileNotFoundError(f"O arquivo especificado não foi encontrado: {self.mdx_path}")

        mdx_tool = MDXSearchTool(mdx=self.mdx_path)

        try:
            results = mdx_tool.run(search_query=search_query)
        except Exception as e:
            raise RuntimeError(f"Erro ao executar a busca semântica: {e}")

        # Formatar os resultados como string para compatibilidade
        formatted_results = f"Query: {search_query}\nTotal Matches: {len(results)}\nResults:\n"
        formatted_results += "\n".join(results)  # Adiciona os resultados linha por linha
        
        return formatted_results
import mysql.connector
from mysql.connector import Error
from phi.tools import Toolkit
#ATUALIZE
from frameworkagentsadapter import MindsDbQuery,MindsDbProductStock,NaturalLanguageStockCheckerTool,EmailFetchTool,EmailSendTool

class NaturalLanguageQueryPhi(Toolkit):
    def __init__(self):
                super().__init__(name="natural_language_db")
                self.register(self.run_question)
        
    def run_question(self, question: str) -> str:
        return MindsDbQuery(question)
    
class NaturalLanguageStockCheckerToolPhi(Toolkit):
    def __init__(self):
                super().__init__(name="natural_language_stock_shecker_tool")
                self.register(self.run_product_checker)
        
    def run_product_checker(self, product_name: str) -> str:
        stock_query = f"""
        Para o produto '{product_name}', retorne apenas:
        1. Nome exato do produto mais similar
        2. Quantidade em estoque
        3. Se houver outros produtos similares, liste no máximo 2
        Formato: PRODUTO: [nome], ESTOQUE: [quantidade]
        """
        return NaturalLanguageStockCheckerTool()._run(stock_query)
    

class EmailFetchToolPhi(Toolkit):
    def __init__(self):
                super().__init__(name="email_fetch_tool")
                self.register(self.run_fetch_email)
        
    def run_fetch_email(self, product_name: str) -> str:
        
        return "fetch"

class EmailSenderToolPhi(Toolkit):
    def __init__(self):
                super().__init__(name="email_sender_tool")
                self.register(self.run_send_email)
        
    def run_send_email(self, product_name: str) -> str:
        
        return "sent"






class FileReaderTool(Toolkit):
    
    def __init__(self, filename: str, directory: str = "./"):
        super().__init__(name="file_reader_tool")
        self.filename = filename
        self.directory = directory
        
        self.readtool = FileTools(base_dir=self.directory)
        self.register(self.read_file)
    def read_file(self) -> str:
        try:
            return self.readtool.read_file(file_name=self.filename)
        except Exception as e:
            return f"Error Reading file: {e}"


class FileWriterTool(Toolkit):
    
    def __init__(self, filename: str, directory: str = "./", overwrite: str = "True"):
        super().__init__(name="file_writer_tool")
        self.filename = filename
        self.directory = directory
        self.overwrite = overwrite
        self.writetool = FileTools(base_dir=self.directory)
        self.register(self.save_file)
    def save_file(self, contents: str) -> str:
        try:
            return self.writetool.save_file(contents=contents,file_name=self.filename,overwrite=self.overwrite)
        except Exception as e:
            return f"Error saving to file: {e}"
class DBQueryToolkit(Toolkit):
    def __init__(self, db_config: Dict[str, Any]):
        """
        Ferramenta Phidata para executar queries SQL em um banco de dados.

        Args:
            db_config (Dict[str, Any]): Configurações do banco de dados.
        """
        super().__init__(name="db_query_toolkit")
        self.db_config = db_config
        self.register(self.run_query)

    def run_query(self, query: str) -> str:
        """
        Executa uma query SQL no banco de dados MySQL.

        Args:
            query (str): Query SQL a ser executada.

        Returns:
            str: Resultados ou mensagem de erro formatada.
        """
        try:
            connection = mysql.connector.connect(
                host=self.db_config.get("host"),
                database=self.db_config.get("database"),
                user=self.db_config.get("user"),
                password=self.db_config.get("password"),
                port=self.db_config.get("port", 3306),
            )

            cursor = connection.cursor()
            cursor.execute(query)

            # Capturar resultados se for um SELECT
            if query.strip().lower().startswith("select"):
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                output = [dict(zip(column_names, row)) for row in results]
                return f"Query Results: {output}"
            else:
                connection.commit()
                return "Query executed successfully (no results returned)."

        except Error as e:
            return f"Error while executing query: {str(e)}"

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()


class HybridToolAdapter(AiTeamTool):
    def __init__(
        self,
        name: str,
        description: str,
        tool_type: str,
        tool_config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name=name, description=description,tool_type=tool_type ,tool_config=tool_config)
        self.tool_type = tool_type
    def cria_instancia(self) -> tuple:
        crewai_tool = super().cria_instancia()
        """
        Cria e retorna instâncias sincronizadas de ferramentas para CrewAI e Phidata.
        """
        tool_type = self.tool_type.lower()
        
        print(f"********CRIANDO PHIDATA TOOL {tool_type}")
        if tool_type == "scrapewebsite":
                          
            phidata_tool=FirecrawlTools(scrape=True, crawl=False)
            
        elif tool_type == "serperdev":
            
            
            phidata_tool = SerpApiTools()
            

        elif tool_type == "fileread":
            # Ferramentas para leitura de arquivos
            file_path = self.tool_config.get("file_path")
            if not file_path:
                raise ValueError("file_path é obrigatório para FileReadTool")
            phidata_tool = FileReaderTool(filename=file_path).read_file
        elif tool_type == "filewrite":
            # Ferramentas para gravar texto em arquivos
            #file_path = self.tool_config.get("file_path")
            #if not file_path:
            #    raise ValueError("file_path é obrigatório para FileReadTool")
            phidata_tool= FileWriterTool(
                filename=self.tool_config.get("filename"),
                directory=self.tool_config.get("directory", "./"),
                overwrite=self.tool_config.get("overwrite", "True")
            ).save_file
            #phidata_tool = FileTools()
            

        elif tool_type == "websitesearch":
            # Ferramentas para busca em websites
            #url = self.tool_config.get("url")
            #if not url:
            #    raise ValueError("url é obrigatório para WebsiteSearchTool e WebsiteTools")
            
            website_tools = WebsiteTools()
            phidata_tool = website_tools
            

        elif tool_type == "mdxsearch":
            # Ferramentas para consultas avançadas (SQL no Phidata)
            mdx = self.tool_config.get("mdx")
            if not mdx:
                raise ValueError("mdx é obrigatório para MDXSearchTool")
            
            phidata_tool = MDXSearchToolkit(mdx_path=mdx).semantic_search_resume  # Caso não exista um equivalente direto no Phidata
        elif tool_type == "dbquerytool":
            db_config = self.tool_config
            if not db_config:
                raise ValueError("db_config é obrigatório para DBQueryToolkit")

            # Instância para Phidata
            phidata_tool = DBQueryToolkit(db_config=db_config).run_query
        elif tool_type == "naturallanguagequerytool":
            phidata_tool = NaturalLanguageQueryPhi().run_question
        #ATUALIZE
        elif tool_type == "naturallanguagestockcheckertool":
            print("Retornando NLQ STOCK")
            phidata_tool= NaturalLanguageStockCheckerToolPhi().run_product_checker
        #ATUALIZE
        elif tool_type == "emailfetchtool":
            config = self.tool_config
            if not config:
                raise ValueError("db_config é obrigatório para Natural Language Stock Tool")
    
            phidata_tool= EmailFetchToolPhi(
                    
            ).run_fetch_email
        #ATUALIZE
        elif tool_type == "emailsendtool":
            config = self.tool_config
            if not config:
                raise ValueError("db_config é obrigatório para Natural Language Stock Tool")
    
            phidata_tool= EmailSenderToolPhi(
                    
            ).run_send_email
        else:
            raise ValueError(f"Tipo de ferramenta não suportado: {self.tool_type}")
        print("FERRAMENTAS RETORNADAS")
        print("crewai_tool")
        print(crewai_tool)
        print("phidata_tool")
        print(phidata_tool)
        return crewai_tool,phidata_tool
    

from phi.agent import Agent as PhidataAgent
from phi.model.openai.chat import OpenAIChat


class   HybridAgentAdapter(AiTeamAgent):
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
        allow_code_execution: bool = False,
        llm: str = "gpt-4o",
        instructions: Optional[List[str]] = None,
        show_tool_calls: bool = False,  # Mostrar chamadas às ferramentas
        markdown: bool = False,  # Respostas em Markdown
        
    ):
        crewai_tools = []
        if tools:
            for tool in tools:
                crewai_tool, _ = tool
                crewai_tools.append(crewai_tool)
        super().__init__(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            tools=crewai_tools,
            allow_delegation=allow_delegation,
            verbose=verbose,
            config=config,
            allow_code_execution=allow_code_execution,
            llm=llm,
        )

        # Criar o campo role para o agente Phidata
        
        rolephi = f"You are a {self.final_config['role']}. {self.final_config['backstory']} So, {self.final_config['goal']}"

        # Separar ferramentas para Phidata
        phidata_tools = []
        if tools:
            for tool in tools:
                _, phi_tool = tool
                phidata_tools.append(phi_tool)

        # Configuração para Phidata
        print(self.final_config['llm'])
        # Extract model name from llm object if it's not a string
        llm_model = self.final_config['llm']
        if hasattr(llm_model, 'model_name'):
            llm_id = llm_model.model_name
        elif isinstance(llm_model, str):
            llm_id = llm_model
        else:
            llm_id = "gpt-4-turbo-preview"  # fallback

        phidata_config = {
            "name": self.final_config['name'],
            "role": rolephi,
            "model": OpenAIChat(id=llm_id),
            "tools": phidata_tools,
            "instructions": instructions or ["Use tables to display data"],
            "show_tool_calls": show_tool_calls,
            "markdown": markdown,
        }

        # Instanciar o agente Phidata
        self.phi_agent = PhidataAgent(**phidata_config)

    def cria_instancia_hibrida(self) -> PhidataAgent:
        """
        Retorna a instância do agente Phidata.
        """
        return self.phi_agent

    
    

    
from phi.playground import Playground, serve_playground_app
from phi.playground import Playground, serve_playground_app
from typing import List, Optional


class InterfaceUIAdapter:
    def __init__(self, agents: List[AiTeamAgent], team: Optional[AiTeamTeam] = None, app_name: str = "playground"):
        """
        Adapta uma lista de agentes do framework para integração com a interface do playground do Phidata.

        Args:
            agents (List[AiTeamAgent]): Lista de agentes do tipo AiTeamAgent
            team (Optional[AiTeamTeam]): Time de agentes (opcional)
            app_name (str): Nome do arquivo Python onde o app será configurado (sem extensão .py)
        """
        # Converte os agentes híbridos em instâncias do agente Phidata
        self.phi_agents = [agent.cria_instancia_hibrida() for agent in agents]
        
        # Adiciona o agente do time se fornecido
        if team and hasattr(team, 'phi_team'):
            self.phi_agents.append(team.phi_team)
        
        # Configura o playground com os agentes Phidata
        self.playground = Playground(agents=self.phi_agents)
        self.app_name = app_name

    def get_app(self):
        """
        Retorna o aplicativo configurado do playground.
        
        Returns:
            FastAPI: Aplicativo FastAPI configurado
        """
        return self.playground.get_app()

    def serve_app(self, reload: bool = True, port: int = 7777):
        """
        Serve o aplicativo usando o servidor do playground.

        Args:
            reload (bool): Indica se o aplicativo deve ser recarregado automaticamente
            port (int): Porta onde o aplicativo será servido
        """
        app = self.get_app()
        app_path = f"{self.app_name}:app"
        
        try:
            serve_playground_app(
                app_path,
                reload=reload,
                port=port
            )
        except Exception as e:
            print(f"Erro ao iniciar o servidor: {str(e)}")
            raise

    def roda_app_agentes(self, reload: bool = True, port: int = 7777):
        """
        Método alternativo para iniciar o aplicativo.
        Alias mais amigável para serve_app.

        Args:
            reload (bool): Indica se o aplicativo deve ser recarregado automaticamente
            port (int): Porta onde o aplicativo será servido
        """
        self.serve_app(reload=reload, port=port)

    @property
    def agentes(self):
        """
        Retorna a lista de agentes Phidata configurados.

        Returns:
            List: Lista de agentes Phidata
        """
        return self.phi_agents


         

    
class HybridTaskAdapter(AiTeamTask):
    def __init__(
        self,
        description: str = None,
        expected_output: str = None,
        tools: Optional[List[Tool]] = None,
        output_json: Optional[Type[BaseModel]] = None,
        output_file: Optional[str] = None,
        human_input: bool = False,
        async_execution: bool = False,
        context: Optional[List[AiTeamTask]] = None,
        agent: Optional[HybridAgentAdapter] = None,
        strategy: Optional[ProcessingStrategy] = None,
        config: Optional[Dict[str, Any]] = None,
        output_pydantic: Optional[Type[BaseModel]] = None,
    ):
        if not agent:
            raise ValueError("Agent é obrigatório para HybridTaskAdapter")
        print("TOOLS")
        print(tools)
        crewai_tools = [crewait for crewait, phidatat in tools] if tools else []
        phidata_tools = [phidatat for crewait, phidatat in tools] if tools else []

        super().__init__(
            description=description,
            expected_output=expected_output,
            tools=crewai_tools,
            output_json=output_json,
            output_file=output_file,
            human_input=human_input,
            async_execution=async_execution,
            context=context,
            agent=agent,
            strategy=strategy,
            config=config,
            output_pydantic=output_pydantic,
        )

        # Inicializar a instância híbrida do agente Phidata
        self.agent.phi_agent = self.atualiza_instancia_hibrida_agente()

    def atualiza_instancia_hibrida_agente(self) -> PhiAgent:
        """
        Retorna uma instância do agente Phidata atualizado com as instruções da tarefa.
        """
        # Obter a instância do agente Phidata
        phi_agent = self.agent.cria_instancia_hibrida()

        # Atualizar as instruções do agente Phidata com os dados da tarefa
        task_instructions = [
            f"Task Description: {self.config.description}",
            f"Expected Output: {self.config.expected_output}",
        ]

        # Adicionar as instruções ao agente Phidata
        phi_agent.instructions = task_instructions + (phi_agent.instructions or [])

        return phi_agent

    def execute_hibrido(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a tarefa híbrida utilizando o agente Phidata.

        Args:
            context (Dict[str, Any]): Contexto adicional para a tarefa.

        Retorna:
            Dict[str, Any]: Resultado da execução.
        """
        # Usar a instância do agente Phidata para execução
        return self.agent.phi_agent.run(context)
    def print_response(self, input_data: str,images: Optional[List[str]] = None, stream: bool = False,show_message: bool = False,):
        """
        Redireciona para o método print_response do agente Phidata.
        """
        current_images = images
        return self.agent.phi_agent.print_response(input_data,images=current_images, stream=stream,show_message=show_message)

    def format_response(
        self,
        input_data: Any,
        images: Optional[List[str]] = None,
        additional_instructions: Optional[List[str]] = None,
        stream: bool = False,
        show_message: bool = False,
        llm: str = "gpt-4o"
    ):
        """
        Formata a resposta de um agente CrewAI utilizando um agente Phidata.

        Args:
            crewai_response (str): Resposta do agente CrewAI a ser formatada.
            additional_instructions (Optional[List[str]]): Instruções adicionais para o agente Phidata.
            stream (bool): Indica se a resposta será exibida em streaming.
            show_message (bool): Indica se a mensagem original será exibida.

        Returns:
            str: Resposta formatada do agente Phidata.
        """
        crewai_response=self.execute(input_data)
        # Instruções padrão para o agente Phidata
        default_instructions = ["Use tables to display data"]

        # Adicionar instruções adicionais, se fornecidas
        if additional_instructions:
            instructions = default_instructions + additional_instructions
        else:
            instructions = default_instructions
        current_images = images
        # Atualizar as instruções do agente Phidata
        self.phi_agent.instructions = instructions
        agent_format = PhiAgent(
            model=OpenAIChat(id=llm),
            images=current_images,
            instructions=instructions,
            show_tool_calls=True,
            markdown=True,
        )


        # Submeter a resposta para formatação
        return agent_format.print_response(
            f"Identifique as informações e formate essa saída: {crewai_response}",
            stream=stream,
            show_message=show_message,
        )

from phi.agent import Agent as PhiAgent
from phi.model.openai import OpenAIChat
from typing import List, Dict, Any, Optional, Union
from crewai import Task, Crew as CrewTeam



class HybridTeamAdapter(AiTeamTeam):
    def __init__(
        self,
        agents: List[AiTeamAgent],
        tasks: List[Task],
        manager_llm: Optional[Any] = None,
        process: Optional[Any] = None,
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
            nome = nome,
            memory_system=memory_system,
        )

        # Criar o agente Phidata que representa o time
        phi_agents = [agent.cria_instancia_hibrida() for agent in agents]
        phi_team_instructions = ["Manage and coordinate tasks and agents."]

        # Adicionar as instruções das tasks como contexto adicional
        for task in self.tasks:
            
            phi_team_instructions.append(f"Task: {task.config.description}")
            phi_team_instructions.append(f"Expected Output: {task.config.expected_output}")

        # Inicializar o agente Phidata para o time
        self.phi_team = PhiAgent(
            

            name = "Time de agentes",
            tools=[],
            instructions=phi_team_instructions+["Always include sources", "Use tables to display data"],
            show_tool_calls=True,
            markdown=True,
            team = phi_agents
        )
    def format_response(
        self,
        
        inputs: Optional[Dict[str, Any]] = None,
        images: Optional[List[str]] = None,
        additional_instructions: Optional[List[str]] = None,
        llm: str = "gpt-4o",
        stream: bool = True,
        show_message: bool = False,
    ):
        """
        Formata a resposta de um agente CrewAI utilizando um agente Phidata.

        Args:
            crewai_response (str): Resposta do agente CrewAI a ser formatada.
            additional_instructions (Optional[List[str]]): Instruções adicionais para o agente Phidata.
            stream (bool): Indica se a resposta será exibida em streaming.
            show_message (bool): Indica se a mensagem original será exibida.

        Returns:
            str: Resposta formatada do agente Phidata.
        """
        try:
            crewai_response = self.executar(inputs=inputs)["team_result"]
            print(f"CrewAI Team Response: {crewai_response}")
        except Exception as e:
            raise RuntimeError(f"Erro ao executar o CrewAI Team: {e}")
        # Instruções padrão para o agente Phidata
        default_instructions = ["Use tables to display data"]

        # Adicionar instruções adicionais, se fornecidas
        if additional_instructions:
            instructions = default_instructions + additional_instructions
        else:
            instructions = default_instructions
        current_images = images
        # Atualizar as instruções do agente Phidata
        print(f"llm={llm}")
        print(f"instructions={instructions}")
        agent_format = PhiAgent(
            model=OpenAIChat(id=llm),
            images = current_images,
            instructions=instructions,
            show_tool_calls=True,
            markdown=True,
        )


        # Submeter a resposta para formatação
        return agent_format.print_response(
            f"Identifique as informações e formate essa saída: {crewai_response}",
            stream=stream,
            show_message=show_message,
        )

    

    def print_response(
        self, 
        input_data: str, 
        images: Optional[List[str]] = None,
        llm: Optional[str] = "gpt-4o", 
        stream: bool = True, 
        show_message: bool = False
    ):
        """
        Atualiza o modelo do agente Phidata e redireciona para o método print_response.

        Args:
            input_data (str): Dados de entrada para o agente.
            llm (Optional[str]): String com o ID do modelo LLM para atualizar no agente.
            stream (bool): Indica se a resposta será exibida em streaming.
            show_message (bool): Indica se a mensagem original será exibida.

        Returns:
            str: Resposta do agente Phidata.
        """
        # Atualizar o modelo do agente Phidata, se fornecido
        if llm:
    
            self.phi_team.model = OpenAIChat(id=llm)
        current_images = images
        
        # Executar o print_response no agente Phidata
        return self.phi_team.print_response(input_data,images=current_images, stream=stream, show_message=show_message)
    def cria_instancia_hibrida(self) -> PhidataAgent:
        """
        Retorna a instância do agente Phidata.
        """
        return self.phi_team

from crewai import Flow as Pipeline
from crewai.flow.flow import listen, start, and_, or_, router

from crewai import Flow
from crewai.flow.flow import listen, start, and_, or_, router
from typing import Any, Callable, List, Dict, Union
from functools import wraps
from crewai import Flow
from crewai.flow.flow import listen, start, and_, or_, router
from typing import Any, Callable, List, Dict, Union, Optional
from functools import wraps

class PipelineAdapter(Flow):
    """
    Classe adaptadora para o Flow do CrewAI que fornece decoradores em português
    e uma interface mais amigável.
    """
    def __init__(self):
        super().__init__()
        

    @staticmethod
    def begin():
        """Adapta o decorador @start do CrewAI"""
        def decorator(func: Callable) -> Callable:
            @start()
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def observe(*args, **kwargs):
        """Adapta o decorador @listen do CrewAI"""
        def decorator(func: Callable) -> Callable:
            @listen(*args, **kwargs)
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def case(dependency):
        """
        Adapta o decorador @router do CrewAI.
        
        Args:
            dependency: Dependência do router
        """
        def decorator(func: Callable) -> Callable:
            @router(dependency)
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def _and(*conditions):
        """Adapta a função and_ do CrewAI"""
        return and_(*conditions)

    @staticmethod
    def _or(*conditions):
        """Adapta a função or_ do CrewAI"""
        return or_(*conditions)

    def execute(self, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa o pipeline adaptando o kickoff do Flow.
        
        Args:
            state: Estado inicial opcional para o pipeline
            
        Returns:
            Dict[str, Any]: Resultado da execução do pipeline
        """
        if state:
            self.state.update(state)
        return self.kickoff()

    def execute_batch(self, items: List[Any], state: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executa o pipeline para uma lista de items.
        
        Args:
            items: Lista de items para processar
            state: Estado inicial opcional para o pipeline
            
        Returns:
            List[Dict[str, Any]]: Lista dos resultados do pipeline
        """
        if state:
            self.state.update(state)
        return self.kickoff_for_each(items=items, initial_state=self.state)


class PipelineAdapterlix(Pipeline):
    def __init__(self):
        super().__init__()
    def format_response(
        self,
        
        inputs: Optional[Dict[str, Any]] = None,
        images: Optional[List[str]] = None,
        additional_instructions: Optional[List[str]] = None,
        llm: str = "gpt-4o",
        stream: bool = True,
        show_message: bool = False,
    ):
        """
        Formata a resposta de um agente CrewAI utilizando um agente Phidata.

        Args:
            crewai_response (str): Resposta do agente CrewAI a ser formatada.
            additional_instructions (Optional[List[str]]): Instruções adicionais para o agente Phidata.
            stream (bool): Indica se a resposta será exibida em streaming.
            show_message (bool): Indica se a mensagem original será exibida.

        Returns:
            str: Resposta formatada do agente Phidata.
        """
        try:
            crewai_response = super().execute()
            print(f"CrewAI Team Response: {crewai_response}")
        except Exception as e:
            raise RuntimeError(f"Erro ao executar o CrewAI Team: {e}")
        # Instruções padrão para o agente Phidata
        default_instructions = ["Use tables to display data"]

        # Adicionar instruções adicionais, se fornecidas
        if additional_instructions:
            instructions = default_instructions + additional_instructions
        else:
            instructions = default_instructions
        current_images = images
        # Atualizar as instruções do agente Phidata
        print(f"llm={llm}")
        print(f"instructions={instructions}")
        agent_format = PhiAgent(
            model=OpenAIChat(id=llm),
            images = current_images,
            instructions=instructions,
            show_tool_calls=True,
            markdown=True,
        )


        # Submeter a resposta para formatação
        return agent_format.print_response(
            f"Identifique as informações e formate essa saída: {crewai_response}",
            stream=stream,
            show_message=show_message,
        )


class HybridPipelineAdapter(AiTeamPipeline):
    def __init__(self):
        super().__init__()
    def format_response(
        self,
        
        inputs: Optional[Dict[str, Any]] = None,
        images: Optional[List[str]] = None,
        additional_instructions: Optional[List[str]] = None,
        llm: str = "gpt-4o",
        stream: bool = True,
        show_message: bool = False,
    ):
        """
        Formata a resposta de um agente CrewAI utilizando um agente Phidata.

        Args:
            crewai_response (str): Resposta do agente CrewAI a ser formatada.
            additional_instructions (Optional[List[str]]): Instruções adicionais para o agente Phidata.
            stream (bool): Indica se a resposta será exibida em streaming.
            show_message (bool): Indica se a mensagem original será exibida.

        Returns:
            str: Resposta formatada do agente Phidata.
        """
        try:
            crewai_response = super().execute()
            print(f"CrewAI Team Response: {crewai_response}")
        except Exception as e:
            raise RuntimeError(f"Erro ao executar o CrewAI Team: {e}")
        # Instruções padrão para o agente Phidata
        default_instructions = ["Use tables to display data"]

        # Adicionar instruções adicionais, se fornecidas
        if additional_instructions:
            instructions = default_instructions + additional_instructions
        else:
            instructions = default_instructions
        current_images = images
        # Atualizar as instruções do agente Phidata
        print(f"llm={llm}")
        print(f"instructions={instructions}")
        agent_format = PhiAgent(
            model=OpenAIChat(id=llm),
            images = current_images,
            instructions=instructions,
            show_tool_calls=True,
            markdown=True,
        )


        # Submeter a resposta para formatação
        return agent_format.print_response(
            f"Identifique as informações e formate essa saída: {crewai_response}",
            stream=stream,
            show_message=show_message,
        )


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
                "agent": HybridAgentAdapter,
                "task": HybridTaskAdapter,
                "team": HybridTeamAdapter,
                "tool": HybridToolAdapter,
                "strategy": AiTeamProcessingStrategy,
                "process": AiTeamProcess,
                "processtype": ProcessType,
                "basetool": AiTeamBaseTool,
                "pipeline": PipelineAdapter,
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
