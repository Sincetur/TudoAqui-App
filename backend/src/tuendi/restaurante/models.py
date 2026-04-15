"""
TUDOaqui API - Tuendi Restaurante Models
Módulo de Delivery de Comida
"""
from typing import Optional
from datetime import datetime, time
from enum import Enum
from uuid import UUID
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, Numeric, Text, ForeignKey, Boolean, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.sql import func
import uuid

from src.database import Base


class RestaurantStatus(str, Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    SUSPENSO = "suspenso"


class MenuItemStatus(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    ESGOTADO = "esgotado"


class FoodOrderStatus(str, Enum):
    PENDENTE = "pendente"
    ACEITE = "aceite"
    PREPARANDO = "preparando"
    PRONTO = "pronto"
    RECOLHIDO = "recolhido"
    EM_ENTREGA = "em_entrega"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class Restaurant(Base):
    """Restaurante parceiro"""
    __tablename__ = "restaurants"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    banner_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Localização
    endereco: Mapped[str] = mapped_column(Text, nullable=False)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    
    # Horário de funcionamento
    hora_abertura: Mapped[time] = mapped_column(Time, default=time(8, 0))
    hora_fecho: Mapped[time] = mapped_column(Time, default=time(22, 0))
    dias_funcionamento: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # [0-6]
    
    # Configurações de entrega
    raio_entrega_km: Mapped[int] = mapped_column(Integer, default=10)
    tempo_preparo_min: Mapped[int] = mapped_column(Integer, default=30)
    pedido_minimo: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    taxa_entrega: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    
    # Categorias de culinária
    categorias: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # ["Angolana", "Portuguesa", etc]
    
    # Stats
    rating_medio: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=5.00)
    total_pedidos: Mapped[int] = mapped_column(Integer, default=0)
    total_avaliacoes: Mapped[int] = mapped_column(Integer, default=0)
    
    # Contacto
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    
    aberto: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(20), default=RestaurantStatus.PENDENTE)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    owner = relationship("User", backref="restaurants_owned")
    menu_categories = relationship("MenuCategory", back_populates="restaurant", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Restaurant {self.nome}>"


class MenuCategory(Base):
    """Categoria do menu"""
    __tablename__ = "menu_categories"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    restaurant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False
    )
    
    nome: Mapped[str] = mapped_column(String(80), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ordem: Mapped[int] = mapped_column(Integer, default=0)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_categories")
    items = relationship("MenuItem", back_populates="category", cascade="all, delete-orphan")


class MenuItem(Base):
    """Item do menu"""
    __tablename__ = "menu_items"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    category_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("menu_categories.id", ondelete="CASCADE"),
        nullable=False
    )
    restaurant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("restaurants.id"),
        nullable=False
    )
    
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    imagem_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    preco: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    preco_promocional: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    
    # Tempo de preparo específico do item
    tempo_preparo_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Opcionais/Adicionais
    opcoes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Informações nutricionais/alérgenos
    info_nutricional: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    popular: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default=MenuItemStatus.ATIVO)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    category = relationship("MenuCategory", back_populates="items")
    restaurant = relationship("Restaurant", backref="menu_items")
    
    @property
    def preco_atual(self) -> Decimal:
        return self.preco_promocional or self.preco


class FoodOrder(Base):
    """Pedido de comida"""
    __tablename__ = "food_orders"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    customer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    restaurant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("restaurants.id"),
        nullable=False
    )
    driver_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("drivers.id"),
        nullable=True
    )
    
    # Endereço de entrega
    endereco_entrega: Mapped[str] = mapped_column(Text, nullable=False)
    latitude_entrega: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    longitude_entrega: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    referencia_entrega: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Valores
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    taxa_entrega: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    desconto: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    # Contato
    telefone_contato: Mapped[str] = mapped_column(String(20), nullable=False)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Tempo estimado
    tempo_preparo_estimado: Mapped[int] = mapped_column(Integer, nullable=False)  # minutos
    tempo_entrega_estimado: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # minutos
    
    # Código de entrega
    codigo_entrega: Mapped[Optional[str]] = mapped_column(String(6), nullable=True)
    
    # Integração Tuendi Entrega
    delivery_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), default=FoodOrderStatus.PENDENTE)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    aceite_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    pronto_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    recolhido_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    entregue_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelado_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    motivo_cancelamento: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    customer = relationship("User", backref="food_orders")
    restaurant = relationship("Restaurant", backref="orders")
    driver = relationship("Driver", backref="food_orders")
    items = relationship("FoodOrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<FoodOrder {self.id} ({self.status})>"


class FoodOrderItem(Base):
    """Item do pedido"""
    __tablename__ = "food_order_items"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    order_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("food_orders.id", ondelete="CASCADE"),
        nullable=False
    )
    menu_item_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("menu_items.id"),
        nullable=False
    )
    
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    # Opcionais selecionados
    opcoes_selecionadas: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Notas do cliente
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Snapshot do item
    item_nome: Mapped[str] = mapped_column(String(120), nullable=False)
    
    # Relationships
    order = relationship("FoodOrder", back_populates="items")
    menu_item = relationship("MenuItem", backref="order_items")


class RestaurantReview(Base):
    """Avaliação do restaurante"""
    __tablename__ = "restaurant_reviews"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    restaurant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False
    )
    order_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("food_orders.id"),
        nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    
    nota_comida: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    nota_entrega: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5
    nota_geral: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    
    comentario: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    restaurant = relationship("Restaurant", backref="reviews")
    user = relationship("User", backref="restaurant_reviews")
