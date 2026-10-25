import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FileText, Pill, Clock, Search, UploadCloud, ChevronRight, Activity, CheckCircle, AlertCircle } from 'lucide-react';
import { MOCK_REPORTS } from '../data/mockData';

const Dashboard = () => {
  const navigate = useNavigate();
  
  return (
    <div style={{ paddingBottom: '4rem' }}>
      {/* Hero Section */}
      <section style={{ backgroundColor: 'var(--color-primary-light)', padding: '4rem 0', textAlign: 'center' }}>
        <div className="container">
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', backgroundColor: 'white', padding: '0.5rem 1rem', borderRadius: '9999px', color: 'var(--color-primary)', fontWeight: 600, marginBottom: '1.5rem', boxShadow: 'var(--shadow-sm)' }}>
            <Activity size={20} />
            <span>AI-Powered Health Insights</span>
          </div>
          
          <h1 style={{ fontSize: '3rem', fontWeight: 700, color: 'var(--color-text-main)', marginBottom: '1.5rem', lineHeight: 1.2 }}>
            Understand Your Health Reports<br />with AI
          </h1>
          
          <p style={{ fontSize: '1.25rem', color: 'var(--color-text-muted)', maxWidth: '600px', margin: '0 auto 2.5rem', lineHeight: 1.6 }}>
            Upload your medical report or prescription and get an easy-to-understand explanation of important information.
          </p>
          
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button 
              className="btn btn-primary" 
              style={{ fontSize: '1.125rem', padding: '1rem 2rem' }}
              onClick={() => navigate('/analyze')}
            >
              <FileText size={24} />
              Analyze Medical Report
            </button>
            <button 
              className="btn btn-secondary" 
              style={{ fontSize: '1.125rem', padding: '1rem 2rem' }}
              onClick={() => navigate('/prescription')}
            >
              <UploadCloud size={24} />
              Upload Prescription
            </button>
          </div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="container" style={{ marginTop: '-2rem', position: 'relative', zIndex: 10 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          {[
            { title: 'Analyze Report', icon: <FileText size={24} />, desc: 'Understand your lab results', link: '/analyze', color: 'var(--color-primary)' },
            { title: 'Upload Prescription', icon: <UploadCloud size={24} />, desc: 'Review medicines to order', link: '/prescription', color: 'var(--color-success)' },
            { title: 'View Report History', icon: <Clock size={24} />, desc: 'Access past analysis', link: '/history', color: 'var(--color-warning)' },
            { title: 'Browse Medicines', icon: <Search size={24} />, desc: 'Search pharmacy catalog', link: '/medicines', color: 'var(--color-text-main)' }
          ].map((action, i) => (
            <Link key={i} to={action.link} className="card" style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', cursor: 'pointer', border: 'none', textDecoration: 'none' }}>
              <div style={{ backgroundColor: `${action.color}15`, color: action.color, padding: '1rem', borderRadius: 'var(--radius-lg)' }}>
                {action.icon}
              </div>
              <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '0.25rem' }}>{action.title}</h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>{action.desc}</p>
              </div>
              <ChevronRight size={20} color="var(--color-text-light)" />
            </Link>
          ))}
        </div>
      </section>

      {/* Stats Summary */}
      <section className="container" style={{ marginTop: '4rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1.5rem' }}>Dashboard Overview</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--color-primary)', marginBottom: '0.5rem' }}>3</div>
            <div style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Reports Analyzed</div>
          </div>
          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--color-warning)', marginBottom: '0.5rem' }}>2</div>
            <div style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Abnormal Findings</div>
          </div>
          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--color-success)', marginBottom: '0.5rem' }}>1</div>
            <div style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Prescriptions Uploaded</div>
          </div>
          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--color-text-main)', marginBottom: '0.5rem' }}>2</div>
            <div style={{ color: 'var(--color-text-muted)', fontWeight: 500 }}>Medicines in Cart</div>
          </div>
        </div>
      </section>

      {/* Recent Reports */}
      <section className="container" style={{ marginTop: '4rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Recent Reports</h2>
          <Link to="/history" style={{ color: 'var(--color-primary)', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            View All <ChevronRight size={16} />
          </Link>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {MOCK_REPORTS.map((report) => (
            <div key={report.id} className="card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '0.25rem' }}>{report.name}</h3>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>{report.date}</div>
                </div>
                {report.status === 'normal' ? (
                  <span className="badge bg-success-light"><CheckCircle size={14} style={{ marginRight: '4px' }} /> Normal</span>
                ) : (
                  <span className="badge bg-warning-light"><AlertCircle size={14} style={{ marginRight: '4px' }} /> Attention</span>
                )}
              </div>
              
              <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.5rem', fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                <div>
                  <span style={{ fontWeight: 600, color: 'var(--color-text-main)' }}>{report.parameters}</span> Parameters
                </div>
                <div>
                  <span style={{ fontWeight: 600, color: 'var(--color-text-main)' }}>{report.type}</span>
                </div>
              </div>
              
              <button className="btn btn-secondary" style={{ width: '100%', marginTop: 'auto' }} onClick={() => navigate('/analyze')}>
                View Report
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
