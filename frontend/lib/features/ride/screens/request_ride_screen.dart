import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';

import '../../../core/config/theme.dart';
import '../../../core/config/routes.dart';
import '../../../core/api/api_client.dart';

class RequestRideScreen extends StatefulWidget {
  const RequestRideScreen({super.key});

  @override
  State<RequestRideScreen> createState() => _RequestRideScreenState();
}

class _RequestRideScreenState extends State<RequestRideScreen> {
  GoogleMapController? _mapController;
  final ApiClient _apiClient = ApiClient();
  
  // Location
  LatLng? _currentLocation;
  LatLng? _pickupLocation;
  LatLng? _dropoffLocation;
  
  // Address
  String _pickupAddress = '';
  String _dropoffAddress = '';
  
  // State
  bool _isLoading = true;
  bool _isEstimating = false;
  bool _isRequesting = false;
  
  // Estimate
  Map<String, dynamic>? _estimate;
  
  // Markers
  final Set<Marker> _markers = {};
  
  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }
  
  Future<void> _getCurrentLocation() async {
    try {
      // Check permissions
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      
      if (permission == LocationPermission.deniedForever) {
        setState(() => _isLoading = false);
        return;
      }
      
      // Get current position
      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      
      setState(() {
        _currentLocation = LatLng(position.latitude, position.longitude);
        _pickupLocation = _currentLocation;
        _pickupAddress = 'Minha localização';
        _isLoading = false;
        _updateMarkers();
      });
      
      _mapController?.animateCamera(
        CameraUpdate.newLatLngZoom(_currentLocation!, 15),
      );
    } catch (e) {
      setState(() => _isLoading = false);
      debugPrint('Error getting location: $e');
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
          infoWindow: InfoWindow(title: 'Origem', snippet: _pickupAddress),
        ),
      );
    }
    
    if (_dropoffLocation != null) {
      _markers.add(
        Marker(
          markerId: const MarkerId('dropoff'),
          position: _dropoffLocation!,
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed),
          infoWindow: InfoWindow(title: 'Destino', snippet: _dropoffAddress),
        ),
      );
    }
    
    setState(() {});
  }
  
  Future<void> _getEstimate() async {
    if (_pickupLocation == null || _dropoffLocation == null) return;
    
    setState(() => _isEstimating = true);
    
    try {
      final response = await _apiClient.estimateRide(
        origemLat: _pickupLocation!.latitude,
        origemLon: _pickupLocation!.longitude,
        origemEndereco: _pickupAddress,
        destinoLat: _dropoffLocation!.latitude,
        destinoLon: _dropoffLocation!.longitude,
        destinoEndereco: _dropoffAddress,
      );
      
      setState(() {
        _estimate = response.data;
        _isEstimating = false;
      });
    } catch (e) {
      setState(() => _isEstimating = false);
      _showError('Erro ao calcular estimativa');
    }
  }
  
  Future<void> _requestRide() async {
    if (_pickupLocation == null || _dropoffLocation == null) return;
    
    setState(() => _isRequesting = true);
    
    try {
      final response = await _apiClient.requestRide(
        origemLat: _pickupLocation!.latitude,
        origemLon: _pickupLocation!.longitude,
        origemEndereco: _pickupAddress,
        destinoLat: _dropoffLocation!.latitude,
        destinoLon: _dropoffLocation!.longitude,
        destinoEndereco: _dropoffAddress,
      );
      
      // Navigate to tracking screen
      if (mounted) {
        Navigator.pushReplacementNamed(
          context,
          AppRoutes.rideTracking,
          arguments: {'rideId': response.data['id']},
        );
      }
    } catch (e) {
      setState(() => _isRequesting = false);
      _showError('Erro ao solicitar corrida');
    }
  }
  
  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppColors.error,
      ),
    );
  }
  
  void _openLocationSearch(bool isPickup) async {
    // TODO: Implement Google Places Autocomplete
    // For now, show a simple dialog
    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (context) => _LocationSearchDialog(isPickup: isPickup),
    );
    
    if (result != null) {
      setState(() {
        if (isPickup) {
          _pickupLocation = LatLng(result['lat'], result['lng']);
          _pickupAddress = result['address'];
        } else {
          _dropoffLocation = LatLng(result['lat'], result['lng']);
          _dropoffAddress = result['address'];
        }
        _updateMarkers();
      });
      
      // Get estimate if both locations are set
      if (_pickupLocation != null && _dropoffLocation != null) {
        _getEstimate();
        
        // Fit bounds
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
                    target: _currentLocation ?? const LatLng(-8.8383, 13.2344), // Luanda default
                    zoom: 14,
                  ),
                  onMapCreated: (controller) => _mapController = controller,
                  markers: _markers,
                  myLocationEnabled: true,
                  myLocationButtonEnabled: false,
                  zoomControlsEnabled: false,
                  mapToolbarEnabled: false,
                ),
          
          // Top Bar
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  // Back button
                  Container(
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 10,
                        ),
                      ],
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.arrow_back),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ),
                  const Spacer(),
                  // My location button
                  Container(
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 10,
                        ),
                      ],
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.my_location),
                      onPressed: () {
                        if (_currentLocation != null) {
                          _mapController?.animateCamera(
                            CameraUpdate.newLatLngZoom(_currentLocation!, 15),
                          );
                        }
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          // Bottom Sheet
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
                  
                  // Location inputs
                  _buildLocationInput(
                    icon: Icons.circle,
                    iconColor: AppColors.success,
                    hint: 'Onde está?',
                    value: _pickupAddress,
                    onTap: () => _openLocationSearch(true),
                  ),
                  
                  const SizedBox(height: 12),
                  
                  _buildLocationInput(
                    icon: Icons.location_on,
                    iconColor: AppColors.error,
                    hint: 'Para onde vai?',
                    value: _dropoffAddress,
                    onTap: () => _openLocationSearch(false),
                  ),
                  
                  // Estimate
                  if (_estimate != null) ...[
                    const SizedBox(height: 20),
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: AppColors.background,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _buildEstimateItem(
                            icon: Icons.straighten,
                            value: '${_estimate!['distancia_km']} km',
                            label: 'Distância',
                          ),
                          _buildEstimateItem(
                            icon: Icons.access_time,
                            value: '${_estimate!['duracao_estimada_min']} min',
                            label: 'Tempo',
                          ),
                          _buildEstimateItem(
                            icon: Icons.payments,
                            value: '${_estimate!['valor_estimado']} Kz',
                            label: 'Preço',
                            highlight: true,
                          ),
                        ],
                      ),
                    ),
                  ],
                  
                  const SizedBox(height: 20),
                  
                  // Request button
                  ElevatedButton(
                    onPressed: _dropoffLocation != null && !_isRequesting
                        ? _requestRide
                        : null,
                    child: _isRequesting
                        ? const SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                Colors.white,
                              ),
                            ),
                          )
                        : const Text('Pedir Tuendi'),
                  ),
                ],
              ),
            ),
          ),
          
          // Loading overlay
          if (_isEstimating)
            Container(
              color: Colors.black.withOpacity(0.3),
              child: const Center(
                child: CircularProgressIndicator(),
              ),
            ),
        ],
      ),
    );
  }
  
  Widget _buildLocationInput({
    required IconData icon,
    required Color iconColor,
    required String hint,
    required String value,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.background,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.border),
        ),
        child: Row(
          children: [
            Icon(icon, color: iconColor, size: 16),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                value.isEmpty ? hint : value,
                style: AppTypography.bodyMedium.copyWith(
                  color: value.isEmpty ? AppColors.textSecondary : AppColors.text,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            const Icon(Icons.chevron_right, color: AppColors.textSecondary),
          ],
        ),
      ),
    );
  }
  
  Widget _buildEstimateItem({
    required IconData icon,
    required String value,
    required String label,
    bool highlight = false,
  }) {
    return Column(
      children: [
        Icon(
          icon,
          color: highlight ? AppColors.primary : AppColors.textSecondary,
          size: 20,
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: AppTypography.bodyLarge.copyWith(
            fontWeight: FontWeight.bold,
            color: highlight ? AppColors.primary : AppColors.text,
          ),
        ),
        Text(
          label,
          style: AppTypography.caption,
        ),
      ],
    );
  }
}

// Simple location search dialog (placeholder for Google Places)
class _LocationSearchDialog extends StatefulWidget {
  final bool isPickup;
  
  const _LocationSearchDialog({required this.isPickup});

  @override
  State<_LocationSearchDialog> createState() => _LocationSearchDialogState();
}

class _LocationSearchDialogState extends State<_LocationSearchDialog> {
  final _controller = TextEditingController();
  
  // Sample locations in Luanda
  final _sampleLocations = [
    {'address': 'Mutamba, Luanda', 'lat': -8.8147, 'lng': 13.2302},
    {'address': 'Talatona, Luanda', 'lat': -8.9167, 'lng': 13.1833},
    {'address': 'Viana, Luanda', 'lat': -8.9000, 'lng': 13.3667},
    {'address': 'Maianga, Luanda', 'lat': -8.8333, 'lng': 13.2333},
    {'address': 'Kilamba, Luanda', 'lat': -8.9333, 'lng': 13.2167},
    {'address': 'Aeroporto 4 de Fevereiro', 'lat': -8.8583, 'lng': 13.2311},
  ];
  
  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              widget.isPickup ? 'Onde está?' : 'Para onde vai?',
              style: AppTypography.headline3,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _controller,
              decoration: const InputDecoration(
                hintText: 'Pesquisar local...',
                prefixIcon: Icon(Icons.search),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 250,
              child: ListView.builder(
                itemCount: _sampleLocations.length,
                itemBuilder: (context, index) {
                  final location = _sampleLocations[index];
                  return ListTile(
                    leading: const Icon(Icons.location_on_outlined),
                    title: Text(location['address'] as String),
                    onTap: () => Navigator.pop(context, location),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
