'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import { getScanHistory, downloadReport } from '@/lib/api';
import toast from 'react-hot-toast';

export default function HistoryPage() {
  const router = useRouter();
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    getScanHistory()
      .then((res) => setScans(res.data))
      .catch(() => {
        toast.error('Session expired');
        router.push('/login');
      })
      .finally(() => setLoading(false));
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

  const handleDownload = async (scanId: string) => {
    try {
      const response = await downloadReport(scanId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `SecureScan_Report_${scanId.slice(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Report downloaded!');
    } catch (error) {
      toast.error('Failed to download report');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar />

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">Scan History</h1>
          <p className="text-gray-400 mt-1">{scans.length} total scans</p>
        </div>

        {scans.length === 0 ? (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
            <p className="text-gray-500">No scans yet. Start by uploading a document.</p>
          </div>
        ) : (
          <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left px-6 py-4 text-gray-400 text-sm font-medium">Document</th>
                  <th className="text-left px-6 py-4 text-gray-400 text-sm font-medium">Format</th>
                  <th className="text-left px-6 py-4 text-gray-400 text-sm font-medium">Verdict</th>
                  <th className="text-left px-6 py-4 text-gray-400 text-sm font-medium">Score</th>
                  <th className="text-left px-6 py-4 text-gray-400 text-sm font-medium">Date</th>
                  <th className="text-left px-6 py-4 text-gray-400 text-sm font-medium">Report</th>
                </tr>
              </thead>
              <tbody>
                {scans.map((scan, index) => (
                  <tr key={scan.scan_id} className={`border-b border-gray-800 ${index % 2 === 0 ? '' : 'bg-gray-800/30'}`}>
                    <td className="px-6 py-4">
                      <p className="text-white text-sm font-medium truncate max-w-48">{scan.original_filename}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-gray-400 text-sm font-mono">{scan.file_format}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getVerdictColor(scan.risk_verdict)}`}>
                        {scan.risk_verdict}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-gray-300 text-sm">{scan.risk_score}/100</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-gray-400 text-sm">
                        {new Date(scan.upload_timestamp).toLocaleDateString()}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => handleDownload(scan.scan_id)}
                        className="text-blue-400 hover:text-blue-300 text-sm transition-colors"
                      >
                        Download
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}