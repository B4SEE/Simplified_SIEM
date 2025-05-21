import React, { createContext, useContext, useEffect, useState } from 'react';
import { checkAuthStatus } from '../api/auth';

type AuthState = {
  isLoading: boolean;
  isLoggedIn: boolean;
  token: string | null;
  userId: number | null;
  refresh: () => Promise<void>;
  logout: () => void;
  setAuthToken: (token: string | null) => void;
  setUserId: (id: number | null) => void;
};

const AuthContext = createContext<AuthState | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem('token')
  );
  const [userId, setUserId] = useState<number | null>(() => {
    const id = localStorage.getItem('user_id');
    return id ? Number(id) : null;
  });
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

  const setUserIdWrapper = (id: number | null) => {
    setUserId(id);
    if (id !== null) {
      localStorage.setItem('user_id', id.toString());
    } else {
      localStorage.removeItem('user_id');
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

  const login = (newToken: string, newUserId: number) => {
    localStorage.setItem('token', newToken);
    localStorage.setItem('userId', String(newUserId));
    setToken(newToken);
    setUserId(newUserId);
    setIsLoggedIn(true);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    setToken(null);
    setUserId(null);
    setIsLoggedIn(false);
  };

  useEffect(() => {
    refresh().finally(() => setIsLoading(false));
  }, [token]);

  const value = {
    isLoading,
    isLoggedIn,
    token,
    userId,
    refresh,
    logout,
    login,
    setAuthToken,
    setUserId: setUserIdWrapper,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
};
