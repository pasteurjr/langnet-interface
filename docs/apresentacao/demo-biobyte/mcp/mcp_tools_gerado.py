"""Tools MCP (Model Context Protocol) — auto-gerado pelo LangNet (F2 Fase 3).
Cada tool chama uma ferramenta de um servidor MCP via cliente `mcp` (SSE/HTTP).
Credenciais (se houver) vêm de variáveis de ambiente MCP_CRED_<id> (JSON de headers)."""
import os, json, asyncio
from pydantic import BaseModel, ConfigDict
from crewai.tools import BaseTool

class _MCPArgs(BaseModel):
    model_config = ConfigDict(extra="allow")

def _mcp_call(url, transport, tool, cred_env, args):
    """Chama uma tool MCP e devolve o texto do resultado."""
    headers = None
    raw = os.getenv(cred_env)
    if raw:
        try: headers = json.loads(raw)
        except Exception: headers = None
    async def _c():
        from mcp import ClientSession
        if (transport or "sse") == "http":
            from mcp.client.streamable_http import streamablehttp_client as _cli
            async with _cli(url, headers=headers) as (r, w, _):
                return await _run_call(r, w, tool, args)
        from mcp.client.sse import sse_client
        async with sse_client(url, headers=headers) as (r, w):
            return await _run_call(r, w, tool, args)
    try:
        return asyncio.run(_c())
    except Exception as e:
        return json.dumps({"mcp_error": str(e)})

async def _run_call(read, write, tool, args):
    from mcp import ClientSession
    async with ClientSession(read, write) as s:
        await s.initialize()
        res = await s.call_tool(tool, args or {})
        return "\n".join(getattr(c, "text", None) or str(c) for c in res.content)

class MCPTool_0(BaseTool):
    name: str = "consultar_microbiologia"
    description: str = "Consulta o resultado de hemocultura e antibiograma do paciente no sistema\nlaboratorial (LIS) externo. Retorna microrganismo, perfil de resist\u00eancia e flag de\nmultirresist\u00eancia (MDR). Use o identificador do caso (ex.: 'CAS-2023-001')."
    args_schema: type[BaseModel] = _MCPArgs
    def _run(self, **kwargs):
        return _mcp_call("http://127.0.0.1:9120/sse", "sse", "consultar_microbiologia", "MCP_CRED_2e2377718a2d", kwargs)

class MCPTool_1(BaseTool):
    name: str = "escore_risco_cox"
    description: str = "Calcula o escore de risco de ICSAC pelo modelo de perigos proporcionais de Cox.\nRecebe fatores cl\u00ednicos (dias de cateter, interna\u00e7\u00e3o em UTI, nutri\u00e7\u00e3o parenteral,\nneutropenia, idade) e devolve o escore (0-1) e o n\u00edvel de risco (Baixo/M\u00e9dio/Alto)."
    args_schema: type[BaseModel] = _MCPArgs
    def _run(self, **kwargs):
        return _mcp_call("http://127.0.0.1:9120/sse", "sse", "escore_risco_cox", "MCP_CRED_2e2377718a2d", kwargs)


MCP_TOOLS = {
    "consultar_microbiologia": MCPTool_0(),
    "escore_risco_cox": MCPTool_1(),
}
