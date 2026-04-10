import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/auth_service.dart';
import '../../widgets/common.dart';

/// Home partilhado pelos Agentes (Imobiliario + Viagem)
class AgenteHome extends StatefulWidget {
  final String tipoAgente; // 'agente_imobiliario' ou 'agente_viagem'
  const AgenteHome({super.key, required this.tipoAgente});

  @override
  State<AgenteHome> createState() => _AgenteHomeState();
}

class _AgenteHomeState extends State<AgenteHome> {
  int _currentIndex = 0;

  bool get isImobiliario => widget.tipoAgente == 'agente_imobiliario';
  String get titulo => isImobiliario ? 'Agente Imobiliario' : 'Agente de Viagem';
  IconData get mainIcon => isImobiliario ? Icons.apartment : Icons.flight_takeoff;
  Color get mainColor => isImobiliario ? Colors.purple : Colors.teal;
  String get itemLabel => isImobiliario ? 'Imoveis' : 'Pacotes';

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();

    return Scaffold(
      body: [
        _DashboardTab(titulo: titulo, icon: mainIcon, color: mainColor, itemLabel: itemLabel, auth: auth),
        EmptyState(icon: mainIcon, title: itemLabel, subtitle: 'Gerir $itemLabel'),
        const EmptyState(icon: Icons.people, title: 'Clientes', subtitle: 'Gestao de clientes'),
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

class _DashboardTab extends StatelessWidget {
  final String titulo;
  final IconData icon;
  final Color color;
  final String itemLabel;
  final AuthService auth;
  const _DashboardTab({required this.titulo, required this.icon, required this.color, required this.itemLabel, required this.auth});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Icon(icon, color: color, size: 28),
              const SizedBox(width: 10),
              Expanded(child: Text(titulo, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22))),
              if (auth.partner != null) StatusBadge(label: auth.partner!.status, variant: auth.partner!.isAprovado ? 'success' : 'warning'),
            ]),
            const SizedBox(height: 20),
            Row(children: [
              Expanded(child: StatCard(label: itemLabel, value: '0', icon: icon, color: color)),
              const SizedBox(width: 12),
              Expanded(child: StatCard(label: 'Clientes', value: '0', icon: Icons.people, color: AppTheme.info)),
            ]),
            const SizedBox(height: 12),
            Row(children: [
              Expanded(child: StatCard(label: 'Receita Mes', value: '0 Kz', icon: Icons.account_balance_wallet, color: AppTheme.success)),
              const SizedBox(width: 12),
              Expanded(child: StatCard(label: 'Avaliacao', value: '4.6', icon: Icons.star, color: AppTheme.accent)),
            ]),
          ],
        ),
      ),
    );
  }
}

class _ProfileTab extends StatelessWidget {
  final dynamic user;
  final String titulo;
  const _ProfileTab({this.user, required this.titulo});
  @override
  Widget build(BuildContext context) => SafeArea(
    child: Padding(padding: const EdgeInsets.all(20), child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 20),
        Text('Perfil $titulo', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
        const Spacer(),
        SizedBox(width: double.infinity, child: OutlinedButton.icon(
          onPressed: () => context.read<AuthService>().logout(),
          icon: const Icon(Icons.logout, color: AppTheme.danger),
          label: const Text('Sair', style: TextStyle(color: AppTheme.danger)),
        )),
      ],
    )),
  );
}
