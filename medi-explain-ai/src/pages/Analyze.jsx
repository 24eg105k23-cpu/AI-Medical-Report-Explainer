import React, { useState, useEffect } from 'react';
import { UploadCloud, FileText, CheckCircle, AlertCircle, Search, Copy, Download, Share2, ChevronLeft, ChevronDown, ChevronUp, Activity } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { MOCK_REPORT_DETAILS } from '../data/mockData';

const Analyze = () => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [results, setResults] = useState(null);
  const [expandedTerm, setExpandedTerm] = useState(null);
  const navigate = useNavigate();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleAnalyze = () => {
    setAnalyzing(true);
    // Simulate multi-step analysis
    const steps = [
      'Reading report...',
      'Identifying medical values...',
      'Understanding medical terminology...',
      'Preparing your explanation...'
    ];
    
    let currentStep = 0;
    const interval = setInterval(() => {
      currentStep++;
      if (currentStep < steps.length) {
        setAnalysisStep(currentStep);
      } else {
        clearInterval(interval);
        setAnalyzing(false);
        setResults(MOCK_REPORT_DETAILS.r1); // Always mock CBC for demo
      }
    }, 1500);
  };

  const stepsText = [
    'Reading report...',
    'Identifying medical values...',
    'Understanding medical terminology...',
    'Preparing your explanation...'
  ];

  if (results) {
    return (
      <div className="container" style={{ padding: '2rem 0', paddingBottom: '4rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div>
            <button className="btn" style={{ padding: '0.5rem 0', background: 'none', color: 'var(--color-primary)' }} onClick={() => navigate('/')}>
              <ChevronLeft size={20} /> Back to Dashboard
            </button>
            <h1 style={{ fontSize: '2rem', fontWeight: 700, marginTop: '0.5rem' }}>Report Analysis</h1>
            <div style={{ color: 'var(--color-text-muted)' }}>{results.name} • {results.date}</div>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn btn-secondary"><Download size={20} /> Download Summary</button>
            <button className="btn btn-secondary"><Share2 size={20} /> Share</button>
          </div>
        </div>

        {/* Overall Summary */}
        <div className="card" style={{ marginBottom: '2rem', borderLeft: '4px solid var(--color-primary)' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>Simple Summary</h2>
          <p style={{ fontSize: '1.125rem', color: 'var(--color-text-main)' }}>{results.summary}</p>
        </div>

        {/* Health Status Overview */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
          <div className="card" style={{ textAlign: 'center', backgroundColor: 'var(--color-success-light)', border: 'none' }}>
            <div style={{ fontSize: '3rem', fontWeight: 700, color: 'var(--color-success)' }}>{results.stats.normal}</div>
            <div style={{ color: 'var(--color-success)', fontWeight: 600 }}>Normal</div>
          </div>
          <div className="card" style={{ textAlign: 'center', backgroundColor: 'var(--color-danger-light)', border: 'none' }}>
            <div style={{ fontSize: '3rem', fontWeight: 700, color: 'var(--color-danger)' }}>{results.stats.high}</div>
            <div style={{ color: 'var(--color-danger)', fontWeight: 600 }}>High</div>
          </div>
          <div className="card" style={{ textAlign: 'center', backgroundColor: 'var(--color-warning-light)', border: 'none' }}>
            <div style={{ fontSize: '3rem', fontWeight: 700, color: 'var(--color-warning)' }}>{results.stats.low}</div>
            <div style={{ color: 'var(--color-warning)', fontWeight: 600 }}>Low</div>
          </div>
        </div>

        {/* Abnormal Values */}
        {(results.stats.high > 0 || results.stats.low > 0) && (
          <div style={{ marginBottom: '3rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1.5rem', color: 'var(--color-danger)' }}>Values That May Need Attention</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {results.parameters.filter(p => p.status !== 'normal').map(param => (
                <div key={param.id} className="card" style={{ borderLeft: `4px solid var(--color-${param.status === 'high' ? 'danger' : 'warning'})` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{param.name}</h3>
                    <span className={`badge bg-${param.status === 'high' ? 'danger' : 'warning'}-light`} style={{ textTransform: 'capitalize' }}>
                      <AlertCircle size={14} style={{ marginRight: '4px' }} /> {param.status}
                    </span>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem', padding: '1rem', backgroundColor: 'var(--color-bg-page)', borderRadius: 'var(--radius-md)' }}>
                    <div>
                      <div style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>Current Value</div>
                      <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{param.value} <span style={{ fontSize: '1rem', fontWeight: 400, color: 'var(--color-text-muted)' }}>{param.unit}</span></div>
                    </div>
                    <div>
                      <div style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>Reference Range</div>
                      <div style={{ fontSize: '1.125rem', fontWeight: 500 }}>{param.range}</div>
                    </div>
                  </div>
                  <p style={{ color: 'var(--color-text-main)' }}><strong>Explanation:</strong> {param.explanation}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* All Parameters */}
        <div style={{ marginBottom: '3rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>All Report Parameters</h2>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className="badge bg-primary-light" style={{ border: 'none', cursor: 'pointer' }}>All</button>
              <button className="badge" style={{ border: '1px solid var(--color-border)', backgroundColor: 'white', cursor: 'pointer' }}>Normal</button>
              <button className="badge" style={{ border: '1px solid var(--color-border)', backgroundColor: 'white', cursor: 'pointer' }}>Abnormal</button>
            </div>
          </div>
          
          <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead style={{ backgroundColor: 'var(--color-bg-page)', borderBottom: '1px solid var(--color-border)' }}>
                <tr>
                  <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600 }}>Parameter</th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600 }}>Value</th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600 }}>Range</th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600 }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {results.parameters.map((param, index) => (
                  <tr key={param.id} style={{ borderBottom: index < results.parameters.length - 1 ? '1px solid var(--color-border)' : 'none' }}>
                    <td style={{ padding: '1rem', fontWeight: 500 }}>{param.name}</td>
                    <td style={{ padding: '1rem', fontWeight: 700 }}>{param.value} <span style={{ fontSize: '0.875rem', fontWeight: 400, color: 'var(--color-text-muted)' }}>{param.unit}</span></td>
                    <td style={{ padding: '1rem', color: 'var(--color-text-muted)' }}>{param.range}</td>
                    <td style={{ padding: '1rem' }}>
                      <span className={`badge bg-${param.status === 'normal' ? 'success' : (param.status === 'high' ? 'danger' : 'warning')}-light`}>
                        {param.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Medical Terms */}
        <div style={{ marginBottom: '3rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1.5rem' }}>Medical Terms Explained</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {results.parameters.map(param => (
              <div key={param.id} className="card" style={{ padding: '1rem' }}>
                <div 
                  style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
                  onClick={() => setExpandedTerm(expandedTerm === param.id ? null : param.id)}
                >
                  <h3 style={{ fontSize: '1.125rem', fontWeight: 600 }}>{param.name}</h3>
                  {expandedTerm === param.id ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </div>
                {expandedTerm === param.id && (
                  <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--color-border)' }}>
                    <p style={{ marginBottom: '0.5rem' }}><strong>Technical meaning:</strong> {param.termMeaning}</p>
                    <p style={{ color: 'var(--color-text-muted)' }}><strong>Simple explanation:</strong> {param.explanation}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Questions for Doctor */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Questions You May Want to Ask Your Doctor</h2>
            <button className="btn btn-secondary" style={{ padding: '0.5rem 1rem' }}><Copy size={16} /> Copy All Questions</button>
          </div>
          <div className="card">
            <ul style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {results.questions.map((q, i) => (
                <li key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', paddingBottom: '1rem', borderBottom: i < results.questions.length - 1 ? '1px solid var(--color-border)' : 'none' }}>
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                    <div style={{ backgroundColor: 'var(--color-primary-light)', color: 'var(--color-primary)', width: '24px', height: '24px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontWeight: 600 }}>{i + 1}</div>
                    <span style={{ fontSize: '1.125rem', color: 'var(--color-text-main)' }}>{q}</span>
                  </div>
                  <button className="btn" style={{ background: 'none', border: 'none', color: 'var(--color-text-muted)', padding: '0.25rem' }}><Copy size={18} /></button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    );
  }

  if (analyzing) {
    return (
      <div className="container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div className="animate-spin" style={{ color: 'var(--color-primary)', marginBottom: '2rem' }}>
          <Activity size={64} />
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>{stepsText[analysisStep]}</h2>
        <div style={{ width: '100%', maxWidth: '400px', backgroundColor: 'var(--color-border)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
          <div style={{ width: `${((analysisStep + 1) / stepsText.length) * 100}%`, backgroundColor: 'var(--color-primary)', height: '100%', transition: 'width 0.5s ease-in-out' }}></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '4rem 0', maxWidth: '800px' }}>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 700, marginBottom: '1rem' }}>Analyze Medical Report</h1>
        <p style={{ fontSize: '1.125rem', color: 'var(--color-text-muted)' }}>Upload your lab results or medical report for a simple, easy-to-understand explanation.</p>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', justifyContent: 'center' }}>
        <button className="btn btn-primary" style={{ flex: 1, maxWidth: '200px' }}>Upload File</button>
        <button className="btn btn-secondary" style={{ flex: 1, maxWidth: '200px' }}>Paste Text</button>
      </div>

      <div 
        className={`card ${dragActive ? 'bg-primary-light' : ''}`}
        style={{ 
          border: `2px dashed ${dragActive ? 'var(--color-primary)' : 'var(--color-border)'}`, 
          padding: '4rem 2rem', 
          textAlign: 'center',
          transition: 'all 0.2s',
          cursor: 'pointer'
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-upload').click()}
      >
        <input 
          id="file-upload" 
          type="file" 
          style={{ display: 'none' }} 
          accept=".pdf,.jpg,.png" 
          onChange={(e) => {
            if(e.target.files && e.target.files[0]) {
              setFile(e.target.files[0]);
            }
          }}
        />
        
        {!file ? (
          <>
            <div style={{ backgroundColor: 'var(--color-primary-light)', color: 'var(--color-primary)', width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
              <UploadCloud size={40} />
            </div>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Drop your medical report here</h3>
            <p style={{ color: 'var(--color-text-muted)' }}>Supports PDF, JPG, and PNG</p>
          </>
        ) : (
          <>
            <div style={{ backgroundColor: 'var(--color-success-light)', color: 'var(--color-success)', width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
              <FileText size={40} />
            </div>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>{file.name}</h3>
            <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>{(file.size / 1024 / 1024).toFixed(2)} MB • {file.type || 'Unknown type'}</p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <button 
                className="btn btn-secondary" 
                onClick={(e) => { e.stopPropagation(); setFile(null); }}
              >
                Remove
              </button>
              <button 
                className="btn btn-primary"
                onClick={(e) => { e.stopPropagation(); handleAnalyze(); }}
              >
                Analyze Report
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Analyze;
