import 'package:flutter/material.dart';

/// Tipos de item no carrinho
enum CartItemType { produto, menuItem, ticket, alojamento, turismo }

/// Item generico do carrinho
class CartItem {
  final String id;
  final String name;
  final double price;
  int quantity;
  final CartItemType type;
  final String? imageUrl;
  final Map<String, dynamic> meta; // dados extras (seller_id, restaurant_id, etc)

  CartItem({
    required this.id,
    required this.name,
    required this.price,
    this.quantity = 1,
    required this.type,
    this.imageUrl,
    this.meta = const {},
  });

  double get subtotal => price * quantity;

  CartItem copyWith({int? quantity}) => CartItem(
        id: id,
        name: name,
        price: price,
        quantity: quantity ?? this.quantity,
        type: type,
        imageUrl: imageUrl,
        meta: meta,
      );
}

/// Provider do carrinho — estado global
class CartProvider extends ChangeNotifier {
  final List<CartItem> _items = [];
  String? _contextId; // restaurant_id, seller_id, event_id, etc

  List<CartItem> get items => List.unmodifiable(_items);
  int get count => _items.fold(0, (sum, i) => sum + i.quantity);
  double get subtotal => _items.fold(0.0, (sum, i) => sum + i.subtotal);
  bool get isEmpty => _items.isEmpty;
  String? get contextId => _contextId;

  /// Adiciona item. Se ja existe, incrementa quantidade.
  /// Se o contextId mudou (ex: outro restaurante), limpa o carrinho.
  void addItem(CartItem item, {String? contextId}) {
    if (contextId != null && _contextId != null && _contextId != contextId) {
      _items.clear();
    }
    if (contextId != null) _contextId = contextId;

    final idx = _items.indexWhere((i) => i.id == item.id);
    if (idx >= 0) {
      _items[idx].quantity += item.quantity;
    } else {
      _items.add(item);
    }
    notifyListeners();
  }

  /// Remove item pelo id
  void removeItem(String id) {
    _items.removeWhere((i) => i.id == id);
    if (_items.isEmpty) _contextId = null;
    notifyListeners();
  }

  /// Atualiza quantidade de um item
  void updateQuantity(String id, int qty) {
    final idx = _items.indexWhere((i) => i.id == id);
    if (idx < 0) return;
    if (qty <= 0) {
      _items.removeAt(idx);
    } else {
      _items[idx].quantity = qty;
    }
    notifyListeners();
  }

  /// Limpa carrinho
  void clear() {
    _items.clear();
    _contextId = null;
    notifyListeners();
  }
}
