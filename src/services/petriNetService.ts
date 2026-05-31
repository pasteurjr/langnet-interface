/**
 * Petri Net Service
 * Comunicação com /api/petri-net/* — gera, lê e atualiza a Rede de Petri
 * armazenada em projects.project_data.
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

export interface GeneratePetriNetPayload {
  agentsYamlSessionId: string;
  tasksYamlSessionId: string;
  taskExecutionFlowSessionId?: string;
}

export interface PetriNetData {
  nome: string;
  lugares: any[];
  transicoes: any[];
  arcos: any[];
  agentes: any[];
  [k: string]: any;
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

export async function generatePetriNet(
  projectId: string,
  payload: GeneratePetriNetPayload,
): Promise<PetriNetData> {
  const res = await fetch(`${API_BASE}/petri-net/${projectId}/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      agents_yaml_session_id: payload.agentsYamlSessionId,
      tasks_yaml_session_id: payload.tasksYamlSessionId,
      task_execution_flow_session_id: payload.taskExecutionFlowSessionId,
    }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  const body = await res.json();
  return body.petri_net as PetriNetData;
}

export async function getPetriNet(projectId: string): Promise<PetriNetData | null> {
  const res = await fetch(`${API_BASE}/petri-net/${projectId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(await parseError(res));
  const body = await res.json();
  return (body.petri_net as PetriNetData) ?? null;
}

export async function updatePetriNet(
  projectId: string,
  petriNet: PetriNetData,
): Promise<void> {
  const res = await fetch(`${API_BASE}/petri-net/${projectId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({ petri_net: petriNet }),
  });
  if (!res.ok) throw new Error(await parseError(res));
}
