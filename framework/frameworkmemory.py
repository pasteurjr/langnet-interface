from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from collections import deque

# 1. Classes Target (Abstratas)
class MemoryStore(ABC):
    """Classe base abstrata para armazenamento de memória"""
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
    """Classe abstrata para memória de curto prazo"""
    def __init__(self, capacity: int = 100):
        super().__init__(capacity)
        self.recent_access = deque(maxlen=capacity)

    @abstractmethod
    def get_recent(self, limit: int = 10) -> List[Any]:
        """Recupera as memórias mais recentes"""
        pass


class LongTermMemory(MemoryStore):
    """Classe abstrata para memória de longo prazo"""
    def __init__(self, 
                 capacity: int = 1000, 
                 persistence_path: Optional[Path] = None,
                 retention_policy: str = "importance"):  # Adicionado retention_policy
        super().__init__(capacity)
        self.persistence_path = persistence_path
        self.retention_policy = retention_policy
        
        # Métricas para importância
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
    def _apply_retention_policy(self) -> bool:  # Adicionado método abstrato
        """Aplica política de retenção quando capacidade é atingida"""
        pass


class ContextManager(ABC):
    """Classe abstrata para gerenciar o contexto da conversação"""
    def __init__(self):
        self.current_context = {}  # Adicionado
        self.context_history = []  # Adicionado

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


class AgentMemorySystem(ABC):
    """Classe abstrata para o sistema de memória do agente"""
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


# 2. LangChain Adapters
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import pickle
from collections import deque
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory

class LangChainShortTermAdapter(ShortTermMemory):
    """Adapter para memória de curto prazo com LangChain"""

    def __init__(self, capacity: int = 100, api_key: Optional[str] = None):
        super().__init__(capacity)
        self.api_key = api_key
        self.recent_access = deque(maxlen=capacity)
        self.langchain_memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=capacity,
            return_messages=True
        )
        print(f"Inicializando com capacidade: {capacity}")

    def add(self, key: str, value: Any):
        """Adiciona uma memória garantindo unicidade e ordem"""
        print(f"Tentando adicionar: {key} -> {value}")
        
        # Primeiro, procura por duplicata por valor
        existing_key = None
        value_str = str(value)
        for k, v in self.memories.items():
            if str(v['value']) == value_str:
                existing_key = k
                break

        # Se encontrou duplicata, atualiza ela
        if existing_key:
            print(f"Encontrada duplicata: {existing_key}")
            # Atualiza timestamp
            self.memories[existing_key]['timestamp'] = datetime.now().isoformat()
            # Move para o final da fila de acesso
            if existing_key in self.recent_access:
                self.recent_access.remove(existing_key)
            self.recent_access.append(existing_key)
            return

        # Se vai estourar a capacidade, remove a memória mais antiga não duplicada
        while len(self.memories) >= self.capacity:
            oldest_key = self.recent_access[0]
            if oldest_key in self.memories:
                print(f"Removendo por capacidade: {oldest_key}")
                del self.memories[oldest_key]
                self.recent_access.remove(oldest_key)

        # Adiciona nova memória
        self.memories[key] = {
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'access_count': 0
        }
        self.recent_access.append(key)
        
        # Integração com LangChain
        self.langchain_memory.save_context({"input": key}, {"output": str(value)})
        
        print(f"Estado após adição:")
        print(f"Memórias: {list(self.memories.keys())}")
        print(f"Recent access: {list(self.recent_access)}")

    def get(self, key: str) -> Optional[Any]:
        """Recupera uma memória e incrementa access_count"""
        memory = self.memories.get(key)
        if memory:
            memory['access_count'] += 1
            # Move para o final da fila de acesso ao ser acessado
            if key in self.recent_access:
                self.recent_access.remove(key)
                self.recent_access.append(key)
            return memory['value']
        return None

    def clear(self):
        """Limpa todas as memórias"""
        self.memories.clear()
        self.recent_access.clear()
        self.langchain_memory.clear()

    def get_recent(self, limit: int = 10) -> List[Any]:
        """Recupera as memórias mais recentes sem duplicatas"""
        seen = set()
        recent_memories = []
        
        # Usa lista reversa da recent_access para manter ordem cronológica
        for key in reversed(list(self.recent_access)):
            if len(recent_memories) >= limit:
                break
                
            memory = self.memories.get(key)
            if memory:
                value = memory['value']
                value_str = str(value)
                
                if value_str not in seen:
                    seen.add(value_str)
                    recent_memories.append(value)
        
        print(f"get_recent(limit={limit}) retornando: {recent_memories}")
        return recent_memories


class LangChainLongTermAdapter(LongTermMemory):
    def __init__(self, 
                 capacity: int = 1000, 
                 persistence_path: Optional[Path] = None,
                 retention_policy: str = "importance",
                 api_key: Optional[str] = None):
        super().__init__(capacity, persistence_path, retention_policy)
        self.api_key = api_key
        
        # Inicializa LangChain memory
        self.langchain_memory = None
        if api_key:
            try:
                self.langchain_memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                )
            except Exception as e:
                print(f"Erro ao inicializar LangChain: {e}")
                
        if persistence_path and persistence_path.exists():
            self.load_persistent_memories()

    def add(self, key: str, value: Any, persistent: bool = False) -> bool:
        """Adiciona memória com gestão de capacidade"""
        print(f"Tentando adicionar memória: {key} (persistent={persistent})")
        
        if len(self.memories) >= self.capacity:
            if not self._apply_retention_policy():
                print("Não foi possível aplicar política de retenção - todas as memórias são persistentes")
                return False
                
        memory_entry = {
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'access_count': 0,
            'persistent': persistent
        }
        
        self.memories[key] = memory_entry
        
        # Atualiza LangChain apenas para memórias persistentes
        if persistent:
            self.save_persistent_memories()
            self._sync_with_langchain()
            
        return True

    def _sync_with_langchain(self):
        """Sincroniza apenas memórias persistentes com LangChain"""
        if not self.langchain_memory:
            return
            
        try:
            # Limpa todo o histórico atual
            self.langchain_memory.clear()
            
            # Coleta apenas memórias persistentes
            persistent_memories = []
            seen_values = set()  # Para controle de unicidade
            
            for key, memory in self.memories.items():
                if memory.get('persistent', False):
                    value_str = str(memory['value'])
                    if value_str not in seen_values:
                        seen_values.add(value_str)
                        persistent_memories.append((key, memory['value']))
            
            # Adiciona memórias persistentes únicas
            for key, value in persistent_memories:
                self.langchain_memory.chat_memory.add_user_message(str(key))
                self.langchain_memory.chat_memory.add_ai_message(str(value))
            
            print(f"Sincronizado com LangChain: {len(persistent_memories)} memórias únicas")
        except Exception as e:
            print(f"Erro ao sincronizar com LangChain: {e}")

    def save_persistent_memories(self):
        """Salva apenas memórias persistentes"""
        if self.persistence_path:
            try:
                persistent_memories = {
                    k: v for k, v in self.memories.items() 
                    if v.get('persistent', False)
                }
                with open(self.persistence_path, 'wb') as f:
                    pickle.dump(persistent_memories, f)
                print(f"Memórias persistentes salvas: {len(persistent_memories)}")
            except Exception as e:
                print(f"Erro ao salvar memórias persistentes: {e}")

    # [Outros métodos permanecem iguais...]
    def get(self, key: str) -> Optional[Any]:
        """Recupera uma memória e incrementa access_count"""
        memory = self.memories.get(key)
        if memory:
            memory['access_count'] += 1
            print(f"Acessando memória {key} - access_count: {memory['access_count']}")
            return memory['value']
            
        if self.langchain_memory:
            try:
                history = self.langchain_memory.load_memory_variables({})
                messages = history.get("chat_history", [])
                for message in messages:
                    if key in message.content:
                        return message.content
            except Exception as e:
                print(f"Erro ao buscar no LangChain: {e}")
                
        return None

    def clear(self):
        """Limpa todas as memórias"""
        self.memories.clear()
        if self.langchain_memory:
            self.langchain_memory.clear()

    def calculate_importance(self, memory: Dict) -> float:
        """Calcula pontuação de importância da memória"""
        if not isinstance(memory, dict):
            return 0.0
            
        score = 0.0
        
        # Pontuação por acessos
        access_score = min(memory.get('access_count', 0) / 10.0, 1.0)
        score += access_score * self.access_weight
        
        # Pontuação por recência
        if 'timestamp' in memory:
            age = (datetime.now() - datetime.fromisoformat(memory['timestamp'])).days
            recency_score = 1.0 - min(age / 30.0, 1.0)  # Normaliza para 30 dias
            score += recency_score * self.recency_weight
        
        # Pontuação por persistência
        persistence_score = 1.0 if memory.get('persistent', False) else 0.0
        score += persistence_score * self.persistence_weight
        
        return score
    def get_important_memories(self, threshold: float = 0.5) -> List[Any]:
        """Recupera memórias acima do threshold de importância com normalização de emoções"""
        def normalize_emotion(emotion: str) -> str:
            return emotion.strip().rstrip('.').upper()
        
        important_memories = []
        emotion_counts = {}  # Para contar emoções normalizadas

        for memory in self.memories.values():
            if self.calculate_importance(memory) >= threshold:
                if isinstance(memory['value'], dict) and 'result' in memory['value']:
                    # Pega o sentiment data
                    sentiment_data = memory['value']['result'].get('sentiment', {})
                    if sentiment_data and 'identified_sentiments' in sentiment_data:
                        # Normaliza cada emoção antes de adicionar
                        sentiments = [normalize_emotion(s) for s in sentiment_data['identified_sentiments']]
                        # Atualiza as emoções normalizadas na memória
                        sentiment_data['identified_sentiments'] = sentiments
                        memory['value']['result']['sentiment'] = sentiment_data

                important_memories.append(memory['value'])

        return important_memories

    
    def load_persistent_memories(self):
        """Carrega memórias do arquivo de persistência"""
        if self.persistence_path and self.persistence_path.exists():
            try:
                with open(self.persistence_path, 'rb') as f:
                    self.memories = pickle.load(f)
                print(f"Memórias carregadas: {len(self.memories)}")
                self._sync_with_langchain()
            except Exception as e:
                print(f"Erro ao carregar memórias persistentes: {e}")
                self.memories = {}
    def _apply_retention_policy(self) -> bool:
        """Aplica política de retenção quando a capacidade é atingida."""
        if not self.memories:
            return False

        try:
            # Filtrar memórias não persistentes
            non_persistent = {
                k: m for k, m in self.memories.items()
                if not m.get('persistent', False)
            }

            if not non_persistent:
                return False

            if self.retention_policy == "importance":
                # Calcula importância e remove a menos importante
                scores = [(k, self.calculate_importance(m))
                        for k, m in non_persistent.items()]
                key_to_remove = min(scores, key=lambda x: x[1])[0]

            elif self.retention_policy == "recency":
                # Calcula score de recência baseado em último acesso e contagem de acessos
                scores = []
                for k, m in non_persistent.items():
                    # Pega último acesso ou timestamp original
                    last_access = datetime.fromisoformat(m.get('last_access', m['timestamp']))
                    # Considera também número de acessos para determinar "uso recente"
                    access_weight = min(m.get('access_count', 0) / 10.0, 1.0)  # Normaliza contagem de acessos
                    # Calcula idade em segundos
                    age = (datetime.now() - last_access).total_seconds()
                    age_weight = 1.0 - min(age / (24 * 3600), 1.0)  # Normaliza idade para 24 horas
                    # Score final combina último acesso com frequência de uso
                    recency_score = (age_weight * 0.7) + (access_weight * 0.3)
                    scores.append((k, recency_score))
                
                # Remove memória com menor score de recência
                key_to_remove = min(scores, key=lambda x: x[1])[0]

            elif self.retention_policy == "hybrid":
                # Combina importância e recência
                scores = []
                for k, m in non_persistent.items():
                    importance = self.calculate_importance(m)
                    age_seconds = (datetime.now() - datetime.fromisoformat(m['timestamp'])).total_seconds()
                    hybrid_score = importance * 0.7 + (1 - min(age_seconds / (365 * 24 * 3600), 1)) * 0.3
                    scores.append((k, hybrid_score))

                if not scores:
                    return False

                key_to_remove = min(scores, key=lambda x: x[1])[0]

            else:
                return False

            # Remove a memória selecionada
            if key_to_remove in self.memories:
                print(f"Removendo memória por política {self.retention_policy}: {key_to_remove}")
                del self.memories[key_to_remove]
                return True

        except Exception as e:
            print(f"Erro ao aplicar política de retenção: {e}")
            return False

        return False

    






    


class LangChainContextAdapter(ContextManager):
    """Adapter para gerenciamento de contexto do LangChain"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        self.current_context = {}
        self.context_history = []  # Adicionado histórico de contexto
        self.langchain_memory = ConversationBufferMemory(
            memory_key="context",
            return_messages=True
        )

    def set_context(self, context_type: str, context_data: Any):
        """Define um novo contexto, substituindo o anterior"""
        self.current_context[context_type] = {
            'data': context_data,
            'timestamp': datetime.now().isoformat()
        }
        # Mantém histórico de contextos
        self.context_history.append(self.current_context.copy())
        
        # Integração com LangChain
        self.langchain_memory.save_context(
            {"input": context_type},
            {"output": str(context_data)}
        )

    def get_context(self, context_type: str) -> Optional[Any]:
        """Recupera um contexto específico"""
        return self.current_context.get(context_type, {}).get('data')

    def clear_context(self):
        """Limpa o contexto atual mas mantém o histórico"""
        # Antes de limpar, adiciona contexto atual ao histórico se não estiver vazio
        if self.current_context:
            self.context_history.append(self.current_context.copy())
            
        # Limpa apenas o contexto atual
        self.current_context.clear()
        
        # Limpa o langchain memory
        self.langchain_memory.clear()

class LangChainAgentMemorySystem(AgentMemorySystem):
    """Sistema de memória usando adapters LangChain"""

    def __init__(self, 
                 agent_name: str, 
                 persistence_path: Optional[Path] = None, 
                 api_key: Optional[str] = None,
                 short_term_capacity: int = 100,
                 long_term_capacity: int = 1000):
        self.agent_name = agent_name
        self.api_key = api_key
        
        # Inicializa componentes com capacidades específicas
        self.short_term = LangChainShortTermAdapter(
            capacity=short_term_capacity,
            api_key=api_key
        )
        
        self.long_term = LangChainLongTermAdapter(
            capacity=long_term_capacity,
            persistence_path=persistence_path / f"{agent_name}_memory.pkl" if persistence_path else None,
            api_key=api_key
        )
        
        self.context = LangChainContextAdapter(api_key=api_key)

    def remember(self, key: str, value: Any, long_term: bool = False):
        """Armazena uma memória"""
        self.short_term.add(key, value)
        if long_term:
            self.long_term.add(key, value, persistent=True)

    def recall(self, key: str, search_long_term: bool = True) -> Optional[Any]:
        """Recupera uma memória"""
        value = self.short_term.get(key)
        if value is None and search_long_term:
            value = self.long_term.get(key)
        return value

    def set_context(self, context_type: str, context_data: Any):
        """Define um contexto"""
        self.context.set_context(context_type, context_data)

    def get_context(self, context_type: str) -> Optional[Any]:
        """Recupera um contexto"""
        return self.context.get_context(context_type)

    def summarize_memory(self) -> Dict:
        """Resumo do estado da memória"""
        return {
            'agent_name': self.agent_name,
            'short_term_count': len(self.short_term.memories),
            'long_term_count': len(self.long_term.memories),
            'current_context': self.context.current_context
        }


class LangChainMemorySystemFactory:
    """Factory para selecionar o sistema de memória apropriado"""

    @staticmethod
    def create_memory_system(
        implementation: str,
        agent_name: str,
        persistence_path: Optional[Path] = None,
        api_key: Optional[str] = None,
        short_term_capacity: int = 100,
        long_term_capacity: int = 1000,
        memory_type: str = "buffer",  # "buffer", "buffer_window", "buffer_summary"
    ) -> AgentMemorySystem:
        """
        Seleciona e instancia o sistema de memória apropriado

        Args:
            implementation: "default" ou "langchain"
            agent_name: Nome do agente
            persistence_path: Caminho para persistência
            api_key: API key para serviços que necessitem
            short_term_capacity: Capacidade da memória de curto prazo
            long_term_capacity: Capacidade da memória de longo prazo
            memory_type: Tipo de memória (apenas para langchain)
        """
        if implementation == "default":
            from framework import AgentMemorySystem as DefaultMemorySystem

            return DefaultMemorySystem(
                agent_name=agent_name, persistence_path=persistence_path
            )

        elif implementation == "langchain":
            if memory_type == "buffer_summary" and not api_key:
                raise ValueError("API key necessária para memory_type='buffer_summary'")

            return LangChainAgentMemorySystem(
                agent_name=agent_name,
                persistence_path=persistence_path,
                api_key=api_key,
                short_term_capacity=short_term_capacity,
                long_term_capacity=long_term_capacity,
                #memory_type=memory_type,
            )

        else:
            raise ValueError(f"Implementação de memória desconhecida: {implementation}")





