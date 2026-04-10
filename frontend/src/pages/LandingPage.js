import React, { useState } from 'react';
import {
  Calendar, ShoppingBag, Home, MapPin, Building2, Package,
  UtensilsCrossed, Car, ChevronRight, Users, Mail, Phone,
  Globe, TrendingUp, Shield, Star, ArrowRight, Menu, X
} from 'lucide-react';

const MODULES = [
  { icon: Calendar, label: 'Eventos', desc: 'Descubra e compre bilhetes para os melhores eventos de Angola', color: '#dc2626' },
  { icon: ShoppingBag, label: 'Marketplace', desc: 'Compre e venda produtos com entrega em toda Angola', color: '#eab308' },
  { icon: Home, label: 'Alojamento', desc: 'Reserve quartos, apartamentos e casas de ferias', color: '#3b82f6' },
  { icon: MapPin, label: 'Turismo', desc: 'Experiencias turisticas unicas em Angola', color: '#22c55e' },
  { icon: Building2, label: 'Imobiliario', desc: 'Compra, venda e arrendamento de imoveis', color: '#a855f7' },
  { icon: Package, label: 'Entregas', desc: 'Envie e receba encomendas com rastreio GPS', color: '#f97316' },
  { icon: UtensilsCrossed, label: 'Restaurantes', desc: 'Encomende comida dos melhores restaurantes', color: '#ef4444' },
  { icon: Car, label: 'Taxi', desc: 'Viagens seguras com motoristas verificados', color: '#eab308' },
];

const TEAM = [
  { nome: 'Joao Nhimi', cargo: 'CEO', area: 'Nhimi Corporate' },
  { nome: 'Miguel da Costa', cargo: 'Conselheiro', area: 'Estrategia' },
  { nome: 'Eliseu da Costa', cargo: 'IT', area: 'Tecnologia' },
  { nome: 'Filipe da Costa', cargo: 'Marketing', area: 'Comunicacao' },
  { nome: 'Joao Malonda', cargo: 'Relacoes Publicas', area: 'Comunicacao' },
  { nome: 'Ansty Kavango', cargo: 'Contabilista', area: 'Financas' },
  { nome: 'Eva Kambala', cargo: 'Assistente Administrativa', area: 'Operacoes' },
];

export default function LandingPage({ onGoToApp }) {
  const [mobileMenu, setMobileMenu] = useState(false);

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    setMobileMenu(false);
  };

  const goTo = (path) => {
    window.location.href = path;
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white" data-testid="landing-page">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0a0a0a]/90 backdrop-blur-xl border-b border-[#262626]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-lg bg-[#dc2626] flex items-center justify-center">
              <span className="text-white text-sm font-black">T</span>
            </div>
            <div>
              <span className="text-white font-black text-sm">TUDO</span>
              <span className="text-[#eab308] font-black text-sm">Aqui</span>
            </div>
          </div>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-6">
            {['sobre', 'modulos', 'equipa', 'investidores', 'contacto'].map(s => (
              <button key={s} onClick={() => scrollTo(s)} className="text-[#a3a3a3] hover:text-white text-sm capitalize transition">
                {s}
              </button>
            ))}
            <button
              onClick={onGoToApp}
              data-testid="landing-enter-btn"
              className="px-4 py-2 bg-[#dc2626] hover:bg-[#b91c1c] text-white text-sm font-semibold rounded-lg transition"
            >
              Entrar
            </button>
          </div>

          {/* Mobile hamburger */}
          <button className="md:hidden p-2 text-[#a3a3a3]" onClick={() => setMobileMenu(!mobileMenu)}>
            {mobileMenu ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile menu */}
        {mobileMenu && (
          <div className="md:hidden bg-[#171717] border-t border-[#262626] px-4 py-4 space-y-3">
            {['sobre', 'modulos', 'equipa', 'investidores', 'contacto'].map(s => (
              <button key={s} onClick={() => scrollTo(s)} className="block w-full text-left text-[#a3a3a3] hover:text-white text-sm capitalize py-2">
                {s}
              </button>
            ))}
            <button onClick={onGoToApp} className="w-full py-2 bg-[#dc2626] text-white text-sm font-semibold rounded-lg">
              Entrar na App
            </button>
          </div>
        )}
      </nav>

      {/* Hero */}
      <section className="pt-24 pb-16 sm:pt-32 sm:pb-24 px-4" data-testid="hero-section">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-[#dc2626]/10 border border-[#dc2626]/20 rounded-full mb-6">
            <Star className="w-3.5 h-3.5 text-[#eab308]" />
            <span className="text-[#eab308] text-xs font-medium">SuperApp de Angola</span>
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-tight mb-4">
            A sua vida em um{' '}
            <span className="bg-gradient-to-r from-[#dc2626] to-[#eab308] bg-clip-text text-transparent">
              so lugar
            </span>
          </h1>
          <p className="text-base sm:text-lg text-[#a3a3a3] max-w-2xl mx-auto mb-8">
            Eventos, compras, restaurantes, alojamento, turismo, entregas, taxi e imobiliario.
            Tudo o que precisa numa unica aplicacao feita por e para angolanos.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <button
              onClick={onGoToApp}
              data-testid="hero-cta-btn"
              className="w-full sm:w-auto px-8 py-3.5 bg-[#dc2626] hover:bg-[#b91c1c] text-white font-bold rounded-xl text-base transition flex items-center justify-center gap-2"
            >
              Comecar Agora <ArrowRight className="w-5 h-5" />
            </button>
            <button
              onClick={() => scrollTo('investidores')}
              data-testid="hero-invest-btn"
              className="w-full sm:w-auto px-8 py-3.5 bg-[#171717] border border-[#262626] hover:border-[#eab308] text-[#eab308] font-bold rounded-xl text-base transition flex items-center justify-center gap-2"
            >
              <TrendingUp className="w-5 h-5" /> Investir no Projecto
            </button>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-8 border-y border-[#262626]">
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
          {[
            { v: '8', l: 'Modulos' },
            { v: '18', l: 'Provincias' },
            { v: '100%', l: 'Angolano' },
            { v: '24/7', l: 'Disponivel' },
          ].map((s, i) => (
            <div key={i}>
              <p className="text-2xl sm:text-3xl font-black text-white">{s.v}</p>
              <p className="text-xs text-[#a3a3a3] mt-1">{s.l}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Sobre */}
      <section id="sobre" className="py-16 sm:py-24 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-base sm:text-lg font-bold text-[#dc2626] mb-2">Sobre o TUDOaqui</h2>
          <h3 className="text-2xl sm:text-3xl font-black mb-6">O SuperApp que Angola merece</h3>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <p className="text-[#a3a3a3] text-sm leading-relaxed mb-4">
                O TUDOaqui e a primeira super aplicacao angolana que reune todos os servicos do dia-a-dia
                numa unica plataforma. Desde comprar bilhetes para eventos, encomendar comida, reservar
                alojamento, ate chamar um taxi ou enviar encomendas — tudo ao alcance de um toque.
              </p>
              <p className="text-[#a3a3a3] text-sm leading-relaxed">
                Desenvolvido em Angola, para Angola. Com pagamento por transferencia bancaria (BAI),
                Unitel Money e dinheiro. Suporte completo em portugues e adaptado a realidade angolana.
              </p>
            </div>
            <div className="space-y-3">
              {[
                { icon: Shield, text: 'Pagamentos seguros com multiplas opcoes' },
                { icon: Globe, text: 'Cobertura em todas as 18 provincias' },
                { icon: Users, text: 'Sistema de parceiros com pagamento directo' },
                { icon: Star, text: 'Avaliacoes e reviews em todos os modulos' },
              ].map((f, i) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-[#171717] rounded-xl border border-[#262626]">
                  <div className="w-8 h-8 rounded-lg bg-[#dc2626]/10 flex items-center justify-center flex-shrink-0">
                    <f.icon className="w-4 h-4 text-[#dc2626]" />
                  </div>
                  <span className="text-sm text-[#a3a3a3]">{f.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Modulos */}
      <section id="modulos" className="py-16 sm:py-24 px-4 bg-[#0f0f0f]">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-base sm:text-lg font-bold text-[#eab308] mb-2">Modulos</h2>
            <h3 className="text-2xl sm:text-3xl font-black">8 servicos, 1 aplicacao</h3>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {MODULES.map((m, i) => (
              <div
                key={i}
                className="p-5 bg-[#171717] border border-[#262626] rounded-xl hover:border-[#404040] transition group"
                data-testid={`module-card-${m.label.toLowerCase()}`}
              >
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center mb-3"
                  style={{ backgroundColor: `${m.color}15` }}
                >
                  <m.icon className="w-5 h-5" style={{ color: m.color }} />
                </div>
                <h4 className="text-white font-bold text-sm mb-1">{m.label}</h4>
                <p className="text-[#a3a3a3] text-xs leading-relaxed">{m.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Equipa */}
      <section id="equipa" className="py-16 sm:py-24 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-base sm:text-lg font-bold text-[#dc2626] mb-2">Equipa</h2>
            <h3 className="text-2xl sm:text-3xl font-black">Quem esta por detras do TUDOaqui</h3>
          </div>

          {/* Empresa */}
          <div className="grid md:grid-cols-2 gap-6 mb-10">
            <div className="p-6 bg-[#171717] border border-[#262626] rounded-xl">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg bg-[#dc2626]/10 flex items-center justify-center">
                  <Building2 className="w-5 h-5 text-[#dc2626]" />
                </div>
                <div>
                  <h4 className="text-white font-bold text-sm">Nhimi Corporate</h4>
                  <p className="text-[#a3a3a3] text-xs">Dono do Projecto</p>
                </div>
              </div>
              <p className="text-[#a3a3a3] text-xs leading-relaxed">
                NIF: 5001193074 — Com sede em Luanda, representado pelo Sr. Joao Nhimi.
              </p>
            </div>
            <div className="p-6 bg-[#171717] border border-[#262626] rounded-xl">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg bg-[#eab308]/10 flex items-center justify-center">
                  <Globe className="w-5 h-5 text-[#eab308]" />
                </div>
                <div>
                  <h4 className="text-white font-bold text-sm">Sincesoft</h4>
                  <p className="text-[#a3a3a3] text-xs">Empresa Desenvolvedora</p>
                </div>
              </div>
              <p className="text-[#a3a3a3] text-xs leading-relaxed">
                Sinceridade Service — NIF: 2403104787, com sede em Luanda.
                <br />
                <a href="https://3s-ao.com" target="_blank" rel="noopener noreferrer" className="text-[#eab308] hover:underline">3s-ao.com</a>
                {' | '}
                <a href="mailto:apoioaocliente@3s-ao.com" className="text-[#eab308] hover:underline">apoioaocliente@3s-ao.com</a>
                {' | Tel: 951 064 945'}
              </p>
            </div>
          </div>

          {/* Staff */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {TEAM.map((p, i) => (
              <div key={i} className="p-4 bg-[#171717] border border-[#262626] rounded-xl text-center" data-testid={`team-${i}`}>
                <div className="w-12 h-12 rounded-full bg-[#dc2626]/10 flex items-center justify-center mx-auto mb-2">
                  <span className="text-[#dc2626] font-bold text-sm">{p.nome[0]}</span>
                </div>
                <h4 className="text-white font-bold text-xs">{p.nome}</h4>
                <p className="text-[#eab308] text-[10px] font-medium">{p.cargo}</p>
                <p className="text-[#a3a3a3] text-[10px]">{p.area}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Investidores */}
      <section id="investidores" className="py-16 sm:py-24 px-4 bg-[#0f0f0f]">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-[#eab308]/10 border border-[#eab308]/20 rounded-full mb-4">
            <TrendingUp className="w-3.5 h-3.5 text-[#eab308]" />
            <span className="text-[#eab308] text-xs font-medium">Oportunidade de Investimento</span>
          </div>
          <h3 className="text-2xl sm:text-3xl font-black mb-4">Faca Parte do Projecto</h3>
          <p className="text-[#a3a3a3] text-sm max-w-2xl mx-auto mb-8">
            O TUDOaqui esta a abrir portas para investidores que queiram fazer parte desta revolucao digital
            em Angola. Junte-se a nos e construa o futuro da economia digital angolana.
          </p>

          <div className="max-w-md mx-auto p-6 bg-[#171717] border-2 border-[#eab308]/30 rounded-2xl mb-8" data-testid="invest-card">
            <p className="text-[#a3a3a3] text-xs uppercase tracking-wider mb-2">Investimento minimo</p>
            <p className="text-3xl sm:text-4xl font-black text-[#eab308] mb-1">5.400.000,00 Kz</p>
            <p className="text-[#a3a3a3] text-sm mb-4">Equivalente a <span className="text-white font-bold">0,5%</span> de participacao</p>
            <div className="space-y-2 text-left mb-6">
              {[
                'Participacao directa no projecto',
                'Retorno sobre o crescimento da plataforma',
                'Relatorios trimestrais de desempenho',
                'Acesso a reunioes do conselho',
              ].map((b, i) => (
                <div key={i} className="flex items-center gap-2">
                  <ChevronRight className="w-3.5 h-3.5 text-[#eab308] flex-shrink-0" />
                  <span className="text-[#a3a3a3] text-xs">{b}</span>
                </div>
              ))}
            </div>
            <a
              href="mailto:nhimi@nhimi.com?subject=Interesse%20em%20Investir%20no%20TUDOaqui"
              data-testid="invest-cta-btn"
              className="block w-full py-3 bg-[#eab308] hover:bg-[#ca8a04] text-[#0a0a0a] font-bold rounded-xl text-sm transition text-center"
            >
              Contactar para Investir
            </a>
          </div>

          <p className="text-[#a3a3a3] text-xs">
            Para mais informacoes, contacte directamente: <a href="mailto:nhimi@nhimi.com" className="text-[#eab308] hover:underline">nhimi@nhimi.com</a> ou <a href="tel:+244924865667" className="text-[#eab308] hover:underline">+244 924 865 667</a>
          </p>
        </div>
      </section>

      {/* Contacto */}
      <section id="contacto" className="py-16 sm:py-24 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-base sm:text-lg font-bold text-[#dc2626] mb-2">Contacto</h2>
            <h3 className="text-2xl sm:text-3xl font-black">Fale Connosco</h3>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <a href="mailto:nhimi@nhimi.com" className="p-5 bg-[#171717] border border-[#262626] rounded-xl hover:border-[#dc2626] transition text-center">
              <Mail className="w-6 h-6 text-[#dc2626] mx-auto mb-2" />
              <p className="text-white font-bold text-sm mb-1">Email Projecto</p>
              <p className="text-[#a3a3a3] text-xs">nhimi@nhimi.com</p>
            </a>
            <a href="tel:+244924865667" className="p-5 bg-[#171717] border border-[#262626] rounded-xl hover:border-[#eab308] transition text-center">
              <Phone className="w-6 h-6 text-[#eab308] mx-auto mb-2" />
              <p className="text-white font-bold text-sm mb-1">Telefone</p>
              <p className="text-[#a3a3a3] text-xs">+244 924 865 667</p>
            </a>
            <a href="mailto:apoioaocliente@3s-ao.com" className="p-5 bg-[#171717] border border-[#262626] rounded-xl hover:border-[#a3a3a3] transition text-center">
              <Globe className="w-6 h-6 text-[#a3a3a3] mx-auto mb-2" />
              <p className="text-white font-bold text-sm mb-1">Suporte Tecnico</p>
              <p className="text-[#a3a3a3] text-xs">apoioaocliente@3s-ao.com</p>
              <p className="text-[#a3a3a3] text-xs">+244 951 064 945</p>
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-[#262626] bg-[#0f0f0f]">
        <div className="max-w-5xl mx-auto">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-md bg-[#dc2626] flex items-center justify-center">
                <span className="text-white text-[10px] font-black">T</span>
              </div>
              <span className="text-white font-black text-xs">TUDO<span className="text-[#eab308]">Aqui</span></span>
            </div>
            <div className="flex gap-6">
              <button onClick={() => goTo('/privacidade')} className="text-[#a3a3a3] hover:text-white text-xs transition" data-testid="footer-privacy-link">
                Politica de Privacidade
              </button>
              <button onClick={() => goTo('/termos')} className="text-[#a3a3a3] hover:text-white text-xs transition" data-testid="footer-terms-link">
                Termos de Servico
              </button>
              <a href="https://3s-ao.com" target="_blank" rel="noopener noreferrer" className="text-[#a3a3a3] hover:text-white text-xs transition">
                3s-ao.com
              </a>
            </div>
          </div>
          <p className="text-[#a3a3a3] text-[10px] text-center">
            2025 TUDOaqui. Nhimi Corporate (NIF: 5001193074) | Desenvolvido por Sincesoft (NIF: 2403104787)
          </p>
        </div>
      </footer>
    </div>
  );
}
