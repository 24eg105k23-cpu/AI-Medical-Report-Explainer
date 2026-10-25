import React from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';

const Checkout = () => (
  <div className="container" style={{ padding: '4rem 0', maxWidth: '700px' }}>
    <div className="card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
      <AlertTriangle size={48} color="var(--color-warning)" style={{ marginBottom: '1rem' }} />
      <h1 style={{ marginBottom: '0.75rem' }}>Checkout is not available</h1>
      <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
        No pharmacy ordering, pricing, payment, or delivery service is connected. No order has been placed.
      </p>
      <Link to="/" className="btn btn-secondary">Return to dashboard</Link>
    </div>
  </div>
);

export default Checkout;
