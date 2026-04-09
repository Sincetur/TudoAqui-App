import React, { useEffect, useState } from 'react';
import { User, Shield, Send, Clock, CheckCircle, XCircle, ChevronRight, CreditCard, Building2, Banknote, Smartphone, Store } from 'lucide-react';
import { api } from '../api';
import { PageHeader, LoadingState, Badge } from '../components/Layout';
import FormModal, { FormField, FormInput, FormTextarea, FormSelect, SubmitButton } from '../components/FormModal';

const ROLE_LABELS = {
  cliente: 'Cliente', motorista: 'Motorista', motoqueiro: 'Motoqueiro',
  proprietario: 'Proprietario', guia_turista: 'Guia Turista',
  agente_imobiliario: 'Agente Imobiliario', agente_viagem: 'Agente de Viagem',
  staff: 'Staff', admin: 'Administrador',
};

const UPGRADABLE = [
  { value: 'motorista', label: 'Motorista', desc: 'Condutor de taxi ou transporte privado' },
  { value: 'motoqueiro', label: 'Motoqueiro', desc: 'Entregas rapidas de moto ou kupapata' },
  { value: 'proprietario', label: 'Proprietario', desc: 'Dono de alojamento, restaurante ou loja' },
  { value: 'guia_turista', label: 'Guia Turista', desc: 'Guia de experiencias e tours turisticos' },
  { value: 'agente_imobiliario', label: 'Agente Imobiliario', desc: 'Venda e arrendamento de imoveis' },
  { value: 'agente_viagem', label: 'Agente de Viagem', desc: 'Pacotes turisticos e viagens' },
  { value: 'staff', label: 'Staff', desc: 'Funcionario de eventos ou servicos' },
];

const statusConfig = {
  pendente: { icon: Clock, variant: 'warning', label: 'Pendente' },
  aprovado: { icon: CheckCircle, variant: 'success', label: 'Aprovado' },
  rejeitado: { icon: XCircle, variant: 'danger', label: 'Rejeitado' },
};

const PARTNER_ROLES = ['motorista', 'motoqueiro', 'proprietario', 'guia_turista', 'agente_imobiliario', 'agente_viagem', 'staff'];

export default function Account({ user, onProfileUpdate }) {
  const [profile, setProfile] = useState(null);
  const [requests, setRequests] = useState([]);
  const [payments, setPayments] = useState([]);
  const [partner, setPartner] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [showEditProfile, setShowEditProfile] = useState(false);
  const [showPartnerRegister, setShowPartnerRegister] = useState(false);
  const [showPartnerPayment, setShowPartnerPayment] = useState(false);

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      api.getProfile().catch(() => null),
      api.myRoleRequests().catch(() => []),
      api.listMyPayments().catch(() => []),
      api.getMyPartner().catch(() => null),
    ]).then(([p, r, pay, part]) => {
      setProfile(p);
      setRequests(Array.isArray(r) ? r : []);
      setPayments(Array.isArray(pay) ? pay : []);
      setPartner(part);
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
        {/* Partner Section */}
        {PARTNER_ROLES.includes(currentRole) && (
          <div className="bg-dark-900 border border-dark-800 rounded-xl p-5" data-testid="partner-section">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-semibold text-sm flex items-center gap-2">
                <Store className="w-4 h-4 text-primary-400" /> Parceiro TUDOaqui
              </h3>
              {!partner && (
                <button
                  onClick={() => setShowPartnerRegister(true)}
                  className="flex items-center gap-1 px-3 py-1.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition"
                  data-testid="register-partner-btn"
                >
                  <Store className="w-3.5 h-3.5" /> Registar como Parceiro
                </button>
              )}
            </div>

            {!partner && (
              <p className="text-dark-400 text-sm">
                Registe-se como parceiro para receber pagamentos directamente dos clientes. O admin ira aprovar o seu registo.
              </p>
            )}

            {partner && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">{partner.nome_negocio}</p>
                    <p className="text-dark-500 text-xs">{(PARTNER_TIPOS.find(t => t.value === partner.tipo) || {}).label || partner.tipo} - {partner.cidade}, {partner.provincia}</p>
                  </div>
                  <Badge variant={partner.status === 'aprovado' ? 'success' : partner.status === 'pendente' ? 'warning' : partner.status === 'suspenso' ? 'danger' : 'default'}>
                    {partner.status}
                  </Badge>
                </div>

                {/* Payment methods summary */}
                <div className="grid grid-cols-3 gap-2">
                  <div className={`p-2 rounded-lg text-center text-xs ${partner.aceita_unitel_money ? 'bg-green-500/10 text-green-400' : 'bg-dark-800 text-dark-500'}`}>
                    <Smartphone className="w-4 h-4 mx-auto mb-0.5" />
                    Unitel Money
                    {partner.aceita_unitel_money && <p className="font-mono text-xs mt-0.5">{partner.unitel_money_numero}</p>}
                  </div>
                  <div className={`p-2 rounded-lg text-center text-xs ${partner.aceita_transferencia ? 'bg-blue-500/10 text-blue-400' : 'bg-dark-800 text-dark-500'}`}>
                    <Building2 className="w-4 h-4 mx-auto mb-0.5" />
                    Transferencia
                    {partner.aceita_transferencia && <p className="font-mono text-xs mt-0.5">{partner.banco_nome}</p>}
                  </div>
                  <div className={`p-2 rounded-lg text-center text-xs ${partner.aceita_dinheiro ? 'bg-yellow-500/10 text-yellow-400' : 'bg-dark-800 text-dark-500'}`}>
                    <Banknote className="w-4 h-4 mx-auto mb-0.5" />
                    Dinheiro
                  </div>
                </div>

                <button
                  onClick={() => setShowPartnerPayment(true)}
                  className="w-full py-2 bg-dark-800 hover:bg-dark-700 border border-dark-700 text-white text-sm rounded-lg transition"
                  data-testid="config-partner-payment-btn"
                >
                  Configurar Dados de Pagamento
                </button>

                {partner.admin_nota && (
                  <p className="text-dark-500 text-xs">Nota admin: {partner.admin_nota}</p>
                )}
              </div>
            )}
          </div>
        )}

        {/* My Payments */}
        {payments.length > 0 && (
          <div className="bg-dark-900 border border-dark-800 rounded-xl p-5" data-testid="my-payments">
            <h3 className="text-white font-semibold text-sm mb-3 flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-primary-400" /> Meus Pagamentos
            </h3>
            <div className="space-y-2">
              {payments.slice(0, 10).map((p, i) => (
                <div key={p.id || i} className="flex items-center justify-between p-3 bg-dark-800 rounded-lg" data-testid={`my-payment-${i}`}>
                  <div className="flex items-center gap-3">
                    {p.metodo === 'transferencia' ? <Building2 className="w-4 h-4 text-blue-400" /> : <Banknote className="w-4 h-4 text-green-400" />}
                    <div>
                      <p className="text-white text-sm font-medium font-mono">{p.referencia}</p>
                      <p className="text-dark-500 text-xs">{p.origem_tipo} - {new Date(p.created_at).toLocaleDateString('pt-AO')}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-accent-400 font-bold text-sm">{Number(p.valor_total).toLocaleString('pt-AO')} Kz</p>
                    <Badge variant={p.status === 'confirmado' ? 'success' : p.status === 'pendente' ? 'warning' : p.status === 'falhado' ? 'danger' : 'default'}>
                      {p.status}
                    </Badge>
                  </div>
                </div>
              ))}
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
      {showPartnerRegister && (
        <PartnerRegisterForm
          onClose={() => setShowPartnerRegister(false)}
          onCreated={() => { setShowPartnerRegister(false); fetchData(); }}
        />
      )}
      {showPartnerPayment && partner && (
        <PartnerPaymentForm
          partner={partner}
          onClose={() => setShowPartnerPayment(false)}
          onUpdated={() => { setShowPartnerPayment(false); fetchData(); }}
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


const PARTNER_TIPOS = [
  { value: 'motorista', label: 'Motorista' },
  { value: 'motoqueiro', label: 'Motoqueiro' },
  { value: 'proprietario', label: 'Proprietario' },
  { value: 'staff', label: 'Staff' },
  { value: 'guia_turista', label: 'Guia Turista' },
  { value: 'agente_imobiliario', label: 'Agente Imobiliario' },
  { value: 'agente_viagem', label: 'Agente de Viagem' },
];

function PartnerRegisterForm({ onClose, onCreated }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    const fd = new FormData(e.target);
    try {
      await api.registerPartner({
        tipo: fd.get('tipo'),
        nome_negocio: fd.get('nome_negocio'),
        descricao: fd.get('descricao') || null,
        provincia: fd.get('provincia') || null,
        cidade: fd.get('cidade') || null,
      });
      onCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <FormModal title="Registar como Parceiro" onClose={onClose}>
      <form onSubmit={handleSubmit} data-testid="partner-register-form">
        <FormField label="Tipo de Parceiro *">
          <FormSelect name="tipo" options={PARTNER_TIPOS} placeholder="Seleccionar tipo..." required />
        </FormField>
        <FormField label="Nome do Negocio *">
          <FormInput name="nome_negocio" placeholder="Ex: Loja do Joao" required />
        </FormField>
        <FormField label="Descricao">
          <FormTextarea name="descricao" placeholder="Descreva o seu negocio..." rows={3} />
        </FormField>
        <FormField label="Provincia">
          <FormInput name="provincia" placeholder="Ex: Luanda" />
        </FormField>
        <FormField label="Cidade">
          <FormInput name="cidade" placeholder="Ex: Luanda" />
        </FormField>
        {error && <p className="text-red-400 text-sm mb-3" data-testid="form-error">{error}</p>}
        <SubmitButton loading={loading}>Registar Parceiro</SubmitButton>
      </form>
    </FormModal>
  );
}

function PartnerPaymentForm({ partner, onClose, onUpdated }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    const fd = new FormData(e.target);
    try {
      await api.updatePartnerPayment({
        unitel_money_numero: fd.get('unitel_money_numero') || null,
        unitel_money_titular: fd.get('unitel_money_titular') || null,
        aceita_unitel_money: fd.get('aceita_unitel_money') === 'on',
        banco_nome: fd.get('banco_nome') || null,
        banco_conta: fd.get('banco_conta') || null,
        banco_iban: fd.get('banco_iban') || null,
        banco_titular: fd.get('banco_titular') || null,
        aceita_transferencia: fd.get('aceita_transferencia') === 'on',
        aceita_dinheiro: fd.get('aceita_dinheiro') === 'on',
      });
      onUpdated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <FormModal title="Configurar Dados de Pagamento" onClose={onClose}>
      <form onSubmit={handleSubmit} data-testid="partner-payment-form">
        {/* Unitel Money */}
        <div className="mb-4 p-3 bg-dark-800 rounded-lg">
          <label className="flex items-center gap-2 text-white text-sm font-medium mb-2">
            <input type="checkbox" name="aceita_unitel_money" defaultChecked={partner.aceita_unitel_money} className="rounded border-dark-600" />
            <Smartphone className="w-4 h-4 text-orange-400" /> Aceitar Unitel Money
          </label>
          <FormField label="Numero Unitel Money">
            <FormInput name="unitel_money_numero" placeholder="+244 9XX XXX XXX" defaultValue={partner.unitel_money_numero || ''} />
          </FormField>
          <FormField label="Titular">
            <FormInput name="unitel_money_titular" placeholder="Nome do titular" defaultValue={partner.unitel_money_titular || ''} />
          </FormField>
        </div>

        {/* Transferencia */}
        <div className="mb-4 p-3 bg-dark-800 rounded-lg">
          <label className="flex items-center gap-2 text-white text-sm font-medium mb-2">
            <input type="checkbox" name="aceita_transferencia" defaultChecked={partner.aceita_transferencia} className="rounded border-dark-600" />
            <Building2 className="w-4 h-4 text-blue-400" /> Aceitar Transferencia Bancaria
          </label>
          <FormField label="Banco">
            <FormInput name="banco_nome" placeholder="Ex: BAI" defaultValue={partner.banco_nome || ''} />
          </FormField>
          <FormField label="Numero de Conta">
            <FormInput name="banco_conta" placeholder="Numero da conta" defaultValue={partner.banco_conta || ''} />
          </FormField>
          <FormField label="IBAN">
            <FormInput name="banco_iban" placeholder="AO06 ..." defaultValue={partner.banco_iban || ''} />
          </FormField>
          <FormField label="Titular">
            <FormInput name="banco_titular" placeholder="Nome do titular" defaultValue={partner.banco_titular || ''} />
          </FormField>
        </div>

        {/* Dinheiro */}
        <div className="mb-4 p-3 bg-dark-800 rounded-lg">
          <label className="flex items-center gap-2 text-white text-sm font-medium">
            <input type="checkbox" name="aceita_dinheiro" defaultChecked={partner.aceita_dinheiro} className="rounded border-dark-600" />
            <Banknote className="w-4 h-4 text-green-400" /> Aceitar Dinheiro (Cash)
          </label>
        </div>

        {error && <p className="text-red-400 text-sm mb-3" data-testid="form-error">{error}</p>}
        <SubmitButton loading={loading}>Guardar Configuracao</SubmitButton>
      </form>
    </FormModal>
  );
}
