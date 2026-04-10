import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/auth_service.dart';
import '../../widgets/common.dart';

/// Home do Motoqueiro - Dashboard de entregas
class MotoqueiroHome extends StatefulWidget {
  const MotoqueiroHome({super.key});

  @override
  State<MotoqueiroHome> createState() => _MotoqueiroHomeState();
}

class _MotoqueiroHomeState extends State<MotoqueiroHome> {
  int _currentIndex = 0;
  bool _online = false;

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();

    return Scaffold(
      body: [
        _MotoqueiroMainTab(online: _online, onToggle: (v) => setState(() => _online = v), auth: auth),
        const _EntregasTab(),
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

class _MotoqueiroMainTab extends StatelessWidget {
  final bool online;
  final ValueChanged<bool> onToggle;
  final AuthService auth;
  const _MotoqueiroMainTab({required this.online, required this.onToggle, required this.auth});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.two_wheeler, color: AppTheme.accent, size: 28),
                const SizedBox(width: 10),
                const Expanded(child: Text('Motoqueiro', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22))),
                GestureDetector(
                  onTap: () => onToggle(!online),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                    decoration: BoxDecoration(
                      color: online ? AppTheme.success.withOpacity(0.15) : AppTheme.dark700,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: online ? AppTheme.success : AppTheme.dark600),
                    ),
                    child: Text(online ? 'Online' : 'Offline', style: TextStyle(color: online ? AppTheme.success : AppTheme.dark400, fontWeight: FontWeight.w600, fontSize: 13)),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(child: StatCard(label: 'Entregas Hoje', value: '0', icon: Icons.local_shipping, color: AppTheme.primary)),
                const SizedBox(width: 12),
                Expanded(child: StatCard(label: 'Ganhos Hoje', value: '0 Kz', icon: Icons.account_balance_wallet, color: AppTheme.success)),
              ],
            ),
            const SizedBox(height: 20),
            if (!online)
              const EmptyState(icon: Icons.power_settings_new, title: 'Offline', subtitle: 'Active para receber pedidos de entrega')
            else
              TCard(
                child: Column(
                  children: [
                    const CircularProgressIndicator(color: AppTheme.accent, strokeWidth: 3),
                    const SizedBox(height: 12),
                    const Text('A procurar entregas...', style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _EntregasTab extends StatelessWidget {
  const _EntregasTab();
  @override
  Widget build(BuildContext context) => const SafeArea(child: EmptyState(icon: Icons.local_shipping, title: 'Sem entregas', subtitle: 'Historico de entregas'));
}

class _GanhosTab extends StatelessWidget {
  const _GanhosTab();
  @override
  Widget build(BuildContext context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Ganhos', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
              const SizedBox(height: 20),
              TCard(child: Column(children: [
                const Text('Saldo', style: TextStyle(color: AppTheme.dark400, fontSize: 12)),
                const SizedBox(height: 8),
                const Text('0 Kz', style: TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 32)),
              ])),
            ],
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
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 20),
              const Text('Perfil Motoqueiro', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
              const SizedBox(height: 20),
              TCard(child: Row(children: [
                CircleAvatar(radius: 28, backgroundColor: AppTheme.accent, child: const Icon(Icons.two_wheeler, color: Colors.black)),
                const SizedBox(width: 14),
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(user?.nome ?? 'Motoqueiro', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                  Text(user?.telefone ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 13)),
                ]),
              ])),
              const Spacer(),
              SizedBox(width: double.infinity, child: OutlinedButton.icon(
                onPressed: () => context.read<AuthService>().logout(),
                icon: const Icon(Icons.logout, color: AppTheme.danger),
                label: const Text('Sair', style: TextStyle(color: AppTheme.danger)),
              )),
            ],
          ),
        ),
      );
}
