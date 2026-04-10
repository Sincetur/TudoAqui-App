import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/auth_service.dart';
import '../../services/module_service.dart';
import '../../services/location_service.dart';
import '../../widgets/common.dart';

class MotoqueiroHome extends StatefulWidget {
  const MotoqueiroHome({super.key});
  @override
  State<MotoqueiroHome> createState() => _MotoqueiroHomeState();
}

class _MotoqueiroHomeState extends State<MotoqueiroHome> {
  int _currentIndex = 0;
  bool _online = false;
  final _svc = ModuleService();
  final _locSvc = LocationService();

  void _toggleOnline(bool v) {
    setState(() => _online = v);
    if (v) {
      _locSvc.startTracking(onPosition: (_) {});
    } else {
      _locSvc.stopTracking();
    }
  }

  @override
  void dispose() {
    _locSvc.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    return Scaffold(
      body: [
        _MotoqueiroMainTab(online: _online, onToggle: _toggleOnline, auth: auth),
        _EntregasTab(svc: _svc, online: _online, locSvc: _locSvc),
        const _GanhosTab(),
        _ProfileTab(user: auth.user),
      ][_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home_rounded), label: 'Inicio'),
          BottomNavigationBarItem(icon: Icon(Icons.local_shipping), label: 'Entregas'),
          BottomNavigationBarItem(icon: Icon(Icons.account_balance_wallet), label: 'Ganhos'),
          BottomNavigationBarItem(icon: Icon(Icons.person_rounded), label: 'Perfil'),
        ],
      ),
    );
  }
}

class _MotoqueiroMainTab extends StatefulWidget {
  final bool online;
  final ValueChanged<bool> onToggle;
  final AuthService auth;
  const _MotoqueiroMainTab({required this.online, required this.onToggle, required this.auth});
  @override
  State<_MotoqueiroMainTab> createState() => _MotoqueiroMainTabState();
}

class _MotoqueiroMainTabState extends State<_MotoqueiroMainTab> {
  final _svc = ModuleService();
  int _entregasHoje = 0;
  int _totalEntregas = 0;
  String _ganhos = '0';
  String _avaliacao = '--';

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    try {
      final entregas = await _svc.listMyDeliveries();
      final hoje = DateTime.now();
      int hojeCont = 0;
      for (final e in entregas) {
        final dt = e['created_at'] ?? '';
        if (dt.toString().startsWith('${hoje.year}-${hoje.month.toString().padLeft(2, '0')}-${hoje.day.toString().padLeft(2, '0')}')) {
          hojeCont++;
        }
      }
      if (mounted) setState(() {
        _totalEntregas = entregas.length;
        _entregasHoje = hojeCont;
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
            const Expanded(child: Text('Motoqueiro', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22))),
            GestureDetector(
              onTap: () => onToggle(!online),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: online ? AppTheme.success.withOpacity(0.15) : AppTheme.dark700,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: online ? AppTheme.success : AppTheme.dark600),
                ),
                child: Row(mainAxisSize: MainAxisSize.min, children: [
                  Container(width: 8, height: 8, decoration: BoxDecoration(color: online ? AppTheme.success : AppTheme.dark500, shape: BoxShape.circle)),
                  const SizedBox(width: 8),
                  Text(online ? 'Online' : 'Offline', style: TextStyle(color: online ? AppTheme.success : AppTheme.dark400, fontWeight: FontWeight.w600, fontSize: 13)),
                ]),
              ),
            ),
          ]),
          const SizedBox(height: 20),
          Row(children: [
            Expanded(child: StatCard(label: 'Entregas Hoje', value: '$_entregasHoje', icon: Icons.local_shipping, color: Colors.orange)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(label: 'Ganhos Hoje', value: '$_ganhos Kz', icon: Icons.account_balance_wallet, color: AppTheme.success)),
          ]),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(child: StatCard(label: 'Avaliacao', value: _avaliacao, icon: Icons.star, color: AppTheme.accent)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(label: 'Total', value: '$_totalEntregas', icon: Icons.check_circle, color: AppTheme.info)),
          ]),
          const SizedBox(height: 24),
          if (!online)
            TCard(child: Column(children: [
              const Icon(Icons.power_settings_new, size: 48, color: AppTheme.dark500),
              const SizedBox(height: 12),
              const Text('Voce esta offline', style: TextStyle(color: AppTheme.dark400, fontSize: 14)),
              const SizedBox(height: 4),
              const Text('Active para receber entregas', style: TextStyle(color: AppTheme.dark500, fontSize: 12)),
              const SizedBox(height: 16),
              PrimaryButton(label: 'Ficar Online', onPressed: () => onToggle(true), icon: Icons.wifi),
            ])),
          if (auth.partner != null) ...[
            const SizedBox(height: 16),
            TCard(child: Row(children: [
              Icon(auth.partner!.isAprovado ? Icons.verified : Icons.pending, color: auth.partner!.isAprovado ? AppTheme.success : AppTheme.warning),
              const SizedBox(width: 12),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(auth.partner!.nomeNegocio, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                Text(auth.partner!.isAprovado ? 'Parceiro aprovado' : 'Aguardando aprovacao', style: TextStyle(color: auth.partner!.isAprovado ? AppTheme.success : AppTheme.warning, fontSize: 12)),
              ])),
            ])),
          ],
        ]),
      ),
    );
  }
}

class _EntregasTab extends StatefulWidget {
  final ModuleService svc;
  final bool online;
  final LocationService locSvc;
  const _EntregasTab({required this.svc, required this.online, required this.locSvc});
  @override
  State<_EntregasTab> createState() => _EntregasTabState();
}

class _EntregasTabState extends State<_EntregasTab> {
  List<dynamic> _pendingDeliveries = [];
  Map<String, dynamic>? _activeDelivery;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final pos = await widget.locSvc.getCurrentPosition();
      if (pos != null && widget.online) {
        _pendingDeliveries = await widget.svc.listPendingDeliveries(pos.latitude, pos.longitude);
      }
    } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _accept(Map<String, dynamic> d) async {
    try {
      final result = await widget.svc.acceptDelivery(d['id'].toString());
      setState(() {
        _activeDelivery = result;
        _pendingDeliveries.removeWhere((e) => e['id'] == d['id']);
      });
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Entrega aceite!'), backgroundColor: AppTheme.success));
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e'), backgroundColor: AppTheme.danger));
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
          const Text('Entregas', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
          IconButton(icon: const Icon(Icons.refresh, color: AppTheme.dark400), onPressed: _load),
        ]),
        const SizedBox(height: 12),
        if (_activeDelivery != null) ...[
          TCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              const Icon(Icons.local_shipping, color: Colors.orange), const SizedBox(width: 8),
              const Expanded(child: Text('Entrega Ativa', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold))),
              const StatusBadge(label: 'Em curso', variant: 'primary'),
            ]),
            const SizedBox(height: 8),
            Row(children: [const Icon(Icons.circle, size: 8, color: AppTheme.success), const SizedBox(width: 6),
              Expanded(child: Text(_activeDelivery!['origem_endereco'] ?? '', style: const TextStyle(color: AppTheme.dark300, fontSize: 13)))]),
            const SizedBox(height: 4),
            Row(children: [const Icon(Icons.place, size: 8, color: AppTheme.primary), const SizedBox(width: 6),
              Expanded(child: Text(_activeDelivery!['destino_endereco'] ?? '', style: const TextStyle(color: AppTheme.dark300, fontSize: 13)))]),
          ])),
          const SizedBox(height: 16),
        ],
        if (!widget.online) ...[
          const EmptyState(icon: Icons.wifi_off, title: 'Offline', subtitle: 'Fique online para ver entregas pendentes'),
        ] else ...[
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator(color: Colors.orange))
                : _pendingDeliveries.isEmpty
                    ? const EmptyState(icon: Icons.local_shipping, title: 'Sem entregas', subtitle: 'Nenhuma entrega pendente na sua zona')
                    : ListView.builder(
                        itemCount: _pendingDeliveries.length,
                        itemBuilder: (ctx, i) {
                          final d = _pendingDeliveries[i];
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: TCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                              Row(children: [
                                Expanded(child: Text(d['descricao'] ?? 'Entrega', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600))),
                                Text('${(d['valor_estimado'] ?? 0).toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold)),
                              ]),
                              const SizedBox(height: 4),
                              Row(children: [const Icon(Icons.circle, size: 8, color: AppTheme.success), const SizedBox(width: 6),
                                Expanded(child: Text(d['origem_endereco'] ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)))]),
                              Row(children: [const Icon(Icons.place, size: 8, color: AppTheme.primary), const SizedBox(width: 6),
                                Expanded(child: Text(d['destino_endereco'] ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)))]),
                              const SizedBox(height: 8),
                              SizedBox(width: double.infinity, child: ElevatedButton(onPressed: () => _accept(d), child: const Text('Aceitar'))),
                            ])),
                          );
                        },
                      ),
          ),
        ],
      ]),
    ));
  }
}

class _GanhosTab extends StatelessWidget {
  const _GanhosTab();
  @override
  Widget build(BuildContext context) => SafeArea(
    child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Ganhos', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
        const SizedBox(height: 20),
        TCard(child: Column(children: [
          const Text('Saldo Total', style: TextStyle(color: AppTheme.dark400, fontSize: 12)),
          const SizedBox(height: 8),
          const Text('0 Kz', style: TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 32)),
          const SizedBox(height: 16),
          Row(children: [
            Expanded(child: StatCard(label: 'Hoje', value: '0 Kz', icon: Icons.today, color: AppTheme.success)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(label: 'Este Mes', value: '0 Kz', icon: Icons.date_range, color: AppTheme.info)),
          ]),
        ])),
      ]),
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
          CircleAvatar(radius: 28, backgroundColor: Colors.orange, child: const Icon(Icons.two_wheeler, color: Colors.white)),
          const SizedBox(width: 14),
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(user?.nome ?? 'Motoqueiro', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            Text(user?.telefone ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 13)),
            const StatusBadge(label: 'Motoqueiro', variant: 'warning'),
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
