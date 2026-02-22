'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

interface UserContextType {
  token: string | null;
  setToken: (token: string) => void;
  logout: () => void;
  hideScores: boolean;
  setHideScores: (value: boolean) => Promise<void>;
  isLoadingSettings: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [hideScores, setHideScoresState] = useState(false);
  const [isLoadingSettings, setIsLoadingSettings] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('soccer_access_token');
    if (savedToken) {
      setTokenState(savedToken);
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/me`, {
        headers: { 'Authorization': `Bearer ${savedToken}` }
      })
      .then(res => res.ok ? res.json() : (logout(), null))
      .then(data => {
        if (data) setHideScoresState(data.hide_scores);
      })
      .catch(() => logout())
      .finally(() => setIsLoadingSettings(false));
    } else {
      setIsLoadingSettings(false);
    }
  }, []);

  const setHideScores = async (value: boolean) => {
    if (!token) return;
    setHideScoresState(value);

    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ hide_scores: value }),
      });
    } catch (error) {
      console.error("Failed to save settings", error);
    }
  };

  const setToken = (newToken: string) => {
    setTokenState(newToken);
    localStorage.setItem('soccer_access_token', newToken); // Use consistent key
  };

  const logout = () => {
    setTokenState(null);
    localStorage.removeItem('soccer_access_token');
  };

  return (
    <UserContext.Provider value={{ token, setToken, logout, hideScores, setHideScores, isLoadingSettings }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) throw new Error('useUser must be used within a UserProvider');
  return context;
}


