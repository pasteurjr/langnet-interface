"""
LangNet FastAPI Router
REST API endpoints for multi-agent system execution
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import uuid

# Import LangNet components
from agents.langnetagents import (
    execute_full_pipeline,
    execute_document_analysis_workflow,
    execute_agent_design_workflow,
    execute_task_with_context,
    init_full_state
)
from agents.langnetstate import LangNetFullState
from app.dependencies import get_current_user
from app.database import get_db_connection


router = APIRouter(prefix="/api/langnet", tags=["langnet"])


# In-memory execution storage (replace with Redis in production)
EXECUTIONS = {}


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ExecuteFullPipelineRequest(BaseModel):
    """Request model for full pipeline execution"""
    project_id: str = Field(description="Project UUID")
    document_id: str = Field(description="Document UUID")
    document_path: str = Field(description="Path to uploaded document")
    framework_choice: str = Field(default="crewai", description="Target framework")


class ExecuteTaskRequest(BaseModel):
    """Request model for single task execution"""
    task_name: str = Field(description="Name of task to execute")
    context_state: Dict[str, Any] = Field(description="Current context state")


class DocumentAnalysisRequest(BaseModel):
    """Request model for document analysis workflow"""
    project_id: str = Field(description="Project UUID")
    document_id: str = Field(description="Document UUID")
    document_path: Optional[str] = Field(default=None, description="Path to uploaded document")
    additional_instructions: Optional[str] = Field(default="", description="Additional analysis instructions")
    enable_web_research: bool = Field(default=True, description="Enable web research for enrichment")


class AgentDesignRequest(BaseModel):
    """Request model for agent design workflow"""
    requirements_data: Dict[str, Any] = Field(description="Extracted requirements")
    specification_data: Dict[str, Any] = Field(description="Generated specification")


class ExecutionResponse(BaseModel):
    """Response model for execution requests"""
    execution_id: str
    status: str
    message: str
    started_at: str


class ExecutionStatusResponse(BaseModel):
    """Response model for execution status"""
    execution_id: str
    status: str
    current_task: Optional[str]
    current_phase: Optional[str]
    progress_percentage: float
    completed_tasks: int
    total_tasks: int
    errors: List[Dict[str, Any]]
    execution_log: List[Dict[str, Any]]
    started_at: str
    completed_at: Optional[str]


class ExecutionResultResponse(BaseModel):
    """Response model for execution results"""
    execution_id: str
    status: str
    result: Dict[str, Any]
    errors: List[Dict[str, Any]]


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/execute-full-pipeline", response_model=ExecutionResponse)
async def execute_full_pipeline_endpoint(
    request: ExecuteFullPipelineRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Execute the complete LangNet pipeline

    Workflow:
    1. Document Analysis → Requirements → Specification
    2. Agent Design → Task Decomposition
    3. Workflow Design (Petri Net)
    4. Code Generation (YAML + Python)

    Returns execution ID for status tracking
    """
    execution_id = str(uuid.uuid4())

    # Initialize execution tracking
    EXECUTIONS[execution_id] = {
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "state": None,
        "error": None
    }

    # Execute in background
    def run_pipeline():
        try:
            def verbose_callback(message: str):
                print(f"[{execution_id}] {message}")

            result = execute_full_pipeline(
                project_id=request.project_id,
                document_id=request.document_id,
                document_path=request.document_path,
                framework_choice=request.framework_choice,
                verbose_callback=verbose_callback
            )

            EXECUTIONS[execution_id]["status"] = "completed"
            EXECUTIONS[execution_id]["completed_at"] = datetime.now().isoformat()
            EXECUTIONS[execution_id]["state"] = result

        except Exception as e:
            EXECUTIONS[execution_id]["status"] = "failed"
            EXECUTIONS[execution_id]["error"] = str(e)
            EXECUTIONS[execution_id]["completed_at"] = datetime.now().isoformat()

    background_tasks.add_task(run_pipeline)

    return ExecutionResponse(
        execution_id=execution_id,
        status="running",
        message="Pipeline execution started",
        started_at=EXECUTIONS[execution_id]["started_at"]
    )


@router.get("/execution/{execution_id}/status", response_model=ExecutionStatusResponse)
async def get_execution_status(execution_id: str):
    """
    Get execution status and progress

    Returns current task, progress percentage, and execution log
    """
    if execution_id not in EXECUTIONS:
        raise HTTPException(status_code=404, detail="Execution not found")

    execution = EXECUTIONS[execution_id]
    state = execution.get("state") or {}

    return ExecutionStatusResponse(
        execution_id=execution_id,
        status=execution["status"],
        current_task=state.get("current_task"),
        current_phase=state.get("current_phase"),
        progress_percentage=state.get("progress_percentage", 0.0),
        completed_tasks=state.get("completed_tasks", 0),
        total_tasks=state.get("total_tasks", 9),
        errors=state.get("errors", []),
        execution_log=state.get("execution_log", []),
        started_at=execution["started_at"],
        completed_at=execution.get("completed_at")
    )


@router.get("/execution/{execution_id}/result", response_model=ExecutionResultResponse)
async def get_execution_result(
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get execution final result

    Returns complete state with all generated artifacts
    """
    if execution_id not in EXECUTIONS:
        raise HTTPException(status_code=404, detail="Execution not found")

    execution = EXECUTIONS[execution_id]

    if execution["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Execution not finished yet")

    return ExecutionResultResponse(
        execution_id=execution_id,
        status=execution["status"],
        result=execution.get("state", {}),
        errors=execution.get("state", {}).get("errors", [])
    )


@router.post("/analyze-document")
async def analyze_document_endpoint(
    request: DocumentAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Execute document analysis workflow only

    Steps: Parse → Extract Requirements → Validate → Generate Specification
    """
    execution_id = str(uuid.uuid4())

    EXECUTIONS[execution_id] = {
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "state": None,
        "error": None
    }

    def run_analysis():
        try:
            # Get document info from database to extract path
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM documents WHERE id = ?", (request.document_id,))
            row = cursor.fetchone()
            document_path = row[0] if row else request.document_path
            cursor.close()
            conn.close()

            result = execute_document_analysis_workflow(
                project_id=request.project_id,
                document_id=request.document_id,
                document_path=document_path,
                additional_instructions=request.additional_instructions or "",
                enable_web_research=request.enable_web_research
            )
            EXECUTIONS[execution_id]["status"] = "completed"
            EXECUTIONS[execution_id]["completed_at"] = datetime.now().isoformat()
            EXECUTIONS[execution_id]["state"] = result
        except Exception as e:
            EXECUTIONS[execution_id]["status"] = "failed"
            EXECUTIONS[execution_id]["error"] = str(e)
            EXECUTIONS[execution_id]["completed_at"] = datetime.now().isoformat()

    background_tasks.add_task(run_analysis)

    return ExecutionResponse(
        execution_id=execution_id,
        status="running",
        message="Document analysis started",
        started_at=EXECUTIONS[execution_id]["started_at"]
    )


@router.post("/design-agents")
async def design_agents_endpoint(
    request: AgentDesignRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Execute agent design workflow

    Steps: Suggest Agents → Decompose Tasks
    """
    execution_id = str(uuid.uuid4())

    EXECUTIONS[execution_id] = {
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "state": None,
        "error": None
    }

    def run_design():
        try:
            result = execute_agent_design_workflow(
                requirements_data=request.requirements_data,
                specification_data=request.specification_data
            )
            EXECUTIONS[execution_id]["status"] = "completed"
            EXECUTIONS[execution_id]["completed_at"] = datetime.now().isoformat()
            EXECUTIONS[execution_id]["state"] = result
        except Exception as e:
            EXECUTIONS[execution_id]["status"] = "failed"
            EXECUTIONS[execution_id]["error"] = str(e)
            EXECUTIONS[execution_id]["completed_at"] = datetime.now().isoformat()

    background_tasks.add_task(run_design)

    return ExecutionResponse(
        execution_id=execution_id,
        status="running",
        message="Agent design started",
        started_at=EXECUTIONS[execution_id]["started_at"]
    )


@router.post("/execute-task")
async def execute_task_endpoint(
    request: ExecuteTaskRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Execute a single task with provided context state

    Useful for resuming workflows or testing individual tasks
    """
    try:
        result_state = execute_task_with_context(
            task_name=request.task_name,
            context_state=request.context_state
        )

        return {
            "success": True,
            "task": request.task_name,
            "state": result_state
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/list")
async def list_available_tasks(current_user: dict = Depends(get_current_user)):
    """
    List all available tasks

    Returns task names, descriptions, and dependencies
    """
    from agents.langnetagents import TASK_REGISTRY, TASKS_CONFIG

    tasks = []
    for task_name, task_config in TASK_REGISTRY.items():
        tasks.append({
            "name": task_name,
            "description": TASKS_CONFIG[task_name]["description"],
            "expected_output": TASKS_CONFIG[task_name]["expected_output"],
            "phase": task_config["phase"],
            "requires": task_config["requires"],
            "produces": task_config["produces"]
        })

    return {"tasks": tasks}


@router.get("/agents/list")
async def list_available_agents(current_user: dict = Depends(get_current_user)):
    """
    List all available agents

    Returns agent names, roles, and goals
    """
    from agents.langnetagents import AGENTS_CONFIG

    agents = []
    for agent_name, agent_config in AGENTS_CONFIG.items():
        agents.append({
            "name": agent_name,
            "role": agent_config["role"],
            "goal": agent_config["goal"],
            "backstory": agent_config["backstory"][:200] + "...",
            "verbose": agent_config["verbose"],
            "allow_delegation": agent_config["allow_delegation"]
        })

    return {"agents": agents}


@router.delete("/execution/{execution_id}")
async def delete_execution(
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete execution data

    Clears execution from memory
    """
    if execution_id not in EXECUTIONS:
        raise HTTPException(status_code=404, detail="Execution not found")

    del EXECUTIONS[execution_id]

    return {"message": "Execution deleted successfully"}


@router.post("/save-results/{execution_id}")
async def save_execution_results(
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Save execution results to database

    Persists generated agents, tasks, YAML, code to respective tables
    """
    if execution_id not in EXECUTIONS:
        raise HTTPException(status_code=404, detail="Execution not found")

    execution = EXECUTIONS[execution_id]

    if execution["status"] != "completed":
        raise HTTPException(status_code=400, detail="Execution not completed")

    state = execution["state"]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Save agents
        agents_data = state.get("agents_data", [])
        for agent in agents_data:
            cursor.execute("""
                INSERT INTO agents (
                    id, project_id, agent_id, name, role, goal, backstory,
                    tools, verbose, allow_delegation, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                state["project_id"],
                agent.get("agent_id", agent["name"]),
                agent["name"],
                agent["role"],
                agent["goal"],
                agent["backstory"],
                json.dumps(agent.get("tools", [])),
                agent.get("verbose", True),
                agent.get("allow_delegation", False),
                "active"
            ))

        # Save tasks
        tasks_data = state.get("tasks_data", [])
        for task in tasks_data:
            cursor.execute("""
                INSERT INTO tasks (
                    id, project_id, task_id, name, description,
                    expected_output, tools, async_execution
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                state["project_id"],
                task.get("task_id", task["name"]),
                task["name"],
                task["description"],
                task.get("expected_output", ""),
                json.dumps(task.get("tools", [])),
                task.get("async_execution", False)
            ))

        # Save YAML files
        if state.get("agents_yaml"):
            cursor.execute("""
                INSERT INTO yaml_files (
                    id, project_id, file_type, filename, content, version
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                state["project_id"],
                "agents",
                "agents.yaml",
                state["agents_yaml"],
                "1.0"
            ))

        if state.get("tasks_yaml"):
            cursor.execute("""
                INSERT INTO yaml_files (
                    id, project_id, file_type, filename, content, version
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                state["project_id"],
                "tasks",
                "tasks.yaml",
                state["tasks_yaml"],
                "1.0"
            ))

        # Save generated code
        if state.get("generated_code"):
            cursor.execute("""
                INSERT INTO code_generations (
                    id, project_id, framework, code_content,
                    additional_files, requirements
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                state["project_id"],
                state.get("framework_choice", "crewai"),
                state["generated_code"],
                json.dumps(state.get("generated_files", {})),
                state.get("requirements_txt", "")
            ))

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "success": True,
            "message": "Results saved to database",
            "agents_saved": len(agents_data),
            "tasks_saved": len(tasks_data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save results: {str(e)}")


@router.get("/execution/{execution_id}/requirements-document")
async def get_requirements_document(execution_id: str):
    """
    Get the requirements document (Markdown) generated by the LangNet pipeline.

    This returns the requirements_document_md field from the final state,
    which is generated by the validate_requirements task using the template.
    """
    try:
        # Get execution from database
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            # Nota: a coluna real é finished_at (não completed_at), e final_marking (não final_state)
            cursor.execute(
                "SELECT execution_metadata, status, finished_at, requirements_document FROM execution_sessions WHERE id = %s",
                (execution_id,)
            )
            execution = cursor.fetchone()
            cursor.close()

        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        if execution['status'] != 'completed':
            raise HTTPException(
                status_code=400,
                detail=f"Execution not completed yet (status: {execution['status']})"
            )

        # Preferência: coluna dedicada `requirements_document`. Fallback: extrair
        # do execution_metadata (JSON) se ele tiver `requirements_document_md`.
        requirements_md = execution.get("requirements_document") or ""
        meta = {}
        if execution.get("execution_metadata"):
            try:
                meta = json.loads(execution["execution_metadata"]) or {}
            except Exception:
                meta = {}
            if not requirements_md:
                requirements_md = meta.get("requirements_document_md", "") or meta.get("requirements_document", "")

        if not requirements_md:
            raise HTTPException(
                status_code=404,
                detail="Requirements document not generated. This may happen if the validate_requirements task was not executed."
            )

        return {
            "execution_id": execution_id,
            "document": requirements_md,
            "generated_at": execution['finished_at'].isoformat() if execution.get('finished_at') else None,
            "project_id": meta.get("project_id"),
            "document_id": meta.get("document_id"),
            "project_name": meta.get("project_name")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve requirements document: {str(e)}"
        )


class RefineRequirementsRequest(BaseModel):
    message: str


@router.post("/execution/{execution_id}/requirements-document/refine")
async def refine_requirements_document(execution_id: str, req: RefineRequirementsRequest):
    """Refina o documento de requisitos com base em uma instrução do usuário.

    - Carrega o doc atual da execution_sessions
    - Envia pro LLM (respeita LLM_PROVIDER — DeepSeek cloud ou LM Studio local)
    - Persiste a nova versão em requirements_document
    - Retorna o documento novo + tempo de processamento
    """
    import time as _time
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT requirements_document FROM execution_sessions WHERE id=%s",
                (execution_id,),
            )
            row = cur.fetchone()
            cur.close()
        if not row or not row.get("requirements_document"):
            raise HTTPException(status_code=404, detail="Requirements document not found")

        current = row["requirements_document"]
        instruction = (req.message or "").strip()
        if not instruction:
            raise HTTPException(status_code=400, detail="Empty refinement message")

        # LLM (usa get_llm que respeita LLM_PROVIDER)
        try:
            from backend.agents.langnetagents import get_llm  # execução com PYTHONPATH normal
        except Exception:
            from agents.langnetagents import get_llm  # execução a partir de backend/

        llm = get_llm(use_deepseek=False)

        n_lines = len(current.splitlines())
        n_chars = len(current)
        prompt = f"""TAREFA: Copiar um documento Markdown inteiro, aplicando pequenas modificações.

VOCÊ ESTÁ PROIBIDO DE:
- Escrever "[...]", "[Restante do conteúdo original]", "[demais seções idênticas]",
  "[conteúdo mantido]", "[Resto omitido]", "[...continua]", "…", ou qualquer
  outra notação que represente conteúdo omitido.
- Resumir seções.
- Substituir tabelas por descrições curtas.
- Escrever meta-comentários tipo "aqui vai o mesmo conteúdo do original".

VOCÊ DEVE:
- Copiar CADA LINHA do documento original ({n_lines} linhas, {n_chars} chars),
  do início ao fim, alterando apenas o que a instrução pedir.
- Preservar TODAS as tabelas com todas as linhas.
- Preservar TODAS as seções (1 a 20), com todos os itens.
- Se por acaso você atingir seu limite de tokens antes de terminar, continue
  copiando LITERALMENTE em vez de abreviar.
- Atualizar a versão nos metadados (1.0 → 1.1) e registrar a mudança na seção
  "Controle de Versões".

Seu output será REJEITADO automaticamente se contiver qualquer marca de omissão.
O output esperado deve ter aproximadamente {n_chars} chars (podendo ficar um
pouco maior por causa das adições).

MODIFICAÇÕES A APLICAR:
{instruction}

DOCUMENTO ORIGINAL COMPLETO ({n_chars} chars, {n_lines} linhas):
=====BEGIN_ORIGINAL_DOC=====
{current}
=====END_ORIGINAL_DOC=====

Agora produza o documento COMPLETO, do primeiro ao último caractere, com as
modificações aplicadas. Comece com "# Documento de Requisitos" e não pare
até ter copiado todas as {n_lines} linhas (com adições aplicadas)."""

        t0 = _time.time()
        try:
            raw = llm.call([{"role": "user", "content": prompt}])
        except Exception:
            raw = llm.call(prompt)
        elapsed = _time.time() - t0

        # Extrai após </think> se presente (R1 e similares)
        import re as _re
        m = _re.search(r"</think>\s*(.*)", raw, _re.DOTALL)
        new_doc = m.group(1).strip() if m else raw.strip()
        # Remove fence markdown se veio dentro de bloco
        m = _re.match(r"^```(?:markdown|md)?\s*\n(.*)\n```\s*$", new_doc, _re.DOTALL | _re.IGNORECASE)
        if m:
            new_doc = m.group(1).strip()

        # Detecta placeholders de omissão que LLMs pequenos gostam de usar
        omission_patterns = [
            r"\.\.\.\s*\[Restante do conteúdo",
            r"\[conteúdo original mantido\]",
            r"\[Resto do documento",
            r"\[Restante omitido",
            r"\[demais seções idênticas",
        ]
        import re as _re
        detected_omissions = [p for p in omission_patterns if _re.search(p, new_doc)]

        if detected_omissions:
            # Rejeita — LLM comprimiu. Pede pra usuário tentar de novo (idealmente com modelo maior).
            raise HTTPException(
                status_code=422,
                detail=(
                    "LLM comprimiu o documento usando placeholders "
                    f"({', '.join(detected_omissions)[:200]}). O modelo local não conseguiu "
                    "reescrever o documento inteiro. Tente: (a) mudar pra deepseek cloud "
                    "(LLM_PROVIDER=deepseek); (b) fazer uma mudança menor por vez; ou "
                    "(c) usar modelo maior (R1 32B ou v4-pro)."
                ),
            )

        if len(new_doc) < 500:
            raise HTTPException(
                status_code=502,
                detail=f"LLM retornou resposta muito curta ({len(new_doc)} chars). Preview: {new_doc[:200]}",
            )

        # Ratio de compressão suspeito: se doc encolheu mais de 40%, provavelmente perdeu conteúdo
        if len(current) > 5000 and len(new_doc) < len(current) * 0.6:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"LLM devolveu documento muito menor ({len(new_doc)} vs original {len(current)} chars, "
                    f"redução de {100*(1-len(new_doc)/len(current)):.0f}%). "
                    "Provavelmente omitiu conteúdo. Tente pedido mais focado ou modelo maior."
                ),
            )

        # Persiste
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE execution_sessions SET requirements_document=%s WHERE id=%s",
                (new_doc, execution_id),
            )
            conn.commit()
            cur.close()

        return {
            "execution_id": execution_id,
            "document": new_doc,
            "elapsed_seconds": round(elapsed, 1),
            "document_size": len(new_doc),
            "previous_size": len(current),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refine failed: {str(e)}")
