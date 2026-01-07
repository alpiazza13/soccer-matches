'use client';

import { useEffect, useState } from 'react';
import MatchCard from '../components/MatchCard';
import { Match } from '../types/matches';

export default function Home() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const LIMIT = 20;

  const fetchMatches = async (currentOffset: number) => {
    setLoading(true);
    try {
      // Fetching with limit and offset from your FastAPI parameters
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/matches?user_id=9&limit=${LIMIT}&offset=${currentOffset}`
      );
      const newData = await res.json();
      
      // Append new matches to the existing list
      setMatches(prev => [...prev, ...newData]);
    } catch (error) {
      console.error("Failed to fetch matches:", error);
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch on load
  useEffect(() => {
    fetchMatches(0);
  }, []);

  const handleLoadMore = () => {
    const nextOffset = offset + LIMIT;
    setOffset(nextOffset);
    fetchMatches(nextOffset);
  };

  return (
    <main className="max-w-4xl mx-auto p-8 bg-slate-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-8 text-slate-900">Match Schedule</h1>
      
      <div className="grid gap-3 mb-8">
        {matches.map((match) => (
          <MatchCard key={match.id} match={match} />
        ))}
      </div>

      <div className="flex justify-center pb-12">
        <button
          onClick={handleLoadMore}
          disabled={loading}
          className="px-8 py-3 bg-blue-600 text-white rounded-full font-semibold shadow-lg hover:bg-blue-700 transition-colors disabled:bg-slate-300"
        >
          {loading ? 'Loading...' : 'Load More Matches'}
        </button>
      </div>
    </main>
  );
}