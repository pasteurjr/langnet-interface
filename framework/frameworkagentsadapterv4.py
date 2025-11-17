
from typing import Any, Dict, List, Union, Optional, Type, TypedDict, Callable
import langgraph.graph
import langgraph.types
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from frameworkagentsadapterv3 import (
    HybridTaskAdapter, 
    HybridAgentAdapter,
    HybridToolAdapter,
    ProcessingStrategy,
    HybridTeamAdapter,
    HybridPipelineAdapter,
    PipelineAdapter
)
from frameworkagentsadapter import (
AiTeamAgent, AiTeamTask,AiTeamBaseTool, AiTeamProcess, 
AiTeamPipeline, AiTeamTeam, AiTeamTool
)
from frameworkagentsadapter import (
AiTeamAgent, AiTeamTask,AiTeamBaseTool, AiTeamProcess, 
AiTeamPipeline, AiTeamTeam, AiTeamTool,AiTeamProcessingStrategy
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



class AgentState(TypedDict):
    """Estado base para nós do grafo"""
    messages: List[Union[HumanMessage, AIMessage]]
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    current_node: str

class LangGraphTaskAdapter(HybridTaskAdapter):
    """Adaptador para usar tasks como nós do LangGraph"""
    def __init__(
        self,
        description: str = None,
        expected_output: str = None,
        tools: Optional[List[Tool]] = None,
        output_json: Optional[Type[BaseModel]] = None,
        output_file: Optional[str] = None,
        human_input: bool = False,
        async_execution: bool = False,
        context: Optional[List["HybridTaskAdapter"]] = None,
        agent: Optional[HybridAgentAdapter] = None,
        strategy: Optional[ProcessingStrategy] = None,
        config: Optional[Dict[str, Any]] = None,
        output_pydantic: Optional[Type[BaseModel]] = None,
        state_class: Type[Any] = None,
        input_func: Callable[[Any], Dict[str, Any]]= None,
        output_func: Callable[[Any, Any], Any]= None,
    
    ):
        super().__init__(
            description=description,
            expected_output=expected_output,
            tools=tools,
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
        self.input_func = input_func
        self.output_func = output_func
        self.state_class = state_class

    def get_node_name(self) -> str:
        """
        Gera o nome do nó seguindo a convenção:
        nome_do_agente + primeiros 20 caracteres da descrição (espaços substituídos por _)
        """
        # Obtém o nome do agente
        agent_name = self.agent.name if self.agent else "no_agent"
        
        # Processa a descrição
        description = self.config.description if self.config.description else ""
        # Pega os primeiros 20 caracteres e substitui espaços por _
        processed_description = description[:20].replace(" ", "_")
        
        # Combina nome do agente com descrição processada
        return f"{agent_name}_{processed_description}"
    
    def as_langflow_node(self):
        def node_func(state: self.state_class) -> self.state_class:
            try:
                # Usa a função de input para preparar os dados para a task
                input_state = self.input_func(state)
                print("*******INPUT_STATE*******ccc")
                print(input_state)
                
                # Executa a task
                result = self.execute(input_state)
                #print("RESULT**********")
                #print(result)
                #new_state = self.output_func(state, result)
            
                
                output_state=self.output_func(state, result)
                #print("*******OUPUT_STATE*******")
                #print(output_state) 
                # Usa a função de output para formatar o resultado
                return output_state
                    
            except Exception as e:
                print(f"Erro no nó {self.get_node_name()}: {str(e)}")
                # Mantém estado atual mas registra erro
                error_state = dict(state)
                if "outputs" not in error_state:
                    error_state["outputs"] = {}
                error_state["outputs"][self.get_node_name()] = {"error": str(e)}
                return self.state_class(**error_state)
            
        return node_func
    
    
    
    
    

class LangGraphTeamAdapter(HybridTeamAdapter):
    """Adaptador para usar teams como nós do LangGraph"""
    def __init__(
        self,
        agents: List[AiTeamAgent],
        tasks: List[Task],
        manager_llm: Optional[Any] = None,
        process: Optional[Any] = None,
        memory: bool = False,
        verbose: Union[bool, int] = False,
        nome : str = None,
        state_class: Type[Any] = None,
        input_func: Callable[[Any], Dict[str, Any]]= None,
        output_func: Callable[[Any, Any], Any]= None,
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
        self.input_func = input_func
        self.output_func = output_func
        self.state_class = state_class
    
    def get_node_name(self) -> str:
        """
        Gera o nome do nó para o team
        Usa o nome do team se definido, ou gera um baseado na composição do team
        """
        if self.nome:  # Usa o nome definido do team se existir
            # Processa para garantir compatibilidade como nome de nó
            return self.nome.replace(" ", "_")[:80]  # Limita a 30 caracteres
            
        # Se não tiver nome, gera baseado nos agentes
        agent_names = [agent.nome for agent in self.agents if hasattr(agent, 'nome')]
        team_identifier = "_".join(agent_names)[:60]  # Limita a 60 caracteres
        print(team_identifier)
        return f"team_{team_identifier}"

    def as_langflow_node(self):
        """
        Converte o team em uma função de nó do LangGraph
        """
        def node_func(state: self.state_class) -> self.state_class:
            try:
                # Usa a função de input para preparar os dados para a task
                input_state = self.input_func(state)
                print("*******INPUT_STATE*******ccc")
                print(input_state)
                
                # Executa o team
                result = self.executar(input_state)
                #print("RESULT**********")
                #print(result)
                #new_state = self.output_func(state, result)
            
                
                output_state=self.output_func(state, result)
                #print("*******OUPUT_STATE*******")
                #print(output_state) 
                # Usa a função de output para formatar o resultado
                return output_state
                    
            except Exception as e:
                print(f"Erro no nó {self.get_node_name()}: {str(e)}")
                # Mantém estado atual mas registra erro
                error_state = dict(state)
                if "outputs" not in error_state:
                    error_state["outputs"] = {}
                error_state["outputs"][self.get_node_name()] = {"error": str(e)}
                return self.state_class(**error_state)
            
        return node_func
        '''
        def team_node(state: AgentState) -> AgentState:
            # Obtém inputs do estado
            team_inputs = state["inputs"].get(self.get_node_name(), {})
            
            # Executa o team usando o método executar herdado
            result = self.executar(inputs=team_inputs)
            
            # Se o resultado for um dicionário com team_result, usa ele
            # Senão, usa o resultado completo
            team_output = result.get("team_result", result) if isinstance(result, dict) else result
            
            # Atualiza o estado
            return {
                "messages": state["messages"],
                "inputs": state["inputs"],
                "outputs": {
                    **state["outputs"],
                    self.get_node_name(): team_output
                },
                "current_node": self.get_node_name()
            }
            
        return team_node
        '''        

from typing import Any, Dict, List, Union, Optional, Type, TypedDict, Callable
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END, START
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
import langgraph
import uuid

class AgentState(TypedDict):
    """Estado base para nós do grafo"""
    messages: List[Union[HumanMessage, AIMessage]]
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    current_node: str
from typing import ClassVar
from frameworkagents import BaseTudo

class Graph(BaseTudo):
    """Adaptador para o StateGraph do LangGraph"""
    
    END = langgraph.graph.END
    START = langgraph.graph.START
    interrupt = langgraph.types.interrupt
    Command = langgraph.types.Command

    def __init__(self, state_class: Type[Any]):
        super().__init__()
        self.state_class = state_class
        self.graph = StateGraph(state_class)  # Usa a classe de estado passada
        self.checkpointer = MemorySaver()
    def cria_instancia(self) -> StateGraph:
        return self.graph

    def add_human_node(self, key: str):
        def human_interaction_node(state: AgentState):
            value = self.interrupt({
                "messages": state["messages"],
                "outputs": state["outputs"],
                "request_feedback": True,
                "node": key
            })
            
            return {
                "messages": state["messages"],
                "inputs": state["inputs"],
                "outputs": {**state["outputs"], key: value},
                "current_node": key
            }
            
        self.graph.add_node(key, human_interaction_node)
        return self

    def stream(
        self,
        input_data: Union[AgentState, 'Graph.Command'],
        **kwargs
    ):
        app = self.compile()
        
        if isinstance(input_data, self.Command):
            thread_config = kwargs.get("config", {"configurable": {"thread_id": uuid.uuid4()}})
        else:
            thread_config = {"configurable": {"thread_id": uuid.uuid4()}}
            
        kwargs["config"] = thread_config
        return app.stream(input_data, **kwargs)

    def resume(
        self, 
        command_data: Any, 
        thread_id: Optional[uuid.UUID] = None
    ):
        command = self.Command(resume=command_data)
        
        if thread_id is None:
            thread_id = uuid.uuid4()
            
        config = {"configurable": {"thread_id": thread_id}}
        return self.stream(command, config=config)
    

    def add_node(self, key: str, node: Union[HybridTaskAdapter, HybridTeamAdapter, Any]):
        if isinstance(node, (HybridTaskAdapter, HybridTeamAdapter)):
            real_name = node.get_node_name()
            node = node.as_langflow_node()
            self.graph.add_node(real_name, node)
            return real_name
        else:
            self.graph.add_node(key, node)
            return key

    def set_entry_point(self, entry_point: str):
        self.graph.set_entry_point(entry_point)
        return self

    def add_edge(self, start: str, end: Union[str, END]):
        self.graph.add_edge(start, end)
        return self

    def add_conditional_edges(
        self,
        start: str,
        condition_function: Callable[[AgentState], str]
    ):
        self.graph.add_conditional_edges(start, condition_function)
        return self

    def add_parallel_edges(
        self, 
        start: str,
        parallel_nodes: List[str],
        join_node: str
    ):
        def join_results(states: List[AgentState]) -> AgentState:
            try:
                invalid_states = [
                    i for i, state in enumerate(states) 
                    if not self.validate_state(state)
                ]
                
                if invalid_states:
                    raise ValueError(f"Estados inválidos nos índices: {invalid_states}")
                
                combined_outputs = {}
                for state in states:
                    try:
                        combined_outputs.update(state["outputs"])
                    except Exception as e:
                        raise RuntimeError(f"Erro ao combinar outputs: {str(e)}")
                
                combined_state = {
                    "messages": states[-1]["messages"],
                    "inputs": states[-1]["inputs"],
                    "outputs": combined_outputs,
                    "current_node": join_node
                }
                
                if not self.validate_state(combined_state):
                    raise ValueError("Estado combinado inválido")
                    
                return combined_state
                
            except Exception as e:
                return {
                    "messages": [],
                    "inputs": {},
                    "outputs": {"error": str(e)},
                    "current_node": join_node
                }

        try:
            self.graph.add_parallel_edges(start, parallel_nodes, join_results)
            return self
        except Exception as e:
            raise RuntimeError(f"Erro ao adicionar edges paralelos: {str(e)}")

    def branch(
        self,
        current_node: str,
        condition: Callable[[AgentState], bool],
        true_branch: List[str],
        false_branch: List[str],
        join_node: str
    ):
        def branch_router(state: AgentState) -> str:
            return true_branch[0] if condition(state) else (false_branch[0] if false_branch else join_node)
        
        self.add_conditional_edges(current_node, branch_router)
        
        for branch in [true_branch, false_branch]:
            if branch:
                for i in range(len(branch) - 1):
                    self.add_edge(branch[i], branch[i + 1])
                self.add_edge(branch[-1], join_node)
        
        return self
    
    def loop(
        self,
        start_node: str,
        condition: Callable[[AgentState], bool],
        loop_body: List[str],
        exit_node: str
    ):
        # Verifica se o loop_body não está vazio
        if not loop_body:
            raise ValueError("O loop_body não pode estar vazio.")
        
        # Lista de nós adicionados ao grafo
        added_nodes = set(self.graph.nodes)  # Obtém os nós já adicionados ao StateGraph
        
        # Verifica se os nós existem no grafo
        missing_nodes = []
        for node in loop_body + [start_node, exit_node]:
            if node not in added_nodes:
                missing_nodes.append(node)
        
        if missing_nodes:
            raise ValueError(f"Os seguintes nós não existem no grafo: {missing_nodes}")
        
        # Função para rotear o fluxo com base na condição
        def loop_router(state: AgentState) -> str:
            return loop_body[0] if condition(state) else exit_node
        
        # Conecta os nós do loop_body em sequência
        for i in range(len(loop_body) - 1):
            self.graph.add_edge(loop_body[i], loop_body[i + 1])
        
        # Conecta o último nó do loop_body de volta ao start_node
        self.graph.add_edge(loop_body[-1], start_node)
        
        # Adiciona a aresta condicional a partir do start_node
        self.graph.add_conditional_edges(start_node, loop_router)
        
        return self



    def loop2(
        self,
        start_node: str,
        condition: Callable[[AgentState], bool],
        loop_body: List[str],
        exit_node: str
    ):
        # Função para rotear o fluxo com base na condição
        def loop_router(state: AgentState) -> str:
            return loop_body[0] if condition(state) else exit_node
        
        # Conecta os nós do loop_body em sequência
        for i in range(len(loop_body) - 1):
            self.add_edge(loop_body[i], loop_body[i + 1])
        
        # Conecta o último nó do loop_body de volta ao start_node
        self.add_edge(loop_body[-1], start_node)
        
        # Adiciona a aresta condicional a partir do start_node
        self.add_conditional_edges(start_node, loop_router)
        
        return self


    
    
    def validate_state(self, state: Dict[str, Any]) -> bool:
        required_keys = {"messages", "inputs", "outputs", "current_node"}
        return all(key in state for key in required_keys)

    def compile(self):
        return self.graph.compile()

    def execute(
        self,
        initial_state: Optional[AgentState] = None,
        allow_interrupts: bool = True,
        **kwargs
    ) -> AgentState:
        app = self.compile()
        
        if initial_state is None:
            initial_state = {
                "messages": [],
                "inputs": {},
                "outputs": {},
                "current_node": None
            }
            
        thread_config = {
            "configurable": {
                "thread_id": uuid.uuid4(),
                "allow_interrupts": allow_interrupts
            }
        }
        kwargs["config"] = thread_config
        
        return app.invoke(initial_state, **kwargs)





class GraphDerivado(StateGraph):
    """Adaptador para o StateGraph do LangGraph"""
    
    END = langgraph.graph.END
    START = langgraph.graph.START
    interrupt= langgraph.types.interrupt
    Command=langgraph.types.Command
    #interrupt = interrupt
    #Command = Command
    def __init__(self):
        super().__init__(AgentState)
        self.checkpointer = MemorySaver()

    def add_human_node(self, key: str):
        """
        Adiciona um nó que pode solicitar interação humana
        """
        def human_interaction_node(state: AgentState):
            # Usa o interrupt estático da classe
            value = Graph.interrupt(
                {
                    "messages": state["messages"],
                    "outputs": state["outputs"],
                    "request_feedback": True,
                    "node": key
                }
            )
            
            return {
                "messages": state["messages"],
                "inputs": state["inputs"],
                "outputs": {**state["outputs"], key: value},
                "current_node": key
            }
            
        self.add_node(key, human_interaction_node)
        return self

    def stream(
        self,
        input_data: Union[AgentState, 'Graph.Command'],
        **kwargs
    ):
        """
        Stream de execução com suporte a interrupções e retomadas
        """
        app = self.compile()
        
        # Se for um Command, usa configuração existente
        if isinstance(input_data, Graph.Command):
            thread_config = kwargs.get("config", {"configurable": {"thread_id": uuid.uuid4()}})
        else:
            thread_config = {"configurable": {"thread_id": uuid.uuid4()}}
            
        kwargs["config"] = thread_config
        
        return app.stream(input_data, **kwargs)

    def resume(
        self, 
        command_data: Any, 
        thread_id: Optional[uuid.UUID] = None
    ):
        """
        Retoma execução após interrupção
        
        Args:
            command_data: Dados para retomada
            thread_id: ID da thread para retomar
        """
        # Cria Command usando o tipo estático
        command = Graph.Command(resume=command_data)
        
        if thread_id is None:
            thread_id = uuid.uuid4()
            
        config = {"configurable": {"thread_id": thread_id}}
        
        return self.stream(command, config=config)

    def add_conditional_edgesxusma(
        self,
        start: str,
        condition_function: Callable[[AgentState], str],
        interrupt_check: Optional[Callable[[AgentState], bool]] = None
    ):
        """
        Adiciona edges condicionais com suporte opcional a interrupções
        
        Args:
            start: Nó de origem
            condition_function: Função que determina próximo nó
            interrupt_check: Função opcional que verifica necessidade de interrupção
        """
        def wrapped_condition(state: AgentState) -> str:
            # Verifica se precisa interromper
            if interrupt_check and interrupt_check(state):
                return Graph.interrupt({
                    "reason": "condition_interrupt",
                    "node": start,
                    "state": state
                })
            
            return condition_function(state)
            
        super().add_conditional_edges(start, wrapped_condition)
        return self

    def execute(
        self,
        initial_state: Optional[AgentState] = None,
        allow_interrupts: bool = True,
        **kwargs
    ) -> AgentState:
        """
        Executa o grafo com suporte a interrupções
        
        Args:
            initial_state: Estado inicial opcional
            allow_interrupts: Se deve permitir interrupções
            **kwargs: Argumentos adicionais
        """
        app = self.compile()
        
        if initial_state is None:
            initial_state = {
                "messages": [],
                "inputs": {},
                "outputs": {},
                "current_node": None
            }
            
        thread_config = {
            "configurable": {
                "thread_id": uuid.uuid4(),
                "allow_interrupts": allow_interrupts
            }
        }
        kwargs["config"] = thread_config
        
        return app.invoke(initial_state, **kwargs)
        
    




    def validate_state(self, state: Dict[str, Any]) -> bool:
        """
        Valida se um estado tem todos os campos necessários
        """
        required_keys = {"messages", "inputs", "outputs", "current_node"}
        return all(key in state for key in required_keys)

    def add_node(self, key: str, node: Union[HybridTaskAdapter, HybridTeamAdapter, Any]):
        if isinstance(node, (HybridTaskAdapter, HybridTeamAdapter)):
            real_name = node.get_node_name()  # Pega o nome gerado pela task
            node = node.as_langflow_node()
            super().add_node(real_name, node)
            return real_name
        else:
            super().add_node(key, node)
            return key

    
    def set_entry_point(self, entry_point: str):
        """Define o ponto de entrada do grafo"""
        super().set_entry_point(entry_point)
        return self

    def add_edge(self, start: str, end: Union[str,END]):
        """
        Adiciona uma aresta direta entre dois nós
        
        Args:
            start: Nó de origem
            end: Nó de destino ou END
        """
        super().add_edge(start, end)
        return self

    def add_conditional_edges(
        self,
        start: str,
        condition_function: Callable[[AgentState], str]
    ):
        """
        Adiciona arestas condicionais a partir de um nó
        
        Args:
            start: Nó de origem
            condition_function: Função que determina próximo nó baseado no estado
        """
        super().add_conditional_edges(start, condition_function)
        return self

    def add_parallel_edges(
        self, 
        start: str,
        parallel_nodes: List[str],
        join_node: str
    ):
        """
        Adiciona execução paralela de nós com tratamento de erros robusto
        
        Args:
            start: Nó inicial
            parallel_nodes: Lista de nós para executar em paralelo
            join_node: Nó que agregará resultados
            
        Raises:
            ValueError: Se nós não existem ou parâmetros inválidos
            RuntimeError: Se ocorre erro durante execução paralela
        """
        # Validar existência dos nós
        all_nodes = [start, join_node] + parallel_nodes
        existing_nodes = set(self._nodes.keys())  # Assumindo que _nodes é o dict de nós do StateGraph
        missing_nodes = [node for node in all_nodes if node not in existing_nodes]
        
        if missing_nodes:
            raise ValueError(f"Nós não encontrados no grafo: {missing_nodes}")
            
        if not parallel_nodes:
            raise ValueError("Lista de nós paralelos não pode estar vazia")
            
        def join_results(states: List[AgentState]) -> AgentState:
            try:
                # Validar todos os estados antes de combinar
                invalid_states = [
                    i for i, state in enumerate(states) 
                    if not self.validate_state(state)
                ]
                
                if invalid_states:
                    raise ValueError(f"Estados inválidos nos índices: {invalid_states}")
                
                # Combina outputs de todos os estados
                combined_outputs = {}
                for state in states:
                    try:
                        combined_outputs.update(state["outputs"])
                    except Exception as e:
                        raise RuntimeError(f"Erro ao combinar outputs: {str(e)}")
                
                # Retorna estado combinado
                combined_state = {
                    "messages": states[-1]["messages"],
                    "inputs": states[-1]["inputs"],
                    "outputs": combined_outputs,
                    "current_node": join_node
                }
                
                # Validar estado final
                if not self.validate_state(combined_state):
                    raise ValueError("Estado combinado inválido")
                    
                return combined_state
                
            except Exception as e:
                # Criar estado de erro
                error_state = {
                    "messages": [],
                    "inputs": {},
                    "outputs": {"error": str(e)},
                    "current_node": join_node
                }
                return error_state

        try:
            super().add_parallel_edges(start, parallel_nodes, join_results)
            return self
        except Exception as e:
            raise RuntimeError(f"Erro ao adicionar edges paralelos: {str(e)}")    


    def add_parallel_edgesX(
        self, 
        start: str,
        parallel_nodes: List[str],
        join_node: str
    ):
        """
        Adiciona execução paralela de nós
        
        Args:
            start: Nó inicial
            parallel_nodes: Lista de nós para executar em paralelo
            join_node: Nó que agregará resultados
        """
        def join_results(states: List[AgentState]) -> AgentState:
            # Combina outputs de todos os estados
            combined_outputs = {}
            for state in states:
                combined_outputs.update(state["outputs"])
            
            # Retorna estado combinado
            return {
                "messages": states[-1]["messages"],
                "inputs": states[-1]["inputs"],
                "outputs": combined_outputs,
                "current_node": join_node
            }

        super().add_parallel_edges(start, parallel_nodes, join_results)
        return self

    def branch(
        self,
        current_node: str,
        condition: Callable[[AgentState], bool],
        true_branch: List[str],
        false_branch: List[str],
        join_node: str
    ):
        """
        Cria um branch condicional no grafo
        
        Args:
            current_node: Nó de onde parte o branch
            condition: Função que avalia condição
            true_branch: Sequência de nós se verdadeiro
            false_branch: Sequência de nós se falso
            join_node: Nó para reunir os branches
        """
        def branch_router(state: AgentState) -> str:
            return true_branch[0] if condition(state) else (false_branch[0] if false_branch else join_node)
        
        # Adiciona edges condicionais para o branch
        self.add_conditional_edges(current_node, branch_router)
        
        # Adiciona edges sequenciais em cada branch
        for branch in [true_branch, false_branch]:
            if branch:  # Só processa o branch se não estiver vazio
                for i in range(len(branch) - 1):
                    self.add_edge(branch[i], branch[i + 1])
                self.add_edge(branch[-1], join_node)
        
        return self

    def loop(
        self,
        start_node: str,
        condition: Callable[[AgentState], bool],
        loop_body: List[str],
        exit_node: str
    ):
        """
        Cria um loop no grafo
        
        Args:
            start_node: Nó inicial do loop
            condition: Função que determina se continua loop
            loop_body: Sequência de nós no corpo do loop
            exit_node: Nó para sair do loop
        """
        def loop_router(state: AgentState) -> str:
            return loop_body[0] if condition(state) else exit_node
        
        # Adiciona edges do corpo do loop
        for i in range(len(loop_body) - 1):
            self.add_edge(loop_body[i], loop_body[i + 1])
            
        # Adiciona edge de volta ao início
        self.add_edge(loop_body[-1], start_node)
        
        # Adiciona edge condicional para decidir continuar/sair
        self.add_conditional_edges(start_node, loop_router)
        
        return self

    def compile(self):
        """
        Compila o grafo para execução
        
        Returns:
            Runnable: Grafo compilado pronto para execução
        """
        return super().compile()
    def executex2(
        self,
        initial_state: Optional[AgentState] = None,
        **kwargs
    ) -> AgentState:
        """
        Executa o grafo compilado com validação de estado
        """
        app = self.compile()
        
        if initial_state is None:
            initial_state = {
                "messages": [],
                "inputs": {},
                "outputs": {},
                "current_node": None
            }
        
        # Validar estado inicial
        if not self.validate_state(initial_state):
            raise ValueError("Estado inicial inválido")
            
        try:
            final_state = app.invoke(initial_state, **kwargs)
            
            # Validar estado final
            if not self.validate_state(final_state):
                raise ValueError("Estado final inválido")
                
            return final_state
            
        except Exception as e:
            # Retornar estado de erro válido
            return {
                "messages": [],
                "inputs": initial_state.get("inputs", {}),
                "outputs": {"error": str(e)},
                "current_node": "error"
            }
    def executeX(
        self,
        initial_state: Optional[AgentState] = None,
        **kwargs
    ) -> AgentState:
        """
        Executa o grafo compilado
        
        Args:
            initial_state: Estado inicial opcional
            **kwargs: Argumentos adicionais para execução
            
        Returns:
            AgentState: Estado final após execução
        """
        app = self.compile()
        
        if initial_state is None:
            initial_state = {
                "messages": [],
                "inputs": {},
                "outputs": {},
                "current_node": None
            }
            
        return app.invoke(initial_state, **kwargs)
       
    
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
                "task": LangGraphTaskAdapter,
                "team": LangGraphTeamAdapter,
                "tool": HybridToolAdapter,
                "strategy": AiTeamProcessingStrategy,
                "process": AiTeamProcess,
                "processtype": ProcessType,
                "basetool": AiTeamBaseTool,
                "pipeline": PipelineAdapter,
                "graph": Graph,
                "agentstate": AgentState,
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
