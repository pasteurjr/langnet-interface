import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export interface AnalyzeDocumentsRequest {
  document_ids: string[];
  project_id: string;
  instructions?: string;
  use_web_research: boolean;
}

export interface AnalyzeDocumentsResponse {
  session_id: string;
  execution_id: string;
  status: string;
  message: string;
  websocket_url: string;
}

/**
 * Inicia análise em batch de múltiplos documentos
 * Cria uma sessão de chat e retorna o ID para acompanhamento via WebSocket
 */
export const analyzeDocumentsBatch = async (
  request: AnalyzeDocumentsRequest
): Promise<AnalyzeDocumentsResponse> => {
  const token = localStorage.getItem('accessToken');
  const response = await axios.post<AnalyzeDocumentsResponse>(
    `${API_BASE}/documents/analyze-batch`,
    request,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.data;
};

/**
 * Conecta ao WebSocket de execução para receber atualizações em tempo real
 */
export const connectToExecutionWebSocket = (
  executionId: string,
  onMessage: (data: any) => void,
  onError?: (error: Event) => void,
  onClose?: (event: CloseEvent) => void
): WebSocket => {
  const WS_BASE = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
  const ws = new WebSocket(`${WS_BASE}/ws/execution/${executionId}`);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  };

  if (onError) {
    ws.onerror = onError;
  }

  if (onClose) {
    ws.onclose = onClose;
  }

  return ws;
};
