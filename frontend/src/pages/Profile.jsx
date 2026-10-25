import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { User } from 'lucide-react';
import { apiRequest, getToken } from '../api';

const Profile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(getToken()));
  const [error, setError] = useState('');

  useEffect(() => {
    if (!getToken()) {
      setLoading(false);
      return;
    }
    apiRequest('/api/v1/auth/me')
      .then(setUser)
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="container" style={{ padding: '3rem 0', maxWidth: '700px' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1.5rem' }}>Account</h1>
      {!getToken() ? (
        <div className="card" style={{ textAlign: 'center' }}>
          <p style={{ marginBottom: '1rem' }}>Sign in to view your account details.</p>
          <Link to="/login" className="btn btn-primary">Sign in</Link>
        </div>
      ) : loading ? <p>Loading account…</p> : error ? (
        <p role="alert" style={{ color: 'var(--color-danger)' }}>{error}</p>
      ) : user && (
        <section className="card">
          <User size={32} color="var(--color-primary)" style={{ marginBottom: '1rem' }} />
          <dl style={{ display: 'grid', gap: '1rem' }}>
            <div><dt style={labelStyle}>Email</dt><dd>{user.email}</dd></div>
            <div><dt style={labelStyle}>Account status</dt><dd>{user.account_status}</dd></div>
            <div><dt style={labelStyle}>Account created</dt><dd>{new Date(user.created_at).toLocaleString()}</dd></div>
          </dl>
          <p style={{ marginTop: '1.5rem', color: 'var(--color-text-muted)' }}>
            Only account information stored by the service is shown here.
          </p>
        </section>
      )}
    </div>
  );
};

const labelStyle = { color: 'var(--color-text-muted)', fontSize: '0.875rem' };

export default Profile;
