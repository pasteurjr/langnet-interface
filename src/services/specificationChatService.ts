/**
 * Specification Chat Service
 * Handles chat-based refinement for functional specifications
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
 * Types for chat service
 */
export interface RefineSpecificationRequest {
  message: string;
  action_type?: 'refine' | 'chat';  // 'refine' modifies document, 'chat' only analyzes
  parent_message_id?: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  sender_type: 'user' | 'agent' | 'system';
  message_text: string;
  message_type: string;
  sender_name?: string;
  parent_message_id?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface RefineResponse {
  user_message_id: string;
  agent_message: ChatMessage;
  status: string;
  message: string;
}

export interface ChatHistoryResponse {
  messages: ChatMessage[];
  total: number;
}

export interface SessionStatusResponse {
  session_id: string;
  session_name: string;
  status: string;
  specification_document: string;
  doc_size: number;
  current_version: number;
  requirements_session_id: string;
  requirements_version: number;
  started_at: string | null;
  finished_at: string | null;
  updated_at: string | null;
}

/**
 * Send refinement request for specification
 */
export const refineSpecification = async (
  sessionId: string,
  request: RefineSpecificationRequest
): Promise<RefineResponse> => {
  console.log('📡 Sending specification refinement request:', sessionId);

  const response = await fetch(`${API_BASE_URL}/specifications/${sessionId}/refine`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to refine specification:', error);
    throw new Error(error.detail || 'Failed to refine specification');
  }

  const result = await response.json();
  console.log('✅ Refinement request sent:', result);
  return result;
};

/**
 * Get chat history for specification session
 */
export const getChatHistory = async (
  sessionId: string
): Promise<ChatHistoryResponse> => {
  const response = await fetch(`${API_BASE_URL}/specifications/${sessionId}/chat-history`, {
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
 * Get specification session status
 */
export const getSessionStatus = async (
  sessionId: string
): Promise<SessionStatusResponse> => {
  const response = await fetch(`${API_BASE_URL}/specifications/${sessionId}/status`, {
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
 * Analyze specification without modifying it (chat mode)
 * Convenience function that calls refineSpecification with action_type='chat'
 */
export const analyzeSpecification = async (
  sessionId: string,
  question: string,
  parentMessageId?: string
): Promise<RefineResponse> => {
  return refineSpecification(sessionId, {
    message: question,
    action_type: 'chat',
    parent_message_id: parentMessageId,
  });
};

/**
 * Export all functions
 */
export default {
  refineSpecification,
  analyzeSpecification,
  getChatHistory,
  getSessionStatus,
};
