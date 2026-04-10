import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { api } from './api';
import Layout from './components/Layout';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Events from './pages/Events';
import Marketplace from './pages/Marketplace';
import Alojamento from './pages/Alojamento';
import Turismo from './pages/Turismo';
import Imoveis from './pages/Imoveis';
import Entregas from './pages/Entregas';
import Restaurantes from './pages/Restaurantes';
import Admin from './pages/Admin';
import Account from './pages/Account';

function AppContent() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      api.getMe()
        .then(u => setUser(u))
        .catch(() => {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogin = (userData, tokens) => {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    setUser(userData);
    navigate('/');
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-950">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-dark-400 text-sm">A carregar...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/" element={<LandingPage onGoToApp={() => navigate('/login')} />} />
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  }

  return (
    <Layout user={user} onLogout={handleLogout}>
      <Routes>
        <Route path="/" element={<Dashboard user={user} />} />
        <Route path="/eventos" element={<Events />} />
        <Route path="/marketplace" element={<Marketplace />} />
        <Route path="/alojamento" element={<Alojamento />} />
        <Route path="/turismo" element={<Turismo />} />
        <Route path="/imoveis" element={<Imoveis />} />
        <Route path="/entregas" element={<Entregas />} />
        <Route path="/restaurantes" element={<Restaurantes />} />
        <Route path="/conta" element={<Account user={user} onProfileUpdate={() => api.getMe().then(setUser)} />} />
        {user.role === 'admin' && <Route path="/admin" element={<Admin user={user} />} />}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
