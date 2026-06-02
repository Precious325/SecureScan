'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { loginUser } from '@/lib/api';
import { setToken } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string; general?: string }>({});
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setLoading(true);

    try {
      const response = await loginUser({ email, password });
      setToken(response.data.access_token);
      localStorage.setItem('userRole', response.data.role || 'user');
      toast.success('Login successful!');
      router.push('/dashboard');
    } catch (error: any) {
      setErrors({ general: 'Incorrect email or password. Please check and try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl mb-4">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-white">SecureScan</h1>
          <p className="text-gray-400 mt-1">Forensic Document Verification</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8">
          <h2 className="text-xl font-semibold text-white mb-6">Sign in to your account</h2>

          {errors.general && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
              <p className="text-red-400 text-sm">{errors.general}</p>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Email address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setErrors(prev => ({ ...prev, email: undefined })); }}
                required
                autoComplete="email"
                className={`w-full px-4 py-3 bg-gray-800 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-1 transition-colors
                  ${errors.email ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-gray-700 focus:border-blue-500 focus:ring-blue-500'}`}
                placeholder="you@example.com"
              />
              {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setErrors(prev => ({ ...prev, password: undefined })); }}
                  required
                  autoComplete="current-password"
                  className={`w-full px-4 py-3 pr-12 bg-gray-800 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-1 transition-colors
                    ${errors.password ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-gray-700 focus:border-blue-500 focus:ring-blue-500'}`}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-300"
                >
                  {showPassword ? (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 4.411m0 0L21 21" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
              {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password}</p>}
            </div>

            <div className="flex justify-end">
              <Link href="/forgot-password" className="text-blue-400 hover:text-blue-300 text-sm">
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white font-semibold rounded-lg transition-colors"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <p className="text-center text-gray-400 mt-6">
            Don&apos;t have an account?{' '}
            <Link href="/register" className="text-blue-400 hover:text-blue-300 font-medium">
              Create one
            </Link>
          </p>
        </div>

        <p className="text-center text-gray-600 text-sm mt-6">
          University of Bamenda — College of Technology
        </p>
      </div>
    </div>
  );
}