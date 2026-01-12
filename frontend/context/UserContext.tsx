'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

interface UserContextType {
  userEmail: string | null;
  setUserEmail: (email: string) => void;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    const savedEmail = localStorage.getItem('soccer_user_email');
    if (savedEmail) setUserEmail(savedEmail);
  }, []);

  const handleSetUserEmail = (email: string) => {
    setUserEmail(email);
    localStorage.setItem('soccer_user_email', email);
  };

  const logout = () => {
    setUserEmail(null);
    localStorage.removeItem('soccer_user_email');
  };

  return (
    <UserContext.Provider value={{ userEmail, setUserEmail: handleSetUserEmail, logout }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) throw new Error('useUser must be used within a UserProvider');
  return context;
}