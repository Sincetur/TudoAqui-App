import React, { useEffect, useState } from 'react';
import { Calendar, MapPin, Clock, Tag, Search } from 'lucide-react';
import { api } from '../api';
import { PageHeader, EmptyState, LoadingState, ItemCard, Badge } from '../components/Layout';

export default function Events() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    api.listEvents()
      .then(data => setEvents(Array.isArray(data) ? data : []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = events.filter(e =>
    (e.titulo || '').toLowerCase().includes(search.toLowerCase()) ||
    (e.local || '').toLowerCase().includes(search.toLowerCase())
  );

  if (selected) {
    return <EventDetail event={selected} onBack={() => setSelected(null)} />;
  }

  return (
    <div data-testid="events-page">
      <PageHeader
        title="Eventos"
        subtitle={`${events.length} eventos disponiveis`}
      />
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-fade-in">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
          <input
            data-testid="events-search"
            type="text"
            placeholder="Procurar eventos..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-dark-900 border border-dark-800 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition"
          />
        </div>

        {loading && <LoadingState />}
        {error && <p className="text-red-400 text-sm" data-testid="events-error">{error}</p>}
        {!loading && !error && filtered.length === 0 && (
          <EmptyState icon={Calendar} title="Nenhum evento" description="Os eventos aparecerao aqui quando disponiveis." />
        )}

        <div className="grid gap-3 sm:grid-cols-2">
          {filtered.map((ev, i) => (
            <ItemCard key={ev.id || i} onClick={() => setSelected(ev)} testId={`event-item-${i}`}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-white font-semibold text-sm mb-1">{ev.titulo || `Evento ${i+1}`}</h3>
                  <div className="flex items-center gap-3 text-dark-400 text-xs">
                    <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{ev.local || 'Luanda'}</span>
                    <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{ev.data_evento || '-'}</span>
                  </div>
                  {ev.categoria && <Badge variant="primary">{ev.categoria}</Badge>}
                </div>
                <div className="w-9 h-9 rounded-lg bg-primary-600/15 flex items-center justify-center flex-shrink-0">
                  <Calendar className="w-4 h-4 text-primary-400" />
                </div>
              </div>
              {ev.descricao && <p className="text-dark-400 text-xs mt-2 line-clamp-2">{ev.descricao}</p>}
            </ItemCard>
          ))}
        </div>
      </div>
    </div>
  );
}

function EventDetail({ event, onBack }) {
  return (
    <div data-testid="event-detail">
      <PageHeader title={event.titulo || 'Evento'} subtitle={event.categoria} onBack={onBack} />
      <div className="max-w-4xl mx-auto px-4 md:px-6 py-6 space-y-6 animate-slide-up">
        <div className="bg-dark-900 border border-dark-800 rounded-xl p-5">
          <h2 className="text-white font-bold text-lg mb-3">{event.titulo}</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2 text-dark-300">
              <MapPin className="w-4 h-4 text-primary-400" />
              <span>{event.local || 'N/A'}</span>
            </div>
            <div className="flex items-center gap-2 text-dark-300">
              <Calendar className="w-4 h-4 text-accent-400" />
              <span>{event.data_evento || 'N/A'}</span>
            </div>
            <div className="flex items-center gap-2 text-dark-300">
              <Clock className="w-4 h-4 text-sky-400" />
              <span>{event.hora_evento || 'N/A'}</span>
            </div>
            {event.categoria && (
              <div className="flex items-center gap-2 text-dark-300">
                <Tag className="w-4 h-4 text-violet-400" />
                <span>{event.categoria}</span>
              </div>
            )}
          </div>
          {event.descricao && (
            <p className="text-dark-400 text-sm mt-4 leading-relaxed">{event.descricao}</p>
          )}
        </div>

        {event.status && (
          <div className="bg-dark-900 border border-dark-800 rounded-xl p-5">
            <h3 className="text-white font-semibold text-sm mb-2">Estado</h3>
            <Badge variant={event.status === 'publicado' ? 'success' : 'warning'}>{event.status}</Badge>
          </div>
        )}
      </div>
    </div>
  );
}
