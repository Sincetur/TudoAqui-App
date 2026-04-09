import React, { useState, useEffect } from 'react';
import { X, Building2, Banknote, Copy, Check, Clock, AlertCircle } from 'lucide-react';
import { api } from '../api';

const METODOS = [
  { id: 'transferencia', nome: 'Transferencia Bancaria', desc: 'Via BAI. Confirmacao em ate 24h.', Icon: Building2 },
  { id: 'dinheiro', nome: 'Dinheiro (Cash)', desc: 'Pagamento na entrega ou no local.', Icon: Banknote },
];

export default function CheckoutModal({ origem_tipo, origem_id, valor, descricao, onClose, onSuccess }) {
  const [metodo, setMetodo] = useState('');
  const [bankInfo, setBankInfo] = useState(null);
  const [comprovativo, setComprovativo] = useState('');
  const [notas, setNotas] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(null);
  const [copied, setCopied] = useState('');

  useEffect(() => {
    api.getBankInfo().then(setBankInfo).catch(() => {});
  }, []);

  const formatPrice = (v) => `${Number(v).toLocaleString('pt-AO')} Kz`;

  const copyText = (text, field) => {
    navigator.clipboard.writeText(text.replace(/\s/g, '')).catch(() => {});
    setCopied(field);
    setTimeout(() => setCopied(''), 2000);
  };

  const handlePay = async () => {
    if (!metodo) { setError('Seleccione um metodo de pagamento'); return; }
    if (metodo === 'transferencia' && !comprovativo.trim()) {
      setError('Introduza a referencia do comprovativo');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const payment = await api.createPayment({
        origem_tipo,
        origem_id,
        metodo,
        valor,
        comprovativo_ref: metodo === 'transferencia' ? comprovativo.trim() : null,
        notas: notas.trim() || null,
      });
      setSuccess(payment);
      if (onSuccess) onSuccess(payment);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4" data-testid="checkout-success">
        <div className="bg-dark-900 border border-dark-800 rounded-2xl p-6 w-full max-w-md animate-slide-up">
          <div className="text-center">
            <div className="w-16 h-16 rounded-full bg-green-500/15 flex items-center justify-center mx-auto mb-4">
              <Check className="w-8 h-8 text-green-400" />
            </div>
            <h3 className="text-white font-bold text-lg mb-1">Pagamento Registado</h3>
            <p className="text-dark-400 text-sm mb-4">
              {metodo === 'transferencia'
                ? 'O seu pagamento sera confirmado em ate 24h apos verificacao do comprovativo.'
                : 'Prepare o valor exacto para pagamento no local.'}
            </p>
            <div className="bg-dark-800 rounded-lg p-3 mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-dark-400">Referencia</span>
                <span className="text-white font-mono text-xs">{success.referencia}</span>
              </div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-dark-400">Valor</span>
                <span className="text-accent-400 font-bold">{formatPrice(success.valor_total)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-dark-400">Estado</span>
                <span className="flex items-center gap-1 text-yellow-400 text-xs">
                  <Clock className="w-3 h-3" /> Pendente
                </span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-full py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition"
              data-testid="checkout-close-btn"
            >
              Fechar
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4" data-testid="checkout-modal">
      <div className="bg-dark-900 border border-dark-800 rounded-2xl w-full max-w-md max-h-[90vh] overflow-y-auto animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-800">
          <h3 className="text-white font-bold text-base">Pagamento</h3>
          <button onClick={onClose} className="p-1.5 text-dark-400 hover:text-white transition" data-testid="checkout-close">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Resumo */}
          <div className="bg-dark-800 rounded-xl p-4">
            <p className="text-dark-400 text-xs uppercase tracking-wider mb-1">Resumo</p>
            {descricao && <p className="text-white text-sm font-medium mb-2">{descricao}</p>}
            <div className="flex justify-between items-center">
              <span className="text-dark-400 text-sm">Total a pagar</span>
              <span className="text-accent-400 font-bold text-lg" data-testid="checkout-total">{formatPrice(valor)}</span>
            </div>
          </div>

          {/* Metodos */}
          <div>
            <p className="text-white text-sm font-semibold mb-2">Metodo de pagamento</p>
            <div className="space-y-2">
              {METODOS.map(m => (
                <button
                  key={m.id}
                  onClick={() => { setMetodo(m.id); setError(''); }}
                  data-testid={`payment-method-${m.id}`}
                  className={`w-full flex items-center gap-3 p-3 rounded-xl border transition ${
                    metodo === m.id
                      ? 'border-primary-500 bg-primary-500/10'
                      : 'border-dark-700 bg-dark-800 hover:border-dark-600'
                  }`}
                >
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    metodo === m.id ? 'bg-primary-600' : 'bg-dark-700'
                  }`}>
                    <m.Icon className="w-5 h-5 text-white" />
                  </div>
                  <div className="text-left flex-1">
                    <p className="text-white text-sm font-medium">{m.nome}</p>
                    <p className="text-dark-400 text-xs">{m.desc}</p>
                  </div>
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                    metodo === m.id ? 'border-primary-500' : 'border-dark-600'
                  }`}>
                    {metodo === m.id && <div className="w-2.5 h-2.5 rounded-full bg-primary-500" />}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Dados bancarios (se transferencia) */}
          {metodo === 'transferencia' && bankInfo && (
            <div className="bg-dark-800 rounded-xl p-4 space-y-3 animate-fade-in" data-testid="bank-info-section">
              <p className="text-white text-sm font-semibold">Dados para Transferencia</p>
              <BankField label="Banco" value={bankInfo.banco} onCopy={() => copyText(bankInfo.banco, 'banco')} copied={copied === 'banco'} />
              <BankField label="Conta" value={bankInfo.conta} onCopy={() => copyText(bankInfo.conta, 'conta')} copied={copied === 'conta'} />
              <BankField label="IBAN" value={bankInfo.iban} onCopy={() => copyText(bankInfo.iban, 'iban')} copied={copied === 'iban'} />
              <BankField label="SWIFT" value={bankInfo.swift} onCopy={() => copyText(bankInfo.swift, 'swift')} copied={copied === 'swift'} />
              <BankField label="Titular" value={bankInfo.titular} />
              <div className="flex items-start gap-2 pt-2 border-t border-dark-700">
                <AlertCircle className="w-4 h-4 text-accent-400 mt-0.5 flex-shrink-0" />
                <p className="text-dark-400 text-xs leading-relaxed">{bankInfo.instrucoes}</p>
              </div>

              {/* Comprovativo */}
              <div>
                <label className="text-dark-300 text-xs font-medium block mb-1">Referencia do comprovativo *</label>
                <input
                  type="text"
                  value={comprovativo}
                  onChange={e => setComprovativo(e.target.value)}
                  placeholder="Ex: TRF-20260409-123456"
                  data-testid="comprovativo-input"
                  className="w-full px-3 py-2.5 bg-dark-900 border border-dark-700 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition"
                />
              </div>
              <div>
                <label className="text-dark-300 text-xs font-medium block mb-1">Notas (opcional)</label>
                <input
                  type="text"
                  value={notas}
                  onChange={e => setNotas(e.target.value)}
                  placeholder="Informacao adicional..."
                  data-testid="notas-input"
                  className="w-full px-3 py-2.5 bg-dark-900 border border-dark-700 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition"
                />
              </div>
            </div>
          )}

          {/* Cash info */}
          {metodo === 'dinheiro' && (
            <div className="bg-dark-800 rounded-xl p-4 animate-fade-in" data-testid="cash-info-section">
              <div className="flex items-start gap-2">
                <Banknote className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-white text-sm font-medium">Pagamento em Dinheiro</p>
                  <p className="text-dark-400 text-xs mt-1">
                    Prepare o valor exacto de <span className="text-accent-400 font-bold">{formatPrice(valor)}</span> para pagamento na entrega ou no local.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <p className="text-red-400 text-sm flex items-center gap-1" data-testid="checkout-error">
              <AlertCircle className="w-4 h-4" /> {error}
            </p>
          )}

          {/* Submit */}
          <button
            onClick={handlePay}
            disabled={!metodo || loading}
            data-testid="checkout-pay-btn"
            className="w-full py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-dark-700 disabled:text-dark-500 text-white text-sm font-semibold rounded-xl transition"
          >
            {loading ? 'A processar...' : metodo === 'transferencia' ? 'Confirmar Transferencia' : metodo === 'dinheiro' ? 'Confirmar Pedido' : 'Seleccione um metodo'}
          </button>
        </div>
      </div>
    </div>
  );
}

function BankField({ label, value, onCopy, copied }) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <p className="text-dark-500 text-xs">{label}</p>
        <p className="text-white text-sm font-medium">{value}</p>
      </div>
      {onCopy && (
        <button onClick={onCopy} className="p-1.5 text-dark-400 hover:text-white transition" data-testid={`copy-${label.toLowerCase()}`}>
          {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
        </button>
      )}
    </div>
  );
}
