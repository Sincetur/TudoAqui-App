import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/auth_service.dart';
import '../../services/api_service.dart';
import '../../config/api_config.dart';
import '../../widgets/common.dart';

/// Home do Cliente - Dashboard principal com todos os modulos
class ClienteHome extends StatefulWidget {
  const ClienteHome({super.key});

  @override
  State<ClienteHome> createState() => _ClienteHomeState();
}

class _ClienteHomeState extends State<ClienteHome> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    final user = auth.user;

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: [
          _DashboardTab(user: user),
          const _ExploreTab(),
          const _PaymentsTab(),
          _ProfileTab(user: user),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home_rounded), label: 'Inicio'),
          BottomNavigationBarItem(icon: Icon(Icons.explore_rounded), label: 'Explorar'),
          BottomNavigationBarItem(icon: Icon(Icons.payment_rounded), label: 'Pagamentos'),
          BottomNavigationBarItem(icon: Icon(Icons.person_rounded), label: 'Perfil'),
        ],
      ),
    );
  }
}

class _DashboardTab extends StatelessWidget {
  final dynamic user;
  const _DashboardTab({this.user});

  @override
  Widget build(BuildContext context) {
    final modules = [
      _ModuleItem('Eventos', Icons.event, AppTheme.primary, '/events'),
      _ModuleItem('Marketplace', Icons.shopping_bag, AppTheme.accent, '/marketplace'),
      _ModuleItem('Alojamento', Icons.hotel, Colors.blue, '/alojamento'),
      _ModuleItem('Turismo', Icons.flight, Colors.green, '/turismo'),
      _ModuleItem('Imobiliario', Icons.apartment, Colors.purple, '/realestate'),
      _ModuleItem('Entregas', Icons.local_shipping, Colors.orange, '/entregas'),
      _ModuleItem('Restaurantes', Icons.restaurant, Colors.red, '/restaurantes'),
      _ModuleItem('Taxi', Icons.local_taxi, AppTheme.accent, '/taxi'),
    ];

    return SafeArea(
      child: CustomScrollView(
        slivers: [
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
              child: Row(
                children: [
                  Container(
                    width: 44, height: 44,
                    decoration: BoxDecoration(color: AppTheme.primary, borderRadius: BorderRadius.circular(14)),
                    child: const Center(child: Text('T', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20))),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Ola, ${user?.nome ?? 'Utilizador'}!', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                        Text(user?.roleLabel ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.notifications_outlined, color: AppTheme.dark400),
                    onPressed: () {},
                  ),
                ],
              ),
            ),
          ),
          // Search bar
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: AppTheme.dark800,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppTheme.dark700),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.search, color: AppTheme.dark500, size: 20),
                    SizedBox(width: 10),
                    Text('Pesquisar em TUDOaqui...', style: TextStyle(color: AppTheme.dark500, fontSize: 14)),
                  ],
                ),
              ),
            ),
          ),
          // Module grid
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            sliver: SliverGrid(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 4,
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 0.8,
              ),
              delegate: SliverChildBuilderDelegate(
                (context, index) {
                  final m = modules[index];
                  return GestureDetector(
                    onTap: () {},
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 52, height: 52,
                          decoration: BoxDecoration(
                            color: m.color.withOpacity(0.12),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Icon(m.icon, color: m.color, size: 24),
                        ),
                        const SizedBox(height: 6),
                        Text(m.label, style: const TextStyle(color: AppTheme.dark300, fontSize: 11), textAlign: TextAlign.center, maxLines: 1, overflow: TextOverflow.ellipsis),
                      ],
                    ),
                  );
                },
                childCount: modules.length,
              ),
            ),
          ),
          const SliverToBoxAdapter(child: SizedBox(height: 24)),
          // Quick actions
          const SliverToBoxAdapter(
            child: Padding(
              padding: EdgeInsets.symmetric(horizontal: 20),
              child: Text('Destaques', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            ),
          ),
          const SliverToBoxAdapter(child: SizedBox(height: 12)),
          SliverToBoxAdapter(
            child: SizedBox(
              height: 120,
              child: ListView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 20),
                children: [
                  _PromoCard('Eventos em Luanda', 'Descubra os melhores eventos', AppTheme.primary),
                  _PromoCard('Novos Restaurantes', 'Comida angolana deliciosa', Colors.orange),
                  _PromoCard('Alojamento', 'Quartos a partir de 5.000 Kz', Colors.blue),
                ],
              ),
            ),
          ),
          const SliverToBoxAdapter(child: SizedBox(height: 100)),
        ],
      ),
    );
  }
}

class _ExploreTab extends StatelessWidget {
  const _ExploreTab();

  @override
  Widget build(BuildContext context) {
    return const SafeArea(
      child: Center(
        child: EmptyState(icon: Icons.explore, title: 'Explorar', subtitle: 'Descubra tudo em Angola'),
      ),
    );
  }
}

class _PaymentsTab extends StatelessWidget {
  const _PaymentsTab();

  @override
  Widget build(BuildContext context) {
    return const SafeArea(
      child: Center(
        child: EmptyState(icon: Icons.payment, title: 'Pagamentos', subtitle: 'O seu historico de pagamentos'),
      ),
    );
  }
}

class _ProfileTab extends StatelessWidget {
  final dynamic user;
  const _ProfileTab({this.user});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 20),
            const Text('Perfil', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
            const SizedBox(height: 20),
            TCard(
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: AppTheme.primary,
                    child: Text(
                      (user?.nome ?? 'U')[0].toUpperCase(),
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(user?.nome ?? 'Utilizador', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                        Text(user?.telefone ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 13)),
                        StatusBadge(label: user?.roleLabel ?? 'Cliente', variant: 'primary'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const Spacer(),
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

class _ModuleItem {
  final String label;
  final IconData icon;
  final Color color;
  final String route;
  _ModuleItem(this.label, this.icon, this.color, this.route);
}

class _PromoCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final Color color;
  const _PromoCard(this.title, this.subtitle, this.color);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 220,
      margin: const EdgeInsets.only(right: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(colors: [color, color.withOpacity(0.7)]),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
          const SizedBox(height: 4),
          Text(subtitle, style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 12)),
        ],
      ),
    );
  }
}
