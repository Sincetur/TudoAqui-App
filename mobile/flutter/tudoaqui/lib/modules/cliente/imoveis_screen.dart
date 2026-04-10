import 'package:flutter/material.dart';
import '../../config/theme.dart';
import '../../services/module_service.dart';
import '../../widgets/common.dart';

class ImoveisScreen extends StatefulWidget {
  const ImoveisScreen({super.key});
  @override
  State<ImoveisScreen> createState() => _ImoveisScreenState();
}

class _ImoveisScreenState extends State<ImoveisScreen> {
  final _svc = ModuleService();
  List<dynamic> _imoveis = [];
  bool _loading = true;
  String _search = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try { _imoveis = await _svc.listImoveis(); } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  List<dynamic> get _filtered => _imoveis.where((p) =>
      (p['titulo'] ?? '').toString().toLowerCase().contains(_search.toLowerCase()) ||
      (p['cidade'] ?? '').toString().toLowerCase().contains(_search.toLowerCase())).toList();

  String _price(Map<String, dynamic> p) {
    if (p['preco_venda'] != null) return '${num.tryParse(p['preco_venda'].toString())?.toStringAsFixed(0)} Kz';
    if (p['preco_arrendamento'] != null) return '${num.tryParse(p['preco_arrendamento'].toString())?.toStringAsFixed(0)} Kz/mes';
    return '';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(title: const Text('Imobiliario'), backgroundColor: AppTheme.dark800),
      body: Column(children: [
        _Search(hint: 'Procurar imoveis...', onChanged: (v) => setState(() => _search = v)),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(color: Colors.purple))
              : _filtered.isEmpty
                  ? const EmptyState(icon: Icons.apartment, title: 'Sem imoveis', subtitle: 'Nenhum imovel disponivel')
                  : RefreshIndicator(onRefresh: _load, child: ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: _filtered.length,
                      itemBuilder: (ctx, i) => _ImovelCard(imovel: _filtered[i], price: _price(_filtered[i]), onTap: () => _openDetail(_filtered[i])),
                    )),
        ),
      ]),
    );
  }

  void _openDetail(Map<String, dynamic> im) {
    Navigator.push(context, MaterialPageRoute(builder: (_) => _ImovelDetailScreen(imovel: im)));
  }
}

class _ImovelCard extends StatelessWidget {
  final Map<String, dynamic> imovel;
  final String price;
  final VoidCallback onTap;
  const _ImovelCard({required this.imovel, required this.price, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TCard(onTap: onTap, child: Row(children: [
        Container(
          width: 56, height: 56,
          decoration: BoxDecoration(color: Colors.purple.withOpacity(0.12), borderRadius: BorderRadius.circular(12)),
          child: const Icon(Icons.apartment, color: Colors.purple),
        ),
        const SizedBox(width: 12),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(imovel['titulo'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
          Row(children: [
            const Icon(Icons.place, size: 12, color: AppTheme.dark400), const SizedBox(width: 4),
            Expanded(child: Text('${imovel['cidade'] ?? ''} ${imovel['bairro'] ?? ''}', style: const TextStyle(color: AppTheme.dark400, fontSize: 12), overflow: TextOverflow.ellipsis)),
          ]),
          Row(children: [
            if (imovel['quartos'] != null) ...[const Icon(Icons.bed, size: 12, color: AppTheme.dark400), const SizedBox(width: 2), Text('${imovel['quartos']}q ', style: const TextStyle(color: AppTheme.dark400, fontSize: 12))],
            if (imovel['area_util'] != null) ...[const Icon(Icons.square_foot, size: 12, color: AppTheme.dark400), const SizedBox(width: 2), Text('${imovel['area_util']}m2', style: const TextStyle(color: AppTheme.dark400, fontSize: 12))],
          ]),
          if (imovel['tipo_transacao'] != null)
            StatusBadge(label: imovel['tipo_transacao'] == 'venda' ? 'Venda' : 'Arrendamento', variant: imovel['tipo_transacao'] == 'venda' ? 'accent' : 'primary'),
        ])),
        Text(price, style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 14)),
      ])),
    );
  }
}

class _ImovelDetailScreen extends StatelessWidget {
  final Map<String, dynamic> imovel;
  const _ImovelDetailScreen({required this.imovel});

  @override
  Widget build(BuildContext context) {
    final caract = (imovel['caracteristicas'] as List?)?.cast<String>() ?? [];
    String price = '';
    if (imovel['preco_venda'] != null) price = '${imovel['preco_venda'].toStringAsFixed(0)} Kz';
    if (imovel['preco_arrendamento'] != null) price += '${price.isNotEmpty ? " / " : ""}${imovel['preco_arrendamento'].toStringAsFixed(0)} Kz/mes';

    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(title: Text(imovel['titulo'] ?? ''), backgroundColor: AppTheme.dark800),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Container(
            height: 200, width: double.infinity,
            decoration: BoxDecoration(color: Colors.purple.withOpacity(0.08), borderRadius: BorderRadius.circular(16)),
            child: const Center(child: Icon(Icons.apartment, color: Colors.purple, size: 64)),
          ),
          const SizedBox(height: 16),
          Text(imovel['titulo'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20)),
          Text('${imovel['cidade'] ?? ''}, ${imovel['provincia'] ?? ''}', style: const TextStyle(color: AppTheme.dark400)),
          const SizedBox(height: 12),
          Text(price, style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 22)),
          const SizedBox(height: 12),
          Wrap(spacing: 16, runSpacing: 8, children: [
            if (imovel['quartos'] != null) _DetailTag(Icons.bed, '${imovel['quartos']} quartos'),
            if (imovel['suites'] != null) _DetailTag(Icons.king_bed, '${imovel['suites']} suites'),
            if (imovel['banheiros'] != null) _DetailTag(Icons.bathtub, '${imovel['banheiros']} ban'),
            if (imovel['vagas_garagem'] != null) _DetailTag(Icons.garage, '${imovel['vagas_garagem']} garagem'),
            if (imovel['area_util'] != null) _DetailTag(Icons.square_foot, '${imovel['area_util']} m2'),
          ]),
          if (imovel['descricao'] != null) ...[
            const SizedBox(height: 12),
            Text(imovel['descricao'], style: const TextStyle(color: AppTheme.dark300, fontSize: 14)),
          ],
          if (caract.isNotEmpty) ...[
            const SizedBox(height: 16),
            const Text('Caracteristicas', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 8),
            Wrap(spacing: 6, runSpacing: 6, children: caract.map((c) =>
              Container(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4), decoration: BoxDecoration(color: AppTheme.dark800, borderRadius: BorderRadius.circular(8)),
                child: Text(c, style: const TextStyle(color: AppTheme.dark300, fontSize: 12)))).toList()),
          ],
          const SizedBox(height: 20),
          PrimaryButton(label: 'Contactar Agente', icon: Icons.phone, onPressed: () {
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Contacto do agente disponivel na web'), backgroundColor: AppTheme.info));
          }),
        ]),
      ),
    );
  }
}

class _DetailTag extends StatelessWidget {
  final IconData icon;
  final String text;
  const _DetailTag(this.icon, this.text);
  @override
  Widget build(BuildContext context) => Row(mainAxisSize: MainAxisSize.min, children: [
    Icon(icon, size: 14, color: AppTheme.dark400), const SizedBox(width: 4), Text(text, style: const TextStyle(color: AppTheme.dark300, fontSize: 12)),
  ]);
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
