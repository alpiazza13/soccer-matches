import MatchCard from '../components/MatchCard';
import { Match } from '../types/matches';

async function getMatches(): Promise<Match[]> {
  // Pass user_id=9 to the join logic in main.py
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/matches?user_id=9`, { 
    cache: 'no-store' 
  });
  if (!res.ok) throw new Error('Failed to fetch matches');
  return res.json();
}

export default async function Home() {
  const matches = await getMatches();

  return (
    <main className="max-w-4xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6">User 9's Match Tracker</h1>
      <div className="grid gap-3">
        {matches.map((match) => (
          <MatchCard key={match.id} match={match} />
        ))}
      </div>
    </main>
  );
}