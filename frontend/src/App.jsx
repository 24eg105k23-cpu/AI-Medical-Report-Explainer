import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { Activity, User, Menu, X, LogIn, LogOut } from 'lucide-react';
import './index.css';
import { apiRequest, clearToken, getToken } from './api';
import Dashboard from './pages/Dashboard';
import Analyze from './pages/Analyze';
import History from './pages/History';
import Prescription from './pages/Prescription';
import Medicines from './pages/Medicines';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import Orders from './pages/Orders';
import Profile from './pages/Profile';
import Login from './pages/Login';

// Layout Component
const Navbar = () => {
  const [isOpen, setIsOpen] = React.useState(false);
  const [authenticated, setAuthenticated] = React.useState(Boolean(getToken()));
  const location = useLocation();
  const navigate = useNavigate();

  const navLinks = [
    { name: 'Dashboard', path: '/' },
    { name: 'Medical Reports', path: '/history' },
    { name: 'Prescription', path: '/prescription' }
  ];

  React.useEffect(() => {
    const updateAuth = () => setAuthenticated(Boolean(getToken()));
    window.addEventListener('auth-change', updateAuth);
    return () => window.removeEventListener('auth-change', updateAuth);
  }, []);

  const logout = async () => {
    try {
      if (getToken()) await apiRequest('/api/v1/auth/logout', { method: 'POST' });
    } catch (error) {
      window.alert(`Could not revoke the server session: ${error.message}`);
    } finally {
      clearToken();
      navigate('/login');
    }
  };

  const isActive = (path) => location.pathname === path || (path !== '/' && location.pathname.startsWith(path));

  return (
    <nav className="navbar" style={{ backgroundColor: 'white', borderBottom: '1px solid var(--color-border)', position: 'sticky', top: 0, zIndex: 50 }}>
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '4rem' }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, fontSize: '1.25rem', color: 'var(--color-primary-dark)' }}>
          <Activity size={28} color="var(--color-primary)" />
          MediExplain AI
        </Link>

        {/* Desktop Nav */}
        <div style={{ display: 'none', gap: '2rem' }} className="desktop-nav">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              to={link.path}
              style={{
                color: isActive(link.path) ? 'var(--color-primary)' : 'var(--color-text-muted)',
                fontWeight: isActive(link.path) ? 600 : 500,
                borderBottom: isActive(link.path) ? '2px solid var(--color-primary)' : '2px solid transparent',
                padding: '1.25rem 0'
              }}
            >
              {link.name}
            </Link>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {authenticated ? (
            <>
              <Link to="/profile" aria-label="Profile" style={{ color: 'var(--color-text-muted)' }}><User size={24} /></Link>
              <button className="btn btn-secondary" onClick={logout} style={{ padding: '0.5rem 0.75rem' }}>
                <LogOut size={18} /> Sign out
              </button>
            </>
          ) : (
            <Link to="/login" className="btn btn-secondary" style={{ padding: '0.5rem 0.75rem' }}>
              <LogIn size={18} /> Sign in
            </Link>
          )}
          <button className="mobile-menu-btn" onClick={() => setIsOpen(!isOpen)} style={{ background: 'none', border: 'none', color: 'var(--color-text-main)' }}>
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Nav */}
      {isOpen && (
        <div style={{ padding: '1rem', borderTop: '1px solid var(--color-border)', backgroundColor: 'white' }} className="mobile-nav">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              to={link.path}
              onClick={() => setIsOpen(false)}
              style={{
                display: 'block',
                padding: '0.75rem 1rem',
                color: isActive(link.path) ? 'var(--color-primary)' : 'var(--color-text-main)',
                backgroundColor: isActive(link.path) ? 'var(--color-primary-light)' : 'transparent',
                borderRadius: 'var(--radius-md)',
                fontWeight: 500,
                marginBottom: '0.25rem'
              }}
            >
              {link.name}
            </Link>
          ))}
        </div>
      )}
      <style>{`
        @media (min-width: 768px) {
          .desktop-nav { display: flex !important; }
          .mobile-menu-btn { display: none !important; }
          .mobile-nav { display: none !important; }
        }
      `}</style>
    </nav>
  );
};

const FooterDisclaimer = () => (
  <div style={{ backgroundColor: 'var(--color-warning-light)', borderTop: '1px solid #fde68a', padding: '1rem 0', marginTop: 'auto' }}>
    <div className="container" style={{ textAlign: 'center', fontSize: '0.875rem', color: 'var(--color-warning)' }}>
      <strong>Disclaimer:</strong> MediExplain AI is designed for educational and convenience purposes only. It does not provide medical diagnosis or replace professional medical advice. Always consult your doctor or pharmacist regarding your health reports, medicines, and treatment.
    </div>
  </div>
);

const App = () => {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Navbar />
        <main style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyze" element={<Analyze />} />
            <Route path="/history" element={<History />} />
            <Route path="/prescription" element={<Prescription />} />
            <Route path="/medicines" element={<Medicines />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/checkout" element={<Checkout />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/login" element={<Login />} />
            <Route path="*" element={<div className="container" style={{ padding: '2rem 0' }}><h2>Page not found</h2></div>} />
          </Routes>
        </main>
        <FooterDisclaimer />
      </div>
    </BrowserRouter>
  );
};

export default App;
