import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';

import '../../../core/api/api_client.dart';

// ============================================
// Events
// ============================================

abstract class AuthEvent extends Equatable {
  const AuthEvent();
  
  @override
  List<Object?> get props => [];
}

class AuthCheckRequested extends AuthEvent {}

class AuthLoginRequested extends AuthEvent {
  final String telefone;
  
  const AuthLoginRequested(this.telefone);
  
  @override
  List<Object?> get props => [telefone];
}

class AuthOtpVerified extends AuthEvent {
  final String telefone;
  final String codigo;
  
  const AuthOtpVerified({
    required this.telefone,
    required this.codigo,
  });
  
  @override
  List<Object?> get props => [telefone, codigo];
}

class AuthLogoutRequested extends AuthEvent {}

// ============================================
// States
// ============================================

abstract class AuthState extends Equatable {
  const AuthState();
  
  @override
  List<Object?> get props => [];
}

class AuthInitial extends AuthState {}

class AuthLoading extends AuthState {}

class AuthOtpSent extends AuthState {
  final String telefone;
  
  const AuthOtpSent(this.telefone);
  
  @override
  List<Object?> get props => [telefone];
}

class AuthAuthenticated extends AuthState {
  final Map<String, dynamic> user;
  
  const AuthAuthenticated(this.user);
  
  @override
  List<Object?> get props => [user];
}

class AuthUnauthenticated extends AuthState {}

class AuthError extends AuthState {
  final String message;
  
  const AuthError(this.message);
  
  @override
  List<Object?> get props => [message];
}

// ============================================
// Bloc
// ============================================

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final ApiClient apiClient;
  
  AuthBloc({required this.apiClient}) : super(AuthInitial()) {
    on<AuthCheckRequested>(_onAuthCheckRequested);
    on<AuthLoginRequested>(_onAuthLoginRequested);
    on<AuthOtpVerified>(_onAuthOtpVerified);
    on<AuthLogoutRequested>(_onAuthLogoutRequested);
  }
  
  Future<void> _onAuthCheckRequested(
    AuthCheckRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    
    try {
      final hasToken = await apiClient.hasValidToken();
      
      if (hasToken) {
        final response = await apiClient.getMe();
        emit(AuthAuthenticated(response.data));
      } else {
        emit(AuthUnauthenticated());
      }
    } catch (e) {
      emit(AuthUnauthenticated());
    }
  }
  
  Future<void> _onAuthLoginRequested(
    AuthLoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    
    try {
      await apiClient.login(event.telefone);
      emit(AuthOtpSent(event.telefone));
    } catch (e) {
      emit(AuthError(_getErrorMessage(e)));
    }
  }
  
  Future<void> _onAuthOtpVerified(
    AuthOtpVerified event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    
    try {
      final response = await apiClient.verifyOtp(event.telefone, event.codigo);
      
      // Save tokens
      await apiClient.saveTokens(
        response.data['access_token'],
        response.data['refresh_token'],
      );
      
      emit(AuthAuthenticated(response.data['user']));
    } catch (e) {
      emit(AuthError(_getErrorMessage(e)));
    }
  }
  
  Future<void> _onAuthLogoutRequested(
    AuthLogoutRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    
    try {
      await apiClient.logout();
    } catch (_) {}
    
    emit(AuthUnauthenticated());
  }
  
  String _getErrorMessage(dynamic error) {
    if (error is Exception) {
      return error.toString().replaceAll('Exception: ', '');
    }
    return 'Ocorreu um erro. Tente novamente.';
  }
}
