'use client';

import { useEffect, useState, useCallback } from 'react';
import MatchCard from '../components/MatchCard';
import UserLogin from '../components/UserLogin';
import RefreshButton from '../components/RefreshButton';
import { Match } from '../types/matches';
import { useUser } from '../context/UserContext';

export default function Home() {
  const { userEmail, logout } = useUser();
  const [matches, setMatches] = useState<Match[]>([]);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const LIMIT = 20;

  const fetchMatches = useCallback(async (currentOffset: number) => {
    if (!userEmail) return;
    setLoading(true);
    try {
      // Fetching with limit and offset from your FastAPI parameters
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/matches?email=${userEmail}&limit=${LIMIT}&offset=${currentOffset}`
      );
      const newData = await res.json();
      
      setMatches(prev => {
        // If it's a fresh load (offset 0), just return the new data
        if (currentOffset === 0) return newData;

        // If we are appending, filter out matches that already exist in 'prev'
        const existingIds = new Set(prev.map(m => m.external_id));
        const uniqueNewData = newData.filter((m: Match) => !existingIds.has(m.id));
        
        return [...prev, ...uniqueNewData];
      });
      
    } catch (error) {
      console.error("Failed to fetch matches:", error);
    } finally {
      setLoading(false);
    }
  }, [userEmail]);

  useEffect(() => {
    if (userEmail) {
      setMatches([]); // Clear matches when user changes
      setOffset(0);
      fetchMatches(0);
    }
  }, [userEmail, fetchMatches]);

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

  const handleSyncComplete = () => {
    setOffset(0);
    fetchMatches(0);
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
            <RefreshButton onSyncComplete={handleSyncComplete} />
            
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
          {matches.map((match) => (
            <MatchCard key={match.external_id} match={match} />
          ))}
        </div>

        <div className="flex justify-center pb-12">
          <button
            onClick={handleLoadMore}
            disabled={loading}
            className="px-8 py-3 bg-blue-600 text-white rounded-full font-semibold shadow-lg hover:bg-blue-700 disabled:bg-slate-300 transition-all"
          >
            {loading ? 'Loading...' : 'Load More'}
          </button>
        </div>
      </main>
    );
  }