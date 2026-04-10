import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/auth_service.dart';
import '../../widgets/common.dart';

/// Home do Proprietario - Gerir loja/restaurante/alojamento
class ProprietarioHome extends StatefulWidget {
  const ProprietarioHome({super.key});

  @override
  State<ProprietarioHome> createState() => _ProprietarioHomeState();
}

class _ProprietarioHomeState extends State<ProprietarioHome> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();

    return Scaffold(
      body: [
        _DashboardTab(auth: auth),
        const _PedidosTab(),
        const _ProdutosTab(),
        _ProfileTab(user: auth.user),
      ][_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.dashboard_rounded), label: 'Dashboard'),
          BottomNavigationBarItem(icon: Icon(Icons.receipt_long), label: 'Pedidos'),
          BottomNavigationBarItem(icon: Icon(Icons.inventory_2), label: 'Produtos'),
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
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.store, color: AppTheme.primary, size: 28),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(auth.partner?.nomeNegocio ?? 'Meu Negocio', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
                      Text(auth.partner?.tipoLabel ?? 'Proprietario', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
                    ],
                  ),
                ),
                if (auth.partner != null)
                  StatusBadge(label: auth.partner!.status, variant: auth.partner!.isAprovado ? 'success' : 'warning'),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(child: StatCard(label: 'Pedidos Hoje', value: '0', icon: Icons.receipt_long, color: AppTheme.primary)),
                const SizedBox(width: 12),
                Expanded(child: StatCard(label: 'Receita Hoje', value: '0 Kz', icon: Icons.trending_up, color: AppTheme.success)),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: StatCard(label: 'Produtos', value: '0', icon: Icons.inventory_2, color: AppTheme.info)),
                const SizedBox(width: 12),
                Expanded(child: StatCard(label: 'Avaliacao', value: '4.5', icon: Icons.star, color: AppTheme.accent)),
              ],
            ),
            const SizedBox(height: 24),
            const Text('Ultimos Pedidos', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 12),
            const EmptyState(icon: Icons.receipt_long, title: 'Sem pedidos', subtitle: 'Os pedidos dos clientes aparecerão aqui'),
          ],
        ),
      ),
    );
  }
}

class _PedidosTab extends StatelessWidget {
  const _PedidosTab();
  @override
  Widget build(BuildContext context) => const SafeArea(child: EmptyState(icon: Icons.receipt_long, title: 'Pedidos', subtitle: 'Gestao de pedidos'));
}

class _ProdutosTab extends StatelessWidget {
  const _ProdutosTab();
  @override
  Widget build(BuildContext context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Produtos', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
                  ElevatedButton.icon(icon: const Icon(Icons.add, size: 18), label: const Text('Adicionar'), onPressed: () {}),
                ],
              ),
              const Expanded(child: EmptyState(icon: Icons.inventory_2, title: 'Sem produtos', subtitle: 'Adicione produtos ao seu catalogo')),
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
              const Text('Perfil', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
              const SizedBox(height: 20),
              TCard(child: Row(children: [
                CircleAvatar(radius: 28, backgroundColor: AppTheme.primary, child: const Icon(Icons.store, color: Colors.white)),
                const SizedBox(width: 14),
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(user?.nome ?? 'Proprietario', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
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
