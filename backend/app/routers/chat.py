"""
Chat Messages Router
API endpoints for chat message management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
import asyncio
from pathlib import Path
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
    get_chat_threads,
    get_db_connection
)
from app.dependencies import get_current_user
from app.parsers import DocumentParser
from utils.pdf_processor import process_pdf_for_agent, chunk_text
from agents.langnetagents import execute_document_analysis_workflow

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
        # print(f"📨 Found {len(messages)} messages for session {session_id}")  # COMMENTED TO REDUCE LOG SPAM
        has_more = len(messages) > page_size
        if has_more:
            messages = messages[:-1]
        total = get_chat_message_count(session_id, include_deleted)

        # Convert messages to response objects one by one with error handling
        message_responses = []
        for msg in messages:
            try:
                # print(f"🔄 Converting message {msg.get('id')}: sender_type={msg.get('sender_type')}, message_type={msg.get('message_type')}")  # COMMENTED TO REDUCE LOG SPAM
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


@router.get("/sessions/{session_id}/status")
async def get_session_status(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get execution session status and updated requirements document

    Args:
        session_id: Execution session ID
        current_user: Authenticated user

    Returns:
        Session status, requirements document, and metadata
    """
    try:
        with get_db_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    id,
                    session_name,
                    project_id,
                    user_id,
                    requirements_document,
                    status,
                    started_at,
                    finished_at
                FROM execution_sessions
                WHERE id = %s
            """, (session_id,))
            session = cursor.fetchone()
            cursor.close()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Check authorization
        if session['user_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Not authorized to access this session")

        return {
            "session_id": session['id'],
            "session_name": session['session_name'],
            "project_id": session['project_id'],
            "status": session['status'],
            "requirements_document": session['requirements_document'],
            "doc_size": len(session['requirements_document'] or ''),
            "started_at": session['started_at'].isoformat() if session['started_at'] else None,
            "finished_at": session['finished_at'].isoformat() if session['finished_at'] else None,
            "created_at": session['started_at'].isoformat() if session['started_at'] else None
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get session status: {str(e)}")


class RefineRequirementsRequest(BaseModel):
    message: str
    parent_message_id: Optional[str] = None


async def execute_refinement_workflow(
    session_id: str,
    refinement_instructions: str,
    current_requirements: str,
    project_id: str,
    agent_message_id: str
):
    """
    Execute refinement workflow with agent in background

    Args:
        session_id: Execution session ID
        refinement_instructions: User's refinement request
        current_requirements: Current requirements document
        project_id: Project ID for loading documents
        agent_message_id: Message ID to update with results
    """
    try:
        print(f"\n{'='*80}")
        print(f"[REFINEMENT] Starting refinement workflow")
        print(f"[REFINEMENT] Session ID: {session_id}")
        print(f"[REFINEMENT] Project ID: {project_id}")
        print(f"[REFINEMENT] Instructions length: {len(refinement_instructions)} chars")
        print(f"[REFINEMENT] Current requirements length: {len(current_requirements)} chars")
        print(f"{'='*80}\n")

        # 0. Update session status to 'processing'
        with get_db_connection() as db:
            cursor = db.cursor()
            cursor.execute("""
                UPDATE execution_sessions
                SET status = 'processing'
                WHERE id = %s
            """, (session_id,))
            db.commit()
            cursor.close()
        print(f"[REFINEMENT] Session status updated to 'processing'")

        # 1. Load original documents from the project
        with get_db_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, filename, file_path, file_type
                FROM documents
                WHERE project_id = %s
                ORDER BY uploaded_at DESC
            """, (project_id,))
            documents = cursor.fetchall()
            cursor.close()

        print(f"[REFINEMENT] Found {len(documents)} documents for project {project_id}")

        # 2. Extract and chunk document content (same pattern as documents.py)
        all_documents_content = ""
        all_documents_info = []

        for idx, doc in enumerate(documents, 1):
            doc_id = doc['id']
            doc_filename = doc['filename']
            doc_path = doc['file_path']
            doc_type = Path(doc_path).suffix[1:]  # .pdf -> pdf

            print(f"[REFINEMENT] Processing document {idx}/{len(documents)}: {doc_filename}")

            # Use chunking for PDFs
            if doc_type == "pdf":
                try:
                    result = process_pdf_for_agent(
                        doc_path,
                        max_pages=50,
                        chunk_size=4000,
                        chunk_overlap=400,
                        max_chunks=None
                    )
                    doc_text = "\n\n---CHUNK---\n\n".join(result['formatted_chunks'])
                    word_count = result['stats']['raw_text_words']
                    print(f"[REFINEMENT] PDF extracted: {len(result['formatted_chunks'])} chunks, {word_count} words")
                except Exception as e:
                    print(f"[REFINEMENT] PDF chunking failed, using simple parser: {e}")
                    parsed = DocumentParser.parse(doc_path)
                    if not parsed["success"]:
                        print(f"[REFINEMENT] Failed to parse {doc_filename}")
                        continue
                    doc_text = parsed["text"]
                    word_count = len(doc_text.split())
            else:
                # Simple parser for other formats
                parsed = DocumentParser.parse(doc_path)
                if not parsed["success"]:
                    print(f"[REFINEMENT] Failed to parse {doc_filename}")
                    continue
                doc_text = parsed["text"]
                word_count = len(doc_text.split())

                # Apply chunking if text is long
                if len(doc_text) > 30000:
                    chunks = chunk_text(doc_text, max_chunk_size=4000, overlap=400)
                    doc_text = "\n\n---CHUNK---\n\n".join(
                        [f"[CHUNK {i+1}]\n{c}" for i, c in enumerate(chunks)]
                    )

            all_documents_info.append({
                "id": doc_id,
                "filename": doc_filename,
                "type": doc_type,
                "word_count": word_count
            })

            all_documents_content += f"\n\n{'='*80}\n"
            all_documents_content += f"DOCUMENT: {doc_filename} (type: {doc_type})\n"
            all_documents_content += f"{'='*80}\n\n"
            all_documents_content += doc_text

        print(f"[REFINEMENT] Total content extracted: {len(all_documents_content)} chars")

        # 3. Prepare context for agent with REFINEMENT mode
        refinement_context = f"""
CURRENT REQUIREMENTS DOCUMENT:
{current_requirements}

REFINEMENT INSTRUCTIONS FROM USER:
{refinement_instructions}

Please analyze the current requirements document and apply the requested refinements.
Maintain the structure and quality of the original document while incorporating the changes.
"""

        # 4. Call LLM DIRECTLY for refinement (simpler and faster)
        print(f"[REFINEMENT] Calling LLM directly for refinement...")

        from app.llm import get_llm_client

        refinement_prompt = f"""Você é um especialista em análise de requisitos de software.

DOCUMENTO ATUAL DE REQUISITOS:
{current_requirements}

INSTRUÇÕES DE REFINAMENTO DO USUÁRIO:
{refinement_instructions}

CONTEXTO ADICIONAL DOS DOCUMENTOS ORIGINAIS:
{all_documents_content[:10000]}

TAREFA:
Refine o documento de requisitos seguindo EXATAMENTE as instruções do usuário.
Mantenha a mesma estrutura e formato markdown do documento original.
Retorne APENAS o documento refinado completo em markdown, sem explicações adicionais.
"""

        llm_client = get_llm_client()
        refined_requirements = llm_client.complete(
            prompt=refinement_prompt,
            temperature=0.7,
            max_tokens=16000
        )

        print(f"[REFINEMENT] LLM completed. Refined document length: {len(refined_requirements)} chars")

        if not refined_requirements or len(refined_requirements) < 100:
            print(f"[REFINEMENT] ⚠️ WARNING: LLM returned empty or too short document!")
            print(f"[REFINEMENT] Response length: {len(refined_requirements)}")
            raise Exception("Refinement failed: LLM returned empty or invalid response")

        # 6. Update session with refined requirements
        with get_db_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                UPDATE execution_sessions
                SET requirements_document = %s,
                    status = 'completed',
                    finished_at = NOW()
                WHERE id = %s
            """, (refined_requirements, session_id))
            db.commit()
            cursor.close()

        print(f"[REFINEMENT] Updated session {session_id} with refined requirements")

        # 7. Update agent message with completion
        update_chat_message(
            message_id=agent_message_id,
            message_text=f"✅ Refinamento concluído! O documento foi atualizado com base em suas instruções.",
            metadata={'type': 'refinement_response', 'status': 'completed'}
        )

        # 8. Send completion notification with diff data
        save_chat_message(
            session_id=session_id,
            sender_type='system',
            message_text='✅ Documento refinado com sucesso. Veja as alterações destacadas.',
            message_type='info',
            sender_name='Sistema',
            metadata={
                'type': 'refinement_complete',
                'has_diff': True,
                'old_document': current_requirements,
                'new_document': refined_requirements
            }
        )

        print(f"[REFINEMENT] ✅ Workflow completed successfully")

    except Exception as e:
        print(f"[REFINEMENT] ❌ Error during refinement: {e}")
        import traceback
        traceback.print_exc()

        # Update session status to 'failed'
        try:
            with get_db_connection() as db:
                cursor = db.cursor()
                cursor.execute("""
                    UPDATE execution_sessions
                    SET status = 'failed'
                    WHERE id = %s
                """, (session_id,))
                db.commit()
                cursor.close()
        except:
            pass

        # Update agent message with error
        try:
            update_chat_message(
                message_id=agent_message_id,
                message_text=f"❌ Erro ao processar refinamento: {str(e)}",
                metadata={'type': 'refinement_response', 'status': 'error', 'error': str(e)}
            )
        except:
            pass


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
        # Get session data
        with get_db_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                SELECT requirements_document, project_id
                FROM execution_sessions
                WHERE id = %s
            """, (session_id,))
            session = cursor.fetchone()
            cursor.close()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        current_requirements = session.get('requirements_document', '')
        project_id = session.get('project_id')

        if not current_requirements:
            raise HTTPException(status_code=400, detail="No requirements document found in session")

        if not project_id:
            raise HTTPException(status_code=400, detail="Session has no associated project")

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

        # Save agent initial response
        agent_response = f"Entendi sua solicitação. Processando refinamento do documento..."
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

        # Execute refinement in background
        asyncio.create_task(execute_refinement_workflow(
            session_id=session_id,
            refinement_instructions=request.message,
            current_requirements=current_requirements,
            project_id=project_id,
            agent_message_id=agent_message_id
        ))

        return {
            "user_message_id": user_message_id,
            "agent_message": ChatMessageResponse(**agent_message),
            "status": "processing",
            "message": "Refinement request received. Processing with AI agent..."
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process refinement: {str(e)}")
