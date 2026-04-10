import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'api_service.dart';
import '../config/api_config.dart';

/// Servico WebSocket para comunicacao em tempo real
class WebSocketService {
  WebSocketChannel? _channel;
  Timer? _pingTimer;
  bool _connected = false;
  Function(Map<String, dynamic>)? onMessage;
  Function()? onDisconnect;
  String? _currentToken;

  bool get connected => _connected;

  /// Conecta ao WebSocket como motorista
  Future<void> connectAsDriver() async {
    final token = await ApiService().token;
    if (token == null) return;
    _currentToken = token;

    final wsUrl = ApiConfig.baseUrl
        .replaceFirst('https://', 'wss://')
        .replaceFirst('http://', 'ws://');
    final url = '$wsUrl/ws/driver/$token';

    await _connect(url);
  }

  /// Conecta ao WebSocket como cliente
  Future<void> connectAsClient() async {
    final token = await ApiService().token;
    if (token == null) return;
    _currentToken = token;

    final wsUrl = ApiConfig.baseUrl
        .replaceFirst('https://', 'wss://')
        .replaceFirst('http://', 'ws://');
    final url = '$wsUrl/ws/client/$token';

    await _connect(url);
  }

  Future<void> _connect(String url) async {
    try {
      disconnect();
      _channel = WebSocketChannel.connect(Uri.parse(url));
      _connected = true;

      // Listen for messages
      _channel!.stream.listen(
        (data) {
          try {
            final msg = jsonDecode(data as String) as Map<String, dynamic>;
            onMessage?.call(msg);
          } catch (_) {}
        },
        onDone: () {
          _connected = false;
          onDisconnect?.call();
        },
        onError: (_) {
          _connected = false;
          onDisconnect?.call();
        },
      );

      // Start ping timer to keep alive
      _pingTimer?.cancel();
      _pingTimer = Timer.periodic(
        const Duration(seconds: 30),
        (_) => send({'type': 'ping'}),
      );
    } catch (e) {
      _connected = false;
    }
  }

  /// Envia mensagem pelo WebSocket
  void send(Map<String, dynamic> data) {
    if (_channel != null && _connected) {
      try {
        _channel!.sink.add(jsonEncode(data));
      } catch (_) {}
    }
  }

  /// Envia localizacao do motorista
  void sendLocation({
    required double latitude,
    required double longitude,
    double? bearing,
    double? speed,
    String? rideId,
  }) {
    send({
      'type': 'location_update',
      'latitude': latitude,
      'longitude': longitude,
      if (bearing != null) 'bearing': bearing,
      if (speed != null) 'speed': speed,
      if (rideId != null) 'ride_id': rideId,
    });
  }

  /// Junta-se ao grupo de uma corrida
  void joinRide(String rideId) {
    send({'type': 'join_ride', 'ride_id': rideId});
  }

  /// Sai do grupo de uma corrida
  void leaveRide(String rideId) {
    send({'type': 'leave_ride', 'ride_id': rideId});
  }

  /// Desconecta
  void disconnect() {
    _pingTimer?.cancel();
    _pingTimer = null;
    _channel?.sink.close();
    _channel = null;
    _connected = false;
  }

  void dispose() {
    disconnect();
  }
}
