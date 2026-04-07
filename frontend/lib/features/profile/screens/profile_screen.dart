import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/config/theme.dart';
import '../../../core/config/routes.dart';
import '../../auth/bloc/auth_bloc.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Minha Conta'),
      ),
      body: BlocBuilder<AuthBloc, AuthState>(
        builder: (context, state) {
          if (state is! AuthAuthenticated) {
            return const Center(child: CircularProgressIndicator());
          }
          
          final user = state.user;
          
          return SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                // Profile Header
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 10,
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      // Avatar
                      CircleAvatar(
                        radius: 50,
                        backgroundColor: AppColors.primary,
                        child: Text(
                          (user['nome'] ?? 'U')[0].toUpperCase(),
                          style: const TextStyle(
                            fontSize: 40,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      // Name
                      Text(
                        user['nome'] ?? 'Utilizador',
                        style: AppTypography.headline3,
                      ),
                      const SizedBox(height: 4),
                      
                      // Phone
                      Text(
                        user['telefone'] ?? '',
                        style: AppTypography.bodyMedium.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      // Edit button
                      OutlinedButton.icon(
                        onPressed: () {
                          // TODO: Navigate to edit profile
                        },
                        icon: const Icon(Icons.edit, size: 18),
                        label: const Text('Editar perfil'),
                        style: OutlinedButton.styleFrom(
                          minimumSize: const Size(200, 44),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                
                // Menu Options
                _buildMenuSection(
                  title: 'Conta',
                  items: [
                    _MenuItem(
                      icon: Icons.history,
                      title: 'Histórico de corridas',
                      onTap: () {
                        Navigator.pushNamed(context, AppRoutes.rideHistory);
                      },
                    ),
                    _MenuItem(
                      icon: Icons.account_balance_wallet,
                      title: 'Carteira',
                      onTap: () {
                        // TODO: Navigate to wallet
                      },
                    ),
                    _MenuItem(
                      icon: Icons.payment,
                      title: 'Métodos de pagamento',
                      onTap: () {
                        // TODO: Navigate to payment methods
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                
                _buildMenuSection(
                  title: 'Preferências',
                  items: [
                    _MenuItem(
                      icon: Icons.notifications,
                      title: 'Notificações',
                      onTap: () {
                        // TODO: Navigate to notifications settings
                      },
                    ),
                    _MenuItem(
                      icon: Icons.language,
                      title: 'Idioma',
                      subtitle: 'Português',
                      onTap: () {
                        // TODO: Language selector
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                
                _buildMenuSection(
                  title: 'Suporte',
                  items: [
                    _MenuItem(
                      icon: Icons.help_outline,
                      title: 'Ajuda',
                      onTap: () {
                        // TODO: Navigate to help
                      },
                    ),
                    _MenuItem(
                      icon: Icons.info_outline,
                      title: 'Sobre',
                      onTap: () {
                        _showAboutDialog(context);
                      },
                    ),
                    _MenuItem(
                      icon: Icons.description_outlined,
                      title: 'Termos e Privacidade',
                      onTap: () {
                        // TODO: Navigate to terms
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                
                // Logout button
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () => _confirmLogout(context),
                    icon: const Icon(Icons.logout, color: AppColors.error),
                    label: const Text('Sair'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppColors.error,
                      side: const BorderSide(color: AppColors.error),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                
                // Version
                Text(
                  'TUDOaqui v1.0.0',
                  style: AppTypography.caption,
                ),
              ],
            ),
          );
        },
      ),
    );
  }
  
  Widget _buildMenuSection({
    required String title,
    required List<_MenuItem> items,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: Text(
              title,
              style: AppTypography.bodySmall.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.textSecondary,
              ),
            ),
          ),
          ...items.map((item) => _buildMenuItem(item)),
        ],
      ),
    );
  }
  
  Widget _buildMenuItem(_MenuItem item) {
    return ListTile(
      leading: Icon(item.icon, color: AppColors.textSecondary),
      title: Text(item.title, style: AppTypography.bodyMedium),
      subtitle: item.subtitle != null
          ? Text(item.subtitle!, style: AppTypography.caption)
          : null,
      trailing: const Icon(
        Icons.chevron_right,
        color: AppColors.textSecondary,
      ),
      onTap: item.onTap,
    );
  }
  
  void _confirmLogout(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Sair'),
        content: const Text('Tem certeza que deseja sair da sua conta?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<AuthBloc>().add(AuthLogoutRequested());
              Navigator.pushNamedAndRemoveUntil(
                context,
                AppRoutes.login,
                (route) => false,
              );
            },
            style: TextButton.styleFrom(foregroundColor: AppColors.error),
            child: const Text('Sair'),
          ),
        ],
      ),
    );
  }
  
  void _showAboutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Center(
                child: Text('🚀', style: TextStyle(fontSize: 24)),
              ),
            ),
            const SizedBox(width: 12),
            const Text('TUDOaqui'),
          ],
        ),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('A sua vida, num só app.'),
            SizedBox(height: 16),
            Text('Versão: 1.0.0'),
            Text('© 2025 TUDOaqui'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Fechar'),
          ),
        ],
      ),
    );
  }
}

class _MenuItem {
  final IconData icon;
  final String title;
  final String? subtitle;
  final VoidCallback onTap;
  
  const _MenuItem({
    required this.icon,
    required this.title,
    this.subtitle,
    required this.onTap,
  });
}
