'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { getMe, getScanHistory } from '@/lib/api';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    const fetchData = async () => {
      try {
        const [userRes, scansRes] = await Promise.all([getMe(), getScanHistory()]);
        setUser(userRes.data);
        setScans(scansRes.data.slice(0, 5));
      } catch (error) {
        toast.error('Session expired. Please login again.');
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router]);

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'AUTHENTIC': return 'text-green-400 bg-green-400/10';
      case 'SUSPICIOUS': return 'text-yellow-400 bg-yellow-400/10';
      case 'LIKELY FORGED': return 'text-orange-400 bg-orange-400/10';
      case 'FORGED': return 'text-red-400 bg-red-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-white text-lg">Loading...</div>
      </div>
    );
  }

  const totalScans = scans.length;
  const forgedCount = scans.filter(s =>
    s.risk_verdict === 'FORGED' || s.risk_verdict === 'LIKELY FORGED'
  ).length;
  const authenticCount = scans.filter(s => s.risk_verdict === 'AUTHENTIC').length;

  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar userName={user?.full_name} />

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">
            Welcome back, {user?.full_name?.split(' ')[0]}
          </h1>
          <p className="text-gray-400 mt-1">
            Forensic Document Verification Dashboard
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <p className="text-gray-400 text-sm">Total Scans</p>
            <p className="text-3xl font-bold text-white mt-1">{totalScans}</p>
          </div>
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <p className="text-gray-400 text-sm">Authentic Documents</p>
            <p className="text-3xl font-bold text-green-400 mt-1">{authenticCount}</p>
          </div>
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <p className="text-gray-400 text-sm">Suspicious / Forged</p>
            <p className="text-3xl font-bold text-red-400 mt-1">{forgedCount}</p>
          </div>
        </div>

        {/* Quick Action */}
        <div className="bg-blue-600/10 border border-blue-600/30 rounded-xl p-6 mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-white font-semibold text-lg">Verify a Document</h2>
            <p className="text-gray-400 text-sm mt-1">
              Upload a PDF or image to run forensic analysis
            </p>
          </div>
          <Link
            href="/scan"
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
          >
            New Scan →
          </Link>
        </div>

        {/* Recent Scans */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white font-semibold">Recent Scans</h2>
            <Link href="/history" className="text-blue-400 hover:text-blue-300 text-sm">
              View all →
            </Link>
          </div>

          {scans.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No scans yet. Start by uploading a document.
            </div>
          ) : (
            <div className="space-y-3">
              {scans.map((scan) => (
                <div
                  key={scan.scan_id}
                  className="flex items-center justify-between p-4 bg-gray-800 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gray-700 rounded flex items-center justify-center text-xs text-gray-300 font-mono">
                      {scan.file_format}
                    </div>
                    <div>
                      <p className="text-white text-sm font-medium">{scan.original_filename}</p>
                      <p className="text-gray-500 text-xs">{new Date(scan.upload_timestamp).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getVerdictColor(scan.risk_verdict)}`}>
                      {scan.risk_verdict}
                    </span>
                    <span className="text-gray-400 text-sm">{scan.risk_score}/100</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}