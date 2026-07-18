"""
Test Cases Router — Geração de Casos de Teste por Grafo de Causa-Efeito (CEG).

Nova etapa do pipeline LangNet: a partir da Especificação Funcional (casos de uso),
extrai o grafo causa-efeito de cada UC (método do artigo do Pasteur Ottoni), gera a
tabela de decisão minimizada e os casos de teste. Fase seguinte: executor que roda
cada caso contra a app rodando (esperado×obtido).

Espelha o padrão de routers/ui_spec.py.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid
import json
import datetime

from app.database import get_db_connection
from app.dependencies import get_current_user

from agents.langnettest import parse_use_cases, ceg_for_uc, refine_ceg
from agents.ceg_engine import generate_test_cases
from agents.ceg_render import ceg_to_svg
from agents.langnetvalidation import build_validation_html


router = APIRouter(prefix="/api/test-cases", tags=["test-cases"])


# ─────────────────── Schemas ───────────────────

class GenerateRequest(BaseModel):
    specification_session_id: str = Field(..., description="Session ID da specification (casos de uso) a consumir")
    only: Optional[List[str]] = Field(None, description="Lista de UC ids p/ gerar só um subconjunto (ex.: ['UC-001'])")


class ChatMessageRequest(BaseModel):
    content: str = Field(..., description="Instrução de refino em linguagem natural")
    uc_id: Optional[str] = Field(None, description="UC alvo do ajuste (ex.: 'UC-004'). Se ausente, tenta inferir.")


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


def _fetch_session(session_id: str) -> Dict[str, Any]:
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM test_case_sessions WHERE id=%s", (session_id,))
            row = cur.fetchone()
        finally:
            cur.close()
    if not row:
        raise HTTPException(404, "Sessão de casos de teste não encontrada")
    return row


def _update_results(session_id: str, results: List[dict], status: str, log: str) -> None:
    total_cases = sum(r.get("n_cases", 0) for r in results)
    total_ucs = len([r for r in results if not r.get("error")])
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """UPDATE test_case_sessions
                   SET results_json=%s, total_ucs=%s, total_cases=%s, status=%s, generation_log=%s
                   WHERE id=%s""",
                (json.dumps({"results": results}, ensure_ascii=False),
                 total_ucs, total_cases, status, log, session_id),
            )
            conn.commit()
        finally:
            cur.close()


def _serialize(row: Dict[str, Any], with_svg: bool = True) -> Dict[str, Any]:
    data = json.loads(row["results_json"]) if row.get("results_json") else {"results": []}
    results = data.get("results", [])
    if with_svg:
        for r in results:
            if r.get("ceg") and "svg" not in r:
                try:
                    r["svg"] = ceg_to_svg(r["ceg"])
                except Exception:
                    r["svg"] = None
    return {
        "session_id": row["id"],
        "project_id": row["project_id"],
        "specification_session_id": row.get("specification_session_id"),
        "status": row["status"],
        "version": row["version"],
        "total_ucs": row["total_ucs"],
        "total_cases": row["total_cases"],
        "results": results,
        "generation_log": row.get("generation_log"),
        "created_at": str(row.get("created_at")),
        "updated_at": str(row.get("updated_at")),
    }


# ─────────────────── Background: geração progressiva ───────────────────

def _run_generation(session_id: str, spec_doc: str, only: Optional[List[str]]) -> None:
    """Gera o CEG + casos de cada UC, persistindo progressivamente (galeria enche
    conforme processa)."""
    ucs = parse_use_cases(spec_doc)
    if only:
        ucs = [u for u in ucs if u["id"] in only]
    results: List[dict] = []
    log: List[str] = []
    for i, uc in enumerate(ucs, 1):
        try:
            ceg = ceg_for_uc(uc)
        except Exception as e:
            ceg = None
            log.append(f"{uc['id']}: erro no LLM — {e}")
        if not ceg:
            results.append({"uc": uc["id"], "name": uc["name"], "error": "CEG não gerado"})
            log.append(f"{uc['id']}: CEG falhou")
        else:
            tc = generate_test_cases(ceg)
            results.append({"uc": uc["id"], "name": uc["name"], "actor": uc.get("actor"),
                            "objetivo": uc.get("objetivo"), "ceg": ceg, **tc})
            log.append(f"{uc['id']}: {tc['n_causes']} causas, {tc['n_effects']} efeitos, {tc['n_cases']} casos")
        # persiste a cada UC — status 'generating' até o último
        st = "draft" if i == len(ucs) else "generating"
        _update_results(session_id, results, st, "\n".join(log))


# ─────────────────── Endpoints ───────────────────

@router.post("/{project_id}/generate")
def generate_test_cases_ep(project_id: str, req: GenerateRequest,
                           background: BackgroundTasks, current_user=Depends(get_current_user)):
    """Dispara a geração dos casos de teste (CEG) de todos os UCs (ou só `only`).
    Roda em background e persiste progressivamente; use GET latest p/ acompanhar."""
    spec_doc, _ = _fetch_spec_content(req.specification_session_id)

    session_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO test_case_sessions
                   (id, project_id, user_id, specification_session_id, version, status,
                    results_json, total_ucs, total_cases, generation_log)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (session_id, project_id, current_user["id"], req.specification_session_id,
                 1, "generating", json.dumps({"results": []}), 0, 0, "Iniciando…"),
            )
            conn.commit()
        finally:
            cur.close()

    background.add_task(_run_generation, session_id, spec_doc, req.only)
    return {"session_id": session_id, "status": "generating",
            "message": "Geração iniciada. Acompanhe via GET /project/{project_id}/latest"}


@router.get("/project/{project_id}/latest")
def get_latest_for_project(project_id: str, current_user=Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT * FROM test_case_sessions WHERE project_id=%s ORDER BY created_at DESC LIMIT 1",
                (project_id,),
            )
            row = cur.fetchone()
        finally:
            cur.close()
    if not row:
        return {"session_id": None, "message": "Nenhum caso de teste gerado ainda"}
    return _serialize(row)


@router.get("/{session_id}")
def get_session(session_id: str, current_user=Depends(get_current_user)):
    return _serialize(_fetch_session(session_id))


# ─────────────────── Refino pelo agente (chat) ───────────────────

def _pick_uc(results: List[dict], content: str, uc_id: Optional[str]) -> Optional[int]:
    """Índice do UC alvo: usa uc_id, senão procura um 'UC-\\d+' citado no texto."""
    import re
    target = uc_id
    if not target:
        m = re.search(r'UC[-\s]?(\d+)', content, re.I)
        if m:
            target = f"UC-{int(m.group(1)):03d}"
    if not target:
        return None
    for i, r in enumerate(results):
        if r.get("uc") == target:
            return i
    return None


@router.post("/{session_id}/chat")
def chat_refine(session_id: str, req: ChatMessageRequest, current_user=Depends(get_current_user)):
    """Refina os casos de teste: o agente reajusta o grafo causa-efeito de um UC
    conforme a instrução; regenera a tabela de decisão e os casos; sobe a versão.
    O documento de validação reflete automaticamente (é gerado a partir daqui)."""
    row = _fetch_session(session_id)
    data = json.loads(row["results_json"]) if row.get("results_json") else {"results": []}
    results = data.get("results", [])

    idx = _pick_uc(results, req.content, req.uc_id)
    if idx is None:
        raise HTTPException(400, "Não identifiquei o UC a ajustar. Informe o uc_id (ex.: 'UC-004').")
    target = results[idx]
    if not target.get("ceg"):
        raise HTTPException(400, f"{target.get('uc')} não tem grafo para refinar.")

    try:
        new_ceg = refine_ceg(target["ceg"], req.content)
    except Exception as e:
        raise HTTPException(502, f"Falha no refino: {e}")
    if not new_ceg:
        raise HTTPException(502, "O agente não retornou um grafo válido. Tente reformular a instrução.")

    tc = generate_test_cases(new_ceg)
    results[idx] = {"uc": target["uc"], "name": target.get("name"), "actor": target.get("actor"),
                    "objetivo": target.get("objetivo"), "ceg": new_ceg, **tc}

    total_cases = sum(r.get("n_cases", 0) for r in results if not r.get("error"))
    total_ucs = len([r for r in results if not r.get("error")])
    reply = f"{target['uc']} ajustado: {tc['n_causes']} causas, {tc['n_effects']} efeitos, {tc['n_cases']} casos."

    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """UPDATE test_case_sessions SET results_json=%s, total_ucs=%s, total_cases=%s,
                   version=version+1 WHERE id=%s""",
                (json.dumps({"results": results}, ensure_ascii=False), total_ucs, total_cases, session_id),
            )
            cur.execute(
                "INSERT INTO test_case_chat_messages (id, test_case_session_id, role, content, uc_id) VALUES (%s,%s,%s,%s,%s)",
                (str(uuid.uuid4()), session_id, "user", req.content, target["uc"]),
            )
            cur.execute(
                "INSERT INTO test_case_chat_messages (id, test_case_session_id, role, content, uc_id) VALUES (%s,%s,%s,%s,%s)",
                (str(uuid.uuid4()), session_id, "assistant", reply, target["uc"]),
            )
            conn.commit()
        finally:
            cur.close()

    updated = dict(results[idx])
    try:
        updated["svg"] = ceg_to_svg(new_ceg)
    except Exception:
        updated["svg"] = None
    return {"status": "ok", "uc": target["uc"], "reply": reply, "result": updated}


@router.get("/{session_id}/chat")
def get_chat(session_id: str, current_user=Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT role, content, uc_id, created_at FROM test_case_chat_messages "
                "WHERE test_case_session_id=%s ORDER BY created_at ASC",
                (session_id,),
            )
            rows = cur.fetchall()
        finally:
            cur.close()
    return {"messages": [{"role": r["role"], "content": r["content"], "uc_id": r["uc_id"],
                          "at": str(r["created_at"])} for r in rows]}


@router.post("/{session_id}/approve")
def approve_session(session_id: str, req: ApprovalRequest, current_user=Depends(get_current_user)):
    _fetch_session(session_id)
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute("UPDATE test_case_sessions SET status=%s WHERE id=%s",
                        ("approved" if req.approve else "draft", session_id))
            conn.commit()
        finally:
            cur.close()
    return {"status": "approved" if req.approve else "draft"}


@router.get("/{session_id}/document", response_class=HTMLResponse)
def get_validation_document(session_id: str, current_user=Depends(get_current_user)):
    """Documento de Validação por Casos de Teste (HTML imprimível/baixável)."""
    row = _fetch_session(session_id)
    data = json.loads(row["results_json"]) if row.get("results_json") else {"results": []}
    # nome do projeto
    project_name = "Projeto"
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT name FROM projects WHERE id=%s", (row["project_id"],))
            p = cur.fetchone()
            if p:
                project_name = p["name"]
        finally:
            cur.close()
    html = build_validation_html(
        data.get("results", []), project_name,
        datetime.date.today().strftime("%d/%m/%Y"),
    )
    return HTMLResponse(content=html)
