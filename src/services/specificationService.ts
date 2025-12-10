/**
 * Specification Service
 * Handles functional specification generation, refinement, and versioning
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
 * Types for specification
 */
export interface CreateSpecificationRequest {
  project_id: string;
  requirements_session_id: string;
  requirements_version: number;
  complementary_document_ids?: string[];
  session_name?: string;
  detail_level?: 'basic' | 'detailed' | 'comprehensive';
  target_audience?: 'technical' | 'business' | 'mixed';
  include_data_model?: boolean;
  include_use_cases?: boolean;
  include_business_rules?: boolean;
  include_glossary?: boolean;
  custom_instructions?: string;
}

export interface SpecificationSession {
  id: string;
  project_id: string;
  user_id: string;
  requirements_session_id: string;
  requirements_version: number;
  session_name: string;
  started_at: string;
  finished_at?: string;
  status: 'generating' | 'completed' | 'failed' | 'cancelled' | 'paused' | 'reviewing';
  specification_document?: string;
  generation_log?: string;
  execution_metadata?: string;
  generation_time_ms?: number;
  ai_model_used?: string;
  total_sections: number;
  approval_status: 'pending' | 'approved' | 'needs_revision' | 'rejected';
  approved_by?: string;
  approved_at?: string;
  approval_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface SpecificationVersion {
  specification_session_id: string;
  version: number;
  specification_document: string;
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

export interface RefineSpecificationRequest {
  message: string;
  parent_message_id?: string;
}

export interface UpdateSpecificationRequest {
  content: string;
}

/**
 * Create a new specification generation session
 */
export const createSpecificationSession = async (
  request: CreateSpecificationRequest
): Promise<{ session_id: string; status: string; message: string }> => {
  console.log('📡 Creating specification session:', request);

  const response = await fetch(`${API_BASE_URL}/specifications/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Failed to create specification session:', error);
    throw new Error(error.detail || 'Failed to create specification session');
  }

  const result = await response.json();
  console.log('✅ Specification session created:', result);
  return result;
};

/**
 * List specification sessions with optional filtering
 */
export const listSpecifications = async (
  projectId?: string,
  status?: string,
  limit: number = 50,
  offset: number = 0
): Promise<{ sessions: SpecificationSession[]; total: number }> => {
  const params = new URLSearchParams();
  if (projectId) params.append('project_id', projectId);
  if (status) params.append('status', status);
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());

  const queryString = params.toString();
  const url = `${API_BASE_URL}/specifications/${queryString ? `?${queryString}` : ''}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch specifications');
  }

  return response.json();
};

/**
 * Get single specification session
 */
export const getSpecification = async (
  sessionId: string
): Promise<SpecificationSession> => {
  const response = await fetch(`${API_BASE_URL}/specifications/${sessionId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch specification');
  }

  return response.json();
};

/**
 * Update specification (manual edit)
 */
export const updateSpecification = async (
  sessionId: string,
  request: UpdateSpecificationRequest
): Promise<{ message: string; version: number }> => {
  const response = await fetch(`${API_BASE_URL}/specifications/${sessionId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update specification');
  }

  return response.json();
};

/**
 * List all versions of a specification
 */
export const listSpecificationVersions = async (
  sessionId: string
): Promise<{ versions: SpecificationVersion[] }> => {
  const response = await fetch(`${API_BASE_URL}/specifications/${sessionId}/versions`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch specification versions');
  }

  return response.json();
};

/**
 * Get specific version of a specification
 */
export const getSpecificationVersion = async (
  sessionId: string,
  version: number
): Promise<SpecificationVersion> => {
  const response = await fetch(`${API_BASE_URL}/specifications/${sessionId}/versions/${version}`, {
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
 * Refine specification via chat
 */
export const refineSpecification = async (
  sessionId: string,
  request: RefineSpecificationRequest
): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/specifications/${sessionId}/refine`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to refine specification');
  }

  return response.json();
};

/**
 * Export all specification service functions
 */
export default {
  createSpecificationSession,
  listSpecifications,
  getSpecification,
  updateSpecification,
  listSpecificationVersions,
  getSpecificationVersion,
  refineSpecification,
};
