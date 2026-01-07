// frontend/components/MatchCard.tsx
import { Match } from '../types/matches';

interface MatchCardProps {
  match: Match;
  isDone?: boolean; // We'll pass this in once your backend supports it
}

export default function MatchCard({ match, isDone }: MatchCardProps) {
  const date = new Date(match.utc_date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
  const time = new Date(match.utc_date).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="flex items-center justify-between p-4 bg-white border rounded-xl shadow-sm hover:shadow-md transition-shadow">
      {/* Time Section */}
      <div className="w-24 text-sm">
        <div className="font-bold text-slate-900">{date}</div>
        <div className="text-slate-500">{time}</div>
      </div>

      {/* Teams & Score */}
      <div className="flex-1 flex items-center justify-center gap-6">
        <div className="flex-1 text-right font-medium">{match.home_team.name}</div>
        <div className="flex items-center gap-2 bg-slate-50 px-4 py-2 rounded-lg border">
          <span className="text-xl font-bold tabular-nums">
            {match.score?.fullTime?.home ?? 0}
          </span>
          <span className="text-slate-300">-</span>
          <span className="text-xl font-bold tabular-nums">
            {match.score?.fullTime?.away ?? 0}
          </span>
        </div>
        <div className="flex-1 text-left font-medium">{match.away_team.name}</div>
      </div>

      {/* Status & Checkbox */}
      <div className="w-32 flex flex-col items-end gap-1">
        <span className={`text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded ${
          match.status === 'FINISHED' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
        }`}>
          {match.status}
        </span>
        <label className="flex items-center gap-2 cursor-pointer mt-1">
          <span className="text-xs text-slate-500">Watched</span>
          <input 
            type="checkbox" 
            checked={isDone} 
            readOnly // Temporary until we add the "Toggle" functionality
            className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
        </label>
      </div>
    </div>
  );
}