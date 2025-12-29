/**
 * Agent Task Service
 * Handles API calls for unified agent and task generation
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Get authentication token from localStorage
 */
const getAuthToken = (): string | null => {
  return localStorage.getItem('accessToken') || localStorage.getItem('token');
};

/**
 * Create authorization headers
 */
const getAuthHeaders = (): HeadersInit => {
  const token = getAuthToken();
  return {
    'Authorization': token ? `Bearer ${token}` : '',
    'Content-Type': 'application/json',
  };
};

/**
 * Types for agent/task generation
 */
export interface GenerateRequest {
  specification_session_id?: string;
  agent_task_spec_session_id?: string;
  specification_version?: number;
  detail_level?: 'concise' | 'balanced' | 'detailed';
  frameworks?: string[];
  max_agents?: number;
  custom_instructions?: string;
  auto_generate_yaml?: boolean;
}

export interface AgentData {
  name: string;
  role: string;
  goal: string;
  backstory: string;
  tools: string[];
  verbose?: boolean;
  allow_delegation?: boolean;
  delegation_targets?: string[];
  rationale?: string;
}

export interface TaskData {
  name: string;
  description: string;
  agent_id: string;
  expected_output: string;
  inputs?: Record<string, any>;
  outputs?: Record<string, any>;
  dependencies?: string[];
  parallel_execution?: string[];
  rationale?: string;
}

export interface GenerateResponse {
  session_id: string;
  agents: AgentData[];
  tasks: TaskData[];
  agents_yaml: string;
  tasks_yaml: string;
  dependency_graph?: any;
  status: string;
  message: string;
}

export interface RefineRequest {
  message: string;
  action_type?: 'refine' | 'chat';
}

export interface RefineResponse {
  session_id: string;
  refined_agents: AgentData[];
  refined_tasks: TaskData[];
  agents_yaml?: string;
  tasks_yaml?: string;
  refinement_summary: string;
  status: string;
  message: string;
}

export interface SessionStatusResponse {
  session_id: string;
  status: 'draft' | 'generating' | 'completed' | 'failed';
  total_agents_generated: number;
  total_tasks_generated: number;
  agents_yaml_content?: string;
  tasks_yaml_content?: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  sender_type: 'user' | 'agent' | 'system';
  message_text: string;
  message_type: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface ChatHistoryResponse {
  messages: ChatMessage[];
  total: number;
}

/**
 * Generate agents and tasks from specification
 */
export const generateAgentsAndTasks = async (
  request: GenerateRequest
): Promise<GenerateResponse> => {
  console.log('🚀 Generating agents and tasks:', request.specification_session_id);

  const response = await fetch(`${API_BASE_URL}/agent-task/generate`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to generate agents/tasks:', error);
    throw new Error(error.detail || 'Failed to generate agents and tasks');
  }

  const result = await response.json();
  console.log('✅ Agents and tasks generated:', result);
  return result;
};

/**
 * Refine agents/tasks via chat
 */
export const refineAgentsAndTasks = async (
  sessionId: string,
  refinementMessage: string
): Promise<RefineResponse> => {
  console.log('✏️ Refining session:', sessionId);

  const response = await fetch(`${API_BASE_URL}/agent-task/refine`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      session_id: sessionId,
      refinement_message: refinementMessage
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to refine:', error);
    throw new Error(error.detail || 'Failed to refine agents/tasks');
  }

  const result = await response.json();
  console.log('✅ Refinement completed:', result);
  return result;
};

/**
 * List all agent/task sessions for a project
 */
export const listAgentTaskSessions = async (
  projectId: string
): Promise<{ sessions: any[]; total: number }> => {
  console.log('📋 Listing agent/task sessions for project:', projectId);

  const response = await fetch(`${API_BASE_URL}/agent-task/sessions?project_id=${projectId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to list sessions:', error);
    throw new Error(error.detail || 'Failed to list sessions');
  }

  const result = await response.json();
  console.log('✅ Sessions listed:', result);
  return result;
};

/**
 * Get specific agent/task session
 */
export const getAgentTaskSession = async (
  sessionId: string
): Promise<GenerateResponse> => {
  console.log('🔍 Getting agent/task session:', sessionId);

  const response = await fetch(`${API_BASE_URL}/agent-task/sessions/${sessionId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to get session:', error);
    throw new Error(error.detail || 'Failed to get session');
  }

  const result = await response.json();
  console.log('✅ Session retrieved:', result);
  return result;
};

/**
 * Get session status (deprecated - use getAgentTaskSession instead)
 */
export const getSessionStatus = async (
  sessionId: string
): Promise<SessionStatusResponse> => {
  const response = await fetch(`${API_BASE_URL}/agent-task/sessions/${sessionId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get session status');
  }

  return response.json();
};

/**
 * Get chat history
 */
export const getChatHistory = async (
  sessionId: string
): Promise<ChatHistoryResponse> => {
  const response = await fetch(`${API_BASE_URL}/agent-task/${sessionId}/chat-history`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get chat history');
  }

  return response.json();
};

/**
 * Export YAMLs as ZIP
 */
export const exportYamlsAsZip = async (
  sessionId: string
): Promise<Blob> => {
  console.log('💾 Exporting YAMLs as ZIP:', sessionId);

  const response = await fetch(`${API_BASE_URL}/agent-task/${sessionId}/export`, {
    method: 'GET',
    headers: {
      'Authorization': getAuthToken() ? `Bearer ${getAuthToken()}` : '',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to export:', error);
    throw new Error(error.detail || 'Failed to export YAMLs');
  }

  const blob = await response.blob();
  console.log('✅ YAMLs exported');
  return blob;
};

/**
 * Download exported YAMLs
 */
export const downloadYamlsZip = async (sessionId: string, filename: string = 'agents-tasks.zip') => {
  const blob = await exportYamlsAsZip(sessionId);
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};

/**
 * Review agent/task specification response
 */
export interface ReviewAgentTaskSpecResponse {
  review_message_id: string;
  suggestions: string;  // Markdown
  status: string;
  message: string;
}

/**
 * Review agent/task specification document
 * Returns structured suggestions for improvement
 * IMPORTANT: Review is SYNCHRONOUS - returns immediately with suggestions
 */
export const reviewAgentTaskSpec = async (
  sessionId: string
): Promise<ReviewAgentTaskSpecResponse> => {
  console.log('🔍 Sending review request:', sessionId);

  const response = await fetch(`${API_BASE_URL}/agent-task-spec/${sessionId}/review`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to review:', error);
    throw new Error(error.detail || 'Failed to review specification');
  }

  const result = await response.json();
  console.log('✅ Review completed:', result);

  // IMPORTANTE: Review é SÍNCRONO - retorna imediatamente com as sugestões
  // NÃO precisa de polling (diferente do refinement)
  return result;
};

/**
 * Export all functions
 */
export default {
  generateAgentsAndTasks,
  refineAgentsAndTasks,
  listAgentTaskSessions,
  getAgentTaskSession,
  getSessionStatus,
  getChatHistory,
  exportYamlsAsZip,
  downloadYamlsZip,
  reviewAgentTaskSpec,
};
