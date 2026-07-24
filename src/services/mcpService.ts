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

// ── F2 Fase 2: vínculo por projeto + atribuição de tools aos agentes ──
export interface ProjectServer extends McpServer { enabled: boolean; }
export interface ProjectTool { mcp_server_id: string; server_name: string; tool_name: string; description: string; }
export interface AgentInfo { agent_id: string; role: string; goal: string; }
export interface AgentTool { id: string; agent_id: string; mcp_server_id: string; tool_name: string; source: string; }
export interface Suggestion { agent_id: string; mcp_server_id: string; tool_name: string; server_name: string; score: number; match: string[]; }

export async function projectServers(pid: string): Promise<ProjectServer[]> {
  const r = await fetch(`${API_BASE_URL}/mcp/project/${pid}/servers`, { headers: headers() });
  return (await r.json()).servers;
}
export async function enableServer(pid: string, sid: string): Promise<void> {
  await fetch(`${API_BASE_URL}/mcp/project/${pid}/servers/${sid}`, { method: 'POST', headers: headers() });
}
export async function disableServer(pid: string, sid: string): Promise<void> {
  await fetch(`${API_BASE_URL}/mcp/project/${pid}/servers/${sid}`, { method: 'DELETE', headers: headers() });
}
export async function projectTools(pid: string): Promise<ProjectTool[]> {
  const r = await fetch(`${API_BASE_URL}/mcp/project/${pid}/tools`, { headers: headers() });
  return (await r.json()).tools;
}
export async function projectAgents(pid: string): Promise<AgentInfo[]> {
  const r = await fetch(`${API_BASE_URL}/mcp/project/${pid}/agents`, { headers: headers() });
  return (await r.json()).agents;
}
export async function agentTools(pid: string): Promise<AgentTool[]> {
  const r = await fetch(`${API_BASE_URL}/mcp/project/${pid}/agent-tools`, { headers: headers() });
  return (await r.json()).agent_tools;
}
export async function assignTool(pid: string, p: { agent_id: string; mcp_server_id: string; tool_name: string; source?: string; }): Promise<void> {
  await fetch(`${API_BASE_URL}/mcp/project/${pid}/agent-tools`, { method: 'POST', headers: headers(), body: JSON.stringify(p) });
}
export async function unassignTool(pid: string, agent_id: string, tool_name: string): Promise<void> {
  await fetch(`${API_BASE_URL}/mcp/project/${pid}/agent-tools?agent_id=${encodeURIComponent(agent_id)}&tool_name=${encodeURIComponent(tool_name)}`, { method: 'DELETE', headers: headers() });
}
export async function suggestTools(pid: string): Promise<Suggestion[]> {
  const r = await fetch(`${API_BASE_URL}/mcp/project/${pid}/suggest`, { method: 'POST', headers: headers() });
  return (await r.json()).suggestions;
}
