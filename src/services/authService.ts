/**
 * Authentication service
 */
import api from './api';

export interface User {
  id: string;
  name: string;
  email: string;
  role?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  role?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/**
 * Login user
 */
export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>('/auth/login', credentials);

  // Store token and user in localStorage
  localStorage.setItem('accessToken', response.data.access_token);
  localStorage.setItem('user', JSON.stringify(response.data.user));

  return response.data;
};

/**
 * Register new user
 */
export const register = async (userData: RegisterRequest): Promise<User> => {
  const response = await api.post<User>('/auth/register', userData);
  return response.data;
};

/**
 * Logout user
 */
export const logout = (): void => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('user');
  window.location.href = '/login';
};

/**
 * Get current user from localStorage
 */
export const getCurrentUser = (): User | null => {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }
  return null;
};

/**
 * Get current user profile from API
 */
export const getMe = async (): Promise<User> => {
  const response = await api.get<User>('/auth/me');

  // Update user in localStorage
  localStorage.setItem('user', JSON.stringify(response.data));

  return response.data;
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  const token = localStorage.getItem('accessToken');
  return !!token;
};
