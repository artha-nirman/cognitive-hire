'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authProvider, AuthUser } from '@/lib/auth/azure-b2c-provider';

export interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  getAccessToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  logout: async () => {},
  getAccessToken: async () => null,
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  
  useEffect(() => {
    const initAuth = async () => {
      try {
        await authProvider.initialize();
        const currentUser = await authProvider.getCurrentUser();
        setUser(currentUser);
      } catch (error) {
        console.error('Auth initialization error:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    initAuth();
  }, []);
  
  const login = async (): Promise<void> => {
    setIsLoading(true);
    try {
      const loggedInUser = await authProvider.signIn();
      setUser(loggedInUser);
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const logout = async (): Promise<void> => {
    try {
      await authProvider.signOut();
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };
  
  const getAccessToken = async (): Promise<string | null> => {
    return await authProvider.getAccessToken();
  };
  
  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    getAccessToken,
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
