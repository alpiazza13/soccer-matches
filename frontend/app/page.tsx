// frontend/app/page.tsx
import MatchCard from '../components/MatchCard';
import { Match } from '../types/matches';

async function getMatches(): Promise<Match[]> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/matches`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch matches');
  return res.json();
}

export default async function Home() {
  const matches = await getMatches();

  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-extrabold text-slate-900">Matches</h1>
          <p className="text-slate-500">Keep track of your watched matches.</p>
        </header>
        
        <div className="grid gap-3">
          {matches.map((match) => (
            <MatchCard key={match.id} match={match} />
          ))}
        </div>
      </div>
    </main>
  );
}