'use client';
import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import Navbar from '@/components/Navbar';
import { downloadReport } from '@/lib/api';

export default function ScanPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [downloading, setDownloading] = useState(false);
  const [docType, setDocType] = useState<string>('official_pdf');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setResult(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
  });

  const handleScan = async () => {
    if (!file) return;
    setScanning(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('doc_type', docType);
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/scan/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      if (response.status === 401) {
        toast.error('Session expired. Please login again.');
        router.push('/login');
        return;
      }
      if (!response.ok) {
        const err = await response.json();
        toast.error(err.detail || 'Scan failed');
        return;
      }
      const data = await response.json();
      setResult(data);
      toast.success('Scan complete!');
    } catch (error: any) {
      toast.error('Scan failed. Please try again.');
    } finally {
      setScanning(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!result) return;
    setDownloading(true);
    try {
      const response = await downloadReport(result.scan_id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `SecureScan_Report_${result.scan_id.slice(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Report downloaded!');
    } catch (error) {
      toast.error('Failed to download report');
    } finally {
      setDownloading(false);
    }
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'AUTHENTIC': return 'text-green-400 border-green-400 bg-green-400/10';
      case 'SUSPICIOUS': return 'text-yellow-400 border-yellow-400 bg-yellow-400/10';
      case 'LIKELY FORGED': return 'text-orange-400 border-orange-400 bg-orange-400/10';
      case 'FORGED': return 'text-red-400 border-red-400 bg-red-400/10';
      default: return 'text-gray-400 border-gray-400 bg-gray-400/10';
    }
  };

  const resetScan = () => {
    setFile(null);
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4 sm:py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">New Document Scan</h1>
          <p className="text-gray-400 mt-1">Upload a document for forensic analysis</p>
        </div>

        {/* Document Type Selector */}
        {!result && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Document Type
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { value: 'official_pdf', label: 'Official PDF', icon: '📄', desc: 'Downloaded PDF document' },
                { value: 'scanned', label: 'Scanned Copy', icon: '🖨', desc: 'Physically scanned document' },
                { value: 'phone_photo', label: 'Phone Photo', icon: '📷', desc: 'Photo taken with phone camera' },
                { value: 'downloaded', label: 'Downloaded File', icon: '⬇️', desc: 'File sent via WhatsApp/email' },
              ].map(dt => (
                <button
                  key={dt.value}
                  onClick={() => setDocType(dt.value)}
                  className={`p-3 rounded-xl border-2 text-left transition-all ${
                    docType === dt.value
                      ? 'border-blue-500 bg-blue-500/10'
                      : 'border-gray-700 bg-gray-900 hover:border-gray-600'
                  }`}
                >
                  <div className="text-2xl mb-1">{dt.icon}</div>
                  <div className="text-white text-sm font-medium">{dt.label}</div>
                  <div className="text-gray-500 text-xs mt-1">{dt.desc}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Upload Area */}
        {!result && (
          <>
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors mb-6
                ${isDragActive ? 'border-blue-500 bg-blue-500/10'
                  : file ? 'border-green-500 bg-green-500/5'
                  : 'border-gray-700 bg-gray-900 hover:border-gray-600'}`}
            >
              <input {...getInputProps()} />
              {file ? (
                <div>
                  <div className="w-16 h-16 bg-green-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-white font-medium text-lg">{file.name}</p>
                  <p className="text-gray-400 text-sm mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                  <p className="text-gray-500 text-sm mt-3">Click or drag to change file</p>
                </div>
              ) : (
                <div>
                  <div className="w-16 h-16 bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <p className="text-white font-medium text-lg">
                    {isDragActive ? 'Drop your document here' : 'Drag & drop your document'}
                  </p>
                  <p className="text-gray-400 text-sm mt-2">or click to browse files</p>
                  <p className="text-gray-600 text-xs mt-4">Supports PDF, JPG, PNG, DOCX</p>
                  <p className="text-gray-600 text-xs mt-1">Please upload document images only (certificates, transcripts, ID cards)</p>
                </div>
              )}
            </div>
          </>
        )}

        {/* Scan Button */}
        {file && !result && (
          <button
            onClick={handleScan}
            disabled={scanning}
            className="w-full py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white font-bold text-lg rounded-xl transition-colors"
          >
            {scanning ? (
              <span className="flex items-center justify-center gap-3">
                <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Running Forensic Analysis...
              </span>
            ) : 'Run Forensic Scan'}
          </button>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            <div className={`border-2 rounded-xl p-6 text-center ${getVerdictColor(result.risk_verdict)}`}>
              <p className="text-4xl font-black">{result.risk_verdict}</p>
              <p className="text-2xl font-bold mt-1">Risk Score: {result.risk_score}/100</p>
              <p className="mt-2 opacity-80">{result.recommendation}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <div className={`w-2 h-2 rounded-full ${result.layer1_metadata?.suspicion_flag ? 'bg-red-400' : 'bg-green-400'}`} />
                  <h3 className="text-white font-semibold text-sm">Layer 1 — Metadata</h3>
                </div>
                <p className="text-gray-400 text-xs">{result.layer1_metadata?.anomaly_count || 0} anomalies detected</p>
                <p className="text-gray-500 text-xs mt-1">Completeness: {result.layer1_metadata?.completeness_score || 0}%</p>
                {result.layer1_metadata?.anomalies?.length > 0 && (
                  <div className="mt-3 space-y-1">
                    {result.layer1_metadata.anomalies.map((a: any, i: number) => (
                      <div key={i} className="text-xs text-orange-400 bg-orange-400/10 px-2 py-1 rounded">
                        {a.rule_id}: {a.severity}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <div className={`w-2 h-2 rounded-full ${result.layer2_ela?.suspicion_flag ? 'bg-red-400' : 'bg-green-400'}`} />
                  <h3 className="text-white font-semibold text-sm">Layer 2 — ELA</h3>
                </div>
                <p className="text-gray-400 text-xs">ELA Score: {result.layer2_ela?.ela_score?.toFixed(4) || '0.0000'}</p>
                <p className="text-gray-500 text-xs mt-1">{result.layer2_ela?.interpretation}</p>
              </div>

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <div className={`w-2 h-2 rounded-full ${result.layer3_hash?.match_status === 'MATCH' ? 'bg-green-400' : 'bg-red-400'}`} />
                  <h3 className="text-white font-semibold text-sm">Layer 3 — Hash</h3>
                </div>
                <p className="text-gray-400 text-xs">Status: {result.layer3_hash?.match_status}</p>
                <p className="text-gray-500 text-xs mt-1 break-all font-mono">{result.sha256_hash?.slice(0, 20)}...</p>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleDownloadReport}
                disabled={downloading}
                className="flex-1 py-3 bg-green-600 hover:bg-green-700 disabled:bg-green-800 text-white font-semibold rounded-xl transition-colors"
              >
                {downloading ? 'Generating...' : 'Download Forensic Certificate'}
              </button>
              <button
                onClick={resetScan}
                className="px-6 py-3 bg-gray-800 hover:bg-gray-700 text-white font-semibold rounded-xl transition-colors"
              >
                Scan Another
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}