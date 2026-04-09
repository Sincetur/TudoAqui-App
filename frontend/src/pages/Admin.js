import React, { useEffect, useState } from 'react';
import {
  Users, Calendar, ShoppingBag, Home, MapPin, Building2, UtensilsCrossed,
  BarChart3, Shield, ChevronDown, Search, RefreshCw, ArrowUpCircle, CheckCircle, XCircle,
  CreditCard, Banknote, Clock
} from 'lucide-react';
import { api } from '../api';
import { PageHeader, LoadingState, Badge } from '../components/Layout';

const ROLES = [
  { value: 'cliente', label: 'Cliente' },
  { value: 'organizador', label: 'Organizador' },
  { value: 'vendedor', label: 'Vendedor' },
  { value: 'anfitriao', label: 'Anfitriao' },
  { value: 'agente', label: 'Agente' },
  { value: 'motorista', label: 'Motorista' },
  { value: 'entregador', label: 'Entregador' },
  { value: 'staff', label: 'Staff' },
  { value: 'admin', label: 'Admin' },
];

const STATUSES = [
  { value: 'ativo', label: 'Ativo', variant: 'success' },
  { value: 'inativo', label: 'Inativo', variant: 'default' },
  { value: 'suspenso', label: 'Suspenso', variant: 'danger' },
  { value: 'pendente', label: 'Pendente', variant: 'warning' },
];

const roleColor = (r) => {
  const map = { admin: 'danger', staff: 'warning', organizador: 'primary', vendedor: 'accent', anfitriao: 'success', agente: 'primary', motorista: 'accent', entregador: 'accent', cliente: 'default' };
  return map[r] || 'default';
};

export default function Admin({ user }) {
  const [tab, setTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.adminStats()
      .then(s => setStats(s))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const tabs = [
    { key: 'overview', label: 'Visao Geral', icon: BarChart3 },
    { key: 'users', label: 'Utilizadores', icon: Users },
    { key: 'payments', label: 'Pagamentos', icon: CreditCard },
    { key: 'upgrades', label: 'Upgrades', icon: ArrowUpCircle },
    { key: 'content', label: 'Conteudo', icon: ShoppingBag },
  ];

  return (
    <div data-testid="admin-page">
      <PageHeader
        title="Painel Admin"
        subtitle="Gestao do TUDOaqui SuperApp"
        actions={
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-primary-400" />
            <span className="text-primary-400 text-xs font-medium">ADMIN</span>
          </div>
        }
      />
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-6 space-y-6 animate-fade-in">
        {/* Tabs */}
        <div className="flex gap-1 bg-dark-900 p-1 rounded-lg border border-dark-800 w-fit">
          {tabs.map(t => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              data-testid={`admin-tab-${t.key}`}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-md text-sm font-medium transition ${tab === t.key ? 'bg-primary-600 text-white' : 'text-dark-400 hover:text-white'}`}
            >
              <t.icon className="w-3.5 h-3.5" />{t.label}
            </button>
          ))}
        </div>

        {error && <p className="text-red-400 text-sm" data-testid="admin-error">{error}</p>}
        {loading && <LoadingState />}

        {!loading && tab === 'overview' && stats && <OverviewTab stats={stats} />}
        {!loading && tab === 'users' && <UsersTab />}
        {!loading && tab === 'payments' && <PaymentsTab />}
        {!loading && tab === 'upgrades' && <UpgradesTab />}
        {!loading && tab === 'content' && <ContentTab />}
      </div>
    </div>
  );
}

function OverviewTab({ stats }) {
  const moduleStats = [
    { key: 'users', label: 'Utilizadores', icon: Users, color: 'bg-primary-600' },
    { key: 'events', label: 'Eventos', icon: Calendar, color: 'bg-sky-600' },
    { key: 'products', label: 'Produtos', icon: ShoppingBag, color: 'bg-accent-600' },
    { key: 'alojamento', label: 'Alojamento', icon: Home, color: 'bg-emerald-600' },
    { key: 'turismo', label: 'Turismo', icon: MapPin, color: 'bg-violet-600' },
    { key: 'imoveis', label: 'Imoveis', icon: Building2, color: 'bg-blue-600' },
    { key: 'restaurantes', label: 'Restaurantes', icon: UtensilsCrossed, color: 'bg-rose-600' },
  ];

  return (
    <div className="space-y-6" data-testid="admin-overview">
      {/* Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {moduleStats.map(m => (
          <div key={m.key} className="bg-dark-900 border border-dark-800 rounded-xl p-4" data-testid={`stat-card-${m.key}`}>
            <div className="flex items-center justify-between mb-3">
              <div className={`w-9 h-9 rounded-lg ${m.color} flex items-center justify-center`}>
                <m.icon className="w-4 h-4 text-white" />
              </div>
              <span className="text-white text-2xl font-bold">{stats.totais[m.key] || 0}</span>
            </div>
            <p className="text-dark-400 text-xs">{m.label}</p>
          </div>
        ))}
      </div>

      {/* Roles Distribution */}
      <div className="bg-dark-900 border border-dark-800 rounded-xl p-5">
        <h3 className="text-white font-semibold text-sm mb-4">Distribuicao de Roles</h3>
        <div className="grid grid-cols-3 sm:grid-cols-5 gap-3">
          {ROLES.map(r => (
            <div key={r.value} className="text-center" data-testid={`role-stat-${r.value}`}>
              <p className="text-white font-bold text-lg">{stats.roles[r.value] || 0}</p>
              <p className="text-dark-400 text-xs capitalize">{r.label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function UsersTab() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [editingUser, setEditingUser] = useState(null);
  const [actionLoading, setActionLoading] = useState('');

  const fetchUsers = (params = '') => {
    setLoading(true);
    const qs = [];
    if (roleFilter) qs.push(`role=${roleFilter}`);
    if (search) qs.push(`search=${search}`);
    const queryStr = qs.length ? `?${qs.join('&')}` : '';
    api.adminUsers(queryStr)
      .then(d => setUsers(Array.isArray(d) ? d : []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchUsers(); }, [roleFilter]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchUsers();
  };

  const handleRoleChange = async (userId, newRole) => {
    setActionLoading(userId + '-role');
    try {
      await api.adminUpdateRole(userId, newRole);
      fetchUsers();
    } catch (e) {
      alert(e.message);
    } finally {
      setActionLoading('');
      setEditingUser(null);
    }
  };

  const handleStatusChange = async (userId, newStatus) => {
    setActionLoading(userId + '-status');
    try {
      await api.adminUpdateStatus(userId, newStatus);
      fetchUsers();
    } catch (e) {
      alert(e.message);
    } finally {
      setActionLoading('');
    }
  };

  return (
    <div className="space-y-4" data-testid="admin-users-tab">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <form onSubmit={handleSearch} className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
          <input
            data-testid="admin-users-search"
            type="text"
            placeholder="Procurar por telefone ou nome..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-dark-900 border border-dark-800 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition"
          />
        </form>
        <select
          value={roleFilter}
          onChange={e => setRoleFilter(e.target.value)}
          data-testid="admin-users-role-filter"
          className="px-3 py-2.5 bg-dark-900 border border-dark-800 rounded-lg text-white text-sm focus:outline-none focus:border-primary-500"
        >
          <option value="">Todos os roles</option>
          {ROLES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
        </select>
        <button onClick={() => fetchUsers()} className="p-2.5 bg-dark-900 border border-dark-800 rounded-lg text-dark-400 hover:text-white transition" data-testid="admin-users-refresh">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* User Table */}
      {loading ? <LoadingState /> : (
        <div className="bg-dark-900 border border-dark-800 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full" data-testid="admin-users-table">
              <thead>
                <tr className="border-b border-dark-800">
                  <th className="text-left text-dark-400 text-xs font-medium px-4 py-3">Utilizador</th>
                  <th className="text-left text-dark-400 text-xs font-medium px-4 py-3">Telefone</th>
                  <th className="text-left text-dark-400 text-xs font-medium px-4 py-3">Role</th>
                  <th className="text-left text-dark-400 text-xs font-medium px-4 py-3">Estado</th>
                  <th className="text-left text-dark-400 text-xs font-medium px-4 py-3">Acoes</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u, i) => (
                  <tr key={u.id} className="border-b border-dark-800/50 hover:bg-dark-800/30 transition" data-testid={`user-row-${i}`}>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-full bg-dark-700 flex items-center justify-center flex-shrink-0">
                          <span className="text-dark-300 text-xs font-bold">{(u.nome || u.telefone || 'U')[0].toUpperCase()}</span>
                        </div>
                        <span className="text-white text-sm font-medium">{u.nome || '-'}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-dark-300 text-sm">{u.telefone}</td>
                    <td className="px-4 py-3">
                      {editingUser === u.id + '-role' ? (
                        <select
                          defaultValue={u.role}
                          onChange={e => handleRoleChange(u.id, e.target.value)}
                          autoFocus
                          onBlur={() => setEditingUser(null)}
                          className="px-2 py-1 bg-dark-800 border border-dark-600 rounded text-white text-xs"
                          data-testid={`role-select-${i}`}
                        >
                          {ROLES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
                        </select>
                      ) : (
                        <button
                          onClick={() => setEditingUser(u.id + '-role')}
                          className="cursor-pointer"
                          data-testid={`role-badge-${i}`}
                          disabled={actionLoading === u.id + '-role'}
                        >
                          <Badge variant={roleColor(u.role)}>
                            {u.role} <ChevronDown className="w-2.5 h-2.5 inline ml-0.5" />
                          </Badge>
                        </button>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={STATUSES.find(s => s.value === u.status)?.variant || 'default'}>
                        {u.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        {u.status === 'ativo' ? (
                          <button
                            onClick={() => handleStatusChange(u.id, 'suspenso')}
                            className="px-2 py-1 text-xs text-red-400 hover:bg-red-400/10 rounded transition"
                            data-testid={`suspend-btn-${i}`}
                          >Suspender</button>
                        ) : (
                          <button
                            onClick={() => handleStatusChange(u.id, 'ativo')}
                            className="px-2 py-1 text-xs text-green-400 hover:bg-green-400/10 rounded transition"
                            data-testid={`activate-btn-${i}`}
                          >Ativar</button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {users.length === 0 && <p className="text-dark-500 text-sm text-center py-8">Nenhum utilizador encontrado</p>}
        </div>
      )}
    </div>
  );
}

function UpgradesTab() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [actionLoading, setActionLoading] = useState('');

  const fetchRequests = () => {
    setLoading(true);
    const qs = filter ? `?status_filter=${filter}` : '';
    api.adminRoleRequests(qs)
      .then(d => setRequests(Array.isArray(d) ? d : []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchRequests(); }, [filter]);

  const handleApprove = async (id) => {
    setActionLoading(id);
    try {
      await api.adminApproveRole(id, 'Aprovado pelo admin');
      fetchRequests();
    } catch (e) {
      alert(e.message);
    } finally {
      setActionLoading('');
    }
  };

  const handleReject = async (id) => {
    setActionLoading(id);
    try {
      await api.adminRejectRole(id, 'Rejeitado pelo admin');
      fetchRequests();
    } catch (e) {
      alert(e.message);
    } finally {
      setActionLoading('');
    }
  };

  return (
    <div className="space-y-4" data-testid="admin-upgrades-tab">
      <div className="flex gap-2">
        {['', 'pendente', 'aprovado', 'rejeitado'].map(s => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            data-testid={`upgrade-filter-${s || 'all'}`}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${filter === s ? 'bg-primary-600 text-white' : 'bg-dark-900 border border-dark-800 text-dark-400 hover:text-white'}`}
          >{s === '' ? 'Todos' : s.charAt(0).toUpperCase() + s.slice(1)}</button>
        ))}
      </div>

      {loading ? <LoadingState /> : (
        <div className="space-y-3">
          {requests.length === 0 && <p className="text-dark-500 text-sm text-center py-8">Nenhum pedido de upgrade</p>}
          {requests.map((r, i) => (
            <div key={r.id} className="bg-dark-900 border border-dark-800 rounded-xl p-4" data-testid={`upgrade-request-${i}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-dark-700 flex items-center justify-center">
                    <span className="text-dark-300 text-sm font-bold">{(r.user_nome || 'U')[0]}</span>
                  </div>
                  <div>
                    <p className="text-white font-semibold text-sm">{r.user_nome || 'Sem nome'}</p>
                    <p className="text-dark-400 text-xs">{r.user_telefone}</p>
                  </div>
                </div>
                <Badge variant={r.status === 'pendente' ? 'warning' : r.status === 'aprovado' ? 'success' : 'danger'}>
                  {r.status}
                </Badge>
              </div>
              <div className="mt-3 pl-13">
                <div className="flex items-center gap-2 text-sm mb-1">
                  <Badge variant={roleColor(r.user_role_atual)}>{r.user_role_atual}</Badge>
                  <span className="text-dark-500">→</span>
                  <Badge variant={roleColor(r.role_pretendido)}>{r.role_pretendido}</Badge>
                </div>
                <p className="text-dark-400 text-sm mt-1">{r.motivo}</p>
                <p className="text-dark-600 text-xs mt-1">{new Date(r.created_at).toLocaleDateString('pt-AO')}</p>
              </div>
              {r.status === 'pendente' && (
                <div className="flex gap-2 mt-3 pt-3 border-t border-dark-800">
                  <button
                    onClick={() => handleApprove(r.id)}
                    disabled={actionLoading === r.id}
                    className="flex items-center gap-1 px-3 py-1.5 bg-green-500/15 text-green-400 hover:bg-green-500/25 rounded-lg text-sm font-medium transition disabled:opacity-50"
                    data-testid={`approve-btn-${i}`}
                  >
                    <CheckCircle className="w-3.5 h-3.5" /> Aprovar
                  </button>
                  <button
                    onClick={() => handleReject(r.id)}
                    disabled={actionLoading === r.id}
                    className="flex items-center gap-1 px-3 py-1.5 bg-red-500/15 text-red-400 hover:bg-red-500/25 rounded-lg text-sm font-medium transition disabled:opacity-50"
                    data-testid={`reject-btn-${i}`}
                  >
                    <XCircle className="w-3.5 h-3.5" /> Rejeitar
                  </button>
                </div>
              )}
              {r.admin_nota && (
                <p className="text-dark-500 text-xs mt-2 italic">Nota: {r.admin_nota}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}



function PaymentsTab() {
  const [payments, setPayments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [metodoFilter, setMetodoFilter] = useState('');
  const [actionLoading, setActionLoading] = useState('');

  const fetchData = () => {
    setLoading(true);
    const qs = [];
    if (statusFilter) qs.push(`status_filter=${statusFilter}`);
    if (metodoFilter) qs.push(`metodo=${metodoFilter}`);
    const queryStr = qs.length ? `?${qs.join('&')}` : '';
    Promise.all([
      api.adminPayments(queryStr).catch(() => []),
      api.adminPaymentStats().catch(() => null),
    ]).then(([p, s]) => {
      setPayments(Array.isArray(p) ? p : []);
      setStats(s);
    }).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [statusFilter, metodoFilter]);

  const formatPrice = (v) => v ? `${Number(v).toLocaleString('pt-AO')} Kz` : '0 Kz';
  const formatDate = (d) => d ? new Date(d).toLocaleDateString('pt-AO', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' }) : '-';

  const handleConfirm = async (id) => {
    setActionLoading(id);
    try {
      await api.adminConfirmPayment(id, 'Confirmado pelo admin');
      fetchData();
    } catch (e) { alert(e.message); }
    finally { setActionLoading(''); }
  };

  const handleReject = async (id) => {
    setActionLoading(id);
    try {
      await api.adminRejectPayment(id, 'Rejeitado pelo admin');
      fetchData();
    } catch (e) { alert(e.message); }
    finally { setActionLoading(''); }
  };

  const statusBadge = (s) => {
    const map = { pendente: 'warning', confirmado: 'success', falhado: 'danger', iniciado: 'default', processando: 'primary', reembolsado: 'accent' };
    return map[s] || 'default';
  };

  const metodoLabel = (m) => {
    const map = { transferencia: 'Transferencia', dinheiro: 'Dinheiro', multicaixa: 'Multicaixa', mobilemoney: 'Mobile Money', wallet: 'Wallet' };
    return map[m] || m;
  };

  return (
    <div className="space-y-4" data-testid="admin-payments-tab">
      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-dark-900 border border-dark-800 rounded-xl p-4">
            <p className="text-dark-400 text-xs">Total Pagamentos</p>
            <p className="text-white text-xl font-bold mt-1">{stats.total}</p>
          </div>
          <div className="bg-dark-900 border border-dark-800 rounded-xl p-4">
            <p className="text-dark-400 text-xs flex items-center gap-1"><Clock className="w-3 h-3 text-yellow-400" /> Pendentes</p>
            <p className="text-yellow-400 text-xl font-bold mt-1">{stats.pendentes}</p>
          </div>
          <div className="bg-dark-900 border border-dark-800 rounded-xl p-4">
            <p className="text-dark-400 text-xs flex items-center gap-1"><CheckCircle className="w-3 h-3 text-green-400" /> Confirmados</p>
            <p className="text-green-400 text-xl font-bold mt-1">{stats.confirmados}</p>
          </div>
          <div className="bg-dark-900 border border-dark-800 rounded-xl p-4">
            <p className="text-dark-400 text-xs">Receita Total</p>
            <p className="text-accent-400 text-xl font-bold mt-1">{formatPrice(stats.receita_total)}</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <select
          value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
          className="px-3 py-2 bg-dark-900 border border-dark-800 rounded-lg text-white text-sm focus:outline-none focus:border-primary-500"
          data-testid="payments-status-filter"
        >
          <option value="">Todos os estados</option>
          <option value="pendente">Pendente</option>
          <option value="confirmado">Confirmado</option>
          <option value="falhado">Falhado</option>
          <option value="iniciado">Iniciado</option>
        </select>
        <select
          value={metodoFilter} onChange={e => setMetodoFilter(e.target.value)}
          className="px-3 py-2 bg-dark-900 border border-dark-800 rounded-lg text-white text-sm focus:outline-none focus:border-primary-500"
          data-testid="payments-metodo-filter"
        >
          <option value="">Todos os metodos</option>
          <option value="transferencia">Transferencia</option>
          <option value="dinheiro">Dinheiro</option>
        </select>
        <button onClick={fetchData} className="p-2 bg-dark-900 border border-dark-800 rounded-lg text-dark-400 hover:text-white transition" data-testid="payments-refresh">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Table */}
      {loading ? <LoadingState /> : (
        <div className="bg-dark-900 border border-dark-800 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full" data-testid="payments-table">
              <thead>
                <tr className="border-b border-dark-800">
                  <th className="text-left text-dark-400 text-xs font-medium px-4 py-3">Referencia</th>
                  <th className="text-left text-dark-400 text-xs font-medium px-4 py-3">Metodo</th>
                  <th className="text-left text-dark-400 text-xs font-medium px-4 py-3">Valor</th>
                  <th className="text-left text-dark-400 text-xs font-medium px-4 py-3">Origem</th>
                  <th className="text-left text-dark-400 text-xs font-medium px-4 py-3">Estado</th>
                  <th className="text-left text-dark-400 text-xs font-medium px-4 py-3">Data</th>
                  <th className="text-left text-dark-400 text-xs font-medium px-4 py-3">Acoes</th>
                </tr>
              </thead>
              <tbody>
                {payments.map((p, i) => (
                  <tr key={p.id} className="border-b border-dark-800/50 hover:bg-dark-800/30 transition" data-testid={`payment-row-${i}`}>
                    <td className="px-4 py-3">
                      <span className="text-white text-xs font-mono">{p.referencia}</span>
                      {p.comprovativo_ref && (
                        <p className="text-dark-500 text-xs mt-0.5">Comp: {p.comprovativo_ref}</p>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className="flex items-center gap-1 text-dark-300 text-sm">
                        {p.metodo === 'transferencia' ? <Building2 className="w-3 h-3" /> : <Banknote className="w-3 h-3" />}
                        {metodoLabel(p.metodo)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-accent-400 font-bold text-sm">{formatPrice(p.valor_total)}</td>
                    <td className="px-4 py-3 text-dark-300 text-xs">{p.origem_tipo}</td>
                    <td className="px-4 py-3"><Badge variant={statusBadge(p.status)}>{p.status}</Badge></td>
                    <td className="px-4 py-3 text-dark-400 text-xs">{formatDate(p.created_at)}</td>
                    <td className="px-4 py-3">
                      {p.status === 'pendente' && (
                        <div className="flex gap-1">
                          <button
                            onClick={() => handleConfirm(p.id)}
                            disabled={actionLoading === p.id}
                            className="p-1.5 bg-green-500/15 text-green-400 hover:bg-green-500/25 rounded-lg transition disabled:opacity-50"
                            data-testid={`confirm-payment-${i}`}
                          >
                            <CheckCircle className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleReject(p.id)}
                            disabled={actionLoading === p.id}
                            className="p-1.5 bg-red-500/15 text-red-400 hover:bg-red-500/25 rounded-lg transition disabled:opacity-50"
                            data-testid={`reject-payment-${i}`}
                          >
                            <XCircle className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      )}
                      {p.status !== 'pendente' && <span className="text-dark-600 text-xs">-</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {payments.length === 0 && <p className="text-dark-500 text-sm text-center py-8">Nenhum pagamento encontrado</p>}
        </div>
      )}
    </div>
  );
}


function ContentTab() {
  const [events, setEvents] = useState([]);
  const [restaurants, setRestaurants] = useState([]);
  const [sellers, setSellers] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.adminEvents().catch(() => []),
      api.adminRestaurants().catch(() => []),
      api.adminSellers().catch(() => []),
      api.adminAgents().catch(() => []),
    ]).then(([ev, rest, sel, ag]) => {
      setEvents(Array.isArray(ev) ? ev : []);
      setRestaurants(Array.isArray(rest) ? rest : []);
      setSellers(Array.isArray(sel) ? sel : []);
      setAgents(Array.isArray(ag) ? ag : []);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingState />;

  return (
    <div className="space-y-6" data-testid="admin-content-tab">
      {/* Events */}
      <ContentSection title="Eventos" icon={Calendar} count={events.length}>
        {events.map((e, i) => (
          <tr key={e.id} className="border-b border-dark-800/50" data-testid={`admin-event-${i}`}>
            <td className="px-4 py-2.5 text-white text-sm">{e.titulo}</td>
            <td className="px-4 py-2.5 text-dark-300 text-sm">{e.local}</td>
            <td className="px-4 py-2.5 text-dark-300 text-sm">{e.data_evento}</td>
            <td className="px-4 py-2.5"><Badge variant={e.status === 'ativo' ? 'success' : 'warning'}>{e.status}</Badge></td>
          </tr>
        ))}
      </ContentSection>

      {/* Restaurants */}
      <ContentSection title="Restaurantes" icon={UtensilsCrossed} count={restaurants.length}>
        {restaurants.map((r, i) => (
          <tr key={r.id} className="border-b border-dark-800/50" data-testid={`admin-restaurant-${i}`}>
            <td className="px-4 py-2.5 text-white text-sm">{r.nome}</td>
            <td className="px-4 py-2.5 text-dark-300 text-sm">{r.cidade}</td>
            <td className="px-4 py-2.5 text-dark-300 text-sm">{r.total_pedidos} pedidos</td>
            <td className="px-4 py-2.5"><Badge variant={r.aberto ? 'success' : 'danger'}>{r.aberto ? 'Aberto' : 'Fechado'}</Badge></td>
          </tr>
        ))}
      </ContentSection>

      {/* Sellers */}
      <ContentSection title="Vendedores" icon={ShoppingBag} count={sellers.length}>
        {sellers.map((s, i) => (
          <tr key={s.id} className="border-b border-dark-800/50" data-testid={`admin-seller-${i}`}>
            <td className="px-4 py-2.5 text-white text-sm">{s.nome_loja}</td>
            <td className="px-4 py-2.5 text-dark-300 text-sm">{s.cidade}</td>
            <td className="px-4 py-2.5 text-dark-300 text-sm">{s.total_vendas} vendas</td>
            <td className="px-4 py-2.5"><Badge variant={s.status === 'aprovado' ? 'success' : 'warning'}>{s.status}</Badge></td>
          </tr>
        ))}
      </ContentSection>

      {/* Agents */}
      <ContentSection title="Agentes Imobiliarios" icon={Building2} count={agents.length}>
        {agents.map((a, i) => (
          <tr key={a.id} className="border-b border-dark-800/50" data-testid={`admin-agent-${i}`}>
            <td className="px-4 py-2.5 text-white text-sm">{a.nome_profissional}</td>
            <td className="px-4 py-2.5 text-dark-300 text-sm">{a.plano}</td>
            <td className="px-4 py-2.5 text-dark-300 text-sm">{a.total_vendas}V / {a.total_arrendamentos}A</td>
            <td className="px-4 py-2.5"><Badge variant={a.status === 'aprovado' ? 'success' : 'warning'}>{a.status}</Badge></td>
          </tr>
        ))}
      </ContentSection>
    </div>
  );
}

function ContentSection({ title, icon: Icon, count, children }) {
  return (
    <div className="bg-dark-900 border border-dark-800 rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-dark-800 flex items-center gap-2">
        <Icon className="w-4 h-4 text-dark-400" />
        <h3 className="text-white font-semibold text-sm">{title}</h3>
        <span className="text-dark-500 text-xs">({count})</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <tbody>{children}</tbody>
        </table>
      </div>
      {count === 0 && <p className="text-dark-500 text-sm text-center py-6">Sem registos</p>}
    </div>
  );
}
