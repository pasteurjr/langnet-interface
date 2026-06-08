"""
Router: /api/code-generation
Gera, lê, atualiza e baixa o código Python multi-arquivo de um sistema agêntico
CrewAI compatível com o framework visualtasksexec, a partir dos artefatos
prévios (agents.yaml + tasks.yaml + petri_net em projects.project_data).
"""

import asyncio
import io
import json
import re
import uuid
import zipfile
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app import code_runner

from app.database import (
    create_code_generation_session,
    create_code_generation_version,
    get_code_generation_session,
    get_code_generation_version,
    get_code_generation_versions,
    get_code_generation_chat_messages,
    get_agents_yaml_session,
    get_tasks_yaml_session,
    get_task_execution_flow_session,
    get_project_data,
    list_code_generation_sessions,
    save_code_generation_chat_message,
    update_code_generation_session,
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/code-generation", tags=["code-generation"])


# ════════════════════════════════════════════════════════════
# REQUEST / RESPONSE MODELS
# ════════════════════════════════════════════════════════════

class GenerateCodeRequest(BaseModel):
    agents_yaml_session_id: str
    tasks_yaml_session_id: str
    task_execution_flow_session_id: Optional[str] = None
    # Recomendado: fornece o agent_task_spec para parser deterministic
    # extrair a coluna `| Tools |` e amarrar tools por agent/task.
    agent_task_spec_session_id: Optional[str] = None
    websocket_port: int = 5002
    session_name: Optional[str] = None


class UpdateFilesRequest(BaseModel):
    files: List[Dict[str, str]]
    change_description: Optional[str] = "Manual edit"


class RefineRequest(BaseModel):
    message: str


# ════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════

_FILES_KEY = "generated_files"


def _safe_path(path: str) -> str:
    """Slug-safe path inside the ZIP — no leading slashes or '..'."""
    return re.sub(r"\.{2,}", ".", (path or "").lstrip("/").replace("\\", "/"))


def _zip_files(files: List[Dict[str, str]]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            path = _safe_path(f.get("path", "unnamed.txt"))
            content = f.get("content", "")
            if isinstance(content, (dict, list)):
                content = json.dumps(content, ensure_ascii=False, indent=2)
            z.writestr(path, content)
    return buf.getvalue()


def _files_to_string_for_diff(files: List[Dict[str, str]]) -> str:
    """Concatena arquivos em um único bloco textual para que o LLM possa
    diff-refinar entendendo a árvore inteira em um único contexto."""
    out: List[str] = []
    for f in files:
        out.append(f"### FILE: {f.get('path')}\n```\n{f.get('content','')}\n```")
    return "\n\n".join(out)


def _parse_files_from_llm(text: str) -> List[Dict[str, str]]:
    """Extrai blocos `### FILE: <path>` seguidos de fenced code do output do LLM."""
    pattern = re.compile(
        r"###\s*FILE:\s*(?P<path>[^\n]+?)\s*\n```(?:\w+)?\n(?P<content>.*?)```",
        re.DOTALL,
    )
    out: List[Dict[str, str]] = []
    for m in pattern.finditer(text or ""):
        path = m.group("path").strip()
        content = m.group("content")
        out.append({"path": path, "content": content, "language": _guess_language(path)})
    return out


def _guess_language(path: str) -> str:
    if path.endswith(".py"):
        return "python"
    if path.endswith(".yaml") or path.endswith(".yml"):
        return "yaml"
    if path.endswith(".json"):
        return "json"
    if path.endswith(".md"):
        return "markdown"
    if path == "Dockerfile":
        return "dockerfile"
    return "text"


def _load_agents_and_tasks_yaml(req: GenerateCodeRequest):
    agents_session = get_agents_yaml_session(req.agents_yaml_session_id)
    if not agents_session:
        raise HTTPException(404, "agents.yaml session não encontrada")
    agents_yaml = agents_session.get("agents_yaml_content", "")
    if not agents_yaml:
        raise HTTPException(400, "agents.yaml vazio")

    tasks_session = get_tasks_yaml_session(req.tasks_yaml_session_id)
    if not tasks_session:
        raise HTTPException(404, "tasks.yaml session não encontrada")
    tasks_yaml = tasks_session.get("tasks_yaml_content", "")
    if not tasks_yaml:
        raise HTTPException(400, "tasks.yaml vazio")

    return agents_session, agents_yaml, tasks_yaml


# ════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════

@router.post("/{project_id}/generate")
async def generate_code(
    project_id: str,
    request: GenerateCodeRequest,
    current_user: dict = Depends(get_current_user),
):
    """Roda a task design_python_code (LLM) + adapter Python e persiste a árvore."""
    agents_session, agents_yaml, tasks_yaml = _load_agents_and_tasks_yaml(request)

    petri_net = get_project_data(project_id)
    if not petri_net or not petri_net.get("lugares"):
        raise HTTPException(
            400,
            "Rede de Petri não encontrada em projects.project_data — gere a Petri Net antes.",
        )

    # Lazy import to avoid heavy import on every request
    from agents.langnetagents import execute_task_with_context
    from agents.langnetstate import init_full_state

    state = init_full_state(
        project_id=project_id,
        document_id="code-generation",
        document_path="",
    )
    state["agents_yaml"] = agents_yaml
    state["tasks_yaml"] = tasks_yaml
    state["petri_net_data"] = petri_net
    state["websocket_port"] = int(request.websocket_port)
    state["project_name"] = state.get("project_name") or "Sistema Agêntico"
    state["use_deepseek"] = True

    # Carrega agent_task_spec_document (markdown) se foi informado — permite o
    # adapter Python parsear a coluna `| Tools |` e amarrar tools por task/agente.
    if request.agent_task_spec_session_id:
        from app.database import get_agent_task_spec_session
        ats_session = get_agent_task_spec_session(request.agent_task_spec_session_id)
        if ats_session and ats_session.get("agent_task_spec_document"):
            state["agent_task_spec_document"] = ats_session["agent_task_spec_document"]

    session_id = str(uuid.uuid4())
    session_name = request.session_name or f"code_gen_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    create_code_generation_session(
        {
            "id": session_id,
            "project_id": project_id,
            "user_id": current_user["id"],
            "agents_yaml_session_id": request.agents_yaml_session_id,
            "tasks_yaml_session_id": request.tasks_yaml_session_id,
            "task_execution_flow_session_id": request.task_execution_flow_session_id,
            "agent_task_spec_session_id": request.agent_task_spec_session_id,
            "websocket_port": request.websocket_port,
            "session_name": session_name,
            "status": "generating",
            "execution_metadata": {},
        }
    )

    try:
        result_state = execute_task_with_context("generate_python_code", state)
    except Exception as exc:  # noqa: BLE001
        update_code_generation_session(
            session_id,
            {"status": "failed", "generation_log": str(exc), "finished_at": datetime.utcnow()},
        )
        raise HTTPException(500, f"Falha ao gerar código: {exc}") from exc

    files = result_state.get("generated_files_list") or []
    if not files:
        update_code_generation_session(
            session_id,
            {"status": "failed", "generation_log": "Nenhum arquivo gerado", "finished_at": datetime.utcnow()},
        )
        raise HTTPException(502, "Gerador não retornou arquivos")

    warnings = result_state.get("validation_warnings") or []

    update_code_generation_session(
        session_id,
        {
            "status": "completed",
            "generated_files": files,
            "total_files": len(files),
            "current_version": 1,
            "finished_at": datetime.utcnow(),
            "execution_metadata": {"validation_warnings": warnings},
        },
    )
    create_code_generation_version(
        {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "version": 1,
            "generated_files": files,
            "created_by": current_user["id"],
            "change_type": "initial",
            "change_description": f"Geração inicial ({len(files)} arquivos)",
            "total_files": len(files),
        }
    )
    return {
        "session_id": session_id,
        "status": "completed",
        "files": files,
        "total_files": len(files),
        "websocket_port": request.websocket_port,
        "validation_warnings": warnings,
    }


@router.get("")
def list_sessions(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    sessions = list_code_generation_sessions(project_id)
    return {"sessions": sessions, "total": len(sessions)}


@router.get("/{session_id}")
def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    session = get_code_generation_session(session_id)
    if not session:
        raise HTTPException(404, "Sessão não encontrada")
    return session


@router.put("/{session_id}")
def update_files(
    session_id: str,
    request: UpdateFilesRequest,
    current_user: dict = Depends(get_current_user),
):
    """Persiste edição inline. Cria nova versão (change_type='manual_edit')."""
    session = get_code_generation_session(session_id)
    if not session:
        raise HTTPException(404, "Sessão não encontrada")
    new_version = int(session.get("current_version", 1)) + 1

    update_code_generation_session(
        session_id,
        {
            "generated_files": request.files,
            "total_files": len(request.files),
            "current_version": new_version,
        },
    )
    create_code_generation_version(
        {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "version": new_version,
            "generated_files": request.files,
            "created_by": current_user["id"],
            "change_type": "manual_edit",
            "change_description": request.change_description or "Manual edit",
            "total_files": len(request.files),
        }
    )
    return {"status": "ok", "version": new_version}


@router.post("/{session_id}/refine")
async def refine_files(
    session_id: str,
    request: RefineRequest,
    current_user: dict = Depends(get_current_user),
):
    """Refinamento via chat: LLM recebe a árvore + instrução e devolve nova árvore."""
    session = get_code_generation_session(session_id)
    if not session:
        raise HTTPException(404, "Sessão não encontrada")
    old_files = session.get("generated_files") or []
    if not old_files:
        raise HTTPException(400, "Sessão sem arquivos para refinar")

    # Persist user message
    save_code_generation_chat_message(
        {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "sender_type": "user",
            "message_text": request.message,
            "message_data": {},
            "message_type": "chat",
        }
    )

    from app.llm import get_llm_response_async

    files_block = _files_to_string_for_diff(old_files)
    prompt = f"""Você é um engenheiro Python sênior. Refine a árvore de arquivos de um projeto agêntico CrewAI orquestrado por Rede de Petri.

INSTRUÇÃO DO USUÁRIO:
{request.message}

ÁRVORE ATUAL:
{files_block}

REGRAS:
1. Retorne APENAS os arquivos que mudaram, no formato:
   ### FILE: <path>
   ```<lang>
   <content>
   ```
2. Não retorne arquivos inalterados.
3. Mantenha imports, indentação e PEP 8.
4. Não escape backslashes do código."""

    llm_text = await get_llm_response_async(prompt=prompt, max_tokens=8000)

    changed = _parse_files_from_llm(llm_text)
    if not changed:
        save_code_generation_chat_message(
            {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "sender_type": "assistant",
                "message_text": llm_text[:2000],
                "message_data": {"has_diff": False},
                "message_type": "chat",
            }
        )
        return {"has_diff": False, "message": llm_text}

    by_path = {f["path"]: f for f in old_files}
    affected_paths: List[str] = []
    for f in changed:
        by_path[f["path"]] = {
            **(by_path.get(f["path"]) or {}),
            **f,
        }
        affected_paths.append(f["path"])
    new_files = list(by_path.values())

    new_version = int(session.get("current_version", 1)) + 1

    # Re-validar a árvore atualizada para que o banner de warnings reflita
    # o estado atual depois do refinamento (fecha o loop SDD).
    # Carrega o agent_task_spec da sessão original (persistido no create)
    ats_md = ""
    ats_sid = session.get("agent_task_spec_session_id")
    if ats_sid:
        from app.database import get_agent_task_spec_session
        ats = get_agent_task_spec_session(ats_sid)
        if ats:
            ats_md = ats.get("agent_task_spec_document") or ""
    from agents.langnetagents import _validate_generated_project
    warnings = _validate_generated_project(new_files, {
        "agent_task_spec_document": ats_md,
    })

    update_code_generation_session(
        session_id,
        {
            "generated_files": new_files,
            "total_files": len(new_files),
            "current_version": new_version,
            "execution_metadata": {"validation_warnings": warnings},
        },
    )
    create_code_generation_version(
        {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "version": new_version,
            "generated_files": new_files,
            "created_by": current_user["id"],
            "change_type": "refine",
            "change_description": (request.message[:200] + "…") if len(request.message) > 200 else request.message,
            "total_files": len(new_files),
        }
    )

    save_code_generation_chat_message(
        {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "sender_type": "assistant",
            "message_text": f"Refinamento aplicado em {len(affected_paths)} arquivo(s).",
            "message_data": {
                "has_diff": True,
                "affected_paths": affected_paths,
                "new_version": new_version,
            },
            "message_type": "chat",
        }
    )

    return {
        "has_diff": True,
        "version": new_version,
        "affected_paths": affected_paths,
        "files": new_files,
        "validation_warnings": warnings,
    }


@router.get("/{session_id}/versions")
def list_versions(session_id: str, current_user: dict = Depends(get_current_user)):
    versions = get_code_generation_versions(session_id)
    return {"versions": versions, "total": len(versions)}


@router.get("/{session_id}/versions/{version}")
def get_version(session_id: str, version: int, current_user: dict = Depends(get_current_user)):
    row = get_code_generation_version(session_id, version)
    if not row:
        raise HTTPException(404, "Versão não encontrada")
    return row


@router.get("/{session_id}/chat-history")
def chat_history(session_id: str, current_user: dict = Depends(get_current_user)):
    msgs = get_code_generation_chat_messages(session_id)
    return {"messages": msgs}


# ════════════════════════════════════════════════════════════
# EXECUÇÃO LOCAL DO CÓDIGO GERADO (subprocess + venv)
# ════════════════════════════════════════════════════════════

@router.post("/{session_id}/run")
def start_run_endpoint(session_id: str, current_user: dict = Depends(get_current_user)):
    """Cria /tmp/langnet-runs/<session_id>/<run_id>/, instala deps em venv
    isolado e sobe `python main.py`. Retorna run_id imediatamente — o status
    e o stdout devem ser consumidos por GET /run/{run_id}/status ou
    WS /ws/code-generation/run/{run_id}."""
    session = get_code_generation_session(session_id)
    if not session:
        raise HTTPException(404, "Sessão não encontrada")
    files = session.get("generated_files") or []
    if not files:
        raise HTTPException(400, "Sessão sem arquivos")
    run = code_runner.start_run(session_id, files)
    return run.to_public()


@router.get("/run/{run_id}/status")
def run_status(run_id: str, current_user: dict = Depends(get_current_user)):
    run = code_runner.get_run(run_id)
    if not run:
        raise HTTPException(404, "Run não encontrado")
    return {**run.to_public(), "stdout_tail": run.stdout_lines[-300:]}


@router.post("/run/{run_id}/stop")
def run_stop(run_id: str, current_user: dict = Depends(get_current_user)):
    run = code_runner.stop_run(run_id)
    if not run:
        raise HTTPException(404, "Run não encontrado")
    return run.to_public()


@router.get("/{session_id}/runs")
def list_runs(session_id: str, current_user: dict = Depends(get_current_user)):
    runs = code_runner.list_runs_for_session(session_id)
    return {"runs": [r.to_public() for r in runs]}


@router.websocket("/run/{run_id}/ws")
async def run_ws(websocket: WebSocket, run_id: str, token: str = ""):
    """Stream em tempo real do stdout do run.
    Auth via query param ?token=... (não dá pra mandar header em WS browser)."""
    # Auth via query token
    try:
        from app.utils import decode_access_token
        payload = decode_access_token(token)
        if not payload:
            await websocket.close(code=1008)
            return
    except Exception:
        await websocket.close(code=1008)
        return

    run = code_runner.get_run(run_id)
    if not run:
        await websocket.close(code=1003)
        return

    await websocket.accept()
    # Envia status atual + tail recente
    await websocket.send_json({"type": "status", "data": run.to_public()})
    for line in run.stdout_lines[-500:]:
        await websocket.send_json({"type": "line", "data": line})

    q = code_runner.subscribe(run)
    try:
        while True:
            msg = await q.get()
            await websocket.send_json(msg)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        code_runner.unsubscribe(run, q)


@router.get("/{session_id}/download")
def download_zip(session_id: str, current_user: dict = Depends(get_current_user)):
    session = get_code_generation_session(session_id)
    if not session:
        raise HTTPException(404, "Sessão não encontrada")
    files = session.get("generated_files") or []
    if not files:
        raise HTTPException(400, "Sessão sem arquivos")
    zip_bytes = _zip_files(files)
    name = (session.get("session_name") or session_id).replace(" ", "_")
    warnings = (session.get("execution_metadata") or {}).get("validation_warnings") or []
    # Categorias únicas para o frontend decidir avisar
    categories: List[str] = []
    for w in warnings:
        cat = w.split(":", 1)[0].strip()
        if cat and cat not in categories:
            categories.append(cat)
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{name}.zip"',
            "X-Validation-Warnings-Count": str(len(warnings)),
            "X-Validation-Warnings-Categories": ",".join(categories),
            # Expor headers customizados via CORS para o browser poder lê-los
            "Access-Control-Expose-Headers": "X-Validation-Warnings-Count, X-Validation-Warnings-Categories, Content-Disposition",
        },
    )


@router.get("/{session_id}/download-check")
def download_check(session_id: str, current_user: dict = Depends(get_current_user)):
    """Endpoint leve para o frontend decidir se mostra confirm antes de baixar.
    Não retorna o ZIP, só metadados das warnings."""
    session = get_code_generation_session(session_id)
    if not session:
        raise HTTPException(404, "Sessão não encontrada")
    warnings = (session.get("execution_metadata") or {}).get("validation_warnings") or []
    categories: List[str] = []
    for w in warnings:
        cat = w.split(":", 1)[0].strip()
        if cat and cat not in categories:
            categories.append(cat)
    return {
        "warnings_count": len(warnings),
        "warnings_categories": categories,
        "warnings": warnings,
    }
