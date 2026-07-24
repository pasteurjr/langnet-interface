"""
Router: /api/mcp — Servidores MCP (Model Context Protocol) — F2 Fase 1

Registro GLOBAL de servidores MCP + teste de conexão real (handshake) que DESCOBRE
as ferramentas expostas pelo servidor. Segredos (credenciais/headers) nunca são
retornados em claro. Um servidor só fica 'ativo' após um teste bem-sucedido.

Transportes suportados na Fase 1: sse (recomendado) e http (streamable). stdio fica
para uma fase seguinte.
"""
import json
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.database import get_db_connection
from app.routers.auth import get_current_user

router = APIRouter(prefix="/mcp", tags=["mcp"])


# ── Descoberta via cliente MCP ──
async def _discover_tools(transport: str, url: str, headers: Optional[dict]) -> List[Dict[str, Any]]:
    """Conecta ao servidor MCP e lista suas ferramentas. Levanta em caso de falha."""
    from mcp import ClientSession
    transport = (transport or "sse").lower()
    if not url:
        raise ValueError("url do servidor MCP é obrigatória para sse/http")

    async def _list(read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.list_tools()
            return [{
                "name": t.name,
                "description": t.description or "",
                "input_schema": getattr(t, "inputSchema", None),
            } for t in res.tools]

    if transport == "sse":
        from mcp.client.sse import sse_client
        async with sse_client(url, headers=headers or None) as (read, write):
            return await _list(read, write)
    elif transport == "http":
        from mcp.client.streamable_http import streamablehttp_client
        async with streamablehttp_client(url, headers=headers or None) as (read, write, _):
            return await _list(read, write)
    else:
        raise ValueError(f"transporte '{transport}' não suportado na Fase 1 (use sse ou http)")


def _row_public(row: dict) -> dict:
    """Serializa um servidor mascarando os segredos."""
    caps = []
    if row.get("capabilities_json"):
        try:
            caps = json.loads(row["capabilities_json"])
        except Exception:
            caps = []
    return {
        "id": row["id"],
        "name": row["name"],
        "transport": row["transport"],
        "url": row.get("url"),
        "command": row.get("command"),
        "category": row.get("category"),
        "status": row.get("status"),
        "has_credentials": bool(row.get("credentials_json")),
        "tools_count": len(caps),
        "tools": caps,
        "last_error": row.get("last_error"),
        "updated_at": str(row.get("updated_at")) if row.get("updated_at") else None,
    }


# ── Models ──
class ServerIn(BaseModel):
    name: str
    transport: str = "sse"
    url: Optional[str] = None
    command: Optional[str] = None
    category: Optional[str] = None
    credentials: Optional[Dict[str, str]] = None  # headers/env (segredo)


class TestIn(BaseModel):
    transport: str = "sse"
    url: Optional[str] = None
    credentials: Optional[Dict[str, str]] = None


# ── POST /mcp/test — testa uma config ad-hoc (antes de salvar) ──
@router.post("/test")
async def test_connection(req: TestIn, current_user: dict = Depends(get_current_user)):
    try:
        tools = await _discover_tools(req.transport, req.url or "", req.credentials)
        return {"ok": True, "tools_count": len(tools),
                "tools": [{"name": t["name"], "description": t["description"]} for t in tools],
                "message": f"Conectado — {len(tools)} ferramenta(s) descoberta(s)."}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


# ── POST /mcp/servers — registrar ──
@router.post("/servers")
def register_server(req: ServerIn, current_user: dict = Depends(get_current_user)):
    sid = str(uuid.uuid4())
    creds = json.dumps(req.credentials) if req.credentials else None
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO mcp_servers (id, name, transport, url, command, category, "
                "credentials_json, status, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,'registrado',%s)",
                (sid, req.name, req.transport, req.url, req.command, req.category, creds,
                 current_user.get("id")),
            )
            conn.commit()
            cur.close()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(400, f"Falha ao registrar servidor MCP: {exc}")
    return {"id": sid, "status": "registrado"}


# ── GET /mcp/servers — listar (mascarado) ──
@router.get("/servers")
def list_servers(current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM mcp_servers ORDER BY created_at DESC")
        rows = cur.fetchall()
        cur.close()
    return {"servers": [_row_public(r) for r in rows]}


# ── GET /mcp/servers/{id} — detalhe + tools ──
@router.get("/servers/{server_id}")
def get_server(server_id: str, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM mcp_servers WHERE id=%s", (server_id,))
        row = cur.fetchone()
        cur.close()
    if not row:
        raise HTTPException(404, "Servidor MCP não encontrado")
    return _row_public(row)


# ── POST /mcp/servers/{id}/test — testar + descobrir + ativar ──
@router.post("/servers/{server_id}/test")
async def test_server(server_id: str, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM mcp_servers WHERE id=%s", (server_id,))
        row = cur.fetchone()
        cur.close()
    if not row:
        raise HTTPException(404, "Servidor MCP não encontrado")
    headers = {}
    if row.get("credentials_json"):
        try:
            headers = json.loads(row["credentials_json"])
        except Exception:
            headers = {}
    try:
        tools = await _discover_tools(row["transport"], row.get("url") or "", headers)
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE mcp_servers SET status='ativo', capabilities_json=%s, last_error=NULL WHERE id=%s",
                (json.dumps(tools, ensure_ascii=False), server_id),
            )
            conn.commit(); cur.close()
        return {"ok": True, "status": "ativo", "tools_count": len(tools),
                "tools": [{"name": t["name"], "description": t["description"]} for t in tools],
                "message": f"Ativo — {len(tools)} ferramenta(s) descoberta(s)."}
    except Exception as exc:  # noqa: BLE001
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE mcp_servers SET status='erro', last_error=%s WHERE id=%s",
                        (str(exc)[:500], server_id))
            conn.commit(); cur.close()
        return {"ok": False, "status": "erro", "error": str(exc)}


# ── DELETE /mcp/servers/{id} ──
@router.delete("/servers/{server_id}")
def delete_server(server_id: str, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM mcp_servers WHERE id=%s", (server_id,))
        affected = cur.rowcount
        conn.commit(); cur.close()
    if not affected:
        raise HTTPException(404, "Servidor MCP não encontrado")
    return {"status": "removido"}


# ═══════════════════════════════════════════════════════════════════════
# F2 Fase 2 — Vínculo por projeto + atribuição de tools aos agentes
# ═══════════════════════════════════════════════════════════════════════
import re as _re_mcp


_STOP = {"para", "pela", "pelo", "com", "sem", "por", "dos", "das", "que", "uma", "seu", "sua",
         "the", "and", "for", "com", "agent", "agente", "gerar", "manter", "realizar", "cada"}


def _tokens(s: str):
    return set(t for t in _re_mcp.split(r"[^a-zA-Z0-9]+", (s or "").lower())
               if len(t) > 3 and t not in _STOP)


def _project_agents(project_id: str):
    """Lista os agentes (id, role, goal) do agents.yaml mais recente do projeto."""
    import yaml as _yaml
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT agents_yaml_content FROM agents_yaml_sessions WHERE project_id=%s "
                "AND status='completed' ORDER BY created_at DESC LIMIT 1", (project_id,))
            r = cur.fetchone(); cur.close()
        if not r or not r.get("agents_yaml_content"):
            return []
        content = r["agents_yaml_content"]
        # Remove cercas markdown (```yaml ... ```) que o LLM às vezes envolve.
        mfence = _re_mcp.search(r"```(?:ya?ml)?\s*\n(.*?)\n```", content, _re_mcp.DOTALL | _re_mcp.IGNORECASE)
        if mfence:
            content = mfence.group(1)
        else:
            content = "\n".join(l for l in content.splitlines() if not l.strip().startswith("```"))
        parsed = _yaml.safe_load(content) or {}
        out = []
        for aid, adef in parsed.items():
            if isinstance(adef, dict):
                out.append({"agent_id": aid, "role": adef.get("role", ""), "goal": adef.get("goal", "")})
        return out
    except Exception as exc:  # noqa: BLE001
        print(f"[MCP] falha ao ler agents do projeto: {exc}")
        return []


def _project_enabled_servers(project_id: str):
    """Servidores MCP ativos habilitados no projeto (com suas tools)."""
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT s.* FROM mcp_servers s JOIN mcp_project_servers ps ON ps.mcp_server_id=s.id "
            "WHERE ps.project_id=%s AND ps.enabled=1", (project_id,))
        rows = cur.fetchall(); cur.close()
    return rows


@router.get("/project/{project_id}/servers")
def project_servers(project_id: str, current_user: dict = Depends(get_current_user)):
    """Todos os servidores + flag enabled para o projeto."""
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM mcp_servers ORDER BY created_at DESC")
        allsrv = cur.fetchall()
        cur.execute("SELECT mcp_server_id FROM mcp_project_servers WHERE project_id=%s AND enabled=1", (project_id,))
        enabled = {r["mcp_server_id"] for r in cur.fetchall()}
        cur.close()
    out = []
    for r in allsrv:
        pub = _row_public(r)
        pub["enabled"] = r["id"] in enabled
        out.append(pub)
    return {"servers": out}


@router.post("/project/{project_id}/servers/{server_id}")
def enable_server(project_id: str, server_id: str, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO mcp_project_servers (project_id, mcp_server_id, enabled) VALUES (%s,%s,1) "
            "ON DUPLICATE KEY UPDATE enabled=1", (project_id, server_id))
        conn.commit(); cur.close()
    return {"status": "habilitado"}


@router.delete("/project/{project_id}/servers/{server_id}")
def disable_server(project_id: str, server_id: str, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE mcp_project_servers SET enabled=0 WHERE project_id=%s AND mcp_server_id=%s",
                    (project_id, server_id))
        conn.commit(); cur.close()
    return {"status": "desabilitado"}


@router.get("/project/{project_id}/tools")
def project_tools(project_id: str, current_user: dict = Depends(get_current_user)):
    """Catálogo de tools MCP disponíveis ao projeto (dos servidores ativos habilitados)."""
    out = []
    for s in _project_enabled_servers(project_id):
        caps = json.loads(s["capabilities_json"]) if s.get("capabilities_json") else []
        for t in caps:
            out.append({"mcp_server_id": s["id"], "server_name": s["name"],
                        "tool_name": t.get("name"), "description": t.get("description", "")})
    return {"tools": out}


@router.get("/project/{project_id}/agents")
def project_agents_ep(project_id: str, current_user: dict = Depends(get_current_user)):
    return {"agents": _project_agents(project_id)}


class AgentToolIn(BaseModel):
    agent_id: str
    mcp_server_id: str
    tool_name: str
    source: str = "manual"


@router.get("/project/{project_id}/agent-tools")
def list_agent_tools(project_id: str, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM mcp_agent_tools WHERE project_id=%s", (project_id,))
        rows = cur.fetchall(); cur.close()
    return {"agent_tools": [{**r, "created_at": str(r.get("created_at"))} for r in rows]}


@router.post("/project/{project_id}/agent-tools")
def assign_agent_tool(project_id: str, req: AgentToolIn, current_user: dict = Depends(get_current_user)):
    aid = str(uuid.uuid4())
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO mcp_agent_tools (id, project_id, agent_id, mcp_server_id, tool_name, source) "
            "VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE source=VALUES(source)",
            (aid, project_id, req.agent_id, req.mcp_server_id, req.tool_name, req.source))
        conn.commit(); cur.close()
    return {"id": aid, "status": "atribuido"}


@router.delete("/project/{project_id}/agent-tools")
def unassign_agent_tool(project_id: str, agent_id: str, tool_name: str,
                        current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM mcp_agent_tools WHERE project_id=%s AND agent_id=%s AND tool_name=%s",
                    (project_id, agent_id, tool_name))
        conn.commit(); cur.close()
    return {"status": "removido"}


@router.post("/project/{project_id}/suggest")
def suggest_agent_tools(project_id: str, current_user: dict = Depends(get_current_user)):
    """Sugere (heurística por sobreposição de tokens) quais tools MCP combinam com cada agente,
    casando role+goal do agente com nome+descrição da tool. Não persiste — retorna sugestões."""
    agents = _project_agents(project_id)
    tools = project_tools(project_id, current_user)["tools"]
    suggestions = []
    for ag in agents:
        atok = _tokens(ag["role"] + " " + ag["goal"] + " " + ag["agent_id"])
        for t in tools:
            ttok = _tokens((t["tool_name"] or "") + " " + (t["description"] or ""))
            shared = atok & ttok
            if len(shared) >= 1:
                suggestions.append({
                    "agent_id": ag["agent_id"], "mcp_server_id": t["mcp_server_id"],
                    "tool_name": t["tool_name"], "server_name": t["server_name"],
                    "score": len(shared), "match": sorted(shared)})
    suggestions.sort(key=lambda s: -s["score"])
    return {"suggestions": suggestions}
