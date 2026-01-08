'use client';

import { Match } from '../types/matches';
import { useState } from 'react';

export default function MatchCard({ match }: { match: Match }) {
  const [done, setDone] = useState(match.is_done);

  const toggleDone = async () => {
    const newStatus = !done;
    setDone(newStatus); // Optimistic update

    try {
      // hardcoding user_id=9 for now
      // match.external_id is used here as per main.py logic
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/matches/${match.external_id}/done?user_id=9`, {
        method: 'POST',
      });
    } catch (error) {
      setDone(!newStatus); // Revert on error
      console.error("Failed to update status", error);
    }
  };

  return (
    <div className="flex items-center justify-between p-4 bg-white border rounded-xl shadow-sm">
      <div className="w-24 text-sm font-bold text-slate-900">
        {new Date(match.utc_date).toLocaleDateString()}
      </div>

      <div className="flex-1 flex items-center justify-center gap-4">
        <span className="flex-1 text-right">{match.home_team.short_name}</span>
        <span className="font-mono bg-slate-100 px-2 rounded">
            {match.score?.fullTime?.home ?? 0} - {match.score?.fullTime?.away ?? 0}
        </span>
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