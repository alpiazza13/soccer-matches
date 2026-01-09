'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

interface UserContextType {
  userId: number | null;
  setUserId: (id: number) => void;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [userId, setUserId] = useState<number | null>(null);

  useEffect(() => {
    const savedId = localStorage.getItem('soccer_user_id');
    if (savedId) setUserId(parseInt(savedId));
  }, []);

  const handleSetUserId = (id: number) => {
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