import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/auth_service.dart';
import '../../widgets/common.dart';

/// Ecra de Login OTP
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _phoneController = TextEditingController();
  final _otpController = TextEditingController();
  bool _otpSent = false;

  @override
  void dispose() {
    _phoneController.dispose();
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _sendOtp() async {
    final phone = _phoneController.text.trim();
    if (phone.isEmpty) return;
    final auth = context.read<AuthService>();
    final ok = await auth.sendOtp(phone.startsWith('+') ? phone : '+244$phone');
    if (ok && mounted) setState(() => _otpSent = true);
  }

  Future<void> _verifyOtp() async {
    final phone = _phoneController.text.trim();
    final code = _otpController.text.trim();
    if (code.length < 4) return;
    final auth = context.read<AuthService>();
    await auth.verifyOtp(phone.startsWith('+') ? phone : '+244$phone', code);
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Logo
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
                const SizedBox(height: 4),
                const Text('a sua vida em um so lugar', style: TextStyle(color: AppTheme.dark400, fontSize: 13)),
                const SizedBox(height: 40),

                // Phone input
                if (!_otpSent) ...[
                  TextField(
                    controller: _phoneController,
                    keyboardType: TextInputType.phone,
                    style: const TextStyle(color: Colors.white),
                    decoration: const InputDecoration(
                      prefixText: '+244 ',
                      prefixStyle: TextStyle(color: AppTheme.dark400),
                      hintText: '923 456 789',
                      prefixIcon: Icon(Icons.phone, color: AppTheme.dark500),
                    ),
                  ),
                  const SizedBox(height: 16),
                  PrimaryButton(
                    label: 'Enviar Codigo',
                    onPressed: _sendOtp,
                    loading: auth.loading,
                    icon: Icons.arrow_forward,
                  ),
                ],

                // OTP input
                if (_otpSent) ...[
                  Text(
                    'Codigo enviado para ${_phoneController.text}',
                    style: const TextStyle(color: AppTheme.dark300, fontSize: 13),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _otpController,
                    keyboardType: TextInputType.number,
                    textAlign: TextAlign.center,
                    maxLength: 6,
                    style: const TextStyle(color: Colors.white, fontSize: 24, letterSpacing: 8, fontWeight: FontWeight.bold),
                    decoration: const InputDecoration(
                      hintText: '------',
                      counterText: '',
                    ),
                  ),
                  const SizedBox(height: 16),
                  PrimaryButton(
                    label: 'Verificar',
                    onPressed: _verifyOtp,
                    loading: auth.loading,
                    icon: Icons.check,
                  ),
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: () => setState(() {
                      _otpSent = false;
                      _otpController.clear();
                    }),
                    child: const Text('Alterar numero', style: TextStyle(color: AppTheme.dark400)),
                  ),
                ],

                // Error
                if (auth.error != null) ...[
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppTheme.danger.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(auth.error!, style: const TextStyle(color: AppTheme.danger, fontSize: 13)),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
