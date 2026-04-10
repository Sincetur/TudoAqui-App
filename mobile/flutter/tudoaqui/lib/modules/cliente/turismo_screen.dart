import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/module_service.dart';
import '../../services/cart_service.dart';
import '../../modules/common/checkout_screen.dart';
import '../../widgets/common.dart';

class TurismoScreen extends StatefulWidget {
  const TurismoScreen({super.key});
  @override
  State<TurismoScreen> createState() => _TurismoScreenState();
}

class _TurismoScreenState extends State<TurismoScreen> {
  final _svc = ModuleService();
  List<dynamic> _experiences = [];
  bool _loading = true;
  String _search = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try { _experiences = await _svc.listExperiences(); } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  List<dynamic> get _filtered => _experiences.where((e) =>
      (e['titulo'] ?? '').toString().toLowerCase().contains(_search.toLowerCase())).toList();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(title: const Text('Turismo'), backgroundColor: AppTheme.dark800),
      body: Column(children: [
        _SearchBox(hint: 'Procurar experiencias...', onChanged: (v) => setState(() => _search = v)),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(color: Colors.green))
              : _filtered.isEmpty
                  ? const EmptyState(icon: Icons.flight, title: 'Sem experiencias', subtitle: 'Nenhuma experiencia disponivel')
                  : RefreshIndicator(onRefresh: _load, child: ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: _filtered.length,
                      itemBuilder: (ctx, i) => _ExpCard(exp: _filtered[i], onTap: () => _openDetail(_filtered[i])),
                    )),
        ),
      ]),
    );
  }

  void _openDetail(Map<String, dynamic> exp) {
    Navigator.push(context, MaterialPageRoute(builder: (_) => _TurismoDetailScreen(exp: exp, svc: _svc)));
  }
}

class _ExpCard extends StatelessWidget {
  final Map<String, dynamic> exp;
  final VoidCallback onTap;
  const _ExpCard({required this.exp, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TCard(onTap: onTap, child: Row(children: [
        Container(
          width: 48, height: 48,
          decoration: BoxDecoration(color: Colors.green.withOpacity(0.12), borderRadius: BorderRadius.circular(12)),
          child: const Icon(Icons.flight, color: Colors.green),
        ),
        const SizedBox(width: 12),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(exp['titulo'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
          Row(children: [
            const Icon(Icons.place, size: 12, color: AppTheme.dark400),
            const SizedBox(width: 4),
            Text('${exp['cidade'] ?? exp['local'] ?? ''}', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
            const SizedBox(width: 10),
            const Icon(Icons.schedule, size: 12, color: AppTheme.dark400),
            const SizedBox(width: 4),
            Text('${exp['duracao_horas'] ?? 0}h', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
          ]),
          if (exp['tipo'] != null) StatusBadge(label: exp['tipo'], variant: 'success'),
        ])),
        Column(children: [
          Text('${(exp['preco'] ?? 0).toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 15)),
          const Text('/pessoa', style: TextStyle(color: AppTheme.dark500, fontSize: 10)),
        ]),
      ])),
    );
  }
}

class _TurismoDetailScreen extends StatefulWidget {
  final Map<String, dynamic> exp;
  final ModuleService svc;
  const _TurismoDetailScreen({required this.exp, required this.svc});
  @override
  State<_TurismoDetailScreen> createState() => _TurismoDetailScreenState();
}

class _TurismoDetailScreenState extends State<_TurismoDetailScreen> {
  int _adultos = 1;
  int _criancas = 0;
  List<dynamic> _schedules = [];
  String? _selectedScheduleId;
  bool _loadingSchedules = true;

  @override
  void initState() {
    super.initState();
    _loadSchedules();
  }

  Future<void> _loadSchedules() async {
    try {
      _schedules = await widget.svc.listSchedules(widget.exp['id'].toString());
    } catch (_) {}
    if (mounted) setState(() => _loadingSchedules = false);
  }

  double get _totalEstimado {
    final preco = (widget.exp['preco'] ?? 0).toDouble();
    final precoCrianca = (widget.exp['preco_crianca'] ?? preco * 0.5).toDouble();
    return (preco * _adultos) + (precoCrianca * _criancas);
  }

  void _reservar() {
    if (_adultos <= 0) return;

    final cart = context.read<CartProvider>();
    cart.clear();
    cart.addItem(
      CartItem(
        id: widget.exp['id'].toString(),
        name: '${widget.exp['titulo']} ($_adultos adultos${_criancas > 0 ? ', $_criancas criancas' : ''})',
        price: _totalEstimado,
        type: CartItemType.turismo,
        meta: {
          'experience_id': widget.exp['id']?.toString(),
          'schedule_id': _selectedScheduleId,
        },
      ),
      contextId: widget.exp['id']?.toString(),
    );

    Navigator.push(context, MaterialPageRoute(
      builder: (_) => CheckoutScreen(
        titulo: 'Reserva Turismo',
        extraData: {
          'schedule_id': _selectedScheduleId ?? '',
          'adultos': _adultos,
          'criancas': _criancas,
        },
      ),
    ));
  }

  @override
  Widget build(BuildContext context) {
    final inclui = (widget.exp['inclui'] as List?)?.cast<String>() ?? [];
    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(title: Text(widget.exp['titulo'] ?? ''), backgroundColor: AppTheme.dark800),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Container(
            height: 180, width: double.infinity,
            decoration: BoxDecoration(color: Colors.green.withOpacity(0.08), borderRadius: BorderRadius.circular(16)),
            child: const Center(child: Icon(Icons.flight, color: Colors.green, size: 64)),
          ),
          const SizedBox(height: 16),
          Text(widget.exp['titulo'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20)),
          const SizedBox(height: 4),
          Text('${widget.exp['cidade'] ?? ''} - ${widget.exp['local'] ?? ''}', style: const TextStyle(color: AppTheme.dark400)),
          const SizedBox(height: 12),
          Row(children: [
            _Tag(Icons.schedule, '${widget.exp['duracao_horas'] ?? 0}h'),
            _Tag(Icons.people, '${widget.exp['min_participantes'] ?? 1}-${widget.exp['max_participantes'] ?? 10} pessoas'),
          ]),
          const SizedBox(height: 16),
          Text('${(widget.exp['preco'] ?? 0).toStringAsFixed(0)} Kz / pessoa', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 22)),
          if (widget.exp['preco_crianca'] != null)
            Text('Crianca: ${widget.exp['preco_crianca'].toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.dark400, fontSize: 13)),
          if (widget.exp['descricao'] != null) ...[
            const SizedBox(height: 12),
            Text(widget.exp['descricao'], style: const TextStyle(color: AppTheme.dark300, fontSize: 14)),
          ],
          if (inclui.isNotEmpty) ...[
            const SizedBox(height: 16),
            const Text('Inclui', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 8),
            ...inclui.map((i) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(children: [const Icon(Icons.check, size: 14, color: Colors.green), const SizedBox(width: 8), Text(i, style: const TextStyle(color: AppTheme.dark300, fontSize: 13))]),
            )),
          ],

          const SizedBox(height: 24),
          const Text('Reservar Experiencia', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 12),

          // Schedule selector
          if (_loadingSchedules)
            const Center(child: Padding(
              padding: EdgeInsets.all(8),
              child: CircularProgressIndicator(color: Colors.green, strokeWidth: 2),
            ))
          else if (_schedules.isNotEmpty) ...[
            const Text('Horario', style: TextStyle(color: AppTheme.dark400, fontSize: 13)),
            const SizedBox(height: 6),
            Wrap(spacing: 8, runSpacing: 8, children: _schedules.map((s) {
              final sid = s['id'].toString();
              final selected = _selectedScheduleId == sid;
              final vagas = s['vagas_livres'] ?? s['vagas_disponiveis'] ?? 0;
              return GestureDetector(
                onTap: vagas > 0 ? () => setState(() => _selectedScheduleId = sid) : null,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: selected ? AppTheme.primary.withOpacity(0.12) : AppTheme.dark800,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: selected ? AppTheme.primary : AppTheme.dark700),
                  ),
                  child: Column(children: [
                    Text('${s['data'] ?? ''}', style: TextStyle(color: selected ? Colors.white : AppTheme.dark300, fontSize: 13, fontWeight: FontWeight.w600)),
                    Text('${s['hora_inicio'] ?? ''} ($vagas vagas)', style: TextStyle(color: selected ? AppTheme.dark300 : AppTheme.dark500, fontSize: 11)),
                  ]),
                ),
              );
            }).toList()),
            const SizedBox(height: 16),
          ],

          // Guest counters
          Row(children: [
            Expanded(child: _Counter(label: 'Adultos', value: _adultos, onChanged: (v) => setState(() => _adultos = v), min: 1, max: widget.exp['max_participantes'] ?? 10)),
            const SizedBox(width: 12),
            Expanded(child: _Counter(label: 'Criancas', value: _criancas, onChanged: (v) => setState(() => _criancas = v), min: 0, max: 5)),
          ]),

          const SizedBox(height: 16),
          TCard(child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
            Text('$_adultos adultos${_criancas > 0 ? ' + $_criancas criancas' : ''}', style: const TextStyle(color: AppTheme.dark300, fontSize: 14)),
            Text('${_totalEstimado.toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 18)),
          ])),

          const SizedBox(height: 20),
          PrimaryButton(
            label: 'Reservar - ${_totalEstimado.toStringAsFixed(0)} Kz',
            icon: Icons.book_online,
            onPressed: _reservar,
          ),
        ]),
      ),
    );
  }
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

class _Tag extends StatelessWidget {
  final IconData icon;
  final String text;
  const _Tag(this.icon, this.text);
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(right: 16),
    child: Row(children: [Icon(icon, size: 14, color: AppTheme.dark400), const SizedBox(width: 4), Text(text, style: const TextStyle(color: AppTheme.dark400, fontSize: 12))]),
  );
}

class _SearchBox extends StatelessWidget {
  final String hint;
  final ValueChanged<String> onChanged;
  const _SearchBox({required this.hint, required this.onChanged});
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
