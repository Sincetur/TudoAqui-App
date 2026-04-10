import 'package:flutter/material.dart';
import '../config/theme.dart';

/// Badge de status reutilizavel
class StatusBadge extends StatelessWidget {
  final String label;
  final String variant;

  const StatusBadge({super.key, required this.label, this.variant = 'default'});

  @override
  Widget build(BuildContext context) {
    final colors = {
      'success': (AppTheme.success.withOpacity(0.15), AppTheme.success),
      'warning': (AppTheme.warning.withOpacity(0.15), AppTheme.warning),
      'danger': (AppTheme.danger.withOpacity(0.15), AppTheme.danger),
      'primary': (AppTheme.primary.withOpacity(0.15), AppTheme.primary),
      'accent': (AppTheme.accent.withOpacity(0.15), AppTheme.accent),
      'default': (AppTheme.dark700, AppTheme.dark400),
    };
    final (bg, fg) = colors[variant] ?? colors['default']!;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(label, style: TextStyle(color: fg, fontSize: 11, fontWeight: FontWeight.w600)),
    );
  }
}

/// Card customizado TUDOaqui
class TCard extends StatelessWidget {
  final Widget child;
  final VoidCallback? onTap;
  final EdgeInsets? padding;

  const TCard({super.key, required this.child, this.onTap, this.padding});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: padding ?? const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppTheme.dark800,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.dark700),
        ),
        child: child,
      ),
    );
  }
}

/// Stat card para dashboards
class StatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const StatCard({
    super.key,
    required this.label,
    required this.value,
    required this.icon,
    this.color = AppTheme.primary,
  });

  @override
  Widget build(BuildContext context) {
    return TCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: color),
              const SizedBox(width: 6),
              Text(label, style: const TextStyle(color: AppTheme.dark400, fontSize: 11)),
            ],
          ),
          const SizedBox(height: 8),
          Text(value, style: TextStyle(color: color, fontSize: 22, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}

/// Botao de accao principal
class PrimaryButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final bool loading;
  final IconData? icon;

  const PrimaryButton({
    super.key,
    required this.label,
    this.onPressed,
    this.loading = false,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: loading ? null : onPressed,
        child: loading
            ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (icon != null) ...[Icon(icon, size: 18), const SizedBox(width: 8)],
                  Text(label),
                ],
              ),
      ),
    );
  }
}

/// Empty state
class EmptyState extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;

  const EmptyState({super.key, required this.icon, required this.title, this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 48, color: AppTheme.dark600),
            const SizedBox(height: 16),
            Text(title, style: const TextStyle(color: AppTheme.dark400, fontSize: 14, fontWeight: FontWeight.w600)),
            if (subtitle != null) ...[
              const SizedBox(height: 4),
              Text(subtitle!, style: const TextStyle(color: AppTheme.dark500, fontSize: 12), textAlign: TextAlign.center),
            ],
          ],
        ),
      ),
    );
  }
}

/// Formato de preco Kwanzas
String formatPrice(num value) => '${value.toStringAsFixed(0).replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (m) => '${m[1]}.')} Kz';
