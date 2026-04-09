import React, { useEffect, useState } from 'react';
import { ShoppingBag, Search, Package, Plus } from 'lucide-react';
import { api } from '../api';
import { PageHeader, EmptyState, LoadingState, ItemCard, Badge } from '../components/Layout';
import FormModal, { FormField, FormInput, FormTextarea, SubmitButton } from '../components/FormModal';

export default function Marketplace() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState(null);
  const [showCreate, setShowCreate] = useState(false);

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      api.listProducts().catch(() => []),
      api.listCategories().catch(() => []),
    ]).then(([prods, cats]) => {
      setProducts(Array.isArray(prods) ? prods : []);
      setCategories(Array.isArray(cats) ? cats : []);
    }).catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const filtered = products.filter(p =>
    (p.nome || '').toLowerCase().includes(search.toLowerCase())
  );

  const formatPrice = (v) => v ? `${Number(v).toLocaleString('pt-AO')} Kz` : '';

  if (selected) {
    return <ProductDetail product={selected} onBack={() => setSelected(null)} formatPrice={formatPrice} />;
  }

  return (
    <div data-testid="marketplace-page">
      <PageHeader title="Marketplace" subtitle={`${products.length} produtos`}
        actions={
          <button onClick={() => setShowCreate(true)} className="flex items-center gap-1.5 px-3 py-1.5 bg-primary-600 hover:bg-primary-700 text-white text-sm rounded-lg transition" data-testid="create-product-btn">
            <Plus className="w-4 h-4" /> Vender
          </button>
        }
      />
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-fade-in">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
          <input
            data-testid="marketplace-search"
            type="text"
            placeholder="Procurar produtos..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-dark-900 border border-dark-800 rounded-lg text-white text-sm placeholder-dark-500 focus:outline-none focus:border-primary-500 transition"
          />
        </div>

        {categories.length > 0 && (
          <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1">
            {categories.map((c, i) => (
              <button key={c.id || i} data-testid={`category-${i}`} className="flex-shrink-0 px-3 py-1.5 bg-dark-800 hover:bg-dark-700 border border-dark-700 rounded-full text-dark-300 text-xs transition">
                {c.nome}
              </button>
            ))}
          </div>
        )}

        {loading && <LoadingState />}
        {error && <p className="text-red-400 text-sm" data-testid="marketplace-error">{error}</p>}
        {!loading && !error && filtered.length === 0 && (
          <EmptyState icon={ShoppingBag} title="Nenhum produto" description="Os produtos aparecerao aqui quando disponiveis." />
        )}

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((p, i) => (
            <ItemCard key={p.id || i} onClick={() => setSelected(p)} testId={`product-item-${i}`}>
              <div className="flex items-start gap-3">
                <div className="w-14 h-14 rounded-lg bg-dark-800 flex items-center justify-center flex-shrink-0">
                  <Package className="w-6 h-6 text-dark-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-white font-semibold text-sm truncate">{p.nome}</h3>
                  <p className="text-accent-400 font-bold text-sm mt-0.5">
                    {formatPrice(p.preco_atual || p.preco)}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    {p.em_promocao && <Badge variant="danger">Promo</Badge>}
                    {p.stock > 0 && <Badge variant="success">Em stock</Badge>}
                    {p.stock === 0 && <Badge variant="warning">Esgotado</Badge>}
                  </div>
                </div>
              </div>
            </ItemCard>
          ))}
        </div>
      </div>
      {showCreate && <CreateProductForm onClose={() => setShowCreate(false)} onCreated={() => { setShowCreate(false); fetchData(); }} />}
    </div>
  );
}

function CreateProductForm({ onClose, onCreated }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    const fd = new FormData(e.target);
    try {
      await api.createProduct({
        nome: fd.get('nome'),
        descricao: fd.get('descricao') || null,
        preco: parseFloat(fd.get('preco')),
        stock: parseInt(fd.get('stock')) || 0,
      });
      onCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <FormModal title="Publicar Produto" onClose={onClose}>
      <form onSubmit={handleSubmit} data-testid="create-product-form">
        <FormField label="Nome do produto *">
          <FormInput name="nome" placeholder="Nome do produto" required />
        </FormField>
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Preco (Kz) *">
            <FormInput name="preco" type="number" placeholder="5000" required />
          </FormField>
          <FormField label="Stock *">
            <FormInput name="stock" type="number" placeholder="10" required />
          </FormField>
        </div>
        <FormField label="Descricao">
          <FormTextarea name="descricao" placeholder="Descreva o produto..." />
        </FormField>
        {error && <p className="text-red-400 text-sm mb-3" data-testid="form-error">{error}</p>}
        <SubmitButton loading={loading}>Publicar Produto</SubmitButton>
      </form>
    </FormModal>
  );
}

function ProductDetail({ product, onBack, formatPrice }) {
  return (
    <div data-testid="product-detail">
      <PageHeader title={product.nome || 'Produto'} onBack={onBack} />
      <div className="max-w-4xl mx-auto px-4 md:px-6 py-6 space-y-4 animate-slide-up">
        <div className="bg-dark-900 border border-dark-800 rounded-xl p-5">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-20 h-20 rounded-xl bg-dark-800 flex items-center justify-center">
              <Package className="w-10 h-10 text-dark-500" />
            </div>
            <div>
              <h2 className="text-white font-bold text-lg">{product.nome}</h2>
              <p className="text-accent-400 font-bold text-xl">{formatPrice(product.preco_atual || product.preco)}</p>
              {product.preco_promocional && (
                <p className="text-dark-500 text-sm line-through">{formatPrice(product.preco)}</p>
              )}
            </div>
          </div>
          {product.descricao && <p className="text-dark-400 text-sm leading-relaxed">{product.descricao}</p>}
          <div className="flex items-center gap-4 mt-4 text-xs text-dark-400">
            <span>Stock: {product.stock ?? 'N/A'}</span>
            <span>Visualizacoes: {product.visualizacoes ?? 0}</span>
            <span>Vendas: {product.vendas ?? 0}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
