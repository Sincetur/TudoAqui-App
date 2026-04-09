import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Car, Package, UtensilsCrossed, Calendar, ShoppingBag, Home, MapPin, Building2,
  Activity, TrendingUp, Zap
} from 'lucide-react';
import { api } from '../api';

const modules = [
  { key: 'eventos', to: '/eventos', icon: Calendar, label: 'Eventos', desc: 'Tickets e check-in', color: 'bg-primary-600' },
  { key: 'marketplace', to: '/marketplace', icon: ShoppingBag, label: 'Marketplace', desc: 'Compras online', color: 'bg-accent-600' },
  { key: 'alojamento', to: '/alojamento', icon: Home, label: 'Alojamento', desc: 'Reserva de estadias', color: 'bg-emerald-600' },
  { key: 'turismo', to: '/turismo', icon: MapPin, label: 'Turismo', desc: 'Tours e experiencias', color: 'bg-sky-600' },
  { key: 'realestate', to: '/imoveis', icon: Building2, label: 'Imobiliario', desc: 'Venda e arrendamento', color: 'bg-violet-600' },
  { key: 'entrega', to: '/entregas', icon: Package, label: 'Entregas', desc: 'Delivery de pacotes', color: 'bg-blue-600' },
  { key: 'restaurante', to: '/restaurantes', icon: UtensilsCrossed, label: 'Restaurantes', desc: 'Delivery de comida', color: 'bg-rose-600' },
  { key: 'taxi', to: '/', icon: Car, label: 'Taxi', desc: 'Em breve', color: 'bg-dark-600' },
];

export default function Dashboard({ user }) {
  const navigate = useNavigate();
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    api.health()
      .then(d => setApiStatus(d.status))
      .catch(() => setApiStatus('offline'));
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 md:px-6 py-6 space-y-8 animate-fade-in" data-testid="dashboard-page">
      {/* Welcome Banner */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-primary-700 via-primary-600 to-accent-600 p-6 md:p-8">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMSIgZmlsbD0icmdiYSgyNTUsMjU1LDI1NSwwLjA4KSIvPjwvc3ZnPg==')] opacity-60" />
        <div className="relative z-10">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-1" data-testid="welcome-msg">
            Ola, {user?.nome || 'Utilizador'}
          </h2>
          <p className="text-white/70 text-sm md:text-base">A sua vida em um so lugar</p>
        </div>
        <div className="absolute -bottom-4 -right-4 w-32 h-32 rounded-full bg-white/5 blur-2xl" />
      </section>

      {/* Stats */}
      <section className="grid grid-cols-3 gap-3" data-testid="stats-section">
        <div className="bg-dark-900 border border-dark-800 rounded-xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary-600/15 flex items-center justify-center flex-shrink-0">
            <Activity className="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <p className="text-dark-400 text-xs">Estado</p>
            <p className="text-white font-bold text-sm" data-testid="api-status">
              {apiStatus === 'healthy' ? 'Online' : apiStatus === null ? '...' : 'Offline'}
            </p>
          </div>
        </div>
        <div className="bg-dark-900 border border-dark-800 rounded-xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-accent-500/15 flex items-center justify-center flex-shrink-0">
            <TrendingUp className="w-5 h-5 text-accent-400" />
          </div>
          <div>
            <p className="text-dark-400 text-xs">Conta</p>
            <p className="text-white font-bold text-sm">{user?.role || 'Cliente'}</p>
          </div>
        </div>
        <div className="bg-dark-900 border border-dark-800 rounded-xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/15 flex items-center justify-center flex-shrink-0">
            <Zap className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <p className="text-dark-400 text-xs">Servicos</p>
            <p className="text-white font-bold text-sm">{modules.length}</p>
          </div>
        </div>
      </section>

      {/* Module Grid */}
      <section data-testid="modules-section">
        <h3 className="text-white font-semibold text-base mb-4">Servicos disponiveis</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {modules.map(m => (
            <button
              key={m.key}
              onClick={() => m.key !== 'taxi' && navigate(m.to)}
              disabled={m.key === 'taxi'}
              data-testid={`module-card-${m.key}`}
              className="group bg-dark-900 border border-dark-800 hover:border-dark-600 rounded-xl p-4 text-left transition-all duration-200 hover:-translate-y-0.5 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <div className={`inline-flex items-center justify-center w-10 h-10 rounded-lg ${m.color} mb-3 transition-transform group-hover:scale-110`}>
                <m.icon className="w-5 h-5 text-white" />
              </div>
              <h4 className="text-white font-semibold text-sm">{m.label}</h4>
              <p className="text-dark-500 text-xs mt-0.5">{m.desc}</p>
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}
