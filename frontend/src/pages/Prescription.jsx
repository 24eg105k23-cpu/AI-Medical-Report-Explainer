import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, FileText, UploadCloud } from 'lucide-react';
import { apiRequest, getToken } from '../api';

const Prescription = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState('');

  const processPrescription = async (event) => {
    event.preventDefault();
    if (!file) return;
    setWorking(true);
    setError('');
    try {
      const form = new FormData();
      form.append('file', file);
      form.append('document_type', 'prescription');
      const document = await apiRequest('/api/v1/documents/upload', { method: 'POST', body: form });
      const prescription = await apiRequest(`/api/v1/documents/${document.id}/process-prescription`, { method: 'POST' });
      setResult({ ...prescription, originalFilename: document.original_filename });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setWorking(false);
    }
  };

  return (
    <div className="container" style={{ padding: '3rem 0', maxWidth: '850px' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Prescription extraction</h1>
      <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>Medicine details shown here are extracted from the prescription you upload. OCR may be inaccurate; confirm every detail with a pharmacist or clinician.</p>
      {!getToken() ? (
        <div className="card" style={{ textAlign: 'center' }}>
          <p style={{ marginBottom: '1rem' }}>Sign in to securely upload and view prescriptions.</p>
          <Link to="/login" className="btn btn-primary">Sign in</Link>
        </div>
      ) : (
        <>
          {!result && (
            <form className="card" onSubmit={processPrescription}>
              <label htmlFor="prescription-file" style={{ display: 'block', padding: '3rem 1rem', textAlign: 'center', border: '2px dashed var(--color-border)', borderRadius: 'var(--radius-md)', cursor: 'pointer' }}>
                {file ? <FileText size={40} color="var(--color-primary)" /> : <UploadCloud size={40} color="var(--color-primary)" />}
                <span style={{ display: 'block', marginTop: '1rem', fontWeight: 600 }}>{file?.name || 'Choose a prescription (PDF, PNG, or JPEG)'}</span>
              </label>
              <input id="prescription-file" type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={(event) => setFile(event.target.files?.[0] || null)} style={{ display: 'none' }} />
              <button className="btn btn-primary" type="submit" disabled={!file || working} style={{ width: '100%', marginTop: '1rem' }}>
                {working ? 'Uploading and extracting…' : 'Upload and extract'}
              </button>
            </form>
          )}
          {error && <p role="alert" style={{ color: 'var(--color-danger)', marginTop: '1rem' }}>{error}</p>}
          {result && (
            <section style={{ marginTop: '1.5rem' }}>
              <h2 style={{ marginBottom: '0.5rem' }}>{result.originalFilename}</h2>
              <div className="card" style={{ background: 'var(--color-warning-light)', marginBottom: '1rem' }}>
                <AlertTriangle size={18} /> Extracted values are unverified. Do not use them to change or start a medication.
              </div>
              {result.items.length === 0 ? (
                <div className="card">No medicine details could be extracted from this prescription.</div>
              ) : result.items.map((item) => (
                <article className="card" key={item.id} style={{ marginBottom: '1rem' }}>
                  <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>{item.extracted_medicine_name}</h3>
                  <dl style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '0.75rem' }}>
                    <Detail label="Strength" value={item.extracted_strength} />
                    <Detail label="Instructions" value={item.extracted_instructions} />
                    <Detail label="Frequency" value={item.frequency} />
                    <Detail label="Duration" value={item.duration} />
                    <Detail label="Route" value={item.route} />
                    <Detail label="Review status" value={item.verification_status.replaceAll('_', ' ')} />
                  </dl>
                  {item.confidence_metadata?.needs_human_confirmation && (
                    <p style={{ color: 'var(--color-warning)', marginTop: '0.75rem' }}>This extraction needs human confirmation.</p>
                  )}
                </article>
              ))}
              <button className="btn btn-secondary" onClick={() => { setResult(null); setFile(null); }}>Upload another prescription</button>
            </section>
          )}
        </>
      )}
    </div>
  );
};

const Detail = ({ label, value }) => (
  <div><dt style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>{label}</dt><dd>{value || 'Not extracted'}</dd></div>
);

export default Prescription;
