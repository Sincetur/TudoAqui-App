import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../config/app_config.dart';

/// Cliente HTTP para comunicação com a API
class ApiClient {
  late final Dio _dio;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  
  ApiClient() {
    _dio = Dio(
      BaseOptions(
        baseUrl: EnvironmentConfig.apiBaseUrl,
        connectTimeout: const Duration(milliseconds: AppConfig.connectionTimeout),
        receiveTimeout: const Duration(milliseconds: AppConfig.receiveTimeout),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );
    
    _setupInterceptors();
  }
  
  void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add auth token
          final token = await _storage.read(key: AppConfig.accessTokenKey);
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onResponse: (response, handler) {
          return handler.next(response);
        },
        onError: (error, handler) async {
          // Handle 401 - try to refresh token
          if (error.response?.statusCode == 401) {
            try {
              final refreshed = await _refreshToken();
              if (refreshed) {
                // Retry original request
                final opts = error.requestOptions;
                final token = await _storage.read(key: AppConfig.accessTokenKey);
                opts.headers['Authorization'] = 'Bearer $token';
                
                final response = await _dio.fetch(opts);
                return handler.resolve(response);
              }
            } catch (_) {}
          }
          return handler.next(error);
        },
      ),
    );
  }
  
  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _storage.read(key: AppConfig.refreshTokenKey);
      if (refreshToken == null) return false;
      
      final response = await _dio.post(
        '/auth/refresh-token',
        data: {'refresh_token': refreshToken},
      );
      
      if (response.statusCode == 200) {
        await _storage.write(
          key: AppConfig.accessTokenKey,
          value: response.data['access_token'],
        );
        await _storage.write(
          key: AppConfig.refreshTokenKey,
          value: response.data['refresh_token'],
        );
        return true;
      }
    } catch (_) {}
    return false;
  }
  
  // ============================================
  // Auth
  // ============================================
  
  Future<Response> login(String telefone) async {
    return _dio.post('/auth/login', data: {'telefone': telefone});
  }
  
  Future<Response> verifyOtp(String telefone, String codigo) async {
    return _dio.post('/auth/verify-otp', data: {
      'telefone': telefone,
      'codigo': codigo,
    });
  }
  
  Future<Response> getMe() async {
    return _dio.get('/auth/me');
  }
  
  Future<void> logout() async {
    final refreshToken = await _storage.read(key: AppConfig.refreshTokenKey);
    try {
      await _dio.post('/auth/logout', data: {'refresh_token': refreshToken});
    } catch (_) {}
    
    await _storage.delete(key: AppConfig.accessTokenKey);
    await _storage.delete(key: AppConfig.refreshTokenKey);
  }
  
  // ============================================
  // Rides
  // ============================================
  
  Future<Response> estimateRide({
    required double origemLat,
    required double origemLon,
    required String origemEndereco,
    required double destinoLat,
    required double destinoLon,
    required String destinoEndereco,
  }) async {
    return _dio.post('/rides/estimate', data: {
      'origem': {
        'latitude': origemLat,
        'longitude': origemLon,
        'endereco': origemEndereco,
      },
      'destino': {
        'latitude': destinoLat,
        'longitude': destinoLon,
        'endereco': destinoEndereco,
      },
    });
  }
  
  Future<Response> requestRide({
    required double origemLat,
    required double origemLon,
    required String origemEndereco,
    required double destinoLat,
    required double destinoLon,
    required String destinoEndereco,
  }) async {
    return _dio.post('/rides/request', data: {
      'origem_latitude': origemLat,
      'origem_longitude': origemLon,
      'origem_endereco': origemEndereco,
      'destino_latitude': destinoLat,
      'destino_longitude': destinoLon,
      'destino_endereco': destinoEndereco,
    });
  }
  
  Future<Response> getCurrentRide() async {
    return _dio.get('/rides/current');
  }
  
  Future<Response> getRide(String rideId) async {
    return _dio.get('/rides/$rideId');
  }
  
  Future<Response> cancelRide(String rideId, {String? motivo}) async {
    return _dio.post('/rides/$rideId/cancel', data: {
      if (motivo != null) 'motivo': motivo,
    });
  }
  
  Future<Response> rateRide(String rideId, int nota, {String? comentario}) async {
    return _dio.post('/rides/$rideId/rate', data: {
      'nota': nota,
      if (comentario != null) 'comentario': comentario,
    });
  }
  
  Future<Response> getRideHistory({int limit = 20, int offset = 0}) async {
    return _dio.get('/rides/history/client', queryParameters: {
      'limit': limit,
      'offset': offset,
    });
  }
  
  // ============================================
  // Notifications
  // ============================================
  
  Future<Response> getNotifications({bool unreadOnly = false}) async {
    return _dio.get('/notifications', queryParameters: {
      'unread_only': unreadOnly,
    });
  }
  
  Future<Response> getUnreadCount() async {
    return _dio.get('/notifications/unread-count');
  }
  
  Future<Response> markNotificationRead(String notificationId) async {
    return _dio.post('/notifications/$notificationId/read');
  }
  
  // ============================================
  // Payments
  // ============================================
  
  Future<Response> getWallet() async {
    return _dio.get('/payments/wallet/me');
  }
  
  Future<Response> getPaymentHistory() async {
    return _dio.get('/payments');
  }
  
  // ============================================
  // Tokens management
  // ============================================
  
  Future<void> saveTokens(String accessToken, String refreshToken) async {
    await _storage.write(key: AppConfig.accessTokenKey, value: accessToken);
    await _storage.write(key: AppConfig.refreshTokenKey, value: refreshToken);
  }
  
  Future<String?> getAccessToken() async {
    return _storage.read(key: AppConfig.accessTokenKey);
  }
  
  Future<bool> hasValidToken() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }
}
