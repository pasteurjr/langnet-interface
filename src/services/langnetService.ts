/**
 * LangNet Service
 * Client for LangNet multi-agent system API
 */

import { useState, useEffect } from 'react';
import api from './api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

/**
 * Get authentication token
 */
const getAuthToken = (): string | null => {
  // Try 'accessToken' first (standard), fall back to 'token' for backwards compatibility
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

// ============================================================================
// TYPES
// ============================================================================

export interface ExecutionResponse {
  execution_id: string;
  status: string;
  message: string;
  started_at: string;
}

export interface ExecutionStatusResponse {
  execution_id: string;
  status: string;
  current_task: string | null;
  current_phase: string | null;
  progress_percentage: number;
  completed_tasks: number;
  total_tasks: number;
  errors: Array<any>;
  execution_log: Array<any>;
  started_at: string;
  completed_at: string | null;
}

export interface ExecutionResultResponse {
  execution_id: string;
  status: string;
  result: any;
  errors: Array<any>;
}

export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Execute full LangNet pipeline
 */
export const executeFullPipeline = async (
  projectId: string,
  documentId: string,
  documentPath: string,
  frameworkChoice: string = 'crewai'
): Promise<ExecutionResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/langnet/execute-full-pipeline`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      project_id: projectId,
      document_id: documentId,
      document_path: documentPath,
      framework_choice: frameworkChoice
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to execute pipeline');
  }

  return response.json();
};

/**
 * Execute document analysis workflow only
 */
export const analyzeDocument = async (
  documentId: string,
  documentPath: string
): Promise<ExecutionResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/langnet/analyze-document`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      document_id: documentId,
      document_path: documentPath
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to analyze document');
  }

  return response.json();
};

/**
 * Execute agent design workflow
 */
export const designAgents = async (
  requirementsData: any,
  specificationData: any
): Promise<ExecutionResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/langnet/design-agents`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      requirements_data: requirementsData,
      specification_data: specificationData
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to design agents');
  }

  return response.json();
};

/**
 * Get execution status
 */
export const getExecutionStatus = async (
  executionId: string
): Promise<ExecutionStatusResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/langnet/execution/${executionId}/status`, {
    method: 'GET',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get execution status');
  }

  return response.json();
};

/**
 * Get execution result
 */
export const getExecutionResult = async (
  executionId: string
): Promise<ExecutionResultResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/langnet/execution/${executionId}/result`, {
    method: 'GET',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get execution result');
  }

  return response.json();
};

/**
 * Save execution results to database
 */
export const saveExecutionResults = async (
  executionId: string
): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/api/langnet/save-results/${executionId}`, {
    method: 'POST',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to save results');
  }

  return response.json();
};

/**
 * Delete execution
 */
export const deleteExecution = async (executionId: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/api/langnet/execution/${executionId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete execution');
  }
};

/**
 * List available tasks
 */
export const listTasks = async (): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/api/langnet/tasks/list`, {
    method: 'GET',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to list tasks');
  }

  return response.json();
};

/**
 * List available agents
 */
export const listAgents = async (): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/api/langnet/agents/list`, {
    method: 'GET',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to list agents');
  }

  return response.json();
};

// ============================================================================
// WEBSOCKET
// ============================================================================

/**
 * Connect to execution WebSocket for real-time updates
 */
export const connectToExecutionWebSocket = (
  executionId: string,
  onMessage: (message: WebSocketMessage) => void,
  onError?: (error: Event) => void,
  onClose?: (event: CloseEvent) => void
): WebSocket => {
  const token = getAuthToken();
  const ws = new WebSocket(`${WS_BASE_URL}/ws/langnet/${executionId}`);

  ws.onopen = () => {
    console.log(`WebSocket connected for execution: ${executionId}`);
  };

  ws.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);
      onMessage(message);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) onError(error);
  };

  ws.onclose = (event) => {
    console.log('WebSocket closed:', event.code, event.reason);
    if (onClose) onClose(event);
  };

  return ws;
};

/**
 * Hook for WebSocket connection (React)
 */
export const useLangNetWebSocket = (
  executionId: string | null,
  enabled: boolean = true
) => {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [status, setStatus] = useState<string>('disconnected');
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    if (!executionId || !enabled) return;

    const websocket = connectToExecutionWebSocket(
      executionId,
      (message) => {
        setMessages((prev) => [...prev, message]);

        // Update status based on message type
        if (message.type === 'connected') {
          setStatus('connected');
        } else if (message.type === 'execution_completed') {
          setStatus('completed');
        } else if (message.type === 'execution_failed') {
          setStatus('failed');
        }
      },
      () => setStatus('error'),
      () => setStatus('disconnected')
    );

    setWs(websocket);
    setStatus('connecting');

    return () => {
      websocket.close();
    };
  }, [executionId, enabled]);

  return { messages, status, ws };
};

export default {
  executeFullPipeline,
  analyzeDocument,
  designAgents,
  getExecutionStatus,
  getExecutionResult,
  saveExecutionResults,
  deleteExecution,
  listTasks,
  listAgents,
  connectToExecutionWebSocket,

  // Document Analysis with LangNet (single document)
  analyzeDocumentWithLangNet: async (
    projectId: number,
    documentId: number,
    additionalInstructions: string,
    enableWebResearch: boolean = true
  ): Promise<string> => {
    const response = await api.post('/api/langnet/analyze-document', {
      project_id: projectId.toString(),
      document_id: documentId.toString(),
      additional_instructions: additionalInstructions,
      enable_web_research: enableWebResearch
    });
    return response.data.execution_id;
  },

  // Document Analysis with LangNet (multiple documents)
  analyzeDocumentsWithLangNet: async (
    projectId: number,
    documentIds: number[],
    additionalInstructions: string,
    enableWebResearch: boolean = true
  ): Promise<string> => {
    const response = await api.post('/api/langnet/analyze-documents', {
      project_id: projectId.toString(),
      document_ids: documentIds.map(id => id.toString()),
      additional_instructions: additionalInstructions,
      enable_web_research: enableWebResearch
    });
    return response.data.execution_id;
  },

  // Poll execution status until complete
  pollExecutionStatus: async (executionId: string, maxAttempts: number = 60): Promise<any> => {
    let attempts = 0;

    while (attempts < maxAttempts) {
      const response = await api.get(`/api/langnet/execution/${executionId}/status`);
      const status = response.data.status;

      if (status === 'completed') {
        return response.data;
      } else if (status === 'failed') {
        throw new Error(`Execution failed: ${response.data.error || 'Unknown error'}`);
      }

      // Wait 2 seconds before next poll
      await new Promise(resolve => setTimeout(resolve, 2000));
      attempts++;
    }

    throw new Error('Execution timeout - took longer than expected');
  },

  // Get requirements document
  getRequirementsDocument: async (executionId: string): Promise<string> => {
    const response = await api.get(`/api/langnet/execution/${executionId}/requirements-document`);
    return response.data.document;
  }
};
