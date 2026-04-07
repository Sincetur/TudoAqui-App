import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pin_code_fields/pin_code_fields.dart';

import '../../../core/config/theme.dart';
import '../../../core/config/routes.dart';
import '../bloc/auth_bloc.dart';

class OTPScreen extends StatefulWidget {
  final String telefone;
  
  const OTPScreen({super.key, required this.telefone});

  @override
  State<OTPScreen> createState() => _OTPScreenState();
}

class _OTPScreenState extends State<OTPScreen> {
  final _otpController = TextEditingController();
  Timer? _timer;
  int _secondsRemaining = 300; // 5 minutes
  bool _canResend = false;
  
  @override
  void initState() {
    super.initState();
    _startTimer();
  }
  
  @override
  void dispose() {
    _timer?.cancel();
    _otpController.dispose();
    super.dispose();
  }
  
  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_secondsRemaining > 0) {
        setState(() => _secondsRemaining--);
      } else {
        setState(() => _canResend = true);
        timer.cancel();
      }
    });
  }
  
  String get _formattedTime {
    final minutes = _secondsRemaining ~/ 60;
    final seconds = _secondsRemaining % 60;
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }
  
  void _verifyOtp(String code) {
    if (code.length == 6) {
      context.read<AuthBloc>().add(
        AuthOtpVerified(telefone: widget.telefone, codigo: code),
      );
    }
  }
  
  void _resendOtp() {
    if (!_canResend) return;
    
    setState(() {
      _secondsRemaining = 300;
      _canResend = false;
    });
    _startTimer();
    
    context.read<AuthBloc>().add(AuthLoginRequested(widget.telefone));
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<AuthBloc, AuthState>(
      listener: (context, state) {
        if (state is AuthAuthenticated) {
          Navigator.pushNamedAndRemoveUntil(
            context,
            AppRoutes.home,
            (route) => false,
          );
        } else if (state is AuthError) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(state.message),
              backgroundColor: AppColors.error,
            ),
          );
          _otpController.clear();
        }
      },
      child: Scaffold(
        backgroundColor: AppColors.background,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () => Navigator.pop(context),
          ),
        ),
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Verificação',
                  style: AppTypography.headline2,
                ),
                const SizedBox(height: 8),
                
                Text(
                  'Enviámos um código de 6 dígitos para',
                  style: AppTypography.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 4),
                
                Text(
                  widget.telefone,
                  style: AppTypography.bodyLarge.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 40),
                
                // OTP Input
                PinCodeTextField(
                  appContext: context,
                  controller: _otpController,
                  length: 6,
                  keyboardType: TextInputType.number,
                  animationType: AnimationType.fade,
                  pinTheme: PinTheme(
                    shape: PinCodeFieldShape.box,
                    borderRadius: BorderRadius.circular(12),
                    fieldHeight: 56,
                    fieldWidth: 48,
                    activeFillColor: AppColors.surface,
                    inactiveFillColor: AppColors.surface,
                    selectedFillColor: AppColors.surface,
                    activeColor: AppColors.primary,
                    inactiveColor: AppColors.border,
                    selectedColor: AppColors.primary,
                  ),
                  enableActiveFill: true,
                  onCompleted: _verifyOtp,
                  onChanged: (_) {},
                ),
                const SizedBox(height: 24),
                
                // Timer & Resend
                Center(
                  child: Column(
                    children: [
                      if (!_canResend)
                        Text(
                          'Código expira em $_formattedTime',
                          style: AppTypography.bodySmall,
                        ),
                      const SizedBox(height: 8),
                      TextButton(
                        onPressed: _canResend ? _resendOtp : null,
                        child: Text(
                          'Reenviar código',
                          style: TextStyle(
                            color: _canResend
                                ? AppColors.primary
                                : AppColors.disabled,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                
                const Spacer(),
                
                // Verify Button
                BlocBuilder<AuthBloc, AuthState>(
                  builder: (context, state) {
                    final isLoading = state is AuthLoading;
                    
                    return ElevatedButton(
                      onPressed: isLoading
                          ? null
                          : () => _verifyOtp(_otpController.text),
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
                          : const Text('Verificar'),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
