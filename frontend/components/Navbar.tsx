'use client';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { logout } from '@/lib/auth';
import { getMe } from '@/lib/api';

export default function Navbar({ userName }: { userName?: string }) {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      const cachedRole = localStorage.getItem('userRole');
      if (cachedRole) setUser({ role: cachedRole });
      getMe().then(res => {
        setUser(res.data);
        localStorage.setItem('userRole', res.data.role || 'user');
      }).catch(() => {});
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('userRole');
    logout();
    router.push('/login');
  };

  const getInitials = (name: string) => {
    return name?.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2) || '??';
  };

  return (
    <nav className="bg-gray-900 border-b border-gray-800 px-6 py-4">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <span className="text-white font-bold text-lg">SecureScan</span>
        </Link>

        <div className="flex items-center gap-6">
          <Link href="/dashboard" className="text-gray-300 hover:text-white transition-colors">
            Dashboard
          </Link>
          <Link href="/scan" className="text-gray-300 hover:text-white transition-colors">
            New Scan
          </Link>
          <Link href="/history" className="text-gray-300 hover:text-white transition-colors">
            History
          </Link>
          {user?.role === 'admin' && (
            <Link href="/admin" className="text-yellow-400 hover:text-yellow-300 transition-colors font-medium">
              ⚙ Admin
            </Link>
          )}

          {/* Profile Avatar */}
          <div className="relative">
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-bold hover:bg-blue-700 transition-colors focus:outline-none"
            >
              {getInitials(user?.full_name || userName || '?')}
            </button>

            {showDropdown && (
              <div className="absolute right-0 mt-2 w-48 bg-gray-900 border border-gray-800 rounded-xl shadow-lg z-50">
                <div className="px-4 py-3 border-b border-gray-800">
                  <p className="text-white text-sm font-medium truncate">{user?.full_name || userName}</p>
                  <p className="text-gray-400 text-xs truncate">{user?.email}</p>
                </div>
                <div className="py-1">
                  <Link
                    href="/profile"
                    onClick={() => setShowDropdown(false)}
                    className="block px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-800 text-sm transition-colors"
                  >
                    👤 My Profile
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-red-400 hover:text-red-300 hover:bg-gray-800 text-sm transition-colors"
                  >
                    🚪 Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}