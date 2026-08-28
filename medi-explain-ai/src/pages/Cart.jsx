import React, { useState } from 'react';
import { Trash2, Plus, Minus, ShoppingCart, ArrowRight } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { MOCK_MEDICINES } from '../data/mockData';

const initialCartItems = [
  { ...MOCK_MEDICINES[0], quantity: 2 },
  { ...MOCK_MEDICINES[1], quantity: 1 }
];

const Cart = () => {
  const [cartItems, setCartItems] = useState(initialCartItems);
  const navigate = useNavigate();

  const updateQuantity = (id, delta) => {
    setCartItems(prev => prev.map(item =>
      item.id === id ? { ...item, quantity: Math.max(1, item.quantity + delta) } : item
    ));
  };

  const removeItem = (id) => {
    setCartItems(prev => prev.filter(item => item.id !== id));
  };

  const subtotal = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const delivery = subtotal > 0 ? 40 : 0;
  const total = subtotal + delivery;

  if (cartItems.length === 0) {
    return (
      <div className="container" style={{ padding: '4rem 0', textAlign: 'center' }}>
        <ShoppingCart size={64} color="var(--color-text-light)" style={{ marginBottom: '1rem' }} />
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Your cart is empty</h2>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>Browse medicines and add them to your cart.</p>
        <Link to="/medicines" className="btn btn-primary">Browse Medicines</Link>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '3rem 0', paddingBottom: '4rem' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '2rem' }}>Shopping Cart</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
        {/* On larger screens, use a 2-column layout */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem' }}>
          {/* Cart Items */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {cartItems.map(item => (
              <div key={item.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div style={{ flex: 1, minWidth: '180px' }}>
                  <h3 style={{ fontSize: '1.125rem', fontWeight: 600 }}>{item.name}</h3>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>{item.strength} • {item.form}</div>
                  <div style={{ color: 'var(--color-primary)', fontWeight: 700, marginTop: '0.5rem' }}>₹{item.price.toFixed(2)}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <button className="btn btn-secondary" style={{ padding: '0.375rem', width: '36px', height: '36px' }} onClick={() => updateQuantity(item.id, -1)}>
                    <Minus size={16} />
                  </button>
                  <span style={{ fontWeight: 600, fontSize: '1.125rem', minWidth: '24px', textAlign: 'center' }}>{item.quantity}</span>
                  <button className="btn btn-secondary" style={{ padding: '0.375rem', width: '36px', height: '36px' }} onClick={() => updateQuantity(item.id, 1)}>
                    <Plus size={16} />
                  </button>
                  <button className="btn" style={{ padding: '0.375rem', background: 'none', border: 'none', color: 'var(--color-danger)' }} onClick={() => removeItem(item.id)}>
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Order Summary */}
          <div className="card" style={{ alignSelf: 'flex-start', position: 'sticky', top: '5rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem' }}>Order Summary</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--color-text-muted)' }}>Subtotal ({cartItems.length} items)</span>
                <span style={{ fontWeight: 600 }}>₹{subtotal.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--color-text-muted)' }}>Delivery</span>
                <span style={{ fontWeight: 600 }}>₹{delivery.toFixed(2)}</span>
              </div>
              <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 700, fontSize: '1.125rem' }}>Total</span>
                <span style={{ fontWeight: 700, fontSize: '1.25rem', color: 'var(--color-primary)' }}>₹{total.toFixed(2)}</span>
              </div>
            </div>
            <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => navigate('/checkout')}>
              Proceed to Checkout <ArrowRight size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;
