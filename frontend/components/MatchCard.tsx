'use client';

import { Match } from '../types/matches';
import { useEffect, useState } from 'react';
import { useUser } from '../context/UserContext';

export default function MatchCard({ match, onToggle }: { match: Match, onToggle: (id: number, isDone: boolean) => void }) {
    const { token, hideScores, isLoadingSettings } = useUser();
    const [done, setDone] = useState(match.is_done);
    const [showScoreLocally, setShowScoreLocally] = useState(false);

  const localDate = new Date(match.utc_date);
  const dateString = localDate.toLocaleDateString();
  const timeString = localDate.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', hour12: true });

  const toggleDone = async () => {
    if (!token) return;
    const newStatus = !done;
    setDone(newStatus); // Optimistic update
    onToggle(match.external_id, newStatus); // Notify parent to update local state

    try {
      // match.external_id is used here as per main.py logic
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/matches/${match.external_id}/status?is_done=${newStatus}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });
    } catch (error) {
      setDone(!newStatus); // Revert on error
      onToggle(match.external_id, !newStatus); // Revert in parent
      console.error("Failed to update status", error);
    }
  };

  useEffect(() => {
    // If the global setting is toggled ON, re-hide any individually revealed scores
    if (hideScores) {
      setShowScoreLocally(false);
    }
  }, [hideScores]);

  return (
    <div className="flex items-center justify-between p-4 bg-white border rounded-xl shadow-sm">
      <div className="w-36 text-sm font-bold text-blue-700">
        {dateString} {timeString}
      </div>

      <div className="flex-1 flex items-center justify-center gap-4">
        <span className="flex-1 text-right">{match.home_team.short_name}</span>

        <div 
          className="relative group cursor-pointer"
          onClick={() => hideScores && setShowScoreLocally(!showScoreLocally)}
        >
          <span className={`font-mono bg-slate-100 px-2 rounded transition-all duration-300 ${
            (hideScores || isLoadingSettings) && !showScoreLocally ? 'blur-md select-none' : ''
          }`}>
            {match.score?.fullTime?.home ?? 0} - {match.score?.fullTime?.away ?? 0}
          </span>
          
          {hideScores && !showScoreLocally && (
            <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold uppercase text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity">
              Show
            </span>
          )}
        </div>

        <span className="flex-1 text-left">{match.away_team.short_name}</span>
      </div>

      <div className="w-32 flex items-center justify-end gap-3">
        <span className="text-xs text-slate-400 uppercase">{match.status}</span>
        <input 
          type="checkbox" 
          checked={done} 
          onChange={toggleDone}
          className="w-5 h-5 rounded border-gray-300 text-blue-600 cursor-pointer"
        />
      </div>
    </div>
  );
}