"""
Data Model Router
Nova etapa do pipeline LangNet: extrai entidades da especificação e gera
schema SQL + models.py + Alembic migrations.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid
import json
from datetime import datetime

from app.database import get_db_connection, get_db_cursor
from app.dependencies import get_current_user
from agents.langnetdatamodel import execute_data_model_workflow, refine_data_model


router = APIRouter(prefix="/api/data-model", tags=["data-model"])


# ─────────────────── Schemas ───────────────────

class GenerateRequest(BaseModel):
    specification_session_id: str = Field(..., description="Session ID da specification a consumir")
    target_dbms: str = Field("mysql", description="mysql | postgresql | sqlite")


class UpdateRequest(BaseModel):
    data_model_yaml: Optional[str] = None
    schema_sql: Optional[str] = None
    models_py: Optional[str] = None
    alembic_migration: Optional[str] = None
    status: Optional[str] = None


class ChatMessageRequest(BaseModel):
    content: str
    target_dbms: Optional[str] = "mysql"


class ApprovalRequest(BaseModel):
    approve: bool = True


# ─────────────────── Helpers ───────────────────

def _fetch_specification_content(spec_session_id: str) -> str:
    """Busca o conteúdo do documento de especificação mais recente."""
    with get_db_connection() as conn:
      cur = conn.cursor(dictionary=True)
      try:
        # Fonte primária: execution_specification_sessions (é o que o endpoint /api/specifications/ retorna)
        cur.execute(
            "SELECT specification_document FROM execution_specification_sessions WHERE id=%s",
            (spec_session_id,),
        )
        row = cur.fetchone()
        if row and row.get("specification_document"):
            return row["specification_document"]

        # Fallback 1: histórico de versões
        cur.execute(
            "SELECT specification_document FROM specification_version_history "
            "WHERE specification_session_id=%s ORDER BY version DESC LIMIT 1",
            (spec_session_id,),
        )
        row = cur.fetchone()
        if row and row.get("specification_document"):
            return row["specification_document"]

        # Fallback 2: pega da specifications table (conteúdo current)
        cur.execute("SELECT content FROM specifications WHERE id=%s", (spec_session_id,))
        row = cur.fetchone()
        if row and row.get("content"):
            return row["content"]
        raise HTTPException(status_code=404, detail="Especificação não encontrada")
      finally:
        cur.close()


def _fetch_session(session_id: str) -> Dict[str, Any]:
    with get_db_connection() as conn:
      cur = conn.cursor(dictionary=True)
      try:
        cur.execute("SELECT * FROM data_model_sessions WHERE id=%s", (session_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Data Model session não encontrada")
        return row
      finally:
        cur.close()


def _fetch_latest_by_project(project_id: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
      cur = conn.cursor(dictionary=True)
      try:
        cur.execute(
            "SELECT * FROM data_model_sessions WHERE project_id=%s ORDER BY updated_at DESC LIMIT 1",
            (project_id,),
        )
        return cur.fetchone()
      finally:
        cur.close()


# ─────────────────── Endpoints ───────────────────

@router.post("/{project_id}/generate")
def generate_data_model(project_id: str, req: GenerateRequest, current_user=Depends(get_current_user)):
    """Executa o pipeline completo de Data Model para um projeto."""
    spec_content = _fetch_specification_content(req.specification_session_id)
    try:
        result = execute_data_model_workflow(
            specification_document=spec_content,
            target_dbms=req.target_dbms,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha na geração: {e}")

    session_id = str(uuid.uuid4())
    with get_db_connection() as conn:
      cur = conn.cursor()
      try:
        cur.execute(
            """INSERT INTO data_model_sessions
               (id, project_id, user_id, specification_session_id, version, status,
                target_dbms, data_model_yaml, schema_sql, models_py, alembic_migration,
                entities_json, validation_report)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                session_id,
                project_id,
                current_user["id"],
                req.specification_session_id,
                1,
                "draft",
                req.target_dbms,
                result["data_model_yaml"],
                result["schema_sql"],
                result["models_py"],
                result["alembic_migration"],
                result["entities_json"],
                result["validation_report"],
            ),
        )
        conn.commit()
      finally:
        cur.close()

    return {"session_id": session_id, "status": "draft", **result}


@router.get("/project/{project_id}/latest")
def get_latest_for_project(project_id: str, current_user=Depends(get_current_user)):
    """Retorna a sessão de Data Model mais recente do projeto."""
    row = _fetch_latest_by_project(project_id)
    if not row:
        return {"session_id": None, "message": "Nenhum Data Model gerado ainda"}
    return {
        "session_id": row["id"],
        "status": row["status"],
        "target_dbms": row["target_dbms"],
        "version": row["version"],
        "data_model_yaml": row["data_model_yaml"],
        "schema_sql": row["schema_sql"],
        "models_py": row["models_py"],
        "alembic_migration": row["alembic_migration"],
        "entities_json": row["entities_json"],
        "validation_report": row["validation_report"],
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
    }


@router.get("/{session_id}")
def get_session(session_id: str, current_user=Depends(get_current_user)):
    """Retorna uma sessão específica."""
    row = _fetch_session(session_id)
    return {
        "session_id": row["id"],
        "status": row["status"],
        "target_dbms": row["target_dbms"],
        "version": row["version"],
        "data_model_yaml": row["data_model_yaml"],
        "schema_sql": row["schema_sql"],
        "models_py": row["models_py"],
        "alembic_migration": row["alembic_migration"],
        "entities_json": row["entities_json"],
        "validation_report": row["validation_report"],
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
    }


@router.put("/{session_id}")
def update_session(session_id: str, req: UpdateRequest, current_user=Depends(get_current_user)):
    """Atualiza campos da sessão (edição manual)."""
    row = _fetch_session(session_id)
    fields = []
    values = []
    for k in ("data_model_yaml", "schema_sql", "models_py", "alembic_migration", "status"):
        v = getattr(req, k)
        if v is not None:
            fields.append(f"{k}=%s")
            values.append(v)
    if not fields:
        return {"status": "no-op"}
    values.append(session_id)
    with get_db_connection() as conn:
      cur = conn.cursor()
      try:
        cur.execute(f"UPDATE data_model_sessions SET {','.join(fields)} WHERE id=%s", values)
        conn.commit()
      finally:
        cur.close()
    return {"status": "ok"}


@router.post("/{session_id}/chat")
def chat_refine(session_id: str, req: ChatMessageRequest, current_user=Depends(get_current_user)):
    """Refina o Data Model via chat (LLM re-gera artefatos)."""
    row = _fetch_session(session_id)
    current_yaml = row.get("data_model_yaml") or ""
    dbms = req.target_dbms or row.get("target_dbms") or "mysql"

    try:
        result = refine_data_model(current_yaml, req.content, target_dbms=dbms)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha no refino: {e}")

    # Persiste
    with get_db_connection() as conn:
      cur = conn.cursor()
      try:
        cur.execute(
            """UPDATE data_model_sessions SET
               data_model_yaml=%s, schema_sql=%s, models_py=%s,
               alembic_migration=%s, entities_json=%s,
               validation_report=%s, version=version+1
               WHERE id=%s""",
            (
                result["data_model_yaml"],
                result["schema_sql"],
                result["models_py"],
                result["alembic_migration"],
                result["entities_json"],
                result.get("validation_report", ""),
                session_id,
            ),
        )
        # Registra mensagens
        msg_user_id = str(uuid.uuid4())
        msg_bot_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO data_model_chat_messages (id, data_model_session_id, role, content) VALUES (%s,%s,%s,%s)",
            (msg_user_id, session_id, "user", req.content),
        )
        cur.execute(
            "INSERT INTO data_model_chat_messages (id, data_model_session_id, role, content) VALUES (%s,%s,%s,%s)",
            (msg_bot_id, session_id, "assistant", "Data Model atualizado com sucesso."),
        )
        conn.commit()
      finally:
        cur.close()

    return {"status": "ok", **result}


@router.get("/{session_id}/chat")
def get_chat(session_id: str, current_user=Depends(get_current_user)):
    """Histórico de conversa do refino."""
    with get_db_connection() as conn:
      cur = conn.cursor(dictionary=True)
      try:
        cur.execute(
            "SELECT role, content, created_at FROM data_model_chat_messages "
            "WHERE data_model_session_id=%s ORDER BY created_at ASC",
            (session_id,),
        )
        return {"messages": [{"role": r["role"], "content": r["content"], "at": str(r["created_at"])} for r in cur.fetchall()]}
      finally:
        cur.close()


@router.post("/{session_id}/approve")
def approve_session(session_id: str, req: ApprovalRequest, current_user=Depends(get_current_user)):
    """Aprova o Data Model (marca como 'approved' e libera pra próxima etapa)."""
    with get_db_connection() as conn:
      cur = conn.cursor()
      try:
        cur.execute(
            "UPDATE data_model_sessions SET status=%s, approved_at=NOW(), approved_by=%s WHERE id=%s",
            ("approved" if req.approve else "draft", current_user["id"], session_id),
        )
        conn.commit()
      finally:
        cur.close()
    return {"status": "approved" if req.approve else "draft"}
