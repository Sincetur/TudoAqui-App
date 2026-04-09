import React, { useState, useEffect } from 'react';
import { X, Building2, Banknote, Smartphone, Copy, Check, Clock, AlertCircle } from 'lucide-react';
import { api } from '../api';

export default function CheckoutModal({ origem_tipo, origem_id, valor, descricao, partner_id, onClose, onSuccess }) {
  const [metodo, setMetodo] = useState('');
  const [partnerInfo, setPartnerInfo] = useState(null);
  const [fallbackBank, setFallbackBank] = useState(null);
  const [comprovativo, setComprovativo] = useState('');
  const [notas, setNotas] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingInfo, setLoadingInfo] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(null);
  const [copied, setCopied] = useState('');

  useEffect(() => {
    const fetchPaymentInfo = async () => {
      setLoadingInfo(true);
      try {
        if (partner_id) {
          const info = await api.getPartnerPaymentInfo(partner_id);
          setPartnerInfo(info);
        } else {
          const bank = await api.getBankInfo();
          setFallbackBank(bank);
        }
      } catch { /* ignore */ }
      setLoadingInfo(false);
    };
    fetchPaymentInfo();
  }, [partner_id]);

  const formatPrice = (v) => `${Number(v).toLocaleString('pt-AO')} Kz`;

  const copyText = (text, field) => {
    navigator.clipboard.writeText(text.replace(/\s/g, '')).catch(() => {});
    setCopied(field);
    setTimeout(() => setCopied(''), 2000);
  };

  // Build available methods
  const availableMethods = (() => {
    if (partnerInfo && partnerInfo.metodos) {
      return partnerInfo.metodos.map(m => ({
        id: m.id,
        nome: m.nome,
        desc: m.id === 'unitelmoney' ? `Envie para ${m.dados.numero}` : m.id === 'transferencia' ? `Via ${m.dados.banco || 'banco'}` : 'Pagamento no local',
        Icon: m.id === 'unitelmoney' ? Smartphone : m.id === 'transferencia' ? Building2 : Banknote,
        dados: m.dados,
      }));
    }
    return [
      { id: 'transferencia', nome: 'Transferencia Bancaria', desc: 'Via BAI. Confirmacao em ate 24h.', Icon: Building2, dados: fallbackBank },
      { id: 'dinheiro', nome: 'Dinheiro (Cash)', desc: 'Pagamento na entrega ou no local.', Icon: Banknote, dados: {} },
    ];
  })();

  const selectedMethodData = availableMethods.find(m => m.id === metodo);

  const needsComprovativo = metodo === 'transferencia' || metodo === 'unitelmoney';

  const handlePay = async () => {
    if (!metodo) { setError('Seleccione um metodo de pagamento'); return; }
    if (needsComprovativo && !comprovativo.trim()) {
      setError('Introduza a referencia do comprovativo');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const paymentMetodo = metodo === 'unitelmoney' ? 'transferencia' : metodo;
      const payment = await api.createPayment({
        origem_tipo,
        origem_id,
        metodo: paymentMetodo,
        valor,
        comprovativo_ref: needsComprovativo ? comprovativo.trim() : null,
        notas: notas.trim() || (metodo === 'unitelmoney' ? 'Pago via Unitel Money' : null),
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
              {needsComprovativo
                ? 'O seu pagamento sera confirmado em ate 24h apos verificacao.'
                : 'Prepare o valor exacto para pagamento no local.'}
            </p>
            {partnerInfo && <p className="text-dark-500 text-xs mb-3">Parceiro: {partnerInfo.parceiro}</p>}
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
          <div>
            <h3 className="text-white font-bold text-base">Pagamento</h3>
            {partnerInfo && <p className="text-dark-500 text-xs">Pagar a: {partnerInfo.parceiro}</p>}
          </div>
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

          {loadingInfo ? (
            <div className="text-center py-4"><span className="text-dark-400 text-sm">A carregar metodos...</span></div>
          ) : (
            <>
              {/* Metodos */}
              <div>
                <p className="text-white text-sm font-semibold mb-2">Metodo de pagamento</p>
                <div className="space-y-2">
                  {availableMethods.map(m => (
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

              {/* Unitel Money details */}
              {metodo === 'unitelmoney' && selectedMethodData?.dados && (
                <div className="bg-dark-800 rounded-xl p-4 space-y-3 animate-fade-in" data-testid="unitelmoney-info-section">
                  <p className="text-white text-sm font-semibold">Dados Unitel Money</p>
                  <BankField label="Numero" value={selectedMethodData.dados.numero} onCopy={() => copyText(selectedMethodData.dados.numero, 'numero')} copied={copied === 'numero'} />
                  <BankField label="Titular" value={selectedMethodData.dados.titular} />
                  <div className="flex items-start gap-2 pt-2 border-t border-dark-700">
                    <AlertCircle className="w-4 h-4 text-accent-400 mt-0.5 flex-shrink-0" />
                    <p className="text-dark-400 text-xs leading-relaxed">Envie {formatPrice(valor)} via Unitel Money para o numero acima e introduza a referencia da transaccao.</p>
                  </div>
                  <div>
                    <label className="text-dark-300 text-xs font-medium block mb-1">Referencia da transaccao *</label>
                    <input type="text" value={comprovativo} onChange={e => setComprovativo(e.target.value)} placeholder="Ex: UM-20260409-123456"
                      data-testid="comprovativo-input"
                      className="w-full px-3 py-2.5 bg-dark-900 border border-dark-700 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition" />
                  </div>
                </div>
              )}

              {/* Transferencia details */}
              {metodo === 'transferencia' && (
                <div className="bg-dark-800 rounded-xl p-4 space-y-3 animate-fade-in" data-testid="bank-info-section">
                  <p className="text-white text-sm font-semibold">Dados para Transferencia</p>
                  {selectedMethodData?.dados?.banco && <BankField label="Banco" value={selectedMethodData.dados.banco} onCopy={() => copyText(selectedMethodData.dados.banco, 'banco')} copied={copied === 'banco'} />}
                  {selectedMethodData?.dados?.conta && <BankField label="Conta" value={selectedMethodData.dados.conta} onCopy={() => copyText(selectedMethodData.dados.conta, 'conta')} copied={copied === 'conta'} />}
                  {(selectedMethodData?.dados?.iban || fallbackBank?.iban) && <BankField label="IBAN" value={selectedMethodData?.dados?.iban || fallbackBank?.iban} onCopy={() => copyText(selectedMethodData?.dados?.iban || fallbackBank?.iban, 'iban')} copied={copied === 'iban'} />}
                  {(selectedMethodData?.dados?.swift || fallbackBank?.swift) && <BankField label="SWIFT" value={selectedMethodData?.dados?.swift || fallbackBank?.swift} onCopy={() => copyText(selectedMethodData?.dados?.swift || fallbackBank?.swift, 'swift')} copied={copied === 'swift'} />}
                  {(selectedMethodData?.dados?.titular || fallbackBank?.titular) && <BankField label="Titular" value={selectedMethodData?.dados?.titular || fallbackBank?.titular} />}
                  <div className="flex items-start gap-2 pt-2 border-t border-dark-700">
                    <AlertCircle className="w-4 h-4 text-accent-400 mt-0.5 flex-shrink-0" />
                    <p className="text-dark-400 text-xs leading-relaxed">Apos efectuar a transferencia, introduza a referencia do comprovativo abaixo.</p>
                  </div>
                  <div>
                    <label className="text-dark-300 text-xs font-medium block mb-1">Referencia do comprovativo *</label>
                    <input type="text" value={comprovativo} onChange={e => setComprovativo(e.target.value)} placeholder="Ex: TRF-20260409-123456"
                      data-testid="comprovativo-input"
                      className="w-full px-3 py-2.5 bg-dark-900 border border-dark-700 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition" />
                  </div>
                  <div>
                    <label className="text-dark-300 text-xs font-medium block mb-1">Notas (opcional)</label>
                    <input type="text" value={notas} onChange={e => setNotas(e.target.value)} placeholder="Informacao adicional..."
                      data-testid="notas-input"
                      className="w-full px-3 py-2.5 bg-dark-900 border border-dark-700 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition" />
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
                        Prepare o valor exacto de <span className="text-accent-400 font-bold">{formatPrice(valor)}</span> para pagamento
                        {partnerInfo ? ` a ${partnerInfo.parceiro}` : ' na entrega ou no local'}.
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
                {loading ? 'A processar...' :
                  metodo === 'unitelmoney' ? 'Confirmar Unitel Money' :
                  metodo === 'transferencia' ? 'Confirmar Transferencia' :
                  metodo === 'dinheiro' ? 'Confirmar Pedido' : 'Seleccione um metodo'}
              </button>
            </>
          )}
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
