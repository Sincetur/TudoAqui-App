import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/module_service.dart';
import '../../services/cart_service.dart';
import '../../modules/common/checkout_screen.dart';
import '../../widgets/common.dart';

class RestaurantesScreen extends StatefulWidget {
  const RestaurantesScreen({super.key});
  @override
  State<RestaurantesScreen> createState() => _RestaurantesScreenState();
}

class _RestaurantesScreenState extends State<RestaurantesScreen> {
  final _svc = ModuleService();
  List<dynamic> _restaurants = [];
  bool _loading = true;
  String _search = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try { _restaurants = await _svc.listRestaurants(); } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  List<dynamic> get _filtered => _restaurants.where((r) =>
      (r['nome'] ?? '').toString().toLowerCase().contains(_search.toLowerCase())).toList();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(title: const Text('Restaurantes'), backgroundColor: AppTheme.dark800),
      body: Column(children: [
        _Search(hint: 'Procurar restaurantes...', onChanged: (v) => setState(() => _search = v)),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(color: Colors.red))
              : _filtered.isEmpty
                  ? const EmptyState(icon: Icons.restaurant, title: 'Sem restaurantes', subtitle: 'Nenhum restaurante disponivel')
                  : RefreshIndicator(onRefresh: _load, child: ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: _filtered.length,
                      itemBuilder: (ctx, i) => _RestCard(rest: _filtered[i], onTap: () => _openMenu(_filtered[i])),
                    )),
        ),
      ]),
    );
  }

  void _openMenu(Map<String, dynamic> rest) {
    Navigator.push(context, MaterialPageRoute(builder: (_) => _RestMenuScreen(rest: rest, svc: _svc)));
  }
}

class _RestCard extends StatelessWidget {
  final Map<String, dynamic> rest;
  final VoidCallback onTap;
  const _RestCard({required this.rest, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TCard(onTap: onTap, child: Row(children: [
        Container(
          width: 48, height: 48,
          decoration: BoxDecoration(color: Colors.red.withOpacity(0.12), borderRadius: BorderRadius.circular(12)),
          child: const Icon(Icons.restaurant, color: Colors.red),
        ),
        const SizedBox(width: 12),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(rest['nome'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
          Row(children: [
            if (rest['cozinha'] != null) ...[
              const Icon(Icons.restaurant_menu, size: 12, color: AppTheme.dark400), const SizedBox(width: 4),
              Text(rest['cozinha'] ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
            ],
            if (rest['tempo_medio_min'] != null) ...[
              const SizedBox(width: 10),
              const Icon(Icons.schedule, size: 12, color: AppTheme.dark400), const SizedBox(width: 4),
              Text('${rest['tempo_medio_min']} min', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
            ],
          ]),
          if (rest['rating_medio'] != null) Row(children: [
            const Icon(Icons.star, size: 12, color: AppTheme.accent), const SizedBox(width: 2),
            Text('${rest['rating_medio']}', style: const TextStyle(color: AppTheme.accent, fontSize: 12)),
            if (rest['pedido_minimo'] != null) Text(' - Min: ${rest['pedido_minimo'].toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.dark500, fontSize: 11)),
          ]),
        ])),
        if (rest['aberto'] == true)
          const StatusBadge(label: 'Aberto', variant: 'success')
        else
          const StatusBadge(label: 'Fechado', variant: 'danger'),
      ])),
    );
  }
}

class _RestMenuScreen extends StatefulWidget {
  final Map<String, dynamic> rest;
  final ModuleService svc;
  const _RestMenuScreen({required this.rest, required this.svc});
  @override
  State<_RestMenuScreen> createState() => _RestMenuScreenState();
}

class _RestMenuScreenState extends State<_RestMenuScreen> {
  List<dynamic> _menu = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadMenu();
  }

  Future<void> _loadMenu() async {
    try {
      _menu = await widget.svc.getMenu(widget.rest['id'].toString());
    } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  void _addToCart(Map<String, dynamic> item) {
    final cart = context.read<CartProvider>();
    final restId = widget.rest['id'].toString();
    cart.addItem(
      CartItem(
        id: item['id'].toString(),
        name: item['nome'] ?? 'Item',
        price: (item['preco'] ?? 0).toDouble(),
        type: CartItemType.menuItem,
        meta: {'restaurant_id': restId, 'categoria': item['categoria']},
      ),
      contextId: restId,
    );
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('${item['nome']} adicionado'),
        backgroundColor: AppTheme.success,
        duration: const Duration(seconds: 1),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cart = context.watch<CartProvider>();

    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(
        title: Text(widget.rest['nome'] ?? 'Menu'),
        backgroundColor: AppTheme.dark800,
        actions: [
          if (!cart.isEmpty)
            _CartBadge(
              count: cart.count,
              onTap: () => Navigator.push(context, MaterialPageRoute(
                builder: (_) => const CheckoutScreen(titulo: 'Checkout Restaurante'),
              )),
            ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Colors.red))
          : _menu.isEmpty
              ? const EmptyState(icon: Icons.restaurant_menu, title: 'Menu vazio', subtitle: 'Este restaurante ainda nao tem menu')
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _menu.length,
                  itemBuilder: (ctx, i) {
                    final item = _menu[i];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 10),
                      child: TCard(child: Row(children: [
                        Container(
                          width: 48, height: 48,
                          decoration: BoxDecoration(color: Colors.red.withOpacity(0.08), borderRadius: BorderRadius.circular(12)),
                          child: const Icon(Icons.fastfood, color: Colors.red, size: 24),
                        ),
                        const SizedBox(width: 12),
                        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                          Text(item['nome'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                          if (item['descricao'] != null) Text(item['descricao'], style: const TextStyle(color: AppTheme.dark400, fontSize: 12), maxLines: 1, overflow: TextOverflow.ellipsis),
                          if (item['categoria'] != null) StatusBadge(label: item['categoria'], variant: 'primary'),
                        ])),
                        Text('${(item['preco'] ?? 0).toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 15)),
                        const SizedBox(width: 8),
                        GestureDetector(
                          onTap: () => _addToCart(item),
                          child: Container(
                            width: 36, height: 36,
                            decoration: BoxDecoration(color: AppTheme.primary.withOpacity(0.15), borderRadius: BorderRadius.circular(10)),
                            child: const Icon(Icons.add, color: AppTheme.primary, size: 20),
                          ),
                        ),
                      ])),
                    );
                  },
                ),
      floatingActionButton: cart.isEmpty ? null : FloatingActionButton.extended(
        backgroundColor: AppTheme.primary,
        icon: const Icon(Icons.shopping_cart_checkout, color: Colors.white),
        label: Text('Checkout (${cart.count}) - ${cart.subtotal.toStringAsFixed(0)} Kz',
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        onPressed: () => Navigator.push(context, MaterialPageRoute(
          builder: (_) => const CheckoutScreen(titulo: 'Checkout Restaurante'),
        )),
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

class _Search extends StatelessWidget {
  final String hint;
  final ValueChanged<String> onChanged;
  const _Search({required this.hint, required this.onChanged});
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.all(16),
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      decoration: BoxDecoration(color: AppTheme.dark800, borderRadius: BorderRadius.circular(12), border: Border.all(color: AppTheme.dark700)),
      child: Row(children: [const Icon(Icons.search, color: AppTheme.dark500, size: 20), const SizedBox(width: 10),
        Expanded(child: TextField(onChanged: onChanged, style: const TextStyle(color: Colors.white, fontSize: 14),
          decoration: InputDecoration(border: InputBorder.none, hintText: hint, hintStyle: const TextStyle(color: AppTheme.dark500))))]),
    ),
  );
}
