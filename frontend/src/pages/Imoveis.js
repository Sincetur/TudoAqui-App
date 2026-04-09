import React, { useEffect, useState } from 'react';
import { Building2, Search, MapPin, Bed, Maximize, Heart, Star } from 'lucide-react';
import { api } from '../api';
import { PageHeader, EmptyState, LoadingState, ItemCard, Badge } from '../components/Layout';

export default function Imoveis() {
  const [properties, setProperties] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [tab, setTab] = useState('imoveis');
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    Promise.all([
      api.listImoveis().catch(() => []),
      api.listAgents().catch(() => []),
    ]).then(([props, ags]) => {
      setProperties(Array.isArray(props) ? props : []);
      setAgents(Array.isArray(ags) ? ags : []);
    }).catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const formatPrice = (v) => v ? `${Number(v).toLocaleString('pt-AO')} Kz` : '';
  const filtered = properties.filter(p =>
    (p.titulo || '').toLowerCase().includes(search.toLowerCase()) ||
    (p.cidade || '').toLowerCase().includes(search.toLowerCase())
  );

  if (selected) {
    return <ImovelDetail property={selected} onBack={() => setSelected(null)} formatPrice={formatPrice} />;
  }

  return (
    <div data-testid="imoveis-page">
      <PageHeader title="Imobiliario" subtitle={`${properties.length} imoveis | ${agents.length} agentes`} />
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-fade-in">
        {/* Tabs */}
        <div className="flex gap-1 bg-dark-900 p-1 rounded-lg border border-dark-800 w-fit">
          <button
            onClick={() => setTab('imoveis')}
            data-testid="tab-imoveis"
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition ${tab === 'imoveis' ? 'bg-primary-600 text-white' : 'text-dark-400 hover:text-white'}`}
          >Imoveis</button>
          <button
            onClick={() => setTab('agentes')}
            data-testid="tab-agentes"
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition ${tab === 'agentes' ? 'bg-primary-600 text-white' : 'text-dark-400 hover:text-white'}`}
          >Agentes</button>
        </div>

        {tab === 'imoveis' && (
          <>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
              <input
                data-testid="imoveis-search"
                type="text"
                placeholder="Procurar imoveis..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-dark-900 border border-dark-800 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition"
              />
            </div>

            {loading && <LoadingState />}
            {error && <p className="text-red-400 text-sm">{error}</p>}
            {!loading && !error && filtered.length === 0 && (
              <EmptyState icon={Building2} title="Nenhum imovel" description="Os imoveis aparecerao aqui quando disponiveis." />
            )}

            <div className="grid gap-3 sm:grid-cols-2">
              {filtered.map((p, i) => (
                <ItemCard key={p.id || i} onClick={() => setSelected(p)} testId={`imovel-item-${i}`}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant={p.tipo_transacao === 'venda' ? 'primary' : 'accent'}>
                          {p.tipo_transacao === 'venda' ? 'Venda' : 'Arrendamento'}
                        </Badge>
                        {p.destaque && <Badge variant="warning">Destaque</Badge>}
                      </div>
                      <h3 className="text-white font-semibold text-sm">{p.titulo}</h3>
                    </div>
                    <Heart className="w-4 h-4 text-dark-500 flex-shrink-0 ml-2" />
                  </div>
                  <p className="text-accent-400 font-bold text-sm">
                    {p.preco_venda ? formatPrice(p.preco_venda) : formatPrice(p.preco_arrendamento)}
                    {p.preco_arrendamento && !p.preco_venda && <span className="text-dark-500 text-xs font-normal">/mes</span>}
                  </p>
                  <div className="flex items-center gap-3 text-xs text-dark-400 mt-2">
                    <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{p.cidade}{p.bairro ? `, ${p.bairro}` : ''}</span>
                    <span className="flex items-center gap-1"><Bed className="w-3 h-3" />{p.quartos} T</span>
                    {p.area_util && <span className="flex items-center gap-1"><Maximize className="w-3 h-3" />{p.area_util}m2</span>}
                  </div>
                </ItemCard>
              ))}
            </div>
          </>
        )}

        {tab === 'agentes' && (
          <div className="grid gap-3 sm:grid-cols-2">
            {agents.length === 0 && !loading && (
              <EmptyState icon={Building2} title="Nenhum agente" description="Os agentes aparecerao aqui." />
            )}
            {agents.map((a, i) => (
              <ItemCard key={a.id || i} testId={`agent-item-${i}`}>
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-dark-800 flex items-center justify-center flex-shrink-0">
                    <span className="text-dark-400 font-bold text-lg">{(a.nome_profissional || 'A')[0]}</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-white font-semibold text-sm">{a.nome_profissional}</h3>
                    {a.provincias && <p className="text-dark-400 text-xs">{a.provincias.join(', ')}</p>}
                    {a.rating_medio > 0 && (
                      <div className="flex items-center gap-1 text-xs text-accent-400 mt-0.5">
                        <Star className="w-3 h-3 fill-accent-400" />{a.rating_medio}
                      </div>
                    )}
                  </div>
                </div>
              </ItemCard>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function ImovelDetail({ property, onBack, formatPrice }) {
  const p = property;
  return (
    <div data-testid="imovel-detail">
      <PageHeader title={p.titulo || 'Imovel'} onBack={onBack} />
      <div className="max-w-4xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-slide-up">
        <div className="bg-dark-900 border border-dark-800 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Badge variant={p.tipo_transacao === 'venda' ? 'primary' : 'accent'}>
              {p.tipo_transacao === 'venda' ? 'Venda' : 'Arrendamento'}
            </Badge>
            {p.tipo && <Badge>{p.tipo}</Badge>}
          </div>
          <h2 className="text-white font-bold text-lg mb-1">{p.titulo}</h2>
          <p className="text-accent-400 font-bold text-xl">
            {p.preco_venda ? formatPrice(p.preco_venda) : formatPrice(p.preco_arrendamento)}
            {p.preco_arrendamento && !p.preco_venda && <span className="text-dark-500 text-sm font-normal">/mes</span>}
          </p>
          <div className="flex items-center gap-2 mt-2 text-dark-400 text-xs">
            <MapPin className="w-3 h-3" />{p.endereco || p.cidade}, {p.provincia}
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold">{p.quartos}</p><p className="text-dark-400 text-xs">Quartos</p>
            </div>
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold">{p.suites ?? 0}</p><p className="text-dark-400 text-xs">Suites</p>
            </div>
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold">{p.banheiros ?? 0}</p><p className="text-dark-400 text-xs">Banheiros</p>
            </div>
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold">{p.vagas_garagem ?? 0}</p><p className="text-dark-400 text-xs">Garagem</p>
            </div>
          </div>

          {p.area_util && (
            <div className="flex items-center gap-2 mt-3 text-dark-300 text-sm">
              <Maximize className="w-4 h-4" />Area util: {p.area_util}m2
              {p.area_total && <span className="text-dark-500">| Total: {p.area_total}m2</span>}
            </div>
          )}

          {p.descricao && <p className="text-dark-400 text-sm leading-relaxed mt-4">{p.descricao}</p>}

          {p.caracteristicas && p.caracteristicas.length > 0 && (
            <div className="mt-4">
              <h4 className="text-white text-sm font-semibold mb-2">Caracteristicas</h4>
              <div className="flex flex-wrap gap-1.5">
                {p.caracteristicas.map((c, i) => <Badge key={i} variant="success">{c}</Badge>)}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
