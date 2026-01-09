'use client';

import { useEffect, useState, useCallback } from 'react';
import MatchCard from '../components/MatchCard';
import UserLogin from '../components/UserLogin';
import { Match } from '../types/matches';
import { useUser } from '../context/UserContext';

export default function Home() {
  const { userId, logout } = useUser();
  const [matches, setMatches] = useState<Match[]>([]);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const LIMIT = 20;

  const fetchMatches = useCallback(async (currentOffset: number) => {
    if (!userId) return;
    setLoading(true);
    try {
      // Fetching with limit and offset from your FastAPI parameters
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/matches?user_id=${userId}&limit=${LIMIT}&offset=${currentOffset}`
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
  }, [userId]);

  useEffect(() => {
    if (userId) {
      setMatches([]); // Clear matches when user changes
      setOffset(0);
      fetchMatches(0);
    }
  }, [userId, fetchMatches]);

  if (!userId) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-slate-50">
          <div className="p-8 bg-white rounded-2xl shadow-xl border w-full max-w-md text-center">
            <h1 className="text-2xl font-bold mb-4">Welcome back</h1>
            <p className="text-slate-500 mb-6 text-sm">Enter your User ID to view your matches.</p>
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

  console.log("Match IDs in list:", matches.map(m => m.external_id));
  return (
      <main className="max-w-4xl mx-auto p-8 bg-slate-50 min-h-screen">
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Matches</h1>
            <p className="text-sm text-slate-500">Tracking for User #{userId}</p>
          </div>
          <button 
            onClick={logout} 
            className="text-xs font-semibold text-red-500 hover:bg-red-50 px-3 py-1 rounded transition-colors"
          >
            Sign Out
          </button>
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