/// Modelo de Utilizador TUDOaqui
class UserModel {
  final String id;
  final String telefone;
  final String? nome;
  final String? email;
  final String role;
  final String status;
  final DateTime? createdAt;

  UserModel({
    required this.id,
    required this.telefone,
    this.nome,
    this.email,
    required this.role,
    this.status = 'ativo',
    this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) => UserModel(
        id: json['id'] ?? '',
        telefone: json['telefone'] ?? '',
        nome: json['nome'],
        email: json['email'],
        role: json['role'] ?? 'cliente',
        status: json['status'] ?? 'ativo',
        createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at']) : null,
      );

  bool get isAdmin => role == 'admin';
  bool get isMotorista => role == 'motorista';
  bool get isMotoqueiro => role == 'motoqueiro';
  bool get isProprietario => role == 'proprietario';
  bool get isGuiaTurista => role == 'guia_turista';
  bool get isAgenteImobiliario => role == 'agente_imobiliario';
  bool get isAgenteViagem => role == 'agente_viagem';
  bool get isStaff => role == 'staff';
  bool get isCliente => role == 'cliente';

  bool get isPartnerRole => [
        'motorista', 'motoqueiro', 'proprietario', 'guia_turista',
        'agente_imobiliario', 'agente_viagem', 'staff'
      ].contains(role);

  String get roleLabel => {
        'cliente': 'Cliente',
        'motorista': 'Motorista',
        'motoqueiro': 'Motoqueiro',
        'proprietario': 'Proprietario',
        'guia_turista': 'Guia Turista',
        'agente_imobiliario': 'Agente Imobiliario',
        'agente_viagem': 'Agente de Viagem',
        'staff': 'Staff',
        'admin': 'Administrador',
      }[role] ?? role;
}
