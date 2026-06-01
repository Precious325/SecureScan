'use client';
import { useState } from 'react';
import Link from 'next/link';
import toast from 'react-hot-toast';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (!email) { toast.error('Please enter your email'); return; }
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      const data = await res.json();
      setSubmitted(true);
      toast.success('Request submitted!');
    } catch (error) {
      toast.error('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white">Forgot Password</h1>
          <p className="text-gray-400 mt-2">Request a password reset from the administrator</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8">
          {!submitted ? (
            <>
              <div className="bg-blue-600/10 border border-blue-600/30 rounded-lg p-4 mb-6">
                <p className="text-gray-400 text-sm">
                  Enter your registered email address. The system administrator will review your request and send you a reset code via email.
                </p>
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                />
              </div>
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white font-semibold rounded-lg transition-colors"
              >
                {loading ? 'Submitting...' : 'Submit Reset Request'}
              </button>
            </>
          ) : (
            <div className="text-center">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-white mb-2">Request Submitted!</h2>
              <p className="text-gray-400 text-sm mb-6">
                Your password reset request has been submitted. The administrator will review it and send a reset code to <span className="text-white font-medium">{email}</span>. Please be patient.
              </p>
             <Link href={`/reset-password?email=${encodeURIComponent(email)}`} className="text-blue-400 hover:text-blue-300 text-sm">
  Already have a reset code? Click here →
</Link>
            </div>
          )}

          <div className="mt-6 text-center">
            <Link href="/login" className="text-gray-400 hover:text-gray-300 text-sm">
              ← Back to Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}