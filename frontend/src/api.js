const TOKEN_KEY = 'medi-explain-access-token';

export const getToken = () => localStorage.getItem(TOKEN_KEY);

export const saveToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token);
  window.dispatchEvent(new Event('auth-change'));
};

export const clearToken = () => {
  localStorage.removeItem(TOKEN_KEY);
  window.dispatchEvent(new Event('auth-change'));
};

export async function apiRequest(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);

  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(path, { ...options, headers });
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload?.detail || payload?.message || `Request failed (${response.status})`;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  if (payload?.success === false) {
    throw new Error(payload.message || 'The request could not be completed.');
  }
  return payload?.data;
}
