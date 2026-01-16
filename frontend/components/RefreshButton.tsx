'use client';

import { useState, useEffect } from 'react';
import { RefreshCw, CheckCircle2 } from 'lucide-react';

interface RefreshButtonProps {
  onSyncComplete: () => void;
  isFresh: boolean;           
  lastSynced: string | null;
}

export default function RefreshButton({ onSyncComplete, isFresh, lastSynced }: RefreshButtonProps) {
  const [isSyncing, setIsSyncing] = useState(false);
  const [timeAgo, setTimeAgo] = useState<string>('');

  useEffect(() => {
    const calculateTimeAgo = () => {
      if (!lastSynced) {
        setTimeAgo('Never synced');
        return;
      }

      const lastDate = new Date(lastSynced).getTime();
      const now = new Date().getTime();
      const diffInSeconds = Math.floor((now - lastDate) / 1000);
      const diffInMinutes = Math.floor(diffInSeconds / 60);
      const diffInHours = Math.floor(diffInMinutes / 60);
      const diffInDays = Math.floor(diffInHours / 24);

      if (diffInSeconds < 60) {
        setTimeAgo('Just now');
      } else if (diffInMinutes < 60) {
        setTimeAgo(`${diffInMinutes} ${diffInMinutes === 1 ? 'minute' : 'minutes'} ago`);
      } else if (diffInHours < 24) {
        setTimeAgo(`${diffInHours} ${diffInHours === 1 ? 'hour' : 'hours'} ago`);
      } else if (diffInDays < 7) {
        setTimeAgo(`${diffInDays} ${diffInDays === 1 ? 'day' : 'days'} ago`);
      } else {
        // Fallback to a simple date string for very old data
        setTimeAgo(new Date(lastSynced).toLocaleDateString());
      }
    };

    calculateTimeAgo();
    const interval = setInterval(calculateTimeAgo, 60000); // Run calculateTimeAgo every minute
    return () => clearInterval(interval); // Cleanup on unmount
  }, [lastSynced]);

  const handleRefresh = async () => {
    if (isSyncing || isFresh) return;

    setIsSyncing(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/matches/sync`, {
        method: 'POST',
      });

      const data = await res.json();

      if (res.ok) {
        // This will display "Database synced successfully"  OR "Data is already fresh..." from your backend logic
        alert(data.message); 
        onSyncComplete();
      } else if (res.status === 429) {
        alert("Sync in progress. Please wait.");
      }

    } catch (error) {
        console.error("Sync error:", error);
        alert("Connection error");
    } finally {
        setIsSyncing(false);
    }
  };

  return (
      <div className="flex flex-col items-end gap-1">
        <button
          onClick={handleRefresh}
          disabled={isSyncing || isFresh}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-bold text-xs uppercase tracking-wider transition-all shadow-sm
            ${isSyncing 
              ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
              : isFresh
                ? 'bg-green-50 text-green-600 cursor-default' // Green state for fresh data
                : 'bg-blue-50 text-blue-600 hover:bg-blue-100'}`}
        >
          {isSyncing ? (
            <RefreshCw size={14} className="animate-spin" />
          ) : isFresh ? (
            <CheckCircle2 size={14} />
          ) : (
            <RefreshCw size={14} />
          )}
          
          {isSyncing ? 'Syncing...' : isFresh ? 'Data Up to Date' : 'Refresh Data'}
        </button>
        
        {lastSynced && (
          <span className="text-[10px] text-slate-400 font-medium px-1">
            Last updated: {timeAgo}
          </span>
        )}
      </div>
    );
  }