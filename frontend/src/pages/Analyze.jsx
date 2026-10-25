import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, FileText, UploadCloud } from 'lucide-react';
import { apiRequest, getToken } from '../api';

const Analyze = () => {
  const [file, setFile] = useState(null);
  const [uploadedDocument, setUploadedDocument] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [reviewNotice, setReviewNotice] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState('');

  const handleUpload = async (event) => {
    event.preventDefault();
    if (!file) return;
    setWorking(true);
    setError('');
    setAnalysis(null);
    try {
      const form = new FormData();
      form.append('file', file);
      form.append('document_type', 'report');
      const uploaded = await apiRequest('/api/v1/documents/upload', { method: 'POST', body: form });
      setUploadedDocument(uploaded);
      try {
        const textResult = await apiRequest(`/api/v1/documents/${uploaded.id}/text`);
        setExtractedText(textResult.extracted_text || '');
        setReviewNotice(uploaded.processing_status === 'extraction_failed'
          ? 'Text extraction failed. Enter or paste the report text below to continue.'
          : 'Review and correct the extracted text before analysis.');
      } catch {
        setExtractedText('');
        setReviewNotice('No text could be extracted. Enter or paste the report text below to continue.');
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setWorking(false);
    }
  };

  const handleAnalyzeReviewedText = async (event) => {
    event.preventDefault();
    if (!uploadedDocument || !extractedText.trim()) return;
    setWorking(true);
    setError('');
    try {
      await apiRequest(`/api/v1/documents/${uploadedDocument.id}/text`, {
        method: 'PATCH',
        body: JSON.stringify({ extracted_text: extractedText }),
      });
      const result = await apiRequest(`/api/v1/documents/${uploadedDocument.id}/analyze`, {
        method: 'POST',
        body: JSON.stringify({}),
      });
      setAnalysis({ ...result, originalFilename: uploadedDocument.original_filename });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setWorking(false);
    }
  };

  if (analysis) {
    const explanation = analysis.explanation || {};
    const values = analysis.laboratory_values || [];
    return (
      <div className="container" style={{ padding: '3rem 0', maxWidth: '1000px' }}>
        <Link to="/history" style={{ color: 'var(--color-primary)' }}>← Your documents</Link>
        <h1 style={{ fontSize: '2rem', margin: '1rem 0 0.25rem' }}>Analysis results</h1>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>{analysis.originalFilename}</p>

        <section className="card" style={{ marginBottom: '1.5rem' }}>
          <h2 style={{ marginBottom: '0.75rem' }}>Summary</h2>
          <p>{analysis.summary || 'No summary was returned.'}</p>
          {analysis.model_provider && (
            <small style={{ display: 'block', marginTop: '0.75rem', color: 'var(--color-text-muted)' }}>
              Explanation provider: {analysis.model_provider}
            </small>
          )}
        </section>

        <h2 style={{ marginBottom: '1rem' }}>Extracted laboratory values</h2>
        {values.length === 0 ? (
          <div className="card">No laboratory values were extracted from this document.</div>
        ) : (
          <div className="card" style={{ overflowX: 'auto', padding: 0, marginBottom: '1.5rem' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead><tr>{['Test', 'Extracted value', 'Unit', 'Reference range', 'Status'].map((label) => <th key={label} style={tableHead}>{label}</th>)}</tr></thead>
              <tbody>
                {values.map((value) => (
                  <tr key={value.id || `${value.test_name}-${value.value_text}`}>
                    <td style={tableCell}>{value.test_name}</td>
                    <td style={tableCell}>{value.value_text}</td>
                    <td style={tableCell}>{value.unit || 'Not provided'}</td>
                    <td style={tableCell}>{value.reference_range?.text_range || 'Not provided on report'}</td>
                    <td style={tableCell}>{value.abnormality_status.replaceAll('_', ' ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {(explanation.test_explanations || []).length > 0 && (
          <>
            <h2 style={{ marginBottom: '1rem' }}>Explanations</h2>
            <div style={{ display: 'grid', gap: '1rem', marginBottom: '1.5rem' }}>
              {explanation.test_explanations.map((item) => (
                <section className="card" key={item.test_name}>
                  <h3 style={{ marginBottom: '0.5rem' }}>{item.test_name}</h3>
                  <p>{item.what_it_measures}</p>
                  <p style={{ marginTop: '0.5rem', color: 'var(--color-text-muted)' }}>{item.educational_note}</p>
                </section>
              ))}
            </div>
          </>
        )}

        {explanation.medical_disclaimer && <p className="card" style={{ color: 'var(--color-text-muted)' }}>{explanation.medical_disclaimer}</p>}
        {(analysis.sources || []).length > 0 && (
          <section style={{ marginTop: '1.5rem' }}>
            <h2 style={{ marginBottom: '0.75rem' }}>Sources</h2>
            {analysis.sources.map((source) => (
              <p key={`${source.title}-${source.chunk_id}`}>
                {source.source_url ? <a href={source.source_url} target="_blank" rel="noreferrer">{source.title}</a> : source.title}
                {' — '}{source.publisher}
              </p>
            ))}
          </section>
        )}
        <button className="btn btn-primary" style={{ marginTop: '1.5rem' }} onClick={() => {
          setFile(null);
          setUploadedDocument(null);
          setExtractedText('');
          setReviewNotice('');
          setAnalysis(null);
          setError('');
        }}>
          Analyze another report
        </button>
      </div>
    );
  }

  if (uploadedDocument) {
    return (
      <div className="container" style={{ padding: '3rem 0', maxWidth: '800px' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Review extracted text</h1>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
          Check the text from <strong>{uploadedDocument.original_filename}</strong>. Correct recognition errors before analysis.
        </p>
        {reviewNotice && <p role="status" className="card" style={{ marginBottom: '1rem' }}>{reviewNotice}</p>}
        <form onSubmit={handleAnalyzeReviewedText} className="card">
          <label htmlFor="extracted-report-text" style={{ display: 'block', fontWeight: 600, marginBottom: '0.5rem' }}>Extracted report text</label>
          <textarea
            id="extracted-report-text"
            required
            value={extractedText}
            onChange={(event) => setExtractedText(event.target.value)}
            rows={16}
            style={{ width: '100%', boxSizing: 'border-box', padding: '0.875rem', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', font: 'inherit', resize: 'vertical' }}
          />
          {error && <p role="alert" style={{ color: 'var(--color-danger)', marginTop: '1rem' }}>{error}</p>}
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem', flexWrap: 'wrap' }}>
            <button className="btn btn-primary" type="submit" disabled={working || !extractedText.trim()}>
              {working ? 'Saving text and analyzing…' : 'Save text and analyze'}
            </button>
            <button className="btn btn-secondary" type="button" disabled={working} onClick={() => {
              setUploadedDocument(null);
              setExtractedText('');
              setReviewNotice('');
              setFile(null);
              setError('');
            }}>Choose another file</button>
          </div>
        </form>
        <p style={{ color: 'var(--color-text-muted)', marginTop: '1rem' }}>
          Please verify important values against your original report and discuss the results with a healthcare professional.
        </p>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '4rem 0', maxWidth: '800px' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>Analyze a medical report</h1>
        <p style={{ color: 'var(--color-text-muted)' }}>Results are based on the document you upload. Check extracted text and values with your healthcare professional.</p>
      </div>
      {!getToken() ? (
        <div className="card" style={{ textAlign: 'center' }}>
          <p style={{ marginBottom: '1rem' }}>Sign in to securely upload and access your report.</p>
          <Link className="btn btn-primary" to="/login">Sign in</Link>
        </div>
      ) : (
        <form onSubmit={handleUpload} className="card" style={{ padding: '2rem' }}>
          <label htmlFor="report-file" style={{ display: 'block', padding: '3rem 1rem', textAlign: 'center', border: '2px dashed var(--color-border)', borderRadius: 'var(--radius-md)', cursor: 'pointer' }}>
            {file ? <FileText size={40} color="var(--color-primary)" /> : <UploadCloud size={40} color="var(--color-primary)" />}
            <span style={{ display: 'block', marginTop: '1rem', fontWeight: 600 }}>{file?.name || 'Choose a report (PDF, PNG, or JPEG)'}</span>
            {file && <small>{(file.size / 1024 / 1024).toFixed(2)} MB</small>}
          </label>
          <input id="report-file" type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={(event) => setFile(event.target.files?.[0] || null)} style={{ display: 'none' }} />
          {error && <p role="alert" style={{ color: 'var(--color-danger)', marginTop: '1rem' }}><AlertCircle size={18} /> {error}</p>}
          <button className="btn btn-primary" type="submit" disabled={!file || working} style={{ width: '100%', marginTop: '1.5rem' }}>
            {working ? 'Uploading and analyzing your report…' : 'Upload and analyze'}
          </button>
        </form>
      )}
    </div>
  );
};

const tableHead = { padding: '0.875rem', textAlign: 'left', background: 'var(--color-bg-page)', borderBottom: '1px solid var(--color-border)' };
const tableCell = { padding: '0.875rem', borderBottom: '1px solid var(--color-border)' };

export default Analyze;
