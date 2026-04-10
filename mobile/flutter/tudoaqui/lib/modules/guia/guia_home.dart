import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/auth_service.dart';
import '../../widgets/common.dart';

/// Home do Guia Turista - Experiencias e tours
class GuiaHome extends StatefulWidget {
  const GuiaHome({super.key});

  @override
  State<GuiaHome> createState() => _GuiaHomeState();
}

class _GuiaHomeState extends State<GuiaHome> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();

    return Scaffold(
      body: [
        _DashboardTab(auth: auth),
        const _ExperienciasTab(),
        const _ReservasTab(),
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

class _DashboardTab extends StatelessWidget {
  final AuthService auth;
  const _DashboardTab({required this.auth});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              const Icon(Icons.flight, color: Colors.green, size: 28),
              const SizedBox(width: 10),
              const Expanded(child: Text('Guia Turista', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22))),
              if (auth.partner != null) StatusBadge(label: auth.partner!.status, variant: auth.partner!.isAprovado ? 'success' : 'warning'),
            ]),
            const SizedBox(height: 20),
            Row(children: [
              Expanded(child: StatCard(label: 'Experiencias', value: '0', icon: Icons.explore, color: Colors.green)),
              const SizedBox(width: 12),
              Expanded(child: StatCard(label: 'Reservas', value: '0', icon: Icons.book_online, color: AppTheme.info)),
            ]),
            const SizedBox(height: 12),
            Row(children: [
              Expanded(child: StatCard(label: 'Receita Mes', value: '0 Kz', icon: Icons.account_balance_wallet, color: AppTheme.success)),
              const SizedBox(width: 12),
              Expanded(child: StatCard(label: 'Avaliacao', value: '4.7', icon: Icons.star, color: AppTheme.accent)),
            ]),
          ],
        ),
      ),
    );
  }
}

class _ExperienciasTab extends StatelessWidget {
  const _ExperienciasTab();
  @override
  Widget build(BuildContext context) => SafeArea(child: Padding(
    padding: const EdgeInsets.all(20),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
        const Text('Experiencias', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
        ElevatedButton.icon(icon: const Icon(Icons.add, size: 18), label: const Text('Criar'), onPressed: () {}),
      ]),
      const Expanded(child: EmptyState(icon: Icons.explore, title: 'Sem experiencias', subtitle: 'Crie tours e experiencias turisticas')),
    ]),
  ));
}

class _ReservasTab extends StatelessWidget {
  const _ReservasTab();
  @override
  Widget build(BuildContext context) => const SafeArea(child: EmptyState(icon: Icons.book_online, title: 'Reservas', subtitle: 'Gestao de reservas de turistas'));
}

class _ProfileTab extends StatelessWidget {
  final dynamic user;
  const _ProfileTab({this.user});
  @override
  Widget build(BuildContext context) => SafeArea(
    child: Padding(padding: const EdgeInsets.all(20), child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 20),
        const Text('Perfil Guia', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
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
