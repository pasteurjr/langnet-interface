import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
};

export interface RequirementsDocument {
  session_id: string;
  session_name: string;
  status: string;
  content: string;
}

/**
 * Get requirements document for a session
 */
export const getRequirementsDocument = async (sessionId: string): Promise<RequirementsDocument> => {
  const response = await axios.get<RequirementsDocument>(
    `${API_BASE}/documents/sessions/${sessionId}/requirements`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Update requirements document (save edits)
 */
export const updateRequirementsDocument = async (
  sessionId: string,
  content: string
): Promise<{ success: boolean; message: string }> => {
  const response = await axios.put(
    `${API_BASE}/documents/sessions/${sessionId}/requirements`,
    { content },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

export default {
  getRequirementsDocument,
  updateRequirementsDocument
};
