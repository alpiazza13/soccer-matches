'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

interface UserContextType {
  userId: string | null;
  setUserId: (id: string) => void;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const savedId = localStorage.getItem('soccer_user_id');
    if (savedId) setUserId(savedId);
  }, []);

  const handleSetUserId = (id: string) => {
    setUserId(id);
    localStorage.setItem('soccer_user_id', id.toString());
  };

  const logout = () => {
    setUserId(null);
    localStorage.removeItem('soccer_user_id');
  };

  return (
    <UserContext.Provider value={{ userId, setUserId: handleSetUserId, logout }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) throw new Error('useUser must be used within a UserProvider');
  return context;
}