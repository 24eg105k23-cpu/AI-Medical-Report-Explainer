import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingCart } from 'lucide-react';

const Cart = () => (
  <div className="container" style={{ padding: '4rem 0', maxWidth: '700px' }}>
    <div className="card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
      <ShoppingCart size={48} color="var(--color-text-light)" style={{ marginBottom: '1rem' }} />
      <h1 style={{ marginBottom: '0.75rem' }}>Cart unavailable</h1>
      <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
        There is no connected pharmacy catalog or server-backed cart. No sample items are shown.
      </p>
      <Link to="/medicines" className="btn btn-secondary">Catalog availability</Link>
    </div>
  </div>
);

export default Cart;
