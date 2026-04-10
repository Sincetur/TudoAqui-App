import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/auth_service.dart';
import '../../services/module_service.dart';
import '../../widgets/common.dart';

class ProprietarioHome extends StatefulWidget {
  const ProprietarioHome({super.key});
  @override
  State<ProprietarioHome> createState() => _ProprietarioHomeState();
}

class _ProprietarioHomeState extends State<ProprietarioHome> {
  int _currentIndex = 0;
  final _svc = ModuleService();

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    return Scaffold(
      body: [
        _DashboardTab(auth: auth, svc: _svc),
        _PedidosTab(svc: _svc),
        _ProdutosTab(svc: _svc),
        _ProfileTab(user: auth.user),
      ][_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.dashboard_rounded), label: 'Dashboard'),
          BottomNavigationBarItem(icon: Icon(Icons.receipt_long), label: 'Pedidos'),
          BottomNavigationBarItem(icon: Icon(Icons.inventory_2), label: 'Produtos'),
          BottomNavigationBarItem(icon: Icon(Icons.person_rounded), label: 'Perfil'),
        ],
      ),
    );
  }
}

class _DashboardTab extends StatefulWidget {
  final AuthService auth;
  final ModuleService svc;
  const _DashboardTab({required this.auth, required this.svc});
  @override
  State<_DashboardTab> createState() => _DashboardTabState();
}

class _DashboardTabState extends State<_DashboardTab> {
  int _totalProducts = 0;
  int _totalOrders = 0;

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    try {
      final products = await widget.svc.listProducts();
      final orders = await widget.svc.listMyOrders();
      if (mounted) setState(() {
        _totalProducts = products.length;
        _totalOrders = orders.length;
      });
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            const Icon(Icons.store, color: AppTheme.primary, size: 28),
            const SizedBox(width: 10),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(widget.auth.partner?.nomeNegocio ?? 'Meu Negocio', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
              Text(widget.auth.partner?.tipoLabel ?? 'Proprietario', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
            ])),
            if (widget.auth.partner != null)
              StatusBadge(label: widget.auth.partner!.status, variant: widget.auth.partner!.isAprovado ? 'success' : 'warning'),
          ]),
          const SizedBox(height: 20),
          Row(children: [
            Expanded(child: StatCard(label: 'Pedidos', value: '$_totalOrders', icon: Icons.receipt_long, color: AppTheme.primary)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(label: 'Produtos', value: '$_totalProducts', icon: Icons.inventory_2, color: AppTheme.info)),
          ]),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(child: StatCard(label: 'Receita Hoje', value: '0 Kz', icon: Icons.trending_up, color: AppTheme.success)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(label: 'Avaliacao', value: '4.5', icon: Icons.star, color: AppTheme.accent)),
          ]),
        ]),
      ),
    );
  }
}

class _PedidosTab extends StatefulWidget {
  final ModuleService svc;
  const _PedidosTab({required this.svc});
  @override
  State<_PedidosTab> createState() => _PedidosTabState();
}

class _PedidosTabState extends State<_PedidosTab> {
  List<dynamic> _orders = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try { _orders = await widget.svc.listMyOrders(); } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Pedidos', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
        const SizedBox(height: 12),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
              : _orders.isEmpty
                  ? const EmptyState(icon: Icons.receipt_long, title: 'Sem pedidos', subtitle: 'Os pedidos dos clientes aparecerao aqui')
                  : RefreshIndicator(onRefresh: _load, child: ListView.builder(
                      itemCount: _orders.length,
                      itemBuilder: (ctx, i) {
                        final o = _orders[i];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: TCard(child: Row(children: [
                            const Icon(Icons.receipt_long, color: AppTheme.primary),
                            const SizedBox(width: 12),
                            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                              Text('Pedido #${(o['id'] ?? '').toString().substring(0, 8)}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                              Text('${o['total']?.toStringAsFixed(0) ?? '0'} Kz - ${o['endereco_entrega'] ?? ''}', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
                            ])),
                            StatusBadge(label: o['status'] ?? '', variant: o['status'] == 'entregue' ? 'success' : 'warning'),
                          ])),
                        );
                      },
                    )),
        ),
      ]),
    ));
  }
}

class _ProdutosTab extends StatefulWidget {
  final ModuleService svc;
  const _ProdutosTab({required this.svc});
  @override
  State<_ProdutosTab> createState() => _ProdutosTabState();
}

class _ProdutosTabState extends State<_ProdutosTab> {
  List<dynamic> _products = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try { _products = await widget.svc.listProducts(); } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  void _showCreateDialog() {
    final nomeCtrl = TextEditingController();
    final precoCtrl = TextEditingController();
    final descCtrl = TextEditingController();
    final stockCtrl = TextEditingController(text: '10');

    showDialog(context: context, builder: (ctx) => AlertDialog(
      backgroundColor: AppTheme.dark800,
      title: const Text('Novo Produto', style: TextStyle(color: Colors.white)),
      content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [
        _DialogField(ctrl: nomeCtrl, label: 'Nome do produto'),
        _DialogField(ctrl: precoCtrl, label: 'Preco (Kz)', keyboard: TextInputType.number),
        _DialogField(ctrl: descCtrl, label: 'Descricao'),
        _DialogField(ctrl: stockCtrl, label: 'Stock', keyboard: TextInputType.number),
      ])),
      actions: [
        TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar', style: TextStyle(color: AppTheme.dark400))),
        ElevatedButton(onPressed: () async {
          if (nomeCtrl.text.isEmpty || precoCtrl.text.isEmpty) return;
          Navigator.pop(ctx);
          try {
            await widget.svc.createProduct({
              'nome': nomeCtrl.text,
              'preco': double.tryParse(precoCtrl.text) ?? 0,
              'descricao': descCtrl.text,
              'stock': int.tryParse(stockCtrl.text) ?? 10,
            });
            _load();
            if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Produto criado!'), backgroundColor: AppTheme.success));
          } catch (e) {
            if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e'), backgroundColor: AppTheme.danger));
          }
        }, child: const Text('Criar')),
      ],
    ));
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
          const Text('Produtos', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
          ElevatedButton.icon(icon: const Icon(Icons.add, size: 18), label: const Text('Adicionar'), onPressed: _showCreateDialog),
        ]),
        const SizedBox(height: 12),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(color: AppTheme.info))
              : _products.isEmpty
                  ? const EmptyState(icon: Icons.inventory_2, title: 'Sem produtos', subtitle: 'Adicione produtos ao seu catalogo')
                  : RefreshIndicator(onRefresh: _load, child: ListView.builder(
                      itemCount: _products.length,
                      itemBuilder: (ctx, i) {
                        final p = _products[i];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: TCard(child: Row(children: [
                            Container(
                              width: 44, height: 44,
                              decoration: BoxDecoration(color: AppTheme.accent.withOpacity(0.1), borderRadius: BorderRadius.circular(10)),
                              child: const Icon(Icons.shopping_bag, color: AppTheme.accent, size: 20),
                            ),
                            const SizedBox(width: 12),
                            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                              Text(p['nome'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                              Text('Stock: ${p['stock'] ?? 0}', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
                            ])),
                            Text('${(p['preco'] ?? p['preco_atual'] ?? 0).toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 15)),
                          ])),
                        );
                      },
                    )),
        ),
      ]),
    ));
  }
}

class _DialogField extends StatelessWidget {
  final TextEditingController ctrl;
  final String label;
  final TextInputType? keyboard;
  const _DialogField({required this.ctrl, required this.label, this.keyboard});
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: TextField(
      controller: ctrl, keyboardType: keyboard,
      style: const TextStyle(color: Colors.white, fontSize: 14),
      decoration: InputDecoration(
        labelText: label, labelStyle: const TextStyle(color: AppTheme.dark500),
        filled: true, fillColor: AppTheme.dark900,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppTheme.dark700)),
        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppTheme.dark700)),
      ),
    ),
  );
}

class _ProfileTab extends StatelessWidget {
  final dynamic user;
  const _ProfileTab({this.user});
  @override
  Widget build(BuildContext context) => SafeArea(
    child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const SizedBox(height: 20),
        const Text('Perfil', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
        const SizedBox(height: 20),
        TCard(child: Row(children: [
          CircleAvatar(radius: 28, backgroundColor: AppTheme.primary, child: const Icon(Icons.store, color: Colors.white)),
          const SizedBox(width: 14),
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(user?.nome ?? 'Proprietario', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            Text(user?.telefone ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 13)),
          ]),
        ])),
        const Spacer(),
        SizedBox(width: double.infinity, child: OutlinedButton.icon(
          onPressed: () => context.read<AuthService>().logout(),
          icon: const Icon(Icons.logout, color: AppTheme.danger),
          label: const Text('Sair', style: TextStyle(color: AppTheme.danger)),
        )),
      ]),
    ),
  );
}
