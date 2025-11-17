# frameworkagents.py
from __future__ import annotations  # Importante para type hints com strings
from typing import List, Optional, Type, Dict, Any

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union, Optional, Callable, Type
from pathlib import Path
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class BaseTudo(ABC):
    def __init__(self):
        self.instanciaunica = None

    @abstractmethod
    def cria_instancia(self) -> Any:
        """Método abstrato para criar a instância específica em cada classe"""
        pass

    def create(self) -> Any:
        """Método template que implementa o padrão singleton"""
        if not self.instanciaunica:
            self.instanciaunica = self.cria_instancia()
        return self.instanciaunica


# Memory Classes (mantidas como estavam no framework original)
class MemoryStore(ABC):
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.memories = {}

    @abstractmethod
    def add(self, key: str, value: Any):
        """Adiciona uma memória"""
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Recupera uma memória"""
        pass

    @abstractmethod
    def clear(self):
        """Limpa todas as memórias"""
        pass


class ShortTermMemory(MemoryStore):
    def __init__(self, capacity: int = 100):
        super().__init__(capacity)
        self.recent_access = deque(maxlen=capacity)

    @abstractmethod
    def get_recent(self, limit: int = 10) -> List[Any]:
        """Recupera as memórias mais recentes"""
        pass


class LongTermMemory(MemoryStore):
    def __init__(
        self,
        capacity: int = 1000,
        persistence_path: Optional[Path] = None,
        retention_policy: str = "importance",
    ):
        super().__init__(capacity)
        self.persistence_path = persistence_path
        self.retention_policy = retention_policy
        self.access_weight = 0.4
        self.recency_weight = 0.3
        self.persistence_weight = 0.3

    @abstractmethod
    def calculate_importance(self, memory: Dict) -> float:
        pass

    @abstractmethod
    def get_important_memories(self, threshold: float = 0.5) -> List[Any]:
        pass

    @abstractmethod
    def save_persistent_memories(self):
        pass

    @abstractmethod
    def load_persistent_memories(self):
        pass

    @abstractmethod
    def _apply_retention_policy(self) -> bool:
        pass


class ContextManager(ABC):
    def __init__(self):
        self.current_context = {}
        self.context_history = []

    @abstractmethod
    def set_context(self, context_type: str, context_data: Any):
        pass

    @abstractmethod
    def get_context(self, context_type: str) -> Optional[Any]:
        pass

    @abstractmethod
    def clear_context(self):
        pass


class TaskMemorySystem(ABC):
    def __init__(
        self,
        task_name: str,
        persistence_path: Optional[Path] = None,
        api_key: Optional[str] = None,
        short_term_capacity: int = 100,
        long_term_capacity: int = 1000,
        memory_type: str = "buffer_summary",
    ):
        self.task_name = task_name
        self.persistence_path = persistence_path
        self.api_key = api_key
        self.short_term_capacity = short_term_capacity
        self.long_term_capacity = long_term_capacity
        self.memory_type = memory_type

    @abstractmethod
    def remember(self, key: str, value: Any, long_term: bool = False):
        pass

    @abstractmethod
    def recall(self, key: str, search_long_term: bool = True) -> Optional[Any]:
        pass

    @abstractmethod
    def set_context(self, context_type: str, context_data: Any):
        pass

    @abstractmethod
    def get_context(self, context_type: str) -> Optional[Any]:
        pass

    @abstractmethod
    def summarize_memory(self) -> Dict:
        pass


# Strategy Pattern
class ProcessingStrategy(ABC):
    @abstractmethod
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa dados usando a estratégia definida"""
        pass


class ProcessType(Enum):
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"
    PARALLEL = "parallel"


class Process(BaseTudo):
    def __init__(self, process_type: ProcessType):
        super().__init__()
        self.process_type = process_type


# Tool Base Class
class Tool(BaseTudo):
    def __init__(
        self,
        name: str,
        description: str,
        tool_config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__()
        self.name = name
        self.description = description
        self.tool_config = tool_config or {}


@dataclass
class TaskConfig:
    description: str = None
    expected_output: str = None
    tools: Optional[List[Tool]] = None
    output_json: Optional[Type[BaseModel]] = None
    output_file: Optional[str] = None
    human_input: bool = False
    async_execution: bool = False
    context: Optional[List["Task"]] = None  # Note as aspas em 'Task'
    strategy: Optional[ProcessingStrategy] = None
    config: Optional[Dict[str, Any]] = None
    output_pydantic: Optional[Type[BaseModel]] = None


class Task(BaseTudo):
    def __init__(
        self,
        description: str = None,
        expected_output: str = None,
        tools: Optional[List[Tool]] = None,
        output_json: Optional[Type[BaseModel]] = None,
        output_file: Optional[str] = None,
        human_input: bool = False,
        async_execution: bool = False,
        context: Optional[List["Task"]] = None,  # Note as aspas aqui também
        strategy: Optional[ProcessingStrategy] = None,
        config: Optional[Dict[str, Any]] = None,
        output_pydantic: Optional[Type[BaseModel]] = None,
    ):
        super().__init__()
        
        self.config = TaskConfig(
            description=description,
            expected_output=expected_output,
            tools=tools,
            output_json=output_json,
            output_file=output_file,
            human_input=human_input,
            async_execution=async_execution,
            context=context,
            strategy=strategy,
            config=config,
            output_pydantic=output_pydantic,
        )
        print(self.config)

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a tarefa"""
        pass


# Agent Base Class
@dataclass
class AgentProfile:
    role: str = None
    goal: str = None
    backstory: Optional[str] = None
    tools: Optional[List[Tool]] = None  # Novo - tools opcional
    allow_delegation: bool = True  # Novo - controle de delegação
    verbose: bool = False  # Novo - controle de verbosidade
    config: Optional[Dict[str, Any]] = None  # Novo campo
    allow_code_execution:bool=False
    llm: str = None


class Agent(BaseTudo):
    def __init__(
        self,
        name: str = None,
        role: str = None,
        goal: str = None,
        backstory: Optional[str] = None,
        tools: Optional[List[Tool]] = None,
        allow_delegation: bool = True,
        verbose: bool = False,
        config: Optional[Dict[str, Any]] = None,  # Novo parâmetro
        allow_code_execution:bool=False,
        llm: str = None

    ):
        super().__init__()
        self.name = name
        self.profile = AgentProfile(
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

    @abstractmethod
    def execute(self, input_data: Any) -> Dict[str, Any]:
        """Executa ação do agente"""
        pass


# Team (antigo Crew) Base Class
# Em frameworkagents.py
class Team(BaseTudo):
    def __init__(
        self,
        agents: List[Agent],
        tasks: List[Task],
        manager_llm: Optional[Any] = None,  # Adicionado
        process: Optional[Process] = None,  # Adicionado
        memory: bool = False,
        verbose: Union[bool, int] = False,
        nome : str = None
    ):
        super().__init__()
        self.agents = agents
        self.tasks = tasks
        self.manager_llm = manager_llm
        self.process = process
        self.use_memory = memory
        self.verbose = verbose
        self.nome = nome

    @abstractmethod
    @abstractmethod
    def executar(self, inputs: Dict[str, Any]) -> str:
        """Executa tarefas do time"""
        pass

    # Em frameworkagents.py


from abc import abstractmethod
from typing import List, Dict, Any, Optional, Union, Callable


class Pipeline(BaseTudo):
    """Classe base para pipelines"""

    def __init__(self):
        super().__init__()
        self.steps: Dict[str, Any] = {}
        self.start_step: Optional[Any] = None
        self.state: Dict[str, Any] = {}

    @abstractmethod
    def add_step(
        self,
        name: str,
        operation: Callable,
        operation_type: str,
        dependencies: List[str] = None,
        paths: List[str] = None,
    ):
        """Adiciona um passo ao pipeline"""
        pass

    @abstractmethod
    def start(self):
        """Define o ponto de início do pipeline"""
        pass

    @abstractmethod
    def listen(self, *dependencies):
        """Define listeners para etapas do pipeline"""
        pass

    @abstractmethod
    def router(self, dependency, paths: List[str]):
        """Define roteamento no pipeline"""
        pass

    @abstractmethod
    def and_(self, *operations) -> Any:
        """Operador lógico AND para operações"""
        pass

    @abstractmethod
    def or_(self, *operations) -> Any:
        """Operador lógico OR para operações"""
        pass

    @abstractmethod
    def execute(self) -> Any:
        """Executa o pipeline"""
        pass

    @abstractmethod
    def cria_instancia(self) -> "Pipeline":
        """Implementação requerida pelo BaseTudo"""
        pass


# Observer Pattern
class AgentObserver(ABC):
    @abstractmethod
    def update(self, agent: Agent, result: Any):
        pass


class Observable(ABC):
    def __init__(self):
        self._observers = []

    def attach(self, observer: AgentObserver):
        self._observers.append(observer)

    def detach(self, observer: AgentObserver):
        self._observers.remove(observer)

    def notify(self, agent: Agent, result: Any):
        for observer in self._observers:
            observer.update(agent, result)
