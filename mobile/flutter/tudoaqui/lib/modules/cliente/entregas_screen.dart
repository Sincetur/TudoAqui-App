import 'package:flutter/material.dart';
import '../../config/theme.dart';
import '../../services/module_service.dart';
import '../../widgets/common.dart';

class EntregasScreen extends StatefulWidget {
  const EntregasScreen({super.key});
  @override
  State<EntregasScreen> createState() => _EntregasScreenState();
}

class _EntregasScreenState extends State<EntregasScreen> with SingleTickerProviderStateMixin {
  final _svc = ModuleService();
  late TabController _tab;
  List<dynamic> _deliveries = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _tab = TabController(length: 2, vsync: this);
    _loadDeliveries();
  }

  Future<void> _loadDeliveries() async {
    setState(() => _loading = true);
    try { _deliveries = await _svc.listMyDeliveries(); } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  @override
  void dispose() {
    _tab.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(
        title: const Text('Entregas'),
        backgroundColor: AppTheme.dark800,
        bottom: TabBar(controller: _tab, tabs: const [
          Tab(text: 'Nova Entrega'),
          Tab(text: 'Minhas Entregas'),
        ]),
      ),
      body: TabBarView(controller: _tab, children: [
        _NewDeliveryTab(svc: _svc),
        _MyDeliveriesTab(deliveries: _deliveries, loading: _loading, onRefresh: _loadDeliveries),
      ]),
    );
  }
}

class _NewDeliveryTab extends StatefulWidget {
  final ModuleService svc;
  const _NewDeliveryTab({required this.svc});
  @override
  State<_NewDeliveryTab> createState() => _NewDeliveryTabState();
}

class _NewDeliveryTabState extends State<_NewDeliveryTab> {
  final _origemCtrl = TextEditingController();
  final _destinoCtrl = TextEditingController();
  final _descCtrl = TextEditingController();
  final _telCtrl = TextEditingController();
  bool _submitting = false;

  Future<void> _submit() async {
    if (_origemCtrl.text.length < 5 || _destinoCtrl.text.length < 5) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Preencha origem e destino'), backgroundColor: AppTheme.danger));
      return;
    }
    setState(() => _submitting = true);
    try {
      await widget.svc.createDelivery({
        'origem_endereco': _origemCtrl.text,
        'origem_latitude': -8.8383,
        'origem_longitude': 13.2344,
        'destino_endereco': _destinoCtrl.text,
        'destino_latitude': -8.84,
        'destino_longitude': 13.24,
        'descricao': _descCtrl.text,
        'telefone_contato': _telCtrl.text.isNotEmpty ? _telCtrl.text : '+244900000000',
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Entrega solicitada!'), backgroundColor: AppTheme.success));
        _origemCtrl.clear(); _destinoCtrl.clear(); _descCtrl.clear();
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e'), backgroundColor: AppTheme.danger));
    }
    if (mounted) setState(() => _submitting = false);
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Solicitar Entrega', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
        const SizedBox(height: 16),
        _Field(ctrl: _origemCtrl, label: 'Endereco de recolha', icon: Icons.circle),
        _Field(ctrl: _destinoCtrl, label: 'Endereco de entrega', icon: Icons.place),
        _Field(ctrl: _descCtrl, label: 'Descricao do pacote', icon: Icons.inventory_2),
        _Field(ctrl: _telCtrl, label: 'Telefone de contacto', icon: Icons.phone),
        const SizedBox(height: 16),
        PrimaryButton(label: 'Solicitar Entrega', icon: Icons.local_shipping, loading: _submitting, onPressed: _submit),
      ]),
    );
  }
}

class _Field extends StatelessWidget {
  final TextEditingController ctrl;
  final String label;
  final IconData icon;
  const _Field({required this.ctrl, required this.label, required this.icon});
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: TextField(
      controller: ctrl,
      style: const TextStyle(color: Colors.white, fontSize: 14),
      decoration: InputDecoration(
        prefixIcon: Icon(icon, color: AppTheme.dark400, size: 18),
        labelText: label,
        labelStyle: const TextStyle(color: AppTheme.dark500),
        filled: true,
        fillColor: AppTheme.dark800,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppTheme.dark700)),
        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppTheme.dark700)),
      ),
    ),
  );
}

class _MyDeliveriesTab extends StatelessWidget {
  final List<dynamic> deliveries;
  final bool loading;
  final Future<void> Function() onRefresh;
  const _MyDeliveriesTab({required this.deliveries, required this.loading, required this.onRefresh});

  String _statusLabel(String? s) => {
    'solicitada': 'Solicitada',
    'aceite': 'Aceite',
    'recolhida': 'Recolhida',
    'em_transito': 'Em transito',
    'entregue': 'Entregue',
    'cancelada': 'Cancelada',
  }[s] ?? s ?? '';

  String _statusVariant(String? s) => {
    'entregue': 'success',
    'cancelada': 'danger',
    'em_transito': 'primary',
  }[s] ?? 'warning';

  @override
  Widget build(BuildContext context) {
    if (loading) return const Center(child: CircularProgressIndicator(color: Colors.orange));
    if (deliveries.isEmpty) return const EmptyState(icon: Icons.local_shipping, title: 'Sem entregas', subtitle: 'As suas entregas aparecerão aqui');
    return RefreshIndicator(
      onRefresh: onRefresh,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: deliveries.length,
        itemBuilder: (ctx, i) {
          final d = deliveries[i];
          return Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: TCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [
                const Icon(Icons.local_shipping, color: Colors.orange, size: 20),
                const SizedBox(width: 8),
                Expanded(child: Text(d['descricao'] ?? 'Entrega #${(d['id'] ?? '').toString().substring(0, 8)}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14))),
                StatusBadge(label: _statusLabel(d['status']), variant: _statusVariant(d['status'])),
              ]),
              const SizedBox(height: 8),
              Row(children: [const Icon(Icons.circle, size: 8, color: AppTheme.success), const SizedBox(width: 6),
                Expanded(child: Text(d['origem_endereco'] ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)))]),
              const SizedBox(height: 4),
              Row(children: [const Icon(Icons.place, size: 8, color: AppTheme.primary), const SizedBox(width: 6),
                Expanded(child: Text(d['destino_endereco'] ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)))]),
              if (d['valor_estimado'] != null) ...[
                const SizedBox(height: 6),
                Text('${d['valor_estimado'].toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold)),
              ],
            ])),
          );
        },
      ),
    );
  }
}
