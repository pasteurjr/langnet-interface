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
  filename?: string;
}

/**
 * Get requirements document for a session
 */
export const getRequirementsDocument = async (sessionId: string): Promise<RequirementsDocument> => {
  const url = `${API_BASE}/documents/sessions/${sessionId}/requirements`;
  console.log('🌐 API: GET', url);

  try {
    const response = await axios.get<RequirementsDocument>(
      url,
      { headers: getAuthHeaders() }
    );

    console.log('🌐 API: Resposta recebida', {
      status: response.status,
      statusText: response.statusText,
      hasData: !!response.data,
      dataKeys: response.data ? Object.keys(response.data) : []
    });

    // Add filename based on session name
    const doc = response.data;

    console.log('🌐 API: Dados do documento', {
      session_id: doc.session_id,
      session_name: doc.session_name,
      status: doc.status,
      hasContent: !!doc.content,
      contentLength: doc.content?.length || 0,
      filename: doc.filename
    });

    if (!doc.filename) {
      const sessionName = doc.session_name || 'requisitos';
      doc.filename = `${sessionName.replace(/\s+/g, '_')}.md`;
      console.log('🌐 API: Filename gerado:', doc.filename);
    }

    return doc;
  } catch (error) {
    console.error('🌐 API: Erro na requisição', {
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

/**
 * Update requirements document (save edits)
 */
export const updateRequirementsDocument = async (
  sessionId: string,
  content: string
): Promise<{ success: boolean; message: string }> => {
  const url = `${API_BASE}/documents/sessions/${sessionId}/requirements`;
  console.log('💾 API: PUT', url, {
    contentLength: content.length,
    headers: getAuthHeaders()
  });

  try {
    const response = await axios.put(
      url,
      { content },
      { headers: getAuthHeaders() }
    );

    console.log('✅ API: Documento salvo com sucesso', response.data);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      console.error('❌ Token expirado! Fazendo logout...');
      alert('⚠️ Sessão expirada. Faça login novamente.');
      localStorage.removeItem('accessToken');
      window.location.href = '/login';
      throw new Error('Token expirado');
    }
    throw error;
  }
};

export default {
  getRequirementsDocument,
  updateRequirementsDocument
};
