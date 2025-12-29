"""
Agent & Task Generation Models
===============================

Pydantic models for agent and task generation from specifications.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DetailLevel(str, Enum):
    """Nível de detalhe para geração de agentes e tarefas"""
    CONCISE = "concise"
    BALANCED = "balanced"
    DETAILED = "detailed"


class GenerationStatus(str, Enum):
    """Status da geração"""
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


# ═══════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════

class AgentTaskGenerationRequest(BaseModel):
    """Request para gerar agentes e tarefas a partir de especificação funcional OU documento de especificação de agentes/tarefas"""

    # AMBOS SÃO OPCIONAIS (mas pelo menos um deve ser fornecido)
    specification_session_id: Optional[str] = Field(
        default=None,
        description="ID da sessão de especificação funcional"
    )

    agent_task_spec_session_id: Optional[str] = Field(
        default=None,
        description="ID da sessão de especificação de agentes/tarefas (documento MD intermediário)"
    )

    specification_version: int = Field(
        default=1,
        ge=1,
        description="Versão da especificação a usar"
    )

    detail_level: DetailLevel = Field(
        default=DetailLevel.BALANCED,
        description="Nível de detalhe (concise | balanced | detailed)"
    )

    frameworks: List[str] = Field(
        default=["CrewAI"],
        description="Frameworks de multi-agente suportados"
    )

    max_agents: int = Field(
        default=10,
        ge=1,
        le=20,
        description="Número máximo de agentes a gerar"
    )

    custom_instructions: Optional[str] = Field(
        default=None,
        description="Instruções adicionais para o LLM"
    )

    auto_generate_yaml: bool = Field(
        default=True,
        description="Gerar automaticamente arquivos YAML"
    )

    @validator('agent_task_spec_session_id')
    def validate_source(cls, v, values):
        """Garantir que pelo menos um dos dois IDs foi fornecido"""
        if not v and not values.get('specification_session_id'):
            raise ValueError('Deve fornecer specification_session_id OU agent_task_spec_session_id')
        return v

    class Config:
        schema_extra = {
            "example": {
                "specification_session_id": "550e8400-e29b-41d4-a716-446655440000",
                "specification_version": 1,
                "detail_level": "balanced",
                "frameworks": ["CrewAI"],
                "max_agents": 8,
                "custom_instructions": "Priorizar agentes especializados em validação",
                "auto_generate_yaml": True
            }
        }


class AgentTaskRefinementRequest(BaseModel):
    """Request para refinar agentes/tarefas via chat"""

    session_id: str = Field(
        ...,
        description="ID da sessão de agent_task a refinar"
    )

    refinement_message: str = Field(
        ...,
        min_length=10,
        description="Mensagem do usuário pedindo refinamento"
    )

    class Config:
        schema_extra = {
            "example": {
                "session_id": "650e8400-e29b-41d4-a716-446655440000",
                "refinement_message": "Adicione um agente para validar dados de entrada antes do processamento"
            }
        }


# ═══════════════════════════════════════════════════════════
# AGENT DATA MODELS
# ═══════════════════════════════════════════════════════════

class AgentData(BaseModel):
    """Estrutura de um agente gerado"""

    name: str = Field(
        ...,
        pattern=r"^[a-z][a-z0-9_]*$",
        description="Nome do agente em snake_case"
    )

    role: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="Descrição curta do papel do agente (1-2 linhas)"
    )

    goal: str = Field(
        ...,
        min_length=20,
        max_length=500,
        description="Objetivo específico e mensurável do agente"
    )

    backstory: str = Field(
        ...,
        min_length=50,
        description="Contexto detalhado com responsabilidades numeradas"
    )

    verbose: bool = Field(
        default=True,
        description="Habilitar logs detalhados"
    )

    allow_delegation: bool = Field(
        default=False,
        description="Permitir delegação para outros agentes"
    )

    suggested_tools: List[str] = Field(
        default_factory=list,
        description="Lista de ferramentas CrewAI sugeridas"
    )

    delegation_targets: List[str] = Field(
        default_factory=list,
        description="Nomes de outros agentes para os quais pode delegar"
    )

    rationale: str = Field(
        ...,
        min_length=50,
        description="Justificativa de por que este agente é necessário"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "document_analyzer_agent",
                "role": "Analisador Especializado de Documentos Funcionais",
                "goal": "Extrair entidades, relacionamentos e regras de negócio de documentos de requisitos",
                "backstory": "Você é um especialista em análise de documentos técnicos responsável por:\n1. Ler e interpretar documentos de requisitos funcionais\n2. Identificar entidades de domínio e seus atributos\n3. Extrair regras de negócio e validações",
                "verbose": True,
                "allow_delegation": False,
                "suggested_tools": ["document_reader_tool", "pdf_reader_tool", "json_parser_tool"],
                "delegation_targets": [],
                "rationale": "Este agente é essencial para isolar a complexidade de análise documental."
            }
        }


# ═══════════════════════════════════════════════════════════
# TASK DATA MODELS
# ═══════════════════════════════════════════════════════════

class TaskData(BaseModel):
    """Estrutura de uma task gerada"""

    name: str = Field(
        ...,
        pattern=r"^[a-z][a-z0-9_]*$",
        description="Nome da task em snake_case (verbo + objeto)"
    )

    description: str = Field(
        ...,
        min_length=100,
        description="Instruções completas com input format e process steps"
    )

    expected_output: str = Field(
        ...,
        min_length=50,
        description="Formato exato do resultado esperado"
    )

    agent: str = Field(
        ...,
        description="Nome do agente responsável (deve existir em agents)"
    )

    tools: List[str] = Field(
        default_factory=list,
        description="Lista de ferramentas CrewAI necessárias"
    )

    requires: List[str] = Field(
        default_factory=list,
        description="Campos do state necessários como input"
    )

    produces: List[str] = Field(
        default_factory=list,
        description="Campos que esta task adiciona ao state"
    )

    dependencies: List[str] = Field(
        default_factory=list,
        description="Nomes de tasks que devem executar antes"
    )

    rationale: str = Field(
        ...,
        min_length=50,
        description="Justificativa de por que esta task é necessária"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "extract_functional_requirements",
                "description": "IMPORTANTE: Processar APENAS o documento real fornecido.\n\nExtrair requisitos funcionais do documento...\n\nProcess steps:\n1. Parse documento\n2. Identificar seção 3\n3. Extrair requisitos",
                "expected_output": "Retornar JSON contendo:\n- total_requirements: número\n- requirements: array",
                "agent": "document_analyzer_agent",
                "tools": ["document_reader_tool", "json_parser_tool"],
                "requires": ["specification_document"],
                "produces": ["total_requirements", "requirements"],
                "dependencies": [],
                "rationale": "Esta task é fundamental para estruturar requisitos de forma programática."
            }
        }


# ═══════════════════════════════════════════════════════════
# RESPONSE MODELS
# ═══════════════════════════════════════════════════════════

class DependencyGraph(BaseModel):
    """Grafo de dependências entre tasks"""

    nodes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Nós do grafo (tasks)"
    )

    edges: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Arestas do grafo (dependencies)"
    )

    class Config:
        schema_extra = {
            "example": {
                "nodes": [
                    {"id": "task1", "label": "Extract Requirements"},
                    {"id": "task2", "label": "Analyze Data"}
                ],
                "edges": [
                    {"from": "task1", "to": "task2"}
                ]
            }
        }


class AgentTaskGenerationResponse(BaseModel):
    """Response da geração de agentes e tarefas"""

    session_id: str = Field(
        ...,
        description="ID único da sessão de geração"
    )

    session_name: str = Field(
        ...,
        description="Nome da sessão (auto-gerado)"
    )

    agents: List[AgentData] = Field(
        default_factory=list,
        description="Lista de agentes gerados"
    )

    tasks: List[TaskData] = Field(
        default_factory=list,
        description="Lista de tarefas geradas"
    )

    agents_yaml: Optional[str] = Field(
        default=None,
        description="Conteúdo do arquivo agents.yaml"
    )

    tasks_yaml: Optional[str] = Field(
        default=None,
        description="Conteúdo do arquivo tasks.yaml"
    )

    dependency_graph: Optional[DependencyGraph] = Field(
        default=None,
        description="Grafo de dependências entre tasks"
    )

    status: GenerationStatus = Field(
        default=GenerationStatus.COMPLETED,
        description="Status da geração"
    )

    message: str = Field(
        default="Agentes e tarefas gerados com sucesso",
        description="Mensagem descritiva do resultado"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Data/hora de criação"
    )

    class Config:
        schema_extra = {
            "example": {
                "session_id": "750e8400-e29b-41d4-a716-446655440000",
                "session_name": "Geração - 2025-12-23 14:30",
                "agents": [],  # Lista de AgentData
                "tasks": [],   # Lista de TaskData
                "agents_yaml": "agent_name:\n  role: ...",
                "tasks_yaml": "task_name:\n  description: ...",
                "dependency_graph": None,
                "status": "completed",
                "message": "8 agentes e 12 tarefas gerados com sucesso",
                "created_at": "2025-12-23T14:30:00Z"
            }
        }


class AgentTaskRefinementResponse(BaseModel):
    """Response do refinamento de agentes/tarefas"""

    session_id: str = Field(
        ...,
        description="ID da sessão refinada"
    )

    refined_agents: List[AgentData] = Field(
        default_factory=list,
        description="Agentes após refinamento"
    )

    refined_tasks: List[TaskData] = Field(
        default_factory=list,
        description="Tarefas após refinamento"
    )

    agents_yaml: Optional[str] = Field(
        default=None,
        description="YAML atualizado dos agentes"
    )

    tasks_yaml: Optional[str] = Field(
        default=None,
        description="YAML atualizado das tarefas"
    )

    refinement_summary: str = Field(
        ...,
        description="Resumo das mudanças aplicadas"
    )

    status: GenerationStatus = Field(
        default=GenerationStatus.COMPLETED,
        description="Status do refinamento"
    )

    message: str = Field(
        default="Refinamento aplicado com sucesso",
        description="Mensagem descritiva"
    )


# ═══════════════════════════════════════════════════════════
# DATABASE SESSION MODELS
# ═══════════════════════════════════════════════════════════

class AgentTaskSessionDB(BaseModel):
    """Model para sessão salva no banco de dados"""

    id: str
    project_id: str
    user_id: str
    session_name: str
    specification_session_id: str
    specification_version: int
    detail_level: DetailLevel
    frameworks: List[str]
    custom_instructions: Optional[str]
    agents_count: int
    tasks_count: int
    agents_yaml: Optional[str]
    tasks_yaml: Optional[str]
    agents_json: Optional[List[AgentData]]
    tasks_json: Optional[List[TaskData]]
    dependency_graph: Optional[DependencyGraph]
    status: GenerationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AgentTaskChatMessage(BaseModel):
    """Mensagem do chat de refinamento"""

    id: str
    session_id: str
    sender: str  # 'user' | 'system' | 'assistant'
    message: str
    message_type: str  # 'status' | 'progress' | 'result' | 'error'
    created_at: datetime

    class Config:
        orm_mode = True


# ═══════════════════════════════════════════════════════════
# LIST/QUERY MODELS
# ═══════════════════════════════════════════════════════════

class AgentTaskSessionSummary(BaseModel):
    """Resumo de uma sessão para listagem"""

    id: str
    session_name: str
    specification_session_id: str
    specification_version: int
    agents_count: int
    tasks_count: int
    status: GenerationStatus
    created_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "id": "850e8400-e29b-41d4-a716-446655440000",
                "session_name": "Geração - 2025-12-23 14:30",
                "specification_session_id": "550e8400-e29b-41d4-a716-446655440000",
                "specification_version": 1,
                "agents_count": 8,
                "tasks_count": 12,
                "status": "completed",
                "created_at": "2025-12-23T14:30:00Z"
            }
        }


class AgentTaskSessionListResponse(BaseModel):
    """Response para listagem de sessões"""

    sessions: List[AgentTaskSessionSummary]
    total: int

    class Config:
        schema_extra = {
            "example": {
                "sessions": [],  # Lista de AgentTaskSessionSummary
                "total": 5
            }
        }
