import React, { useEffect, useState } from 'react';
import { MapPin, Search, Clock, Users, Star, Globe } from 'lucide-react';
import { api } from '../api';
import { PageHeader, EmptyState, LoadingState, ItemCard, Badge } from '../components/Layout';

export default function Turismo() {
  const [experiences, setExperiences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    api.listExperiences()
      .then(data => setExperiences(Array.isArray(data) ? data : []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = experiences.filter(e =>
    (e.titulo || '').toLowerCase().includes(search.toLowerCase()) ||
    (e.cidade || '').toLowerCase().includes(search.toLowerCase())
  );

  const formatPrice = (v) => v ? `${Number(v).toLocaleString('pt-AO')} Kz` : '';

  if (selected) {
    return <ExperienceDetail experience={selected} onBack={() => setSelected(null)} formatPrice={formatPrice} />;
  }

  return (
    <div data-testid="turismo-page">
      <PageHeader title="Turismo" subtitle={`${experiences.length} experiencias`} />
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-fade-in">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
          <input
            data-testid="turismo-search"
            type="text"
            placeholder="Procurar experiencias..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-dark-900 border border-dark-800 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition"
          />
        </div>

        {loading && <LoadingState />}
        {error && <p className="text-red-400 text-sm" data-testid="turismo-error">{error}</p>}
        {!loading && !error && filtered.length === 0 && (
          <EmptyState icon={MapPin} title="Nenhuma experiencia" description="As experiencias de turismo aparecerao aqui." />
        )}

        <div className="grid gap-3 sm:grid-cols-2">
          {filtered.map((e, i) => (
            <ItemCard key={e.id || i} onClick={() => setSelected(e)} testId={`experience-item-${i}`}>
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-white font-semibold text-sm flex-1">{e.titulo}</h3>
                <span className="text-accent-400 font-bold text-sm ml-2">{formatPrice(e.preco)}</span>
              </div>
              <div className="flex items-center gap-3 text-xs text-dark-400 mb-2">
                <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{e.cidade || 'N/A'}</span>
                <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{e.duracao_horas || 0}h</span>
                <span className="flex items-center gap-1"><Users className="w-3 h-3" />Max {e.max_participantes || 0}</span>
              </div>
              {e.tipo && <Badge variant="accent">{e.tipo}</Badge>}
              {e.rating_medio > 0 && (
                <div className="flex items-center gap-1 mt-1 text-xs text-accent-400">
                  <Star className="w-3 h-3 fill-accent-400" />{e.rating_medio}
                </div>
              )}
            </ItemCard>
          ))}
        </div>
      </div>
    </div>
  );
}

function ExperienceDetail({ experience, onBack, formatPrice }) {
  const e = experience;
  return (
    <div data-testid="experience-detail">
      <PageHeader title={e.titulo || 'Experiencia'} onBack={onBack} />
      <div className="max-w-4xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-slide-up">
        <div className="bg-dark-900 border border-dark-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white font-bold text-lg">{e.titulo}</h2>
            <span className="text-accent-400 font-bold text-lg">{formatPrice(e.preco)}<span className="text-dark-500 text-xs font-normal">/pessoa</span></span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold">{e.duracao_horas || 0}h</p>
              <p className="text-dark-400 text-xs">Duracao</p>
            </div>
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold">{e.max_participantes || 0}</p>
              <p className="text-dark-400 text-xs">Max. pessoas</p>
            </div>
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold">{e.tipo || 'Tour'}</p>
              <p className="text-dark-400 text-xs">Tipo</p>
            </div>
          </div>
          {e.descricao && <p className="text-dark-400 text-sm leading-relaxed">{e.descricao}</p>}
          <div className="flex items-center gap-2 mt-3 text-dark-400 text-xs">
            <MapPin className="w-3 h-3" />{e.local}, {e.cidade}
          </div>
          {e.ponto_encontro && (
            <p className="text-dark-500 text-xs mt-1">Ponto de encontro: {e.ponto_encontro}</p>
          )}
          {e.idiomas && e.idiomas.length > 0 && (
            <div className="flex items-center gap-2 mt-3">
              <Globe className="w-3 h-3 text-dark-500" />
              <div className="flex gap-1">{e.idiomas.map((l,i) => <Badge key={i}>{l}</Badge>)}</div>
            </div>
          )}
          {e.inclui && e.inclui.length > 0 && (
            <div className="mt-4">
              <h4 className="text-white text-sm font-semibold mb-1">Inclui</h4>
              <div className="flex flex-wrap gap-1.5">
                {e.inclui.map((item,i) => <Badge key={i} variant="success">{item}</Badge>)}
              </div>
            </div>
          )}
          {e.nao_inclui && e.nao_inclui.length > 0 && (
            <div className="mt-3">
              <h4 className="text-white text-sm font-semibold mb-1">Nao inclui</h4>
              <div className="flex flex-wrap gap-1.5">
                {e.nao_inclui.map((item,i) => <Badge key={i} variant="danger">{item}</Badge>)}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
