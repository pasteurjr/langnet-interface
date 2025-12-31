/**
 * Agents YAML Service
 * Handles API calls for agents.yaml generation
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getAuthToken = (): string | null => {
  return localStorage.getItem('accessToken') || localStorage.getItem('token');
};

const getAuthHeaders = (): HeadersInit => {
  const token = getAuthToken();
  return {
    'Authorization': token ? `Bearer ${token}` : '',
    'Content-Type': 'application/json',
  };
};

/**
 * Types for agents.yaml generation
 */
export interface GenerateAgentsYamlRequest {
  agent_task_spec_session_id: string;
  agent_task_spec_version?: number;
  custom_instructions?: string;
}

export interface AgentsYamlResponse {
  session_id: string;
  agents_yaml_content?: string;
  total_agents: number;
  status: string;
  message: string;
  generation_time_ms?: number;
  finished_at?: string;
}

export interface RefineRequest {
  message: string;
  action_type?: 'refine' | 'chat';
}

export interface ReviewResponse {
  review_message_id: string;
  suggestions: string;
  status: string;
  message: string;
}

/**
 * Generate agents.yaml from agent/task specification
 */
export const generateAgentsYaml = async (
  request: GenerateAgentsYamlRequest
): Promise<AgentsYamlResponse> => {
  console.log('🚀 Generating agents.yaml:', request);

  const response = await fetch(`${API_BASE_URL}/agents-yaml/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to generate agents.yaml:', error);
    throw new Error(error.detail || 'Failed to generate agents.yaml');
  }

  const result = await response.json();
  console.log('✅ Agents.yaml generation started:', result);
  return result;
};

/**
 * Get agents.yaml session status (for polling)
 */
export const getAgentsYamlSession = async (
  sessionId: string
): Promise<AgentsYamlResponse> => {
  const response = await fetch(`${API_BASE_URL}/agents-yaml/${sessionId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to get session:', error);
    throw new Error(error.detail || 'Failed to get session');
  }

  return response.json();
};

/**
 * Refine agents.yaml via chat
 */
export const refineAgentsYaml = async (
  sessionId: string,
  message: string
): Promise<any> => {
  console.log('✏️ Refining agents.yaml:', sessionId);

  const response = await fetch(`${API_BASE_URL}/agents-yaml/${sessionId}/refine`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      message,
      action_type: 'refine'
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to refine:', error);
    throw new Error(error.detail || 'Failed to refine agents.yaml');
  }

  const result = await response.json();
  console.log('✅ Refinement started:', result);
  return result;
};

/**
 * Review agents.yaml and get suggestions (SYNCHRONOUS)
 */
export const reviewAgentsYaml = async (
  sessionId: string
): Promise<ReviewResponse> => {
  console.log('🔍 Reviewing agents.yaml:', sessionId);

  const response = await fetch(`${API_BASE_URL}/agents-yaml/${sessionId}/review`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to review:', error);
    throw new Error(error.detail || 'Failed to review agents.yaml');
  }

  const result = await response.json();
  console.log('✅ Review completed:', result);
  return result;
};

/**
 * List all agents.yaml sessions for a project
 */
export const listAgentsYamlSessions = async (
  projectId: string
): Promise<{ sessions: any[]; total: number }> => {
  console.log('📋 Listing agents.yaml sessions for project:', projectId);

  const response = await fetch(`${API_BASE_URL}/agents-yaml/?project_id=${projectId}`, {
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
 * Get all versions for an agents.yaml session
 */
export const getAgentsYamlVersions = async (sessionId: string): Promise<any[]> => {
  const response = await fetch(`${API_BASE_URL}/agents-yaml/${sessionId}/versions`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to get versions:', error);
    throw new Error(error.detail || 'Failed to get versions');
  }

  return response.json();
};

/**
 * Get chat history for agents.yaml session
 */
export const getAgentsYamlChatHistory = async (
  sessionId: string
): Promise<{ messages: any[]; total: number }> => {
  const response = await fetch(`${API_BASE_URL}/agents-yaml/${sessionId}/chat-history`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to get chat history:', error);
    throw new Error(error.detail || 'Failed to get chat history');
  }

  return response.json();
};

/**
 * Export all functions
 */
export default {
  generateAgentsYaml,
  getAgentsYamlSession,
  refineAgentsYaml,
  reviewAgentsYaml,
  listAgentsYamlSessions,
  getAgentsYamlVersions,
  getAgentsYamlChatHistory,
};
