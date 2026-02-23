'use client';

import { useState } from 'react';
import { useUser } from '../context/UserContext';

export default function UserLogin() {
  const { setToken } = useUser();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const formatError = (data: any) => {
      return typeof data.detail === 'string' 
        ? data.detail 
        : JSON.stringify(data.detail);
    };

  const handleLogin = async () => {
    setError(null);
    
    // OAuth2PasswordRequestForm expects x-www-form-urlencoded data
    const formData = new URLSearchParams();
    formData.append('username', email); // backend uses 'username' for the email
    formData.append('password', password);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });
      
      const data = await res.json();
      if (res.ok) {
        setToken(data.access_token); // Save the JWT token
      } else {
        setError(formatError(data) || "Login failed");
      }
    } catch (err) {
      setError("Server connection failed.");
    }
  };

const handleCreate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);
    if (!email) return;
    try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }), // Sending actual password now
        });
      const data = await res.json();
      if (res.ok) {
        setToken(data.access_token);
      } else {
        setError(formatError(data) || "Could not create user.");
      }
    } catch (err) {
      setError("Server connection failed.");
    }
  };

return (
    <div className="space-y-6">
      {/* Email Field */}
      <div>
        <label className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 block">
          Your Email
        </label>
        <input
          type="email"
          placeholder="name@example.com"
          className="w-full border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 text-slate-900"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              //focus password field instead of submitting immediately
              document.getElementById('password-input')?.focus();
            }
          }}
        />
      </div>

    {/* Password Field */}
    <div>
      <label className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 block">
        Password
      </label>
      <div className="relative">
        <input
          id="password-input"
          type={showPassword ? "text" : "password"}
          placeholder="Enter your password"
          className="w-full border rounded-lg px-3 py-2 pr-12 outline-none focus:ring-2 focus:ring-blue-500 text-slate-900"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-black text-slate-400 hover:text-blue-600 uppercase tracking-tighter transition-colors"
        >
          {showPassword ? "Hide" : "Show"}
        </button>
      </div>
    </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button 
          onClick={handleLogin}
          className="flex-1 bg-slate-800 text-white px-4 py-2 rounded-lg font-medium hover:bg-slate-700 transition-colors"
        >
          Sign In
        </button>
        <button 
          onClick={handleCreate}
          className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-500 transition-colors"
        >
          Create New
        </button>
      </div>

      {error && (
        <p className="text-red-500 text-sm bg-red-50 p-2 rounded border border-red-100">
          {error}
        </p>
      )}
    </div>
  );
}