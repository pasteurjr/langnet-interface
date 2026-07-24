// Serviço de Servidores MCP (F2 Fase 1) — registro global + testar conexão + descoberta.
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

function headers() {
  const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
  return { 'Content-Type': 'application/json', Authorization: token ? `Bearer ${token}` : '' };
}

export interface McpTool { name: string; description?: string; }
export interface McpServer {
  id: string;
  name: string;
  transport: string;
  url?: string;
  category?: string;
  status: string;              // registrado | ativo | erro
  has_credentials: boolean;
  tools_count: number;
  tools: McpTool[];
  last_error?: string;
}
export interface McpTestResult {
  ok: boolean;
  status?: string;
  tools_count?: number;
  tools?: McpTool[];
  message?: string;
  error?: string;
}

export async function listServers(): Promise<McpServer[]> {
  const r = await fetch(`${API_BASE_URL}/mcp/servers`, { headers: headers() });
  if (!r.ok) throw new Error(`Falha ao listar servidores MCP (${r.status})`);
  return (await r.json()).servers;
}

export async function registerServer(payload: {
  name: string; transport: string; url?: string; category?: string; credentials?: Record<string, string>;
}): Promise<{ id: string }> {
  const r = await fetch(`${API_BASE_URL}/mcp/servers`, {
    method: 'POST', headers: headers(), body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`Falha ao registrar (${r.status})`);
  return r.json();
}

export async function testAdhoc(payload: {
  transport: string; url?: string; credentials?: Record<string, string>;
}): Promise<McpTestResult> {
  const r = await fetch(`${API_BASE_URL}/mcp/test`, {
    method: 'POST', headers: headers(), body: JSON.stringify(payload),
  });
  return r.json();
}

export async function testServer(id: string): Promise<McpTestResult> {
  const r = await fetch(`${API_BASE_URL}/mcp/servers/${id}/test`, { method: 'POST', headers: headers() });
  return r.json();
}

export async function deleteServer(id: string): Promise<void> {
  await fetch(`${API_BASE_URL}/mcp/servers/${id}`, { method: 'DELETE', headers: headers() });
}
