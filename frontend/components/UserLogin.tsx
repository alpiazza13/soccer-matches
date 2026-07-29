'use client';

import { useState } from 'react';
import { useUser } from '../context/UserContext';

export default function UserLogin() {
  const { setToken } = useUser();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const formatError = (data: any) => {
      return typeof data.detail === 'string' 
        ? data.detail 
        : JSON.stringify(data.detail);
    };

  const handleLogin = async () => {
    setError(null);
    setSuccess(null);

    if (!email || !password) {
      setError("Please enter both an email and a password to login.");
      return;
    }

    setIsSubmitting(true);

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
    } finally {
      setIsSubmitting(false);
    }
  };

const handleCreate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!email || !password) {
      setError("Please enter both an email and a password to create an account.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSubmitting(true);
    
    try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }), // Sending actual password now
        });
      const data = await res.json();
      if (res.ok) {
        setSuccess("Account created successfully! You can now Sign In.");
        setPassword('');
        setToken(data.access_token);
      } else {
        setError(formatError(data) || "Could not create user.");
      }
    } catch (err) {
      setError("Server connection failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

return (
    <div className="space-y-6">

    {/* Sucess and Error Messages */}
    {success && (
          <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-lg text-sm font-medium">
            {success}
          </div>
        )}

    {error && (
      <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm font-medium">
        {error}
      </div>
    )}

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
          disabled={isSubmitting}
          className="flex-1 bg-slate-800 text-white px-4 py-2 rounded-lg font-medium hover:bg-slate-700 transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <span className="flex items-center justify-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Signing In...
            </span>
          ) : (
            'Sign In'
          )}
        </button>
        <button 
          onClick={handleCreate}
          disabled={isSubmitting}
          className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-500 transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <span className="flex items-center justify-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Creating...
            </span>
          ) : (
            'Create Account'
          )}
        </button>
      </div>
    </div>
  );
}