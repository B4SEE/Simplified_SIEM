import React, { createContext, useContext, useEffect, useState } from 'react';
import { checkAuthStatus } from '../api/auth';

type AuthState = {
  isLoading: boolean;
  isLoggedIn: boolean;
  token: string | null;
  refresh: () => Promise<void>;
  logout: () => void;
  setAuthToken: (token: string | null) => void;
};

const AuthContext = createContext<AuthState | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem('token')
  );
  const [isLoading, setIsLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const setAuthToken = (newToken: string | null) => {
    setToken(newToken);
    if (newToken) {
      localStorage.setItem('token', newToken);
    } else {
      localStorage.removeItem('token');
    }
  };

  const refresh = async () => {
    if (!token) {
      setIsLoggedIn(false);
      return;
    }
    try {
      await checkAuthStatus();
      setIsLoggedIn(true);
    } catch {
      localStorage.removeItem('token');
      setToken(null);
      setIsLoggedIn(false);
    }
  };

  const login = (newToken: string) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setIsLoggedIn(true);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setIsLoggedIn(false);
  };

  useEffect(() => {
    refresh().finally(() => setIsLoading(false));
  }, [token]);

  const value = {
    isLoading,
    isLoggedIn,
    token,
    refresh,
    logout,
    login,
    setAuthToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
};
