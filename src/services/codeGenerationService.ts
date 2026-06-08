/**
 * Code Generation Service
 * Comunicação com /api/code-generation/* — gera, edita, refina, baixa
 * a árvore de arquivos Python do sistema agêntico.
 */

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getAuthToken = (): string | null =>
  localStorage.getItem('accessToken') || localStorage.getItem('token');

const getAuthHeaders = (): Record<string, string> => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    Authorization: token ? `Bearer ${token}` : '',
  };
};

export interface GenerateCodePayload {
  agentsYamlSessionId: string;
  tasksYamlSessionId: string;
  taskExecutionFlowSessionId?: string;
  agentTaskSpecSessionId?: string;
  websocketPort?: number;
  sessionName?: string;
}

export interface CodeFile {
  path: string;
  content: string;
  language?: string;
}

export interface CodeGenerationSession {
  id: string;
  project_id: string;
  user_id: string;
  agents_yaml_session_id?: string;
  tasks_yaml_session_id?: string;
  task_execution_flow_session_id?: string;
  websocket_port: number;
  session_name: string;
  status: 'generating' | 'completed' | 'failed';
  generated_files?: CodeFile[];
  total_files?: number;
  current_version?: number;
  execution_metadata?: { validation_warnings?: string[]; [k: string]: any };
  created_at: string;
  updated_at: string;
}

export interface CodeChatMessage {
  id: string;
  sender_type: 'user' | 'assistant' | 'system';
  message_text: string;
  message_data?: {
    has_diff?: boolean;
    affected_paths?: string[];
    new_version?: number;
  };
  message_type: string;
  timestamp: string;
}

async function parseError(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (body?.detail) return String(body.detail);
    return JSON.stringify(body);
  } catch {
    return `${res.status} ${res.statusText}`;
  }
}

export async function generateCode(
  projectId: string,
  payload: GenerateCodePayload,
): Promise<{ session_id: string; status: string; files: CodeFile[]; total_files: number; websocket_port: number; validation_warnings?: string[] }> {
  const res = await fetch(`${API_BASE}/code-generation/${projectId}/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      agents_yaml_session_id: payload.agentsYamlSessionId,
      tasks_yaml_session_id: payload.tasksYamlSessionId,
      task_execution_flow_session_id: payload.taskExecutionFlowSessionId,
      agent_task_spec_session_id: payload.agentTaskSpecSessionId,
      websocket_port: payload.websocketPort ?? 5002,
      session_name: payload.sessionName,
    }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function listCodeSessions(projectId: string): Promise<CodeGenerationSession[]> {
  const res = await fetch(`${API_BASE}/code-generation?project_id=${projectId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(await parseError(res));
  const body = await res.json();
  return body.sessions || [];
}

export async function getCodeSession(sessionId: string): Promise<CodeGenerationSession> {
  const res = await fetch(`${API_BASE}/code-generation/${sessionId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function updateCodeFiles(
  sessionId: string,
  files: CodeFile[],
  changeDescription = 'Manual edit',
): Promise<{ status: string; version: number }> {
  const res = await fetch(`${API_BASE}/code-generation/${sessionId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({ files, change_description: changeDescription }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export interface RefineResponse {
  has_diff: boolean;
  version?: number;
  affected_paths?: string[];
  files?: CodeFile[];
  message?: string;
  validation_warnings?: string[];
}

export async function refineCode(sessionId: string, message: string): Promise<RefineResponse> {
  const res = await fetch(`${API_BASE}/code-generation/${sessionId}/refine`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function listVersions(sessionId: string) {
  const res = await fetch(`${API_BASE}/code-generation/${sessionId}/versions`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return (await res.json()).versions || [];
}

export async function getVersion(sessionId: string, version: number) {
  const res = await fetch(`${API_BASE}/code-generation/${sessionId}/versions/${version}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function getChatHistory(sessionId: string): Promise<CodeChatMessage[]> {
  const res = await fetch(`${API_BASE}/code-generation/${sessionId}/chat-history`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return (await res.json()).messages || [];
}

export async function downloadZip(sessionId: string): Promise<Blob> {
  const token = getAuthToken();
  const res = await fetch(`${API_BASE}/code-generation/${sessionId}/download`, {
    headers: { Authorization: token ? `Bearer ${token}` : '' },
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.blob();
}
