/**
 * Document Service
 * Handles document upload, analysis, and requirements extraction
 */

import { Document, Requirement } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Get authentication token from localStorage
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
  };
};

/**
 * Upload document to server
 */
export const uploadDocument = async (
  file: File,
  projectId: number | string
): Promise<Document> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('project_id', String(projectId));

  const token = getAuthToken();

  console.log('🔑 Upload auth check:', {
    hasToken: !!token,
    tokenLength: token?.length || 0,
    tokenPreview: token ? `${token.substring(0, 20)}...` : 'null'
  });

  // Don't set Content-Type when using FormData - browser sets it automatically with boundary
  const headers: HeadersInit = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  console.log('📡 Sending upload request to:', `${API_BASE_URL}/documents/upload`);
  console.log('📋 Headers:', headers);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    headers: headers,
    body: formData,
  });

  console.log('📥 Upload response:', {
    status: response.status,
    statusText: response.statusText,
    ok: response.ok
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Upload failed:', error);

    // Extract detailed error message
    let errorMessage = 'Failed to upload document';
    if (error.detail) {
      if (Array.isArray(error.detail)) {
        // FastAPI validation errors are arrays
        errorMessage = error.detail.map((e: any) =>
          `${e.loc?.join('.')||'Field'}: ${e.msg}`
        ).join('; ');
      } else if (typeof error.detail === 'string') {
        errorMessage = error.detail;
      }
    }

    throw new Error(errorMessage);
  }

  return response.json();
};

/**
 * List documents with optional filtering
 */
export const listDocuments = async (
  projectId?: number,
  status?: string
): Promise<Document[]> => {
  const params = new URLSearchParams();
  if (projectId) params.append('project_id', projectId.toString());
  if (status) params.append('status', status);

  const queryString = params.toString();
  const url = `${API_BASE_URL}/documents/${queryString ? `?${queryString}` : ''}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch documents');
  }

  return response.json();
};

/**
 * Get single document by ID
 */
export const getDocument = async (documentId: number): Promise<Document> => {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch document');
  }

  return response.json();
};

/**
 * Analyze document and extract requirements
 */
export const analyzeDocument = async (
  documentId: number
): Promise<{
  document_id: number;
  status: string;
  analysis: {
    functional_requirements: any[];
    non_functional_requirements: any[];
    business_rules: any[];
    actors: any[];
    use_cases: any[];
  };
  requirements_extracted: number;
}> => {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/analyze`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to analyze document');
  }

  return response.json();
};

/**
 * Get requirements extracted from document
 */
export const getDocumentRequirements = async (
  documentId: number
): Promise<Requirement[]> => {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/requirements`, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch requirements');
  }

  return response.json();
};

/**
 * Update document metadata
 */
export const updateDocument = async (
  documentId: number,
  updates: {
    name?: string;
    status?: string;
  }
): Promise<Document> => {
  const formData = new FormData();
  if (updates.name) formData.append('name', updates.name);
  if (updates.status) formData.append('status', updates.status);

  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update document');
  }

  return response.json();
};

/**
 * Delete document
 */
export const deleteDocument = async (documentId: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: 'DELETE',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete document');
  }
};

/**
 * Batch upload multiple documents
 */
export const batchUploadDocuments = async (
  files: File[],
  projectId: number,
  onProgress?: (completed: number, total: number) => void
): Promise<Document[]> => {
  const uploadedDocuments: Document[] = [];
  let completed = 0;

  for (const file of files) {
    try {
      const document = await uploadDocument(file, projectId);
      uploadedDocuments.push(document);
      completed++;
      if (onProgress) {
        onProgress(completed, files.length);
      }
    } catch (error) {
      console.error(`Failed to upload ${file.name}:`, error);
      // Continue with remaining files
    }
  }

  return uploadedDocuments;
};

/**
 * Batch analyze multiple documents
 */
export const batchAnalyzeDocuments = async (
  documentIds: number[],
  onProgress?: (completed: number, total: number) => void
): Promise<any[]> => {
  const analyses: any[] = [];
  let completed = 0;

  for (const documentId of documentIds) {
    try {
      const analysis = await analyzeDocument(documentId);
      analyses.push(analysis);
      completed++;
      if (onProgress) {
        onProgress(completed, documentIds.length);
      }
    } catch (error) {
      console.error(`Failed to analyze document ${documentId}:`, error);
      // Continue with remaining documents
    }
  }

  return analyses;
};

/**
 * Get document statistics for a project
 */
export const getDocumentStats = async (
  projectId: number
): Promise<{
  total: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  total_requirements: number;
}> => {
  const documents = await listDocuments(projectId);

  const stats = {
    total: documents.length,
    by_status: {} as Record<string, number>,
    by_type: {} as Record<string, number>,
    total_requirements: 0,
  };

  documents.forEach(doc => {
    // Count by status
    stats.by_status[doc.status] = (stats.by_status[doc.status] || 0) + 1;

    // Count by type
    stats.by_type[doc.type] = (stats.by_type[doc.type] || 0) + 1;
  });

  // Get total requirements (would need to fetch all requirements or use a dedicated endpoint)
  // For now, we'll estimate based on analyzed documents
  const analyzedDocs = documents.filter(d => d.status === 'analyzed');
  for (const doc of analyzedDocs) {
    try {
      const requirements = await getDocumentRequirements(parseInt(doc.id.toString()));
      stats.total_requirements += requirements.length;
    } catch (error) {
      console.error(`Failed to fetch requirements for document ${doc.id}:`, error);
    }
  }

  return stats;
};

export default {
  uploadDocument,
  listDocuments,
  getDocument,
  analyzeDocument,
  getDocumentRequirements,
  updateDocument,
  deleteDocument,
  batchUploadDocuments,
  batchAnalyzeDocuments,
  getDocumentStats,
};
