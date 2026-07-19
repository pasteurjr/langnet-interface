"""
API Router: Petri Net (geração via LLM, leitura e atualização)
Persiste em projects.project_data.
"""

import json
import yaml
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.database import (
    get_project_data,
    update_project_data,
    get_agents_yaml_session,
    get_tasks_yaml_session,
    get_task_execution_flow_session,
    get_db_connection,
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/petri-net", tags=["petri-net"])


# ═══════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════

class GeneratePetriNetRequest(BaseModel):
    agents_yaml_session_id: str
    tasks_yaml_session_id: str
    task_execution_flow_session_id: Optional[str] = None


class UpdatePetriNetRequest(BaseModel):
    petri_net: dict


class ApprovePetriNetRequest(BaseModel):
    version: Optional[int] = None


# ═══════════════════════════════════════════════════════════
# VERSION HISTORY (camada ADITIVA — não altera project_data)
# ═══════════════════════════════════════════════════════════

def _save_petri_version(
    project_id: str,
    petri_net: dict,
    change_type: str,
    change_description: str,
    user_id: Optional[str],
) -> Optional[int]:
    """Registra um snapshot da Rede de Petri em petri_net_version_history.

    Camada aditiva: NUNCA levanta exceção (envolve o INSERT em try/except) para que
    uma falha de versionamento jamais quebre generate/save. Retorna a nova versão ou None.
    """
    try:
        petri_json = json.dumps(petri_net, ensure_ascii=False)
        doc_size = len(petri_json)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(MAX(version), 0) + 1 FROM petri_net_version_history "
                "WHERE project_id = %s",
                (project_id,),
            )
            new_version = int(cursor.fetchone()[0])
            cursor.execute(
                "INSERT INTO petri_net_version_history "
                "(project_id, version, petri_net_json, created_by, change_type, "
                " change_description, doc_size) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    project_id,
                    new_version,
                    petri_json,
                    user_id,
                    change_type,
                    change_description,
                    doc_size,
                ),
            )
            conn.commit()
            cursor.close()
        return new_version
    except Exception as exc:  # noqa: BLE001 — versionamento nunca quebra o fluxo principal
        print(f"⚠️  Falha ao salvar versão da Rede de Petri (ignorada): {exc}")
        return None


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def _strip_md_fences(content: str) -> str:
    """Remove cercas ```yaml ... ``` que o LLM frequentemente coloca em volta.
    Mantém o conteúdo intacto se não houver fences.

    Lida com casos onde o LLM coloca um prefixo (ex: 'tasks.yaml:') antes da fence.
    """
    if not content:
        return content
    import re as _re
    # Extrai o primeiro bloco entre cercas em qualquer parte do texto
    m = _re.search(r"```(?:ya?ml|yaml)?\s*\n(.*?)\n```", content, _re.DOTALL | _re.IGNORECASE)
    if m:
        return m.group(1)
    # Fallback: remove apenas linhas que sejam cercas (filtra ```... e ```)
    lines = content.strip().splitlines()
    cleaned = [ln for ln in lines if not ln.strip().startswith("```")]
    return "\n".join(cleaned)


def _parse_agents_yaml(content: str) -> list:
    """Parse agents.yaml content into a list of agent dicts with id/name/role/goal/backstory."""
    if not content:
        return []
    content = _strip_md_fences(content)
    try:
        parsed = yaml.safe_load(content) or {}
    except yaml.YAMLError:
        return []
    if not isinstance(parsed, dict):
        return []
    return [
        {
            "id": key,
            "name": (val.get("role") if isinstance(val, dict) else key) or key,
            "role": (val.get("role") if isinstance(val, dict) else "") or "",
            "goal": (val.get("goal") if isinstance(val, dict) else "") or "",
            "backstory": (val.get("backstory") if isinstance(val, dict) else "") or "",
        }
        for key, val in parsed.items()
    ]


def _parse_tasks_yaml(content: str) -> list:
    """Parse tasks.yaml content into a list of task dicts with id/description/expected_output/agent."""
    if not content:
        return []
    content = _strip_md_fences(content)
    try:
        parsed = yaml.safe_load(content) or {}
    except yaml.YAMLError:
        return []
    if not isinstance(parsed, dict):
        return []
    return [
        {
            "id": key,
            "description": (val.get("description") if isinstance(val, dict) else "") or "",
            "expected_output": (val.get("expected_output") if isinstance(val, dict) else "") or "",
            "agent": (val.get("agent") if isinstance(val, dict) else "") or "",
        }
        for key, val in parsed.items()
    ]


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/{project_id}/generate")
async def generate_petri_net(
    project_id: str,
    request: GeneratePetriNetRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Gera a Rede de Petri via task design_petri_net (LLM) e persiste em projects.project_data.

    Carrega agents.yaml + tasks.yaml + task_execution_flow (opcional), parseia para listas,
    monta o state e executa apenas a task design_petri_net via execute_task_with_context.
    """
    # Carregar sessões
    agents_session = get_agents_yaml_session(request.agents_yaml_session_id)
    if not agents_session:
        raise HTTPException(status_code=404, detail="agents.yaml session não encontrada")
    agents_yaml = agents_session.get("agents_yaml_content", "")
    if not agents_yaml:
        raise HTTPException(status_code=400, detail="agents.yaml vazio")

    tasks_session = get_tasks_yaml_session(request.tasks_yaml_session_id)
    if not tasks_session:
        raise HTTPException(status_code=404, detail="tasks.yaml session não encontrada")
    tasks_yaml_content = tasks_session.get("tasks_yaml_content", "")
    if not tasks_yaml_content:
        raise HTTPException(status_code=400, detail="tasks.yaml vazio")

    flow_document = ""
    if request.task_execution_flow_session_id:
        flow_session = get_task_execution_flow_session(request.task_execution_flow_session_id)
        if flow_session:
            flow_document = flow_session.get("flow_document", "") or ""

    # Parsear YAMLs em listas estruturadas
    agents_list = _parse_agents_yaml(agents_yaml)
    tasks_list = _parse_tasks_yaml(tasks_yaml_content)

    if not agents_list:
        raise HTTPException(status_code=400, detail="Nenhum agente encontrado em agents.yaml")
    if not tasks_list:
        raise HTTPException(status_code=400, detail="Nenhuma task encontrada em tasks.yaml")

    # Importar agente runner (lazy para evitar custos de import em GET/PUT)
    from agents.langnetagents import execute_task_with_context
    from agents.langnetstate import init_full_state

    # Montar state inicial com os campos consumidos por design_petri_net_input_func
    state = init_full_state(
        project_id=project_id,
        document_id="petri-net-generation",
        document_path="",
    )
    state["agents_data"] = agents_list
    state["tasks_data"] = tasks_list
    state["dependencies"] = {"flow_document_md": flow_document} if flow_document else {}
    state["use_deepseek"] = True

    try:
        result_state = execute_task_with_context("design_petri_net", state)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao executar design_petri_net: {exc}",
        ) from exc

    petri_net = result_state.get("petri_net_data") or {}
    if not petri_net.get("lugares"):
        raise HTTPException(
            status_code=502,
            detail="LLM não retornou rede de Petri válida (lugares vazio)",
        )

    # Substitui placeholder em place.logica pelo JS real (WebSocket call)
    # — mesmo padrão usado quando empacotamos o ZIP de código.
    from agents.langnetagents import _build_petri_net_with_real_logica
    ws_port = int(state.get("websocket_port") or 5002)
    # known_task_names: extrai do tasks.yaml para validar place.task_name e
    # transformar places "intermediários" disfarçados (ex: P_T003_in "join")
    # em propagadores sem chamada WS.
    known_task_names = [t.get("id") for t in tasks_list if isinstance(t, dict) and t.get("id")]
    petri_net = _build_petri_net_with_real_logica(petri_net, ws_port, known_task_names)

    # Persistir em projects.project_data
    affected = update_project_data(project_id, petri_net)
    if affected == 0:
        raise HTTPException(status_code=404, detail="Projeto não encontrado para gravar a rede")

    # ADITIVO: registrar snapshot no histórico (não bloqueia se falhar)
    _save_petri_version(
        project_id,
        petri_net,
        "initial_generation",
        "Geração da rede via agente",
        current_user["id"],
    )

    return {"petri_net": petri_net}


@router.get("/{project_id}")
def get_petri_net(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Retorna a Rede de Petri armazenada em projects.project_data, ou null se não houver."""
    data = get_project_data(project_id)
    return {"petri_net": data}


@router.put("/{project_id}")
def update_petri_net(
    project_id: str,
    request: UpdatePetriNetRequest,
    current_user: dict = Depends(get_current_user),
):
    """Substitui a Rede de Petri em projects.project_data com o payload enviado pelo editor."""
    if not isinstance(request.petri_net, dict):
        raise HTTPException(status_code=400, detail="petri_net deve ser um objeto JSON")
    affected = update_project_data(project_id, request.petri_net)
    if affected == 0:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    # ADITIVO: registrar snapshot no histórico (não bloqueia se falhar)
    _save_petri_version(
        project_id,
        request.petri_net,
        "manual_edit",
        "Edição manual no editor",
        current_user["id"],
    )

    return {"status": "ok"}


# ═══════════════════════════════════════════════════════════
# ENDPOINTS — VERSION HISTORY (aditivo)
# ═══════════════════════════════════════════════════════════

@router.get("/{project_id}/versions")
def list_petri_versions(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Lista as versões (snapshots) da Rede de Petri para o projeto, mais recentes primeiro."""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT version, created_at, change_description, change_type, doc_size, "
            "       is_approved_version "
            "FROM petri_net_version_history WHERE project_id = %s "
            "ORDER BY version DESC",
            (project_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
    versions = [
        {
            "version": r["version"],
            "created_at": r["created_at"].isoformat() if r.get("created_at") else None,
            "change_description": r["change_description"],
            "change_type": r["change_type"],
            "doc_size": r["doc_size"],
            "is_approved_version": bool(r["is_approved_version"]),
        }
        for r in rows
    ]
    return {"versions": versions}


@router.get("/{project_id}/versions/{version}")
def get_petri_version(
    project_id: str,
    version: int,
    current_user: dict = Depends(get_current_user),
):
    """Retorna o snapshot completo de uma versão específica (petri_net parseado)."""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT version, petri_net_json, change_type, change_description, created_at, "
            "       is_approved_version "
            "FROM petri_net_version_history WHERE project_id = %s AND version = %s LIMIT 1",
            (project_id, version),
        )
        row = cursor.fetchone()
        cursor.close()
    if not row:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    try:
        petri_net = json.loads(row["petri_net_json"])
    except (json.JSONDecodeError, TypeError):
        petri_net = None
    return {
        "project_id": project_id,
        "version": row["version"],
        "change_type": row["change_type"],
        "change_description": row["change_description"],
        "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
        "is_approved_version": bool(row["is_approved_version"]),
        "petri_net": petri_net,
    }


@router.post("/{project_id}/restore/{version}")
def restore_petri_version(
    project_id: str,
    version: int,
    current_user: dict = Depends(get_current_user),
):
    """Restaura uma versão passada para a rede viva (project_data) e registra novo snapshot."""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT petri_net_json FROM petri_net_version_history "
            "WHERE project_id = %s AND version = %s LIMIT 1",
            (project_id, version),
        )
        row = cursor.fetchone()
        cursor.close()
    if not row:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    try:
        petri_net = json.loads(row["petri_net_json"])
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=500, detail="Snapshot da versão está corrompido")

    affected = update_project_data(project_id, petri_net)
    if affected == 0:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    _save_petri_version(
        project_id,
        petri_net,
        "manual_edit",
        f"Restaurada versão {version}",
        current_user["id"],
    )

    return {"petri_net": petri_net}


@router.post("/{project_id}/approve")
def approve_petri_version(
    project_id: str,
    request: Optional[ApprovePetriNetRequest] = None,
    current_user: dict = Depends(get_current_user),
):
    """Marca uma versão (ou a mais recente) como aprovada."""
    target_version = request.version if request else None
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if target_version is None:
            cursor.execute(
                "SELECT MAX(version) FROM petri_net_version_history WHERE project_id = %s",
                (project_id,),
            )
            result = cursor.fetchone()
            target_version = result[0] if result else None
        if target_version is None:
            cursor.close()
            raise HTTPException(status_code=404, detail="Nenhuma versão encontrada para aprovar")
        cursor.execute(
            "UPDATE petri_net_version_history SET is_approved_version = 1 "
            "WHERE project_id = %s AND version = %s",
            (project_id, target_version),
        )
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    return {"status": "approved", "version": int(target_version)}
