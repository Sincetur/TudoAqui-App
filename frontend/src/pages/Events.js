import React, { useEffect, useState } from 'react';
import { Calendar, MapPin, Clock, Tag, Search, Plus } from 'lucide-react';
import { api } from '../api';
import { PageHeader, EmptyState, LoadingState, ItemCard, Badge } from '../components/Layout';
import FormModal, { FormField, FormInput, FormTextarea, FormSelect, SubmitButton } from '../components/FormModal';
import CheckoutModal from '../components/CheckoutModal';

export default function Events() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState(null);
  const [showCreate, setShowCreate] = useState(false);

  const fetchEvents = () => {
    setLoading(true);
    api.listEvents()
      .then(data => setEvents(Array.isArray(data) ? data : []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchEvents(); }, []);

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
        actions={
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-1.5 px-3 py-1.5 bg-primary-600 hover:bg-primary-700 text-white text-sm rounded-lg transition" data-testid="create-event-btn">
            <Plus className="w-4 h-4" /> Criar
          </button>
        }
      />
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-fade-in">
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

      {showCreate && <CreateEventForm onClose={() => setShowCreate(false)} onCreated={() => { setShowCreate(false); fetchEvents(); }} />}
    </div>
  );
}

function CreateEventForm({ onClose, onCreated }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    const fd = new FormData(e.target);
    try {
      await api.createEvent({
        titulo: fd.get('titulo'),
        descricao: fd.get('descricao') || null,
        local: fd.get('local'),
        data_evento: fd.get('data_evento'),
        hora_evento: fd.get('hora_evento') + ':00',
        categoria: fd.get('categoria') || null,
      });
      onCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <FormModal title="Criar Evento" onClose={onClose}>
      <form onSubmit={handleSubmit} data-testid="create-event-form">
        <FormField label="Titulo *">
          <FormInput name="titulo" placeholder="Nome do evento" required />
        </FormField>
        <FormField label="Local *">
          <FormInput name="local" placeholder="Local do evento" required />
        </FormField>
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Data *">
            <FormInput name="data_evento" type="date" required />
          </FormField>
          <FormField label="Hora *">
            <FormInput name="hora_evento" type="time" required />
          </FormField>
        </div>
        <FormField label="Categoria">
          <FormSelect name="categoria" placeholder="Selecionar..." options={[
            { value: 'Musica', label: 'Musica' },
            { value: 'Tecnologia', label: 'Tecnologia' },
            { value: 'Desporto', label: 'Desporto' },
            { value: 'Cultura', label: 'Cultura' },
            { value: 'Entretenimento', label: 'Entretenimento' },
            { value: 'Gastronomia', label: 'Gastronomia' },
          ]} />
        </FormField>
        <FormField label="Descricao">
          <FormTextarea name="descricao" placeholder="Descricao do evento..." rows={3} />
        </FormField>
        {error && <p className="text-red-400 text-sm mb-3" data-testid="form-error">{error}</p>}
        <SubmitButton loading={loading}>Criar Evento</SubmitButton>
      </form>
    </FormModal>
  );
}

function EventDetail({ event, onBack }) {
  const [selectedTicket, setSelectedTicket] = useState(null);

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
            <Badge variant={event.status === 'ativo' ? 'success' : 'warning'}>{event.status}</Badge>
          </div>
        )}
        {event.ticket_types && event.ticket_types.length > 0 && (
          <div className="bg-dark-900 border border-dark-800 rounded-xl p-5">
            <h3 className="text-white font-semibold text-sm mb-3">Bilhetes</h3>
            <div className="space-y-2">
              {event.ticket_types.map((tt, i) => (
                <div key={tt.id || i} className="flex items-center justify-between py-2 px-3 bg-dark-800 rounded-lg" data-testid={`ticket-type-${i}`}>
                  <div>
                    <p className="text-white text-sm font-medium">{tt.nome}</p>
                    <p className="text-dark-500 text-xs">{tt.quantidade_disponivel || 0} disponiveis</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-accent-400 font-bold text-sm">{Number(tt.preco).toLocaleString('pt-AO')} Kz</span>
                    <button
                      onClick={() => setSelectedTicket(tt)}
                      className="px-3 py-1 bg-primary-600 hover:bg-primary-700 text-white text-xs font-medium rounded-lg transition"
                      data-testid={`buy-ticket-${i}`}
                    >
                      Comprar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {selectedTicket && (
        <CheckoutModal
          origem_tipo="ticket"
          origem_id={event.id}
          valor={selectedTicket.preco}
          descricao={`${event.titulo} - ${selectedTicket.nome}`}
          onClose={() => setSelectedTicket(null)}
          onSuccess={() => setSelectedTicket(null)}
        />
      )}
    </div>
  );
}
