import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/auth_service.dart';
import '../../services/module_service.dart';
import '../../widgets/common.dart';

class GuiaHome extends StatefulWidget {
  const GuiaHome({super.key});
  @override
  State<GuiaHome> createState() => _GuiaHomeState();
}

class _GuiaHomeState extends State<GuiaHome> {
  int _currentIndex = 0;
  final _svc = ModuleService();

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    return Scaffold(
      body: [
        _DashboardTab(auth: auth, svc: _svc),
        _ExperienciasTab(svc: _svc),
        _ReservasTab(svc: _svc),
        _ProfileTab(user: auth.user),
      ][_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home_rounded), label: 'Inicio'),
          BottomNavigationBarItem(icon: Icon(Icons.explore), label: 'Experiencias'),
          BottomNavigationBarItem(icon: Icon(Icons.book_online), label: 'Reservas'),
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
  int _totalExp = 0;
  int _totalBookings = 0;

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    try {
      final exps = await widget.svc.listExperiences();
      final bookings = await widget.svc.listMyTurismoBookings();
      if (mounted) setState(() {
        _totalExp = exps.length;
        _totalBookings = bookings.length;
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
            const Icon(Icons.explore, color: Colors.green, size: 28),
            const SizedBox(width: 10),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(widget.auth.partner?.nomeNegocio ?? 'Guia Turista', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
              const Text('Guia Turistico', style: TextStyle(color: AppTheme.dark400, fontSize: 12)),
            ])),
            if (widget.auth.partner != null)
              StatusBadge(label: widget.auth.partner!.status, variant: widget.auth.partner!.isAprovado ? 'success' : 'warning'),
          ]),
          const SizedBox(height: 20),
          Row(children: [
            Expanded(child: StatCard(label: 'Experiencias', value: '$_totalExp', icon: Icons.explore, color: Colors.green)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(label: 'Reservas', value: '$_totalBookings', icon: Icons.book_online, color: AppTheme.primary)),
          ]),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(child: StatCard(label: 'Receita', value: '0 Kz', icon: Icons.trending_up, color: AppTheme.success)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(label: 'Avaliacao', value: '4.8', icon: Icons.star, color: AppTheme.accent)),
          ]),
        ]),
      ),
    );
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

  void _showCreateDialog() {
    final tituloCtrl = TextEditingController();
    final localCtrl = TextEditingController();
    final cidadeCtrl = TextEditingController(text: 'Luanda');
    final precoCtrl = TextEditingController();
    final duracaoCtrl = TextEditingController(text: '3');

    showDialog(context: context, builder: (ctx) => AlertDialog(
      backgroundColor: AppTheme.dark800,
      title: const Text('Nova Experiencia', style: TextStyle(color: Colors.white)),
      content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [
        _DField(ctrl: tituloCtrl, label: 'Titulo'),
        _DField(ctrl: localCtrl, label: 'Local'),
        _DField(ctrl: cidadeCtrl, label: 'Cidade'),
        _DField(ctrl: precoCtrl, label: 'Preco (Kz)', keyboard: TextInputType.number),
        _DField(ctrl: duracaoCtrl, label: 'Duracao (horas)', keyboard: TextInputType.number),
      ])),
      actions: [
        TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar', style: TextStyle(color: AppTheme.dark400))),
        ElevatedButton(onPressed: () async {
          if (tituloCtrl.text.length < 3 || localCtrl.text.length < 2) return;
          Navigator.pop(ctx);
          try {
            await widget.svc.createExperience({
              'titulo': tituloCtrl.text,
              'local': localCtrl.text,
              'cidade': cidadeCtrl.text,
              'preco': double.tryParse(precoCtrl.text) ?? 0,
              'duracao_horas': int.tryParse(duracaoCtrl.text) ?? 3,
            });
            _load();
            if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Experiencia criada!'), backgroundColor: AppTheme.success));
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
          const Text('Experiencias', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
          ElevatedButton.icon(icon: const Icon(Icons.add, size: 18), label: const Text('Criar'), onPressed: _showCreateDialog),
        ]),
        const SizedBox(height: 12),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(color: Colors.green))
              : _exps.isEmpty
                  ? const EmptyState(icon: Icons.explore, title: 'Sem experiencias', subtitle: 'Crie a sua primeira experiencia turistica')
                  : RefreshIndicator(onRefresh: _load, child: ListView.builder(
                      itemCount: _exps.length,
                      itemBuilder: (ctx, i) {
                        final e = _exps[i];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: TCard(child: Row(children: [
                            Container(
                              width: 44, height: 44,
                              decoration: BoxDecoration(color: Colors.green.withOpacity(0.1), borderRadius: BorderRadius.circular(10)),
                              child: const Icon(Icons.flight, color: Colors.green, size: 20),
                            ),
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

class _ReservasTab extends StatefulWidget {
  final ModuleService svc;
  const _ReservasTab({required this.svc});
  @override
  State<_ReservasTab> createState() => _ReservasTabState();
}

class _ReservasTabState extends State<_ReservasTab> {
  List<dynamic> _bookings = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try { _bookings = await widget.svc.listMyTurismoBookings(); } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Reservas', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
        const SizedBox(height: 12),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
              : _bookings.isEmpty
                  ? const EmptyState(icon: Icons.book_online, title: 'Sem reservas', subtitle: 'As reservas dos clientes aparecerao aqui')
                  : RefreshIndicator(onRefresh: _load, child: ListView.builder(
                      itemCount: _bookings.length,
                      itemBuilder: (ctx, i) {
                        final b = _bookings[i];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: TCard(child: Row(children: [
                            const Icon(Icons.book_online, color: AppTheme.primary),
                            const SizedBox(width: 12),
                            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                              Text('Reserva #${(b['id'] ?? '').toString().substring(0, 8)}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                              Text('${b['adultos'] ?? 0} adultos - ${b['total']?.toStringAsFixed(0) ?? '0'} Kz', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
                            ])),
                            StatusBadge(label: b['status'] ?? '', variant: b['status'] == 'confirmada' ? 'success' : 'warning'),
                          ])),
                        );
                      },
                    )),
        ),
      ]),
    ));
  }
}

class _DField extends StatelessWidget {
  final TextEditingController ctrl;
  final String label;
  final TextInputType? keyboard;
  const _DField({required this.ctrl, required this.label, this.keyboard});
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
          CircleAvatar(radius: 28, backgroundColor: Colors.green, child: const Icon(Icons.explore, color: Colors.white)),
          const SizedBox(width: 14),
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(user?.nome ?? 'Guia', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            Text(user?.telefone ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 13)),
            const StatusBadge(label: 'Guia Turista', variant: 'success'),
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
