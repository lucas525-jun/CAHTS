import apiClient, { setAuthTokens, clearAuthTokens } from './client';

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  tokens: {
    access: string;
    refresh: string;
  };
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
}

export const authApi = {
  /**
   * Register a new user
   */
  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/register/', data);
    const { tokens } = response.data;
    setAuthTokens(tokens.access, tokens.refresh);
    return response.data;
  },

  /**
   * Login user
   */
  login: async (data: LoginData): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login/', data);
    const { tokens } = response.data;
    setAuthTokens(tokens.access, tokens.refresh);
    return response.data;
  },

  /**
   * Logout user
   */
  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/auth/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearAuthTokens();
    }
  },

  /**
   * Get current user profile
   */
  getProfile: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me/');
    return response.data;
  },

  /**
   * Refresh access token
   */
  refreshToken: async (refreshToken: string): Promise<{ access: string }> => {
    const response = await apiClient.post<{ access: string }>('/auth/refresh/', {
      refresh: refreshToken,
    });
    return response.data;
  },
};

export default authApi;
