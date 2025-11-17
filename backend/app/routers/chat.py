"""
Chat API Endpoints

Provides REST API endpoints for agent conversations with memory support.
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path
import json
import uuid

# Add services to path
services_path = Path(__file__).parent.parent.parent / "services"
sys.path.insert(0, str(services_path))

from memory_service import AgentMemoryService

# Add agents to path
agents_path = Path(__file__).parent.parent.parent / "agents"
sys.path.insert(0, str(agents_path))

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class CreateConversationRequest(BaseModel):
    project_id: str
    agent_id: str
    conversation_type: str = "chat"  # chat, document_analysis, task_execution, refinement
    context_data: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None


class SendMessageRequest(BaseModel):
    conversation_id: str
    message: str
    agent_id: str


class ConversationResponse(BaseModel):
    id: str
    project_id: str
    agent_id: str
    conversation_type: str
    context_data: Optional[Dict[str, Any]]
    started_at: str
    ended_at: Optional[str]
    message_count: int
    status: str


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    agent_id: Optional[str]
    sender: str  # user, agent, system
    content: str
    message_type: str
    metadata: Optional[Dict[str, Any]]
    timestamp: str


# ============================================================================
# CONVERSATION ENDPOINTS
# ============================================================================


@router.post("/conversations", response_model=Dict[str, str])
async def create_conversation(request: CreateConversationRequest):
    """
    Create a new conversation with an agent.

    Returns the conversation_id.
    """
    try:
        memory_service = AgentMemoryService()

        conv_id = memory_service.create_conversation(
            project_id=request.project_id,
            agent_id=request.agent_id,
            conversation_type=request.conversation_type,
            context_data=request.context_data,
            user_id=request.user_id,
        )

        return {"conversation_id": conv_id, "status": "created"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")


@router.get("/conversations/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation(conversation_id: str):
    """Get conversation details"""
    try:
        memory_service = AgentMemoryService()
        conversation = memory_service.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return conversation

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation: {str(e)}")


@router.put("/conversations/{conversation_id}/end")
async def end_conversation(conversation_id: str):
    """Mark conversation as completed"""
    try:
        memory_service = AgentMemoryService()
        success = memory_service.end_conversation(conversation_id)

        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {"status": "completed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ending conversation: {str(e)}")


@router.get("/project/{project_id}/conversations")
async def get_project_conversations(
    project_id: str,
    conversation_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
):
    """Get all conversations for a project"""
    try:
        memory_service = AgentMemoryService()
        conversations = memory_service.get_project_conversations(
            project_id=project_id,
            conversation_type=conversation_type,
            status=status,
            limit=limit,
        )

        return {"conversations": conversations, "count": len(conversations)}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving project conversations: {str(e)}"
        )


# ============================================================================
# MESSAGE ENDPOINTS
# ============================================================================


@router.post("/messages")
async def send_message(request: SendMessageRequest):
    """
    Send a message to an agent and get response.

    This endpoint:
    1. Stores the user message
    2. Loads conversation history
    3. Executes the agent with memory
    4. Stores the agent response
    5. Returns the response
    """
    try:
        memory_service = AgentMemoryService()

        # 1. Get conversation
        conversation = memory_service.get_conversation(request.conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # 2. Store user message
        memory_service.store_message(
            conversation_id=request.conversation_id,
            sender="user",
            content=request.message,
            message_type="text",
        )

        # 3. Load recent conversation history (last 10 messages)
        history = memory_service.get_recent_messages(request.conversation_id, count=10)

        # 4. Get context data
        context_data = conversation.get("context_data", {})

        # 5. Execute agent with memory
        # TODO: Import and execute specific agent based on agent_id
        # For now, return a placeholder response
        agent_response = f"Agent {request.agent_id} received your message: '{request.message}'. " \
                        f"(Agent execution will be implemented in next step)"

        # 6. Store agent response
        response_id = memory_service.store_message(
            conversation_id=request.conversation_id,
            sender="agent",
            content=agent_response,
            message_type="text",
            agent_id=request.agent_id,
        )

        return {
            "message_id": response_id,
            "response": agent_response,
            "conversation_id": request.conversation_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str, limit: int = 50, offset: int = 0):
    """Get message history for a conversation"""
    try:
        memory_service = AgentMemoryService()
        messages = memory_service.get_conversation_history(
            conversation_id=conversation_id, limit=limit, offset=offset
        )

        return {"messages": messages, "count": len(messages)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")


# ============================================================================
# MEMORY ENDPOINTS
# ============================================================================


@router.get("/memory/agent/{agent_id}/recall")
async def recall_agent_memory(agent_id: str, project_id: str, key: str):
    """Recall a specific memory by key"""
    try:
        memory_service = AgentMemoryService()
        value = memory_service.recall_memory(
            agent_id=agent_id, project_id=project_id, key=key
        )

        if value is None:
            raise HTTPException(status_code=404, detail="Memory not found")

        return {"key": key, "value": value}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recalling memory: {str(e)}")


@router.post("/memory/agent/{agent_id}/store")
async def store_agent_memory(
    agent_id: str,
    project_id: str,
    key: str,
    value: Any,
    memory_type: str = "long_term",
    importance: float = 5.0,
):
    """Store a memory item"""
    try:
        memory_service = AgentMemoryService()
        memory_id = memory_service.store_memory(
            agent_id=agent_id,
            project_id=project_id,
            memory_type=memory_type,
            key=key,
            value=value,
            importance=importance,
        )

        return {"memory_id": memory_id, "status": "stored"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing memory: {str(e)}")


@router.get("/memory/project/{project_id}/context")
async def get_project_context(project_id: str, context_type: Optional[str] = None):
    """Get project context"""
    try:
        memory_service = AgentMemoryService()
        context = memory_service.get_project_context(
            project_id=project_id, context_type=context_type
        )

        return {"context": context}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving context: {str(e)}")


# ============================================================================
# MEMORY MANAGEMENT ENDPOINTS
# ============================================================================


@router.delete("/memory/agent/{agent_id}/prune")
async def prune_agent_memory(
    agent_id: str,
    project_id: str,
    memory_type: str = "short_term",
    retention_policy: str = "importance",
    keep_count: int = 100,
):
    """Prune old/low-importance memory items"""
    try:
        memory_service = AgentMemoryService()
        deleted_count = memory_service.prune_memory(
            agent_id=agent_id,
            project_id=project_id,
            memory_type=memory_type,
            retention_policy=retention_policy,
            keep_count=keep_count,
        )

        return {"deleted_count": deleted_count, "status": "pruned"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error pruning memory: {str(e)}")


@router.get("/memory/stats/{agent_id}")
async def get_memory_stats(agent_id: str, project_id: str):
    """Get memory usage statistics for an agent"""
    try:
        memory_service = AgentMemoryService()

        stats = {
            "short_term_count": memory_service.get_memory_count(
                agent_id, project_id, "short_term"
            ),
            "long_term_count": memory_service.get_memory_count(
                agent_id, project_id, "long_term"
            ),
            "context_count": memory_service.get_memory_count(
                agent_id, project_id, "context"
            ),
            "entity_count": memory_service.get_memory_count(agent_id, project_id, "entity"),
        }

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")


# ============================================================================
# WEBSOCKET ENDPOINT (Real-time chat)
# ============================================================================


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    """
    WebSocket endpoint for real-time chat with agents.

    Client sends: {"message": "...", "agent_id": "..."}
    Server sends: {"type": "message", "content": "...", "sender": "agent"}
                 {"type": "thinking", "content": "..."} (optional)
                 {"type": "error", "content": "..."}
    """
    await websocket.accept()

    try:
        memory_service = AgentMemoryService()

        # Verify conversation exists
        conversation = memory_service.get_conversation(conversation_id)
        if not conversation:
            await websocket.send_json({"type": "error", "content": "Conversation not found"})
            await websocket.close()
            return

        await websocket.send_json(
            {"type": "system", "content": f"Connected to conversation {conversation_id}"}
        )

        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = data.get("message", "")
            agent_id = data.get("agent_id", conversation["agent_id"])

            if not message:
                continue

            # Store user message
            memory_service.store_message(
                conversation_id=conversation_id,
                sender="user",
                content=message,
                message_type="text",
            )

            # Echo back user message
            await websocket.send_json({"type": "user_message", "content": message})

            # Simulate "thinking" state
            await websocket.send_json(
                {"type": "thinking", "content": f"{agent_id} is processing..."}
            )

            # TODO: Execute agent and stream response
            # For now, send placeholder
            agent_response = f"Agent {agent_id} received: '{message}'"

            # Store agent response
            memory_service.store_message(
                conversation_id=conversation_id,
                sender="agent",
                content=agent_response,
                message_type="text",
                agent_id=agent_id,
            )

            # Send agent response
            await websocket.send_json({"type": "agent_message", "content": agent_response})

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for conversation {conversation_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_json({"type": "error", "content": str(e)})
        await websocket.close()
