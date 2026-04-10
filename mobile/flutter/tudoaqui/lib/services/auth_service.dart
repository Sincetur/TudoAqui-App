import 'package:flutter/material.dart';
import '../config/api_config.dart';
import '../models/user.dart';
import '../models/partner.dart';
import 'api_service.dart';

/// Servico de autenticacao e gestao do utilizador
class AuthService extends ChangeNotifier {
  final ApiService _api = ApiService();

  UserModel? _user;
  PartnerModel? _partner;
  bool _loading = false;
  String? _error;

  UserModel? get user => _user;
  PartnerModel? get partner => _partner;
  bool get loading => _loading;
  String? get error => _error;
  bool get isAuthenticated => _user != null;
  bool get isPartner => _partner != null;

  /// Envia OTP para o telefone
  Future<bool> sendOtp(String telefone) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      await _api.post(ApiConfig.login, body: {'telefone': telefone}, auth: false);
      _loading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _loading = false;
      notifyListeners();
      return false;
    }
  }

  /// Verifica OTP e faz login
  Future<bool> verifyOtp(String telefone, String codigo) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      final response = await _api.post(
        ApiConfig.verifyOtp,
        body: {'telefone': telefone, 'codigo': codigo},
        auth: false,
      );
      final token = response['access_token'];
      if (token != null) {
        await _api.setToken(token);
        await fetchUser();
        _loading = false;
        notifyListeners();
        return true;
      }
      _error = 'Token nao recebido';
      _loading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _error = e.toString();
      _loading = false;
      notifyListeners();
      return false;
    }
  }

  /// Obtem dados do utilizador autenticado
  Future<void> fetchUser() async {
    try {
      final data = await _api.get(ApiConfig.me);
      _user = UserModel.fromJson(data);
      // Carregar perfil parceiro se aplicavel
      if (_user!.isPartnerRole) {
        await fetchPartner();
      }
      notifyListeners();
    } catch (e) {
      _user = null;
      notifyListeners();
    }
  }

  /// Obtem perfil de parceiro
  Future<void> fetchPartner() async {
    try {
      final data = await _api.get(ApiConfig.partnerMe);
      if (data != null && data is Map<String, dynamic> && data.isNotEmpty) {
        _partner = PartnerModel.fromJson(data);
      }
    } catch (_) {
      _partner = null;
    }
    notifyListeners();
  }

  /// Tenta restaurar sessao
  Future<bool> tryAutoLogin() async {
    final token = await _api.token;
    if (token == null) return false;
    try {
      await fetchUser();
      return _user != null;
    } catch (_) {
      await _api.clearToken();
      return false;
    }
  }

  /// Logout
  Future<void> logout() async {
    await _api.clearToken();
    _user = null;
    _partner = null;
    notifyListeners();
  }
}
