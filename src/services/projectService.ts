/**
 * Project service
 */
import api from './api';

export interface ProjectCreate {
  user_id: string;
  name: string;
  description?: string | null;
  domain?: string | null;
  framework?: string | null;
  default_llm?: string | null;
  memory_system?: string | null;
  start_from?: string;
  template?: string | null;
  status?: string;
}

export interface Project {
  id: string;
  user_id: string;
  name: string;
  description?: string | null;
  domain?: string | null;
  framework?: string | null;
  default_llm?: string | null;
  memory_system?: string | null;
  start_from?: string;
  template?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  last_modified_by?: string | null;
  project_data?: any;
  petri_net?: any;
  config?: any;
}

/**
 * Create a new project
 */
export const createProject = async (projectData: ProjectCreate): Promise<Project> => {
  const response = await api.post<Project>('/projects/', projectData);
  return response.data;
};

/**
 * Get all projects
 */
export const getAllProjects = async (userId?: string): Promise<Project[]> => {
  const params = userId ? { user_id: userId } : {};
  const response = await api.get<Project[]>('/projects/', { params });
  return response.data;
};

/**
 * Get projects (alias for getAllProjects)
 */
export const getProjects = getAllProjects;

/**
 * Get project by ID
 */
export const getProjectById = async (projectId: string): Promise<Project> => {
  const response = await api.get<Project>(`/projects/${projectId}`);
  return response.data;
};

/**
 * Update project
 */
export const updateProject = async (
  projectId: string,
  projectData: Partial<ProjectCreate>
): Promise<Project> => {
  const response = await api.patch<Project>(`/projects/${projectId}`, projectData);
  return response.data;
};

/**
 * Delete project
 */
export const deleteProject = async (projectId: string): Promise<void> => {
  await api.delete(`/projects/${projectId}`);
};

/**
 * Get project statistics
 */
export const getProjectStats = async (projectId: string): Promise<any> => {
  const response = await api.get(`/projects/${projectId}/stats`);
  return response.data;
};
