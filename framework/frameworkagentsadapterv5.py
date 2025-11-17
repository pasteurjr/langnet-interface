#!/usr/bin/env python3
"""
Framework Agents Adapter V5 - Petri Net Integration
Estrutura idêntica ao V4, mas usando Petri Net em vez de LangGraph para orquestração.
Mantém 100% de compatibilidade com frameworks existentes (CrewAI, PhiData, AutoGen).
"""

import asyncio
import aiohttp
import json
import uuid
import logging
import traceback
from typing import Any, Dict, List, Union, Optional, Type, TypedDict, Callable
from datetime import datetime
from pathlib import Path
from collections import deque

# Imports do framework base (iguais ao V4)
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

# Imports dos adaptadores base (iguais ao V4)
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
    AiTeamAgent, AiTeamTask, AiTeamBaseTool, AiTeamProcess, 
    AiTeamPipeline, AiTeamTeam, AiTeamTool, AiTeamProcessingStrategy
)
from frameworkmemory import (
    LangChainAgentMemorySystem, LangChainLongTermAdapter, 
    LangChainMemorySystemFactory, LangChainContextAdapter
)
from frameworkmemorylcf import (
    AiTeamMemorySystemFactory, LangChainFullTaskMemorySystem, 
    LangChainFullContextAdapter, LangChainFullLongTermAdapter, 
    LangChainFullShortTermAdapter
)

# Imports dos frameworks suportados (iguais ao V4)
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
)
from langchain_openai import OpenAI

# CrewAI
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
)
import crewai

# PhiData
from phi.agent import Agent as PhiAgent
from phi.model.openai import OpenAIChat
from phi.tools.firecrawl import FirecrawlTools
from phi.tools.website import WebsiteTools
from phi.tools.file import FileTools
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.serpapi_tools import SerpApiTools
from phi.agent import Agent
from phi.tools import Toolkit
from phi.tools.yfinance import YFinanceTools

# Framework base
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
    BaseTudo
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== ESTADO COMPARTILHADO (equivale AgentState do V4) =====

class PetriNetState(TypedDict):
    """Estado equivalente ao AgentState do V4, mas adaptado para Petri Net"""
    messages: List[Union[HumanMessage, AIMessage]]
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    current_place: str              # Equivale a current_node
    marking_vector: Dict[str, int]  # Estado atual da Petri Net
    execution_id: str               # ID da execução
    petri_metadata: Dict[str, Any]  # Metadados específicos da Petri Net

# ===== CLIENTE HTTP PARA PETRI NET SERVER =====

class PetriNetHTTPClient:
    """Cliente HTTP para comunicação com petri-net-server (localhost:3001)"""
    
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    async def __aenter__(self):
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
        
    async def connect(self):
        """Estabelece conexão HTTP"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
    async def disconnect(self):
        """Encerra conexão HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
            
    async def health_check(self) -> bool:
        """Verifica se o servidor Petri Net está disponível"""
        try:
            if not self.session:
                await self.connect()
                
            async with self.session.get(f"{self.base_url}/health") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"❌ Erro no health check Petri Net: {e}")
            return False
            
    async def initialize_petri_net(self, petri_file: str, execution_id: str) -> Dict[str, Any]:
        """Inicializa execução da Petri Net"""
        try:
            if not self.session:
                await self.connect()
                
            payload = {
                "petri_net_file": petri_file,
                "execution_id": execution_id
            }
            
            async with self.session.post(f"{self.base_url}/api/initialize", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Petri Net inicializada: {execution_id}")
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Petri Net: {e}")
            raise
            
    async def get_enabled_transitions(self) -> List[Dict[str, Any]]:
        """Obtém transições habilitadas"""
        try:
            if not self.session:
                await self.connect()
                
            async with self.session.get(f"{self.base_url}/api/enabled-transitions") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Erro ao obter transições habilitadas: {e}")
            return []
            
    async def execute_transition(self, transition_id: str) -> Dict[str, Any]:
        """Executa uma transição específica"""
        try:
            if not self.session:
                await self.connect()
                
            async with self.session.post(f"{self.base_url}/api/execute-transition/{transition_id}") as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"🔄 Transição executada: {transition_id}")
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao executar transição: {e}")
            raise
            
    async def execute_step(self, max_transitions: int = 1) -> Dict[str, Any]:
        """Executa próximo step automático"""
        try:
            if not self.session:
                await self.connect()
                
            payload = {"max_transitions": max_transitions}
            
            async with self.session.post(f"{self.base_url}/api/execute-step", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"📈 Step executado: {len(result.get('executions', []))} transições")
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao executar step: {e}")
            raise
            
    async def get_status(self) -> Dict[str, Any]:
        """Obtém status atual da Petri Net"""
        try:
            if not self.session:
                await self.connect()
                
            async with self.session.get(f"{self.base_url}/api/status") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Erro ao obter status: {e}")
            return {}
            
    async def stop_execution(self) -> Dict[str, Any]:
        """Para execução da Petri Net"""
        try:
            if not self.session:
                await self.connect()
                
            async with self.session.post(f"{self.base_url}/api/stop") as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("🛑 Execução da Petri Net parada")
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao parar execução: {e}")
            raise

# ===== ADAPTADOR DE TASK (equivale LangGraphTaskAdapter do V4) =====

class PetriNetTaskAdapter(HybridTaskAdapter):
    """Adaptador para usar tasks como places da Petri Net (equivale LangGraphTaskAdapter)"""
    
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
        input_func: Callable[[Any], Dict[str, Any]] = None,
        output_func: Callable[[Any, Any], Any] = None,
        place_id: str = None,           # ID do lugar na Petri Net
        place_name: str = None,         # Nome do lugar (task_name)
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
        
        # Específico para Petri Net
        self.place_id = place_id
        self.place_name = place_name

    def get_place_name(self) -> str:
        """
        Gera o nome do place seguindo a convenção (equivale get_node_name do V4):
        nome_do_agente + primeiros 20 caracteres da descrição (espaços substituídos por _)
        """
        # Se já temos place_name definido, usa ele
        if self.place_name:
            return self.place_name
            
        # Senão, gera como no V4
        agent_name = self.agent.name if self.agent else "no_agent"
        description = self.config.description if self.config.description else ""
        processed_description = description[:20].replace(" ", "_")
        return f"{agent_name}_{processed_description}"
    
    def as_petri_place(self):
        """
        Converte a task em uma função de place da Petri Net (equivale as_langflow_node do V4)
        """
        def place_func(state: self.state_class) -> self.state_class:
            try:
                # Usa a função de input para preparar os dados para a task (igual V4)
                input_state = self.input_func(state)
                logger.debug(f"*******INPUT_STATE******* {self.get_place_name()}")
                logger.debug(input_state)
                
                # Executa a task
                result = self.execute(input_state)
                
                # Usa a função de output para formatar o resultado (igual V4)
                output_state = self.output_func(state, result)
                logger.debug(f"*******OUTPUT_STATE******* {self.get_place_name()}")
                logger.debug(output_state)
                
                return output_state
                    
            except Exception as e:
                logger.error(f"Erro no place {self.get_place_name()}: {str(e)}")
                # Mantém estado atual mas registra erro (igual V4)
                error_state = dict(state)
                if "outputs" not in error_state:
                    error_state["outputs"] = {}
                error_state["outputs"][self.get_place_name()] = {"error": str(e)}
                return self.state_class(**error_state)
            
        return place_func

# ===== ADAPTADOR DE TEAM (equivale LangGraphTeamAdapter do V4) =====

class PetriNetTeamAdapter(HybridTeamAdapter):
    """Adaptador para usar teams como places da Petri Net (equivale LangGraphTeamAdapter)"""
    
    def __init__(
        self,
        agents: List[AiTeamAgent],
        tasks: List[Task],
        manager_llm: Optional[Any] = None,
        process: Optional[Any] = None,
        memory: bool = False,
        verbose: Union[bool, int] = False,
        nome: str = None,
        state_class: Type[Any] = None,
        input_func: Callable[[Any], Dict[str, Any]] = None,
        output_func: Callable[[Any, Any], Any] = None,
        memory_system: LangChainFullTaskMemorySystem = None,
        place_id: str = None,           # ID do lugar na Petri Net
    ):
        super().__init__(
            agents=agents,
            tasks=tasks,
            manager_llm=manager_llm,
            process=process,
            memory=memory,
            verbose=verbose,
            nome=nome,
            memory_system=memory_system,
        )
        self.input_func = input_func
        self.output_func = output_func
        self.state_class = state_class
        self.place_id = place_id
    
    def get_place_name(self) -> str:
        """
        Gera o nome do place para o team (equivale get_node_name do V4)
        Usa o nome do team se definido, ou gera um baseado na composição do team
        """
        if self.nome:  # Usa o nome definido do team se existir
            # Processa para garantir compatibilidade como nome de place
            return self.nome.replace(" ", "_")[:80]  # Limita a 80 caracteres
            
        # Se não tiver nome, gera baseado nos agentes (igual V4)
        agent_names = [agent.nome for agent in self.agents if hasattr(agent, 'nome')]
        team_identifier = "_".join(agent_names)[:60]  # Limita a 60 caracteres
        return f"team_{team_identifier}"

    def as_petri_place(self):
        """
        Converte o team em uma função de place da Petri Net (equivale as_langflow_node do V4)
        """
        def place_func(state: self.state_class) -> self.state_class:
            try:
                # Usa a função de input para preparar os dados para o team (igual V4)
                input_state = self.input_func(state)
                logger.debug(f"*******INPUT_STATE******* {self.get_place_name()}")
                logger.debug(input_state)
                
                # Executa o team
                result = self.executar(input_state)
                
                # Usa a função de output para formatar o resultado (igual V4)
                output_state = self.output_func(state, result)
                logger.debug(f"*******OUTPUT_STATE******* {self.get_place_name()}")
                logger.debug(output_state)
                
                return output_state
                    
            except Exception as e:
                logger.error(f"Erro no place {self.get_place_name()}: {str(e)}")
                # Mantém estado atual mas registra erro (igual V4)
                error_state = dict(state)
                if "outputs" not in error_state:
                    error_state["outputs"] = {}
                error_state["outputs"][self.get_place_name()] = {"error": str(e)}
                return self.state_class(**error_state)
            
        return place_func

# ===== CLASSE PRINCIPAL PETRI NET (equivale Graph do V4) =====

class PetriNet(BaseTudo):
    """Adaptador para Petri Net (equivale à classe Graph do V4)"""
    
    # Equivalentes às constantes do LangGraph
    END = "END_PLACE"
    START = "START_PLACE"
    
    def __init__(self, state_class: Type[Any], petri_file: str = "valep1teste.json"):
        super().__init__()
        self.state_class = state_class
        self.petri_file = petri_file
        
        # Cliente HTTP para petri-net-server
        self.petri_client = PetriNetHTTPClient("http://localhost:3001")
        
        # Registro de places e handlers (equivale aos nós do Graph)
        self.registered_places: Dict[str, Callable] = {}
        self.place_adapters: Dict[str, Union[PetriNetTaskAdapter, PetriNetTeamAdapter]] = {}
        
        # Checkpointer equivalente (armazena histórico)
        self.execution_history: List[Dict] = []
        
        # Configurações
        self.interrupt_enabled = True
        self.human_input_requests: Dict[str, Any] = {}
        
    def cria_instancia(self):
        """Equivale ao método do V4"""
        return self

    def add_place(self, place_name: str, adapter: Union[PetriNetTaskAdapter, PetriNetTeamAdapter, Any]):
        """Equivale a add_node() do V4"""
        if isinstance(adapter, (PetriNetTaskAdapter, PetriNetTeamAdapter)):
            real_name = adapter.get_place_name()
            place_func = adapter.as_petri_place()
            self.registered_places[real_name] = place_func
            self.place_adapters[real_name] = adapter
            return real_name
        else:
            self.registered_places[place_name] = adapter
            return place_name

    def add_human_place(self, place_name: str):
        """Equivale a add_human_node() do V4"""
        def human_interaction_place(state: PetriNetState):
            # Solicitação de input humano (similar ao V4)
            request_data = {
                "messages": state["messages"],
                "outputs": state["outputs"],
                "request_feedback": True,
                "place": place_name,
                "timestamp": datetime.now().isoformat()
            }
            
            # Armazenar solicitação (simulação do interrupt)
            request_id = str(uuid.uuid4())
            self.human_input_requests[request_id] = request_data
            
            logger.info(f"🤚 Input humano solicitado para place: {place_name}")
            
            # Por enquanto, retorna o estado sem mudanças
            # Em implementação real, aguardaria input humano
            return {
                "messages": state["messages"],
                "inputs": state["inputs"],
                "outputs": {**state["outputs"], place_name: f"human_input_pending_{request_id}"},
                "current_place": place_name,
                "marking_vector": state.get("marking_vector", {}),
                "execution_id": state.get("execution_id", ""),
                "petri_metadata": state.get("petri_metadata", {})
            }
        
        self.registered_places[place_name] = human_interaction_place
        return self

    def stream(self, input_data: Union[PetriNetState, Dict], **kwargs):
        """Equivale ao stream() do V4"""
        # Para manter compatibilidade com V4, convertemos para execute
        logger.info("🌊 Stream mode - convertendo para execução síncrona")
        return asyncio.run(self.execute_async(input_data, **kwargs))

    def resume(self, command_data: Any, execution_id: Optional[str] = None):
        """Equivale ao resume() do V4"""
        logger.info(f"▶️ Resumindo execução: {execution_id}")
        # Em implementação completa, retomaria execução pausada
        return {"resumed": True, "execution_id": execution_id, "command_data": command_data}

    def execute(self, initial_state: Optional[PetriNetState] = None, **kwargs) -> PetriNetState:
        """Equivale ao execute() do V4 - versão síncrona"""
        return asyncio.run(self.execute_async(initial_state, **kwargs))
        
    async def execute_async(self, initial_state: Optional[PetriNetState] = None, **kwargs) -> PetriNetState:
        """Execução principal via Petri Net server (versão assíncrona)"""
        
        # Estado inicial (igual V4)
        if initial_state is None:
            initial_state = {
                "messages": [],
                "inputs": {},
                "outputs": {},
                "current_place": None,
                "marking_vector": {},
                "execution_id": str(uuid.uuid4()),
                "petri_metadata": {}
            }

        logger.info(f"🚀 Iniciando execução Petri Net: {initial_state['execution_id']}")
        
        try:
            # 1. Verificar se servidor está disponível
            async with self.petri_client:
                health = await self.petri_client.health_check()
                if not health:
                    raise Exception("Servidor Petri Net não está disponível em localhost:3001")
                
                # 2. Inicializar Petri Net
                await self.petri_client.initialize_petri_net(self.petri_file, initial_state["execution_id"])
                
                # 3. Estado atual
                current_state = initial_state
                
                # 4. Loop de execução (similar ao LangGraph, mas via Petri Net)
                iteration = 0
                max_iterations = kwargs.get('max_iterations', 100)  # Segurança contra loops infinitos
                
                while iteration < max_iterations:
                    iteration += 1
                    
                    # 5. Executar próximo step da Petri Net
                    step_result = await self.petri_client.execute_step(max_transitions=1)
                    
                    executions = step_result.get("executions", [])
                    if not executions:
                        logger.info("ℹ️ Nenhuma transição executada - finalizando")
                        break
                    
                    # 6. Para cada execução, processar places afetados
                    for execution in executions:
                        place_name = execution.get("taskName")  # Nome da task no place
                        if place_name and place_name in self.registered_places:
                            logger.info(f"🎯 Executando place: {place_name}")
                            
                            # Atualizar metadados do estado
                            current_state["current_place"] = place_name
                            current_state["petri_metadata"] = {
                                "transition_id": execution.get("transitionId"),
                                "execution_step": iteration,
                                "timestamp": datetime.now().isoformat()
                            }
                            
                            # Executar handler do place (igual V4)
                            current_state = await self.execute_place_handler(place_name, current_state)
                    
                    # 7. Verificar se execução terminou
                    status = await self.petri_client.get_status()
                    if not status.get("isRunning", False):
                        logger.info("✅ Execução da Petri Net finalizada")
                        break
                        
                    # 8. Pequena pausa para evitar sobrecarga
                    await asyncio.sleep(0.1)
                
                if iteration >= max_iterations:
                    logger.warning(f"⚠️ Execução interrompida por limite de iterações: {max_iterations}")
                
                # 9. Armazenar no histórico
                self.execution_history.append({
                    "execution_id": current_state["execution_id"],
                    "final_state": current_state,
                    "iterations": iteration,
                    "timestamp": datetime.now().isoformat()
                })
                
                return current_state
                
        except Exception as e:
            logger.error(f"❌ Erro na execução Petri Net: {e}")
            logger.error(traceback.format_exc())
            
            # Retornar estado de erro (igual V4)
            error_state = dict(initial_state)
            error_state["outputs"] = {"error": str(e), "traceback": traceback.format_exc()}
            error_state["current_place"] = "error"
            return error_state

    async def execute_place_handler(self, place_name: str, state: PetriNetState) -> PetriNetState:
        """Executa handler de um place (equivale à execução de nó no V4)"""
        handler = self.registered_places.get(place_name)
        if handler:
            try:
                # Se o handler é assíncrono
                if asyncio.iscoroutinefunction(handler):
                    return await handler(state)
                else:
                    return handler(state)
            except Exception as e:
                logger.error(f"❌ Erro no handler do place {place_name}: {e}")
                # Retornar estado com erro
                error_state = dict(state)
                error_state["outputs"] = {**error_state.get("outputs", {}), place_name: {"error": str(e)}}
                return error_state
        else:
            logger.warning(f"⚠️ Handler não encontrado para place: {place_name}")
            return state

    def validate_state(self, state: Dict[str, Any]) -> bool:
        """Valida se um estado tem todos os campos necessários (equivale ao V4)"""
        required_keys = {"messages", "inputs", "outputs", "current_place", "execution_id"}
        return all(key in state for key in required_keys)

    async def stop_execution(self):
        """Para execução da Petri Net"""
        try:
            async with self.petri_client:
                return await self.petri_client.stop_execution()
        except Exception as e:
            logger.error(f"❌ Erro ao parar execução: {e}")
            return {"error": str(e)}

    def get_execution_history(self) -> List[Dict]:
        """Retorna histórico de execuções"""
        return self.execution_history

    def clear_history(self):
        """Limpa histórico de execuções"""
        self.execution_history.clear()

# ===== FACTORY ATUALIZADA (equivale ao V4) =====

class FrameworkAdapterFactory:
    """Factory para selecionar conjunto de adaptadores do framework V5"""

    @staticmethod
    def get_framework_adapters(version: str = "crewai", api_key: Optional[str] = None):
        """
        Retorna as classes de adaptadores do framework na versão especificada
        V5: Idêntico ao V4, mas com adaptadores Petri Net

        Args:
            version: Versão do framework adapter ("crewai", "default", etc)
            api_key: API key para serviços que necessitem
        """
        if version == "crewai":
            return {
                "memory_system": LangChainFullTaskMemorySystem,    # Mesmo do V4
                "agent": HybridAgentAdapter,                       # Mesmo do V4
                "task": PetriNetTaskAdapter,                       # V5: Petri Net
                "team": PetriNetTeamAdapter,                       # V5: Petri Net
                "tool": HybridToolAdapter,                         # Mesmo do V4
                "strategy": AiTeamProcessingStrategy,              # Mesmo do V4
                "process": AiTeamProcess,                          # Mesmo do V4
                "processtype": ProcessType,                        # Mesmo do V4
                "basetool": AiTeamBaseTool,                        # Mesmo do V4
                "pipeline": PipelineAdapter,                       # Mesmo do V4
                "graph": PetriNet,                                 # V5: Petri Net
                "agentstate": PetriNetState,                       # V5: Petri Net
                "memory_factory": AiTeamMemorySystemFactory,       # Mesmo do V4
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

# ===== UTILITÁRIOS E COMPATIBILIDADE =====

# Aliases para compatibilidade com código existente
PetriNetGraph = PetriNet  # Alias
PetriPlace = PetriNetTaskAdapter  # Alias para places individuais
PetriTeam = PetriNetTeamAdapter  # Alias para teams

# Função utilitária para criar estado inicial
def create_initial_petri_state(**kwargs) -> PetriNetState:
    """Cria estado inicial da Petri Net com valores padrão"""
    return {
        "messages": kwargs.get("messages", []),
        "inputs": kwargs.get("inputs", {}),
        "outputs": kwargs.get("outputs", {}),
        "current_place": kwargs.get("current_place", None),
        "marking_vector": kwargs.get("marking_vector", {}),
        "execution_id": kwargs.get("execution_id", str(uuid.uuid4())),
        "petri_metadata": kwargs.get("petri_metadata", {})
    }

# Logging de inicialização
logger.info("🎯 Framework Agents Adapter V5 (Petri Net) carregado com sucesso")
logger.info("📋 Compatibilidade: CrewAI, PhiData, AutoGen, LangChain")
logger.info("🕸️ Orquestração: Petri Net Server (localhost:3001)")