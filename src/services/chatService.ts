import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
};

export interface ChatMessage {
  id: string;
  session_id: string;
  task_execution_id?: string;
  agent_id?: string;
  sender_type: 'user' | 'agent' | 'system' | 'assistant';
  sender_name?: string;
  message_text: string;
  message_type: 'chat' | 'status' | 'progress' | 'result' | 'error' | 'warning' | 'info' | 'document';
  parent_message_id?: string;
  timestamp: string;
  sequence_number?: number;
  is_read: boolean;
  is_pinned: boolean;
  is_deleted: boolean;
  deleted_at?: string;
  metadata?: any;
}

export interface ChatMessagesResponse {
  messages: ChatMessage[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface CreateMessageRequest {
  sender_type: 'user' | 'agent' | 'system' | 'assistant';
  message_text: string;
  message_type?: 'chat' | 'status' | 'progress' | 'result' | 'error' | 'warning' | 'info' | 'document';
  task_execution_id?: string;
  agent_id?: string;
  sender_name?: string;
  parent_message_id?: string;
  metadata?: any;
}

export interface RefineRequirementsRequest {
  message: string;
  parent_message_id?: string;
}

export interface RefineRequirementsResponse {
  user_message_id: string;
  agent_message: ChatMessage;
  status: string;
  message: string;
}

/**
 * Carrega mensagens de chat de uma sessão
 */
export const loadChatMessages = async (
  sessionId: string,
  page: number = 1,
  pageSize: number = 50,
  messageType?: string
): Promise<ChatMessagesResponse> => {
  const params: any = { page, page_size: pageSize };
  if (messageType) params.message_type = messageType;

  const response = await axios.get<ChatMessagesResponse>(
    `${API_BASE}/chat/sessions/${sessionId}/messages`,
    { params }
  );
  return response.data;
};

/**
 * Cria uma nova mensagem de chat
 */
export const createChatMessage = async (
  sessionId: string,
  message: CreateMessageRequest
): Promise<ChatMessage> => {
  const response = await axios.post<ChatMessage>(
    `${API_BASE}/chat/sessions/${sessionId}/messages`,
    message
  );
  return response.data;
};

/**
 * Envia mensagem de refinamento conversacional
 */
export const refineRequirements = async (
  sessionId: string,
  request: RefineRequirementsRequest
): Promise<RefineRequirementsResponse> => {
  const response = await axios.post<RefineRequirementsResponse>(
    `${API_BASE}/chat/sessions/${sessionId}/refine`,
    request,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Busca uma mensagem específica
 */
export const getChatMessage = async (messageId: string): Promise<ChatMessage> => {
  const response = await axios.get<ChatMessage>(
    `${API_BASE}/chat/messages/${messageId}`
  );
  return response.data;
};

/**
 * Atualiza uma mensagem (marca como lida, pina, edita texto, etc)
 */
export const updateChatMessage = async (
  messageId: string,
  updates: {
    message_text?: string;
    is_read?: boolean;
    is_pinned?: boolean;
    metadata?: any;
  }
): Promise<ChatMessage> => {
  const response = await axios.patch<ChatMessage>(
    `${API_BASE}/chat/messages/${messageId}`,
    updates
  );
  return response.data;
};

/**
 * Deleta uma mensagem (soft delete por padrão)
 */
export const deleteChatMessage = async (
  messageId: string,
  permanent: boolean = false
): Promise<{ message: string; permanent: boolean }> => {
  const response = await axios.delete(
    `${API_BASE}/chat/messages/${messageId}`,
    { params: { permanent } }
  );
  return response.data;
};

/**
 * Busca threads/respostas de uma mensagem
 */
export const getChatThreads = async (messageId: string): Promise<ChatMessage[]> => {
  const response = await axios.get<ChatMessage[]>(
    `${API_BASE}/chat/messages/${messageId}/threads`
  );
  return response.data;
};

export interface SessionStatus {
  session_id: string;
  session_name: string;
  project_id: string;
  status: 'running' | 'completed' | 'failed' | 'cancelled' | 'paused' | 'processing';
  requirements_document: string;
  doc_size: number;
  started_at: string | null;
  finished_at: string | null;
  created_at: string | null;
}

/**
 * Busca status da sessão e documento atualizado
 */
export const getSessionStatus = async (sessionId: string): Promise<SessionStatus> => {
  const response = await axios.get<SessionStatus>(
    `${API_BASE}/chat/sessions/${sessionId}/status`
  );
  return response.data;
};
