"""
API Router: Task Execution Flow Generation
Gera task_execution_flow.md a partir de specification + agent_task_spec + tasks.yaml
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

from app.database import (
    create_task_execution_flow_session, get_task_execution_flow_session,
    update_task_execution_flow_session, list_task_execution_flow_sessions,
    get_agent_task_spec_session, get_tasks_yaml_session,
    get_specification_session, get_document, get_db_connection
)
from app.routers.auth import get_current_user
from app.llm import get_llm_response_async
from prompts.generate_task_execution_flow import (
    get_task_execution_flow_prompt,
    get_task_execution_flow_refine_prompt,
    get_task_execution_flow_review_prompt,
)

router = APIRouter(prefix="/task-execution-flow", tags=["task-execution-flow"])


# ═══════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════

class GenerateFlowRequest(BaseModel):
    specification_session_id: str
    agent_task_spec_session_id: str
    tasks_yaml_session_id: str
    uploaded_document_ids: Optional[List[str]] = None
    custom_instructions: Optional[str] = None


class UpdateFlowRequest(BaseModel):
    content: str


class RefineFlowRequest(BaseModel):
    message: str
    action_type: Optional[str] = "refine"


# ═══════════════════════════════════════════════════════════
# HELPERS: RASTREABILIDADE (versões das fontes consumidas)
# ═══════════════════════════════════════════════════════════

def _current_specification_version(spec_session_id: str) -> Optional[int]:
    """Versão CURRENT da Especificação Funcional-fonte.

    A fonte confiável é MAX(version) do histórico. Retorna None se
    indeterminável (nunca lança — rastreabilidade é aditiva/best-effort)."""
    if not spec_session_id:
        return None
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT MAX(version) AS v FROM specification_version_history "
                    "WHERE specification_session_id=%s",
                    (spec_session_id,),
                )
                r = cur.fetchone()
            finally:
                cur.close()
        return int(r["v"]) if r and r.get("v") is not None else None
    except Exception:
        return None


def _current_agent_task_spec_version(ats_session_id: str) -> Optional[int]:
    """Versão CURRENT da Especificação de Agentes/Tarefas-fonte.

    agent_task_specification_sessions não tem coluna version própria
    (specification_version guarda a versão da fonte anterior), então a
    fonte confiável é MAX(version) de agent_task_spec_version_history.
    Nunca lança."""
    if not ats_session_id:
        return None
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT MAX(version) AS v FROM agent_task_spec_version_history "
                    "WHERE session_id=%s",
                    (ats_session_id,),
                )
                r = cur.fetchone()
            finally:
                cur.close()
        return int(r["v"]) if r and r.get("v") is not None else None
    except Exception:
        return None


def _current_tasks_yaml_version(tasks_yaml_session_id: str) -> Optional[int]:
    """Versão CURRENT do tasks.yaml-fonte.

    tasks_yaml_sessions não tem coluna version própria
    (agent_task_spec_version guarda a versão da fonte anterior), então a
    fonte confiável é MAX(version) de tasks_yaml_version_history.
    Nunca lança."""
    if not tasks_yaml_session_id:
        return None
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT MAX(version) AS v FROM tasks_yaml_version_history "
                    "WHERE session_id=%s",
                    (tasks_yaml_session_id,),
                )
                r = cur.fetchone()
            finally:
                cur.close()
        return int(r["v"]) if r and r.get("v") is not None else None
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# HELPERS: VERSIONING + CHAT
# ═══════════════════════════════════════════════════════════

def _save_version(
    session_id: str,
    flow_document: str,
    change_type: str,
    change_description: str,
    user_id: Optional[str] = None,
    is_approved_version: int = 0
) -> int:
    """
    Salva uma nova versão do fluxo no histórico e atualiza o documento da sessão.

    - Calcula a próxima versão como MAX(version)+1 (não há coluna de versão na sessão).
    - Insere a linha no histórico com doc_size = len(flow_document).
    - Atualiza flow_document da sessão.

    Retorna o número da nova versão.
    """
    doc_size = len(flow_document or "")
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT COALESCE(MAX(version), 0) + 1 AS next_version
            FROM task_execution_flow_version_history
            WHERE session_id = %s
        """, (session_id,))
        row = cursor.fetchone()
        new_version = row['next_version'] if row and row.get('next_version') else 1

        cursor.execute("""
            INSERT INTO task_execution_flow_version_history
                (session_id, version, flow_document, created_at, created_by,
                 change_type, change_description, doc_size, is_approved_version)
            VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, %s)
        """, (
            session_id,
            new_version,
            flow_document,
            user_id,
            change_type,
            change_description[:500] if change_description else None,
            doc_size,
            is_approved_version,
        ))

        cursor.execute("""
            UPDATE task_execution_flow_sessions
            SET flow_document = %s, updated_at = NOW()
            WHERE id = %s
        """, (flow_document, session_id))

        conn.commit()
        cursor.close()

    return new_version


def _save_chat_message(
    session_id: str,
    sender_type: str,
    message_text: str,
    message_type: str = "chat",
    sender_name: Optional[str] = None,
    parent_message_id: Optional[str] = None,
    metadata: Optional[str] = None
) -> str:
    """Insere uma mensagem no chat da sessão e retorna o id gerado."""
    message_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO task_execution_flow_chat_messages
                (id, session_id, sender_type, sender_name, message_text,
                 message_type, timestamp, parent_message_id, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(3), %s, %s)
        """, (
            message_id,
            session_id,
            sender_type,
            sender_name,
            message_text,
            message_type,
            parent_message_id,
            metadata,
        ))
        conn.commit()
        cursor.close()
    return message_id


# ═══════════════════════════════════════════════════════════
# GERAÇÃO INICIAL
# ═══════════════════════════════════════════════════════════

@router.post("/")
async def generate_task_execution_flow(
    request: GenerateFlowRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Gera documento de fluxo de execução detalhado

    Input:
        - specification_session_id: ID da sessão de especificação funcional
        - agent_task_spec_session_id: ID da sessão de especificação de agentes/tarefas
        - tasks_yaml_session_id: ID da sessão de tasks.yaml
        - uploaded_document_ids: IDs de documentos externos opcionais
        - custom_instructions: Instruções customizadas (opcional)

    Output:
        - session_id: ID da nova sessão
        - status: 'generating'
    """
    user_id = current_user['id']
    session_id = str(uuid.uuid4())

    # Buscar especificação funcional
    specification_session = get_specification_session(request.specification_session_id)
    if not specification_session:
        raise HTTPException(status_code=404, detail="Especificação funcional não encontrada")

    specification_document = specification_session.get("specification_document", "")
    if not specification_document:
        raise HTTPException(status_code=400, detail="Documento de especificação funcional vazio")

    # Buscar especificação de agentes/tarefas
    agent_task_spec_session = get_agent_task_spec_session(request.agent_task_spec_session_id)
    if not agent_task_spec_session:
        raise HTTPException(status_code=404, detail="Especificação de agentes/tarefas não encontrada")

    agent_task_spec_document = agent_task_spec_session.get("agent_task_spec_document", "")
    if not agent_task_spec_document:
        raise HTTPException(status_code=400, detail="Documento de especificação de agentes/tarefas vazio")

    # Buscar tasks.yaml
    tasks_yaml_session = get_tasks_yaml_session(request.tasks_yaml_session_id)
    if not tasks_yaml_session:
        raise HTTPException(status_code=404, detail="Tasks YAML não encontrado")

    tasks_yaml_content = tasks_yaml_session.get("tasks_yaml_content", "")
    if not tasks_yaml_content:
        raise HTTPException(status_code=400, detail="Tasks YAML vazio")

    # Buscar documentos adicionais (opcional)
    additional_docs_text = ""
    if request.uploaded_document_ids:
        for doc_id in request.uploaded_document_ids:
            doc = get_document(doc_id)
            if doc and doc.get("extracted_text"):
                filename = doc.get("filename", "documento_sem_nome")
                additional_docs_text += f"\n\n### Documento Externo: {filename}\n{doc.get('extracted_text')[:5000]}"

    # Rastreabilidade (ETAPA 2): capturar a versão CURRENT de cada fonte consumida
    specification_version = _current_specification_version(request.specification_session_id)
    agent_task_spec_version = _current_agent_task_spec_version(request.agent_task_spec_session_id)
    tasks_yaml_version = _current_tasks_yaml_version(request.tasks_yaml_session_id)

    # Criar sessão
    session_data = {
        "id": session_id,
        "project_id": specification_session["project_id"],
        "user_id": user_id,
        "specification_session_id": request.specification_session_id,
        "agent_task_spec_session_id": request.agent_task_spec_session_id,
        "tasks_yaml_session_id": request.tasks_yaml_session_id,
        "specification_version": specification_version,
        "agent_task_spec_version": agent_task_spec_version,
        "tasks_yaml_version": tasks_yaml_version,
        "uploaded_document_ids": request.uploaded_document_ids or [],
        "session_name": f"task_flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "status": "generating",
        "execution_metadata": {}
    }

    create_task_execution_flow_session(session_data)

    # Background task
    background_tasks.add_task(
        execute_flow_generation,
        session_id,
        specification_document,
        agent_task_spec_document,
        tasks_yaml_content,
        additional_docs_text,
        request.custom_instructions,
        user_id
    )

    return {
        "session_id": session_id,
        "status": "generating",
        "message": "Geração de fluxo de execução iniciada"
    }


async def execute_flow_generation(
    session_id: str,
    specification_document: str,
    agent_task_spec_document: str,
    tasks_yaml: str,
    additional_docs_text: str,
    custom_instructions: Optional[str],
    user_id: str
):
    """
    Background task: Gera documento de fluxo via LLM
    """
    try:
        print(f"\n{'='*80}")
        print(f"[TASK_FLOW] Starting generation for session {session_id}")
        print(f"{'='*80}\n")

        # Construir prompt
        prompt = get_task_execution_flow_prompt(
            specification_document,
            agent_task_spec_document,
            tasks_yaml,
            additional_docs_text,
            custom_instructions or ""
        )

        print(f"[TASK_FLOW] Calling LLM...")
        start_time = datetime.now()

        # LLM call
        flow_document = await get_llm_response_async(
            prompt=prompt,
            system="Você é especialista em design de workflows e state management (LangGraph).",
            temperature=0.3,
            max_tokens=32000
        )

        end_time = datetime.now()
        generation_time_ms = int((end_time - start_time).total_seconds() * 1000)

        print(f"[TASK_FLOW] ✅ Generated {len(flow_document)} chars in {generation_time_ms}ms")

        # Contar tasks (seções "### Task")
        import re
        task_sections = re.findall(r'^### Task \d+:', flow_document, re.MULTILINE)
        total_tasks = len(task_sections)

        # Verificar se há paralelismo possível (análise simples)
        has_parallelism = "paralel" in flow_document.lower() or "parallel" in flow_document.lower()

        # Atualizar sessão
        update_task_execution_flow_session(session_id, {
            "status": "completed",
            "flow_document": flow_document,
            "total_tasks": total_tasks,
            "has_parallelism": has_parallelism,
            "generation_time_ms": generation_time_ms,
            "finished_at": datetime.now()
        })

        # Registrar versão 1 no histórico (geração inicial)
        try:
            _save_version(
                session_id=session_id,
                flow_document=flow_document,
                change_type="initial_generation",
                change_description="Geração inicial do fluxo de execução",
                user_id=user_id,
            )
            print(f"[TASK_FLOW] ✅ Version 1 recorded in history")
        except Exception as ve:
            print(f"[TASK_FLOW] ⚠️ Failed to record initial version: {ve}")

        print(f"[TASK_FLOW] ✅ Session completed: {total_tasks} tasks, parallelism={has_parallelism}")

    except Exception as e:
        print(f"[TASK_FLOW] ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

        update_task_execution_flow_session(session_id, {
            "status": "failed",
            "generation_log": str(e),
            "finished_at": datetime.now()
        })


# ═══════════════════════════════════════════════════════════
# GET SESSION
# ═══════════════════════════════════════════════════════════

@router.get("/{session_id}")
async def get_session(session_id: str):
    """
    Retorna dados da sessão (usado para polling)
    """
    session = get_task_execution_flow_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    return session


# ═══════════════════════════════════════════════════════════
# LIST SESSIONS
# ═══════════════════════════════════════════════════════════

@router.get("/")
async def list_sessions(project_id: str):
    """
    Lista todas as sessões de fluxo de execução de um projeto
    """
    sessions = list_task_execution_flow_sessions(project_id)
    return {
        "sessions": sessions,
        "total": len(sessions)
    }


# ═══════════════════════════════════════════════════════════
# VERSIONING
# ═══════════════════════════════════════════════════════════

@router.get("/{session_id}/versions")
async def list_versions(session_id: str):
    """Lista todas as versões de um fluxo de execução (mais recente primeiro)."""
    session = get_task_execution_flow_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT version, created_at, change_description, change_type, doc_size
            FROM task_execution_flow_version_history
            WHERE session_id = %s
            ORDER BY version DESC
        """, (session_id,))
        versions = cursor.fetchall()
        cursor.close()

    return {"versions": versions}


@router.get("/{session_id}/versions/{version}")
async def get_version(session_id: str, version: int):
    """Retorna o documento completo de uma versão específica."""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM task_execution_flow_version_history
            WHERE session_id = %s AND version = %s
        """, (session_id, version))
        version_data = cursor.fetchone()
        cursor.close()

    if not version_data:
        raise HTTPException(status_code=404, detail=f"Versão {version} não encontrada")

    return version_data


# ═══════════════════════════════════════════════════════════
# EDIÇÃO MANUAL (nova versão)
# ═══════════════════════════════════════════════════════════

@router.put("/{session_id}")
async def update_task_execution_flow(
    session_id: str,
    request: UpdateFlowRequest,
    current_user: dict = Depends(get_current_user)
):
    """Edição manual do documento → cria nova versão (manual_edit)."""
    session = get_task_execution_flow_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    new_version = _save_version(
        session_id=session_id,
        flow_document=request.content,
        change_type="manual_edit",
        change_description="Edição manual do documento",
        user_id=current_user['id'],
    )

    return {"message": "Fluxo de execução atualizado", "version": new_version}


# ═══════════════════════════════════════════════════════════
# REFINAMENTO (LLM → nova versão)
# ═══════════════════════════════════════════════════════════

@router.post("/{session_id}/refine")
async def refine_task_execution_flow(
    session_id: str,
    request: RefineFlowRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Refina o documento de fluxo via LLM aplicando a instrução do usuário.
    - action_type='refine' (padrão): modifica o documento e cria nova versão (ai_refinement)
    - action_type='chat': apenas responde/analisa sem modificar o documento
    Registra as mensagens (usuário + assistente) no chat da sessão.
    """
    session = get_task_execution_flow_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    current_document = session.get("flow_document", "")
    if not current_document:
        raise HTTPException(status_code=400, detail="Documento de fluxo vazio")

    user_id = current_user['id']
    action_type = request.action_type or "refine"

    # Registrar mensagem do usuário
    user_message_id = _save_chat_message(
        session_id=session_id,
        sender_type="user",
        message_text=request.message,
        message_type="chat",
        sender_name="Você",
    )

    try:
        if action_type == "chat":
            # Modo análise: não modifica o documento
            prompt = get_task_execution_flow_review_prompt(current_document)
            analysis = await get_llm_response_async(
                prompt=(
                    f"{prompt}\n\nPERGUNTA/INSTRUÇÃO DO USUÁRIO:\n{request.message}\n"
                    "Responda de forma direta à instrução do usuário sobre o documento acima."
                ),
                system="Você é especialista em design de workflows e state management (LangGraph).",
                temperature=0.3,
                max_tokens=8000,
            )

            assistant_message_id = _save_chat_message(
                session_id=session_id,
                sender_type="assistant",
                message_text=analysis,
                message_type="chat",
                sender_name="Agente Fluxo de Execução",
                parent_message_id=user_message_id,
            )

            return {
                "user_message_id": user_message_id,
                "assistant_message_id": assistant_message_id,
                "action_type": action_type,
                "status": "completed",
                "message": analysis,
            }

        # Modo refinamento: modifica o documento
        prompt = get_task_execution_flow_refine_prompt(current_document, request.message)
        refined_document = await get_llm_response_async(
            prompt=prompt,
            system="Você é especialista em design de workflows e state management (LangGraph).",
            temperature=0.3,
            max_tokens=32000,
        )

        # Recontar tasks e paralelismo
        import re
        task_sections = re.findall(r'^### Task \d+:', refined_document, re.MULTILINE)
        total_tasks = len(task_sections)
        has_parallelism = "paralel" in refined_document.lower() or "parallel" in refined_document.lower()

        new_version = _save_version(
            session_id=session_id,
            flow_document=refined_document,
            change_type="ai_refinement",
            change_description=request.message[:500],
            user_id=user_id,
        )

        update_task_execution_flow_session(session_id, {
            "total_tasks": total_tasks,
            "has_parallelism": has_parallelism,
        })

        assistant_message_id = _save_chat_message(
            session_id=session_id,
            sender_type="assistant",
            message_text=f"✅ Fluxo refinado com sucesso (versão {new_version}).",
            message_type="chat",
            sender_name="Agente Fluxo de Execução",
            parent_message_id=user_message_id,
        )

        return {
            "user_message_id": user_message_id,
            "assistant_message_id": assistant_message_id,
            "action_type": action_type,
            "status": "completed",
            "version": new_version,
            "flow_document": refined_document,
            "message": f"Fluxo refinado (v{new_version})",
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        _save_chat_message(
            session_id=session_id,
            sender_type="system",
            message_text=f"❌ Erro ao processar: {str(e)}",
            message_type="error",
            parent_message_id=user_message_id,
        )
        raise HTTPException(status_code=500, detail=f"Falha ao refinar fluxo: {str(e)}")


# ═══════════════════════════════════════════════════════════
# REVISÃO (LLM → sugestões, NÃO modifica)
# ═══════════════════════════════════════════════════════════

@router.post("/{session_id}/review")
async def review_task_execution_flow(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Revisão automática do fluxo — gera sugestões de melhoria.
    NÃO modifica o documento nem cria nova versão.
    """
    session = get_task_execution_flow_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    current_document = session.get("flow_document", "")
    if not current_document:
        raise HTTPException(status_code=400, detail="Documento de fluxo vazio")

    try:
        prompt = get_task_execution_flow_review_prompt(current_document)
        suggestions = await get_llm_response_async(
            prompt=prompt,
            system="Você é especialista em design de workflows e state management (LangGraph).",
            temperature=0.3,
            max_tokens=8000,
        )

        review_message_id = _save_chat_message(
            session_id=session_id,
            sender_type="assistant",
            message_text=suggestions,
            message_type="info",
            sender_name="Agente Fluxo de Execução",
            metadata='{"type": "review"}',
        )

        return {"suggestions": suggestions, "review_message_id": review_message_id}

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Falha ao revisar fluxo: {str(e)}")


# ═══════════════════════════════════════════════════════════
# HISTÓRICO DE CHAT
# ═══════════════════════════════════════════════════════════

@router.get("/{session_id}/chat-history")
async def get_chat_history(session_id: str):
    """Retorna as mensagens de chat da sessão."""
    session = get_task_execution_flow_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, session_id, sender_type, sender_name, message_text,
                   message_type, timestamp, parent_message_id, metadata
            FROM task_execution_flow_chat_messages
            WHERE session_id = %s
            ORDER BY timestamp ASC
            LIMIT 200
        """, (session_id,))
        messages = cursor.fetchall()
        cursor.close()

    return {"messages": messages, "total": len(messages)}


# ═══════════════════════════════════════════════════════════
# APROVAÇÃO
# ═══════════════════════════════════════════════════════════

@router.post("/{session_id}/approve")
async def approve_task_execution_flow(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Marca a versão atual (mais recente) como aprovada."""
    session = get_task_execution_flow_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    user_id = current_user['id']

    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT COALESCE(MAX(version), 0) AS current_version
            FROM task_execution_flow_version_history
            WHERE session_id = %s
        """, (session_id,))
        row = cursor.fetchone()
        current_version = row['current_version'] if row else 0

        if not current_version:
            cursor.close()
            raise HTTPException(status_code=400, detail="Nenhuma versão para aprovar")

        cursor.execute("""
            UPDATE task_execution_flow_version_history
            SET is_approved_version = 1, reviewed_by = %s, reviewed_at = NOW()
            WHERE session_id = %s AND version = %s
        """, (user_id, session_id, current_version))

        conn.commit()
        cursor.close()

    return {"message": "Fluxo de execução aprovado", "version": current_version, "status": "approved"}
