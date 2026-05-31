'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import toast from 'react-hot-toast';

export default function TemplatesPage() {
  const router = useRouter();
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    institution_name: '',
    document_type: '',
    document_description: '',
    sha256_hash: ''
  });

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/admin/templates', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (res.status === 403) {
        toast.error('Admin access required');
        router.push('/dashboard');
        return;
      }
      const data = await res.json();
      setTemplates(data);
    } catch (error) {
      toast.error('Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!form.institution_name || !form.document_type || !form.sha256_hash) {
      toast.error('Please fill in all required fields');
      return;
    }
    if (form.sha256_hash.length !== 64) {
      toast.error('SHA-256 hash must be exactly 64 characters');
      return;
    }
    setAdding(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/admin/templates', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(form)
      });
      if (res.ok) {
        toast.success('Template added successfully');
        setForm({ institution_name: '', document_type: '', document_description: '', sha256_hash: '' });
        setShowForm(false);
        fetchTemplates();
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Failed to add template');
      }
    } catch (error) {
      toast.error('Failed to add template');
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (id: string, docType: string) => {
    if (!confirm(`Delete template for "${docType}"?`)) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/admin/templates/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (res.ok) {
        toast.success('Template deleted');
        fetchTemplates();
      }
    } catch (error) {
      toast.error('Failed to delete template');
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
      <div className="max-w-5xl mx-auto px-6 py-8">

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <button
              onClick={() => router.push('/admin')}
              className="text-gray-400 hover:text-white text-sm mb-2 flex items-center gap-1"
            >
              ← Back to Admin Dashboard
            </button>
            <h1 className="text-2xl font-bold text-white">Hash Template Database</h1>
            <p className="text-gray-400 mt-1">
              Register SHA-256 hash fingerprints of authentic documents for Layer 3 verification
            </p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
          >
            {showForm ? 'Cancel' : '+ Add Template'}
          </button>
        </div>

        {/* How it works info box */}
        <div className="bg-blue-600/10 border border-blue-600/30 rounded-xl p-5 mb-6">
          <h3 className="text-blue-400 font-semibold mb-2">How Hash Templates Work</h3>
          <p className="text-gray-400 text-sm">
            To register a document: scan it with SecureScan, copy its SHA-256 hash from the scan result,
            then add it here with the institution name and document type. When someone uploads that exact
            document in the future, SecureScan will return <span className="text-green-400 font-medium">MATCH</span> — 
            confirming it is identical to the authenticated original. Any modification returns <span className="text-red-400 font-medium">NO_MATCH</span>.
          </p>
        </div>

        {/* Add Template Form */}
        {showForm && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
            <h2 className="text-white font-semibold text-lg mb-4">Add New Template</h2>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Institution Name <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={form.institution_name}
                  onChange={e => setForm({ ...form, institution_name: e.target.value })}
                  placeholder="e.g. University of Bamenda"
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Document Type <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={form.document_type}
                  onChange={e => setForm({ ...form, document_type: e.target.value })}
                  placeholder="e.g. Academic Transcript"
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Document Description
              </label>
              <input
                type="text"
                value={form.document_description}
                onChange={e => setForm({ ...form, document_description: e.target.value })}
                placeholder="e.g. UBa COLTECH 2024 Semester 2 Result Slip"
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
            </div>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                SHA-256 Hash <span className="text-red-400">*</span>
                <span className="text-gray-500 font-normal ml-2">(64 characters — copy from scan result)</span>
              </label>
              <input
                type="text"
                value={form.sha256_hash}
                onChange={e => setForm({ ...form, sha256_hash: e.target.value.toLowerCase().trim() })}
                placeholder="e.g. a1b2c3d4e5f6..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 font-mono text-sm"
              />
              {form.sha256_hash && (
                <p className={`text-xs mt-1 ${form.sha256_hash.length === 64 ? 'text-green-400' : 'text-red-400'}`}>
                  {form.sha256_hash.length}/64 characters
                </p>
              )}
            </div>
            <button
              onClick={handleAdd}
              disabled={adding}
              className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-green-800 text-white font-semibold rounded-lg transition-colors"
            >
              {adding ? 'Adding...' : 'Add Template'}
            </button>
          </div>
        )}

        {/* Templates List */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
            <h2 className="text-white font-semibold">
              Registered Templates ({templates.length})
            </h2>
          </div>

          {templates.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg mb-2">No templates registered yet</p>
              <p className="text-sm">Add your first hash template to enable Layer 3 hash verification</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-800">
              {templates.map(t => (
                <div key={t.id} className="px-6 py-4 flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <span className="text-white font-medium">{t.institution_name}</span>
                      <span className="px-2 py-0.5 bg-blue-600/20 text-blue-400 text-xs rounded">
                        {t.document_type}
                      </span>
                    </div>
                    {t.document_description && (
                      <p className="text-gray-400 text-sm mb-1">{t.document_description}</p>
                    )}
                    <p className="text-gray-600 text-xs font-mono">{t.sha256_hash}</p>
                    <p className="text-gray-600 text-xs mt-1">
                      Added: {new Date(t.added_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDelete(t.id, t.document_type)}
                    className="ml-4 px-3 py-1 bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white text-xs rounded transition-colors"
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}