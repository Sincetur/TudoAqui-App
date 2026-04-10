import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/cart_service.dart';
import '../../services/module_service.dart';
import '../../widgets/common.dart';

/// Ecra de checkout unificado para todos os modulos
class CheckoutScreen extends StatefulWidget {
  final String titulo;
  final Map<String, dynamic>? extraData;
  const CheckoutScreen({super.key, required this.titulo, this.extraData});

  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  final _svc = ModuleService();
  final _enderecoCtrl = TextEditingController();
  final _telCtrl = TextEditingController();
  final _notasCtrl = TextEditingController();
  String _paymentMethod = 'cash';
  bool _submitting = false;
  bool _success = false;
  Map<String, dynamic>? _orderResult;

  @override
  Widget build(BuildContext context) {
    final cart = context.watch<CartProvider>();

    if (_success) return _SuccessView(result: _orderResult, titulo: widget.titulo);

    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(title: Text(widget.titulo), backgroundColor: AppTheme.dark800),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          // Items
          const Text('Resumo', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 8),
          ...cart.items.map((item) => _CartItemTile(
            item: item,
            onRemove: () => cart.removeItem(item.id),
            onQtyChanged: (q) => cart.updateQuantity(item.id, q),
          )),

          if (cart.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 32),
              child: EmptyState(icon: Icons.shopping_cart, title: 'Carrinho vazio', subtitle: 'Adicione itens para continuar'),
            ),

          if (!cart.isEmpty) ...[
            const Divider(color: AppTheme.dark700),
            // Totais
            _TotalRow('Subtotal', cart.subtotal),
            _TotalRow('Taxa de servico', cart.subtotal * 0.05),
            _TotalRow('Total', cart.subtotal * 1.05, bold: true),

            const SizedBox(height: 20),

            // Endereco
            const Text('Entrega', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 8),
            _InputField(ctrl: _enderecoCtrl, label: 'Endereco de entrega', icon: Icons.place),
            _InputField(ctrl: _telCtrl, label: 'Telefone (+244)', icon: Icons.phone),
            _InputField(ctrl: _notasCtrl, label: 'Notas (opcional)', icon: Icons.note),

            const SizedBox(height: 20),

            // Pagamento
            const Text('Pagamento', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 8),
            _PaymentOption(
              label: 'Dinheiro (Cash)',
              icon: Icons.money,
              selected: _paymentMethod == 'cash',
              onTap: () => setState(() => _paymentMethod = 'cash'),
            ),
            _PaymentOption(
              label: 'Transferencia Bancaria (BAI)',
              icon: Icons.account_balance,
              selected: _paymentMethod == 'bank_transfer',
              onTap: () => setState(() => _paymentMethod = 'bank_transfer'),
            ),
            _PaymentOption(
              label: 'Unitel Money',
              icon: Icons.phone_android,
              selected: _paymentMethod == 'unitel_money',
              onTap: () => setState(() => _paymentMethod = 'unitel_money'),
            ),

            const SizedBox(height: 24),

            PrimaryButton(
              label: 'Confirmar Pedido - ${(cart.subtotal * 1.05).toStringAsFixed(0)} Kz',
              icon: Icons.check_circle,
              loading: _submitting,
              onPressed: cart.isEmpty ? null : _submitOrder,
            ),
          ],
        ]),
      ),
    );
  }

  Future<void> _submitOrder() async {
    final cart = context.read<CartProvider>();
    if (cart.isEmpty) return;

    if (_enderecoCtrl.text.length < 5) {
      _snack('Preencha o endereco de entrega', AppTheme.danger);
      return;
    }
    if (_telCtrl.text.length < 9) {
      _snack('Preencha o telefone', AppTheme.danger);
      return;
    }

    setState(() => _submitting = true);
    try {
      final firstItem = cart.items.first;
      Map<String, dynamic>? result;

      switch (firstItem.type) {
        case CartItemType.menuItem:
          result = await _svc.createFoodOrder({
            'restaurant_id': cart.contextId,
            'items': cart.items.map((i) => {'menu_item_id': i.id, 'quantidade': i.quantity}).toList(),
            'endereco_entrega': _enderecoCtrl.text,
            'latitude_entrega': -8.8383,
            'longitude_entrega': 13.2344,
            'telefone_contato': _telCtrl.text,
            'notas': _notasCtrl.text.isNotEmpty ? _notasCtrl.text : null,
          });
          break;
        case CartItemType.produto:
          result = await _svc.createOrder({
            'seller_id': cart.contextId,
            'items': cart.items.map((i) => {'product_id': i.id, 'quantidade': i.quantity}).toList(),
            'endereco_entrega': _enderecoCtrl.text,
            'latitude_entrega': -8.8383,
            'longitude_entrega': 13.2344,
            'telefone_contato': _telCtrl.text,
            'notas': _notasCtrl.text.isNotEmpty ? _notasCtrl.text : null,
          });
          break;
        case CartItemType.ticket:
          // Tickets: compra individual por tipo
          for (final item in cart.items) {
            result = await _svc.purchaseTicket(item.id, item.quantity);
          }
          break;
        case CartItemType.alojamento:
          final extra = widget.extraData ?? {};
          result = await _svc.createBooking({
            'property_id': cart.contextId,
            'data_checkin': extra['data_checkin'] ?? '',
            'data_checkout': extra['data_checkout'] ?? '',
            'adultos': extra['adultos'] ?? 1,
            'criancas': extra['criancas'] ?? 0,
            'telefone_contato': _telCtrl.text,
            'notas': _notasCtrl.text.isNotEmpty ? _notasCtrl.text : null,
          });
          break;
        case CartItemType.turismo:
          final extra = widget.extraData ?? {};
          result = await _svc.createTurismoBooking({
            'experience_id': cart.contextId,
            'schedule_id': extra['schedule_id'] ?? '',
            'adultos': extra['adultos'] ?? 1,
            'criancas': extra['criancas'] ?? 0,
            'telefone_contato': _telCtrl.text,
            'notas': _notasCtrl.text.isNotEmpty ? _notasCtrl.text : null,
          });
          break;
      }

      cart.clear();
      setState(() {
        _success = true;
        _orderResult = result;
      });
    } catch (e) {
      _snack('Erro: $e', AppTheme.danger);
    }
    if (mounted) setState(() => _submitting = false);
  }

  void _snack(String msg, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg), backgroundColor: color));
  }
}

class _CartItemTile extends StatelessWidget {
  final CartItem item;
  final VoidCallback onRemove;
  final ValueChanged<int> onQtyChanged;
  const _CartItemTile({required this.item, required this.onRemove, required this.onQtyChanged});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: TCard(
        padding: const EdgeInsets.all(12),
        child: Row(children: [
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(item.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
            Text('${item.price.toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
          ])),
          // Qty controls
          Row(mainAxisSize: MainAxisSize.min, children: [
            _QtyBtn(Icons.remove, () => onQtyChanged(item.quantity - 1)),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 10),
              child: Text('${item.quantity}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
            _QtyBtn(Icons.add, () => onQtyChanged(item.quantity + 1)),
          ]),
          const SizedBox(width: 8),
          Text('${item.subtotal.toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold)),
          const SizedBox(width: 4),
          GestureDetector(onTap: onRemove, child: const Icon(Icons.close, color: AppTheme.danger, size: 18)),
        ]),
      ),
    );
  }
}

class _QtyBtn extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  const _QtyBtn(this.icon, this.onTap);
  @override
  Widget build(BuildContext context) => GestureDetector(
        onTap: onTap,
        child: Container(
          width: 28, height: 28,
          decoration: BoxDecoration(color: AppTheme.dark700, borderRadius: BorderRadius.circular(6)),
          child: Icon(icon, color: Colors.white, size: 16),
        ),
      );
}

class _TotalRow extends StatelessWidget {
  final String label;
  final double value;
  final bool bold;
  const _TotalRow(this.label, this.value, {this.bold = false});
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
          Text(label, style: TextStyle(color: bold ? Colors.white : AppTheme.dark400, fontWeight: bold ? FontWeight.bold : FontWeight.normal, fontSize: bold ? 16 : 13)),
          Text('${value.toStringAsFixed(0)} Kz', style: TextStyle(color: bold ? AppTheme.accent : AppTheme.dark300, fontWeight: bold ? FontWeight.bold : FontWeight.normal, fontSize: bold ? 16 : 13)),
        ]),
      );
}

class _InputField extends StatelessWidget {
  final TextEditingController ctrl;
  final String label;
  final IconData icon;
  const _InputField({required this.ctrl, required this.label, required this.icon});
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 10),
        child: TextField(
          controller: ctrl,
          style: const TextStyle(color: Colors.white, fontSize: 14),
          decoration: InputDecoration(
            prefixIcon: Icon(icon, color: AppTheme.dark400, size: 18),
            labelText: label, labelStyle: const TextStyle(color: AppTheme.dark500),
            filled: true, fillColor: AppTheme.dark800,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppTheme.dark700)),
            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppTheme.dark700)),
          ),
        ),
      );
}

class _PaymentOption extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;
  const _PaymentOption({required this.label, required this.icon, required this.selected, required this.onTap});
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: GestureDetector(
          onTap: onTap,
          child: Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: selected ? AppTheme.primary.withOpacity(0.1) : AppTheme.dark800,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: selected ? AppTheme.primary : AppTheme.dark700),
            ),
            child: Row(children: [
              Icon(icon, color: selected ? AppTheme.primary : AppTheme.dark400, size: 20),
              const SizedBox(width: 12),
              Expanded(child: Text(label, style: TextStyle(color: selected ? Colors.white : AppTheme.dark300, fontSize: 14))),
              if (selected) const Icon(Icons.check_circle, color: AppTheme.primary, size: 20),
            ]),
          ),
        ),
      );
}

class _SuccessView extends StatelessWidget {
  final Map<String, dynamic>? result;
  final String titulo;
  const _SuccessView({this.result, required this.titulo});

  @override
  Widget build(BuildContext context) {
    final orderId = result?['id']?.toString() ?? '';
    final qr = result?['qr_code'] ?? result?['qr_voucher'] ?? '';
    final total = result?['total']?.toStringAsFixed(0) ?? '';

    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(title: Text(titulo), backgroundColor: AppTheme.dark800),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Container(
              width: 80, height: 80,
              decoration: BoxDecoration(color: AppTheme.success.withOpacity(0.15), shape: BoxShape.circle),
              child: const Icon(Icons.check_circle, color: AppTheme.success, size: 48),
            ),
            const SizedBox(height: 20),
            const Text('Pedido Confirmado!', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20)),
            if (total.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text('$total Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 28)),
            ],
            if (orderId.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text('ID: ${orderId.length > 8 ? orderId.substring(0, 8) : orderId}...', style: const TextStyle(color: AppTheme.dark400, fontSize: 13)),
            ],
            if (qr.isNotEmpty) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12)),
                child: Text(qr, style: const TextStyle(color: Colors.black, fontSize: 12, fontFamily: 'monospace')),
              ),
              const Text('Codigo QR / Voucher', style: TextStyle(color: AppTheme.dark500, fontSize: 11)),
            ],
            const SizedBox(height: 24),
            PrimaryButton(
              label: 'Voltar',
              icon: Icons.arrow_back,
              onPressed: () => Navigator.of(context).popUntil((route) => route.isFirst),
            ),
          ]),
        ),
      ),
    );
  }
}
