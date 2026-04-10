import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/auth_service.dart';
import '../../services/module_service.dart';
import '../../widgets/common.dart';

/// Home partilhado pelos Agentes (Imobiliario + Viagem)
class AgenteHome extends StatefulWidget {
  final String tipoAgente;
  const AgenteHome({super.key, required this.tipoAgente});
  @override
  State<AgenteHome> createState() => _AgenteHomeState();
}

class _AgenteHomeState extends State<AgenteHome> {
  int _currentIndex = 0;
  final _svc = ModuleService();

  bool get isImobiliario => widget.tipoAgente == 'agente_imobiliario';
  String get titulo => isImobiliario ? 'Agente Imobiliario' : 'Agente de Viagem';
  IconData get mainIcon => isImobiliario ? Icons.apartment : Icons.flight_takeoff;
  Color get mainColor => isImobiliario ? Colors.purple : Colors.teal;
  String get itemLabel => isImobiliario ? 'Imoveis' : 'Experiencias';

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    return Scaffold(
      body: [
        _DashboardTab(titulo: titulo, icon: mainIcon, color: mainColor, itemLabel: itemLabel, auth: auth, svc: _svc, isImob: isImobiliario),
        isImobiliario ? _ImoveisTab(svc: _svc) : _ExperienciasTab(svc: _svc),
        isImobiliario ? _LeadsTab(svc: _svc) : const _ClientesTab(),
        _ProfileTab(user: auth.user, titulo: titulo),
      ][_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        items: [
          const BottomNavigationBarItem(icon: Icon(Icons.home_rounded), label: 'Inicio'),
          BottomNavigationBarItem(icon: Icon(mainIcon), label: itemLabel),
          const BottomNavigationBarItem(icon: Icon(Icons.people), label: 'Clientes'),
          const BottomNavigationBarItem(icon: Icon(Icons.person_rounded), label: 'Perfil'),
        ],
      ),
    );
  }
}

class _DashboardTab extends StatefulWidget {
  final String titulo;
  final IconData icon;
  final Color color;
  final String itemLabel;
  final AuthService auth;
  final ModuleService svc;
  final bool isImob;
  const _DashboardTab({required this.titulo, required this.icon, required this.color, required this.itemLabel, required this.auth, required this.svc, required this.isImob});
  @override
  State<_DashboardTab> createState() => _DashboardTabState();
}

class _DashboardTabState extends State<_DashboardTab> {
  int _totalItems = 0;

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    try {
      final items = widget.isImob ? await widget.svc.listImoveis() : await widget.svc.listExperiences();
      if (mounted) setState(() => _totalItems = items.length);
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Icon(widget.icon, color: widget.color, size: 28),
            const SizedBox(width: 10),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(widget.auth.partner?.nomeNegocio ?? widget.titulo, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
              Text(widget.titulo, style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
            ])),
            if (widget.auth.partner != null)
              StatusBadge(label: widget.auth.partner!.status, variant: widget.auth.partner!.isAprovado ? 'success' : 'warning'),
          ]),
          const SizedBox(height: 20),
          Row(children: [
            Expanded(child: StatCard(label: widget.itemLabel, value: '$_totalItems', icon: widget.icon, color: widget.color)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(label: 'Clientes', value: '0', icon: Icons.people, color: AppTheme.primary)),
          ]),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(child: StatCard(label: 'Receita', value: '0 Kz', icon: Icons.trending_up, color: AppTheme.success)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(label: 'Avaliacao', value: '4.6', icon: Icons.star, color: AppTheme.accent)),
          ]),
        ]),
      ),
    );
  }
}

class _ImoveisTab extends StatefulWidget {
  final ModuleService svc;
  const _ImoveisTab({required this.svc});
  @override
  State<_ImoveisTab> createState() => _ImoveisTabState();
}

class _ImoveisTabState extends State<_ImoveisTab> {
  List<dynamic> _imoveis = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try { _imoveis = await widget.svc.listImoveis(); } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  void _showCreateDialog() {
    final tituloCtrl = TextEditingController();
    final enderecoCtrl = TextEditingController();
    final cidadeCtrl = TextEditingController(text: 'Luanda');
    final provinciaCtrl = TextEditingController(text: 'Luanda');
    final precoCtrl = TextEditingController();
    final quartosCtrl = TextEditingController(text: '2');

    showDialog(context: context, builder: (ctx) => AlertDialog(
      backgroundColor: AppTheme.dark800,
      title: const Text('Novo Imovel', style: TextStyle(color: Colors.white)),
      content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [
        _FD(ctrl: tituloCtrl, label: 'Titulo'),
        _FD(ctrl: enderecoCtrl, label: 'Endereco'),
        _FD(ctrl: cidadeCtrl, label: 'Cidade'),
        _FD(ctrl: provinciaCtrl, label: 'Provincia'),
        _FD(ctrl: precoCtrl, label: 'Preco Venda (Kz)', keyboard: TextInputType.number),
        _FD(ctrl: quartosCtrl, label: 'Quartos', keyboard: TextInputType.number),
      ])),
      actions: [
        TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar', style: TextStyle(color: AppTheme.dark400))),
        ElevatedButton(onPressed: () async {
          if (tituloCtrl.text.length < 3 || enderecoCtrl.text.length < 5) return;
          Navigator.pop(ctx);
          try {
            await widget.svc.createImovel({
              'titulo': tituloCtrl.text,
              'endereco': enderecoCtrl.text,
              'cidade': cidadeCtrl.text,
              'provincia': provinciaCtrl.text,
              'preco_venda': double.tryParse(precoCtrl.text) ?? 0,
              'quartos': int.tryParse(quartosCtrl.text) ?? 2,
            });
            _load();
            if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Imovel criado!'), backgroundColor: AppTheme.success));
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
          const Text('Imoveis', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
          ElevatedButton.icon(icon: const Icon(Icons.add, size: 18), label: const Text('Adicionar'), onPressed: _showCreateDialog),
        ]),
        const SizedBox(height: 12),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(color: Colors.purple))
              : _imoveis.isEmpty
                  ? const EmptyState(icon: Icons.apartment, title: 'Sem imoveis', subtitle: 'Adicione imoveis ao seu portfolio')
                  : RefreshIndicator(onRefresh: _load, child: ListView.builder(
                      itemCount: _imoveis.length,
                      itemBuilder: (ctx, i) {
                        final im = _imoveis[i];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: TCard(child: Row(children: [
                            Container(width: 44, height: 44, decoration: BoxDecoration(color: Colors.purple.withOpacity(0.1), borderRadius: BorderRadius.circular(10)),
                              child: const Icon(Icons.apartment, color: Colors.purple, size: 20)),
                            const SizedBox(width: 12),
                            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                              Text(im['titulo'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                              Text('${im['cidade'] ?? ''} - ${im['quartos'] ?? 0}q', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
                            ])),
                            Text('${(im['preco_venda'] ?? 0).toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold)),
                          ])),
                        );
                      },
                    )),
        ),
      ]),
    ));
  }
}

class _ExperienciasTab extends StatefulWidget {
  final ModuleService svc;
  const _ExperienciasTab({required this.svc});
  @override
  State<_ExperienciasTab> createState() => _ExperienciasTabState();
}

class _ExperienciasTabState extends State<_ExperienciasTab> {
  List<dynamic> _exps = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try { _exps = await widget.svc.listExperiences(); } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Experiencias', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
        const SizedBox(height: 12),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(color: Colors.teal))
              : _exps.isEmpty
                  ? const EmptyState(icon: Icons.flight, title: 'Sem pacotes', subtitle: 'Crie pacotes de viagem')
                  : RefreshIndicator(onRefresh: _load, child: ListView.builder(
                      itemCount: _exps.length,
                      itemBuilder: (ctx, i) {
                        final e = _exps[i];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: TCard(child: Row(children: [
                            Container(width: 44, height: 44, decoration: BoxDecoration(color: Colors.teal.withOpacity(0.1), borderRadius: BorderRadius.circular(10)),
                              child: const Icon(Icons.flight_takeoff, color: Colors.teal, size: 20)),
                            const SizedBox(width: 12),
                            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                              Text(e['titulo'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                              Text('${e['cidade'] ?? ''} - ${e['duracao_horas'] ?? 0}h', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
                            ])),
                            Text('${(e['preco'] ?? 0).toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold)),
                          ])),
                        );
                      },
                    )),
        ),
      ]),
    ));
  }
}

class _LeadsTab extends StatefulWidget {
  final ModuleService svc;
  const _LeadsTab({required this.svc});
  @override
  State<_LeadsTab> createState() => _LeadsTabState();
}

class _LeadsTabState extends State<_LeadsTab> {
  List<dynamic> _leads = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try { _leads = await widget.svc.listMyLeads(); } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Clientes / Leads', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
        const SizedBox(height: 12),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
              : _leads.isEmpty
                  ? const EmptyState(icon: Icons.people, title: 'Sem leads', subtitle: 'Os contactos de clientes interessados aparecerao aqui')
                  : RefreshIndicator(onRefresh: _load, child: ListView.builder(
                      itemCount: _leads.length,
                      itemBuilder: (ctx, i) {
                        final l = _leads[i];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: TCard(child: Row(children: [
                            const Icon(Icons.person, color: AppTheme.primary),
                            const SizedBox(width: 12),
                            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                              Text(l['nome'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                              Text(l['telefone'] ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
                              if (l['mensagem'] != null) Text(l['mensagem'], style: const TextStyle(color: AppTheme.dark500, fontSize: 11), maxLines: 1, overflow: TextOverflow.ellipsis),
                            ])),
                            StatusBadge(label: l['status'] ?? 'novo', variant: l['status'] == 'contactado' ? 'success' : 'warning'),
                          ])),
                        );
                      },
                    )),
        ),
      ]),
    ));
  }
}

class _ClientesTab extends StatelessWidget {
  const _ClientesTab();
  @override
  Widget build(BuildContext context) => const SafeArea(
    child: EmptyState(icon: Icons.people, title: 'Clientes', subtitle: 'Gestao de clientes do agente de viagem'),
  );
}

class _FD extends StatelessWidget {
  final TextEditingController ctrl;
  final String label;
  final TextInputType? keyboard;
  const _FD({required this.ctrl, required this.label, this.keyboard});
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
  final String titulo;
  const _ProfileTab({this.user, required this.titulo});
  @override
  Widget build(BuildContext context) => SafeArea(
    child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const SizedBox(height: 20),
        const Text('Perfil', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
        const SizedBox(height: 20),
        TCard(child: Row(children: [
          const CircleAvatar(radius: 28, backgroundColor: Colors.purple, child: Icon(Icons.badge, color: Colors.white)),
          const SizedBox(width: 14),
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(user?.nome ?? titulo, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            Text(user?.telefone ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 13)),
            StatusBadge(label: titulo, variant: 'primary'),
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
