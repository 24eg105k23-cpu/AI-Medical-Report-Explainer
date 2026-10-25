import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Activity, ChevronRight, FileText, UploadCloud } from 'lucide-react';
import { apiRequest, getToken } from '../api';

const Dashboard = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(Boolean(getToken()));
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (!getToken()) {
      setLoading(false);
      setDocuments([]);
      return;
    }
    let active = true;
    apiRequest('/api/v1/documents?page=1&page_size=100')
      .then((response) => { if (active) setDocuments(response.items); })
      .catch((requestError) => { if (active) setError(requestError.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const completedReports = documents.filter(
    (document) => document.document_type === 'report' && document.processing_status === 'completed',
  ).length;
  const prescriptions = documents.filter((document) => document.document_type === 'prescription').length;

  return (
    <div style={{ paddingBottom: '4rem' }}>
      <section style={{ backgroundColor: 'var(--color-primary-light)', padding: '4rem 0', textAlign: 'center' }}>
        <div className="container">
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', backgroundColor: 'white', padding: '0.5rem 1rem', borderRadius: '9999px', color: 'var(--color-primary)', fontWeight: 600, marginBottom: '1.5rem' }}>
            <Activity size={20} /> Health report analysis
          </div>
          <h1 style={{ fontSize: '3rem', fontWeight: 700, marginBottom: '1.5rem', lineHeight: 1.2 }}>
            Understand your medical reports
          </h1>
          <p style={{ fontSize: '1.125rem', color: 'var(--color-text-muted)', maxWidth: '600px', margin: '0 auto 2rem', lineHeight: 1.6 }}>
            Upload a report or prescription to extract information from your document.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button className="btn btn-primary" onClick={() => navigate('/analyze')}>
              <FileText size={20} /> Upload medical report
            </button>
            <button className="btn btn-secondary" onClick={() => navigate('/prescription')}>
              <UploadCloud size={20} /> Upload prescription
            </button>
          </div>
        </div>
      </section>

      <section className="container" style={{ marginTop: '2rem' }}>
        {!getToken() ? (
          <div className="card" style={{ textAlign: 'center' }}>
            <h2 style={{ marginBottom: '0.5rem' }}>Sign in to view your records</h2>
            <p style={{ color: 'var(--color-text-muted)', marginBottom: '1rem' }}>Only documents belonging to your account are shown.</p>
            <Link to="/login" className="btn btn-primary">Sign in or create account</Link>
          </div>
        ) : (
          <>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Your records</h2>
            {error && <p role="alert" className="card" style={{ color: 'var(--color-danger)' }}>{error}</p>}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
              <div className="card"><strong style={{ fontSize: '2rem' }}>{loading ? '—' : documents.length}</strong><div>Uploaded documents</div></div>
              <div className="card"><strong style={{ fontSize: '2rem' }}>{loading ? '—' : completedReports}</strong><div>Completed report analyses</div></div>
              <div className="card"><strong style={{ fontSize: '2rem' }}>{loading ? '—' : prescriptions}</strong><div>Uploaded prescriptions</div></div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Recent documents</h2>
              <Link to="/history" style={{ color: 'var(--color-primary)' }}>View all <ChevronRight size={16} /></Link>
            </div>
            {loading ? <p>Loading your documents…</p> : documents.length === 0 ? (
              <div className="card" style={{ textAlign: 'center', padding: '2rem' }}>
                <p style={{ color: 'var(--color-text-muted)', marginBottom: '1rem' }}>No documents have been uploaded to this account.</p>
                <button className="btn btn-primary" onClick={() => navigate('/analyze')}>Upload your first report</button>
              </div>
            ) : (
              <div style={{ display: 'grid', gap: '1rem' }}>
                {documents.slice(0, 5).map((document) => (
                  <div key={document.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
                    <div><strong>{document.original_filename}</strong><div style={{ color: 'var(--color-text-muted)' }}>{document.document_type} · {new Date(document.created_at).toLocaleString()}</div></div>
                    <span>{document.processing_status.replaceAll('_', ' ')}</span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
};

export default Dashboard;
