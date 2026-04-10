import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/module_service.dart';
import '../../services/cart_service.dart';
import '../../modules/common/checkout_screen.dart';
import '../../widgets/common.dart';

class MarketplaceScreen extends StatefulWidget {
  const MarketplaceScreen({super.key});
  @override
  State<MarketplaceScreen> createState() => _MarketplaceScreenState();
}

class _MarketplaceScreenState extends State<MarketplaceScreen> {
  final _svc = ModuleService();
  List<dynamic> _products = [];
  bool _loading = true;
  String _search = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      _products = await _svc.listProducts();
    } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  List<dynamic> get _filtered => _products.where((p) =>
      (p['nome'] ?? '').toString().toLowerCase().contains(_search.toLowerCase())).toList();

  String _price(dynamic v) => v != null ? '${num.tryParse(v.toString())?.toStringAsFixed(0) ?? v} Kz' : '';

  @override
  Widget build(BuildContext context) {
    final cart = context.watch<CartProvider>();
    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(
        title: const Text('Marketplace'),
        backgroundColor: AppTheme.dark800,
        actions: [
          if (!cart.isEmpty)
            _CartBadge(
              count: cart.count,
              onTap: () => Navigator.push(context, MaterialPageRoute(
                builder: (_) => const CheckoutScreen(titulo: 'Checkout Marketplace'),
              )),
            ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: _SearchBox(hint: 'Procurar produtos...', onChanged: (v) => setState(() => _search = v)),
          ),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator(color: AppTheme.accent))
                : _filtered.isEmpty
                    ? const EmptyState(icon: Icons.shopping_bag, title: 'Sem produtos', subtitle: 'Nenhum produto disponivel')
                    : RefreshIndicator(
                        onRefresh: _load,
                        child: GridView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 2, mainAxisSpacing: 10, crossAxisSpacing: 10, childAspectRatio: 0.75,
                          ),
                          itemCount: _filtered.length,
                          itemBuilder: (ctx, i) {
                            final p = _filtered[i];
                            return GestureDetector(
                              onTap: () => _openDetail(p),
                              child: Container(
                                decoration: BoxDecoration(
                                  color: AppTheme.dark800,
                                  borderRadius: BorderRadius.circular(14),
                                  border: Border.all(color: AppTheme.dark700),
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Container(
                                      height: 100,
                                      decoration: BoxDecoration(
                                        color: AppTheme.accent.withOpacity(0.08),
                                        borderRadius: const BorderRadius.vertical(top: Radius.circular(14)),
                                      ),
                                      child: const Center(child: Icon(Icons.shopping_bag, color: AppTheme.accent, size: 32)),
                                    ),
                                    Padding(
                                      padding: const EdgeInsets.all(10),
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(p['nome'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 13), maxLines: 2, overflow: TextOverflow.ellipsis),
                                          const SizedBox(height: 4),
                                          Text(_price(p['preco'] ?? p['preco_atual']), style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 15)),
                                          if (p['em_promocao'] == true && p['preco_promocional'] != null)
                                            Text(_price(p['preco']), style: const TextStyle(color: AppTheme.dark500, fontSize: 11, decoration: TextDecoration.lineThrough)),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  void _openDetail(Map<String, dynamic> p) {
    Navigator.push(context, MaterialPageRoute(builder: (_) => _ProductDetailScreen(product: p)));
  }
}

class _ProductDetailScreen extends StatelessWidget {
  final Map<String, dynamic> product;
  const _ProductDetailScreen({required this.product});

  @override
  Widget build(BuildContext context) {
    final cart = context.read<CartProvider>();
    final price = (product['preco_atual'] ?? product['preco'] ?? 0).toDouble();

    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(title: Text(product['nome'] ?? 'Produto'), backgroundColor: AppTheme.dark800),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              height: 200,
              width: double.infinity,
              decoration: BoxDecoration(
                color: AppTheme.accent.withOpacity(0.08),
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Center(child: Icon(Icons.shopping_bag, color: AppTheme.accent, size: 64)),
            ),
            const SizedBox(height: 16),
            Text(product['nome'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20)),
            const SizedBox(height: 8),
            Text('${price.toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 24)),
            if (product['descricao'] != null) ...[
              const SizedBox(height: 12),
              Text(product['descricao'], style: const TextStyle(color: AppTheme.dark300, fontSize: 14)),
            ],
            const SizedBox(height: 8),
            if (product['stock'] != null)
              Text('Stock: ${product['stock']}', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
            const SizedBox(height: 20),
            PrimaryButton(
              label: 'Adicionar ao Carrinho',
              icon: Icons.add_shopping_cart,
              onPressed: () {
                cart.addItem(
                  CartItem(
                    id: product['id'].toString(),
                    name: product['nome'] ?? 'Produto',
                    price: price,
                    type: CartItemType.produto,
                    meta: {'seller_id': product['seller_id']?.toString()},
                  ),
                  contextId: product['seller_id']?.toString(),
                );
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('${product['nome']} adicionado ao carrinho'),
                    backgroundColor: AppTheme.success,
                    action: SnackBarAction(
                      label: 'Checkout',
                      textColor: Colors.white,
                      onPressed: () => Navigator.push(context, MaterialPageRoute(
                        builder: (_) => const CheckoutScreen(titulo: 'Checkout Marketplace'),
                      )),
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _CartBadge extends StatelessWidget {
  final int count;
  final VoidCallback onTap;
  const _CartBadge({required this.count, required this.onTap});
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(right: 12),
    child: GestureDetector(
      onTap: onTap,
      child: Stack(clipBehavior: Clip.none, children: [
        const Icon(Icons.shopping_cart, color: Colors.white, size: 26),
        Positioned(
          right: -6, top: -4,
          child: Container(
            padding: const EdgeInsets.all(4),
            decoration: const BoxDecoration(color: AppTheme.primary, shape: BoxShape.circle),
            child: Text('$count', style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
          ),
        ),
      ]),
    ),
  );
}

class _SearchBox extends StatelessWidget {
  final String hint;
  final ValueChanged<String> onChanged;
  const _SearchBox({required this.hint, required this.onChanged});
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 14),
    decoration: BoxDecoration(color: AppTheme.dark800, borderRadius: BorderRadius.circular(12), border: Border.all(color: AppTheme.dark700)),
    child: Row(children: [
      const Icon(Icons.search, color: AppTheme.dark500, size: 20),
      const SizedBox(width: 10),
      Expanded(child: TextField(
        onChanged: onChanged,
        style: const TextStyle(color: Colors.white, fontSize: 14),
        decoration: InputDecoration(border: InputBorder.none, hintText: hint, hintStyle: const TextStyle(color: AppTheme.dark500)),
      )),
    ]),
  );
}
