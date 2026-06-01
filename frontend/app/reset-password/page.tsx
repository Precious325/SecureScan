'use client';
import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'code' | 'password'>('code');
  const [errors, setErrors] = useState<any>({});

  useEffect(() => {
    const emailParam = searchParams.get('email');
    if (emailParam) setEmail(emailParam);
  }, [searchParams]);

  const handleVerifyCode = () => {
    setErrors({});
    if (!email) { setErrors({ email: 'Please enter your email address.' }); return; }
    if (code.length !== 6) { setErrors({ code: 'Please enter the 6-digit code.' }); return; }
    setStep('password');
  };

  const handleResetPassword = async () => {
    setErrors({});
    if (newPassword.length < 6) { setErrors({ newPassword: 'Password must be at least 6 characters.' }); return; }
    if (newPassword !== confirmPassword) { setErrors({ confirmPassword: 'Passwords do not match.' }); return; }

    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.toLowerCase().trim(),
          code,
          new_password: newPassword
        })
      });
      const data = await res.json();
      if (res.ok) {
        toast.success('Password reset successfully! Please sign in.');
        router.push('/login');
      } else {
        toast.error(data.detail || 'Reset failed. Please try again.');
        setStep('code');
      }
    } catch (error) {
      toast.error('Something went wrong. Please try again.');
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
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-white">Reset Password</h1>
          <p className="text-gray-400 mt-1">
            {step === 'code' ? 'Enter your email and the reset code' : 'Choose your new password'}
          </p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8">
          <div className="flex items-center gap-2 mb-6">
            <div className={`flex-1 h-1.5 rounded-full ${step === 'code' ? 'bg-blue-600' : 'bg-green-500'}`} />
            <div className={`flex-1 h-1.5 rounded-full ${step === 'password' ? 'bg-blue-600' : 'bg-gray-700'}`} />
          </div>

          {step === 'code' ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={e => { setEmail(e.target.value); setErrors((p: any) => ({ ...p, email: undefined })); }}
                  className={`w-full px-4 py-3 bg-gray-800 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-1 transition-colors ${errors.email ? 'border-red-500' : 'border-gray-700 focus:border-blue-500'}`}
                  placeholder="your@email.com"
                />
                {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">6-digit Reset Code</label>
                <input
                  type="text"
                  value={code}
                  onChange={e => {
                    const val = e.target.value.replace(/\D/g, '').slice(0, 6);
                    setCode(val);
                    setErrors((p: any) => ({ ...p, code: undefined }));
                  }}
                  maxLength={6}
                  className={`w-full px-4 py-3 bg-gray-800 border rounded-lg text-white text-center text-2xl tracking-widest placeholder-gray-500 focus:outline-none focus:ring-1 transition-colors ${errors.code ? 'border-red-500' : 'border-gray-700 focus:border-blue-500'}`}
                  placeholder="000000"
                />
                {errors.code && <p className="text-red-400 text-xs mt-1">{errors.code}</p>}
              </div>

              <button
                onClick={handleVerifyCode}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
              >
                Verify Code →
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">New Password</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={e => { setNewPassword(e.target.value); setErrors((p: any) => ({ ...p, newPassword: undefined })); }}
                  className={`w-full px-4 py-3 bg-gray-800 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-1 transition-colors ${errors.newPassword ? 'border-red-500' : 'border-gray-700 focus:border-blue-500'}`}
                  placeholder="••••••••"
                />
                {errors.newPassword && <p className="text-red-400 text-xs mt-1">{errors.newPassword}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Confirm Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={e => { setConfirmPassword(e.target.value); setErrors((p: any) => ({ ...p, confirmPassword: undefined })); }}
                  className={`w-full px-4 py-3 bg-gray-800 border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-1 transition-colors ${errors.confirmPassword ? 'border-red-500' : 'border-gray-700 focus:border-blue-500'}`}
                  placeholder="••••••••"
                />
                {errors.confirmPassword && <p className="text-red-400 text-xs mt-1">{errors.confirmPassword}</p>}
              </div>

              <button
                onClick={handleResetPassword}
                disabled={loading}
                className="w-full py-3 bg-green-600 hover:bg-green-700 disabled:bg-green-800 text-white font-semibold rounded-lg transition-colors"
              >
                {loading ? 'Resetting...' : 'Reset Password'}
              </button>

              <button
                onClick={() => setStep('code')}
                className="w-full py-2 text-gray-400 hover:text-white text-sm transition-colors"
              >
                ← Back
              </button>
            </div>
          )}

          <p className="text-center text-gray-400 mt-6">
            <Link href="/login" className="text-blue-400 hover:text-blue-300 font-medium">
              ← Back to Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-950 flex items-center justify-center"><div className="text-white">Loading...</div></div>}>
      <ResetPasswordForm />
    </Suspense>
  );
}