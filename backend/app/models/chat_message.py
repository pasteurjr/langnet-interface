"""
Chat Message Models
Pydantic models for chat messages
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any
from datetime import datetime
from enum import Enum


class SenderType(str, Enum):
    """Tipo de remetente da mensagem"""
    user = "user"
    agent = "agent"
    system = "system"
    assistant = "assistant"


class MessageType(str, Enum):
    """Tipo/categoria da mensagem"""
    chat = "chat"
    status = "status"
    progress = "progress"
    result = "result"
    error = "error"
    warning = "warning"
    info = "info"
    document = "document"


class ChatMessageBase(BaseModel):
    """Base model for chat message"""
    session_id: str = Field(..., description="ID da sessão de execução")
    task_execution_id: Optional[str] = Field(None, description="ID da execução da task")
    agent_id: Optional[str] = Field(None, description="ID do agente")
    sender_type: SenderType = Field(..., description="Tipo de remetente")
    sender_name: Optional[str] = Field(None, description="Nome do remetente")
    message_text: str = Field(..., description="Conteúdo da mensagem")
    message_type: MessageType = Field(MessageType.chat, description="Tipo da mensagem")
    parent_message_id: Optional[str] = Field(None, description="ID da mensagem pai")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")


class ChatMessageCreate(ChatMessageBase):
    """Model for creating a chat message"""
    pass


class ChatMessageUpdate(BaseModel):
    """Model for updating a chat message"""
    message_text: Optional[str] = None
    is_read: Optional[bool] = None
    is_pinned: Optional[bool] = None
    is_deleted: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageResponse(ChatMessageBase):
    """Model for chat message response"""
    id: str
    timestamp: datetime
    sequence_number: Optional[int] = None
    is_read: bool = False
    is_pinned: bool = False
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatMessageListResponse(BaseModel):
    """Model for list of chat messages"""
    messages: list[ChatMessageResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
