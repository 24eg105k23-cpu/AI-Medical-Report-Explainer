import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiRequest, saveToken } from '../api';

const Login = () => {
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [working, setWorking] = useState(false);
  const navigate = useNavigate();

  const submit = async (event) => {
    event.preventDefault();
    setError('');
    setWorking(true);
    try {
      if (mode === 'register') {
        await apiRequest('/api/v1/auth/register', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        });
      }
      const result = await apiRequest('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      saveToken(result.access_token);
      navigate('/');
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setWorking(false);
    }
  };

  return (
    <div className="container" style={{ padding: '4rem 0', maxWidth: '480px' }}>
      <div className="card">
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
          {mode === 'login' ? 'Sign in' : 'Create your account'}
        </h1>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
          Your reports are private to your account.
        </p>
        <form onSubmit={submit} style={{ display: 'grid', gap: '1rem' }}>
          <label>
            Email
            <input
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              style={inputStyle}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              minLength={mode === 'register' ? 8 : undefined}
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              style={inputStyle}
            />
          </label>
          {error && <p role="alert" style={{ color: 'var(--color-danger)' }}>{error}</p>}
          <button className="btn btn-primary" type="submit" disabled={working}>
            {working ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>
        <p style={{ marginTop: '1rem', color: 'var(--color-text-muted)' }}>
          {mode === 'login' ? 'New here? ' : 'Already registered? '}
          <button
            type="button"
            onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}
            style={{ border: 0, background: 'none', color: 'var(--color-primary)', cursor: 'pointer' }}
          >
            {mode === 'login' ? 'Create an account' : 'Sign in'}
          </button>
        </p>
        <Link to="/" style={{ color: 'var(--color-text-muted)' }}>Back to home</Link>
      </div>
    </div>
  );
};

const inputStyle = {
  display: 'block',
  width: '100%',
  padding: '0.75rem 1rem',
  marginTop: '0.375rem',
  border: '1px solid var(--color-border)',
  borderRadius: 'var(--radius-md)',
  font: 'inherit',
  boxSizing: 'border-box',
};

export default Login;
