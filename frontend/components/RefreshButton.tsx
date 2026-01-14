'use client';

import { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';

interface RefreshButtonProps {
  onSyncComplete: () => void;
}

export default function RefreshButton({ onSyncComplete }: RefreshButtonProps) {
  const [isSyncing, setIsSyncing] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  // Handle the countdown timer
  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  const handleRefresh = async () => {
    if (isSyncing || cooldown > 0) return;

    setIsSyncing(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/matches/sync`, {
        method: 'POST',
      });

      if (res.ok) {
        onSyncComplete(); // Tell the page to re-fetch matches
        setCooldown(60);  // Set a 60-second cooldown
      } else {
        alert("Failed to sync matches. Please try again later.");
      }
    } catch (error) {
        console.error("Sync error:", error);
        alert("Connection error. Check if backend is running.");
    } finally {
        setIsSyncing(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-1">
      <button
        onClick={handleRefresh}
        disabled={isSyncing || cooldown > 0}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-bold text-xs uppercase tracking-wider transition-all shadow-sm
          ${isSyncing || cooldown > 0 
            ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
            : 'bg-blue-50 text-blue-600 hover:bg-blue-100'}`}
      >
        <RefreshCw size={14} className={`${isSyncing ? 'animate-spin' : ''}`} />
        {isSyncing ? 'Syncing...' : cooldown > 0 ? `Wait ${cooldown}s` : 'Refresh Data'}
      </button>
    </div>
  );
}