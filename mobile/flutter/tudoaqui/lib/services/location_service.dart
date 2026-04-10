import 'dart:async';
import 'package:geolocator/geolocator.dart';

/// Servico de localizacao GPS para motoristas e motoqueiros
class LocationService {
  StreamSubscription<Position>? _positionStream;
  Position? _currentPosition;

  Position? get currentPosition => _currentPosition;

  /// Verifica e solicita permissoes de localizacao
  Future<bool> checkPermissions() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return false;

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return false;
    }
    if (permission == LocationPermission.deniedForever) return false;

    return true;
  }

  /// Obtem posicao actual uma vez
  Future<Position?> getCurrentPosition() async {
    final hasPermission = await checkPermissions();
    if (!hasPermission) return null;

    try {
      _currentPosition = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          distanceFilter: 5,
        ),
      );
      return _currentPosition;
    } catch (e) {
      return null;
    }
  }

  /// Inicia tracking continuo de posicao
  void startTracking({
    required Function(Position) onPosition,
    int distanceFilter = 10,
  }) {
    _positionStream?.cancel();

    const locationSettings = LocationSettings(
      accuracy: LocationAccuracy.high,
      distanceFilter: 10,
    );

    _positionStream = Geolocator.getPositionStream(
      locationSettings: locationSettings,
    ).listen(
      (Position position) {
        _currentPosition = position;
        onPosition(position);
      },
      onError: (e) {
        // Silently handle GPS errors
      },
    );
  }

  /// Para tracking continuo
  void stopTracking() {
    _positionStream?.cancel();
    _positionStream = null;
  }

  /// Calcula distancia entre 2 pontos (metros)
  double distanceBetween(
    double lat1,
    double lon1,
    double lat2,
    double lon2,
  ) {
    return Geolocator.distanceBetween(lat1, lon1, lat2, lon2);
  }

  void dispose() {
    stopTracking();
  }
}
