import React, { useEffect, useState } from 'react';
import { Package, MapPin, Truck, Clock, ArrowRight, Calculator } from 'lucide-react';
import { api } from '../api';
import { PageHeader, EmptyState, LoadingState, ItemCard, Badge } from '../components/Layout';

const statusColors = {
  pendente: 'warning',
  aceite: 'accent',
  em_recolha: 'primary',
  recolhido: 'primary',
  em_transito: 'accent',
  entregue: 'success',
  cancelado: 'danger',
};

export default function Entregas() {
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tab, setTab] = useState('lista');
  const [estimate, setEstimate] = useState(null);
  const [estimating, setEstimating] = useState(false);

  useEffect(() => {
    api.listMyDeliveries()
      .then(data => setDeliveries(Array.isArray(data) ? data : []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const formatPrice = (v) => v ? `${Number(v).toLocaleString('pt-AO')} Kz` : '';

  const handleEstimate = async (e) => {
    e.preventDefault();
    setEstimating(true);
    setEstimate(null);
    const fd = new FormData(e.target);
    try {
      const result = await api.estimateDelivery({
        origem_latitude: parseFloat(fd.get('olat')),
        origem_longitude: parseFloat(fd.get('olng')),
        destino_latitude: parseFloat(fd.get('dlat')),
        destino_longitude: parseFloat(fd.get('dlng')),
        tipo: 'pacote_pequeno',
        prioridade: 'normal',
      });
      setEstimate(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setEstimating(false);
    }
  };

  return (
    <div data-testid="entregas-page">
      <PageHeader title="Entregas" subtitle="Envie pacotes por toda Angola" />
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-fade-in">
        {/* Tabs */}
        <div className="flex gap-1 bg-dark-900 p-1 rounded-lg border border-dark-800 w-fit">
          <button
            onClick={() => setTab('lista')}
            data-testid="tab-entregas-lista"
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition ${tab === 'lista' ? 'bg-primary-600 text-white' : 'text-dark-400 hover:text-white'}`}
          >Minhas entregas</button>
          <button
            onClick={() => setTab('estimar')}
            data-testid="tab-entregas-estimar"
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition ${tab === 'estimar' ? 'bg-primary-600 text-white' : 'text-dark-400 hover:text-white'}`}
          >Estimar preco</button>
        </div>

        {tab === 'lista' && (
          <>
            {loading && <LoadingState />}
            {error && <p className="text-red-400 text-sm">{error}</p>}
            {!loading && !error && deliveries.length === 0 && (
              <EmptyState icon={Package} title="Nenhuma entrega" description="As suas entregas aparecerao aqui." />
            )}
            <div className="space-y-3">
              {deliveries.map((d, i) => (
                <ItemCard key={d.id || i} testId={`delivery-item-${i}`}>
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant={statusColors[d.status] || 'default'}>{d.status}</Badge>
                    <span className="text-accent-400 font-bold text-sm">{formatPrice(d.total)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <div className="flex-1">
                      <p className="text-dark-300 text-xs flex items-center gap-1"><MapPin className="w-3 h-3 text-green-400" />{d.origem_endereco}</p>
                      <p className="text-dark-300 text-xs flex items-center gap-1 mt-1"><MapPin className="w-3 h-3 text-primary-400" />{d.destino_endereco}</p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-dark-500" />
                  </div>
                  <div className="flex items-center gap-3 text-xs text-dark-500 mt-2">
                    <span>{d.tipo}</span>
                    <span>{d.prioridade}</span>
                    {d.distancia_km && <span>{d.distancia_km} km</span>}
                  </div>
                </ItemCard>
              ))}
            </div>
          </>
        )}

        {tab === 'estimar' && (
          <div className="bg-dark-900 border border-dark-800 rounded-xl p-5">
            <h3 className="text-white font-semibold text-sm mb-4 flex items-center gap-2">
              <Calculator className="w-4 h-4 text-accent-400" /> Estimar custo de entrega
            </h3>
            <form onSubmit={handleEstimate} className="space-y-4">
              <div>
                <label className="text-dark-300 text-xs block mb-1">Origem (Latitude, Longitude)</label>
                <div className="grid grid-cols-2 gap-2">
                  <input name="olat" defaultValue="-8.839" className="px-3 py-2 bg-dark-800 border border-dark-700 rounded-lg text-white text-sm focus:outline-none focus:border-primary-500" data-testid="estimate-olat" />
                  <input name="olng" defaultValue="13.289" className="px-3 py-2 bg-dark-800 border border-dark-700 rounded-lg text-white text-sm focus:outline-none focus:border-primary-500" data-testid="estimate-olng" />
                </div>
              </div>
              <div>
                <label className="text-dark-300 text-xs block mb-1">Destino (Latitude, Longitude)</label>
                <div className="grid grid-cols-2 gap-2">
                  <input name="dlat" defaultValue="-8.913" className="px-3 py-2 bg-dark-800 border border-dark-700 rounded-lg text-white text-sm focus:outline-none focus:border-primary-500" data-testid="estimate-dlat" />
                  <input name="dlng" defaultValue="13.202" className="px-3 py-2 bg-dark-800 border border-dark-700 rounded-lg text-white text-sm focus:outline-none focus:border-primary-500" data-testid="estimate-dlng" />
                </div>
              </div>
              <button
                type="submit"
                disabled={estimating}
                data-testid="estimate-submit-btn"
                className="w-full py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg text-sm transition disabled:opacity-50"
              >
                {estimating ? 'A calcular...' : 'Calcular estimativa'}
              </button>
            </form>

            {estimate && (
              <div className="mt-4 p-4 bg-dark-800 rounded-lg border border-dark-700 animate-slide-up" data-testid="estimate-result">
                <h4 className="text-white font-semibold text-sm mb-2">Estimativa</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <span className="text-dark-400">Distancia</span><span className="text-white text-right">{estimate.distancia_km} km</span>
                  <span className="text-dark-400">Duracao</span><span className="text-white text-right">{estimate.duracao_estimada_min} min</span>
                  <span className="text-dark-400">Preco base</span><span className="text-white text-right">{formatPrice(estimate.preco_base)}</span>
                  <span className="text-dark-400">Taxa prioridade</span><span className="text-white text-right">{formatPrice(estimate.taxa_prioridade)}</span>
                  <span className="text-dark-400">Taxa peso</span><span className="text-white text-right">{formatPrice(estimate.taxa_peso)}</span>
                  <div className="col-span-2 border-t border-dark-600 pt-2 mt-1 flex justify-between">
                    <span className="text-white font-bold">Total</span>
                    <span className="text-accent-400 font-bold">{formatPrice(estimate.total)}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
