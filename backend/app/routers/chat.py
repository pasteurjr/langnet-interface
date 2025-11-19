"""
Chat Messages Router
API endpoints for chat message management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from app.models.chat_message import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatMessageUpdate,
    ChatMessageListResponse
)
from app.database import (
    save_chat_message,
    get_chat_messages,
    get_chat_message,
    update_chat_message,
    delete_chat_message,
    get_chat_message_count,
    get_chat_threads
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def create_message(
    session_id: str,
    message: ChatMessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new chat message"""
    try:
        message.session_id = session_id
        message_id = save_chat_message(
            session_id=message.session_id,
            sender_type=message.sender_type.value,
            message_text=message.message_text,
            message_type=message.message_type.value,
            task_execution_id=message.task_execution_id,
            agent_id=message.agent_id,
            sender_name=message.sender_name,
            parent_message_id=message.parent_message_id,
            metadata=message.metadata
        )
        created_message = get_chat_message(message_id)
        if not created_message:
            raise HTTPException(status_code=500, detail="Failed to retrieve created message")
        return ChatMessageResponse(**created_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create message: {str(e)}")


@router.get("/sessions/{session_id}/messages", response_model=ChatMessageListResponse)
async def list_messages(
    session_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    message_type: Optional[str] = Query(None),
    include_deleted: bool = Query(False),
    current_user: dict = Depends(get_current_user)
):
    """List messages for a session with pagination"""
    try:
        offset = (page - 1) * page_size
        messages = get_chat_messages(
            session_id=session_id,
            limit=page_size + 1,
            offset=offset,
            include_deleted=include_deleted,
            message_type=message_type
        )
        print(f"📨 Found {len(messages)} messages for session {session_id}")
        has_more = len(messages) > page_size
        if has_more:
            messages = messages[:-1]
        total = get_chat_message_count(session_id, include_deleted)

        # Convert messages to response objects one by one with error handling
        message_responses = []
        for msg in messages:
            try:
                print(f"🔄 Converting message {msg.get('id')}: sender_type={msg.get('sender_type')}, message_type={msg.get('message_type')}")
                message_responses.append(ChatMessageResponse(**msg))
            except Exception as conv_error:
                print(f"❌ Error converting message {msg.get('id')}: {conv_error}")
                print(f"   Message data: {msg}")
                raise

        return ChatMessageListResponse(
            messages=message_responses,
            total=total,
            page=page,
            page_size=page_size,
            has_more=has_more
        )
    except Exception as e:
        import traceback
        print(f"❌ Error in list_messages: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to list messages: {str(e)}")


@router.get("/messages/{message_id}", response_model=ChatMessageResponse)
async def get_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a single message by ID"""
    message = get_chat_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return ChatMessageResponse(**message)


@router.patch("/messages/{message_id}", response_model=ChatMessageResponse)
async def update_message(
    message_id: str,
    updates: ChatMessageUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a message"""
    existing = get_chat_message(message_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Message not found")
    affected_rows = update_chat_message(
        message_id=message_id,
        message_text=updates.message_text,
        is_read=updates.is_read,
        is_pinned=updates.is_pinned,
        metadata=updates.metadata
    )
    if affected_rows == 0:
        raise HTTPException(status_code=400, detail="No fields to update")
    updated_message = get_chat_message(message_id)
    return ChatMessageResponse(**updated_message)


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    permanent: bool = Query(False),
    current_user: dict = Depends(get_current_user)
):
    """Delete a message (soft delete by default)"""
    existing = get_chat_message(message_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Message not found")
    affected_rows = delete_chat_message(message_id, soft_delete=not permanent)
    if affected_rows == 0:
        raise HTTPException(status_code=400, detail="Failed to delete message")
    return {"message": "Message deleted successfully", "permanent": permanent}


@router.get("/messages/{message_id}/threads", response_model=list[ChatMessageResponse])
async def get_message_threads(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all replies/threads for a message"""
    threads = get_chat_threads(message_id)
    return [ChatMessageResponse(**msg) for msg in threads]


class RefineRequirementsRequest(BaseModel):
    message: str
    parent_message_id: Optional[str] = None


@router.post("/sessions/{session_id}/refine")
async def refine_requirements(
    session_id: str,
    request: RefineRequirementsRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Conversational refinement of requirements
    User sends a message to refine/clarify the generated requirements
    Agent responds with updated analysis

    Args:
        session_id: Chat session ID
        request: Refinement message and optional parent message ID
        current_user: Authenticated user

    Returns:
        Agent response with refined requirements
    """
    try:
        # Save user message
        user_message_id = save_chat_message(
            session_id=session_id,
            sender_type='user',
            message_text=request.message,
            message_type='chat',
            sender_name='Você',
            parent_message_id=request.parent_message_id,
            metadata={'type': 'refinement_request'}
        )

        # TODO: Aqui será integrado com LangNet para processamento real
        # Por enquanto, retornamos uma resposta simulada

        # Save agent response
        agent_response = f"Entendi sua solicitação: '{request.message}'. Processando refinamento..."
        agent_message_id = save_chat_message(
            session_id=session_id,
            sender_type='agent',
            message_text=agent_response,
            message_type='chat',
            sender_name='Agente Analista',
            parent_message_id=user_message_id,
            metadata={'type': 'refinement_response', 'status': 'processing'}
        )

        agent_message = get_chat_message(agent_message_id)

        return {
            "user_message_id": user_message_id,
            "agent_message": ChatMessageResponse(**agent_message),
            "status": "processing",
            "message": "Refinement request received. Processing with AI agent..."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process refinement: {str(e)}")
