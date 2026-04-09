import React, { useEffect, useState } from 'react';
import { Home, Search, MapPin, Users, Star, Bed } from 'lucide-react';
import { api } from '../api';
import { PageHeader, EmptyState, LoadingState, ItemCard, Badge } from '../components/Layout';

export default function Alojamento() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    api.listProperties()
      .then(data => setProperties(Array.isArray(data) ? data : []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = properties.filter(p =>
    (p.titulo || '').toLowerCase().includes(search.toLowerCase()) ||
    (p.cidade || '').toLowerCase().includes(search.toLowerCase())
  );

  const formatPrice = (v) => v ? `${Number(v).toLocaleString('pt-AO')} Kz` : '';

  if (selected) {
    return <PropertyDetail property={selected} onBack={() => setSelected(null)} formatPrice={formatPrice} />;
  }

  return (
    <div data-testid="alojamento-page">
      <PageHeader title="Alojamento" subtitle={`${properties.length} propriedades`} />
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-fade-in">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
          <input
            data-testid="alojamento-search"
            type="text"
            placeholder="Procurar por cidade ou titulo..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-dark-900 border border-dark-800 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition"
          />
        </div>

        {loading && <LoadingState />}
        {error && <p className="text-red-400 text-sm" data-testid="alojamento-error">{error}</p>}
        {!loading && !error && filtered.length === 0 && (
          <EmptyState icon={Home} title="Nenhuma propriedade" description="As propriedades aparecerao aqui quando disponiveis." />
        )}

        <div className="grid gap-3 sm:grid-cols-2">
          {filtered.map((p, i) => (
            <ItemCard key={p.id || i} onClick={() => setSelected(p)} testId={`property-item-${i}`}>
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-white font-semibold text-sm flex-1">{p.titulo}</h3>
                <span className="text-accent-400 font-bold text-sm ml-2">{formatPrice(p.preco_noite)}/noite</span>
              </div>
              <div className="flex items-center gap-3 text-xs text-dark-400">
                <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{p.cidade || 'N/A'}</span>
                <span className="flex items-center gap-1"><Bed className="w-3 h-3" />{p.quartos ?? 0} quartos</span>
                <span className="flex items-center gap-1"><Users className="w-3 h-3" />{p.max_hospedes ?? 0} hospedes</span>
              </div>
              {p.tipo && <Badge variant="accent">{p.tipo}</Badge>}
              {p.rating_medio > 0 && (
                <div className="flex items-center gap-1 mt-2 text-xs text-accent-400">
                  <Star className="w-3 h-3 fill-accent-400" />{p.rating_medio}
                </div>
              )}
            </ItemCard>
          ))}
        </div>
      </div>
    </div>
  );
}

function PropertyDetail({ property, onBack, formatPrice }) {
  return (
    <div data-testid="property-detail">
      <PageHeader title={property.titulo || 'Propriedade'} onBack={onBack} />
      <div className="max-w-4xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-slide-up">
        <div className="bg-dark-900 border border-dark-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white font-bold text-lg">{property.titulo}</h2>
            <span className="text-accent-400 font-bold text-lg">{formatPrice(property.preco_noite)}<span className="text-dark-500 text-xs font-normal">/noite</span></span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold text-lg">{property.quartos ?? 0}</p>
              <p className="text-dark-400 text-xs">Quartos</p>
            </div>
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold text-lg">{property.camas ?? 0}</p>
              <p className="text-dark-400 text-xs">Camas</p>
            </div>
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold text-lg">{property.banheiros ?? 0}</p>
              <p className="text-dark-400 text-xs">Banheiros</p>
            </div>
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold text-lg">{property.max_hospedes ?? 0}</p>
              <p className="text-dark-400 text-xs">Hospedes</p>
            </div>
          </div>
          {property.descricao && <p className="text-dark-400 text-sm leading-relaxed">{property.descricao}</p>}
          <div className="flex items-center gap-2 mt-3 text-dark-400 text-xs">
            <MapPin className="w-3 h-3" />{property.endereco || property.cidade}, {property.provincia}
          </div>
          {property.comodidades && property.comodidades.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {property.comodidades.map((c, i) => <Badge key={i}>{c}</Badge>)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
