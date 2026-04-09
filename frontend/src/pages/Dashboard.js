import React, { useState, useEffect } from 'react';
import {
  Car, Package, UtensilsCrossed, Calendar, ShoppingBag, Home, MapPin, Building2,
  LogOut, User, ChevronRight, Activity, Bell
} from 'lucide-react';
import { api } from '../api';

const modules = [
  { key: 'taxi', icon: Car, label: 'Taxi', desc: 'Corridas urbanas', color: 'from-yellow-500 to-amber-600' },
  { key: 'entrega', icon: Package, label: 'Entrega', desc: 'Delivery de pacotes', color: 'from-blue-500 to-blue-700' },
  { key: 'restaurante', icon: UtensilsCrossed, label: 'Restaurante', desc: 'Delivery de comida', color: 'from-red-500 to-rose-700' },
  { key: 'eventos', icon: Calendar, label: 'Eventos', desc: 'Tickets e check-in', color: 'from-purple-500 to-violet-700' },
  { key: 'marketplace', icon: ShoppingBag, label: 'Marketplace', desc: 'Compras online', color: 'from-green-500 to-emerald-700' },
  { key: 'alojamento', icon: Home, label: 'Alojamento', desc: 'Reserva de estadias', color: 'from-cyan-500 to-teal-700' },
  { key: 'turismo', icon: MapPin, label: 'Turismo', desc: 'Tours e experiencias', color: 'from-orange-500 to-orange-700' },
  { key: 'realestate', icon: Building2, label: 'Imobiliario', desc: 'Venda e arrendamento', color: 'from-indigo-500 to-indigo-700' },
];

function ModuleCard({ icon: Icon, label, desc, color, onClick }) {
  return (
    <button
      onClick={onClick}
      data-testid={`module-${label.toLowerCase()}`}
      className="group bg-dark-900 border border-dark-700 hover:border-dark-500 rounded-2xl p-5 text-left transition-all duration-200 hover:shadow-lg hover:shadow-dark-950/50 hover:-translate-y-0.5"
    >
      <div className={`inline-flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-br ${color} mb-3 transition-transform group-hover:scale-110`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <h3 className="text-white font-semibold text-sm">{label}</h3>
      <p className="text-dark-400 text-xs mt-0.5">{desc}</p>
    </button>
  );
}

function StatCard({ label, value, icon: Icon }) {
  return (
    <div className="bg-dark-900 border border-dark-700 rounded-xl p-4 flex items-center gap-3">
      <div className="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-primary-400" />
      </div>
      <div>
        <p className="text-dark-400 text-xs">{label}</p>
        <p className="text-white font-bold text-lg">{value}</p>
      </div>
    </div>
  );
}

export default function Dashboard({ user, onLogout }) {
  const [apiStatus, setApiStatus] = useState(null);
  const [selectedModule, setSelectedModule] = useState(null);

  useEffect(() => {
    api.health()
      .then(data => setApiStatus(data.status))
      .catch(() => setApiStatus('offline'));
  }, []);

  return (
    <div className="min-h-screen bg-dark-950" data-testid="dashboard">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-dark-950/80 backdrop-blur-xl border-b border-dark-800">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
              <span className="text-white text-sm font-black">T</span>
            </div>
            <div>
              <h1 className="text-white font-bold text-base leading-tight">
                TUDO<span className="text-primary-500">aqui</span>
              </h1>
              <p className="text-dark-500 text-[10px] leading-tight">SuperApp Angola</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button className="relative p-2 text-dark-400 hover:text-white transition" data-testid="notifications-btn">
              <Bell className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2 bg-dark-800 rounded-full py-1.5 px-3">
              <User className="w-4 h-4 text-dark-400" />
              <span className="text-dark-200 text-xs font-medium" data-testid="user-phone">
                {user.telefone}
              </span>
            </div>
            <button
              onClick={onLogout}
              className="p-2 text-dark-400 hover:text-red-400 transition"
              data-testid="logout-btn"
              title="Sair"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6 space-y-8">
        {/* Welcome */}
        <section>
          <h2 className="text-2xl font-bold text-white mb-1" data-testid="welcome-msg">
            Ola, {user.nome || 'Utilizador'}
          </h2>
          <p className="text-dark-400 text-sm">O que precisa hoje?</p>
        </section>

        {/* Stats Row */}
        <section className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <StatCard label="Estado" value={apiStatus === 'healthy' ? 'Online' : 'Offline'} icon={Activity} />
          <StatCard label="Conta" value={user.role || 'Cliente'} icon={User} />
          <StatCard label="Modulos" value={modules.length} icon={ShoppingBag} />
        </section>

        {/* Modules Grid */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-semibold text-base">Servicos</h3>
            <span className="text-dark-500 text-xs">{modules.length} disponiveis</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {modules.map(m => (
              <ModuleCard
                key={m.key}
                {...m}
                onClick={() => setSelectedModule(m.key === selectedModule ? null : m.key)}
              />
            ))}
          </div>
        </section>

        {/* Selected Module Detail */}
        {selectedModule && (
          <section className="bg-dark-900 border border-dark-700 rounded-2xl p-6 animate-in" data-testid="module-detail">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white font-semibold text-lg capitalize">{selectedModule}</h3>
              <button
                onClick={() => setSelectedModule(null)}
                className="text-dark-400 hover:text-white text-sm"
              >
                Fechar
              </button>
            </div>
            <ModuleContent module={selectedModule} />
          </section>
        )}
      </main>
    </div>
  );
}

function ModuleContent({ module }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    setError('');

    const fetchers = {
      eventos: api.listEvents,
      marketplace: api.listProducts,
      alojamento: api.listProperties,
      turismo: api.listExperiences,
      realestate: api.listImoveis,
      restaurante: api.listRestaurants,
    };

    const fetcher = fetchers[module];
    if (fetcher) {
      fetcher()
        .then(d => setData(d))
        .catch(e => setError(e.message))
        .finally(() => setLoading(false));
    } else {
      setData([]);
      setLoading(false);
    }
  }, [module]);

  if (loading) {
    return <p className="text-dark-400 text-sm">A carregar dados...</p>;
  }

  if (error) {
    return <p className="text-red-400 text-sm">{error}</p>;
  }

  if (!data || (Array.isArray(data) && data.length === 0)) {
    return (
      <div className="text-center py-8">
        <p className="text-dark-400 text-sm">Nenhum item encontrado.</p>
        <p className="text-dark-500 text-xs mt-1">Os dados aparecerao aqui quando disponivel.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {Array.isArray(data) && data.slice(0, 5).map((item, i) => (
        <div key={i} className="flex items-center justify-between py-3 px-4 bg-dark-800 rounded-xl">
          <div>
            <p className="text-white text-sm font-medium">{item.nome || item.titulo || item.name || `Item ${i + 1}`}</p>
            <p className="text-dark-400 text-xs">{item.descricao || item.cidade || item.status || ''}</p>
          </div>
          <ChevronRight className="w-4 h-4 text-dark-500" />
        </div>
      ))}
      {Array.isArray(data) && data.length > 5 && (
        <p className="text-dark-500 text-xs text-center pt-2">+ {data.length - 5} mais</p>
      )}
    </div>
  );
}
