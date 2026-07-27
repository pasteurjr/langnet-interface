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
from agents.langnetui import (
    execute_ui_spec_workflow, refine_ui_spec, regenerate_one_screen_from_spec,
)
from prompts.generate_ui_spec import find_uc_block, replace_uc_sections


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


class EditSourceRequest(BaseModel):
    """Edição da interação da tela DIRETAMENTE na Especificação de origem (UC).
    Ao salvar, cria nova versão do spec E regenera só esta tela do protótipo."""
    flow: Optional[str] = Field(None, description="Novo 'Fluxo Principal' (ação do ator / resposta do sistema)")
    wireframe: Optional[str] = Field(None, description="Novo wireframe/esquema ASCII da tela")
    screen_title: Optional[str] = Field(None, description="Nome da tela declarado no wireframe")
    render_png: bool = True


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


def _fetch_schema_sql(project_id: str, data_model_session_id: Optional[str]) -> tuple[str, Optional[str], Optional[int]]:
    """Retorna (schema_sql, data_model_session_id_efetivo, data_model_version_efetiva).

    Quando data_model_session_id vem vazio, auto-descobre o Data Model mais recente
    do projeto e retorna o ID/versão EFETIVAMENTE usados (não o None recebido)."""
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            if data_model_session_id:
                cur.execute(
                    "SELECT id, schema_sql, version FROM data_model_sessions WHERE id=%s",
                    (data_model_session_id,),
                )
            else:
                cur.execute(
                    """SELECT id, schema_sql, version FROM data_model_sessions
                       WHERE project_id=%s AND schema_sql IS NOT NULL AND CHAR_LENGTH(schema_sql)>0
                       ORDER BY created_at DESC LIMIT 1""",
                    (project_id,),
                )
            row = cur.fetchone()
        finally:
            cur.close()
    row = row or {}
    return (
        row.get("schema_sql") or "",
        row.get("id"),
        int(row["version"]) if row.get("version") is not None else None,
    )


def _current_specification_version(spec_session_id: str) -> Optional[int]:
    """Versão CURRENT da Especificação-fonte.

    execution_specification_sessions não tem coluna version própria; a fonte
    confiável é MAX(version) do histórico. Retorna None se indeterminável
    (nunca lança — rastreabilidade é aditiva/best-effort)."""
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


def _save_ui_spec_version(
    session_id: str,
    ui_spec_json: str,
    change_type: str,
    change_description: str,
    user_id: Optional[str],
) -> Optional[int]:
    """Registra um snapshot da UI Spec em ui_spec_version_history.

    Camada ADITIVA e tolerante a falha (nunca lança) — versionamento jamais quebra
    generate/refine. Alinha a etapa de Interface ao padrão das demais etapas, que
    gravam cada geração/refino no seu próprio *_version_history. Retorna a nova versão.
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT COALESCE(MAX(version), 0) + 1 FROM ui_spec_version_history "
                    "WHERE ui_spec_session_id=%s",
                    (session_id,),
                )
                new_v = int(cur.fetchone()[0])
                cur.execute(
                    "INSERT INTO ui_spec_version_history "
                    "(id, ui_spec_session_id, version, ui_spec_json, change_type, "
                    " change_description, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (str(uuid.uuid4()), session_id, new_v, ui_spec_json,
                     change_type, change_description, user_id),
                )
                conn.commit()
            finally:
                cur.close()
        return new_v
    except Exception as exc:  # noqa: BLE001 — versionamento nunca quebra o fluxo
        print(f"[UI-SPEC] falha ao salvar versão (ignorada): {exc}")
        return None


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
    schema_sql, used_dm_session_id, dm_version = _fetch_schema_sql(project_id, req.data_model_session_id)
    spec_version = _current_specification_version(req.specification_session_id)

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
                   (id, project_id, user_id, specification_session_id, specification_version,
                    data_model_session_id, data_model_version,
                    version, status, ui_spec_json, mockups_json, screens_count, generation_log)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    session_id, project_id, current_user["id"],
                    req.specification_session_id, spec_version,
                    used_dm_session_id, dm_version,
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

    # ADITIVO: registra a versão 1 no histórico (mesmo padrão das demais etapas)
    _save_ui_spec_version(
        session_id,
        json.dumps(result["ui_spec"], ensure_ascii=False),
        "initial_generation",
        "Geração inicial da UI Spec",
        current_user["id"],
    )

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

    # ADITIVO: registra o refino no histórico de versões
    _save_ui_spec_version(
        session_id,
        json.dumps(new_spec, ensure_ascii=False),
        "ai_refinement",
        f"Refino por chat — tela '{refined}'" if refined else "Refino por chat",
        current_user["id"],
    )

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


# ─────────────── AMARRAÇÃO Spec ⟷ Protótipo (por tela) ───────────────

def _screen_from_session(row: Dict[str, Any], screen_id: str) -> tuple[Dict[str, Any], list, int]:
    """Retorna (screen, screens_list, index) do ui_spec da sessão. 404 se não achar."""
    ui_spec = json.loads(row["ui_spec_json"]) if row.get("ui_spec_json") else {}
    screens = ui_spec.get("screens", [])
    for i, s in enumerate(screens):
        if s.get("id") == screen_id:
            return s, screens, i
    raise HTTPException(404, f"Tela '{screen_id}' não encontrada nesta UI Spec")


def _uc_id_of_screen(screen: Dict[str, Any]) -> Optional[str]:
    ucs = screen.get("uc") or []
    return ucs[0] if ucs else None


def _new_specification_version(spec_session_id: str, new_doc: str, user_id: Optional[str],
                               change_description: str) -> Optional[int]:
    """Grava uma NOVA versão da Especificação (manual_edit) e atualiza o documento
    corrente. Mesmo padrão do PUT /specifications/{id}. Retorna a nova versão."""
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "UPDATE execution_specification_sessions "
                "SET specification_document=%s, updated_at=NOW() WHERE id=%s",
                (new_doc, spec_session_id),
            )
            cur.execute(
                "SELECT MAX(version) AS mv FROM specification_version_history "
                "WHERE specification_session_id=%s", (spec_session_id,),
            )
            r = cur.fetchone()
            new_v = int((r and r.get("mv")) or 0) + 1
            cur.execute(
                "INSERT INTO specification_version_history "
                "(specification_session_id, version, specification_document, created_by, "
                " change_description, change_type, doc_size) "
                "VALUES (%s,%s,%s,%s,%s,'manual_edit',%s)",
                (spec_session_id, new_v, new_doc, user_id, change_description, len(new_doc)),
            )
            conn.commit()
        finally:
            cur.close()
    return new_v


def _apply_regenerated_screen(session_id: str, row: Dict[str, Any], screens: list, idx: int,
                              new_screen: Dict[str, Any], png: Optional[str],
                              spec_version: Optional[int]) -> Dict[str, Any]:
    """Substitui uma tela no ui_spec da sessão, atualiza mockup/versão/spec_version."""
    # preserva id/rota/uc originais se o LLM os alterou
    old = screens[idx]
    new_screen.setdefault("id", old.get("id"))
    new_screen.setdefault("route", old.get("route"))
    if not new_screen.get("uc"):
        new_screen["uc"] = old.get("uc")
    screens[idx] = new_screen

    ui_spec = json.loads(row["ui_spec_json"]) if row.get("ui_spec_json") else {}
    ui_spec["screens"] = screens
    mockups = json.loads(row["mockups_json"]) if row.get("mockups_json") else {}
    if png:
        mockups[new_screen["id"]] = png

    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE ui_spec_sessions SET ui_spec_json=%s, mockups_json=%s, "
                "version=version+1, specification_version=COALESCE(%s, specification_version) "
                "WHERE id=%s",
                (json.dumps(ui_spec, ensure_ascii=False),
                 json.dumps(mockups, ensure_ascii=False), spec_version, session_id),
            )
            conn.commit()
        finally:
            cur.close()
    return {"ui_spec": ui_spec, "mockup_update": {new_screen["id"]: png} if png else {}}


@router.get("/{session_id}/screen/{screen_id}/source")
def get_screen_source(session_id: str, screen_id: str, current_user=Depends(get_current_user)):
    """Origem (Especificação) da tela: o UC que a gerou — fluxo + wireframe/esquema —
    além do estado de sincronismo (versão do spec usada vs. atual)."""
    row = _fetch_session(session_id)
    screen, _screens, _idx = _screen_from_session(row, screen_id)
    uc_id = _uc_id_of_screen(screen)
    spec_session_id = row.get("specification_session_id")
    if not spec_session_id:
        raise HTTPException(404, "Sessão sem Especificação de origem vinculada")

    spec_doc, _proj = _fetch_spec_content(spec_session_id)
    spec_version_current = _current_specification_version(spec_session_id)
    spec_version_used = row.get("specification_version")

    uc = None
    if uc_id:
        found = find_uc_block(spec_doc, uc_id)
        uc = found["uc"] if found else None

    return {
        "screen_id": screen_id,
        "uc_id": uc_id,
        "spec_session_id": spec_session_id,
        "spec_version_used": spec_version_used,
        "spec_version_current": spec_version_current,
        "stale": bool(spec_version_current is not None and spec_version_used is not None
                      and spec_version_current > spec_version_used),
        "found": uc is not None,
        "actor": (uc or {}).get("actor"),
        "objetivo": (uc or {}).get("objetivo"),
        "screen_title": (uc or {}).get("screen_title"),
        "flow": (uc or {}).get("flow"),
        "wireframe": (uc or {}).get("wireframe"),
    }


@router.post("/{session_id}/screen/{screen_id}/edit-source")
def edit_screen_source(session_id: str, screen_id: str, req: EditSourceRequest,
                       current_user=Depends(get_current_user)):
    """Edita a interação da tela NA ESPECIFICAÇÃO (fluxo + wireframe/esquema) → grava
    nova versão do spec → regenera SÓ esta tela do protótipo a partir do UC editado."""
    row = _fetch_session(session_id)
    screen, screens, idx = _screen_from_session(row, screen_id)
    uc_id = _uc_id_of_screen(screen)
    if not uc_id:
        raise HTTPException(400, "Tela sem UC de origem — não há o que amarrar no spec")
    spec_session_id = row.get("specification_session_id")
    if not spec_session_id:
        raise HTTPException(404, "Sessão sem Especificação de origem vinculada")

    spec_doc, project_id = _fetch_spec_content(spec_session_id)
    new_doc = replace_uc_sections(
        spec_doc, uc_id,
        new_flow=req.flow, new_wireframe=req.wireframe, new_screen_title=req.screen_title,
    )
    if new_doc is None:
        raise HTTPException(404, f"UC '{uc_id}' não encontrado na Especificação")

    # 1) grava nova versão do spec
    new_spec_version = _new_specification_version(
        spec_session_id, new_doc, current_user["id"],
        f"Edição da interação da tela {uc_id} (via etapa de Protótipo)",
    )

    # 2) regenera só esta tela a partir do UC editado + schema da sessão
    schema_sql, _dm_id, _dm_v = _fetch_schema_sql(project_id, row.get("data_model_session_id"))
    try:
        result = regenerate_one_screen_from_spec(new_doc, uc_id, schema_sql, req.render_png)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha ao regenerar a tela: {e}")

    applied = _apply_regenerated_screen(
        session_id, row, screens, idx, result["screen"], result.get("png"), new_spec_version)

    _save_ui_spec_version(
        session_id, json.dumps(applied["ui_spec"], ensure_ascii=False),
        "spec_sync", f"Interação editada no spec ({uc_id}) → tela regenerada",
        current_user["id"],
    )
    return {
        "status": "ok", "screen_id": screen_id, "uc_id": uc_id,
        "new_spec_version": new_spec_version,
        "ui_spec": applied["ui_spec"], "mockup_update": applied["mockup_update"],
    }


@router.post("/{session_id}/screen/{screen_id}/resync")
def resync_screen(session_id: str, screen_id: str, current_user=Depends(get_current_user)):
    """Re-sincroniza a tela com a Especificação ATUAL (quando o spec foi editado em
    outra etapa): regenera só esta tela a partir do UC corrente, sem alterar o spec."""
    row = _fetch_session(session_id)
    screen, screens, idx = _screen_from_session(row, screen_id)
    uc_id = _uc_id_of_screen(screen)
    if not uc_id:
        raise HTTPException(400, "Tela sem UC de origem")
    spec_session_id = row.get("specification_session_id")
    if not spec_session_id:
        raise HTTPException(404, "Sessão sem Especificação de origem vinculada")

    spec_doc, project_id = _fetch_spec_content(spec_session_id)
    spec_version_current = _current_specification_version(spec_session_id)
    schema_sql, _dm_id, _dm_v = _fetch_schema_sql(project_id, row.get("data_model_session_id"))
    try:
        result = regenerate_one_screen_from_spec(spec_doc, uc_id, schema_sql, True)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha ao re-sincronizar: {e}")

    applied = _apply_regenerated_screen(
        session_id, row, screens, idx, result["screen"], result.get("png"), spec_version_current)
    _save_ui_spec_version(
        session_id, json.dumps(applied["ui_spec"], ensure_ascii=False),
        "spec_sync", f"Re-sincronizada com o spec atual ({uc_id})",
        current_user["id"],
    )
    return {"status": "ok", "screen_id": screen_id, "spec_version_current": spec_version_current,
            "ui_spec": applied["ui_spec"], "mockup_update": applied["mockup_update"]}


@router.get("/{session_id}/sync-status")
def sync_status(session_id: str, current_user=Depends(get_current_user)):
    """Estado de sincronismo da UI Spec com a Especificação de origem."""
    row = _fetch_session(session_id)
    spec_session_id = row.get("specification_session_id")
    used = row.get("specification_version")
    current = _current_specification_version(spec_session_id) if spec_session_id else None
    return {
        "spec_session_id": spec_session_id,
        "spec_version_used": used,
        "spec_version_current": current,
        "stale": bool(current is not None and used is not None and current > used),
    }


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
