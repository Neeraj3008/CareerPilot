import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, CandidateProfile } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  token: string | null;
  user: User | null;
  profile: CandidateProfile | null;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (email: string, pass: string, name: string) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('careerpilot_token'));
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshProfile = async () => {
    try {
      const prof = await api.profile.get();
      setProfile(prof);
    } catch (e) {
      console.error('Failed to load profile', e);
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const userData = await api.auth.getMe();
          setUser(userData);
          await refreshProfile();
        } catch (e) {
          console.error('Session expired or invalid', e);
          logout();
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, [token]);

  const login = async (email: string, pass: string) => {
    const data = await api.auth.login(email, pass);
    localStorage.setItem('careerpilot_token', data.access_token);
    setToken(data.access_token);
    const userData = await api.auth.getMe();
    setUser(userData);
    await refreshProfile();
  };

  const register = async (email: string, pass: string, name: string) => {
    await api.auth.register(email, pass, name);
    await login(email, pass);
  };

  const logout = () => {
    localStorage.removeItem('careerpilot_token');
    setToken(null);
    setUser(null);
    setProfile(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, profile, isLoading, login, register, logout, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
