import 'package:flutter/material.dart';
import '../../config/theme.dart';
import '../../services/module_service.dart';
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
    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(title: const Text('Marketplace'), backgroundColor: AppTheme.dark800),
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
            Text('${(product['preco'] ?? product['preco_atual'] ?? 0).toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 24)),
            if (product['descricao'] != null) ...[
              const SizedBox(height: 12),
              Text(product['descricao'], style: const TextStyle(color: AppTheme.dark300, fontSize: 14)),
            ],
            const SizedBox(height: 8),
            if (product['stock'] != null)
              Text('Stock: ${product['stock']}', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
            const SizedBox(height: 20),
            PrimaryButton(label: 'Comprar', icon: Icons.shopping_cart, onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Funcionalidade de checkout disponivel na web'), backgroundColor: AppTheme.info));
            }),
          ],
        ),
      ),
    );
  }
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
