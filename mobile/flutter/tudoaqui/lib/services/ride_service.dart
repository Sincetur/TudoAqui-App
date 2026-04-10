import 'api_service.dart';
import '../config/api_config.dart';
import '../models/ride.dart';

/// Servico de corridas - comunicacao com API
class RideService {
  final ApiService _api = ApiService();

  /// Estima preco e duracao de uma corrida
  Future<RideEstimate> estimateRide({
    required double origemLat,
    required double origemLon,
    required double destinoLat,
    required double destinoLon,
  }) async {
    final data = await _api.post(ApiConfig.ridesEstimate, body: {
      'origem': {'latitude': origemLat, 'longitude': origemLon},
      'destino': {'latitude': destinoLat, 'longitude': destinoLon},
    });
    return RideEstimate.fromJson(data);
  }

  /// Solicita nova corrida
  Future<RideModel> requestRide({
    required String origemEndereco,
    required double origemLat,
    required double origemLon,
    required String destinoEndereco,
    required double destinoLat,
    required double destinoLon,
  }) async {
    final data = await _api.post(ApiConfig.ridesRequest, body: {
      'origem_endereco': origemEndereco,
      'origem_latitude': origemLat,
      'origem_longitude': origemLon,
      'destino_endereco': destinoEndereco,
      'destino_latitude': destinoLat,
      'destino_longitude': destinoLon,
    });
    return RideModel.fromJson(data);
  }

  /// Corrida actual do cliente
  Future<RideModel?> getCurrentRide() async {
    try {
      final data = await _api.get(ApiConfig.ridesCurrent);
      if (data == null || (data is Map && data.isEmpty)) return null;
      return RideModel.fromJson(data);
    } catch (_) {
      return null;
    }
  }

  /// Corridas pendentes proximas (motorista)
  Future<List<RideModel>> getPendingRides(double lat, double lon) async {
    final data = await _api.get(
      '${ApiConfig.ridesPending}?latitude=$lat&longitude=$lon',
    );
    if (data is List) {
      return data.map((r) => RideModel.fromJson(r)).toList();
    }
    return [];
  }

  /// Aceitar corrida (motorista)
  Future<RideModel> acceptRide(String rideId) async {
    final data = await _api.post(ApiConfig.rideAccept(rideId));
    return RideModel.fromJson(data);
  }

  /// Iniciar corrida (motorista)
  Future<RideModel> startRide(String rideId) async {
    final data = await _api.post(ApiConfig.rideStart(rideId));
    return RideModel.fromJson(data);
  }

  /// Finalizar corrida (motorista)
  Future<RideModel> finishRide(String rideId) async {
    final data = await _api.post(ApiConfig.rideFinish(rideId));
    return RideModel.fromJson(data);
  }

  /// Cancelar corrida
  Future<RideModel> cancelRide(String rideId, {String? motivo}) async {
    final data = await _api.post(
      ApiConfig.rideCancel(rideId),
      body: motivo != null ? {'motivo': motivo} : null,
    );
    return RideModel.fromJson(data);
  }

  /// Perfil motorista
  Future<Map<String, dynamic>> getDriverProfile() async {
    return await _api.get(ApiConfig.driverMe);
  }

  /// Toggle online/offline motorista
  Future<Map<String, dynamic>> setOnline({
    required bool online,
    double? lat,
    double? lon,
  }) async {
    return await _api.post(ApiConfig.driverOnline, body: {
      'online': online,
      if (lat != null) 'latitude': lat,
      if (lon != null) 'longitude': lon,
    });
  }

  /// Atualizar localizacao via REST (fallback)
  Future<void> updateLocation(double lat, double lon) async {
    await _api.post(ApiConfig.driverLocation, body: {
      'latitude': lat,
      'longitude': lon,
    });
  }

  /// Stats do motorista
  Future<Map<String, dynamic>> getDriverStats() async {
    return await _api.get(ApiConfig.driverStats);
  }
}
