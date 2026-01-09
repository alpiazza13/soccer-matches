'use client';

import { useState } from 'react';
import { useUser } from '../context/UserContext';

export default function UserLogin() {
  const { setUserId } = useUser();
  const [email, setEmail] = useState('');
  const [existingId, setExistingId] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleExistingLogin = async () => {
    setError(null);
    if (!existingId) return;

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/me?user_id=${existingId}`);
      const data = await res.json();
      
      if (res.ok) {
        setUserId(parseInt(existingId));
      } else {
        const errorMessage = typeof data.detail === 'string' 
          ? data.detail 
          : JSON.stringify(data.detail);
        setError(errorMessage);
      }
    } catch (err) {
      setError("Server connection failed.");
    }
  };

const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, username: email.split('@')[0] }),
      });
      const data = await res.json();
      if (res.ok) {
        setUserId(data.id);
      } else {
        const errorMessage = typeof data.detail === 'string' 
          ? data.detail 
          : JSON.stringify(data.detail);
        setError(errorMessage);
      }
    } catch (err) {
      setError("Server connection failed.");
    }
  };

return (
    <div className="space-y-6">
      {error && (
        <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg">
          {error}
        </div>
      )}

      <div>
        <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Existing User</h2>
        <div className="flex gap-2">
          <input
            type="number"
            placeholder="Enter User ID"
            className="flex-1 border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 text-slate-900"
            value={existingId}
            onChange={(e) => setExistingId(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleExistingLogin()}
          />
          <button 
            onClick={handleExistingLogin}
            className="bg-slate-800 text-white px-4 py-2 rounded-lg font-medium hover:bg-slate-700 transition-colors"
          >
            Go
          </button>
        </div>
      </div>

      <div className="relative py-2">
        <div className="absolute inset-0 flex items-center"><span className="w-full border-t"></span></div>
        <div className="relative flex justify-center text-xs uppercase"><span className="bg-white px-2 text-slate-400 font-semibold">Or</span></div>
      </div>

      <form onSubmit={handleCreateUser}>
        <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">New User</h2>
        <div className="flex flex-col gap-2">
          <input
            type="email"
            placeholder="your-email@example.com"
            className="border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 text-slate-900"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <button 
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 shadow-md"
          >
            Create Account
          </button>
        </div>
      </form>
    </div>
  );
}