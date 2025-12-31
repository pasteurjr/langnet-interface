/**
 * Tasks YAML Service
 * Handles API calls for tasks.yaml generation
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
 * Types for tasks.yaml generation
 */
export interface GenerateTasksYamlRequest {
  agent_task_spec_session_id: string;
  agent_task_spec_version?: number;
  custom_instructions?: string;
}

export interface TasksYamlResponse {
  session_id: string;
  tasks_yaml_content?: string;
  total_tasks: number;
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
 * Generate tasks.yaml from agent/task specification
 */
export const generateTasksYaml = async (
  request: GenerateTasksYamlRequest
): Promise<TasksYamlResponse> => {
  console.log('🚀 Generating tasks.yaml:', request);

  const response = await fetch(`${API_BASE_URL}/tasks-yaml/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to generate tasks.yaml:', error);
    throw new Error(error.detail || 'Failed to generate tasks.yaml');
  }

  const result = await response.json();
  console.log('✅ Tasks.yaml generation started:', result);
  return result;
};

/**
 * Get tasks.yaml session status (for polling)
 */
export const getTasksYamlSession = async (
  sessionId: string
): Promise<TasksYamlResponse> => {
  const response = await fetch(`${API_BASE_URL}/tasks-yaml/${sessionId}`, {
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
 * Refine tasks.yaml via chat
 */
export const refineTasksYaml = async (
  sessionId: string,
  message: string
): Promise<any> => {
  console.log('✏️ Refining tasks.yaml:', sessionId);

  const response = await fetch(`${API_BASE_URL}/tasks-yaml/${sessionId}/refine`, {
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
    throw new Error(error.detail || 'Failed to refine tasks.yaml');
  }

  const result = await response.json();
  console.log('✅ Refinement started:', result);
  return result;
};

/**
 * Review tasks.yaml and get suggestions (SYNCHRONOUS)
 */
export const reviewTasksYaml = async (
  sessionId: string
): Promise<ReviewResponse> => {
  console.log('🔍 Reviewing tasks.yaml:', sessionId);

  const response = await fetch(`${API_BASE_URL}/tasks-yaml/${sessionId}/review`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to review:', error);
    throw new Error(error.detail || 'Failed to review tasks.yaml');
  }

  const result = await response.json();
  console.log('✅ Review completed:', result);
  return result;
};

/**
 * List all tasks.yaml sessions for a project
 */
export const listTasksYamlSessions = async (
  projectId: string
): Promise<{ sessions: any[]; total: number }> => {
  console.log('📋 Listing tasks.yaml sessions for project:', projectId);

  const response = await fetch(`${API_BASE_URL}/tasks-yaml/?project_id=${projectId}`, {
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
 * Get all versions for a tasks.yaml session
 */
export const getTasksYamlVersions = async (sessionId: string): Promise<any[]> => {
  const response = await fetch(`${API_BASE_URL}/tasks-yaml/${sessionId}/versions`, {
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
 * Get chat history for tasks.yaml session
 */
export const getTasksYamlChatHistory = async (
  sessionId: string
): Promise<{ messages: any[]; total: number }> => {
  const response = await fetch(`${API_BASE_URL}/tasks-yaml/${sessionId}/chat-history`, {
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
  generateTasksYaml,
  getTasksYamlSession,
  refineTasksYaml,
  reviewTasksYaml,
  listTasksYamlSessions,
  getTasksYamlVersions,
  getTasksYamlChatHistory,
};
