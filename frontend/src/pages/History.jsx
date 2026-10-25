import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Search, Trash2 } from 'lucide-react';
import { apiRequest, getToken } from '../api';

const History = () => {
  const [documents, setDocuments] = useState([]);
  const [search, setSearch] = useState('');
  const [type, setType] = useState('all');
  const [loading, setLoading] = useState(Boolean(getToken()));
  const [error, setError] = useState('');

  const loadDocuments = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await apiRequest('/api/v1/documents?page=1&page_size=100');
      setDocuments(result.items);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (getToken()) loadDocuments();
    else setLoading(false);
  }, []);

  const filtered = useMemo(() => documents.filter((document) => {
    const matchesName = document.original_filename.toLowerCase().includes(search.toLowerCase());
    const matchesType = type === 'all' || document.document_type === type;
    return matchesName && matchesType;
  }), [documents, search, type]);

  const deleteDocument = async (document) => {
    if (!window.confirm(`Delete "${document.original_filename}" and its extracted data? This cannot be undone.`)) return;
    try {
      await apiRequest(`/api/v1/documents/${document.id}`, { method: 'DELETE' });
      setDocuments((current) => current.filter((item) => item.id !== document.id));
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  return (
    <div className="container" style={{ padding: '3rem 0', paddingBottom: '4rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Your documents</h1>
        <p style={{ color: 'var(--color-text-muted)' }}>Documents uploaded to your account.</p>
      </div>

      {!getToken() ? (
        <div className="card" style={{ textAlign: 'center' }}>
          <p style={{ marginBottom: '1rem' }}>Sign in to view your documents.</p>
          <Link to="/login" className="btn btn-primary">Sign in</Link>
        </div>
      ) : (
        <>
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: 1, minWidth: '220px' }}>
              <Search size={18} />
              <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search filenames" style={inputStyle} />
            </label>
            <select value={type} onChange={(event) => setType(event.target.value)} style={inputStyle}>
              <option value="all">All document types</option>
              <option value="report">Reports</option>
              <option value="prescription">Prescriptions</option>
            </select>
          </div>
          {error && <p role="alert" style={{ color: 'var(--color-danger)', marginBottom: '1rem' }}>{error}</p>}
          {loading ? <p>Loading your documents…</p> : filtered.length === 0 ? (
            <div className="card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
              <FileText size={40} color="var(--color-text-light)" style={{ marginBottom: '1rem' }} />
              <h2 style={{ marginBottom: '0.5rem' }}>{documents.length ? 'No matching documents' : 'No documents yet'}</h2>
              <p style={{ color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
                {documents.length ? 'Try changing your search or filter.' : 'Uploaded medical documents will appear here.'}
              </p>
              {!documents.length && <Link to="/analyze" className="btn btn-primary">Upload a report</Link>}
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '1rem' }}>
              {filtered.map((document) => (
                <div key={document.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <FileText size={24} color="var(--color-primary)" />
                    <div>
                      <strong>{document.original_filename}</strong>
                      <div style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
                        {document.document_type} · {new Date(document.created_at).toLocaleString()} · {(document.file_size / 1024).toFixed(1)} KB
                      </div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <span className="badge">{document.processing_status.replaceAll('_', ' ')}</span>
                    <button className="btn" aria-label={`Delete ${document.original_filename}`} onClick={() => deleteDocument(document)} style={{ color: 'var(--color-danger)' }}>
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

const inputStyle = {
  padding: '0.75rem',
  border: '1px solid var(--color-border)',
  borderRadius: 'var(--radius-md)',
  background: 'white',
  font: 'inherit',
};

export default History;
