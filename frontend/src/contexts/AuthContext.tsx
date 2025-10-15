import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi, type User, type LoginData, type RegisterData } from '../services/api';
import { isAuthenticated, clearAuthTokens } from '../services/api/client';
import { websocketService } from '../services/websocket';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (data: LoginData) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  /**
   * Fetch user profile
   */
  const fetchUser = useCallback(async () => {
    if (!isAuthenticated()) {
      setLoading(false);
      return;
    }

    try {
      const userData = await authApi.getProfile();
      setUser(userData);

      // Connect to WebSocket when user is loaded
      if (userData.id) {
        websocketService.connect(userData.id);
      }
    } catch (error) {
      console.error('Failed to fetch user:', error);
      clearAuthTokens();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Login user
   */
  const login = useCallback(async (data: LoginData) => {
    setLoading(true);
    try {
      const response = await authApi.login(data);
      setUser(response.user);

      // Connect to WebSocket
      if (response.user.id) {
        websocketService.connect(response.user.id);
      }
    } catch (error) {
      setLoading(false);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Register user
   */
  const register = useCallback(async (data: RegisterData) => {
    setLoading(true);
    try {
      const response = await authApi.register(data);
      setUser(response.user);

      // Connect to WebSocket
      if (response.user.id) {
        websocketService.connect(response.user.id);
      }
    } catch (error) {
      setLoading(false);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Disconnect WebSocket
      websocketService.disconnect();

      setUser(null);
      setLoading(false);
    }
  }, []);

  /**
   * Refresh user data
   */
  const refreshUser = useCallback(async () => {
    if (!isAuthenticated()) {
      return;
    }

    try {
      const userData = await authApi.getProfile();
      setUser(userData);
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  }, []);

  // Fetch user on mount
  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      websocketService.disconnect();
    };
  }, []);

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    refreshUser,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
