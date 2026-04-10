/// TUDOaqui SuperApp - Configuracao da API
class ApiConfig {
  // ALTERAR para o URL de producao
  static const String baseUrl = 'https://api.tudoaqui.ao/api/v1';

  // Timeouts
  static const int connectTimeout = 15000;
  static const int receiveTimeout = 15000;

  // Endpoints Auth
  static const String login = '/auth/login';
  static const String verifyOtp = '/auth/verify-otp';
  static const String me = '/auth/me';

  // Endpoints Account
  static const String profile = '/account/profile';
  static const String roleRequest = '/account/role-request';
  static const String roleRequests = '/account/role-requests';

  // Endpoints Partners
  static const String partnerTipos = '/partners/tipos';
  static const String partnerRegister = '/partners/register';
  static const String partnerMe = '/partners/me';
  static const String partnerPayment = '/partners/me/payment';
  static String partnerPaymentInfo(String id) => '/partners/$id/payment-info';
  static String partnerByUser(String uid) => '/partners/by-user/$uid/payment-info';

  // Admin Partners
  static const String adminPartners = '/partners/admin/all';
  static const String adminPartnerStats = '/partners/admin/stats';
  static String adminApprovePartner(String id) => '/partners/admin/$id/approve';
  static String adminSuspendPartner(String id) => '/partners/admin/$id/suspend';
  static String adminRejectPartner(String id) => '/partners/admin/$id/reject';

  // Endpoints Payments
  static const String bankInfo = '/payments/bank-info';
  static const String paymentMethods = '/payments/methods';
  static const String payments = '/payments';
  static String paymentById(String id) => '/payments/$id';
  static String paymentComprovativo(String id) => '/payments/$id/comprovativo';
  static const String adminPayments = '/payments/admin/all';
  static const String adminPaymentStats = '/payments/admin/stats';
  static String confirmPayment(String id) => '/payments/$id/confirm';
  static String rejectPayment(String id) => '/payments/$id/reject';

  // Endpoints Modulos
  static const String events = '/events/';
  static const String marketplaceProducts = '/marketplace/products/';
  static const String alojamento = '/alojamento/properties/';
  static const String turismo = '/turismo/experiences/';
  static const String realestate = '/realestate/properties/';
  static const String restaurantes = '/restaurantes/';
  static String restauranteMenu(String id) => '/restaurantes/$id/menu';
  static const String entregaEstimate = '/entregas/estimate';

  // Admin
  static const String adminStats = '/admin/stats';
  static const String adminUsers = '/admin/users';
  static String adminUserRole(String id) => '/admin/users/$id/role';
}
