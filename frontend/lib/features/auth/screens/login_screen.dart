import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:mask_text_input_formatter/mask_text_input_formatter.dart';

import '../../../core/config/theme.dart';
import '../../../core/config/app_config.dart';
import '../../../core/config/routes.dart';
import '../bloc/auth_bloc.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _phoneController = TextEditingController();
  final _phoneMask = MaskTextInputFormatter(
    mask: '### ### ###',
    filter: {'#': RegExp(r'[0-9]')},
  );
  
  bool get _isPhoneValid => _phoneMask.getUnmaskedText().length >= 9;
  
  @override
  void dispose() {
    _phoneController.dispose();
    super.dispose();
  }
  
  void _onContinue() {
    if (!_isPhoneValid) return;
    
    final phone = '${AppConfig.defaultCountryCode}${_phoneMask.getUnmaskedText()}';
    context.read<AuthBloc>().add(AuthLoginRequested(phone));
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<AuthBloc, AuthState>(
      listener: (context, state) {
        if (state is AuthOtpSent) {
          Navigator.pushNamed(
            context,
            AppRoutes.otp,
            arguments: {'telefone': state.telefone},
          );
        } else if (state is AuthError) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(state.message),
              backgroundColor: AppColors.error,
            ),
          );
        }
      },
      child: Scaffold(
        backgroundColor: AppColors.background,
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Spacer(),
                
                // Header
                const Center(
                  child: Text(
                    '👋',
                    style: TextStyle(fontSize: 64),
                  ),
                ),
                const SizedBox(height: 24),
                
                const Center(
                  child: Text(
                    'Bem-vindo ao TUDOaqui',
                    style: AppTypography.headline2,
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 8),
                
                Center(
                  child: Text(
                    'Insira o seu número de telefone para continuar',
                    style: AppTypography.bodyMedium.copyWith(
                      color: AppColors.textSecondary,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 48),
                
                // Phone Input
                Row(
                  children: [
                    // Country Code
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 18,
                      ),
                      decoration: BoxDecoration(
                        color: AppColors.surface,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: AppColors.border),
                      ),
                      child: Row(
                        children: [
                          const Text('🇦🇴', style: TextStyle(fontSize: 20)),
                          const SizedBox(width: 8),
                          Text(
                            AppConfig.defaultCountryCode,
                            style: AppTypography.bodyLarge.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    
                    // Phone Number
                    Expanded(
                      child: TextField(
                        controller: _phoneController,
                        inputFormatters: [_phoneMask],
                        keyboardType: TextInputType.phone,
                        style: AppTypography.bodyLarge,
                        decoration: const InputDecoration(
                          hintText: '923 456 789',
                        ),
                        onChanged: (_) => setState(() {}),
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 32),
                
                // Continue Button
                BlocBuilder<AuthBloc, AuthState>(
                  builder: (context, state) {
                    final isLoading = state is AuthLoading;
                    
                    return ElevatedButton(
                      onPressed: _isPhoneValid && !isLoading ? _onContinue : null,
                      child: isLoading
                          ? const SizedBox(
                              width: 24,
                              height: 24,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  Colors.white,
                                ),
                              ),
                            )
                          : const Text('Continuar'),
                    );
                  },
                ),
                
                const Spacer(),
                
                // Terms
                Center(
                  child: Text(
                    'Ao continuar, aceita os nossos Termos de Serviço\ne Política de Privacidade',
                    style: AppTypography.caption,
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
