import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  Package, UtensilsCrossed, Calendar, ShoppingBag, Home, MapPin, Building2,
  LogOut, LayoutDashboard, ChevronLeft, Shield, UserCircle
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Inicio' },
  { to: '/eventos', icon: Calendar, label: 'Eventos' },
  { to: '/marketplace', icon: ShoppingBag, label: 'Marketplace' },
  { to: '/alojamento', icon: Home, label: 'Alojamento' },
  { to: '/turismo', icon: MapPin, label: 'Turismo' },
  { to: '/imoveis', icon: Building2, label: 'Imobiliario' },
  { to: '/entregas', icon: Package, label: 'Entregas' },
  { to: '/restaurantes', icon: UtensilsCrossed, label: 'Restaurantes' },
];

export default function Layout({ user, onLogout, children }) {
  const navigate = useNavigate();
  const isAdmin = user?.role === 'admin';

  const allNavItems = [
    ...navItems,
    { to: '/conta', icon: UserCircle, label: 'Conta' },
    ...(isAdmin ? [{ to: '/admin', icon: Shield, label: 'Admin' }] : []),
  ];

  return (
    <div className="min-h-screen bg-dark-950 flex" data-testid="app-layout">
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col w-56 bg-dark-900 border-r border-dark-800 fixed h-full z-40" data-testid="sidebar">
        <div className="p-4 border-b border-dark-800">
          <button onClick={() => navigate('/')} className="flex items-center gap-2" data-testid="logo-link">
            <div className="w-9 h-9 rounded-lg bg-primary-600 flex items-center justify-center">
              <span className="text-white text-sm font-black">T</span>
            </div>
            <div>
              <h1 className="text-white font-black text-sm leading-tight">
                TUDO<span className="text-accent-400">Aqui</span>
              </h1>
              <p className="text-dark-500 text-[9px] leading-tight">a sua vida em um so lugar</p>
            </div>
          </button>
        </div>

        <nav className="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto">
          {allNavItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              data-testid={`nav-${item.label.toLowerCase().replace(/[^a-z]/g, '')}`}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-primary-600/15 text-primary-400 border-l-2 border-primary-500'
                    : 'text-dark-400 hover:text-white hover:bg-dark-800'
                }`
              }
            >
              <item.icon className="w-4 h-4 flex-shrink-0" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-dark-800">
          <div className="flex items-center gap-2 px-2 mb-2">
            <div className="w-7 h-7 rounded-full bg-dark-700 flex items-center justify-center">
              <span className="text-dark-300 text-xs font-bold">
                {(user?.nome || user?.telefone || 'U')[0].toUpperCase()}
              </span>
            </div>
            <span className="text-dark-300 text-xs truncate flex-1">{user?.telefone}</span>
          </div>
          <button
            onClick={onLogout}
            data-testid="sidebar-logout-btn"
            className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-dark-400 hover:text-red-400 hover:bg-red-400/10 text-sm transition"
          >
            <LogOut className="w-4 h-4" />
            Sair
          </button>
        </div>
      </aside>

      {/* Mobile Header */}
      <header className="md:hidden fixed top-0 left-0 right-0 z-50 bg-dark-950/90 backdrop-blur-xl border-b border-dark-800">
        <div className="flex items-center justify-between px-4 py-3">
          <button onClick={() => navigate('/')} className="flex items-center gap-2" data-testid="mobile-logo">
            <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
              <span className="text-white text-xs font-black">T</span>
            </div>
            <span className="text-white font-black text-sm">TUDO<span className="text-accent-400">Aqui</span></span>
          </button>
          <button onClick={onLogout} className="p-2 text-dark-400 hover:text-red-400" data-testid="mobile-logout-btn">
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* Mobile Bottom Nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-dark-900 border-t border-dark-800 px-1 py-1" data-testid="mobile-nav">
        <div className="flex justify-around">
          {navItems.slice(0, 5).map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              data-testid={`mobile-nav-${item.label.toLowerCase().replace(/[^a-z]/g, '')}`}
              className={({ isActive }) =>
                `flex flex-col items-center py-1.5 px-2 rounded-lg text-[10px] transition ${
                  isActive ? 'text-primary-400' : 'text-dark-500'
                }`
              }
            >
              <item.icon className="w-4 h-4 mb-0.5" />
              {item.label.slice(0, 6)}
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 md:ml-56 min-h-screen">
        <div className="pt-16 md:pt-0 pb-20 md:pb-0">
          {children}
        </div>
      </main>
    </div>
  );
}

export function PageHeader({ title, subtitle, onBack, actions }) {
  const navigate = useNavigate();
  return (
    <div className="sticky top-0 md:top-0 z-30 bg-dark-950/90 backdrop-blur-xl border-b border-dark-800">
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {onBack && (
            <button
              onClick={() => (typeof onBack === 'function' ? onBack() : navigate(-1))}
              className="p-1.5 rounded-lg text-dark-400 hover:text-white hover:bg-dark-800 transition"
              data-testid="back-btn"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
          )}
          <div>
            <h1 className="text-white font-bold text-lg" data-testid="page-title">{title}</h1>
            {subtitle && <p className="text-dark-400 text-xs">{subtitle}</p>}
          </div>
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  );
}

export function EmptyState({ icon: Icon, title, description }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 animate-fade-in" data-testid="empty-state">
      <div className="w-14 h-14 rounded-2xl bg-dark-800 flex items-center justify-center mb-4">
        <Icon className="w-7 h-7 text-dark-500" />
      </div>
      <h3 className="text-white font-semibold text-base mb-1">{title}</h3>
      <p className="text-dark-400 text-sm text-center max-w-xs">{description}</p>
    </div>
  );
}

export function LoadingState() {
  return (
    <div className="flex items-center justify-center py-20" data-testid="loading-state">
      <div className="w-8 h-8 border-3 border-primary-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

export function ItemCard({ children, onClick, testId }) {
  return (
    <div
      onClick={onClick}
      data-testid={testId}
      className={`bg-dark-900 border border-dark-800 rounded-xl p-4 transition-all duration-150 ${
        onClick ? 'cursor-pointer hover:border-dark-600 hover:bg-dark-800/50' : ''
      }`}
    >
      {children}
    </div>
  );
}

export function Badge({ children, variant = 'default' }) {
  const styles = {
    default: 'bg-dark-800 text-dark-300',
    primary: 'bg-primary-600/15 text-primary-400',
    accent: 'bg-accent-500/15 text-accent-400',
    success: 'bg-green-500/15 text-green-400',
    warning: 'bg-yellow-500/15 text-yellow-400',
    danger: 'bg-red-500/15 text-red-400',
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium ${styles[variant]}`}>
      {children}
    </span>
  );
}
