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

from agents.langnettest import parse_use_cases, ceg_for_uc, refine_ceg, review_test_cases
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


class UpdateRequest(BaseModel):
    results_json: Optional[Dict[str, Any]] = Field(None, description="Objeto completo dos resultados {'results':[...]} editado")
    validation_document: Optional[str] = Field(None, description="HTML do documento de validação (opcional; se ausente é regerado)")
    change_description: Optional[str] = Field(None, description="Descrição da alteração manual")


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


def _project_name(project_id: str) -> str:
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT name FROM projects WHERE id=%s", (project_id,))
            p = cur.fetchone()
        finally:
            cur.close()
    return (p or {}).get("name") or "Projeto"


def _regen_validation_document(session_id: str) -> None:
    """(Re)gera o Documento de Validação e PERSISTE no banco (coluna validation_document),
    seguindo o padrão das outras etapas — o documento é um artefato versionado, não efêmero."""
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT project_id, results_json FROM test_case_sessions WHERE id=%s", (session_id,))
            row = cur.fetchone()
        finally:
            cur.close()
    if not row:
        return
    data = json.loads(row["results_json"]) if row.get("results_json") else {"results": []}
    html = build_validation_html(
        data.get("results", []), _project_name(row["project_id"]),
        datetime.date.today().strftime("%d/%m/%Y"),
    )
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute("UPDATE test_case_sessions SET validation_document=%s WHERE id=%s", (html, session_id))
            conn.commit()
        finally:
            cur.close()


def _save_version(session_id: str, results_json_str: str, validation_document: Optional[str],
                  change_type: str, change_description: Optional[str],
                  user_id: Optional[str]) -> int:
    """Grava um snapshot no histórico (test_case_version_history) e retorna a nova versão.

    A próxima versão = COALESCE(MAX(version),0)+1 do histórico dessa sessão. A coluna
    version da própria sessão é mantida em sincronia com esse número (fonte única de
    verdade), para evitar dupla contagem em fluxos que também mexem em version.
    """
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT COALESCE(MAX(version),0)+1 AS next_version "
                "FROM test_case_version_history WHERE session_id=%s",
                (session_id,),
            )
            row = cur.fetchone()
            new_version = row["next_version"] if row and row.get("next_version") else 1
        finally:
            cur.close()

    doc_size = len(results_json_str or "")
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO test_case_version_history
                   (session_id, version, results_json, validation_document, created_by,
                    change_type, change_description, doc_size)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (session_id, new_version, results_json_str, validation_document, user_id,
                 change_type, (change_description or "")[:500] or None, doc_size),
            )
            # mantém test_case_sessions.version em sincronia com o histórico
            cur.execute("UPDATE test_case_sessions SET version=%s WHERE id=%s",
                        (new_version, session_id))
            conn.commit()
        finally:
            cur.close()
    return new_version


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
    # ao concluir, gera e persiste o Documento de Validação no banco
    try:
        _regen_validation_document(session_id)
    except Exception:
        pass
    # registra a versão inicial no histórico (snapshot dos resultados + doc de validação)
    try:
        final = _fetch_session(session_id)
        _save_version(
            session_id,
            final.get("results_json") or json.dumps({"results": results}, ensure_ascii=False),
            final.get("validation_document"),
            change_type="initial_generation",
            change_description="Geração inicial dos casos de teste",
            user_id=final.get("user_id"),
        )
    except Exception:
        pass


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

    results_json_str = json.dumps({"results": results}, ensure_ascii=False)
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            # NÃO incrementa version aqui — _save_version é a fonte única da verdade
            cur.execute(
                """UPDATE test_case_sessions SET results_json=%s, total_ucs=%s, total_cases=%s
                   WHERE id=%s""",
                (results_json_str, total_ucs, total_cases, session_id),
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

    # regenera e persiste o Documento de Validação (reflete o refino)
    try:
        _regen_validation_document(session_id)
    except Exception:
        pass

    # registra a nova versão no histórico (fonte única — também sincroniza version da sessão)
    try:
        refreshed = _fetch_session(session_id)
        _save_version(
            session_id,
            refreshed.get("results_json") or results_json_str,
            refreshed.get("validation_document"),
            change_type="ai_refinement",
            change_description=req.content,
            user_id=current_user.get("id"),
        )
    except Exception:
        pass

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
    """Documento de Validação por Casos de Teste — servido do banco (persistido na
    geração/refino). Se ainda não houver, gera, persiste e retorna."""
    row = _fetch_session(session_id)
    if row.get("validation_document"):
        return HTMLResponse(content=row["validation_document"])
    _regen_validation_document(session_id)
    row = _fetch_session(session_id)
    return HTMLResponse(content=row.get("validation_document") or "<h1>Documento indisponível</h1>")


# ─────────────────── Histórico de versões ───────────────────

@router.get("/{session_id}/versions")
def list_versions(session_id: str, current_user=Depends(get_current_user)):
    """Lista as versões da sessão (mais recente primeiro)."""
    _fetch_session(session_id)
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                """SELECT version, created_at, change_description, change_type, doc_size
                   FROM test_case_version_history WHERE session_id=%s
                   ORDER BY version DESC""",
                (session_id,),
            )
            rows = cur.fetchall()
        finally:
            cur.close()
    return {"versions": [
        {"version": r["version"], "created_at": str(r["created_at"]),
         "change_description": r["change_description"], "change_type": r["change_type"],
         "doc_size": r["doc_size"]}
        for r in rows
    ]}


@router.get("/{session_id}/versions/{version}")
def get_version(session_id: str, version: int, current_user=Depends(get_current_user)):
    """Retorna o snapshot completo de uma versão: results (com svg por UC) + doc de validação."""
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT * FROM test_case_version_history WHERE session_id=%s AND version=%s",
                (session_id, version),
            )
            row = cur.fetchone()
        finally:
            cur.close()
    if not row:
        raise HTTPException(404, f"Versão {version} não encontrada")

    data = json.loads(row["results_json"]) if row.get("results_json") else {"results": []}
    results = data.get("results", [])
    for r in results:
        if r.get("ceg") and "svg" not in r:
            try:
                r["svg"] = ceg_to_svg(r["ceg"])
            except Exception:
                r["svg"] = None
    return {
        "session_id": session_id,
        "version": row["version"],
        "change_type": row["change_type"],
        "change_description": row["change_description"],
        "created_at": str(row.get("created_at")),
        "results": results,
        "validation_document": row.get("validation_document"),
    }


@router.put("/{session_id}")
def update_session(session_id: str, req: UpdateRequest, current_user=Depends(get_current_user)):
    """Edição manual: persiste um results_json editado, regenera o documento de
    validação e registra uma versão manual_edit."""
    row = _fetch_session(session_id)

    if req.results_json is not None:
        data = req.results_json
        results = data.get("results", []) if isinstance(data, dict) else []
        results_json_str = json.dumps({"results": results}, ensure_ascii=False)
        total_cases = sum(r.get("n_cases", 0) for r in results if not r.get("error"))
        total_ucs = len([r for r in results if not r.get("error")])
        with get_db_connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    """UPDATE test_case_sessions SET results_json=%s, total_ucs=%s, total_cases=%s
                       WHERE id=%s""",
                    (results_json_str, total_ucs, total_cases, session_id),
                )
                conn.commit()
            finally:
                cur.close()
    else:
        results_json_str = row.get("results_json") or json.dumps({"results": []}, ensure_ascii=False)

    # documento de validação: usa o enviado, senão regenera a partir dos resultados
    if req.validation_document is not None:
        with get_db_connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute("UPDATE test_case_sessions SET validation_document=%s WHERE id=%s",
                            (req.validation_document, session_id))
                conn.commit()
            finally:
                cur.close()
    else:
        try:
            _regen_validation_document(session_id)
        except Exception:
            pass

    refreshed = _fetch_session(session_id)
    new_version = _save_version(
        session_id,
        refreshed.get("results_json") or results_json_str,
        refreshed.get("validation_document"),
        change_type="manual_edit",
        change_description=req.change_description or "Edição manual dos casos de teste",
        user_id=current_user.get("id"),
    )
    return {"message": "Casos de teste atualizados", "version": new_version}


@router.post("/{session_id}/review")
def review_session(session_id: str, current_user=Depends(get_current_user)):
    """Revisão automática (LLM): retorna sugestões de melhoria dos casos de teste.
    NÃO modifica os resultados nem cria versão."""
    row = _fetch_session(session_id)
    data = json.loads(row["results_json"]) if row.get("results_json") else {"results": []}
    results = data.get("results", [])
    try:
        suggestions = review_test_cases(results)
    except Exception as e:
        suggestions = f"Não foi possível gerar sugestões automáticas no momento ({e})."
    return {"suggestions": suggestions}
