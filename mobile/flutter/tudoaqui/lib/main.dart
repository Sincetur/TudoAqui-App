import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import 'config/theme.dart';
import 'services/auth_service.dart';
import 'modules/auth/login_screen.dart';
import 'modules/cliente/home_screen.dart';
import 'modules/motorista/motorista_home.dart';
import 'modules/motoqueiro/motoqueiro_home.dart';
import 'modules/proprietario/proprietario_home.dart';
import 'modules/guia/guia_home.dart';
import 'modules/common/agente_home.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: AppTheme.dark800,
  ));
  runApp(const TUDOaquiApp());
}

class TUDOaquiApp extends StatelessWidget {
  const TUDOaquiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AuthService(),
      child: MaterialApp(
        title: 'TUDOaqui',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.darkTheme,
        home: const AppGate(),
      ),
    );
  }
}

/// Gate que decide qual ecra mostrar baseado no estado de auth
class AppGate extends StatefulWidget {
  const AppGate({super.key});

  @override
  State<AppGate> createState() => _AppGateState();
}

class _AppGateState extends State<AppGate> {
  bool _checking = true;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final auth = context.read<AuthService>();
    await auth.tryAutoLogin();
    if (mounted) setState(() => _checking = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_checking) return const _SplashScreen();

    final auth = context.watch<AuthService>();
    if (!auth.isAuthenticated) return const LoginScreen();

    return _buildHomeForRole(auth.user!.role, auth);
  }

  Widget _buildHomeForRole(String role, AuthService auth) {
    switch (role) {
      case 'motorista':
        return const MotoristaHome();
      case 'motoqueiro':
        return const MotoqueiroHome();
      case 'proprietario':
        return const ProprietarioHome();
      case 'guia_turista':
        return const GuiaHome();
      case 'agente_imobiliario':
        return const AgenteHome(tipoAgente: 'agente_imobiliario');
      case 'agente_viagem':
        return const AgenteHome(tipoAgente: 'agente_viagem');
      case 'staff':
        return const ProprietarioHome(); // Staff usa mesma interface
      case 'admin':
        return const ClienteHome(); // Admin ve dashboard completo
      default:
        return const ClienteHome(); // Cliente
    }
  }
}

class _SplashScreen extends StatelessWidget {
  const _SplashScreen();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.dark900,
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: AppTheme.primary,
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Center(
                child: Text('T', style: TextStyle(color: Colors.white, fontSize: 40, fontWeight: FontWeight.bold)),
              ),
            ),
            const SizedBox(height: 16),
            const Text('TUDOaqui', style: TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold)),
            const SizedBox(height: 24),
            const CircularProgressIndicator(color: AppTheme.primary, strokeWidth: 2),
          ],
        ),
      ),
    );
  }
}
