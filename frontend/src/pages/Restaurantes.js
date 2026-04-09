import React, { useEffect, useState } from 'react';
import { UtensilsCrossed, Search, Star, Clock, MapPin, Truck, ShoppingCart, Plus, Minus } from 'lucide-react';
import { api } from '../api';
import { PageHeader, EmptyState, LoadingState, ItemCard, Badge } from '../components/Layout';

export default function Restaurantes() {
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    api.listRestaurants()
      .then(data => setRestaurants(Array.isArray(data) ? data : []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = restaurants.filter(r =>
    (r.nome || '').toLowerCase().includes(search.toLowerCase())
  );

  const formatPrice = (v) => v ? `${Number(v).toLocaleString('pt-AO')} Kz` : '';

  if (selected) {
    return <RestaurantDetail restaurant={selected} onBack={() => setSelected(null)} formatPrice={formatPrice} />;
  }

  return (
    <div data-testid="restaurantes-page">
      <PageHeader title="Restaurantes" subtitle={`${restaurants.length} restaurantes`} />
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-fade-in">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
          <input
            data-testid="restaurantes-search"
            type="text"
            placeholder="Procurar restaurantes..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-dark-900 border border-dark-800 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition"
          />
        </div>

        {loading && <LoadingState />}
        {error && <p className="text-red-400 text-sm" data-testid="restaurantes-error">{error}</p>}
        {!loading && !error && filtered.length === 0 && (
          <EmptyState icon={UtensilsCrossed} title="Nenhum restaurante" description="Os restaurantes aparecerao aqui quando disponiveis." />
        )}

        <div className="grid gap-3 sm:grid-cols-2">
          {filtered.map((r, i) => (
            <ItemCard key={r.id || i} onClick={() => setSelected(r)} testId={`restaurant-item-${i}`}>
              <div className="flex items-start gap-3">
                <div className="w-14 h-14 rounded-xl bg-dark-800 flex items-center justify-center flex-shrink-0">
                  <UtensilsCrossed className="w-6 h-6 text-dark-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <h3 className="text-white font-semibold text-sm truncate">{r.nome}</h3>
                    {r.aberto ? (
                      <span className="w-2 h-2 rounded-full bg-green-400 flex-shrink-0" />
                    ) : (
                      <span className="w-2 h-2 rounded-full bg-dark-500 flex-shrink-0" />
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-dark-400">
                    {r.rating_medio > 0 && (
                      <span className="flex items-center gap-0.5 text-accent-400"><Star className="w-3 h-3 fill-accent-400" />{r.rating_medio}</span>
                    )}
                    <span className="flex items-center gap-0.5"><Clock className="w-3 h-3" />{r.tempo_preparo_min || 30} min</span>
                    <span className="flex items-center gap-0.5"><Truck className="w-3 h-3" />{formatPrice(r.taxa_entrega)}</span>
                  </div>
                  {r.categorias && r.categorias.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1.5">
                      {r.categorias.slice(0, 3).map((c, ci) => <Badge key={ci}>{c}</Badge>)}
                    </div>
                  )}
                </div>
              </div>
            </ItemCard>
          ))}
        </div>
      </div>
    </div>
  );
}

function RestaurantDetail({ restaurant, onBack, formatPrice }) {
  const [menu, setMenu] = useState([]);
  const [loadingMenu, setLoadingMenu] = useState(true);
  const [cart, setCart] = useState({});
  const r = restaurant;

  useEffect(() => {
    if (r.id) {
      api.getMenu(r.id)
        .then(data => setMenu(Array.isArray(data) ? data : []))
        .catch(() => setMenu([]))
        .finally(() => setLoadingMenu(false));
    } else {
      setLoadingMenu(false);
    }
  }, [r.id]);

  const addToCart = (item) => {
    setCart(prev => ({ ...prev, [item.id]: { ...item, qty: (prev[item.id]?.qty || 0) + 1 } }));
  };

  const removeFromCart = (itemId) => {
    setCart(prev => {
      const c = { ...prev };
      if (c[itemId]?.qty > 1) c[itemId] = { ...c[itemId], qty: c[itemId].qty - 1 };
      else delete c[itemId];
      return c;
    });
  };

  const cartItems = Object.values(cart);
  const cartTotal = cartItems.reduce((t, i) => t + (i.preco_atual || i.preco) * i.qty, 0);
  const cartCount = cartItems.reduce((t, i) => t + i.qty, 0);

  return (
    <div data-testid="restaurant-detail">
      <PageHeader title={r.nome || 'Restaurante'} onBack={onBack} />
      <div className="max-w-4xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-slide-up">
        {/* Info */}
        <div className="bg-dark-900 border border-dark-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-white font-bold text-lg">{r.nome}</h2>
            <Badge variant={r.aberto ? 'success' : 'danger'}>{r.aberto ? 'Aberto' : 'Fechado'}</Badge>
          </div>
          {r.descricao && <p className="text-dark-400 text-sm mb-3">{r.descricao}</p>}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold">{r.tempo_preparo_min || 30} min</p>
              <p className="text-dark-400 text-xs">Preparo</p>
            </div>
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold">{formatPrice(r.taxa_entrega)}</p>
              <p className="text-dark-400 text-xs">Entrega</p>
            </div>
            <div className="bg-dark-800 rounded-lg p-3 text-center">
              <p className="text-white font-bold">{r.rating_medio || 5.0}</p>
              <p className="text-dark-400 text-xs">Rating</p>
            </div>
          </div>
        </div>

        {/* Menu */}
        <div className="bg-dark-900 border border-dark-800 rounded-xl p-5">
          <h3 className="text-white font-semibold text-sm mb-3">Menu</h3>
          {loadingMenu && <LoadingState />}
          {!loadingMenu && menu.length === 0 && (
            <p className="text-dark-500 text-sm">Menu nao disponivel.</p>
          )}
          {menu.map((cat, ci) => (
            <div key={cat.id || ci} className="mb-5 last:mb-0">
              <h4 className="text-dark-300 text-xs font-semibold uppercase tracking-wider mb-2">{cat.nome}</h4>
              <div className="space-y-2">
                {(cat.items || []).map((item, ii) => {
                  const inCart = cart[item.id]?.qty || 0;
                  return (
                    <div key={item.id || ii} className="flex items-center justify-between py-2.5 px-3 bg-dark-800 rounded-lg" data-testid={`menu-item-${ci}-${ii}`}>
                      <div className="flex-1 mr-3">
                        <div className="flex items-center gap-2">
                          <p className="text-white text-sm font-medium">{item.nome}</p>
                          {item.popular && <Badge variant="accent">Popular</Badge>}
                        </div>
                        {item.descricao && <p className="text-dark-500 text-xs mt-0.5">{item.descricao}</p>}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-accent-400 font-bold text-sm">{formatPrice(item.preco_atual || item.preco)}</span>
                        {inCart > 0 ? (
                          <div className="flex items-center gap-1.5 bg-primary-600 rounded-lg px-1">
                            <button onClick={() => removeFromCart(item.id)} className="p-1 text-white hover:bg-primary-700 rounded" data-testid={`cart-minus-${ci}-${ii}`}>
                              <Minus className="w-3 h-3" />
                            </button>
                            <span className="text-white text-xs font-bold min-w-[16px] text-center">{inCart}</span>
                            <button onClick={() => addToCart(item)} className="p-1 text-white hover:bg-primary-700 rounded" data-testid={`cart-plus-${ci}-${ii}`}>
                              <Plus className="w-3 h-3" />
                            </button>
                          </div>
                        ) : (
                          <button onClick={() => addToCart(item)} className="p-1.5 bg-dark-700 hover:bg-primary-600 rounded-lg transition" data-testid={`add-to-cart-${ci}-${ii}`}>
                            <Plus className="w-3.5 h-3.5 text-white" />
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Cart summary */}
        {cartCount > 0 && (
          <div className="sticky bottom-20 md:bottom-4 bg-primary-600 rounded-xl p-4 flex items-center justify-between shadow-xl shadow-primary-600/20 animate-slide-up" data-testid="cart-summary">
            <div>
              <p className="text-white font-semibold text-sm flex items-center gap-2">
                <ShoppingCart className="w-4 h-4" /> {cartCount} {cartCount === 1 ? 'item' : 'itens'}
              </p>
              <p className="text-white/70 text-xs">{r.nome}</p>
            </div>
            <div className="text-right">
              <p className="text-white font-bold">{formatPrice(cartTotal)}</p>
              <p className="text-white/70 text-xs">+ {formatPrice(r.taxa_entrega)} entrega</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
