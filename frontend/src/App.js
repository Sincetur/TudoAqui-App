import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import { api } from './api';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

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
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
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

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={
          user ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />
        } />
        <Route path="/*" element={
          user ? <Dashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" replace />
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
