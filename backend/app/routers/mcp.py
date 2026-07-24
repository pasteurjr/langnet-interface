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
