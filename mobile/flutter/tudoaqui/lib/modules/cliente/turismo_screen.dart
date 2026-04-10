import 'package:flutter/material.dart';
import '../../config/theme.dart';
import '../../services/module_service.dart';
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
    Navigator.push(context, MaterialPageRoute(builder: (_) => _TurismoDetailScreen(exp: exp)));
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

class _TurismoDetailScreen extends StatelessWidget {
  final Map<String, dynamic> exp;
  const _TurismoDetailScreen({required this.exp});

  @override
  Widget build(BuildContext context) {
    final inclui = (exp['inclui'] as List?)?.cast<String>() ?? [];
    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(title: Text(exp['titulo'] ?? ''), backgroundColor: AppTheme.dark800),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Container(
            height: 180, width: double.infinity,
            decoration: BoxDecoration(color: Colors.green.withOpacity(0.08), borderRadius: BorderRadius.circular(16)),
            child: const Center(child: Icon(Icons.flight, color: Colors.green, size: 64)),
          ),
          const SizedBox(height: 16),
          Text(exp['titulo'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20)),
          const SizedBox(height: 4),
          Text('${exp['cidade'] ?? ''} - ${exp['local'] ?? ''}', style: const TextStyle(color: AppTheme.dark400)),
          const SizedBox(height: 12),
          Row(children: [
            _Tag(Icons.schedule, '${exp['duracao_horas'] ?? 0}h'),
            _Tag(Icons.people, '${exp['min_participantes'] ?? 1}-${exp['max_participantes'] ?? 10} pessoas'),
          ]),
          const SizedBox(height: 16),
          Text('${(exp['preco'] ?? 0).toStringAsFixed(0)} Kz / pessoa', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 22)),
          if (exp['preco_crianca'] != null)
            Text('Crianca: ${exp['preco_crianca'].toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.dark400, fontSize: 13)),
          if (exp['descricao'] != null) ...[
            const SizedBox(height: 12),
            Text(exp['descricao'], style: const TextStyle(color: AppTheme.dark300, fontSize: 14)),
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
          const SizedBox(height: 20),
          PrimaryButton(label: 'Reservar', icon: Icons.book_online, onPressed: () {
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Reserva disponivel na web'), backgroundColor: AppTheme.info));
          }),
        ]),
      ),
    );
  }
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
