import React, { useState } from 'react';
import { Search, ShoppingCart, Pill, Filter, AlertTriangle, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { MOCK_MEDICINES } from '../data/mockData';

const allMedicines = [
  ...MOCK_MEDICINES,
  {
    id: 'm4',
    name: 'Cetirizine',
    strength: '10 mg',
    form: 'Tablet',
    manufacturer: 'AllergyCare Pharma',
    price: 35.00,
    availability: 'In Stock',
    prescriptionRequired: false,
    description: 'Used for allergies, hay fever, and common cold symptoms.',
    image: 'https://images.unsplash.com/photo-1550572017-edb79a5bd3c1?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3'
  },
  {
    id: 'm5',
    name: 'Metformin',
    strength: '500 mg',
    form: 'Tablet',
    manufacturer: 'DiabeCare Ltd.',
    price: 75.00,
    availability: 'In Stock',
    prescriptionRequired: true,
    description: 'Used to manage blood sugar levels in type 2 diabetes.',
    image: 'https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3'
  },
  {
    id: 'm6',
    name: 'Omeprazole',
    strength: '20 mg',
    form: 'Capsule',
    manufacturer: 'GastroHealth Inc.',
    price: 60.00,
    availability: 'In Stock',
    prescriptionRequired: false,
    description: 'Used to treat acid reflux, heartburn, and stomach ulcers.',
    image: 'https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3'
  }
];

const categories = ['All', 'Tablet', 'Capsule'];

const Medicines = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [category, setCategory] = useState('All');
  const [selectedMedicine, setSelectedMedicine] = useState(null);
  const navigate = useNavigate();

  const filtered = allMedicines.filter(m => {
    const matchesSearch = m.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = category === 'All' || m.form === category;
    return matchesSearch && matchesCategory;
  });

  // Medicine Detail View
  if (selectedMedicine) {
    const med = selectedMedicine;
    return (
      <div className="container" style={{ padding: '3rem 0', paddingBottom: '4rem', maxWidth: '800px' }}>
        <button className="btn" style={{ padding: '0.5rem 0', background: 'none', color: 'var(--color-primary)', marginBottom: '1.5rem' }}
          onClick={() => setSelectedMedicine(null)}>
          ← Back to Medicines
        </button>
        
        <div className="card" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
            {/* Image display */}
            <div style={{ width: '200px', height: '200px', backgroundColor: 'var(--color-primary-light)', borderRadius: 'var(--radius-lg)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, overflow: 'hidden' }}>
              {med.image && med.image.startsWith('http') ? (
                <img src={med.image} alt={med.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              ) : (
                <Pill size={64} color="var(--color-primary)" />
              )}
            </div>
            
            <div style={{ flex: 1, minWidth: '250px' }}>
              <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>{med.name}</h1>
              <div style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>{med.manufacturer}</div>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{ padding: '1rem', backgroundColor: 'var(--color-bg-page)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>Strength</div>
                  <div style={{ fontWeight: 600 }}>{med.strength}</div>
                </div>
                <div style={{ padding: '1rem', backgroundColor: 'var(--color-bg-page)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>Form</div>
                  <div style={{ fontWeight: 600 }}>{med.form}</div>
                </div>
                <div style={{ padding: '1rem', backgroundColor: 'var(--color-bg-page)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>Availability</div>
                  <div style={{ fontWeight: 600, color: med.availability === 'In Stock' ? 'var(--color-success)' : 'var(--color-warning)' }}>{med.availability}</div>
                </div>
                <div style={{ padding: '1rem', backgroundColor: 'var(--color-bg-page)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>Prescription</div>
                  <div style={{ fontWeight: 600 }}>{med.prescriptionRequired ? 'Required' : 'Not Required'}</div>
                </div>
              </div>

              <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-primary)', marginBottom: '1.5rem' }}>₹{med.price.toFixed(2)}</div>
              
              <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>{med.description}</p>
              
              <button className="btn btn-primary" style={{ width: '100%' }}>
                <ShoppingCart size={20} /> Add to Cart
              </button>
            </div>
          </div>
        </div>

        {/* Safety notice */}
        <div className="card" style={{ marginTop: '1.5rem', borderLeft: '4px solid var(--color-warning)', backgroundColor: 'var(--color-warning-light)' }}>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
            <AlertTriangle size={20} color="var(--color-warning)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9375rem' }}>
              <strong style={{ color: 'var(--color-text-main)' }}>Always verify medicines and dosage with a qualified pharmacist or healthcare professional.</strong>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '3rem 0', paddingBottom: '4rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Medicine Catalog</h1>
        <p style={{ color: 'var(--color-text-muted)' }}>Browse and search for medicines. All prices are indicative.</p>
      </div>

      {/* Search and Filters */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '250px' }}>
          <Search size={20} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-light)' }} />
          <input
            type="text"
            placeholder="Search medicines..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem 1rem 0.75rem 3rem',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              fontSize: '1rem',
              fontFamily: 'var(--font-family)',
              outline: 'none'
            }}
          />
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <Filter size={18} color="var(--color-text-muted)" />
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className="badge"
              style={{
                border: category === cat ? '2px solid var(--color-primary)' : '1px solid var(--color-border)',
                backgroundColor: category === cat ? 'var(--color-primary-light)' : 'white',
                color: category === cat ? 'var(--color-primary)' : 'var(--color-text-muted)',
                cursor: 'pointer',
                fontWeight: category === cat ? 600 : 400
              }}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Medicine Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
        {filtered.map(med => (
          <div key={med.id} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
            {/* Image display */}
            <div style={{ height: '150px', backgroundColor: 'var(--color-primary-light)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem', overflow: 'hidden' }}>
              {med.image && med.image.startsWith('http') ? (
                <img src={med.image} alt={med.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              ) : (
                <Pill size={48} color="var(--color-primary)" />
              )}
            </div>
            
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: 600 }}>{med.name}</h3>
                {med.prescriptionRequired && (
                  <span className="badge bg-primary-light" style={{ fontSize: '0.75rem' }}><ShieldCheck size={12} style={{ marginRight: '2px' }} /> Rx</span>
                )}
              </div>
              
              <div style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>{med.strength} • {med.form}</div>
              <div style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem', marginBottom: '1rem' }}>{med.manufacturer}</div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-primary)' }}>₹{med.price.toFixed(2)}</div>
                <span style={{ fontSize: '0.8125rem', color: med.availability === 'In Stock' ? 'var(--color-success)' : 'var(--color-warning)', fontWeight: 500 }}>
                  {med.availability}
                </span>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className="btn btn-secondary" style={{ flex: 1, padding: '0.625rem' }} onClick={() => setSelectedMedicine(med)}>Details</button>
              <button className="btn btn-primary" style={{ flex: 1, padding: '0.625rem' }}><ShoppingCart size={16} /> Add</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Medicines;
