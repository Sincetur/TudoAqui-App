import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../services/module_service.dart';
import '../../services/cart_service.dart';
import '../../modules/common/checkout_screen.dart';
import '../../widgets/common.dart';

class EventosScreen extends StatefulWidget {
  const EventosScreen({super.key});
  @override
  State<EventosScreen> createState() => _EventosScreenState();
}

class _EventosScreenState extends State<EventosScreen> {
  final _svc = ModuleService();
  List<dynamic> _events = [];
  bool _loading = true;
  String _search = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      _events = await _svc.listEvents();
    } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  List<dynamic> get _filtered => _events.where((e) {
        final q = _search.toLowerCase();
        return (e['titulo'] ?? '').toString().toLowerCase().contains(q) ||
            (e['local'] ?? '').toString().toLowerCase().contains(q);
      }).toList();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(
        title: const Text('Eventos'),
        backgroundColor: AppTheme.dark800,
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: _SearchField(
              hint: 'Procurar eventos...',
              onChanged: (v) => setState(() => _search = v),
            ),
          ),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
                : _filtered.isEmpty
                    ? const EmptyState(icon: Icons.event, title: 'Sem eventos', subtitle: 'Nenhum evento disponivel')
                    : RefreshIndicator(
                        onRefresh: _load,
                        child: ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: _filtered.length,
                          itemBuilder: (ctx, i) => _EventCard(
                            event: _filtered[i],
                            onTap: () => _openDetail(_filtered[i]),
                          ),
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  void _openDetail(Map<String, dynamic> event) {
    Navigator.push(context, MaterialPageRoute(
      builder: (_) => _EventDetailScreen(event: event, svc: _svc),
    ));
  }
}

class _EventCard extends StatelessWidget {
  final Map<String, dynamic> event;
  final VoidCallback onTap;
  const _EventCard({required this.event, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TCard(
        onTap: onTap,
        child: Row(
          children: [
            Container(
              width: 48, height: 48,
              decoration: BoxDecoration(
                color: AppTheme.primary.withOpacity(0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.event, color: AppTheme.primary),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(event['titulo'] ?? 'Evento', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                  const SizedBox(height: 2),
                  Row(children: [
                    const Icon(Icons.place, size: 12, color: AppTheme.dark400),
                    const SizedBox(width: 4),
                    Text(event['local'] ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
                    const SizedBox(width: 10),
                    const Icon(Icons.calendar_today, size: 12, color: AppTheme.dark400),
                    const SizedBox(width: 4),
                    Text(event['data_evento'] ?? '', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
                  ]),
                  if (event['categoria'] != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: StatusBadge(label: event['categoria'], variant: 'primary'),
                    ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: AppTheme.dark500),
          ],
        ),
      ),
    );
  }
}

class _EventDetailScreen extends StatefulWidget {
  final Map<String, dynamic> event;
  final ModuleService svc;
  const _EventDetailScreen({required this.event, required this.svc});
  @override
  State<_EventDetailScreen> createState() => _EventDetailScreenState();
}

class _EventDetailScreenState extends State<_EventDetailScreen> {
  @override
  Widget build(BuildContext context) {
    final cart = context.watch<CartProvider>();
    final tickets = (widget.event['ticket_types'] as List?) ?? [];

    return Scaffold(
      backgroundColor: AppTheme.dark900,
      appBar: AppBar(
        title: Text(widget.event['titulo'] ?? 'Evento'),
        backgroundColor: AppTheme.dark800,
        actions: [
          if (!cart.isEmpty)
            _CartBadge(
              count: cart.count,
              onTap: () => Navigator.push(context, MaterialPageRoute(
                builder: (_) => const CheckoutScreen(titulo: 'Compra de Bilhetes'),
              )),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(widget.event['titulo'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
              const SizedBox(height: 8),
              _InfoRow(Icons.place, widget.event['local'] ?? ''),
              _InfoRow(Icons.calendar_today, widget.event['data_evento'] ?? ''),
              _InfoRow(Icons.access_time, widget.event['hora_evento'] ?? ''),
              if (widget.event['descricao'] != null) ...[
                const SizedBox(height: 12),
                Text(widget.event['descricao'], style: const TextStyle(color: AppTheme.dark300, fontSize: 13)),
              ],
            ])),
            if (tickets.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Text('Bilhetes', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 8),
              ...tickets.map((t) => _TicketTypeCard(
                ticket: t,
                onAdd: () {
                  cart.addItem(
                    CartItem(
                      id: t['id'].toString(),
                      name: '${widget.event['titulo']} - ${t['nome']}',
                      price: (t['preco'] ?? 0).toDouble(),
                      type: CartItemType.ticket,
                      meta: {'event_id': widget.event['id']?.toString()},
                    ),
                    contextId: widget.event['id']?.toString(),
                  );
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Bilhete ${t['nome']} adicionado'),
                      backgroundColor: AppTheme.success,
                      duration: const Duration(seconds: 1),
                    ),
                  );
                },
              )),
            ],
          ],
        ),
      ),
      floatingActionButton: cart.isEmpty ? null : FloatingActionButton.extended(
        backgroundColor: AppTheme.primary,
        icon: const Icon(Icons.confirmation_number, color: Colors.white),
        label: Text('Comprar (${cart.count}) - ${cart.subtotal.toStringAsFixed(0)} Kz',
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        onPressed: () => Navigator.push(context, MaterialPageRoute(
          builder: (_) => const CheckoutScreen(titulo: 'Compra de Bilhetes'),
        )),
      ),
    );
  }
}

class _TicketTypeCard extends StatelessWidget {
  final Map<String, dynamic> ticket;
  final VoidCallback onAdd;
  const _TicketTypeCard({required this.ticket, required this.onAdd});

  @override
  Widget build(BuildContext context) {
    final disponivel = (ticket['quantidade_disponivel'] ?? 0) as int;
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: TCard(child: Row(children: [
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(ticket['nome'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
          Text('Disponiveis: $disponivel', style: const TextStyle(color: AppTheme.dark400, fontSize: 12)),
        ])),
        Text('${(ticket['preco'] ?? 0).toStringAsFixed(0)} Kz', style: const TextStyle(color: AppTheme.accent, fontWeight: FontWeight.bold, fontSize: 16)),
        const SizedBox(width: 10),
        GestureDetector(
          onTap: disponivel > 0 ? onAdd : null,
          child: Container(
            width: 36, height: 36,
            decoration: BoxDecoration(
              color: disponivel > 0 ? AppTheme.primary.withOpacity(0.15) : AppTheme.dark700,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(Icons.add, color: disponivel > 0 ? AppTheme.primary : AppTheme.dark500, size: 20),
          ),
        ),
      ])),
    );
  }
}

class _CartBadge extends StatelessWidget {
  final int count;
  final VoidCallback onTap;
  const _CartBadge({required this.count, required this.onTap});
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(right: 12),
    child: GestureDetector(
      onTap: onTap,
      child: Stack(clipBehavior: Clip.none, children: [
        const Icon(Icons.shopping_cart, color: Colors.white, size: 26),
        Positioned(
          right: -6, top: -4,
          child: Container(
            padding: const EdgeInsets.all(4),
            decoration: const BoxDecoration(color: AppTheme.primary, shape: BoxShape.circle),
            child: Text('$count', style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
          ),
        ),
      ]),
    ),
  );
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String text;
  const _InfoRow(this.icon, this.text);
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 4),
    child: Row(children: [
      Icon(icon, size: 14, color: AppTheme.dark400),
      const SizedBox(width: 8),
      Text(text, style: const TextStyle(color: AppTheme.dark300, fontSize: 13)),
    ]),
  );
}

class _SearchField extends StatelessWidget {
  final String hint;
  final ValueChanged<String> onChanged;
  const _SearchField({required this.hint, required this.onChanged});
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 14),
    decoration: BoxDecoration(
      color: AppTheme.dark800,
      borderRadius: BorderRadius.circular(12),
      border: Border.all(color: AppTheme.dark700),
    ),
    child: Row(children: [
      const Icon(Icons.search, color: AppTheme.dark500, size: 20),
      const SizedBox(width: 10),
      Expanded(child: TextField(
        onChanged: onChanged,
        style: const TextStyle(color: Colors.white, fontSize: 14),
        decoration: InputDecoration(border: InputBorder.none, hintText: hint, hintStyle: const TextStyle(color: AppTheme.dark500)),
      )),
    ]),
  );
}
