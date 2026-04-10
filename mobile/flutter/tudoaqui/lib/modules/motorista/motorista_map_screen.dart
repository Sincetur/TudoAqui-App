import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import '../../config/theme.dart';
import '../../models/ride.dart';
import '../../services/location_service.dart';
import '../../services/websocket_service.dart';
import '../../services/ride_service.dart';
import '../../widgets/common.dart';

/// Ecra do mapa para motoristas com tracking GPS
class MotoristaMapScreen extends StatefulWidget {
  final bool initialOnline;
  final VoidCallback? onBackToHome;

  const MotoristaMapScreen({
    super.key,
    this.initialOnline = false,
    this.onBackToHome,
  });

  @override
  State<MotoristaMapScreen> createState() => _MotoristaMapScreenState();
}

class _MotoristaMapScreenState extends State<MotoristaMapScreen> {
  // Services
  final LocationService _locationService = LocationService();
  final WebSocketService _wsService = WebSocketService();
  final RideService _rideService = RideService();

  // Map controller
  GoogleMapController? _mapController;

  // State
  bool _online = false;
  bool _loading = true;
  bool _loadingAction = false;
  Position? _currentPosition;
  RideModel? _activeRide;
  List<RideModel> _pendingRides = [];
  Timer? _pendingTimer;

  // Map markers & polylines
  final Set<Marker> _markers = {};
  final Set<Polyline> _polylines = {};

  // Luanda default camera
  static const LatLng _luandaCenter = LatLng(-8.8383, 13.2344);

  // Custom map style for dark theme
  static const String _darkMapStyle = '''
[
  {"elementType":"geometry","stylers":[{"color":"#212121"}]},
  {"elementType":"labels.icon","stylers":[{"visibility":"off"}]},
  {"elementType":"labels.text.fill","stylers":[{"color":"#757575"}]},
  {"elementType":"labels.text.stroke","stylers":[{"color":"#212121"}]},
  {"featureType":"administrative","elementType":"geometry","stylers":[{"color":"#757575"}]},
  {"featureType":"poi","elementType":"geometry","stylers":[{"color":"#2a2a2a"}]},
  {"featureType":"road","elementType":"geometry.fill","stylers":[{"color":"#3a3a3a"}]},
  {"featureType":"road","elementType":"geometry.stroke","stylers":[{"color":"#212121"}]},
  {"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#4a4a4a"}]},
  {"featureType":"water","elementType":"geometry","stylers":[{"color":"#1a1a2e"}]}
]
''';

  @override
  void initState() {
    super.initState();
    _online = widget.initialOnline;
    _initMap();
  }

  Future<void> _initMap() async {
    final hasPermission = await _locationService.checkPermissions();
    if (!hasPermission) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Permissao de localizacao necessaria'),
            backgroundColor: AppTheme.danger,
          ),
        );
      }
    }

    final position = await _locationService.getCurrentPosition();
    if (mounted) {
      setState(() {
        _currentPosition = position;
        _loading = false;
      });
    }

    if (position != null) {
      _updateDriverMarker(position.latitude, position.longitude);
      _mapController?.animateCamera(
        CameraUpdate.newLatLng(LatLng(position.latitude, position.longitude)),
      );
    }

    if (_online) {
      _goOnline();
    }
  }

  void _goOnline() async {
    _online = true;

    // Start GPS tracking
    _locationService.startTracking(
      onPosition: _onPositionUpdate,
    );

    // Connect WebSocket
    _wsService.onMessage = _onWsMessage;
    _wsService.onDisconnect = () {
      if (mounted && _online) {
        // Auto-reconnect
        Future.delayed(const Duration(seconds: 3), () {
          if (_online) _wsService.connectAsDriver();
        });
      }
    };
    await _wsService.connectAsDriver();

    // Send initial position
    if (_currentPosition != null) {
      try {
        await _rideService.setOnline(
          online: true,
          lat: _currentPosition!.latitude,
          lon: _currentPosition!.longitude,
        );
      } catch (_) {}
    }

    // Start polling pending rides
    _startPendingPoll();

    if (mounted) setState(() {});
  }

  void _goOffline() async {
    _online = false;
    _locationService.stopTracking();
    _wsService.disconnect();
    _pendingTimer?.cancel();
    _pendingRides.clear();

    try {
      await _rideService.setOnline(online: false);
    } catch (_) {}

    // Clear pending ride markers but keep driver marker
    _markers.removeWhere((m) => m.markerId.value != 'driver');
    _polylines.clear();

    if (mounted) setState(() {});
  }

  void _onPositionUpdate(Position position) {
    _currentPosition = position;
    _updateDriverMarker(position.latitude, position.longitude);

    // Send via WebSocket
    _wsService.sendLocation(
      latitude: position.latitude,
      longitude: position.longitude,
      bearing: position.heading,
      speed: position.speed,
      rideId: _activeRide?.id,
    );

    if (mounted) setState(() {});
  }

  void _onWsMessage(Map<String, dynamic> msg) {
    final type = msg['type'];
    if (type == 'new_ride_nearby') {
      // Refresh pending rides
      _fetchPendingRides();
    } else if (type == 'ride_cancelled') {
      // Ride was cancelled
      if (_activeRide != null && msg['ride_id'] == _activeRide!.id) {
        _activeRide = null;
        _polylines.clear();
        _markers.removeWhere((m) => m.markerId.value.startsWith('ride_'));
        if (mounted) {
          setState(() {});
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Corrida cancelada pelo cliente'),
              backgroundColor: AppTheme.warning,
            ),
          );
        }
      }
    }
  }

  void _startPendingPoll() {
    _pendingTimer?.cancel();
    _fetchPendingRides();
    _pendingTimer = Timer.periodic(
      const Duration(seconds: 15),
      (_) => _fetchPendingRides(),
    );
  }

  Future<void> _fetchPendingRides() async {
    if (!_online || _activeRide != null || _currentPosition == null) return;
    try {
      final rides = await _rideService.getPendingRides(
        _currentPosition!.latitude,
        _currentPosition!.longitude,
      );
      if (mounted) {
        setState(() => _pendingRides = rides);
        _updatePendingMarkers();
      }
    } catch (_) {}
  }

  void _updateDriverMarker(double lat, double lon) {
    _markers.removeWhere((m) => m.markerId.value == 'driver');
    _markers.add(
      Marker(
        markerId: const MarkerId('driver'),
        position: LatLng(lat, lon),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed),
        infoWindow: const InfoWindow(title: 'Voce esta aqui'),
        zIndex: 10,
      ),
    );
  }

  void _updatePendingMarkers() {
    _markers.removeWhere((m) => m.markerId.value.startsWith('pending_'));
    for (var ride in _pendingRides) {
      _markers.add(
        Marker(
          markerId: MarkerId('pending_${ride.id}'),
          position: LatLng(ride.origemLatitude, ride.origemLongitude),
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueOrange),
          infoWindow: InfoWindow(
            title: ride.origemEndereco,
            snippet: '${ride.valorEstimado?.toStringAsFixed(0)} Kz - ${ride.distanciaKm?.toStringAsFixed(1)} km',
          ),
          onTap: () => _showRideDetail(ride),
        ),
      );
    }
  }

  void _updateActiveRideMarkers() {
    if (_activeRide == null) return;
    _markers.removeWhere(
        (m) => m.markerId.value.startsWith('ride_') || m.markerId.value.startsWith('pending_'));

    // Origem marker
    _markers.add(
      Marker(
        markerId: const MarkerId('ride_origem'),
        position: LatLng(_activeRide!.origemLatitude, _activeRide!.origemLongitude),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen),
        infoWindow: InfoWindow(title: 'Recolha', snippet: _activeRide!.origemEndereco),
      ),
    );

    // Destino marker
    _markers.add(
      Marker(
        markerId: const MarkerId('ride_destino'),
        position: LatLng(_activeRide!.destinoLatitude, _activeRide!.destinoLongitude),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
        infoWindow: InfoWindow(title: 'Destino', snippet: _activeRide!.destinoEndereco),
      ),
    );

    // Polyline between origem and destino
    _polylines.clear();
    _polylines.add(
      Polyline(
        polylineId: const PolylineId('route'),
        points: [
          LatLng(_activeRide!.origemLatitude, _activeRide!.origemLongitude),
          LatLng(_activeRide!.destinoLatitude, _activeRide!.destinoLongitude),
        ],
        color: AppTheme.primary,
        width: 4,
        patterns: [PatternItem.dash(20), PatternItem.gap(10)],
      ),
    );
  }

  // ========================
  // Ride Actions
  // ========================

  Future<void> _acceptRide(RideModel ride) async {
    setState(() => _loadingAction = true);
    try {
      final accepted = await _rideService.acceptRide(ride.id);
      _activeRide = accepted;
      _pendingRides.clear();
      _pendingTimer?.cancel();
      _wsService.joinRide(accepted.id);
      _updateActiveRideMarkers();

      // Zoom to show both markers
      if (_currentPosition != null) {
        _fitBounds(
          LatLng(_currentPosition!.latitude, _currentPosition!.longitude),
          LatLng(accepted.origemLatitude, accepted.origemLongitude),
        );
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Corrida aceite!'), backgroundColor: AppTheme.success),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro: $e'), backgroundColor: AppTheme.danger),
        );
      }
    }
    setState(() => _loadingAction = false);
  }

  Future<void> _startRide() async {
    if (_activeRide == null) return;
    setState(() => _loadingAction = true);
    try {
      final started = await _rideService.startRide(_activeRide!.id);
      _activeRide = started;
      _updateActiveRideMarkers();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro: $e'), backgroundColor: AppTheme.danger),
        );
      }
    }
    setState(() => _loadingAction = false);
  }

  Future<void> _finishRide() async {
    if (_activeRide == null) return;
    setState(() => _loadingAction = true);
    try {
      await _rideService.finishRide(_activeRide!.id);
      _wsService.leaveRide(_activeRide!.id);
      _activeRide = null;
      _polylines.clear();
      _markers.removeWhere((m) => m.markerId.value.startsWith('ride_'));
      _startPendingPoll();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Corrida finalizada!'), backgroundColor: AppTheme.success),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro: $e'), backgroundColor: AppTheme.danger),
        );
      }
    }
    setState(() => _loadingAction = false);
  }

  Future<void> _cancelActiveRide() async {
    if (_activeRide == null) return;
    setState(() => _loadingAction = true);
    try {
      await _rideService.cancelRide(_activeRide!.id, motivo: 'Cancelado pelo motorista');
      _wsService.leaveRide(_activeRide!.id);
      _activeRide = null;
      _polylines.clear();
      _markers.removeWhere((m) => m.markerId.value.startsWith('ride_'));
      _startPendingPoll();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro: $e'), backgroundColor: AppTheme.danger),
        );
      }
    }
    setState(() => _loadingAction = false);
  }

  void _fitBounds(LatLng sw, LatLng ne) {
    final bounds = LatLngBounds(
      southwest: LatLng(
        sw.latitude < ne.latitude ? sw.latitude : ne.latitude,
        sw.longitude < ne.longitude ? sw.longitude : ne.longitude,
      ),
      northeast: LatLng(
        sw.latitude > ne.latitude ? sw.latitude : ne.latitude,
        sw.longitude > ne.longitude ? sw.longitude : ne.longitude,
      ),
    );
    _mapController?.animateCamera(CameraUpdate.newLatLngBounds(bounds, 80));
  }

  void _centerOnDriver() {
    if (_currentPosition != null) {
      _mapController?.animateCamera(
        CameraUpdate.newLatLngZoom(
          LatLng(_currentPosition!.latitude, _currentPosition!.longitude),
          16,
        ),
      );
    }
  }

  void _showRideDetail(RideModel ride) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.dark800,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => _RideDetailSheet(
        ride: ride,
        onAccept: () {
          Navigator.pop(ctx);
          _acceptRide(ride);
        },
        loading: _loadingAction,
      ),
    );
  }

  @override
  void dispose() {
    _locationService.dispose();
    _wsService.dispose();
    _pendingTimer?.cancel();
    _mapController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        backgroundColor: AppTheme.dark900,
        body: Center(child: CircularProgressIndicator(color: AppTheme.primary)),
      );
    }

    final initialPos = _currentPosition != null
        ? LatLng(_currentPosition!.latitude, _currentPosition!.longitude)
        : _luandaCenter;

    return Scaffold(
      body: Stack(
        children: [
          // Google Map
          GoogleMap(
            initialCameraPosition: CameraPosition(target: initialPos, zoom: 15),
            onMapCreated: (controller) {
              _mapController = controller;
              controller.setMapStyle(_darkMapStyle);
            },
            markers: _markers,
            polylines: _polylines,
            myLocationEnabled: false,
            myLocationButtonEnabled: false,
            zoomControlsEnabled: false,
            mapToolbarEnabled: false,
            compassEnabled: false,
          ),

          // Top bar
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  // Back button
                  _MapButton(
                    icon: Icons.arrow_back,
                    onTap: widget.onBackToHome,
                  ),
                  const Spacer(),
                  // Online/Offline toggle
                  GestureDetector(
                    onTap: () => _online ? _goOffline() : _goOnline(),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 300),
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                      decoration: BoxDecoration(
                        color: _online
                            ? AppTheme.success.withOpacity(0.9)
                            : AppTheme.dark800.withOpacity(0.9),
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(
                          color: _online ? AppTheme.success : AppTheme.dark600,
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            width: 8,
                            height: 8,
                            decoration: BoxDecoration(
                              color: _online ? Colors.white : AppTheme.dark500,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            _online ? 'Online' : 'Offline',
                            style: TextStyle(
                              color: _online ? Colors.white : AppTheme.dark400,
                              fontWeight: FontWeight.w600,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  // WS indicator
                  if (_online)
                    _MapButton(
                      icon: _wsService.connected ? Icons.wifi : Icons.wifi_off,
                      color: _wsService.connected ? AppTheme.success : AppTheme.danger,
                    ),
                ],
              ),
            ),
          ),

          // Center on me button
          Positioned(
            right: 16,
            bottom: _activeRide != null ? 230 : (_pendingRides.isNotEmpty ? 200 : 100),
            child: _MapButton(
              icon: Icons.my_location,
              onTap: _centerOnDriver,
            ),
          ),

          // Active ride panel
          if (_activeRide != null)
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: _ActiveRidePanel(
                ride: _activeRide!,
                loading: _loadingAction,
                onStart: _startRide,
                onFinish: _finishRide,
                onCancel: _cancelActiveRide,
              ),
            ),

          // Pending rides list
          if (_activeRide == null && _pendingRides.isNotEmpty)
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: _PendingRidesBar(
                rides: _pendingRides,
                onSelect: _showRideDetail,
              ),
            ),

          // Offline message
          if (!_online && _activeRide == null)
            Positioned(
              left: 16,
              right: 16,
              bottom: 24,
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppTheme.dark800.withOpacity(0.95),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppTheme.dark700),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.power_settings_new, color: AppTheme.dark500, size: 32),
                    const SizedBox(height: 8),
                    const Text(
                      'Voce esta offline',
                      style: TextStyle(color: AppTheme.dark400, fontSize: 14),
                    ),
                    const SizedBox(height: 12),
                    PrimaryButton(
                      label: 'Ficar Online',
                      icon: Icons.wifi,
                      onPressed: _goOnline,
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

// =============================================
// Sub-widgets
// =============================================

/// Botao circular no mapa
class _MapButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback? onTap;
  final Color? color;

  const _MapButton({required this.icon, this.onTap, this.color});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: AppTheme.dark800.withOpacity(0.9),
          shape: BoxShape.circle,
          border: Border.all(color: AppTheme.dark700),
        ),
        child: Icon(icon, color: color ?? Colors.white, size: 20),
      ),
    );
  }
}

/// Painel da corrida activa
class _ActiveRidePanel extends StatelessWidget {
  final RideModel ride;
  final bool loading;
  final VoidCallback onStart;
  final VoidCallback onFinish;
  final VoidCallback onCancel;

  const _ActiveRidePanel({
    required this.ride,
    required this.loading,
    required this.onStart,
    required this.onFinish,
    required this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 28),
      decoration: const BoxDecoration(
        color: AppTheme.dark800,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        border: Border(top: BorderSide(color: AppTheme.dark700)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Handle bar
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: AppTheme.dark600,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: 16),
          // Status
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: ride.status == 'em_curso'
                      ? AppTheme.success.withOpacity(0.15)
                      : AppTheme.primary.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  ride.statusLabel,
                  style: TextStyle(
                    color: ride.status == 'em_curso' ? AppTheme.success : AppTheme.primary,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              const Spacer(),
              Text(
                '${ride.valorEstimado?.toStringAsFixed(0) ?? "0"} Kz',
                style: const TextStyle(
                  color: AppTheme.accent,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          // Addresses
          _AddressRow(icon: Icons.circle, color: AppTheme.success, text: ride.origemEndereco),
          const SizedBox(height: 6),
          _AddressRow(icon: Icons.place, color: AppTheme.primary, text: ride.destinoEndereco),
          const SizedBox(height: 6),
          // Distance and time
          Row(
            children: [
              if (ride.distanciaKm != null)
                _InfoChip(Icons.straighten, '${ride.distanciaKm!.toStringAsFixed(1)} km'),
              if (ride.duracaoEstimadaMin != null) ...[
                const SizedBox(width: 12),
                _InfoChip(Icons.schedule, '${ride.duracaoEstimadaMin} min'),
              ],
            ],
          ),
          const SizedBox(height: 16),
          // Action buttons
          if (ride.status == 'aceite' || ride.status == 'motorista_a_caminho')
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: loading ? null : onCancel,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppTheme.danger,
                      side: const BorderSide(color: AppTheme.danger),
                    ),
                    child: const Text('Cancelar'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  flex: 2,
                  child: PrimaryButton(
                    label: 'Cheguei - Iniciar',
                    loading: loading,
                    onPressed: onStart,
                    icon: Icons.play_arrow,
                  ),
                ),
              ],
            ),
          if (ride.status == 'em_curso')
            PrimaryButton(
              label: 'Finalizar Corrida',
              loading: loading,
              onPressed: onFinish,
              icon: Icons.check_circle,
            ),
        ],
      ),
    );
  }
}

class _AddressRow extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String text;
  const _AddressRow({required this.icon, required this.color, required this.text});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 12, color: color),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(color: Colors.white, fontSize: 13),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String text;
  const _InfoChip(this.icon, this.text);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: AppTheme.dark400),
        const SizedBox(width: 4),
        Text(text, style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
      ],
    );
  }
}

/// Barra de corridas pendentes
class _PendingRidesBar extends StatelessWidget {
  final List<RideModel> rides;
  final Function(RideModel) onSelect;

  const _PendingRidesBar({required this.rides, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(0, 12, 0, 24),
      decoration: const BoxDecoration(
        color: AppTheme.dark800,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        border: Border(top: BorderSide(color: AppTheme.dark700)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Text(
              '${rides.length} corrida${rides.length > 1 ? "s" : ""} proxima${rides.length > 1 ? "s" : ""}',
              style: const TextStyle(
                color: AppTheme.accent,
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: 100,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: rides.length,
              itemBuilder: (ctx, i) {
                final ride = rides[i];
                return GestureDetector(
                  onTap: () => onSelect(ride),
                  child: Container(
                    width: 240,
                    margin: const EdgeInsets.only(right: 12),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppTheme.dark900,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppTheme.dark700),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(
                              '${ride.valorEstimado?.toStringAsFixed(0) ?? "0"} Kz',
                              style: const TextStyle(
                                color: AppTheme.accent,
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                            const Spacer(),
                            Text(
                              '${ride.distanciaKm?.toStringAsFixed(1) ?? "?"} km',
                              style: const TextStyle(color: AppTheme.dark400, fontSize: 12),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            const Icon(Icons.circle, size: 8, color: AppTheme.success),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                ride.origemEndereco,
                                style: const TextStyle(color: Colors.white, fontSize: 12),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            const Icon(Icons.place, size: 8, color: AppTheme.primary),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                ride.destinoEndereco,
                                style: const TextStyle(color: AppTheme.dark400, fontSize: 12),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

/// Bottom sheet com detalhes da corrida
class _RideDetailSheet extends StatelessWidget {
  final RideModel ride;
  final VoidCallback onAccept;
  final bool loading;

  const _RideDetailSheet({
    required this.ride,
    required this.onAccept,
    required this.loading,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: AppTheme.dark600,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              const Text(
                'Nova Corrida',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              Text(
                '${ride.valorEstimado?.toStringAsFixed(0) ?? "0"} Kz',
                style: const TextStyle(
                  color: AppTheme.accent,
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _AddressRow(icon: Icons.circle, color: AppTheme.success, text: ride.origemEndereco),
          const SizedBox(height: 8),
          _AddressRow(icon: Icons.place, color: AppTheme.primary, text: ride.destinoEndereco),
          const SizedBox(height: 12),
          Row(
            children: [
              if (ride.distanciaKm != null)
                _InfoChip(Icons.straighten, '${ride.distanciaKm!.toStringAsFixed(1)} km'),
              if (ride.duracaoEstimadaMin != null) ...[
                const SizedBox(width: 16),
                _InfoChip(Icons.schedule, '~${ride.duracaoEstimadaMin} min'),
              ],
            ],
          ),
          const SizedBox(height: 20),
          PrimaryButton(
            label: 'Aceitar Corrida',
            loading: loading,
            onPressed: onAccept,
            icon: Icons.check,
          ),
        ],
      ),
    );
  }
}
