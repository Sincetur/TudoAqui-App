import 'package:flutter/material.dart';
import '../../config/theme.dart';
import '../../services/module_service.dart';
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

class _AlojamentoDetailScreen extends StatelessWidget {
  final Map<String, dynamic> prop;
  const _AlojamentoDetailScreen({required this.prop});

  @override
  Widget build(BuildContext context) {
    final comodidades = (prop['comodidades'] as List?)?.cast<String>() ?? [];
    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(title: Text(prop['titulo'] ?? ''), backgroundColor: AppTheme.dark800),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Container(
            height: 180, width: double.infinity,
            decoration: BoxDecoration(color: Colors.blue.withOpacity(0.08), borderRadius: BorderRadius.circular(16)),
            child: const Center(child: Icon(Icons.hotel, color: Colors.blue, size: 64)),
          ),
          const SizedBox(height: 16),
          Text(prop['titulo'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20)),
          const SizedBox(height: 4),
          Text('${prop['cidade'] ?? ''}, ${prop['provincia'] ?? ''}', style: const TextStyle(color: AppTheme.dark400)),
          const SizedBox(height: 12),
          Row(children: [
            _Stat(Icons.bed, '${prop['quartos'] ?? 0} quartos'),
            _Stat(Icons.bathtub, '${prop['banheiros'] ?? 0} ban'),
            _Stat(Icons.people, '${prop['max_hospedes'] ?? 0} hosp'),
          ]),
          const SizedBox(height: 16),
          Text('${(prop['preco_noite'] ?? 0).toStringAsFixed(0)} Kz / noite', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 22)),
          if (prop['descricao'] != null) ...[
            const SizedBox(height: 12),
            Text(prop['descricao'], style: const TextStyle(color: AppTheme.dark300, fontSize: 14)),
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
          const SizedBox(height: 20),
          PrimaryButton(label: 'Reservar', icon: Icons.book_online, onPressed: () {
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Reserva disponivel na web'), backgroundColor: AppTheme.info));
          }),
        ]),
      ),
    );
  }
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
