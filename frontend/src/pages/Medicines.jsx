import React from 'react';
import { Link } from 'react-router-dom';
import { Pill } from 'lucide-react';

const Medicines = () => (
  <div className="container" style={{ padding: '4rem 0', maxWidth: '700px' }}>
    <div className="card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
      <Pill size={48} color="var(--color-text-light)" style={{ marginBottom: '1rem' }} />
      <h1 style={{ marginBottom: '0.75rem' }}>No medicine catalog connected</h1>
      <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
        This application has no live pharmacy inventory or verified pricing source. No medicines or prices are displayed.
      </p>
      <Link to="/prescription" className="btn btn-primary">Review a prescription extraction</Link>
    </div>
  </div>
);

export default Medicines;
