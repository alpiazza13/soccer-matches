'use client';

import { useEffect, useState, useCallback } from 'react';
import MatchCard from '../components/MatchCard';
import UserLogin from '../components/UserLogin';
import RefreshButton from '../components/RefreshButton';
import { Match } from '../types/matches';
import { useUser } from '../context/UserContext';

interface SyncStatus {
  last_run_at: string | null;
  is_fresh: boolean;
}

export default function Home() {
  const { userEmail, logout, hideScores, setHideScores } = useUser();
  const [matches, setMatches] = useState<Match[]>([]);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [hideDone, setHideDone] = useState(false);
  const LIMIT = 20;

  const fetchMatches = useCallback(async (currentOffset: number) => {
    if (!userEmail) return;
    if (currentOffset > 0) {
      setLoading(true);
    }
    try {
      // Fetching with limit and offset from your FastAPI parameters
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/matches?email=${userEmail}&limit=${LIMIT}&offset=${currentOffset}&hide_done=${hideDone}`
      );
      const newData = await res.json();
      
      setMatches(prev => {
        if (currentOffset === 0) return newData;
        // If we are appending, filter out matches that already exist in 'prev'
        const existingIds = new Set(prev.map(m => m.external_id));
        const uniqueNewData = newData.filter((m: Match) => !existingIds.has(m.external_id));
        return [...prev, ...uniqueNewData];
      });
      
    } catch (error) {
      console.error("Failed to fetch matches:", error);
    } finally {
      setLoading(false);
    }
  }, [userEmail, hideDone]);

  const visibleMatches = hideDone ? matches.filter(match => !match.is_done) : matches;

  const toggleMatchLocal = (matchId: number, isDone: boolean) => {
      setMatches(prev => 
        prev.map(m => m.external_id === matchId ? { ...m, is_done: isDone } : m)
      );
    };

  const fetchSyncStatus = useCallback(async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/matches/sync/status`);
      if (res.ok) {
        const data = await res.json();
        setSyncStatus(data);
      }
    } catch (error) {
      console.error("Failed to fetch sync status:", error);
    }
  }, []);

  const handleSyncComplete = useCallback(() => {
    setOffset(0);
    fetchMatches(0);
    fetchSyncStatus(); 
  }, [fetchMatches, fetchSyncStatus]);


  useEffect(() => {
    if (userEmail) {
      setMatches([]); // Clear matches when user changes
      setOffset(0);
      fetchMatches(0);
      fetchSyncStatus();

      const interval = setInterval(() => {fetchSyncStatus();}, 30000); // Check every 30 seconds
      return () => clearInterval(interval); // Cleanup on unmount
    }
  }, [userEmail, fetchMatches, fetchSyncStatus]);

  useEffect(() => {
    setOffset(0);
    fetchMatches(0);
  }, [hideDone]);

  useEffect(() => {
    if (!userEmail) {
      setMatches([]);
      setOffset(0);
    }
  }, [userEmail]);

  if (!userEmail) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-slate-50">
          <div className="p-8 bg-white rounded-2xl shadow-xl border w-full max-w-md text-center">
            <h1 className="text-2xl font-bold mb-4">Welcome back</h1>
            <p className="text-slate-500 mb-6 text-sm">Login with your email to view your matches.</p>
            <UserLogin />
          </div>
        </div>
      );
    }

  const handleLoadMore = () => {
    const nextOffset = offset + LIMIT;
    setOffset(nextOffset);
    fetchMatches(nextOffset);
  };


  const deleteAccount = async () => {
    const confirmed = window.confirm(
      "Are you sure? This will permanently delete your account and all your 'Done' match history."
    );
    
    if (!confirmed) return;

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/me?email=${userEmail}`, {
        method: 'DELETE',
      });

      if (res.ok) {
        logout();
        alert("Your account has been successfully deleted.");
      } else {
          const data = await res.json();
          alert(`Error: ${data.detail || 'Could not delete account'}`);
      }
    } catch (err) {
        console.error("Delete account failed:", err);
        alert("Server connection failed. Please try again later.");
    }
  };

  console.log("Match IDs in list:", matches.map(m => m.external_id));
  return (
      <main className="max-w-4xl mx-auto p-8 bg-slate-50 min-h-screen">

        <div className="flex justify-between items-end mb-8 border-b border-slate-200 pb-6">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Matches</h1>
            <p className="text-sm text-slate-500 font-medium">
              Logged in as <span className="text-slate-700">{userEmail}</span>
            </p>
          </div>
          
          <div className="flex items-center gap-6">

            <div className="flex items-center gap-2 pr-4 border-r border-slate-200">
              <input
                type="checkbox"
                id="hideDone"
                checked={hideDone}
                onChange={(e) => setHideDone(e.target.checked)}
                className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
              />
              <label htmlFor="hideDone" className="text-[10px] font-bold text-slate-500 uppercase tracking-wider cursor-pointer select-none">
                Hide Completed
              </label>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="hideScores"
                checked={hideScores}
                onChange={(e) => setHideScores(e.target.checked)}
                className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="hideScores" className="text-sm font-medium text-slate-600 cursor-pointer">
                Hide Scores
              </label>
            </div>

            <RefreshButton 
              onSyncComplete={handleSyncComplete} 
              isFresh={syncStatus?.is_fresh ?? false}
              lastSynced={syncStatus?.last_run_at ?? null}
            />
            
            <button 
              onClick={deleteAccount} 
              className="text-xs font-bold text-slate-400 hover:text-red-600 uppercase tracking-wider transition-colors"
            >
              Delete Account
            </button>
            
            <button 
              onClick={logout} 
              className="text-xs font-bold text-red-500 bg-red-50 hover:bg-red-100 px-4 py-2 rounded-lg transition-all shadow-sm"
            >
              Sign Out
            </button>
          </div>
        </div>
        
        <div className="grid gap-3 mb-8">
          {visibleMatches.map((match) => (
            <MatchCard 
              key={match.external_id} 
              match={match} 
              onToggle={toggleMatchLocal}
            />
          ))}
        </div>

      {visibleMatches.length > 0 && (
        <div className="flex justify-center pb-12">
          <button
            onClick={handleLoadMore}
            disabled={loading}
            className="px-8 py-3 bg-blue-600 text-white rounded-full font-semibold shadow-lg hover:bg-blue-700 disabled:bg-slate-300 transition-all"
          >
            {loading ? 'Loading...' : 'Load More'}
          </button>
        </div>
      )}

      </main>
    );
  }