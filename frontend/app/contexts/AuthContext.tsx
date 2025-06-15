'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { setupAxiosInterceptors, isTokenExpired, isValidToken } from '../utils/auth';

interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (token: string, userId: string) => void;
  logout: () => void;
  checkAuth: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Setup axios interceptors on mount
  useEffect(() => {
    setupAxiosInterceptors();
  }, []);

  const checkAuth = async (): Promise<boolean> => {
    try {
      const token = localStorage.getItem('access_token');
      const userId = localStorage.getItem('user_id');

      if (!token || !userId || !isValidToken(token)) {
        return false;
      }

      // Check if token is expired
      if (isTokenExpired(token)) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_id');
        return false;
      }

      // Verify token by making a request to /api/auth/me
      const response = await axios.get('http://localhost:8000/api/auth/me');
      const userData = response.data;

      setUser({
        id: userData.id,
        email: userData.email,
        name: userData.name,
        picture: userData.picture,
      });

      return true;
    } catch (error) {
      console.error('Auth check failed:', error);
      // Clear invalid tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_id');
      setUser(null);
      return false;
    }
  };

  const login = (token: string, userId: string) => {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user_id', userId);
    
    // Fetch user data
    axios.get('http://localhost:8000/api/auth/me')
      .then(response => {
        const userData = response.data;
        setUser({
          id: userData.id,
          email: userData.email,
          name: userData.name,
          picture: userData.picture,
        });
      })
      .catch(error => {
        console.error('Failed to fetch user data:', error);
        logout();
      });
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_id');
    setUser(null);
    router.push('/login');
  };

  useEffect(() => {
    const initializeAuth = async () => {
      await checkAuth();
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 