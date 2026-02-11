/**
 * Task Execution Flow Service
 * Handles task execution flow document generation, refinement, and versioning
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
 * Types for task execution flow
 */
export interface CreateTaskExecutionFlowRequest {
  specification_session_id: string;
  agent_task_spec_session_id: string;
  tasks_yaml_session_id: string;
  uploaded_document_ids?: string[];
  custom_instructions?: string;
}

export interface TaskExecutionFlowSession {
  id: string;
  project_id: string;
  user_id: string;
  specification_session_id: string;
  agent_task_spec_session_id: string;
  tasks_yaml_session_id: string;
  uploaded_document_ids?: string[];
  session_name: string;
  started_at: string;
  finished_at?: string;
  status: 'generating' | 'completed' | 'failed';
  flow_document?: string;
  current_version?: number;
  total_tasks: number;
  has_parallelism: boolean;
  generation_log?: string;
  execution_metadata?: string;
  generation_time_ms?: number;
  ai_model_used?: string;
  created_at: string;
  updated_at: string;
}

export interface TaskExecutionFlowVersion {
  session_id: string;
  version: number;
  flow_document: string;
  created_at: string;
  created_by?: string;
  change_type: 'initial_generation' | 'ai_refinement' | 'manual_edit' | 'approval_revision' | 'feedback_incorporation';
  change_description?: string;
  section_changes?: string;
  doc_size?: number;
  review_notes?: string;
  reviewed_by?: string;
  reviewed_at?: string;
  is_approved_version: boolean;
}

export interface RefineTaskExecutionFlowRequest {
  message: string;
  action_type?: string;
}

export interface UpdateTaskExecutionFlowRequest {
  content: string;
}

/**
 * Create a new task execution flow generation session
 */
export const createTaskExecutionFlowSession = async (
  request: CreateTaskExecutionFlowRequest
): Promise<{ session_id: string; status: string; message: string }> => {
  console.log('📡 Creating task execution flow session:', request);

  const response = await fetch(`${API_BASE_URL}/task-execution-flow/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to create task execution flow session:', error);
    throw new Error(error.detail || 'Failed to create task execution flow session');
  }

  const result = await response.json();
  console.log('✅ Task execution flow session created:', result);
  return result;
};

/**
 * List task execution flow sessions
 */
export const listTaskExecutionFlows = async (
  projectId: string
): Promise<{ sessions: TaskExecutionFlowSession[]; total: number }> => {
  const response = await fetch(`${API_BASE_URL}/task-execution-flow/?project_id=${projectId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch task execution flows');
  }

  return response.json();
};

/**
 * Get single task execution flow session
 */
export const getTaskExecutionFlow = async (
  sessionId: string
): Promise<TaskExecutionFlowSession> => {
  const response = await fetch(`${API_BASE_URL}/task-execution-flow/${sessionId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch task execution flow');
  }

  return response.json();
};

/**
 * Get session status for polling (lightweight)
 */
export const getSessionStatus = async (
  sessionId: string
): Promise<{
  status: 'generating' | 'completed' | 'failed';
  flow_document?: string;
  current_version?: number;
}> => {
  const response = await fetch(`${API_BASE_URL}/task-execution-flow/${sessionId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get session status');
  }

  const data = await response.json();
  return {
    status: data.status,
    flow_document: data.flow_document,
    current_version: 1 // Task execution flow doesn't have versioning yet
  };
};

/**
 * Update task execution flow (manual edit)
 */
export const updateTaskExecutionFlow = async (
  sessionId: string,
  request: UpdateTaskExecutionFlowRequest
): Promise<{ message: string; version: number }> => {
  const response = await fetch(`${API_BASE_URL}/task-execution-flow/${sessionId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update task execution flow');
  }

  return response.json();
};

/**
 * List all versions of a task execution flow
 */
export const listTaskExecutionFlowVersions = async (
  sessionId: string
): Promise<{ versions: TaskExecutionFlowVersion[] }> => {
  const response = await fetch(`${API_BASE_URL}/task-execution-flow/${sessionId}/versions`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch task execution flow versions');
  }

  return response.json();
};

/**
 * Get specific version of a task execution flow
 */
export const getTaskExecutionFlowVersion = async (
  sessionId: string,
  version: number
): Promise<TaskExecutionFlowVersion> => {
  const response = await fetch(`${API_BASE_URL}/task-execution-flow/${sessionId}/versions/${version}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Failed to fetch version ${version}`);
  }

  return response.json();
};

/**
 * Refine task execution flow via chat
 */
export const refineTaskExecutionFlow = async (
  sessionId: string,
  request: RefineTaskExecutionFlowRequest
): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/task-execution-flow/${sessionId}/refine`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to refine task execution flow');
  }

  return response.json();
};

/**
 * Review task execution flow
 */
export const reviewTaskExecutionFlow = async (
  sessionId: string
): Promise<{ suggestions: string; review_message_id?: string }> => {
  const response = await fetch(`${API_BASE_URL}/task-execution-flow/${sessionId}/review`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to review task execution flow');
  }

  return response.json();
};

/**
 * Get chat history for a session
 */
export const getChatHistory = async (
  sessionId: string
): Promise<{ messages: any[] }> => {
  const response = await fetch(`${API_BASE_URL}/task-execution-flow/${sessionId}/chat-history`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch chat history');
  }

  return response.json();
};

/**
 * Export all task execution flow service functions
 */
export default {
  createTaskExecutionFlowSession,
  listTaskExecutionFlows,
  getTaskExecutionFlow,
  getSessionStatus,
  updateTaskExecutionFlow,
  listTaskExecutionFlowVersions,
  getTaskExecutionFlowVersion,
  refineTaskExecutionFlow,
  reviewTaskExecutionFlow,
  getChatHistory,
};
