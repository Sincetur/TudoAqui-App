const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}/api/v1${endpoint}`, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/';
  }

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Erro na requisição');
  }
  return data;
}

export const api = {
  // Auth
  login: (telefone) => request('/auth/login', { method: 'POST', body: JSON.stringify({ telefone }) }),
  verifyOtp: (telefone, codigo) => request('/auth/verify-otp', { method: 'POST', body: JSON.stringify({ telefone, codigo }) }),
  getMe: () => request('/auth/me'),

  // Health
  health: () => fetch(`${API_BASE}/api/health`).then(r => r.json()),

  // Eventos
  listEvents: () => request('/events'),

  // Marketplace
  listProducts: () => request('/marketplace/products'),

  // Alojamento
  listProperties: () => request('/alojamento/properties'),

  // Turismo
  listExperiences: () => request('/turismo/experiences'),

  // Real Estate
  listImoveis: () => request('/realestate/properties'),

  // Entregas
  estimateDelivery: (data) => request('/entregas/estimate', { method: 'POST', body: JSON.stringify(data) }),

  // Restaurantes
  listRestaurants: () => request('/restaurantes'),
};
