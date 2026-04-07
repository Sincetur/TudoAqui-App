import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../config/app_config.dart';
import 'api_client.dart';

/// Serviço WebSocket para comunicação em tempo real
class WebSocketService {
  WebSocketChannel? _channel;
  final ApiClient _apiClient = ApiClient();
  
  // Stream controllers
  final _messageController = StreamController<Map<String, dynamic>>.broadcast();
  final _connectionController = StreamController<bool>.broadcast();
  
  // Streams públicos
  Stream<Map<String, dynamic>> get messages => _messageController.stream;
  Stream<bool> get connectionStatus => _connectionController.stream;
  
  // Estado
  bool _isConnected = false;
  bool get isConnected => _isConnected;
  
  Timer? _pingTimer;
  Timer? _reconnectTimer;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 5;
  
  /// Conecta ao WebSocket
  Future<void> connect({required String userType}) async {
    try {
      final token = await _apiClient.getAccessToken();
      if (token == null) {
        throw Exception('Token não disponível');
      }
      
      final wsUrl = '${EnvironmentConfig.wsBaseUrl}/$userType/$token';
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      _channel!.stream.listen(
        _onMessage,
        onError: _onError,
        onDone: _onDone,
      );
      
      _isConnected = true;
      _reconnectAttempts = 0;
      _connectionController.add(true);
      
      // Iniciar ping para manter conexão
      _startPing();
      
    } catch (e) {
      _isConnected = false;
      _connectionController.add(false);
      _scheduleReconnect(userType);
    }
  }
  
  /// Desconecta do WebSocket
  void disconnect() {
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _isConnected = false;
    _connectionController.add(false);
  }
  
  /// Envia mensagem
  void send(Map<String, dynamic> data) {
    if (_isConnected && _channel != null) {
      _channel!.sink.add(jsonEncode(data));
    }
  }
  
  /// Envia ping
  void _startPing() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      send({'type': 'ping'});
    });
  }
  
  /// Handler de mensagem
  void _onMessage(dynamic message) {
    try {
      final data = jsonDecode(message as String) as Map<String, dynamic>;
      
      // Ignorar pong
      if (data['type'] == 'pong') return;
      
      _messageController.add(data);
    } catch (e) {
      // Ignora mensagens inválidas
    }
  }
  
  /// Handler de erro
  void _onError(dynamic error) {
    _isConnected = false;
    _connectionController.add(false);
  }
  
  /// Handler de conexão fechada
  void _onDone() {
    _isConnected = false;
    _connectionController.add(false);
    _pingTimer?.cancel();
  }
  
  /// Agenda reconexão
  void _scheduleReconnect(String userType) {
    if (_reconnectAttempts >= _maxReconnectAttempts) return;
    
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(
      Duration(seconds: _reconnectAttempts * 2 + 1),
      () {
        _reconnectAttempts++;
        connect(userType: userType);
      },
    );
  }
  
  /// Entrar numa sala de corrida
  void joinRide(String rideId) {
    send({
      'type': 'join_ride',
      'ride_id': rideId,
    });
  }
  
  /// Sair de uma sala de corrida
  void leaveRide(String rideId) {
    send({
      'type': 'leave_ride',
      'ride_id': rideId,
    });
  }
  
  /// Envia localização (motorista)
  void sendLocation({
    required String rideId,
    required double latitude,
    required double longitude,
    double? bearing,
  }) {
    send({
      'type': 'location_update',
      'ride_id': rideId,
      'latitude': latitude,
      'longitude': longitude,
      if (bearing != null) 'bearing': bearing,
    });
  }
  
  /// Dispose
  void dispose() {
    disconnect();
    _messageController.close();
    _connectionController.close();
  }
}

/// Singleton instance
final wsService = WebSocketService();
