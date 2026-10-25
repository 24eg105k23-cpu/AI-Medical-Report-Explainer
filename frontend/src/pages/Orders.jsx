import React from 'react';
import { Link } from 'react-router-dom';
import { Package } from 'lucide-react';

const Orders = () => (
  <div className="container" style={{ padding: '4rem 0', maxWidth: '700px' }}>
    <div className="card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
      <Package size={48} color="var(--color-text-light)" style={{ marginBottom: '1rem' }} />
      <h1 style={{ marginBottom: '0.75rem' }}>No order records available</h1>
      <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
        Order history is not connected to a pharmacy service. No demo orders are shown.
      </p>
      <Link to="/" className="btn btn-secondary">Return to dashboard</Link>
    </div>
  </div>
);

export default Orders;
