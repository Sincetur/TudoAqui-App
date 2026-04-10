/// Modelo de Parceiro TUDOaqui
class PartnerModel {
  final String id;
  final String userId;
  final String tipo;
  final String nomeNegocio;
  final String? descricao;
  final String? provincia;
  final String? cidade;
  final bool aceitaUnitelMoney;
  final bool aceitaTransferencia;
  final bool aceitaDinheiro;
  final String? unitelMoneyNumero;
  final String? unitelMoneyTitular;
  final String? bancoNome;
  final String? bancoConta;
  final String? bancoIban;
  final String? bancoTitular;
  final String status;
  final String? adminNota;
  final String plano;
  final double taxaMensal;
  final DateTime? createdAt;

  PartnerModel({
    required this.id,
    required this.userId,
    required this.tipo,
    required this.nomeNegocio,
    this.descricao,
    this.provincia,
    this.cidade,
    this.aceitaUnitelMoney = false,
    this.aceitaTransferencia = false,
    this.aceitaDinheiro = true,
    this.unitelMoneyNumero,
    this.unitelMoneyTitular,
    this.bancoNome,
    this.bancoConta,
    this.bancoIban,
    this.bancoTitular,
    this.status = 'pendente',
    this.adminNota,
    this.plano = 'basico',
    this.taxaMensal = 0,
    this.createdAt,
  });

  factory PartnerModel.fromJson(Map<String, dynamic> json) => PartnerModel(
        id: json['id'] ?? '',
        userId: json['user_id'] ?? '',
        tipo: json['tipo'] ?? 'proprietario',
        nomeNegocio: json['nome_negocio'] ?? '',
        descricao: json['descricao'],
        provincia: json['provincia'],
        cidade: json['cidade'],
        aceitaUnitelMoney: json['aceita_unitel_money'] ?? false,
        aceitaTransferencia: json['aceita_transferencia'] ?? false,
        aceitaDinheiro: json['aceita_dinheiro'] ?? true,
        unitelMoneyNumero: json['unitel_money_numero'],
        unitelMoneyTitular: json['unitel_money_titular'],
        bancoNome: json['banco_nome'],
        bancoConta: json['banco_conta'],
        bancoIban: json['banco_iban'],
        bancoTitular: json['banco_titular'],
        status: json['status'] ?? 'pendente',
        adminNota: json['admin_nota'],
        plano: json['plano'] ?? 'basico',
        taxaMensal: (json['taxa_mensal'] ?? 0).toDouble(),
        createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at']) : null,
      );

  bool get isAprovado => status == 'aprovado';
  bool get isPendente => status == 'pendente';

  String get tipoLabel => {
        'motorista': 'Motorista',
        'motoqueiro': 'Motoqueiro',
        'proprietario': 'Proprietario',
        'staff': 'Staff',
        'guia_turista': 'Guia Turista',
        'agente_imobiliario': 'Agente Imobiliario',
        'agente_viagem': 'Agente de Viagem',
      }[tipo] ?? tipo;
}

class PaymentModel {
  final String id;
  final String referencia;
  final String origemTipo;
  final String origemId;
  final String metodo;
  final double valor;
  final double taxaServico;
  final double valorTotal;
  final String status;
  final String? comprovativoRef;
  final String? notas;
  final String? adminNota;
  final DateTime? createdAt;

  PaymentModel({
    required this.id,
    required this.referencia,
    required this.origemTipo,
    required this.origemId,
    required this.metodo,
    required this.valor,
    this.taxaServico = 0,
    required this.valorTotal,
    required this.status,
    this.comprovativoRef,
    this.notas,
    this.adminNota,
    this.createdAt,
  });

  factory PaymentModel.fromJson(Map<String, dynamic> json) => PaymentModel(
        id: json['id'] ?? '',
        referencia: json['referencia'] ?? '',
        origemTipo: json['origem_tipo'] ?? '',
        origemId: json['origem_id'] ?? '',
        metodo: json['metodo'] ?? '',
        valor: (json['valor'] ?? 0).toDouble(),
        taxaServico: (json['taxa_servico'] ?? 0).toDouble(),
        valorTotal: (json['valor_total'] ?? 0).toDouble(),
        status: json['status'] ?? '',
        comprovativoRef: json['comprovativo_ref'],
        notas: json['notas'],
        adminNota: json['admin_nota'],
        createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at']) : null,
      );

  String get metodoLabel => {
        'transferencia': 'Transferencia',
        'dinheiro': 'Dinheiro',
        'multicaixa': 'Multicaixa',
        'unitelmoney': 'Unitel Money',
      }[metodo] ?? metodo;
}
