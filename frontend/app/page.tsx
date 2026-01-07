import { Match } from '../types/matches';

async function getMatches(): Promise<Match[]> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/matches`, {
    cache: 'no-store', // Ensures fresh data on every reload
  });

  if (!res.ok) {
    throw new Error('Failed to fetch matches');
  }

  return res.json();
}

export default async function Home() {
  const matches = await getMatches();

  return (
    <main className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Soccer Matches</h1>
      
      <div className="grid gap-4">
        {matches.map((match) => (
          <div key={match.id} className="p-4 border rounded-xl shadow-sm bg-white flex justify-between items-center">
            <div className="flex-1 text-right font-semibold">{match.home_team.name}</div>
            
            <div className="mx-8 flex flex-col items-center">
              <span className="text-sm text-gray-500">{match.status}</span>
              <div className="text-2xl font-bold">
                {match.score?.fullTime?.home ?? 0} - {match.score?.fullTime?.away ?? 0}
              </div>
            </div>

            <div className="flex-1 text-left font-semibold">{match.away_team.name}</div>
          </div>
        ))}
      </div>
    </main>
  );
}