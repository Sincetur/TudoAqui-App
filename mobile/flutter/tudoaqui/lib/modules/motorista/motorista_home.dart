import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/auth_service.dart';
import '../../widgets/common.dart';

/// Home do Motorista - Dashboard de corridas
class MotoristaHome extends StatefulWidget {
  const MotoristaHome({super.key});

  @override
  State<MotoristaHome> createState() => _MotoristaHomeState();
}

class _MotoristaHomeState extends State<MotoristaHome> {
  int _currentIndex = 0;
  bool _online = false;

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: [
          _MotoristaMainTab(online: _online, onToggle: (v) => setState(() => _online = v)),
          const _CorridasTab(),
          const _GanhosTab(),
          _MotoristaProfileTab(user: auth.user, partner: auth.partner),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home_rounded), label: 'Inicio'),
          BottomNavigationBarItem(icon: Icon(Icons.route_rounded), label: 'Corridas'),
          BottomNavigationBarItem(icon: Icon(Icons.account_balance_wallet), label: 'Ganhos'),
          BottomNavigationBarItem(icon: Icon(Icons.person_rounded), label: 'Perfil'),
        ],
      ),
    );
  }
}

class _MotoristaMainTab extends StatelessWidget {
  final bool online;
  final ValueChanged<bool> onToggle;
  const _MotoristaMainTab({required this.online, required this.onToggle});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Expanded(
                  child: Text('Motorista', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
                ),
                // Online/Offline toggle
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
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 8, height: 8,
                          decoration: BoxDecoration(
                            color: online ? AppTheme.success : AppTheme.dark500,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          online ? 'Online' : 'Offline',
                          style: TextStyle(color: online ? AppTheme.success : AppTheme.dark400, fontWeight: FontWeight.w600, fontSize: 13),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Stats do dia
            Row(
              children: [
                Expanded(child: StatCard(label: 'Corridas Hoje', value: '0', icon: Icons.route, color: AppTheme.primary)),
                const SizedBox(width: 12),
                Expanded(child: StatCard(label: 'Ganhos Hoje', value: '0 Kz', icon: Icons.account_balance_wallet, color: AppTheme.success)),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: StatCard(label: 'Avaliacao', value: '4.8', icon: Icons.star, color: AppTheme.accent)),
                const SizedBox(width: 12),
                Expanded(child: StatCard(label: 'Taxa Aceite', value: '95%', icon: Icons.check_circle, color: AppTheme.info)),
              ],
            ),

            const SizedBox(height: 24),

            // Status
            if (!online)
              TCard(
                child: Column(
                  children: [
                    Icon(Icons.power_settings_new, size: 48, color: AppTheme.dark500),
                    const SizedBox(height: 12),
                    const Text('Voce esta offline', style: TextStyle(color: AppTheme.dark400, fontSize: 14)),
                    const SizedBox(height: 4),
                    const Text('Active o modo online para receber corridas', style: TextStyle(color: AppTheme.dark500, fontSize: 12)),
                    const SizedBox(height: 16),
                    PrimaryButton(label: 'Ficar Online', onPressed: () => onToggle(true), icon: Icons.wifi),
                  ],
                ),
              ),

            if (online)
              TCard(
                child: Column(
                  children: [
                    const CircularProgressIndicator(color: AppTheme.primary, strokeWidth: 3),
                    const SizedBox(height: 16),
                    const Text('A procurar corridas...', style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 4),
                    const Text('Mantenha o GPS ligado', style: TextStyle(color: AppTheme.dark400, fontSize: 12)),
                  ],
                ),
              ),

            // Partner status
            if (auth.partner != null) ...[
              const SizedBox(height: 16),
              TCard(
                child: Row(
                  children: [
                    Icon(
                      auth.partner!.isAprovado ? Icons.verified : Icons.pending,
                      color: auth.partner!.isAprovado ? AppTheme.success : AppTheme.warning,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(auth.partner!.nomeNegocio, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                          Text(
                            auth.partner!.isAprovado ? 'Parceiro aprovado' : 'Aguardando aprovacao',
                            style: TextStyle(color: auth.partner!.isAprovado ? AppTheme.success : AppTheme.warning, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                    StatusBadge(label: auth.partner!.status, variant: auth.partner!.isAprovado ? 'success' : 'warning'),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _CorridasTab extends StatelessWidget {
  const _CorridasTab();

  @override
  Widget build(BuildContext context) {
    return const SafeArea(
      child: EmptyState(icon: Icons.route, title: 'Sem corridas', subtitle: 'O historico de corridas aparecera aqui'),
    );
  }
}

class _GanhosTab extends StatelessWidget {
  const _GanhosTab();

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Ganhos', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
            const SizedBox(height: 20),
            TCard(
              child: Column(
                children: [
                  const Text('Saldo Disponivel', style: TextStyle(color: AppTheme.dark400, fontSize: 12)),
                  const SizedBox(height: 8),
                  const Text('0 Kz', style: TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 32)),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(child: StatCard(label: 'Hoje', value: '0 Kz', icon: Icons.today, color: AppTheme.success)),
                      const SizedBox(width: 12),
                      Expanded(child: StatCard(label: 'Semana', value: '0 Kz', icon: Icons.date_range, color: AppTheme.info)),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MotoristaProfileTab extends StatelessWidget {
  final dynamic user;
  final dynamic partner;
  const _MotoristaProfileTab({this.user, this.partner});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 20),
            const Text('Perfil Motorista', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
            const SizedBox(height: 20),
            TCard(
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: AppTheme.accent,
                    child: const Icon(Icons.local_taxi, color: Colors.black, size: 24),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(user?.nome ?? 'Motorista', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                        Text(user?.telefone ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 13)),
                        const StatusBadge(label: 'Motorista', variant: 'accent'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            // Quick settings
            ...[
              _SettingsItem(Icons.payment, 'Dados de Pagamento', () {}),
              _SettingsItem(Icons.car_rental, 'Dados do Veiculo', () {}),
              _SettingsItem(Icons.description, 'Documentos', () {}),
              _SettingsItem(Icons.support, 'Suporte', () {}),
            ],
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () => context.read<AuthService>().logout(),
                icon: const Icon(Icons.logout, color: AppTheme.danger),
                label: const Text('Terminar Sessao', style: TextStyle(color: AppTheme.danger)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SettingsItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  const _SettingsItem(this.icon, this.label, this.onTap);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: TCard(
        onTap: onTap,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(
          children: [
            Icon(icon, color: AppTheme.dark400, size: 20),
            const SizedBox(width: 14),
            Expanded(child: Text(label, style: const TextStyle(color: Colors.white, fontSize: 14))),
            const Icon(Icons.chevron_right, color: AppTheme.dark500, size: 20),
          ],
        ),
      ),
    );
  }
}
