const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1${endpoint}`, { ...options, headers });
  if (res.status === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
    return;
  }
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Erro na requisicao');
  return data;
}

export const api = {
  health: () => fetch(`${API_BASE}/api/health`).then(r => r.json()),

  // Auth
  login: (telefone) => request('/auth/login', { method: 'POST', body: JSON.stringify({ telefone }) }),
  verifyOtp: (telefone, codigo) => request('/auth/verify-otp', { method: 'POST', body: JSON.stringify({ telefone, codigo }) }),
  getMe: () => request('/auth/me'),

  // Eventos
  listEvents: (params = '') => request(`/events${params}`),
  getEvent: (id) => request(`/events/${id}`),
  createEvent: (data) => request('/events', { method: 'POST', body: JSON.stringify(data) }),

  // Marketplace
  listProducts: (params = '') => request(`/marketplace/products${params}`),
  getProduct: (id) => request(`/marketplace/products/${id}`),
  listSellers: () => request('/marketplace/sellers'),
  listCategories: () => request('/marketplace/categories'),
  registerSeller: (data) => request('/marketplace/sellers/register', { method: 'POST', body: JSON.stringify(data) }),
  createProduct: (data) => request('/marketplace/products', { method: 'POST', body: JSON.stringify(data) }),
  createOrder: (data) => request('/marketplace/orders', { method: 'POST', body: JSON.stringify(data) }),
  listMyOrders: () => request('/marketplace/orders/my'),

  // Alojamento
  listProperties: (params = '') => request(`/alojamento/properties${params}`),
  getProperty: (id) => request(`/alojamento/properties/${id}`),
  createProperty: (data) => request('/alojamento/properties', { method: 'POST', body: JSON.stringify(data) }),
  checkAvailability: (id, checkin, checkout) => request(`/alojamento/properties/${id}/availability?checkin=${checkin}&checkout=${checkout}`),
  createBooking: (data) => request('/alojamento/bookings', { method: 'POST', body: JSON.stringify(data) }),
  listMyBookings: () => request('/alojamento/bookings/my'),
  listPropertyReviews: (id) => request(`/alojamento/properties/${id}/reviews`),

  // Turismo
  listExperiences: (params = '') => request(`/turismo/experiences${params}`),
  getExperience: (id) => request(`/turismo/experiences/${id}`),
  createExperience: (data) => request('/turismo/experiences', { method: 'POST', body: JSON.stringify(data) }),
  listSchedules: (id) => request(`/turismo/experiences/${id}/schedules`),
  createTurismoBooking: (data) => request('/turismo/bookings', { method: 'POST', body: JSON.stringify(data) }),
  listMyTurismoBookings: () => request('/turismo/bookings/my'),
  listExperienceReviews: (id) => request(`/turismo/experiences/${id}/reviews`),

  // Real Estate
  listImoveis: (params = '') => request(`/realestate/properties${params}`),
  getImovel: (id) => request(`/realestate/properties/${id}`),
  listAgents: () => request('/realestate/agents'),
  createLead: (data) => request('/realestate/leads', { method: 'POST', body: JSON.stringify(data) }),
  addFavorite: (id) => request(`/realestate/favorites/${id}`, { method: 'POST' }),
  removeFavorite: (id) => request(`/realestate/favorites/${id}`, { method: 'DELETE' }),
  listFavorites: () => request('/realestate/favorites'),

  // Entregas
  estimateDelivery: (data) => request('/entregas/estimate', { method: 'POST', body: JSON.stringify(data) }),
  createDelivery: (data) => request('/entregas', { method: 'POST', body: JSON.stringify(data) }),
  listMyDeliveries: () => request('/entregas/my'),
  getDelivery: (id) => request(`/entregas/${id}`),
  getTracking: (id) => request(`/entregas/${id}/tracking`),

  // Restaurantes
  listRestaurants: (params = '') => request(`/restaurantes${params}`),
  getRestaurant: (id) => request(`/restaurantes/${id}`),
  getMenu: (id) => request(`/restaurantes/${id}/menu`),
  createFoodOrder: (data) => request('/restaurantes/orders', { method: 'POST', body: JSON.stringify(data) }),
  listMyFoodOrders: () => request('/restaurantes/orders/my'),

  // Drivers
  registerDriver: (data) => request('/drivers/register', { method: 'POST', body: JSON.stringify(data) }),
  getDriverProfile: () => request('/drivers/me'),
};
