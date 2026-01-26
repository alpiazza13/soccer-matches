'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

interface UserContextType {
  userEmail: string | null;
  setUserEmail: (email: string) => void;
  logout: () => void;
  hideScores: boolean;
  setHideScores: (value: boolean) => Promise<void>;
  isLoadingSettings: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [hideScores, setHideScoresState] = useState(false);
  const [isLoadingSettings, setIsLoadingSettings] = useState(true);

  useEffect(() => {
    const savedEmail = localStorage.getItem('soccer_user_email');
    if (savedEmail) {
      setUserEmail(savedEmail);
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/me?email=${savedEmail}`)
        .then(res => res.json())
        .then(data => {
          if (data.hide_scores !== undefined) setHideScoresState(data.hide_scores);
          setIsLoadingSettings(false); // Done loading
        })
        .catch(() => setIsLoadingSettings(false)); // Safety break
    } else {
      setIsLoadingSettings(false); // No user to load settings for
    }
  }, []);

  const setHideScores = async (value: boolean) => {
    setHideScoresState(value); // Optimistic update
    if (!userEmail) return;

    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/me/settings?email=${userEmail}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hide_scores: value }),
      });
    } catch (error) {
      console.error("Failed to save settings", error);
    }
  };

  const handleSetUserEmail = (email: string) => {
    setUserEmail(email);
    localStorage.setItem('soccer_user_email', email);
  };

  const logout = () => {
    setUserEmail(null);
    localStorage.removeItem('soccer_user_email');
  };

  return (
    <UserContext.Provider value={{ userEmail, setUserEmail: handleSetUserEmail, 
                                   logout, hideScores, setHideScores, isLoadingSettings }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) throw new Error('useUser must be used within a UserProvider');
  return context;
}


