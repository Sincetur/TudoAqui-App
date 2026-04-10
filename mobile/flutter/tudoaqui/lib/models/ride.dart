/// Modelo de Corrida
class RideModel {
  final String id;
  final String clienteId;
  final String? motoristaId;
  final String origemEndereco;
  final double origemLatitude;
  final double origemLongitude;
  final String destinoEndereco;
  final double destinoLatitude;
  final double destinoLongitude;
  final double? distanciaKm;
  final int? duracaoEstimadaMin;
  final double? valorEstimado;
  final double? valorFinal;
  final String status;
  final DateTime? solicitadaAt;
  final DateTime? aceiteAt;
  final DateTime? iniciadaAt;
  final DateTime? finalizadaAt;

  RideModel({
    required this.id,
    required this.clienteId,
    this.motoristaId,
    required this.origemEndereco,
    required this.origemLatitude,
    required this.origemLongitude,
    required this.destinoEndereco,
    required this.destinoLatitude,
    required this.destinoLongitude,
    this.distanciaKm,
    this.duracaoEstimadaMin,
    this.valorEstimado,
    this.valorFinal,
    required this.status,
    this.solicitadaAt,
    this.aceiteAt,
    this.iniciadaAt,
    this.finalizadaAt,
  });

  factory RideModel.fromJson(Map<String, dynamic> json) => RideModel(
        id: json['id'] ?? '',
        clienteId: json['cliente_id'] ?? '',
        motoristaId: json['motorista_id'],
        origemEndereco: json['origem_endereco'] ?? '',
        origemLatitude: (json['origem_latitude'] ?? 0).toDouble(),
        origemLongitude: (json['origem_longitude'] ?? 0).toDouble(),
        destinoEndereco: json['destino_endereco'] ?? '',
        destinoLatitude: (json['destino_latitude'] ?? 0).toDouble(),
        destinoLongitude: (json['destino_longitude'] ?? 0).toDouble(),
        distanciaKm: json['distancia_km']?.toDouble(),
        duracaoEstimadaMin: json['duracao_estimada_min'],
        valorEstimado: json['valor_estimado']?.toDouble(),
        valorFinal: json['valor_final']?.toDouble(),
        status: json['status'] ?? 'solicitada',
        solicitadaAt: json['solicitada_at'] != null
            ? DateTime.tryParse(json['solicitada_at'])
            : null,
        aceiteAt: json['aceite_at'] != null
            ? DateTime.tryParse(json['aceite_at'])
            : null,
        iniciadaAt: json['iniciada_at'] != null
            ? DateTime.tryParse(json['iniciada_at'])
            : null,
        finalizadaAt: json['finalizada_at'] != null
            ? DateTime.tryParse(json['finalizada_at'])
            : null,
      );

  bool get isActive => [
        'solicitada',
        'aceite',
        'motorista_a_caminho',
        'em_curso'
      ].contains(status);

  bool get isCompleted => status == 'finalizada';

  String get statusLabel => {
        'solicitada': 'A procurar motorista',
        'aceite': 'Motorista a caminho',
        'motorista_a_caminho': 'Motorista a caminho',
        'em_curso': 'Em curso',
        'finalizada': 'Finalizada',
        'cancelada_cliente': 'Cancelada',
        'cancelada_motorista': 'Cancelada pelo motorista',
      }[status] ??
      status;
}

/// Estimativa de corrida
class RideEstimate {
  final double distanciaKm;
  final int duracaoEstimadaMin;
  final double valorEstimado;
  final int motoristasDisponiveis;

  RideEstimate({
    required this.distanciaKm,
    required this.duracaoEstimadaMin,
    required this.valorEstimado,
    required this.motoristasDisponiveis,
  });

  factory RideEstimate.fromJson(Map<String, dynamic> json) => RideEstimate(
        distanciaKm: (json['distancia_km'] ?? 0).toDouble(),
        duracaoEstimadaMin: json['duracao_estimada_min'] ?? 0,
        valorEstimado: (json['valor_estimado'] ?? 0).toDouble(),
        motoristasDisponiveis: json['motoristas_disponiveis'] ?? 0,
      );
}
