'use client';
import { useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import Navbar from '@/components/Navbar';
import { uploadDocument, downloadReport } from '@/lib/api';

export default function ScanPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [downloading, setDownloading] = useState(false);
  const [mode, setMode] = useState<'upload' | 'camera'>('upload');
  const [cameraActive, setCameraActive] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setResult(null);
      setCapturedImage(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxFiles: 1,
  });

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setCameraActive(true);
    } catch (error) {
      toast.error('Could not access camera. Please check permissions.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const video = videoRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(video, 0, 0);
    const imageDataUrl = canvas.toDataURL('image/jpeg', 0.9);
    setCapturedImage(imageDataUrl);

    // Convert to File
    canvas.toBlob((blob) => {
      if (blob) {
        const capturedFile = new File([blob], 'captured_document.jpg', { type: 'image/jpeg' });
        setFile(capturedFile);
        setResult(null);
      }
    }, 'image/jpeg', 0.9);

    stopCamera();
    toast.success('Photo captured! Click Scan to analyze.');
  };

  const handleScan = async () => {
    if (!file) return;
    setScanning(true);
    try {
      const response = await uploadDocument(file);
      setResult(response.data);
      toast.success('Scan complete!');
    } catch (error: any) {
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        router.push('/login');
      } else {
        toast.error(error.response?.data?.detail || 'Scan failed');
      }
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
    setCapturedImage(null);
    stopCamera();
  };

  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar />
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">New Document Scan</h1>
          <p className="text-gray-400 mt-1">Upload or photograph a document for forensic analysis</p>
        </div>

        {/* Mode Toggle */}
        {!result && (
          <div className="flex gap-3 mb-6">
            <button
              onClick={() => { setMode('upload'); stopCamera(); setFile(null); setCapturedImage(null); }}
              className={`flex-1 py-3 rounded-xl font-semibold transition-colors flex items-center justify-center gap-2
                ${mode === 'upload' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white'}`}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Upload Document
            </button>
            <button
              onClick={() => { setMode('camera'); setFile(null); setCapturedImage(null); }}
              className={`flex-1 py-3 rounded-xl font-semibold transition-colors flex items-center justify-center gap-2
                ${mode === 'camera' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white'}`}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Use Camera
            </button>
          </div>
        )}

        {/* Upload Mode */}
        {mode === 'upload' && !result && (
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
                  <p className="text-gray-600 text-xs mt-4">Supports PDF, JPG, PNG</p>
                </div>
              )}
            </div>
          </>
        )}

        {/* Camera Mode */}
        {mode === 'camera' && !result && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
            {capturedImage ? (
              <div className="text-center">
                <img src={capturedImage} alt="Captured" className="max-h-64 mx-auto rounded-lg mb-4" />
                <p className="text-green-400 font-medium mb-3">Photo captured successfully!</p>
                <button
                  onClick={() => { setCapturedImage(null); setFile(null); startCamera(); }}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm"
                >
                  Retake Photo
                </button>
              </div>
            ) : cameraActive ? (
              <div className="text-center">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  className="w-full max-h-64 object-cover rounded-lg mb-4"
                />
                <div className="flex gap-3 justify-center">
                  <button
                    onClick={capturePhoto}
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg"
                  >
                    📷 Capture
                  </button>
                  <button
                    onClick={stopCamera}
                    className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  </svg>
                </div>
                <p className="text-white font-medium mb-2">Take a photo of your document</p>
                <p className="text-gray-400 text-sm mb-4">Position the document clearly in frame</p>
                <button
                  onClick={startCamera}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg"
                >
                  Open Camera
                </button>
              </div>
            )}
            <canvas ref={canvasRef} className="hidden" />
          </div>
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
                  <div className={`w-2 h-2 rounded-full ${result.layer3_hash?.suspicion_flag ? 'bg-red-400' : 'bg-green-400'}`} />
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