import '../services/api_service.dart';
import '../config/api_config.dart';

/// Servico generico para todos os modulos CRUD do SuperApp
class ModuleService {
  final ApiService _api = ApiService();

  // ========= EVENTOS =========
  Future<List<dynamic>> listEvents() async {
    final data = await _api.get(ApiConfig.events);
    return data is List ? data : [];
  }

  Future<Map<String, dynamic>> getEvent(String id) async {
    return await _api.get('${ApiConfig.events}$id');
  }

  Future<Map<String, dynamic>> createEvent(Map<String, dynamic> body) async {
    return await _api.post(ApiConfig.events, body: body);
  }

  // ========= MARKETPLACE =========
  Future<List<dynamic>> listProducts() async {
    final data = await _api.get(ApiConfig.marketplaceProducts);
    return data is List ? data : [];
  }

  Future<Map<String, dynamic>> getProduct(String id) async {
    return await _api.get('${ApiConfig.marketplaceProducts}$id');
  }

  Future<List<dynamic>> listCategories() async {
    final data = await _api.get('/marketplace/categories');
    return data is List ? data : [];
  }

  Future<Map<String, dynamic>> createProduct(Map<String, dynamic> body) async {
    return await _api.post(ApiConfig.marketplaceProducts, body: body);
  }

  Future<Map<String, dynamic>> createOrder(Map<String, dynamic> body) async {
    return await _api.post('/marketplace/orders', body: body);
  }

  Future<List<dynamic>> listMyOrders() async {
    final data = await _api.get('/marketplace/orders/my');
    return data is List ? data : [];
  }

  // ========= ALOJAMENTO =========
  Future<List<dynamic>> listAlojamento() async {
    final data = await _api.get(ApiConfig.alojamento);
    return data is List ? data : [];
  }

  Future<Map<String, dynamic>> getAlojamento(String id) async {
    return await _api.get('${ApiConfig.alojamento}$id');
  }

  Future<Map<String, dynamic>> createAlojamento(Map<String, dynamic> body) async {
    return await _api.post(ApiConfig.alojamento, body: body);
  }

  Future<Map<String, dynamic>> createBooking(Map<String, dynamic> body) async {
    return await _api.post('/alojamento/bookings', body: body);
  }

  Future<List<dynamic>> listMyBookings() async {
    final data = await _api.get('/alojamento/bookings/my');
    return data is List ? data : [];
  }

  // ========= TURISMO =========
  Future<List<dynamic>> listExperiences() async {
    final data = await _api.get(ApiConfig.turismo);
    return data is List ? data : [];
  }

  Future<Map<String, dynamic>> getExperience(String id) async {
    return await _api.get('${ApiConfig.turismo}$id');
  }

  Future<Map<String, dynamic>> createExperience(Map<String, dynamic> body) async {
    return await _api.post(ApiConfig.turismo, body: body);
  }

  Future<List<dynamic>> listSchedules(String id) async {
    final data = await _api.get('${ApiConfig.turismo}$id/schedules');
    return data is List ? data : [];
  }

  Future<Map<String, dynamic>> createTurismoBooking(Map<String, dynamic> body) async {
    return await _api.post('/turismo/bookings', body: body);
  }

  Future<List<dynamic>> listMyTurismoBookings() async {
    final data = await _api.get('/turismo/bookings/my');
    return data is List ? data : [];
  }

  // ========= REAL ESTATE =========
  Future<List<dynamic>> listImoveis() async {
    final data = await _api.get(ApiConfig.realestate);
    return data is List ? data : [];
  }

  Future<Map<String, dynamic>> getImovel(String id) async {
    return await _api.get('${ApiConfig.realestate}$id');
  }

  Future<Map<String, dynamic>> createImovel(Map<String, dynamic> body) async {
    return await _api.post(ApiConfig.realestate, body: body);
  }

  Future<Map<String, dynamic>> createLead(Map<String, dynamic> body) async {
    return await _api.post('/realestate/leads', body: body);
  }

  Future<List<dynamic>> listAgents() async {
    final data = await _api.get('/realestate/agents');
    return data is List ? data : [];
  }

  Future<List<dynamic>> listMyLeads() async {
    final data = await _api.get('/realestate/leads');
    return data is List ? data : [];
  }

  // ========= ENTREGAS =========
  Future<Map<String, dynamic>> estimateDelivery(Map<String, dynamic> body) async {
    return await _api.post(ApiConfig.entregaEstimate, body: body);
  }

  Future<Map<String, dynamic>> createDelivery(Map<String, dynamic> body) async {
    return await _api.post('/entregas', body: body);
  }

  Future<List<dynamic>> listMyDeliveries() async {
    final data = await _api.get('/entregas/my');
    return data is List ? data : [];
  }

  Future<Map<String, dynamic>> getDelivery(String id) async {
    return await _api.get('/entregas/$id');
  }

  // ========= EVENTOS - Compra de Tickets =========
  Future<List<dynamic>> purchaseTicket(String ticketTypeId, int quantidade) async {
    final data = await _api.post('/events/tickets/purchase', body: {
      'ticket_type_id': ticketTypeId,
      'quantidade': quantidade,
    });
    return data is List ? data : [data];
  }

  // ========= RESTAURANTES =========
  Future<List<dynamic>> listRestaurants() async {
    final data = await _api.get(ApiConfig.restaurantes);
    return data is List ? data : [];
  }

  Future<Map<String, dynamic>> getRestaurant(String id) async {
    return await _api.get('${ApiConfig.restaurantes}$id');
  }

  Future<List<dynamic>> getMenu(String id) async {
    final data = await _api.get(ApiConfig.restauranteMenu(id));
    return data is List ? data : [];
  }

  Future<Map<String, dynamic>> createFoodOrder(Map<String, dynamic> body) async {
    return await _api.post('/restaurantes/orders', body: body);
  }

  Future<List<dynamic>> listMyFoodOrders() async {
    final data = await _api.get('/restaurantes/orders/my');
    return data is List ? data : [];
  }

  // ========= DRIVERS/ENTREGAS MANAGEMENT =========
  Future<List<dynamic>> listPendingDeliveries(double lat, double lon) async {
    final data = await _api.get('/entregas/driver/available?latitude=$lat&longitude=$lon');
    return data is List ? data : [];
  }

  Future<Map<String, dynamic>> acceptDelivery(String id) async {
    return await _api.post('/entregas/$id/accept');
  }

  Future<Map<String, dynamic>> pickupDelivery(String id, {String? code}) async {
    return await _api.post('/entregas/$id/start-pickup', body: code != null ? {'codigo': code} : null);
  }

  Future<Map<String, dynamic>> confirmPickup(String id, {String? code}) async {
    return await _api.post('/entregas/$id/confirm-pickup', body: code != null ? {'codigo': code} : null);
  }

  Future<Map<String, dynamic>> startTransit(String id) async {
    return await _api.post('/entregas/$id/start-transit');
  }

  Future<Map<String, dynamic>> completeDelivery(String id, {String? code}) async {
    return await _api.post('/entregas/$id/confirm-delivery', body: code != null ? {'codigo': code} : null);
  }
}
