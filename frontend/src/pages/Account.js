import React, { useEffect, useState } from 'react';
import { User, Shield, Send, Clock, CheckCircle, XCircle, ChevronRight } from 'lucide-react';
import { api } from '../api';
import { PageHeader, LoadingState, Badge } from '../components/Layout';
import FormModal, { FormField, FormInput, FormTextarea, FormSelect, SubmitButton } from '../components/FormModal';

const ROLE_LABELS = {
  cliente: 'Cliente', organizador: 'Organizador de Eventos', vendedor: 'Vendedor Marketplace',
  anfitriao: 'Anfitriao (Alojamento/Turismo)', agente: 'Agente Imobiliario',
  motorista: 'Motorista', entregador: 'Entregador', staff: 'Staff', admin: 'Administrador',
};

const UPGRADABLE = [
  { value: 'organizador', label: 'Organizador de Eventos', desc: 'Criar e gerir eventos, vender bilhetes' },
  { value: 'vendedor', label: 'Vendedor Marketplace', desc: 'Vender produtos no marketplace' },
  { value: 'anfitriao', label: 'Anfitriao', desc: 'Publicar alojamentos e experiencias de turismo' },
  { value: 'agente', label: 'Agente Imobiliario', desc: 'Publicar imoveis para venda e arrendamento' },
  { value: 'motorista', label: 'Motorista', desc: 'Fazer corridas de taxi' },
  { value: 'entregador', label: 'Entregador', desc: 'Fazer entregas de pacotes e comida' },
];

const statusConfig = {
  pendente: { icon: Clock, variant: 'warning', label: 'Pendente' },
  aprovado: { icon: CheckCircle, variant: 'success', label: 'Aprovado' },
  rejeitado: { icon: XCircle, variant: 'danger', label: 'Rejeitado' },
};

export default function Account({ user, onProfileUpdate }) {
  const [profile, setProfile] = useState(null);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [showEditProfile, setShowEditProfile] = useState(false);

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      api.getProfile().catch(() => null),
      api.myRoleRequests().catch(() => []),
    ]).then(([p, r]) => {
      setProfile(p);
      setRequests(Array.isArray(r) ? r : []);
    }).finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const hasPending = requests.some(r => r.status === 'pendente');
  const currentRole = profile?.role || user?.role || 'cliente';
  const canUpgrade = currentRole !== 'admin' && !hasPending;

  if (loading) return <LoadingState />;

  return (
    <div data-testid="account-page">
      <PageHeader title="Minha Conta" subtitle="Perfil e definicoes" />
      <div className="max-w-4xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-fade-in">
        {/* Profile Card */}
        <div className="bg-dark-900 border border-dark-800 rounded-xl p-5" data-testid="profile-card">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-600 to-accent-500 flex items-center justify-center">
              <span className="text-white text-2xl font-bold">{(profile?.nome || profile?.telefone || 'U')[0].toUpperCase()}</span>
            </div>
            <div className="flex-1">
              <h2 className="text-white font-bold text-lg" data-testid="profile-name">{profile?.nome || 'Sem nome'}</h2>
              <p className="text-dark-400 text-sm">{profile?.telefone}</p>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant={currentRole === 'admin' ? 'danger' : 'primary'}>{ROLE_LABELS[currentRole] || currentRole}</Badge>
              </div>
            </div>
            <button
              onClick={() => setShowEditProfile(true)}
              className="px-3 py-1.5 bg-dark-800 hover:bg-dark-700 border border-dark-700 text-white text-sm rounded-lg transition"
              data-testid="edit-profile-btn"
            >Editar</button>
          </div>
          {profile?.email && <p className="text-dark-400 text-sm">Email: {profile.email}</p>}
          {profile?.created_at && <p className="text-dark-500 text-xs mt-1">Conta criada: {new Date(profile.created_at).toLocaleDateString('pt-AO')}</p>}
        </div>

        {/* Upgrade Role */}
        {currentRole !== 'admin' && (
          <div className="bg-dark-900 border border-dark-800 rounded-xl p-5" data-testid="upgrade-section">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-semibold text-sm flex items-center gap-2">
                <Shield className="w-4 h-4 text-accent-400" /> Upgrade de Conta
              </h3>
              {canUpgrade && (
                <button
                  onClick={() => setShowUpgrade(true)}
                  className="flex items-center gap-1 px-3 py-1.5 bg-accent-500 hover:bg-accent-600 text-dark-950 text-sm font-medium rounded-lg transition"
                  data-testid="request-upgrade-btn"
                >
                  <Send className="w-3.5 h-3.5" /> Solicitar Upgrade
                </button>
              )}
            </div>
            <p className="text-dark-400 text-sm mb-3">
              {hasPending
                ? 'Tem um pedido de upgrade pendente. O admin ira analisar em breve.'
                : 'Solicite um upgrade de conta para desbloquear funcionalidades adicionais.'}
            </p>

            {/* Available roles */}
            {!hasPending && (
              <div className="grid gap-2 sm:grid-cols-2">
                {UPGRADABLE.filter(r => r.value !== currentRole).map(r => (
                  <button
                    key={r.value}
                    onClick={() => setShowUpgrade(r.value)}
                    className="flex items-center justify-between p-3 bg-dark-800 hover:bg-dark-700 border border-dark-700 rounded-lg text-left transition group"
                    data-testid={`upgrade-option-${r.value}`}
                  >
                    <div>
                      <p className="text-white text-sm font-medium">{r.label}</p>
                      <p className="text-dark-500 text-xs">{r.desc}</p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-dark-500 group-hover:text-accent-400 transition flex-shrink-0 ml-2" />
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* My Requests History */}
        {requests.length > 0 && (
          <div className="bg-dark-900 border border-dark-800 rounded-xl p-5" data-testid="requests-history">
            <h3 className="text-white font-semibold text-sm mb-3">Historico de Pedidos</h3>
            <div className="space-y-2">
              {requests.map((r, i) => {
                const cfg = statusConfig[r.status] || statusConfig.pendente;
                return (
                  <div key={r.id || i} className="flex items-center justify-between p-3 bg-dark-800 rounded-lg" data-testid={`request-item-${i}`}>
                    <div className="flex items-center gap-3">
                      <cfg.icon className={`w-4 h-4 ${r.status === 'aprovado' ? 'text-green-400' : r.status === 'rejeitado' ? 'text-red-400' : 'text-yellow-400'}`} />
                      <div>
                        <p className="text-white text-sm font-medium">{ROLE_LABELS[r.role_pretendido] || r.role_pretendido}</p>
                        <p className="text-dark-500 text-xs">{new Date(r.created_at).toLocaleDateString('pt-AO')}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant={cfg.variant}>{cfg.label}</Badge>
                      {r.admin_nota && <p className="text-dark-500 text-xs mt-0.5">{r.admin_nota}</p>}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {showUpgrade && (
        <UpgradeForm
          preselected={typeof showUpgrade === 'string' ? showUpgrade : ''}
          currentRole={currentRole}
          onClose={() => setShowUpgrade(false)}
          onCreated={() => { setShowUpgrade(false); fetchData(); }}
        />
      )}
      {showEditProfile && (
        <EditProfileForm
          profile={profile}
          onClose={() => setShowEditProfile(false)}
          onUpdated={() => { setShowEditProfile(false); fetchData(); if (onProfileUpdate) onProfileUpdate(); }}
        />
      )}
    </div>
  );
}

function UpgradeForm({ preselected, currentRole, onClose, onCreated }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    const fd = new FormData(e.target);
    try {
      await api.requestRoleUpgrade({
        role_pretendido: fd.get('role'),
        motivo: fd.get('motivo'),
      });
      onCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <FormModal title="Solicitar Upgrade de Conta" onClose={onClose}>
      <form onSubmit={handleSubmit} data-testid="upgrade-form">
        <FormField label="Role pretendido *">
          <FormSelect name="role" defaultValue={preselected} options={
            UPGRADABLE.filter(r => r.value !== currentRole).map(r => ({ value: r.value, label: r.label }))
          } placeholder="Selecionar role..." />
        </FormField>
        <FormField label="Motivo do pedido *">
          <FormTextarea name="motivo" placeholder="Explique porque pretende este upgrade e que servicos planeia oferecer..." rows={4} required />
        </FormField>
        {error && <p className="text-red-400 text-sm mb-3" data-testid="form-error">{error}</p>}
        <SubmitButton loading={loading}>Enviar Pedido</SubmitButton>
      </form>
    </FormModal>
  );
}

function EditProfileForm({ profile, onClose, onUpdated }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    const fd = new FormData(e.target);
    try {
      await api.updateProfile({
        nome: fd.get('nome') || null,
        email: fd.get('email') || null,
      });
      onUpdated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <FormModal title="Editar Perfil" onClose={onClose}>
      <form onSubmit={handleSubmit} data-testid="edit-profile-form">
        <FormField label="Nome">
          <FormInput name="nome" placeholder="Seu nome completo" defaultValue={profile?.nome || ''} />
        </FormField>
        <FormField label="Email">
          <FormInput name="email" type="email" placeholder="email@exemplo.ao" defaultValue={profile?.email || ''} />
        </FormField>
        {error && <p className="text-red-400 text-sm mb-3" data-testid="form-error">{error}</p>}
        <SubmitButton loading={loading}>Guardar Alteracoes</SubmitButton>
      </form>
    </FormModal>
  );
}
