import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, CheckCircle, AlertCircle, Trash2, FileText, Filter } from 'lucide-react';
import { MOCK_REPORTS } from '../data/mockData';

const allReports = [
  ...MOCK_REPORTS,
  {
    id: 'r4',
    name: 'Thyroid Profile',
    date: '02 February 2026',
    parameters: 4,
    status: 'normal',
    type: 'Hormone Test'
  },
  {
    id: 'r5',
    name: 'Kidney Function Test',
    date: '18 January 2026',
    parameters: 6,
    status: 'attention',
    type: 'Blood Test'
  }
];

const History = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [reports, setReports] = useState(allReports);

  const filtered = reports.filter(r => {
    const matchesSearch = r.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || r.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const handleDelete = (id) => {
    setReports(prev => prev.filter(r => r.id !== id));
  };

  return (
    <div className="container" style={{ padding: '3rem 0', paddingBottom: '4rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Report History</h1>
        <p style={{ color: 'var(--color-text-muted)' }}>View and manage all your analyzed medical reports.</p>
      </div>

      {/* Search and Filters */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '250px' }}>
          <Search size={20} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-light)' }} />
          <input
            type="text"
            placeholder="Search reports..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem 1rem 0.75rem 3rem',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              fontSize: '1rem',
              fontFamily: 'var(--font-family)',
              outline: 'none'
            }}
          />
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <Filter size={18} color="var(--color-text-muted)" />
          {['all', 'normal', 'attention'].map(status => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className="badge"
              style={{
                border: filterStatus === status ? '2px solid var(--color-primary)' : '1px solid var(--color-border)',
                backgroundColor: filterStatus === status ? 'var(--color-primary-light)' : 'white',
                color: filterStatus === status ? 'var(--color-primary)' : 'var(--color-text-muted)',
                cursor: 'pointer',
                textTransform: 'capitalize',
                fontWeight: filterStatus === status ? 600 : 400
              }}
            >
              {status === 'all' ? 'All' : status === 'normal' ? 'Normal' : 'Needs Attention'}
            </button>
          ))}
        </div>
      </div>

      {/* Report List */}
      {filtered.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <FileText size={64} color="var(--color-text-light)" style={{ marginBottom: '1rem' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>No reports found</h3>
          <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
            {searchTerm ? 'Try a different search term.' : 'Upload your first medical report to get started.'}
          </p>
          <Link to="/analyze" className="btn btn-primary">Analyze a Report</Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {filtered.map(report => (
            <div key={report.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1, minWidth: '200px' }}>
                <div style={{ backgroundColor: 'var(--color-primary-light)', color: 'var(--color-primary)', padding: '0.75rem', borderRadius: 'var(--radius-lg)' }}>
                  <FileText size={24} />
                </div>
                <div>
                  <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.25rem' }}>{report.name}</h3>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>{report.date} • {report.type} • {report.parameters} parameters</div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                {report.status === 'normal' ? (
                  <span className="badge bg-success-light"><CheckCircle size={14} style={{ marginRight: '4px' }} /> Normal</span>
                ) : (
                  <span className="badge bg-warning-light"><AlertCircle size={14} style={{ marginRight: '4px' }} /> Attention</span>
                )}
                <Link to="/analyze" className="btn btn-secondary" style={{ padding: '0.5rem 1rem' }}>View</Link>
                <button
                  className="btn"
                  onClick={() => handleDelete(report.id)}
                  style={{ padding: '0.5rem', background: 'none', border: 'none', color: 'var(--color-text-light)' }}
                  title="Delete report"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;
