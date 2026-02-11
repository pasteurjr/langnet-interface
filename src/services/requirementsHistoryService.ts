import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
};

export interface SessionSummary {
  id: string;
  session_name: string;
  status: string;
  created_at: string;
  finished_at: string | null;
  doc_size: number;
}

export interface SessionsListResponse {
  sessions: SessionSummary[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * List all execution sessions that have generated requirements documents
 *
 * @param projectId - Filter by project ID (optional)
 * @param limit - Maximum number of sessions
 * @param offset - Pagination offset
 */
export const listSessions = async (
  projectId?: string,
  limit: number = 50,
  offset: number = 0
): Promise<SessionsListResponse> => {
  // Build URL with optional project filter
  let url = `${API_BASE}/documents/sessions?limit=${limit}&offset=${offset}`;

  if (projectId) {
    url += `&project_id=${projectId}`;
  }

  console.log('📜 API: GET', url);

  try {
    const response = await axios.get<SessionsListResponse>(
      url,
      { headers: getAuthHeaders() }
    );

    console.log('📜 API: Sessions list received', {
      status: response.status,
      total: response.data.total,
      sessionCount: response.data.sessions.length,
      projectId: projectId || 'all'
    });

    return response.data;
  } catch (error) {
    console.error('📜 API: Error fetching sessions', {
      url,
      error: error instanceof Error ? error.message : String(error),
      isAxiosError: axios.isAxiosError(error),
      response: axios.isAxiosError(error) ? {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      } : undefined
    });
    throw error;
  }
};

export default {
  listSessions
};
