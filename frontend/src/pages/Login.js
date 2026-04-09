import React, { useState } from 'react';
import { Phone, ArrowRight, Shield, Loader2 } from 'lucide-react';
import { api } from '../api';

export default function Login({ onLogin }) {
  const [step, setStep] = useState('phone'); // phone | otp
  const [telefone, setTelefone] = useState('');
  const [codigo, setCodigo] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formattedPhone, setFormattedPhone] = useState('');

  const handleSendOtp = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await api.login(telefone);
      setFormattedPhone(result.telefone);
      setStep('otp');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await api.verifyOtp(formattedPhone || telefone, codigo);
      onLogin(result.user, { access_token: result.access_token, refresh_token: result.refresh_token });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-950 px-4" data-testid="login-page">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 mb-4">
            <span className="text-white text-2xl font-black">T</span>
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">
            TUDO<span className="text-primary-500">aqui</span>
          </h1>
          <p className="text-dark-400 text-sm mt-1">A sua vida, num so app.</p>
        </div>

        {/* Card */}
        <div className="bg-dark-900 border border-dark-700 rounded-2xl p-6 shadow-xl">
          {step === 'phone' ? (
            <form onSubmit={handleSendOtp} data-testid="phone-form">
              <h2 className="text-lg font-semibold text-white mb-1">Entrar</h2>
              <p className="text-dark-400 text-sm mb-6">Insira o seu numero de telefone angolano</p>

              <div className="relative mb-4">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                <input
                  data-testid="phone-input"
                  type="tel"
                  placeholder="+244 923 456 789"
                  value={telefone}
                  onChange={e => setTelefone(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-dark-800 border border-dark-600 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition"
                  required
                />
              </div>

              {error && <p className="text-red-400 text-sm mb-4" data-testid="error-message">{error}</p>}

              <button
                data-testid="send-otp-btn"
                type="submit"
                disabled={loading || !telefone}
                className="w-full flex items-center justify-center gap-2 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                  <>Enviar Codigo <ArrowRight className="w-4 h-4" /></>
                )}
              </button>
            </form>
          ) : (
            <form onSubmit={handleVerifyOtp} data-testid="otp-form">
              <h2 className="text-lg font-semibold text-white mb-1">Verificar Codigo</h2>
              <p className="text-dark-400 text-sm mb-6">
                Enviado para <span className="text-primary-400">{formattedPhone}</span>
              </p>

              <div className="relative mb-4">
                <Shield className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                <input
                  data-testid="otp-input"
                  type="text"
                  placeholder="Codigo OTP"
                  value={codigo}
                  onChange={e => setCodigo(e.target.value)}
                  maxLength={6}
                  className="w-full pl-11 pr-4 py-3 bg-dark-800 border border-dark-600 rounded-xl text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition text-center text-xl tracking-widest"
                  required
                />
              </div>

              {error && <p className="text-red-400 text-sm mb-4" data-testid="error-message">{error}</p>}

              <button
                data-testid="verify-otp-btn"
                type="submit"
                disabled={loading || codigo.length < 4}
                className="w-full flex items-center justify-center gap-2 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Verificar'}
              </button>

              <button
                type="button"
                onClick={() => { setStep('phone'); setError(''); setCodigo(''); }}
                className="w-full mt-3 py-2 text-dark-400 hover:text-white text-sm transition"
                data-testid="back-btn"
              >
                Voltar
              </button>
            </form>
          )}
        </div>

        <p className="text-center text-dark-600 text-xs mt-6">
          TUDOaqui SuperApp v1.0
        </p>
      </div>
    </div>
  );
}
