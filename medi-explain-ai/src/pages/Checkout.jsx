import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Package, CreditCard, AlertTriangle } from 'lucide-react';
import { MOCK_MEDICINES } from '../data/mockData';

const Checkout = () => {
  const navigate = useNavigate();
  const [orderPlaced, setOrderPlaced] = useState(false);
  const [formData, setFormData] = useState({
    name: 'Raj Sharma',
    phone: '9876543210',
    address: '42, Wellness Colony, Sector 15',
    city: 'New Delhi',
    state: 'Delhi',
    pin: '110001'
  });

  const orderItems = [
    { ...MOCK_MEDICINES[0], quantity: 2 },
    { ...MOCK_MEDICINES[1], quantity: 1 }
  ];

  const subtotal = orderItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const delivery = 40;
  const total = subtotal + delivery;

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handlePlaceOrder = (e) => {
    e.preventDefault();
    setOrderPlaced(true);
  };

  if (orderPlaced) {
    return (
      <div className="container" style={{ padding: '4rem 0', textAlign: 'center', maxWidth: '600px' }}>
        <div style={{ backgroundColor: 'var(--color-success-light)', width: '100px', height: '100px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 2rem' }}>
          <CheckCircle size={56} color="var(--color-success)" />
        </div>
        <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Order Placed Successfully!</h1>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '1.125rem', marginBottom: '2rem' }}>Thank you for your demo order.</p>

        <div className="card" style={{ textAlign: 'left', marginBottom: '2rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>Order ID</div>
              <div style={{ fontWeight: 600 }}>#DEMO-2026-0842</div>
            </div>
            <div>
              <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>Total</div>
              <div style={{ fontWeight: 700, color: 'var(--color-primary)' }}>₹{total.toFixed(2)}</div>
            </div>
            <div>
              <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>Delivery Address</div>
              <div style={{ fontWeight: 500 }}>{formData.address}, {formData.city}</div>
            </div>
            <div>
              <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>Estimated Delivery</div>
              <div style={{ fontWeight: 500 }}>28 August 2026</div>
            </div>
          </div>
          <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid var(--color-border)' }}>
            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem', marginBottom: '0.5rem' }}>Medicines</div>
            {orderItems.map(item => (
              <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0' }}>
                <span>{item.name} × {item.quantity}</span>
                <span style={{ fontWeight: 600 }}>₹{(item.price * item.quantity).toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={() => navigate('/orders')}>View Orders</button>
          <button className="btn btn-primary" onClick={() => navigate('/medicines')}>Continue Shopping</button>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '3rem 0', paddingBottom: '4rem' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '2rem' }}>Checkout</h1>

      {/* Demo notice */}
      <div className="card" style={{ borderLeft: '4px solid var(--color-primary)', marginBottom: '2rem', backgroundColor: 'var(--color-primary-light)' }}>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <CreditCard size={24} color="var(--color-primary)" />
          <p style={{ color: 'var(--color-primary-dark)', fontWeight: 500 }}>Demo Payment — No real transaction will occur.</p>
        </div>
      </div>

      <form onSubmit={handlePlaceOrder}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem' }}>
          {/* Delivery Information */}
          <div className="card">
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem' }}>Delivery Information</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {[
                { label: 'Full Name', name: 'name', type: 'text' },
                { label: 'Phone Number', name: 'phone', type: 'tel' },
                { label: 'Address', name: 'address', type: 'text' },
                { label: 'City', name: 'city', type: 'text' },
                { label: 'State', name: 'state', type: 'text' },
                { label: 'PIN Code', name: 'pin', type: 'text' }
              ].map(field => (
                <div key={field.name}>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.375rem', color: 'var(--color-text-main)' }}>{field.label}</label>
                  <input
                    type={field.type}
                    name={field.name}
                    value={formData[field.name]}
                    onChange={handleChange}
                    required
                    style={{
                      width: '100%',
                      padding: '0.75rem 1rem',
                      border: '1px solid var(--color-border)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '1rem',
                      fontFamily: 'var(--font-family)',
                      outline: 'none',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Order Summary */}
          <div>
            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem' }}>Order Summary</h2>
              {orderItems.map(item => (
                <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 0', borderBottom: '1px solid var(--color-border)' }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>{item.name}</div>
                    <div style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>{item.strength} × {item.quantity}</div>
                  </div>
                  <div style={{ fontWeight: 600 }}>₹{(item.price * item.quantity).toFixed(2)}</div>
                </div>
              ))}
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '1rem', marginTop: '0.5rem' }}>
                <span style={{ color: 'var(--color-text-muted)' }}>Subtotal</span>
                <span style={{ fontWeight: 600 }}>₹{subtotal.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '0.5rem' }}>
                <span style={{ color: 'var(--color-text-muted)' }}>Delivery</span>
                <span style={{ fontWeight: 600 }}>₹{delivery.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '1rem', marginTop: '0.5rem', borderTop: '1px solid var(--color-border)' }}>
                <span style={{ fontWeight: 700, fontSize: '1.125rem' }}>Total</span>
                <span style={{ fontWeight: 700, fontSize: '1.25rem', color: 'var(--color-primary)' }}>₹{total.toFixed(2)}</span>
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', fontSize: '1.125rem', padding: '1rem' }}>
              <Package size={20} /> Place Demo Order
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default Checkout;
