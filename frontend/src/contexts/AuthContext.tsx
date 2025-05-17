import React, { createContext, useContext, useEffect, useState } from 'react';
import { checkAuthStatus } from '../api/auth';

type AuthState = {
  isLoading: boolean;
  isLoggedIn: boolean;
  token: string | null;
  refresh: () => Promise<void>;
  logout: () => void;
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

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setIsLoggedIn(false);
  };

  useEffect(() => {
    refresh().finally(() => setIsLoading(false));
  }, []);

  const value: AuthState = { isLoading, isLoggedIn, token, refresh, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
};
