/// Configurações gerais da aplicação
class AppConfig {
  AppConfig._();
  
  // App Info
  static const String appName = 'TUDOaqui';
  static const String appVersion = '1.0.0';
  static const String appTagline = 'A sua vida, num só app';
  
  // API
  static const String apiBaseUrl = 'http://localhost:8000/api/v1';
  static const String wsBaseUrl = 'ws://localhost:8000/api/v1/ws';
  
  // Timeouts
  static const int connectionTimeout = 30000; // 30 seconds
  static const int receiveTimeout = 30000;
  
  // Storage Keys
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userDataKey = 'user_data';
  
  // Maps
  static const String googleMapsApiKey = 'YOUR_GOOGLE_MAPS_API_KEY';
  
  // Angola specific
  static const String defaultCountryCode = '+244';
  static const String currency = 'Kz';
  static const String locale = 'pt_AO';
}

/// Configurações de ambiente
enum Environment { dev, staging, prod }

class EnvironmentConfig {
  static Environment currentEnvironment = Environment.dev;
  
  static String get apiBaseUrl {
    switch (currentEnvironment) {
      case Environment.dev:
        return 'http://localhost:8000/api/v1';
      case Environment.staging:
        return 'https://staging-api.tudoaqui.ao/api/v1';
      case Environment.prod:
        return 'https://api.tudoaqui.ao/api/v1';
    }
  }
  
  static String get wsBaseUrl {
    switch (currentEnvironment) {
      case Environment.dev:
        return 'ws://localhost:8000/api/v1/ws';
      case Environment.staging:
        return 'wss://staging-api.tudoaqui.ao/api/v1/ws';
      case Environment.prod:
        return 'wss://api.tudoaqui.ao/api/v1/ws';
    }
  }
}
