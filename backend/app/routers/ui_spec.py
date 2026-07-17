"""
UI Spec Router
Nova etapa do pipeline LangNet, entre Data Model e Agent-Task Spec: gera a
especificação de interface (telas + componentes ligados ao schema + ações) e
mockups HTML→PNG a partir da Especificação Funcional + Data Model.

Espelha o padrão de routers/data_model.py.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid
import json
from datetime import datetime

from app.database import get_db_connection
from app.dependencies import get_current_user
from agents.langnetui import execute_ui_spec_workflow, refine_ui_spec


router = APIRouter(prefix="/api/ui-spec", tags=["ui-spec"])


# ─────────────────── Schemas ───────────────────

class GenerateRequest(BaseModel):
    specification_session_id: str = Field(..., description="Session ID da specification a consumir")
    data_model_session_id: Optional[str] = Field(None, description="Session ID do Data Model (schema). Se ausente, usa o mais recente do projeto.")
    render_png: bool = Field(True, description="Renderizar mockups HTML→PNG")


class ChatMessageRequest(BaseModel):
    content: str
    screen_id: Optional[str] = None


class ApprovalRequest(BaseModel):
    approve: bool = True


# ─────────────────── Helpers ───────────────────

def _fetch_spec_content(spec_session_id: str) -> tuple[str, str]:
    """Retorna (specification_document, project_id)."""
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT specification_document, project_id FROM execution_specification_sessions WHERE id=%s",
                (spec_session_id,),
            )
            row = cur.fetchone()
        finally:
            cur.close()
    if not row or not row.get("specification_document"):
        raise HTTPException(404, "Especificação não encontrada ou vazia")
    return row["specification_document"], row["project_id"]


def _fetch_schema_sql(project_id: str, data_model_session_id: Optional[str]) -> str:
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            if data_model_session_id:
                cur.execute("SELECT schema_sql FROM data_model_sessions WHERE id=%s", (data_model_session_id,))
            else:
                cur.execute(
                    """SELECT schema_sql FROM data_model_sessions
                       WHERE project_id=%s AND schema_sql IS NOT NULL AND CHAR_LENGTH(schema_sql)>0
                       ORDER BY created_at DESC LIMIT 1""",
                    (project_id,),
                )
            row = cur.fetchone()
        finally:
            cur.close()
    return (row or {}).get("schema_sql") or ""


def _fetch_session(session_id: str) -> Dict[str, Any]:
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM ui_spec_sessions WHERE id=%s", (session_id,))
            row = cur.fetchone()
        finally:
            cur.close()
    if not row:
        raise HTTPException(404, "Sessão de UI Spec não encontrada")
    return row


def _serialize(row: Dict[str, Any], include_mockups: bool = True) -> Dict[str, Any]:
    ui_spec = json.loads(row["ui_spec_json"]) if row.get("ui_spec_json") else {}
    out = {
        "session_id": row["id"],
        "project_id": row["project_id"],
        "status": row["status"],
        "version": row["version"],
        "screens_count": row["screens_count"],
        "ui_spec": ui_spec,
        "generation_log": row.get("generation_log"),
        "created_at": str(row.get("created_at")),
        "updated_at": str(row.get("updated_at")),
    }
    if include_mockups:
        out["mockups"] = json.loads(row["mockups_json"]) if row.get("mockups_json") else {}
    return out


# ─────────────────── Endpoints ───────────────────

@router.post("/{project_id}/generate")
def generate_ui_spec(project_id: str, req: GenerateRequest, current_user=Depends(get_current_user)):
    """Gera a UI Spec completa (todas as telas + mockups PNG)."""
    spec_doc, spec_project = _fetch_spec_content(req.specification_session_id)
    schema_sql = _fetch_schema_sql(project_id, req.data_model_session_id)

    try:
        result = execute_ui_spec_workflow(
            specification_document=spec_doc,
            schema_sql=schema_sql,
            render_png=req.render_png,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha na geração: {e}")

    session_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO ui_spec_sessions
                   (id, project_id, user_id, specification_session_id, data_model_session_id,
                    version, status, ui_spec_json, mockups_json, screens_count, generation_log)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    session_id, project_id, current_user["id"],
                    req.specification_session_id, req.data_model_session_id,
                    1, "draft",
                    json.dumps(result["ui_spec"], ensure_ascii=False),
                    json.dumps(result["mockups"], ensure_ascii=False),
                    result["screens_count"],
                    result["generation_log"],
                ),
            )
            conn.commit()
        finally:
            cur.close()

    return {
        "session_id": session_id,
        "status": "draft",
        "screens_count": result["screens_count"],
        "ui_spec": result["ui_spec"],
        "generation_log": result["generation_log"],
    }


@router.get("/project/{project_id}/latest")
def get_latest_for_project(project_id: str, current_user=Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT * FROM ui_spec_sessions WHERE project_id=%s ORDER BY created_at DESC LIMIT 1",
                (project_id,),
            )
            row = cur.fetchone()
        finally:
            cur.close()
    if not row:
        return {"session_id": None, "message": "Nenhuma UI Spec gerada ainda"}
    return _serialize(row)


@router.get("/{session_id}")
def get_session(session_id: str, current_user=Depends(get_current_user)):
    return _serialize(_fetch_session(session_id))


@router.get("/{session_id}/mockups")
def get_mockups(session_id: str, current_user=Depends(get_current_user)):
    """Só os mockups PNG (payload pesado, separado do GET principal se preciso)."""
    row = _fetch_session(session_id)
    return {"mockups": json.loads(row["mockups_json"]) if row.get("mockups_json") else {}}


@router.post("/{session_id}/chat")
def chat_refine(session_id: str, req: ChatMessageRequest, current_user=Depends(get_current_user)):
    """Refina a UI Spec via chat (LLM re-gera o JSON)."""
    row = _fetch_session(session_id)
    current_json = row.get("ui_spec_json") or "{}"
    try:
        result = refine_ui_spec(current_json, req.content, screen_id=req.screen_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha no refino: {e}")

    new_spec = result["ui_spec"]
    mockup_update = result.get("mockup_update") or {}
    refined = result.get("refined_screen")

    # Mescla o PNG atualizado no mockups_json existente
    existing_mockups = json.loads(row["mockups_json"]) if row.get("mockups_json") else {}
    existing_mockups.update(mockup_update)

    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """UPDATE ui_spec_sessions SET ui_spec_json=%s, mockups_json=%s,
                   screens_count=%s, version=version+1 WHERE id=%s""",
                (json.dumps(new_spec, ensure_ascii=False),
                 json.dumps(existing_mockups, ensure_ascii=False),
                 len(new_spec.get("screens", [])), session_id),
            )
            cur.execute(
                "INSERT INTO ui_spec_chat_messages (id, ui_spec_session_id, role, content) VALUES (%s,%s,%s,%s)",
                (str(uuid.uuid4()), session_id, "user", req.content),
            )
            cur.execute(
                "INSERT INTO ui_spec_chat_messages (id, ui_spec_session_id, role, content) VALUES (%s,%s,%s,%s)",
                (str(uuid.uuid4()), session_id, "assistant", f"Tela '{refined}' atualizada."),
            )
            conn.commit()
        finally:
            cur.close()
    return {"status": "ok", "refined_screen": refined, "ui_spec": new_spec,
            "mockup_update": mockup_update}


@router.get("/{session_id}/chat")
def get_chat(session_id: str, current_user=Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT role, content, created_at FROM ui_spec_chat_messages WHERE ui_spec_session_id=%s ORDER BY created_at",
                (session_id,),
            )
            rows = cur.fetchall()
        finally:
            cur.close()
    return {"messages": [{"role": r["role"], "content": r["content"], "created_at": str(r["created_at"])} for r in rows]}


@router.post("/{session_id}/approve")
def approve_session(session_id: str, req: ApprovalRequest, current_user=Depends(get_current_user)):
    _fetch_session(session_id)
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE ui_spec_sessions SET status=%s, approved_at=%s, approved_by=%s WHERE id=%s",
                ("approved" if req.approve else "draft", datetime.now() if req.approve else None,
                 current_user["id"] if req.approve else None, session_id),
            )
            conn.commit()
        finally:
            cur.close()
    return {"status": "approved" if req.approve else "draft"}
