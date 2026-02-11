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
    get_specification_session, get_document
)
from app.routers.auth import get_current_user
from app.llm import get_llm_response_async
from prompts.generate_task_execution_flow import get_task_execution_flow_prompt

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

    # Criar sessão
    session_data = {
        "id": session_id,
        "project_id": specification_session["project_id"],
        "user_id": user_id,
        "specification_session_id": request.specification_session_id,
        "agent_task_spec_session_id": request.agent_task_spec_session_id,
        "tasks_yaml_session_id": request.tasks_yaml_session_id,
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
