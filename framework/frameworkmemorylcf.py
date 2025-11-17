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
class LangChainFullShortTermAdapter(ShortTermMemory):
    """Adapter que utiliza todas as capacidades de memória curta do LangChain"""

    def __init__(
        self,
        capacity: int = 100,
        window_memory: Optional[ConversationBufferWindowMemory] = None,
        main_memory: Optional[Any] = None,
        llm: Optional[Any] = None,
    ):
        super().__init__(capacity)
        self.window_memory = window_memory
        self.main_memory = main_memory
        self.llm = llm
        self.memories = {}
        self.recent_access = deque(maxlen=capacity)

    # ... continua com todos os métodos da classe
    # Continuação do LangChainFullShortTermAdapter

    def add(self, key: str, value: Any):
        """Adiciona memória usando janela deslizante e sumarização"""
        print(f"Tentando adicionar: {key} -> {value}")

        # Verifica duplicatas
        value_str = str(value)
        existing_key = None
        for k, v in self.memories.items():
            if str(v["value"]) == value_str:
                existing_key = k
                break

        if existing_key:
            print(f"Encontrada duplicata: {existing_key}")
            self.memories[existing_key]["timestamp"] = datetime.now().isoformat()
            if existing_key in self.recent_access:
                self.recent_access.remove(existing_key)
            self.recent_access.append(existing_key)
            return

        # Adiciona na memória de janela
        if self.window_memory:
            self.window_memory.save_context({"input": key}, {"output": str(value)})

        # Adiciona na memória principal com sumarização se disponível
        if isinstance(self.main_memory, ConversationSummaryBufferMemory) and self.llm:
            try:
                summary_prompt = f"Sumarize esta informação mantendo detalhes importantes: {str(value)}"
                summary = self.llm(summary_prompt)
                self.main_memory.save_context({"input": key}, {"output": summary})
            except Exception as e:
                print(f"Erro ao gerar sumário: {e}")
                self.main_memory.save_context({"input": key}, {"output": str(value)})
        elif self.main_memory:
            self.main_memory.save_context({"input": key}, {"output": str(value)})

        self.memories[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
        }
        self.recent_access.append(key)

        while len(self.memories) > self.capacity:
            oldest_key = self.recent_access[0]
            if oldest_key in self.memories:
                del self.memories[oldest_key]
                self.recent_access.remove(oldest_key)

    def get(self, key: str) -> Optional[Any]:
        """Recupera memória com contexto enriquecido"""
        memory = self.memories.get(key)
        if memory:
            memory["access_count"] += 1
            if key in self.recent_access:
                self.recent_access.remove(key)
                self.recent_access.append(key)

            if self.main_memory:
                self.main_memory.save_context(
                    {"input": f"access_{key}"}, {"output": str(memory["value"])}
                )

            return memory["value"]

        if self.window_memory:
            history = self.window_memory.load_memory_variables({})
            messages = history.get("recent_history", [])
            for message in messages:
                if key in message.content:
                    return message.content

        if self.main_memory:
            history = self.main_memory.load_memory_variables({})
            messages = history.get("chat_history", [])
            for message in messages:
                if key in message.content:
                    return message.content

        return None

    def get_recent(self, limit: int = 10) -> List[Any]:
        """Recupera memórias recentes usando janela LangChain"""
        recent_memories = []
        seen = set()

        if self.window_memory:
            history = self.window_memory.load_memory_variables({})
            messages = history.get("recent_history", [])

            for msg in messages[-limit:]:
                if hasattr(msg, "content"):
                    value_str = str(msg.content)
                    if value_str not in seen:
                        seen.add(value_str)
                        recent_memories.append(msg.content)

        if len(recent_memories) < limit:
            for key in reversed(list(self.recent_access)):
                if len(recent_memories) >= limit:
                    break

                memory = self.memories.get(key)
                if memory:
                    value = memory["value"]
                    value_str = str(value)
                    if value_str not in seen:
                        seen.add(value_str)
                        recent_memories.append(value)

        return recent_memories

    def clear(self):
        """Limpa todas as memórias"""
        self.memories.clear()
        self.recent_access.clear()
        if self.window_memory:
            self.window_memory.clear()
        if self.main_memory:
            self.main_memory.clear()


# Continuação - LangChainFullLongTermAdapter


class LangChainFullLongTermAdapter(LongTermMemory):
    """Adapter que utiliza todas as capacidades de memória longa do LangChain"""

    def __init__(
        self,
        capacity: int = 1000,
        persistence_path: Optional[Path] = None,
        main_memory: Optional[Any] = None,
        llm: Optional[Any] = None,
        retention_policy: str = "importance",
    ):
        super().__init__(
            capacity=capacity,
            persistence_path=persistence_path,
            retention_policy=retention_policy,
        )
        self.main_memory = main_memory
        self.llm = llm

        if persistence_path:
            self.load_persistent_memories()

    def add(self, key: str, value: Any, persistent: bool = False) -> bool:
        print(
            f"Tentando adicionar memória de longo prazo: {key} (persistent={persistent})"
        )

        if len(self.memories) >= self.capacity:
            if not self._apply_retention_policy():
                print("Não foi possível aplicar política de retenção")
                return False

        memory_entry = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
            "persistent": persistent,
        }

        if (
            persistent
            and isinstance(self.main_memory, ConversationSummaryBufferMemory)
            and self.llm
        ):
            try:
                summary_prompt = (
                    f"Gere um sumário conciso mas informativo: {str(value)}"
                )
                summary = self.llm(summary_prompt)
                memory_entry["summary"] = summary

                self.main_memory.save_context({"input": key}, {"output": summary})
            except Exception as e:
                print(f"Erro ao gerar sumário: {e}")
                memory_entry["summary"] = str(value)
                self.main_memory.save_context({"input": key}, {"output": str(value)})
        elif self.main_memory:
            self.main_memory.save_context({"input": key}, {"output": str(value)})

        self.memories[key] = memory_entry

        if persistent:
            self.save_persistent_memories()

        return True

    def get(self, key: str) -> Optional[Any]:
        memory = self.memories.get(key)
        if memory:
            memory["access_count"] += 1
            memory["last_access"] = datetime.now().isoformat()

            if self.main_memory:
                value = (
                    memory.get("summary", memory["value"])
                    if "summary" in memory
                    else memory["value"]
                )
                self.main_memory.save_context(
                    {"input": f"access_{key}"}, {"output": str(value)}
                )

            return memory["value"]

        if self.main_memory:
            try:
                history = self.main_memory.load_memory_variables({})
                messages = history.get("chat_history", [])
                for message in messages:
                    if key in message.content:
                        return message.content
            except Exception as e:
                print(f"Erro ao buscar da memória principal: {e}")

        return None

    def calculate_importance(self, memory: Dict) -> float:
        if not isinstance(memory, dict):
            return 0.0

        score = 0.0

        if self.llm and "value" in memory:
            try:
                importance_prompt = (
                    "Avalie a importância desta informação de 0 a 1, "
                    "considerando:\n"
                    "- Relevância do conteúdo\n"
                    "- Unicidade da informação\n"
                    "- Potencial utilidade futura\n\n"
                    f"Informação: {str(memory['value'])}\n"
                    "Retorne apenas o número."
                )
                llm_score = float(self.llm(importance_prompt))
                score += llm_score * 0.4
            except Exception as e:
                print(f"Erro ao calcular importância via LLM: {e}")

        access_score = min(memory.get("access_count", 0) / 10.0, 1.0)
        score += access_score * self.access_weight

        if "timestamp" in memory:
            age = (datetime.now() - datetime.fromisoformat(memory["timestamp"])).days
            recency_score = 1.0 - min(age / 30.0, 1.0)
            score += recency_score * self.recency_weight

        persistence_score = 1.0 if memory.get("persistent", False) else 0.0
        score += persistence_score * self.persistence_weight

        return score

    def get_important_memories(self, threshold: float = 0.5) -> List[Any]:
        important_memories = []

        if isinstance(self.main_memory, ConversationSummaryBufferMemory):
            try:
                history = self.main_memory.load_memory_variables({})
                messages = history.get("chat_history", [])
                for message in messages:
                    if hasattr(message, "content"):
                        important_memories.append(message.content)
            except Exception as e:
                print(f"Erro ao recuperar sumários: {e}")

        for memory in self.memories.values():
            if self.calculate_importance(memory) >= threshold:
                value = (
                    memory.get("summary", memory["value"])
                    if "summary" in memory
                    else memory["value"]
                )
                if value not in important_memories:
                    important_memories.append(value)

        return important_memories

    def save_persistent_memories(self):
        if self.persistence_path:
            try:
                persistent_memories = {
                    k: v for k, v in self.memories.items() if v.get("persistent", False)
                }
                with open(self.persistence_path, "wb") as f:
                    pickle.dump(persistent_memories, f)
                print(f"Memórias persistentes salvas: {len(persistent_memories)}")
            except Exception as e:
                print(f"Erro ao salvar memórias: {e}")

    def load_persistent_memories(self):
        if self.persistence_path:
            try:
                with open(self.persistence_path, "rb") as f:
                    self.memories = pickle.load(f)
                print(f"Memórias carregadas: {len(self.memories)}")

                if isinstance(self.main_memory, ConversationSummaryBufferMemory):
                    for key, memory in self.memories.items():
                        if memory.get("persistent", False):
                            value = memory.get("summary", memory["value"])
                            self.main_memory.save_context(
                                {"input": key}, {"output": str(value)}
                            )
            except Exception as e:
                print(f"Erro ao carregar memórias: {e}")
                self.memories = {}

    def clear(self):
        self.memories.clear()
        if self.main_memory:
            self.main_memory.clear()

    def _apply_retention_policy(self) -> bool:
        if not self.memories:
            return False

        try:
            non_persistent = {
                k: m for k, m in self.memories.items() if not m.get("persistent", False)
            }

            if not non_persistent:
                return False

            if self.retention_policy == "importance":
                scores = [
                    (k, self.calculate_importance(m)) for k, m in non_persistent.items()
                ]
                key_to_remove = min(scores, key=lambda x: x[1])[0]

            elif self.retention_policy == "recency":
                timestamps = []
                for key, memory in non_persistent.items():
                    if self.main_memory:
                        history = self.main_memory.load_memory_variables({})
                        last_access = None
                        for msg in reversed(history.get("chat_history", [])):
                            if key in msg.content:
                                last_access = msg.create_time
                                break
                        timestamps.append(
                            (
                                key,
                                last_access
                                or memory.get("last_access")
                                or memory["timestamp"],
                            )
                        )
                    else:
                        timestamps.append(
                            (key, memory.get("last_access") or memory["timestamp"])
                        )

                sorted_keys = sorted(timestamps, key=lambda x: x[1])
                key_to_remove = sorted_keys[0][0]

            elif self.retention_policy == "hybrid":
                scores = []
                for k, m in non_persistent.items():
                    importance = self.calculate_importance(m)

                    if self.main_memory:
                        history = self.main_memory.load_memory_variables({})
                        last_access = None
                        for msg in reversed(history.get("chat_history", [])):
                            if k in msg.content:
                                last_access = msg.create_time
                                break
                        if last_access:
                            age_seconds = (datetime.now() - last_access).total_seconds()
                        else:
                            timestamp = datetime.fromisoformat(
                                m.get("last_access") or m["timestamp"]
                            )
                            age_seconds = (datetime.now() - timestamp).total_seconds()
                    else:
                        timestamp = datetime.fromisoformat(
                            m.get("last_access") or m["timestamp"]
                        )
                        age_seconds = (datetime.now() - timestamp).total_seconds()

                    recency_score = 1.0 - min(age_seconds / (365 * 24 * 3600), 1.0)
                    hybrid_score = importance * 0.7 + recency_score * 0.3
                    scores.append((k, hybrid_score))

                if not scores:
                    return False

                key_to_remove = min(scores, key=lambda x: x[1])[0]
            else:
                return False

            if key_to_remove in self.memories:
                del self.memories[key_to_remove]
                return True

        except Exception as e:
            print(f"Erro ao aplicar política de retenção: {e}")
            return False

        return False


# Continuação - LangChainFullContextAdapter


class LangChainFullContextAdapter(ContextManager):
    """Adapter que utiliza todas as capacidades de gestão de contexto do LangChain"""

    def __init__(
        self,
        context_memory: Optional[ConversationSummaryBufferMemory] = None,
        main_memory: Optional[Any] = None,
        llm: Optional[Any] = None,
    ):
        super().__init__()
        self.context_memory = context_memory
        self.main_memory = main_memory
        self.llm = llm
        self.current_context = {}
        self.context_history = []

    def set_context(self, context_type: str, context_data: Any):
        """Define contexto com sumarização inteligente"""
        if self.current_context:
            self.context_history.append(self.current_context.copy())

        if (
            isinstance(self.context_memory, ConversationSummaryBufferMemory)
            and self.llm
        ):
            try:
                summary_prompt = (
                    "Gere um sumário do contexto que mantenha informações essenciais:\n"
                    f"Tipo: {context_type}\n"
                    f"Dados: {str(context_data)}"
                )
                context_summary = self.llm(summary_prompt)

                self.context_memory.save_context(
                    {"input": context_type}, {"output": context_summary}
                )

                self.current_context[context_type] = {
                    "data": context_data,
                    "summary": context_summary,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                print(f"Erro ao gerar sumário de contexto: {e}")
                self.current_context[context_type] = {
                    "data": context_data,
                    "timestamp": datetime.now().isoformat(),
                }
                if self.context_memory:
                    self.context_memory.save_context(
                        {"input": context_type}, {"output": str(context_data)}
                    )
        else:
            self.current_context[context_type] = {
                "data": context_data,
                "timestamp": datetime.now().isoformat(),
            }
            if self.context_memory:
                self.context_memory.save_context(
                    {"input": context_type}, {"output": str(context_data)}
                )

        if self.main_memory and self.main_memory != self.context_memory:
            self.main_memory.save_context(
                {"input": f"context_{context_type}"}, {"output": str(context_data)}
            )

    def get_context(self, context_type: str) -> Optional[Any]:
        """Recupera contexto com enriquecimento"""
        context = self.current_context.get(context_type, {})
        if context:
            return context.get("data")

        if self.context_memory:
            try:
                history = self.context_memory.load_memory_variables({})
                messages = history.get("context_history", [])
                for message in messages:
                    if context_type in message.content:
                        return message.content
            except Exception as e:
                print(f"Erro ao buscar contexto do LangChain: {e}")

        if self.main_memory and self.main_memory != self.context_memory:
            try:
                history = self.main_memory.load_memory_variables({})
                messages = history.get("chat_history", [])
                for message in messages:
                    if f"context_{context_type}" in message.content:
                        return message.content
            except Exception as e:
                print(f"Erro ao buscar contexto da memória principal: {e}")

        return None

    def clear_context(self):
        """Limpa contexto atual mantendo histórico"""
        if self.current_context:
            self.context_history.append(self.current_context.copy())

        self.current_context.clear()

        if self.context_memory:
            self.context_memory.clear()
        if self.main_memory and self.main_memory != self.context_memory:
            self.main_memory.clear()







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
class LangChainFullShortTermAdapter(ShortTermMemory):
    """Adapter que utiliza todas as capacidades de memória curta do LangChain"""

    def __init__(
        self,
        capacity: int = 100,
        window_memory: Optional[ConversationBufferWindowMemory] = None,
        main_memory: Optional[Any] = None,
        llm: Optional[Any] = None,
    ):
        super().__init__(capacity)
        self.window_memory = window_memory
        self.main_memory = main_memory
        self.llm = llm
        self.memories = {}
        self.recent_access = deque(maxlen=capacity)

    # ... continua com todos os métodos da classe
    # Continuação do LangChainFullShortTermAdapter

    def add(self, key: str, value: Any):
        """Adiciona memória usando janela deslizante e sumarização"""
        print("NO ADD")
        print(f"Tentando adicionar: {key} -> {value}")

        # Verifica duplicatas
        value_str = str(value)
        existing_key = None
        for k, v in self.memories.items():
            if str(v["value"]) == value_str:
                existing_key = k
                break

        if existing_key:
            print(f"Encontrada duplicata: {existing_key}")
            self.memories[existing_key]["timestamp"] = datetime.now().isoformat()
            if existing_key in self.recent_access:
                self.recent_access.remove(existing_key)
            self.recent_access.append(existing_key)
            return

        # Se vai estourar a capacidade, remove a memória mais antiga
        while len(self.memories) >= self.capacity:
            oldest_key = list(self.recent_access)[0]  # Pega o primeiro item da deque
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
        if self.window_memory:
            self.window_memory.save_context({"input": key}, {"output": str(value)})
        if self.main_memory:
            self.main_memory.save_context({"input": key}, {"output": str(value)})
    
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera memória com contexto enriquecido"""
        memory = self.memories.get(key)
        if memory:
            memory["access_count"] += 1
            if key in self.recent_access:
                self.recent_access.remove(key)
                self.recent_access.append(key)

            if self.main_memory:
                self.main_memory.save_context(
                    {"input": f"access_{key}"}, {"output": str(memory["value"])}
                )

            return memory["value"]

        if self.window_memory:
            history = self.window_memory.load_memory_variables({})
            messages = history.get("recent_history", [])
            for message in messages:
                if key in message.content:
                    return message.content

        if self.main_memory:
            history = self.main_memory.load_memory_variables({})
            messages = history.get("chat_history", [])
            for message in messages:
                if key in message.content:
                    return message.content

        return None

    def get_recent(self, limit: int = 10) -> List[Any]:
        """Recupera memórias recentes usando janela LangChain"""
        recent_memories = []
        seen = set()

        if self.window_memory:
            history = self.window_memory.load_memory_variables({})
            messages = history.get("recent_history", [])

            for msg in messages[-limit:]:
                if hasattr(msg, "content"):
                    value_str = str(msg.content)
                    if value_str not in seen:
                        seen.add(value_str)
                        recent_memories.append(msg.content)

        if len(recent_memories) < limit:
            for key in reversed(list(self.recent_access)):
                if len(recent_memories) >= limit:
                    break

                memory = self.memories.get(key)
                if memory:
                    value = memory["value"]
                    value_str = str(value)
                    if value_str not in seen:
                        seen.add(value_str)
                        recent_memories.append(value)

        return recent_memories

    def clear(self):
        """Limpa todas as memórias"""
        self.memories.clear()
        self.recent_access.clear()
        if self.window_memory:
            self.window_memory.clear()
        if self.main_memory:
            self.main_memory.clear()


# Continuação - LangChainFullLongTermAdapter


class LangChainFullLongTermAdapter(LongTermMemory):
    """Adapter que utiliza todas as capacidades de memória longa do LangChain"""

    def __init__(
        self,
        capacity: int = 1000,
        persistence_path: Optional[Path] = None,
        main_memory: Optional[Any] = None,
        llm: Optional[Any] = None,
        retention_policy: str = "importance",
    ):
        super().__init__(
            capacity=capacity,
            persistence_path=persistence_path,
            retention_policy=retention_policy,
        )
        self.main_memory = main_memory
        self.llm = llm
        print(f"persistence_path: {persistence_path}")
        self.memories = {}
    
        # Se tiver persistence_path, garante que é um arquivo .pkl
        if persistence_path:
            if not str(persistence_path).endswith('.pkl'):
                self.persistence_path = persistence_path / "memory.pkl"
            else:
                self.persistence_path = persistence_path
                
            # Garante que o diretório existe
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Tenta carregar memórias existentes
            self.load_persistent_memories()
        
    def add(self, key: str, value: Any, persistent: bool = False) -> bool:
        print(
            f"Tentando adicionar memória de longo prazo: {key} (persistent={persistent})"
        )

        if len(self.memories) >= self.capacity:
            if not self._apply_retention_policy():
                print("Não foi possível aplicar política de retenção")
                return False

        memory_entry = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
            "persistent": persistent,
        }

        if (
            persistent
            and isinstance(self.main_memory, ConversationSummaryBufferMemory)
            and self.llm
        ):
            try:
                summary_prompt = (
                    f"Gere um sumário conciso mas informativo: {str(value)}"
                )
                summary = self.llm(summary_prompt)
                memory_entry["summary"] = summary

                self.main_memory.save_context({"input": key}, {"output": summary})
            except Exception as e:
                print(f"Erro ao gerar sumário: {e}")
                memory_entry["summary"] = str(value)
                self.main_memory.save_context({"input": key}, {"output": str(value)})
        elif self.main_memory:
            self.main_memory.save_context({"input": key}, {"output": str(value)})

        self.memories[key] = memory_entry

        if persistent:
            self.save_persistent_memories()

        return True

    def get(self, key: str) -> Optional[Any]:
        memory = self.memories.get(key)
        if memory:
            memory["access_count"] += 1
            memory["last_access"] = datetime.now().isoformat()

            if self.main_memory:
                value = (
                    memory.get("summary", memory["value"])
                    if "summary" in memory
                    else memory["value"]
                )
                self.main_memory.save_context(
                    {"input": f"access_{key}"}, {"output": str(value)}
                )

            return memory["value"]

        if self.main_memory:
            try:
                history = self.main_memory.load_memory_variables({})
                messages = history.get("chat_history", [])
                for message in messages:
                    if key in message.content:
                        return message.content
            except Exception as e:
                print(f"Erro ao buscar da memória principal: {e}")

        return None

    def calculate_importance(self, memory: Dict) -> float:
        if not isinstance(memory, dict):
            return 0.0

        score = 0.0

        # Pontuação por LLM (40%)
        if self.llm and "value" in memory:
            try:
                importance_prompt = (
                    "Avalie a importância desta informação em uma escala de 0 a 1, "
                    "considerando sua relevância e utilidade.\n"
                    f"Informação: {str(memory['value'])}\n"
                    "Retorne apenas o número entre 0 e 1."
                )
                llm_score = float(self.llm(importance_prompt))
                score += min(max(llm_score, 0.0), 1.0) * 0.4
            except Exception as e:
                print(f"Erro ao calcular importância via LLM: {e}")

        # Pontuação por acessos (30%)
        access_score = min(memory.get("access_count", 0) / 10.0, 1.0)
        score += access_score * 0.3

        # Pontuação por recência (20%)
        if "timestamp" in memory:
            age = (datetime.now() - datetime.fromisoformat(memory["timestamp"])).days
            recency_score = 1.0 - min(age / 30.0, 1.0)
            score += recency_score * 0.2

        # Pontuação por persistência (10%)
        persistence_score = 1.0 if memory.get("persistent", False) else 0.0
        score += persistence_score * 0.1

        return min(max(score, 0.0), 1.0)  # Garantir range entre 0 e 1
    
    def get_important_memories(self, threshold: float = 0.5) -> List[Any]:
        important_memories = []

        if isinstance(self.main_memory, ConversationSummaryBufferMemory):
            try:
                history = self.main_memory.load_memory_variables({})
                messages = history.get("chat_history", [])
                for message in messages:
                    if hasattr(message, "content"):
                        important_memories.append(message.content)
            except Exception as e:
                print(f"Erro ao recuperar sumários: {e}")

        for memory in self.memories.values():
            if self.calculate_importance(memory) >= threshold:
                value = (
                    memory.get("summary", memory["value"])
                    if "summary" in memory
                    else memory["value"]
                )
                if value not in important_memories:
                    important_memories.append(value)

        return important_memories

    def save_persistent_memories(self):
        if self.persistence_path:
            try:
                # Diretório já foi criado no __init__
                with open(self.persistence_path, "wb") as f:
                    pickle.dump(self.memories, f)
                print(f"Memórias salvas em: {self.persistence_path}")
                
            except Exception as e:
                print(f"Erro ao salvar memórias: {e}")
                print(f"Caminho tentado: {self.persistence_path}")

    def load_persistent_memories(self):
        if self.persistence_path:
            # Se arquivo não existe, cria vazio
            if not self.persistence_path.exists():
                print(f"Arquivo não existe, criando novo: {self.persistence_path}")
                self.memories = {}
                self.save_persistent_memories()  # Cria arquivo vazio inicial
                return
                
            # Se existe, tenta carregar
            try:
                with open(self.persistence_path, "rb") as f:
                    self.memories = pickle.load(f)
                print(f"Memórias carregadas de: {self.persistence_path}")
            except Exception as e:
                print(f"Erro ao carregar memórias: {e}")
                self.memories = {}
                # Se falhou ao carregar, recria o arquivo
                self.save_persistent_memories()
    def clear(self):
        self.memories.clear()
        if self.main_memory:
            self.main_memory.clear()

    def _apply_retention_policy(self) -> bool:
        if not self.memories:
            return False
        print(f"Aplicando política de retenção===>{self.retention_policy}")
        try:
            non_persistent = {
                k: m for k, m in self.memories.items() if not m.get("persistent", False)
            }

            if not non_persistent:
                return False

            if self.retention_policy == "importance":
                scores = [
                    (k, self.calculate_importance(m)) for k, m in non_persistent.items()
                ]
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
                '''
                scores = []
                for k, m in non_persistent.items():
                    importance = self.calculate_importance(m)

                    if self.main_memory:
                        history = self.main_memory.load_memory_variables({})
                        last_access = None
                        for msg in reversed(history.get("chat_history", [])):
                            if k in msg.content:
                                last_access = msg.create_time
                                break
                        if last_access:
                            age_seconds = (datetime.now() - last_access).total_seconds()
                        else:
                            timestamp = datetime.fromisoformat(
                                m.get("last_access") or m["timestamp"]
                            )
                            age_seconds = (datetime.now() - timestamp).total_seconds()
                    else:
                        timestamp = datetime.fromisoformat(
                            m.get("last_access") or m["timestamp"]
                        )
                        age_seconds = (datetime.now() - timestamp).total_seconds()

                    recency_score = 1.0 - min(age_seconds / (365 * 24 * 3600), 1.0)
                    hybrid_score = importance * 0.7 + recency_score * 0.3
                    scores.append((k, hybrid_score))

                if not scores:
                    return False

                key_to_remove = min(scores, key=lambda x: x[1])[0]
                '''
            else:
                return False

            if key_to_remove in self.memories:
                del self.memories[key_to_remove]
                return True

        except Exception as e:
            print(f"Erro ao aplicar política de retenção: {e}")
            return False

        return False


# Continuação - LangChainFullContextAdapter


class LangChainFullContextAdapter(ContextManager):
    """Adapter que utiliza todas as capacidades de gestão de contexto do LangChain"""

    def __init__(
        self,
        context_memory: Optional[ConversationSummaryBufferMemory] = None,
        main_memory: Optional[Any] = None,
        llm: Optional[Any] = None,
    ):
        super().__init__()
        self.context_memory = context_memory
        self.main_memory = main_memory
        self.llm = llm
        self.current_context = {}
        self.context_history = []

    def set_context(self, context_type: str, context_data: Any):
        """Define contexto com sumarização inteligente"""
        if self.current_context:
            self.context_history.append(self.current_context.copy())

        if (
            isinstance(self.context_memory, ConversationSummaryBufferMemory)
            and self.llm
        ):
            try:
                summary_prompt = (
                    "Gere um sumário do contexto que mantenha informações essenciais:\n"
                    f"Tipo: {context_type}\n"
                    f"Dados: {str(context_data)}"
                )
                context_summary = self.llm(summary_prompt)

                self.context_memory.save_context(
                    {"input": context_type}, {"output": context_summary}
                )

                self.current_context[context_type] = {
                    "data": context_data,
                    "summary": context_summary,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                print(f"Erro ao gerar sumário de contexto: {e}")
                self.current_context[context_type] = {
                    "data": context_data,
                    "timestamp": datetime.now().isoformat(),
                }
                if self.context_memory:
                    self.context_memory.save_context(
                        {"input": context_type}, {"output": str(context_data)}
                    )
        else:
            self.current_context[context_type] = {
                "data": context_data,
                "timestamp": datetime.now().isoformat(),
            }
            if self.context_memory:
                self.context_memory.save_context(
                    {"input": context_type}, {"output": str(context_data)}
                )

        if self.main_memory and self.main_memory != self.context_memory:
            self.main_memory.save_context(
                {"input": f"context_{context_type}"}, {"output": str(context_data)}
            )

    def get_context(self, context_type: str) -> Optional[Any]:
        """Recupera contexto com enriquecimento"""
        context = self.current_context.get(context_type, {})
        if context:
            return context.get("data")

        if self.context_memory:
            try:
                history = self.context_memory.load_memory_variables({})
                messages = history.get("context_history", [])
                for message in messages:
                    if context_type in message.content:
                        return message.content
            except Exception as e:
                print(f"Erro ao buscar contexto do LangChain: {e}")

        if self.main_memory and self.main_memory != self.context_memory:
            try:
                history = self.main_memory.load_memory_variables({})
                messages = history.get("chat_history", [])
                for message in messages:
                    if f"context_{context_type}" in message.content:
                        return message.content
            except Exception as e:
                print(f"Erro ao buscar contexto da memória principal: {e}")

        return None

    def clear_context(self):
        """Limpa contexto atual mantendo histórico"""
        if self.current_context:
            self.context_history.append(self.current_context.copy())

        self.current_context.clear()

        if self.context_memory:
            self.context_memory.clear()
        if self.main_memory and self.main_memory != self.context_memory:
            self.main_memory.clear()


# Continuação - LangChainFullAgentMemorySystem


# ============================================================================
# DATABASE-BACKED MEMORY ADAPTERS
# ============================================================================


class DatabaseLongTermAdapter(LongTermMemory):
    """
    Database-backed long-term memory adapter.
    Replaces pickle files with MySQL database persistence via AgentMemoryService.
    """

    def __init__(
        self,
        capacity: int = 1000,
        memory_service: Any = None,
        agent_id: str = "",
        project_id: str = "",
        conversation_id: Optional[str] = None,
        retention_policy: str = "importance",
    ):
        super().__init__(
            capacity=capacity,
            persistence_path=None,  # Not used for database
            retention_policy=retention_policy,
        )
        self.memory_service = memory_service
        self.agent_id = agent_id
        self.project_id = project_id
        self.conversation_id = conversation_id

        if not memory_service:
            raise ValueError("memory_service is required for DatabaseLongTermAdapter")

    def add(self, key: str, value: Any, persistent: bool = False) -> bool:
        """Store memory item in database"""
        try:
            # Calculate importance score
            importance = 5.0  # Default
            if persistent:
                importance = 10.0  # Higher importance for persistent memories

            # Store in database
            self.memory_service.store_memory(
                agent_id=self.agent_id,
                project_id=self.project_id,
                memory_type="long_term",
                key=key,
                value=value,
                importance=importance,
                conversation_id=self.conversation_id,
            )
            return True
        except Exception as e:
            print(f"Error storing memory in database: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Retrieve memory item from database"""
        try:
            return self.memory_service.recall_memory(
                agent_id=self.agent_id,
                project_id=self.project_id,
                key=key,
                memory_type="long_term",
            )
        except Exception as e:
            print(f"Error retrieving memory from database: {e}")
            return None

    def remove(self, key: str) -> bool:
        """Remove memory item (not implemented - use prune instead)"""
        # Could implement DELETE if needed
        return False

    def clear(self):
        """Clear all memories (dangerous - use prune instead)"""
        pass  # Not implementing for safety

    def get_all(self) -> Dict[str, Any]:
        """Get all memories (for compatibility)"""
        # Not efficient for database - use search instead
        return {}

    def _apply_retention_policy(self) -> bool:
        """Apply retention policy using database pruning"""
        try:
            count = self.memory_service.get_memory_count(
                agent_id=self.agent_id,
                project_id=self.project_id,
                memory_type="long_term",
            )

            if count >= self.capacity:
                deleted = self.memory_service.prune_memory(
                    agent_id=self.agent_id,
                    project_id=self.project_id,
                    memory_type="long_term",
                    retention_policy=self.retention_policy,
                    keep_count=int(self.capacity * 0.8),  # Keep 80% when pruning
                )
                print(f"Pruned {deleted} long-term memory items")
                return True
            return True
        except Exception as e:
            print(f"Error applying retention policy: {e}")
            return False


class DatabaseShortTermAdapter(ShortTermMemory):
    """
    Database-backed short-term memory adapter.
    Stores recent conversation context with automatic expiration.
    """

    def __init__(
        self,
        capacity: int = 100,
        memory_service: Any = None,
        agent_id: str = "",
        project_id: str = "",
        conversation_id: Optional[str] = None,
        ttl_hours: int = 24,  # Time to live for short-term memories
    ):
        super().__init__(capacity=capacity, enable_dedup=True)
        self.memory_service = memory_service
        self.agent_id = agent_id
        self.project_id = project_id
        self.conversation_id = conversation_id
        self.ttl_hours = ttl_hours

        if not memory_service:
            raise ValueError("memory_service is required for DatabaseShortTermAdapter")

    def add(self, item: Any) -> bool:
        """Add item to short-term memory with expiration"""
        try:
            # Generate key from item
            import hashlib
            item_str = str(item)
            key = hashlib.md5(item_str.encode()).hexdigest()[:16]

            self.memory_service.store_memory(
                agent_id=self.agent_id,
                project_id=self.project_id,
                memory_type="short_term",
                key=key,
                value=item,
                importance=1.0,  # Lower importance for short-term
                conversation_id=self.conversation_id,
                expires_in_hours=self.ttl_hours,
            )
            return True
        except Exception as e:
            print(f"Error adding short-term memory: {e}")
            return False

    def get_recent(self, count: int) -> List[Any]:
        """Get N most recent items"""
        # This would require a more complex query
        # For now, return empty - conversation history is handled separately
        return []

    def contains(self, item: Any) -> bool:
        """Check if item exists (for deduplication)"""
        try:
            import hashlib
            item_str = str(item)
            key = hashlib.md5(item_str.encode()).hexdigest()[:16]

            result = self.memory_service.recall_memory(
                agent_id=self.agent_id,
                project_id=self.project_id,
                key=key,
                memory_type="short_term",
            )
            return result is not None
        except:
            return False

    def clear(self):
        """Clear short-term memory"""
        # Prune all short-term memories
        self.memory_service.prune_memory(
            agent_id=self.agent_id,
            project_id=self.project_id,
            memory_type="short_term",
            keep_count=0,
        )


class DatabaseTaskMemorySystem(TaskMemorySystem):
    """
    Task Memory System backed by database.
    Lightweight implementation using DatabaseLongTermAdapter and DatabaseShortTermAdapter.
    """

    def __init__(
        self,
        task_name: str,
        short_term_memory: DatabaseShortTermAdapter,
        long_term_memory: DatabaseLongTermAdapter,
        memory_service: Any,
        agent_id: str,
        project_id: str,
    ):
        super().__init__(task_name=task_name)
        self.short_term = short_term_memory
        self.long_term = long_term_memory
        self.memory_service = memory_service
        self.agent_id = agent_id
        self.project_id = project_id
        self.context_manager = None  # Simple implementation

    def remember(self, key: str, value: Any, long_term: bool = False):
        """Store in short-term or long-term memory"""
        if long_term:
            self.long_term.add(key, value, persistent=True)
        else:
            self.short_term.add(value)

    def recall(self, key: str, search_long_term: bool = True) -> Optional[Any]:
        """Recall memory (check long-term since short-term uses hash keys)"""
        if search_long_term:
            return self.long_term.get(key)
        return None

    def set_context(self, context_type: str, context_data: Any):
        """Store project context"""
        self.memory_service.store_project_context(
            project_id=self.project_id,
            context_type=context_type,
            key=f"{self.agent_id}_{context_type}",
            value=context_data,
            source="agent_execution",
        )

    def get_context(self, context_type: str) -> Optional[Any]:
        """Get project context"""
        context = self.memory_service.get_project_context(
            project_id=self.project_id, context_type=context_type
        )
        return context.get(f"{self.agent_id}_{context_type}")

    def clear(self):
        """Clear memories"""
        self.short_term.clear()
        # Don't clear long-term by default

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "short_term_count": self.memory_service.get_memory_count(
                self.agent_id, self.project_id, "short_term"
            ),
            "long_term_count": self.memory_service.get_memory_count(
                self.agent_id, self.project_id, "long_term"
            ),
        }


class LangChainFullTaskMemorySystem(TaskMemorySystem):
    """Sistema de memória que utiliza todas as capacidades do LangChain"""

    def __init__(
        self,
        task_name: str,
        persistence_path: Optional[Path] = None,
        api_key: Optional[str] = None,
        short_term_capacity: int = 100,
        long_term_capacity: int = 1000,
        memory_type: str = "buffer_summary",
    ):
        super().__init__(
            task_name=task_name,
            persistence_path=persistence_path,
            api_key=api_key,
            short_term_capacity=short_term_capacity,
            long_term_capacity=long_term_capacity,
            memory_type=memory_type,
        )

        if not api_key:
            raise ValueError("API key é necessária para LangChainFull")

        self.llm = OpenAI(api_key=api_key)

        if memory_type == "buffer_summary":
            print("CRIANDO BUFFER SUMMARY")
            self.main_memory = ConversationSummaryBufferMemory(
                llm=self.llm,
                max_token_limit=2000,
                memory_key="chat_history",
                return_messages=True,
            )

            self.window_memory = ConversationBufferWindowMemory(
                memory_key="recent_history", k=short_term_capacity, return_messages=True
            )

            self.context_memory = ConversationSummaryBufferMemory(
                llm=self.llm,
                max_token_limit=1000,
                memory_key="context_history",
                return_messages=True,
            )

        elif memory_type == "buffer_window":
            print("CRIANDO BUFFER WINDOW")
            self.main_memory = ConversationBufferWindowMemory(
                memory_key="chat_history", k=long_term_capacity, return_messages=True
            )
            self.window_memory = self.main_memory
            self.context_memory = self.main_memory

        else:
            print("CRIANDO BUFFER MEMORY")
            self.main_memory = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )
            self.window_memory = self.main_memory
            self.context_memory = self.main_memory

        self.short_term = LangChainFullShortTermAdapter(
            capacity=short_term_capacity,
            window_memory=self.window_memory,
            main_memory=self.main_memory,
            llm=self.llm,
        )
        if persistence_path:
            # Criar diretório se não existir
            print("CRIANDO DIRETÓRIO====>")
            
            task_dir = Path(persistence_path) / self.task_name
            task_dir.mkdir(parents=True, exist_ok=True)
            print(f"{task_dir}")
            memory_path = task_dir / f"{self.task_name}_memory.pkl"
        else:
            
            memory_path = None

        self.long_term = LangChainFullLongTermAdapter(
            capacity=long_term_capacity,
            persistence_path=memory_path,
            main_memory=self.main_memory,
            llm=self.llm,
        )

        self.context = LangChainFullContextAdapter(
            context_memory=self.context_memory,
            main_memory=self.main_memory,
            llm=self.llm,
        )

    def remember(self, key: str, value: Any, long_term: bool = False):
        print("ENTRANDO NO REMEMBER")
        if not long_term:
            self.short_term.add(key, value)

        else:
            self.long_term.add(key, value, persistent=True)
    
    def recall(self, key: str,  search_long_term: bool = True) -> Optional[Any]:
        """Recupera memória com busca inteligente"""
        print("ENTRANDO NO RECALL")
        # Primeiro tenta memória de curto prazo
        if not search_long_term:
            value = self.short_term.get(key)
        
        
        else:
            # Recupera todas as memórias que começam com o nome da task
            all_memories = []
            for memory_key, memory in self.long_term.memories.items():
                if memory_key.startswith(key):
                    all_memories.append(memory["value"])

            if all_memories:
                print(f"Número de memórias encontradas pelo recall: {len(all_memories)}")
                # Ordena por timestamp decrescente
                all_memories.sort(key=lambda x: x['timestamp'], reverse=True)
                value = all_memories

                # Adiciona resultado na memória de curto prazo
                self.short_term.add(key, value)

        return value
    def recallant(self, key: str, search_long_term: bool = True) -> Optional[Any]:
        """Recupera memória com busca inteligente"""
        value = self.short_term.get(key)

        if value is None and search_long_term:
            value = self.long_term.get(key)

            if value is not None:
                self.short_term.add(key, value)

        return value

    def set_context(self, context_type: str, context_data: Any):
        """Define contexto com propagação"""
        self.context.set_context(context_type, context_data)

    def get_context(self, context_type: str) -> Optional[Any]:
        """Recupera contexto"""
        return self.context.get_context(context_type)

    def summarize_memory(self) -> Dict:
        """Gera sumário do estado do sistema de memória"""
        return {
            "task_name": self.task_name,
            "short_term_count": len(self.short_term.memories),
            "long_term_count": len(self.long_term.memories),
            "current_context": self.context.current_context,
        }
class AiTeamMemorySystemFactory:
    """Factory para selecionar o sistema de memória apropriado"""

    @staticmethod
    def create_memory_system(
        implementation: str,
        task_name: str,
        persistence_path: Optional[Path] = None,
        api_key: Optional[str] = None,
        short_term_capacity: int = 100,
        long_term_capacity: int = 1000,
        memory_type: str = "buffer",  # "buffer", "buffer_window", "buffer_summary"
        # Database-specific parameters
        memory_service: Optional[Any] = None,
        agent_id: Optional[str] = None,
        project_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> TaskMemorySystem:
        """
        Seleciona e instancia o sistema de memória apropriado

        Args:
            implementation: "default", "langchain", or "database"
            task_name: Nome da tarefa/agente
            persistence_path: Caminho para persistência (não usado para database)
            api_key: API key para serviços que necessitem
            short_term_capacity: Capacidade da memória de curto prazo
            long_term_capacity: Capacidade da memória de longo prazo
            memory_type: Tipo de memória (apenas para langchain)
            memory_service: AgentMemoryService instance (para database)
            agent_id: ID do agente (para database)
            project_id: ID do projeto (para database)
            conversation_id: ID da conversa (para database)
        """
        if implementation == "default":
            from frameworkagents import AgentMemorySystem as DefaultMemorySystem

            return DefaultMemorySystem(
                task_name=task_name, persistence_path=persistence_path
            )

        elif implementation == "langchain":
            if memory_type == "buffer_summary" and not api_key:
                raise ValueError("API key necessária para memory_type='buffer_summary'")

            return LangChainFullTaskMemorySystem(
                task_name=task_name,
                persistence_path=persistence_path,
                api_key=api_key,
                short_term_capacity=short_term_capacity,
                long_term_capacity=long_term_capacity,
                memory_type=memory_type,
            )

        elif implementation == "database":
            if not memory_service:
                raise ValueError("memory_service is required for database implementation")
            if not agent_id or not project_id:
                raise ValueError("agent_id and project_id are required for database implementation")

            # Create database-backed adapters
            short_term = DatabaseShortTermAdapter(
                capacity=short_term_capacity,
                memory_service=memory_service,
                agent_id=agent_id,
                project_id=project_id,
                conversation_id=conversation_id,
            )

            long_term = DatabaseLongTermAdapter(
                capacity=long_term_capacity,
                memory_service=memory_service,
                agent_id=agent_id,
                project_id=project_id,
                conversation_id=conversation_id,
            )

            # Create a simple TaskMemorySystem with database adapters
            # We'll create a DatabaseTaskMemorySystem class
            return DatabaseTaskMemorySystem(
                task_name=task_name,
                short_term_memory=short_term,
                long_term_memory=long_term,
                memory_service=memory_service,
                agent_id=agent_id,
                project_id=project_id,
            )

        else:
            raise ValueError(f"Implementação de memória desconhecida: {implementation}")
