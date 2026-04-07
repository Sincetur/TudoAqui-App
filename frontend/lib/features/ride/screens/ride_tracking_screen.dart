import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../core/config/theme.dart';
import '../../../core/config/app_config.dart';
import '../../../core/config/routes.dart';
import '../../../core/api/api_client.dart';

class RideTrackingScreen extends StatefulWidget {
  final String? rideId;
  
  const RideTrackingScreen({super.key, this.rideId});

  @override
  State<RideTrackingScreen> createState() => _RideTrackingScreenState();
}

class _RideTrackingScreenState extends State<RideTrackingScreen> {
  final ApiClient _apiClient = ApiClient();
  GoogleMapController? _mapController;
  WebSocketChannel? _channel;
  Timer? _pollTimer;
  
  // Ride data
  Map<String, dynamic>? _ride;
  Map<String, dynamic>? _driver;
  
  // Locations
  LatLng? _pickupLocation;
  LatLng? _dropoffLocation;
  LatLng? _driverLocation;
  
  // State
  bool _isLoading = true;
  String _status = 'solicitada';
  
  // Markers
  final Set<Marker> _markers = {};
  
  @override
  void initState() {
    super.initState();
    _loadRide();
    _connectWebSocket();
  }
  
  @override
  void dispose() {
    _channel?.sink.close();
    _pollTimer?.cancel();
    super.dispose();
  }
  
  Future<void> _loadRide() async {
    if (widget.rideId == null) {
      // Try to get current ride
      try {
        final response = await _apiClient.getCurrentRide();
        if (response.data != null) {
          _processRideData(response.data);
        } else {
          Navigator.pop(context);
        }
      } catch (e) {
        Navigator.pop(context);
      }
    } else {
      try {
        final response = await _apiClient.getRide(widget.rideId!);
        _processRideData(response.data);
      } catch (e) {
        _showError('Erro ao carregar corrida');
      }
    }
  }
  
  void _processRideData(Map<String, dynamic> data) {
    setState(() {
      _ride = data;
      _status = data['status'];
      _driver = data['motorista'];
      
      _pickupLocation = LatLng(
        data['origem_latitude'],
        data['origem_longitude'],
      );
      _dropoffLocation = LatLng(
        data['destino_latitude'],
        data['destino_longitude'],
      );
      
      _isLoading = false;
      _updateMarkers();
    });
    
    // Fit map to show both points
    if (_pickupLocation != null && _dropoffLocation != null) {
      _fitBounds();
    }
  }
  
  void _connectWebSocket() async {
    try {
      final token = await _apiClient.getAccessToken();
      if (token == null) return;
      
      final wsUrl = '${EnvironmentConfig.wsBaseUrl}/client/$token';
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      _channel!.stream.listen(
        (message) {
          final data = jsonDecode(message);
          _handleWebSocketMessage(data);
        },
        onError: (error) {
          debugPrint('WebSocket error: $error');
          // Fallback to polling
          _startPolling();
        },
        onDone: () {
          debugPrint('WebSocket closed');
        },
      );
      
      // Join ride room
      if (widget.rideId != null) {
        _channel!.sink.add(jsonEncode({
          'type': 'join_ride',
          'ride_id': widget.rideId,
        }));
      }
    } catch (e) {
      debugPrint('WebSocket connection failed: $e');
      _startPolling();
    }
  }
  
  void _startPolling() {
    _pollTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      _loadRide();
    });
  }
  
  void _handleWebSocketMessage(Map<String, dynamic> data) {
    final type = data['type'];
    
    switch (type) {
      case 'ride_accepted':
        setState(() {
          _status = 'aceite';
          _driver = data['driver'];
        });
        _showNotification('Motorista a caminho!');
        break;
        
      case 'driver_location':
        final location = data['location'];
        setState(() {
          _driverLocation = LatLng(
            location['latitude'],
            location['longitude'],
          );
          _updateMarkers();
        });
        break;
        
      case 'ride_started':
        setState(() => _status = 'em_curso');
        _showNotification('Corrida iniciada!');
        break;
        
      case 'ride_finished':
        setState(() => _status = 'finalizada');
        _showRideCompleted(data['valor_final']);
        break;
        
      case 'ride_cancelled':
        _showRideCancelled(data['reason']);
        break;
    }
  }
  
  void _updateMarkers() {
    _markers.clear();
    
    if (_pickupLocation != null) {
      _markers.add(
        Marker(
          markerId: const MarkerId('pickup'),
          position: _pickupLocation!,
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen),
          infoWindow: const InfoWindow(title: 'Origem'),
        ),
      );
    }
    
    if (_dropoffLocation != null) {
      _markers.add(
        Marker(
          markerId: const MarkerId('dropoff'),
          position: _dropoffLocation!,
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed),
          infoWindow: const InfoWindow(title: 'Destino'),
        ),
      );
    }
    
    if (_driverLocation != null) {
      _markers.add(
        Marker(
          markerId: const MarkerId('driver'),
          position: _driverLocation!,
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
          infoWindow: const InfoWindow(title: 'Motorista'),
        ),
      );
    }
    
    setState(() {});
  }
  
  void _fitBounds() {
    if (_pickupLocation == null || _dropoffLocation == null) return;
    
    final bounds = LatLngBounds(
      southwest: LatLng(
        _pickupLocation!.latitude < _dropoffLocation!.latitude
            ? _pickupLocation!.latitude
            : _dropoffLocation!.latitude,
        _pickupLocation!.longitude < _dropoffLocation!.longitude
            ? _pickupLocation!.longitude
            : _dropoffLocation!.longitude,
      ),
      northeast: LatLng(
        _pickupLocation!.latitude > _dropoffLocation!.latitude
            ? _pickupLocation!.latitude
            : _dropoffLocation!.latitude,
        _pickupLocation!.longitude > _dropoffLocation!.longitude
            ? _pickupLocation!.longitude
            : _dropoffLocation!.longitude,
      ),
    );
    
    _mapController?.animateCamera(
      CameraUpdate.newLatLngBounds(bounds, 100),
    );
  }
  
  Future<void> _cancelRide() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cancelar corrida?'),
        content: const Text('Tem certeza que deseja cancelar esta corrida?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Não'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: AppColors.error),
            child: const Text('Sim, cancelar'),
          ),
        ],
      ),
    );
    
    if (confirm == true && widget.rideId != null) {
      try {
        await _apiClient.cancelRide(widget.rideId!);
        if (mounted) {
          Navigator.pushReplacementNamed(context, AppRoutes.home);
        }
      } catch (e) {
        _showError('Erro ao cancelar corrida');
      }
    }
  }
  
  void _showNotification(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppColors.success,
      ),
    );
  }
  
  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppColors.error,
      ),
    );
  }
  
  void _showRideCompleted(double valor) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Corrida finalizada! 🎉'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.check_circle,
              color: AppColors.success,
              size: 64,
            ),
            const SizedBox(height: 16),
            Text(
              '${valor.toStringAsFixed(2)} Kz',
              style: AppTypography.headline2,
            ),
            const SizedBox(height: 8),
            const Text('Obrigado por viajar connosco!'),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Navigate to rating screen
              Navigator.pushReplacementNamed(context, AppRoutes.home);
            },
            child: const Text('Avaliar'),
          ),
        ],
      ),
    );
  }
  
  void _showRideCancelled(String? reason) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Corrida cancelada'),
        content: Text(reason ?? 'A corrida foi cancelada.'),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, AppRoutes.home);
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
  
  String _getStatusText() {
    switch (_status) {
      case 'solicitada':
        return 'Procurando motorista...';
      case 'aceite':
        return 'Motorista a caminho';
      case 'motorista_a_caminho':
        return 'Motorista a caminho';
      case 'em_curso':
        return 'Em viagem';
      case 'finalizada':
        return 'Corrida finalizada';
      default:
        return _status;
    }
  }
  
  IconData _getStatusIcon() {
    switch (_status) {
      case 'solicitada':
        return Icons.search;
      case 'aceite':
      case 'motorista_a_caminho':
        return Icons.directions_car;
      case 'em_curso':
        return Icons.navigation;
      case 'finalizada':
        return Icons.check_circle;
      default:
        return Icons.info;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Map
          _isLoading
              ? const Center(child: CircularProgressIndicator())
              : GoogleMap(
                  initialCameraPosition: CameraPosition(
                    target: _pickupLocation ?? const LatLng(-8.8383, 13.2344),
                    zoom: 14,
                  ),
                  onMapCreated: (controller) {
                    _mapController = controller;
                    _fitBounds();
                  },
                  markers: _markers,
                  myLocationEnabled: true,
                  myLocationButtonEnabled: false,
                  zoomControlsEnabled: false,
                ),
          
          // Status Card (Top)
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(
                        _getStatusIcon(),
                        color: AppColors.primary,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            _getStatusText(),
                            style: AppTypography.bodyLarge.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          if (_status == 'solicitada')
                            const SizedBox(
                              height: 4,
                              child: LinearProgressIndicator(),
                            ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          
          // Bottom Sheet
          if (!_isLoading)
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(24),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 20,
                      offset: const Offset(0, -5),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Handle
                    Container(
                      width: 40,
                      height: 4,
                      margin: const EdgeInsets.only(bottom: 20),
                      decoration: BoxDecoration(
                        color: AppColors.border,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                    
                    // Driver info (if assigned)
                    if (_driver != null) ...[
                      Row(
                        children: [
                          // Driver avatar
                          CircleAvatar(
                            radius: 28,
                            backgroundColor: AppColors.primary,
                            child: Text(
                              (_driver!['nome'] ?? 'M')[0].toUpperCase(),
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _driver!['nome'] ?? 'Motorista',
                                  style: AppTypography.bodyLarge.copyWith(
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                Row(
                                  children: [
                                    const Icon(
                                      Icons.star,
                                      color: AppColors.warning,
                                      size: 16,
                                    ),
                                    const SizedBox(width: 4),
                                    Text(
                                      '${_driver!['rating_medio'] ?? 5.0}',
                                      style: AppTypography.bodySmall,
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      '${_driver!['veiculo'] ?? ''} • ${_driver!['matricula'] ?? ''}',
                                      style: AppTypography.bodySmall,
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                          // Call button
                          IconButton(
                            icon: const Icon(Icons.phone, color: AppColors.primary),
                            onPressed: () {
                              // TODO: Implement call
                            },
                          ),
                        ],
                      ),
                      const Divider(height: 32),
                    ],
                    
                    // Ride info
                    Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  const Icon(
                                    Icons.circle,
                                    color: AppColors.success,
                                    size: 12,
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      _ride?['origem_endereco'] ?? '',
                                      style: AppTypography.bodySmall,
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Row(
                                children: [
                                  const Icon(
                                    Icons.location_on,
                                    color: AppColors.error,
                                    size: 12,
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      _ride?['destino_endereco'] ?? '',
                                      style: AppTypography.bodySmall,
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 8,
                          ),
                          decoration: BoxDecoration(
                            color: AppColors.primary.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            '${_ride?['valor_estimado'] ?? 0} Kz',
                            style: AppTypography.bodyLarge.copyWith(
                              fontWeight: FontWeight.bold,
                              color: AppColors.primary,
                            ),
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 20),
                    
                    // Cancel button (only if ride is not in progress)
                    if (_status == 'solicitada' || _status == 'aceite')
                      OutlinedButton(
                        onPressed: _cancelRide,
                        style: OutlinedButton.styleFrom(
                          foregroundColor: AppColors.error,
                          side: const BorderSide(color: AppColors.error),
                        ),
                        child: const Text('Cancelar corrida'),
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
