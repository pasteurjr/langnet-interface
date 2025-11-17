from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union, Optional, Callable
from pathlib import Path
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
import autogen

# Memory Classes
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
    def __init__(self, 
                 capacity: int = 1000, 
                 persistence_path: Optional[Path] = None,
                 retention_policy: str = "importance"):
        super().__init__(capacity)
        self.persistence_path = persistence_path
        self.retention_policy = retention_policy
        self.access_weight = 0.4
        self.recency_weight = 0.3
        self.persistence_weight = 0.3

    @abstractmethod
    def calculate_importance(self, memory: Dict) -> float:
        """Calcula pontuação de importância da memória"""
        pass

    @abstractmethod
    def get_important_memories(self, threshold: float = 0.5) -> List[Any]:
        """Recupera memórias acima do threshold de importância"""
        pass

    @abstractmethod
    def load_persistent_memories(self):
        """Carrega memórias persistentes"""
        pass

    @abstractmethod
    def save_persistent_memories(self):
        """Salva memórias persistentes"""
        pass

    @abstractmethod
    def _apply_retention_policy(self) -> bool:
        """Aplica política de retenção quando capacidade é atingida"""
        pass

class AgentMemorySystem(ABC):
    @abstractmethod
    def remember(self, key: str, value: Any, long_term: bool = False):
        """Armazena uma memória"""
        pass

    @abstractmethod
    def recall(self, key: str, search_long_term: bool = True) -> Optional[Any]:
        """Recupera uma memória"""
        pass

    @abstractmethod
    def set_context(self, context_type: str, context_data: Any):
        """Define um contexto"""
        pass

    @abstractmethod
    def get_context(self, context_type: str) -> Optional[Any]:
        """Recupera um contexto"""
        pass

    @abstractmethod
    def summarize_memory(self) -> Dict:
        """Resumo do estado da memória"""
        pass



class ContextManager(ABC):
    def __init__(self):
        self.current_context = {}
        self.context_history = []

    @abstractmethod
    def set_context(self, context_type: str, context_data: Any):
        """Define um novo contexto"""
        pass

    @abstractmethod
    def get_context(self, context_type: str) -> Optional[Any]:
        """Recupera um contexto específico"""
        pass

    @abstractmethod
    def clear_context(self):
        """Limpa o contexto atual"""
        pass



# Agent Classes
class ProcessingStrategy(ABC):
    @abstractmethod
    def process(self, data: Any) -> Any:
        pass

class BaseStrategy(ProcessingStrategy):
    def __init__(self, model: Any, template: str):
        self.model = model
        self.template = template

    @abstractmethod
    def process(self, data: Any) -> Any:
        pass

    @abstractmethod
    def log_execution(self, action: str, data: Any):
        pass

@dataclass
class AgentProfile:
    role: str
    goal: str
    backstory: Optional[str] = None
    tools: List[Any] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    allow_delegation: bool = True
    verbose: bool = False
    config: Optional[Dict[str, Any]] = None

class Agent(ABC):
    def __init__(
        self, 
        name: str,
        role: str,
        goal: str,
        backstory: str = None,
        tools: List[Any] = None,
        memory_persistence_path: Optional[Path] = None,
        allow_delegation: bool = True,
        verbose: bool = False,
        config: Optional[Dict[str, Any]] = None, 
        short_term_capacity: int = 100,
        long_term_capacity: int = 1000):     
               
        self.name = name
        self.profile = AgentProfile
        role=role,
        goal=goal,
        backstory=backstory,
        tools=tools or []
            
        self.short_term_capacity = short_term_capacity
        self.long_term_capacity = long_term_capacity
        self._observers = []
        self.current_work = None
        self.execution_history = []
        
    @abstractmethod
    def preprocess(self, input_data: Any) -> Any:
        pass

    @abstractmethod
    def process(self, data: Any) -> Any:
        pass

    @abstractmethod
    def postprocess(self, result: Any) -> Any:
        pass

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        pass

    @abstractmethod
    def log_execution(self, action: str, result: Any):
        pass

    @abstractmethod
    def get_execution_summary(self) -> Dict:
        pass
# Adicionar estas classes ao framework.py:

class Task(ABC):
    @abstractmethod
    def execute(self, **kwargs):
        """Execute the task."""
        pass

class Crew(ABC):
    @abstractmethod
    def add_agent(self, agent: Agent):
        """Add an agent to the crew."""
        pass

    @abstractmethod
    def execute_task(self, task: Task, **kwargs):
        """Execute a task using the crew."""
        pass

    @abstractmethod
    def coordinate(self):
        """Coordinate agents within the crew."""
        pass

class Tool(ABC):
    @abstractmethod
    def use(self, **kwargs):
        """Use the tool for a task."""
        pass

    @abstractmethod
    def calibrate(self, **kwargs):
        """Calibrate the tool."""
        pass



class StrategicAgent(Agent):
    def __init__(self, 
                 name: str,
                 role: str,
                 goal: str,
                 backstory: str = None,
                 tools: List[Any] = None,
                 strategy: ProcessingStrategy = None,
                 memory_persistence_path: Optional[Path] = None,
                 short_term_capacity: int = 100,
                 long_term_capacity: int = 1000):
        super().__init__(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools or [],
            memory_persistence_path=memory_persistence_path,
            short_term_capacity=short_term_capacity,
            long_term_capacity=long_term_capacity
        )
        self.strategy = strategy

    @abstractmethod
    def set_strategy(self, strategy: ProcessingStrategy):
        pass

class AgentFactory(ABC):
    @abstractmethod
    def create_agent(self, agent_type: str) -> Agent:
        pass

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

class AgentManager(Observable):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentManager, cls).__new__(cls)
            cls._instance.agents = {}
        return cls._instance

    def register_agent(self, name: str, agent: Agent):
        self.agents[name] = agent

    def get_agent(self, name: str) -> Agent:
        return self.agents.get(name)

    def process_task(self, agent_name: str, input_data: Any) -> Any:
        agent = self.get_agent(agent_name)
        if agent:
            result = agent.execute(input_data)
            self.notify(agent, result)
            return result
        else:
            raise ValueError(f"Agent {agent_name} not found")

class BaseAgentAdapter(autogen.ConversableAgent):
    def __init__(self, agent: Agent):
        super().__init__(name=agent.name)
        self.agent = agent

    @abstractmethod
    def generate_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Any] = None,
        exclude: Optional[List[Callable]] = None,
    ) -> Union[str, Dict, None]:
        pass

class AgentSystemFacade(ABC):
    def __init__(self):
        self.manager = AgentManager()
        self.autogen_agents = {}

    @abstractmethod
    def register_agent(self, name: str, agent: Agent):
        pass

    @abstractmethod
    def _create_agent_adapter(self, agent: Agent) -> BaseAgentAdapter:
        pass

    @abstractmethod
    def process_task(self, agent_name: str, input_data: Any) -> Any:
        pass

    @abstractmethod
    def run_multi_agent_task(self, task: str, agent_names: List[str]) -> Any:
        pass

class ComponentFactory(ABC):
    @abstractmethod
    def create_memory(self, type: str, **kwargs) -> MemoryStore:
        """Create a memory component."""
        pass

    @abstractmethod
    def create_agent(self, type: str, **kwargs) -> Agent:
        """Create an agent component."""
        pass

    @abstractmethod
    def create_task(self, type: str, **kwargs) -> Task:
        """Create a task component."""
        pass

    @abstractmethod
    def create_crew(self, type: str, **kwargs) -> Crew:
        """Create a crew component."""
        pass

    @abstractmethod
    def create_tool(self, type: str, **kwargs) -> Tool:
        """Create a tool component."""
        pass
