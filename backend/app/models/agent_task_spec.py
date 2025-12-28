"""
Agent Task Specification Models
================================
Pydantic models para geração de especificação intermediária de agentes/tarefas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DetailLevel(str, Enum):
    """Nível de detalhamento"""
    CONCISE = "concise"
    BALANCED = "balanced"
    DETAILED = "detailed"


class AgentTaskSpecStatus(str, Enum):
    """Status da geração"""
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    REVIEWING = "reviewing"


class ApprovalStatus(str, Enum):
    """Status de aprovação"""
    PENDING = "pending"
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    REJECTED = "rejected"


# ═══════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════

class GenerateAgentTaskSpecRequest(BaseModel):
    """Request para gerar especificação de agentes/tarefas"""

    specification_session_id: str = Field(
        ...,
        description="ID da sessão de especificação funcional"
    )
    specification_version: int = Field(
        default=1,
        ge=1,
        description="Versão da especificação funcional"
    )
    detail_level: DetailLevel = Field(
        default=DetailLevel.BALANCED,
        description="Nível de detalhamento"
    )
    frameworks: List[str] = Field(
        default=["CrewAI"],
        description="Frameworks de multi-agente"
    )
    max_agents: int = Field(
        default=10,
        ge=1,
        le=20,
        description="Número máximo de agentes"
    )
    custom_instructions: Optional[str] = Field(
        default=None,
        description="Instruções adicionais"
    )

    class Config:
        schema_extra = {
            "example": {
                "specification_session_id": "550e8400-e29b-41d4-a716-446655440000",
                "specification_version": 1,
                "detail_level": "balanced",
                "frameworks": ["CrewAI"],
                "max_agents": 10,
                "custom_instructions": "Priorizar agentes especializados em validação"
            }
        }


class RefineAgentTaskSpecRequest(BaseModel):
    """Request para refinar especificação via chat"""

    message: str = Field(
        ...,
        min_length=10,
        description="Mensagem de refinamento"
    )
    action_type: str = Field(
        default="refine",
        description="'refine' modifica documento | 'chat' apenas analisa"
    )


# ═══════════════════════════════════════════════════════════
# RESPONSE MODELS
# ═══════════════════════════════════════════════════════════

class AgentTaskSpecResponse(BaseModel):
    """Response da geração/consulta de especificação"""

    session_id: str
    session_name: str
    agent_task_spec_document: Optional[str] = None
    total_agents: int = 0
    total_tasks: int = 0
    status: AgentTaskSpecStatus
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    message: str
    created_at: datetime


class AgentTaskSpecVersionResponse(BaseModel):
    """Response de versão histórica"""

    session_id: str
    version: int
    agent_task_spec_document: str
    created_at: datetime
    change_type: str
    change_description: Optional[str]


class ChatMessageResponse(BaseModel):
    """Response de mensagem de chat"""

    id: str
    session_id: str
    sender_type: str
    message_text: str
    message_type: str
    timestamp: datetime


class AgentTaskSpecListResponse(BaseModel):
    """Response para listagem de sessões"""

    sessions: List[AgentTaskSpecResponse]
    total: int
