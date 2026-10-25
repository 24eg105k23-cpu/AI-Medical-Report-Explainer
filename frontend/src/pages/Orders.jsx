import React, { useState } from 'react';
import { Package, ChevronRight, Clock, CheckCircle, Truck } from 'lucide-react';

const mockOrders = [
  {
    id: '#DEMO-2026-0842',
    date: '26 August 2026',
    medicines: 2,
    amount: 250.00,
    status: 'Processing',
    items: [
      { name: 'Paracetamol 500mg', qty: 2, price: 90.00 },
      { name: 'Atorvastatin 10mg', qty: 1, price: 120.00 }
    ],
    address: '42, Wellness Colony, Sector 15, New Delhi',
    estimatedDelivery: '28 August 2026'
  },
  {
    id: '#DEMO-2026-0715',
    date: '10 July 2026',
    medicines: 3,
    amount: 425.00,
    status: 'Delivered',
    items: [
      { name: 'Amoxicillin 250mg', qty: 1, price: 85.00 },
      { name: 'Cetirizine 10mg', qty: 2, price: 70.00 },
      { name: 'Omeprazole 20mg', qty: 1, price: 60.00 }
    ],
    address: '42, Wellness Colony, Sector 15, New Delhi',
    estimatedDelivery: '13 July 2026'
  },
  {
    id: '#DEMO-2026-0312',
    date: '15 March 2026',
    medicines: 1,
    amount: 75.00,
    status: 'Confirmed',
    items: [
      { name: 'Metformin 500mg', qty: 1, price: 75.00 }
    ],
    address: '42, Wellness Colony, Sector 15, New Delhi',
    estimatedDelivery: '18 March 2026'
  }
];

const statusConfig = {
  Processing: { color: 'var(--color-warning)', bg: 'var(--color-warning-light)', icon: <Clock size={14} /> },
  Confirmed: { color: 'var(--color-primary)', bg: 'var(--color-primary-light)', icon: <CheckCircle size={14} /> },
  Delivered: { color: 'var(--color-success)', bg: 'var(--color-success-light)', icon: <Truck size={14} /> }
};

const Orders = () => {
  const [selectedOrder, setSelectedOrder] = useState(null);

  if (selectedOrder) {
    const order = selectedOrder;
    const sc = statusConfig[order.status];
    return (
      <div className="container" style={{ padding: '3rem 0', paddingBottom: '4rem', maxWidth: '700px' }}>
        <button className="btn" style={{ padding: '0.5rem 0', background: 'none', color: 'var(--color-primary)', marginBottom: '1.5rem' }}
          onClick={() => setSelectedOrder(null)}>
          ← Back to Orders
        </button>

        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Order {order.id}</h2>
              <div style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>Placed on {order.date}</div>
            </div>
            <span className="badge" style={{ backgroundColor: sc.bg, color: sc.color, display: 'flex', alignItems: 'center', gap: '4px' }}>
              {sc.icon} {order.status}
            </span>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>Items</h3>
            {order.items.map((item, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0', borderBottom: i < order.items.length - 1 ? '1px solid var(--color-border)' : 'none' }}>
                <span>{item.name} × {item.qty}</span>
                <span style={{ fontWeight: 600 }}>₹{item.price.toFixed(2)}</span>
              </div>
            ))}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', padding: '1rem', backgroundColor: 'var(--color-bg-page)', borderRadius: 'var(--radius-md)' }}>
            <div>
              <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>Total Amount</div>
              <div style={{ fontWeight: 700, fontSize: '1.25rem', color: 'var(--color-primary)' }}>₹{order.amount.toFixed(2)}</div>
            </div>
            <div>
              <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>Estimated Delivery</div>
              <div style={{ fontWeight: 600 }}>{order.estimatedDelivery}</div>
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>Delivery Address</div>
              <div style={{ fontWeight: 500 }}>{order.address}</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '3rem 0', paddingBottom: '4rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Order History</h1>
        <p style={{ color: 'var(--color-text-muted)' }}>Track your demo medicine orders.</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {mockOrders.map(order => {
          const sc = statusConfig[order.status];
          return (
            <div key={order.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', flexWrap: 'wrap', gap: '1rem' }}
              onClick={() => setSelectedOrder(order)}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1, minWidth: '200px' }}>
                <div style={{ backgroundColor: 'var(--color-primary-light)', color: 'var(--color-primary)', padding: '0.75rem', borderRadius: 'var(--radius-lg)' }}>
                  <Package size={24} />
                </div>
                <div>
                  <h3 style={{ fontSize: '1.125rem', fontWeight: 600 }}>{order.id}</h3>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>{order.date} • {order.medicines} medicines</div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ fontWeight: 700, color: 'var(--color-primary)' }}>₹{order.amount.toFixed(2)}</div>
                <span className="badge" style={{ backgroundColor: sc.bg, color: sc.color, display: 'flex', alignItems: 'center', gap: '4px' }}>
                  {sc.icon} {order.status}
                </span>
                <ChevronRight size={20} color="var(--color-text-light)" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Orders;
