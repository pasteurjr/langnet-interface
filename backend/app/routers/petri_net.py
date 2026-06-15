"""
API Router: Petri Net (geração via LLM, leitura e atualização)
Persiste em projects.project_data.
"""

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


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def _strip_md_fences(content: str) -> str:
    """Remove cercas ```yaml ... ``` que o LLM frequentemente coloca em volta.
    Mantém o conteúdo intacto se não houver fences."""
    if not content:
        return content
    import re as _re
    # Caso típico: linha inicial '```yaml' (ou apenas '```') e fechamento '```' no fim
    m = _re.search(r"^```(?:ya?ml|yaml)?\s*\n(.*?)\n?```\s*$", content.strip(), _re.DOTALL | _re.IGNORECASE)
    if m:
        return m.group(1)
    # Caso mais relaxado: só remove as primeiras/últimas linhas se forem cercas
    lines = content.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines)


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

    # Persistir em projects.project_data
    affected = update_project_data(project_id, petri_net)
    if affected == 0:
        raise HTTPException(status_code=404, detail="Projeto não encontrado para gravar a rede")

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
    return {"status": "ok"}
