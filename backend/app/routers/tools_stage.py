"""Router da etapa FERRAMENTAS.

Segue o padrão das demais etapas do pipeline: seleção da origem (sessão do ATS) + versão,
gerar, refinar por chat, editar, histórico de versões e aprovar. O que esta etapa entrega é
o inventário de ferramentas do sistema com a ORIGEM de implementação de cada uma — e o
portão que impede a geração de código de inventar corpo de ferramenta.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid
import json
import datetime

from app.database import get_db_connection
from app.dependencies import get_current_user

from agents.langnetagents import _parse_tools_from_spec, _direct_llm_complete
from agents.langnettools_stage import (
    resolver_ferramentas, propor_contratos, aplicar_refino, portao,
)

router = APIRouter(prefix="/api/tools-stage", tags=["tools-stage"])


class GenerateRequest(BaseModel):
    agent_task_spec_session_id: Optional[str] = Field(
        None, description="Sessão do ATS a consumir; se ausente usa a mais recente do projeto")


class ChatMessageRequest(BaseModel):
    content: str = Field(..., description="Instrução de refino em linguagem natural")


class ApprovalRequest(BaseModel):
    approve: bool = True


class UpdateRequest(BaseModel):
    tools_json: Dict[str, Any] = Field(..., description="Documento completo editado")
    change_description: Optional[str] = None


def _ats_do_projeto(project_id: str, session_id: Optional[str]):
    """Devolve (ats_markdown, ats_session_id, ats_version)."""
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        if session_id:
            cur.execute("SELECT id, agent_task_spec_document, specification_version "
                        "FROM agent_task_specification_sessions WHERE id=%s", (session_id,))
        else:
            cur.execute(
                "SELECT id, agent_task_spec_document, specification_version "
                "FROM agent_task_specification_sessions WHERE project_id=%s "
                "AND agent_task_spec_document IS NOT NULL AND CHAR_LENGTH(agent_task_spec_document)>0 "
                "ORDER BY created_at DESC LIMIT 1", (project_id,))
        row = cur.fetchone()
        cur.close()
    if not row or not row.get("agent_task_spec_document"):
        raise HTTPException(404, "Nenhuma especificação de Agentes e Tarefas encontrada para este projeto")
    return row["agent_task_spec_document"], row["id"], row.get("specification_version")


def _mcp_do_projeto(project_id: str) -> List[dict]:
    """Ferramentas MCP atribuídas ao projeto (etapa MCP)."""
    try:
        from app.routers.mcp import get_project_tool_assignments  # type: ignore
        return get_project_tool_assignments(project_id) or []
    except Exception:
        pass
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT a.tool_name, a.agent_id, s.name AS server_name, t.description, t.input_schema "
                "FROM mcp_tool_assignments a "
                "LEFT JOIN mcp_servers s ON s.id = a.server_id "
                "LEFT JOIN mcp_tools t ON t.server_id = a.server_id AND t.name = a.tool_name "
                "WHERE a.project_id = %s", (project_id,))
            linhas = cur.fetchall() or []
            cur.close()
        saida = []
        for l in linhas:
            args = []
            try:
                esquema = json.loads(l.get("input_schema") or "{}")
                args = list((esquema.get("properties") or {}).keys())
            except Exception:
                args = []
            saida.append({"tool_name": l.get("tool_name"), "server_name": l.get("server_name"),
                          "description": l.get("description") or "", "input_args": args,
                          "agent_id": l.get("agent_id")})
        return saida
    except Exception:
        return []


def _gravar_versao(conn, session_id: str, versao: int, doc: dict, tipo: str, desc: str, user_id):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tool_version_history (tool_session_id, version, tools_json, change_type, "
        "change_description, created_by) VALUES (%s,%s,%s,%s,%s,%s)",
        (session_id, versao, json.dumps(doc, ensure_ascii=False), tipo, desc, user_id))
    cur.close()


@router.post("/{project_id}/generate")
def gerar(project_id: str, req: GenerateRequest, user=Depends(get_current_user)):
    """Monta o inventário de ferramentas a partir do ATS + atribuições MCP."""
    ats_md, ats_id, ats_ver = _ats_do_projeto(project_id, req.agent_task_spec_session_id)
    binding = _parse_tools_from_spec(ats_md)
    doc = resolver_ferramentas(binding, _mcp_do_projeto(project_id))
    doc = propor_contratos(doc, ats_md, _direct_llm_complete)
    doc["gate"] = portao(doc)
    sid = str(uuid.uuid4())
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tool_sessions (id, project_id, user_id, agent_task_spec_session_id, "
            "agent_task_spec_version, version, status, tools_json, total_tools, total_resolvidas, "
            "total_pendentes, generation_log) VALUES (%s,%s,%s,%s,%s,1,'completed',%s,%s,%s,%s,%s)",
            (sid, project_id, user.get("id") if isinstance(user, dict) else None, ats_id, ats_ver,
             json.dumps(doc, ensure_ascii=False), doc["resumo"]["total"],
             doc["resumo"]["resolvidas"], doc["resumo"]["pendentes"],
             f"origem: ATS {ats_id}"))
        cur.close()
        _gravar_versao(conn, sid, 1, doc, "generated", "geração inicial a partir do ATS",
                       user.get("id") if isinstance(user, dict) else None)
        conn.commit()
    return {"session_id": sid, "version": 1, **doc}


@router.get("/project/{project_id}/latest")
def ultima(project_id: str, user=Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM tool_sessions WHERE project_id=%s ORDER BY created_at DESC LIMIT 1",
                    (project_id,))
        row = cur.fetchone(); cur.close()
    if not row:
        raise HTTPException(404, "Nenhuma sessão de ferramentas para este projeto")
    row["tools_json"] = json.loads(row.get("tools_json") or "{}")
    return row


@router.get("/project/{project_id}/sessions")
def listar(project_id: str, user=Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, version, status, total_tools, total_resolvidas, total_pendentes, "
                    "approval_status, created_at FROM tool_sessions WHERE project_id=%s "
                    "ORDER BY created_at DESC", (project_id,))
        linhas = cur.fetchall() or []; cur.close()
    return {"sessions": linhas}


@router.get("/{session_id}")
def obter(session_id: str, user=Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM tool_sessions WHERE id=%s", (session_id,))
        row = cur.fetchone(); cur.close()
    if not row:
        raise HTTPException(404, "Sessão não encontrada")
    row["tools_json"] = json.loads(row.get("tools_json") or "{}")
    return row


@router.post("/{session_id}/chat")
def refinar(session_id: str, req: ChatMessageRequest, user=Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM tool_sessions WHERE id=%s", (session_id,))
        row = cur.fetchone(); cur.close()
    if not row:
        raise HTTPException(404, "Sessão não encontrada")
    doc = json.loads(row.get("tools_json") or "{}")
    doc = aplicar_refino(doc, req.content, _direct_llm_complete)
    doc["gate"] = portao(doc)
    nova = int(row.get("version") or 1) + 1
    uid = user.get("id") if isinstance(user, dict) else None
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE tool_sessions SET tools_json=%s, version=%s, total_tools=%s, "
                    "total_resolvidas=%s, total_pendentes=%s WHERE id=%s",
                    (json.dumps(doc, ensure_ascii=False), nova, doc["resumo"]["total"],
                     doc["resumo"]["resolvidas"], doc["resumo"]["pendentes"], session_id))
        for papel, texto in (("user", req.content), ("assistant", doc["gate"]["mensagem"])):
            cur.execute("INSERT INTO tool_chat_messages (id, tool_session_id, role, content) "
                        "VALUES (%s,%s,%s,%s)", (str(uuid.uuid4()), session_id, papel, texto))
        cur.close()
        _gravar_versao(conn, session_id, nova, doc, "refined", req.content[:400], uid)
        conn.commit()
    return {"session_id": session_id, "version": nova, **doc}


@router.get("/{session_id}/chat")
def historico_chat(session_id: str, user=Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT role, content, created_at FROM tool_chat_messages "
                    "WHERE tool_session_id=%s ORDER BY created_at", (session_id,))
        msgs = cur.fetchall() or []; cur.close()
    return {"messages": msgs}


@router.put("/{session_id}")
def editar(session_id: str, req: UpdateRequest, user=Depends(get_current_user)):
    doc = req.tools_json
    doc["resumo"] = {
        "total": len(doc.get("tools", [])),
        "resolvidas": sum(1 for t in doc.get("tools", []) if t.get("resolvida")),
        "pendentes": sum(1 for t in doc.get("tools", []) if not t.get("resolvida")),
    }
    doc["gate"] = portao(doc)
    uid = user.get("id") if isinstance(user, dict) else None
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT version FROM tool_sessions WHERE id=%s", (session_id,))
        row = cur.fetchone(); cur.close()
        if not row:
            raise HTTPException(404, "Sessão não encontrada")
        nova = int(row["version"] or 1) + 1
        cur = conn.cursor()
        cur.execute("UPDATE tool_sessions SET tools_json=%s, version=%s, total_tools=%s, "
                    "total_resolvidas=%s, total_pendentes=%s WHERE id=%s",
                    (json.dumps(doc, ensure_ascii=False), nova, doc["resumo"]["total"],
                     doc["resumo"]["resolvidas"], doc["resumo"]["pendentes"], session_id))
        cur.close()
        _gravar_versao(conn, session_id, nova, doc, "manual", req.change_description or "edição manual", uid)
        conn.commit()
    return {"session_id": session_id, "version": nova, **doc}


@router.get("/{session_id}/versions")
def versoes(session_id: str, user=Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT version, change_type, change_description, created_at "
                    "FROM tool_version_history WHERE tool_session_id=%s ORDER BY version DESC",
                    (session_id,))
        linhas = cur.fetchall() or []; cur.close()
    return {"versions": linhas}


@router.get("/{session_id}/versions/{version}")
def versao(session_id: str, version: int, user=Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT tools_json FROM tool_version_history WHERE tool_session_id=%s "
                    "AND version=%s", (session_id, version))
        row = cur.fetchone(); cur.close()
    if not row:
        raise HTTPException(404, "Versão não encontrada")
    return json.loads(row["tools_json"] or "{}")


@router.post("/{session_id}/approve")
def aprovar(session_id: str, req: ApprovalRequest, user=Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT tools_json FROM tool_sessions WHERE id=%s", (session_id,))
        row = cur.fetchone(); cur.close()
        if not row:
            raise HTTPException(404, "Sessão não encontrada")
        doc = json.loads(row.get("tools_json") or "{}")
        g = portao(doc)
        if req.approve and not g["aprovado"]:
            raise HTTPException(400, f"Não é possível aprovar: {g['mensagem']}")
        cur = conn.cursor()
        cur.execute("UPDATE tool_sessions SET approval_status=%s, approved_by=%s, approved_at=%s "
                    "WHERE id=%s",
                    ("approved" if req.approve else "pending",
                     user.get("id") if isinstance(user, dict) else None,
                     datetime.datetime.utcnow(), session_id))
        cur.close(); conn.commit()
    return {"session_id": session_id, "approval_status": "approved" if req.approve else "pending",
            "gate": g}
