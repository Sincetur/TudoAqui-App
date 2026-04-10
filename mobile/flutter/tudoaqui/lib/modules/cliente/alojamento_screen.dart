import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/module_service.dart';
import '../../services/cart_service.dart';
import '../../modules/common/checkout_screen.dart';
import '../../widgets/common.dart';

class AlojamentoScreen extends StatefulWidget {
  const AlojamentoScreen({super.key});
  @override
  State<AlojamentoScreen> createState() => _AlojamentoScreenState();
}

class _AlojamentoScreenState extends State<AlojamentoScreen> {
  final _svc = ModuleService();
  List<dynamic> _props = [];
  bool _loading = true;
  String _search = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try { _props = await _svc.listAlojamento(); } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  List<dynamic> get _filtered => _props.where((p) =>
      (p['titulo'] ?? '').toString().toLowerCase().contains(_search.toLowerCase()) ||
      (p['cidade'] ?? '').toString().toLowerCase().contains(_search.toLowerCase())).toList();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(title: const Text('Alojamento'), backgroundColor: AppTheme.dark800),
      body: Column(
        children: [
          _SearchInput(hint: 'Procurar alojamento...', onChanged: (v) => setState(() => _search = v)),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator(color: Colors.blue))
                : _filtered.isEmpty
                    ? const EmptyState(icon: Icons.hotel, title: 'Sem alojamento', subtitle: 'Nenhuma propriedade disponivel')
                    : RefreshIndicator(onRefresh: _load, child: ListView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        itemCount: _filtered.length,
                        itemBuilder: (ctx, i) => _PropCard(prop: _filtered[i], onTap: () => _openDetail(_filtered[i])),
                      )),
          ),
        ],
      ),
    );
  }

  void _openDetail(Map<String, dynamic> prop) {
    Navigator.push(context, MaterialPageRoute(builder: (_) => _AlojamentoDetailScreen(prop: prop)));
  }
}

class _PropCard extends StatelessWidget {
  final Map<String, dynamic> prop;
  final VoidCallback onTap;
  const _PropCard({required this.prop, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TCard(onTap: onTap, child: Row(children: [
        Container(
          width: 56, height: 56,
          decoration: BoxDecoration(color: Colors.blue.withOpacity(0.12), borderRadius: BorderRadius.circular(12)),
          child: const Icon(Icons.hotel, color: Colors.blue),
        ),
        const SizedBox(width: 12),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(prop['titulo'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
          Row(children: [
            const Icon(Icons.place, size: 12, color: AppTheme.dark400),
            const SizedBox(width: 4),
            Text('${prop['cidade'] ?? ''}, ${prop['provincia'] ?? ''}', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
          ]),
          Row(children: [
            const Icon(Icons.bed, size: 12, color: AppTheme.dark400),
            const SizedBox(width: 4),
            Text('${prop['quartos'] ?? 0}q  ${prop['max_hospedes'] ?? 0} hosp', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
            const Spacer(),
            if (prop['rating_medio'] != null) ...[
              const Icon(Icons.star, size: 12, color: AppTheme.accent),
              const SizedBox(width: 2),
              Text('${prop['rating_medio']}', style: const TextStyle(color: AppTheme.accent, fontSize: 12)),
            ],
          ]),
        ])),
        Column(children: [
          Text('${(prop['preco_noite'] ?? 0).toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 15)),
          const Text('/noite', style: TextStyle(color: AppTheme.dark500, fontSize: 10)),
        ]),
      ])),
    );
  }
}

class _AlojamentoDetailScreen extends StatefulWidget {
  final Map<String, dynamic> prop;
  const _AlojamentoDetailScreen({required this.prop});
  @override
  State<_AlojamentoDetailScreen> createState() => _AlojamentoDetailScreenState();
}

class _AlojamentoDetailScreenState extends State<_AlojamentoDetailScreen> {
  DateTime? _checkin;
  DateTime? _checkout;
  int _adultos = 1;
  int _criancas = 0;

  int get _noites {
    if (_checkin == null || _checkout == null) return 0;
    return _checkout!.difference(_checkin!).inDays;
  }

  double get _totalEstimado {
    final preco = (widget.prop['preco_noite'] ?? 0).toDouble();
    return preco * _noites;
  }

  Future<void> _pickDate(bool isCheckin) async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: isCheckin ? now : (_checkin?.add(const Duration(days: 1)) ?? now.add(const Duration(days: 1))),
      firstDate: isCheckin ? now : (_checkin?.add(const Duration(days: 1)) ?? now),
      lastDate: now.add(const Duration(days: 365)),
      builder: (ctx, child) => Theme(
        data: ThemeData.dark().copyWith(colorScheme: const ColorScheme.dark(primary: AppTheme.primary, surface: AppTheme.dark800)),
        child: child!,
      ),
    );
    if (picked != null) {
      setState(() {
        if (isCheckin) {
          _checkin = picked;
          if (_checkout != null && _checkout!.isBefore(picked.add(const Duration(days: 1)))) {
            _checkout = null;
          }
        } else {
          _checkout = picked;
        }
      });
    }
  }

  void _reservar() {
    if (_checkin == null || _checkout == null || _noites <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Selecione as datas de checkin e checkout'), backgroundColor: AppTheme.danger),
      );
      return;
    }

    final cart = context.read<CartProvider>();
    cart.clear();
    cart.addItem(
      CartItem(
        id: widget.prop['id'].toString(),
        name: '${widget.prop['titulo']} ($_noites noites)',
        price: _totalEstimado,
        type: CartItemType.alojamento,
        meta: {
          'property_id': widget.prop['id']?.toString(),
        },
      ),
      contextId: widget.prop['id']?.toString(),
    );

    Navigator.push(context, MaterialPageRoute(
      builder: (_) => CheckoutScreen(
        titulo: 'Reserva Alojamento',
        extraData: {
          'data_checkin': _checkin!.toIso8601String().split('T')[0],
          'data_checkout': _checkout!.toIso8601String().split('T')[0],
          'adultos': _adultos,
          'criancas': _criancas,
        },
      ),
    ));
  }

  String _formatDate(DateTime? d) => d != null ? '${d.day}/${d.month}/${d.year}' : 'Selecionar';

  @override
  Widget build(BuildContext context) {
    final comodidades = (widget.prop['comodidades'] as List?)?.cast<String>() ?? [];
    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(title: Text(widget.prop['titulo'] ?? ''), backgroundColor: AppTheme.dark800),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Container(
            height: 180, width: double.infinity,
            decoration: BoxDecoration(color: Colors.blue.withOpacity(0.08), borderRadius: BorderRadius.circular(16)),
            child: const Center(child: Icon(Icons.hotel, color: Colors.blue, size: 64)),
          ),
          const SizedBox(height: 16),
          Text(widget.prop['titulo'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20)),
          const SizedBox(height: 4),
          Text('${widget.prop['cidade'] ?? ''}, ${widget.prop['provincia'] ?? ''}', style: const TextStyle(color: AppTheme.dark400)),
          const SizedBox(height: 12),
          Row(children: [
            _Stat(Icons.bed, '${widget.prop['quartos'] ?? 0} quartos'),
            _Stat(Icons.bathtub, '${widget.prop['banheiros'] ?? 0} ban'),
            _Stat(Icons.people, '${widget.prop['max_hospedes'] ?? 0} hosp'),
          ]),
          const SizedBox(height: 16),
          Text('${(widget.prop['preco_noite'] ?? 0).toStringAsFixed(0)} Kz / noite', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 22)),
          if (widget.prop['descricao'] != null) ...[
            const SizedBox(height: 12),
            Text(widget.prop['descricao'], style: const TextStyle(color: AppTheme.dark300, fontSize: 14)),
          ],
          if (comodidades.isNotEmpty) ...[
            const SizedBox(height: 16),
            const Text('Comodidades', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 8),
            Wrap(spacing: 6, runSpacing: 6, children: comodidades.map((c) =>
              Container(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4), decoration: BoxDecoration(color: AppTheme.dark800, borderRadius: BorderRadius.circular(8)),
                child: Text(c, style: const TextStyle(color: AppTheme.dark300, fontSize: 12)),
              )).toList()),
          ],

          const SizedBox(height: 24),
          const Text('Reservar', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 12),

          // Date pickers
          Row(children: [
            Expanded(child: _DateBtn(label: 'Check-in', value: _formatDate(_checkin), onTap: () => _pickDate(true))),
            const SizedBox(width: 12),
            Expanded(child: _DateBtn(label: 'Check-out', value: _formatDate(_checkout), onTap: () => _pickDate(false))),
          ]),
          const SizedBox(height: 12),

          // Guest counters
          Row(children: [
            Expanded(child: _Counter(label: 'Adultos', value: _adultos, onChanged: (v) => setState(() => _adultos = v), min: 1, max: widget.prop['max_hospedes'] ?? 10)),
            const SizedBox(width: 12),
            Expanded(child: _Counter(label: 'Criancas', value: _criancas, onChanged: (v) => setState(() => _criancas = v), min: 0, max: 5)),
          ]),

          if (_noites > 0) ...[
            const SizedBox(height: 16),
            TCard(child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              Text('$_noites noites', style: const TextStyle(color: AppTheme.dark300, fontSize: 14)),
              Text('${_totalEstimado.toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 18)),
            ])),
          ],

          const SizedBox(height: 20),
          PrimaryButton(
            label: _noites > 0 ? 'Reservar - ${_totalEstimado.toStringAsFixed(0)} Kz' : 'Reservar',
            icon: Icons.book_online,
            onPressed: _reservar,
          ),
        ]),
      ),
    );
  }
}

class _DateBtn extends StatelessWidget {
  final String label;
  final String value;
  final VoidCallback onTap;
  const _DateBtn({required this.label, required this.value, required this.onTap});
  @override
  Widget build(BuildContext context) => GestureDetector(
    onTap: onTap,
    child: Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: AppTheme.dark800, borderRadius: BorderRadius.circular(12), border: Border.all(color: AppTheme.dark700)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label, style: const TextStyle(color: AppTheme.dark500, fontSize: 11)),
        const SizedBox(height: 4),
        Row(children: [
          const Icon(Icons.calendar_today, size: 14, color: AppTheme.accent),
          const SizedBox(width: 6),
          Text(value, style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w500)),
        ]),
      ]),
    ),
  );
}

class _Counter extends StatelessWidget {
  final String label;
  final int value;
  final ValueChanged<int> onChanged;
  final int min;
  final int max;
  const _Counter({required this.label, required this.value, required this.onChanged, this.min = 0, this.max = 10});
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(12),
    decoration: BoxDecoration(color: AppTheme.dark800, borderRadius: BorderRadius.circular(12), border: Border.all(color: AppTheme.dark700)),
    child: Row(children: [
      Text(label, style: const TextStyle(color: AppTheme.dark400, fontSize: 13)),
      const Spacer(),
      GestureDetector(
        onTap: value > min ? () => onChanged(value - 1) : null,
        child: Container(
          width: 28, height: 28,
          decoration: BoxDecoration(color: AppTheme.dark700, borderRadius: BorderRadius.circular(6)),
          child: Icon(Icons.remove, size: 16, color: value > min ? Colors.white : AppTheme.dark500),
        ),
      ),
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12),
        child: Text('$value', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
      ),
      GestureDetector(
        onTap: value < max ? () => onChanged(value + 1) : null,
        child: Container(
          width: 28, height: 28,
          decoration: BoxDecoration(color: AppTheme.dark700, borderRadius: BorderRadius.circular(6)),
          child: Icon(Icons.add, size: 16, color: value < max ? Colors.white : AppTheme.dark500),
        ),
      ),
    ]),
  );
}

class _Stat extends StatelessWidget {
  final IconData icon;
  final String text;
  const _Stat(this.icon, this.text);
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(right: 16),
    child: Row(children: [
      Icon(icon, size: 14, color: AppTheme.dark400),
      const SizedBox(width: 4),
      Text(text, style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
    ]),
  );
}

class _SearchInput extends StatelessWidget {
  final String hint;
  final ValueChanged<String> onChanged;
  const _SearchInput({required this.hint, required this.onChanged});
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.all(16),
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      decoration: BoxDecoration(color: AppTheme.dark800, borderRadius: BorderRadius.circular(12), border: Border.all(color: AppTheme.dark700)),
      child: Row(children: [
        const Icon(Icons.search, color: AppTheme.dark500, size: 20),
        const SizedBox(width: 10),
        Expanded(child: TextField(onChanged: onChanged, style: const TextStyle(color: Colors.white, fontSize: 14),
          decoration: InputDecoration(border: InputBorder.none, hintText: hint, hintStyle: const TextStyle(color: AppTheme.dark500)))),
      ]),
    ),
  );
}
