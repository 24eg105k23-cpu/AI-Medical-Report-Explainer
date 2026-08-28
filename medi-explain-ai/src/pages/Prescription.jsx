import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle, AlertTriangle, Pill, ShoppingCart, Activity } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { MOCK_EXTRACTED_PRESCRIPTION } from '../data/mockData';

const Prescription = () => {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState(0);
  const [results, setResults] = useState(null);
  const navigate = useNavigate();

  const stepsText = [
    'Reading prescription...',
    'Identifying medicines...',
    'Checking medicine details...'
  ];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
  };

  const handleProcess = () => {
    setProcessing(true);
    let step = 0;
    const interval = setInterval(() => {
      step++;
      if (step < stepsText.length) {
        setProcessingStep(step);
      } else {
        clearInterval(interval);
        setProcessing(false);
        setResults(MOCK_EXTRACTED_PRESCRIPTION);
      }
    }, 1500);
  };

  const handleAddToCart = (medicine) => {
    // In a real app, this would add to a cart context
    alert(`${medicine.medicineName} added to cart!`);
  };

  if (results) {
    return (
      <div className="container" style={{ padding: '3rem 0', paddingBottom: '4rem' }}>
        <div style={{ marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Medicines Found in Prescription</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>Review the medicines identified from your prescription below.</p>
        </div>

        {/* Safety notice */}
        <div className="card" style={{ borderLeft: '4px solid var(--color-warning)', marginBottom: '2rem', backgroundColor: 'var(--color-warning-light)' }}>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
            <AlertTriangle size={24} color="var(--color-warning)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h3 style={{ fontWeight: 600, marginBottom: '0.25rem', color: 'var(--color-text-main)' }}>Please verify before purchasing</h3>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9375rem' }}>Always verify prescription information with a pharmacist or doctor before purchasing any medicine. This is an AI-assisted reading and may contain errors.</p>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {results.map(med => (
            <div key={med.id} className="card" style={{ borderLeft: `4px solid ${med.status === 'verified' ? 'var(--color-success)' : 'var(--color-warning)'}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ backgroundColor: med.status === 'verified' ? 'var(--color-success-light)' : 'var(--color-warning-light)', color: med.status === 'verified' ? 'var(--color-success)' : 'var(--color-warning)', padding: '0.75rem', borderRadius: 'var(--radius-lg)' }}>
                    <Pill size={24} />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{med.medicineName}</h3>
                    <span style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>{med.strength}</span>
                  </div>
                </div>
                {med.status === 'verified' ? (
                  <span className="badge bg-success-light"><CheckCircle size={14} style={{ marginRight: '4px' }} /> Verified</span>
                ) : (
                  <span className="badge bg-warning-light"><AlertTriangle size={14} style={{ marginRight: '4px' }} /> Needs Review</span>
                )}
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', padding: '1rem', backgroundColor: 'var(--color-bg-page)', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
                <div>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem', marginBottom: '0.25rem' }}>Dosage</div>
                  <div style={{ fontWeight: 600 }}>{med.dosage}</div>
                </div>
                <div>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem', marginBottom: '0.25rem' }}>Frequency</div>
                  <div style={{ fontWeight: 600 }}>{med.frequency}</div>
                </div>
                <div>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem', marginBottom: '0.25rem' }}>Duration</div>
                  <div style={{ fontWeight: 600 }}>{med.duration}</div>
                </div>
                <div>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem', marginBottom: '0.25rem' }}>Instructions</div>
                  <div style={{ fontWeight: 600 }}>{med.instructions}</div>
                </div>
              </div>

              {med.matchedMedicine && (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <div style={{ fontSize: '0.9375rem', color: 'var(--color-text-muted)' }}>
                    <strong style={{ color: 'var(--color-text-main)' }}>₹{med.matchedMedicine.price.toFixed(2)}</strong> • {med.matchedMedicine.manufacturer}
                  </div>
                  <button className="btn btn-primary" style={{ padding: '0.5rem 1rem' }} onClick={() => handleAddToCart(med)}>
                    <ShoppingCart size={16} /> Add to Cart
                  </button>
                </div>
              )}

              {!med.matchedMedicine && (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <p style={{ fontSize: '0.9375rem', color: 'var(--color-warning)' }}>Could not match this medicine automatically. Please verify with your pharmacist.</p>
                  <button className="btn btn-secondary" style={{ padding: '0.5rem 1rem' }} onClick={() => navigate('/medicines')}>
                    Search Medicines
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={() => { setResults(null); setFile(null); }}>Upload Another Prescription</button>
          <button className="btn btn-primary" onClick={() => navigate('/cart')}><ShoppingCart size={20} /> View Cart</button>
        </div>
      </div>
    );
  }

  if (processing) {
    return (
      <div className="container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div className="animate-spin" style={{ color: 'var(--color-primary)', marginBottom: '2rem' }}>
          <Activity size={64} />
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>{stepsText[processingStep]}</h2>
        <div style={{ width: '100%', maxWidth: '400px', backgroundColor: 'var(--color-border)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
          <div style={{ width: `${((processingStep + 1) / stepsText.length) * 100}%`, backgroundColor: 'var(--color-primary)', height: '100%', transition: 'width 0.5s ease-in-out' }}></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '4rem 0', maxWidth: '800px' }}>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 700, marginBottom: '1rem' }}>Prescription Assistant</h1>
        <p style={{ fontSize: '1.125rem', color: 'var(--color-text-muted)', maxWidth: '600px', margin: '0 auto' }}>
          Upload a prescription and review the medicines identified from it before ordering.
        </p>
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
        onClick={() => document.getElementById('prescription-upload').click()}
      >
        <input
          id="prescription-upload"
          type="file"
          style={{ display: 'none' }}
          accept=".pdf,.jpg,.png"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) setFile(e.target.files[0]);
          }}
        />

        {!file ? (
          <>
            <div style={{ backgroundColor: 'var(--color-primary-light)', color: 'var(--color-primary)', width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
              <UploadCloud size={40} />
            </div>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Upload your doctor's prescription</h3>
            <p style={{ color: 'var(--color-text-muted)' }}>Supports PDF, JPG, and PNG</p>
          </>
        ) : (
          <>
            <div style={{ backgroundColor: 'var(--color-success-light)', color: 'var(--color-success)', width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
              <FileText size={40} />
            </div>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>{file.name}</h3>
            <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
              {(file.size / 1024 / 1024).toFixed(2)} MB • {file.type || 'Unknown type'}
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <button className="btn btn-secondary" onClick={(e) => { e.stopPropagation(); setFile(null); }}>Remove</button>
              <button className="btn btn-primary" onClick={(e) => { e.stopPropagation(); handleProcess(); }}>Process Prescription</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Prescription;
