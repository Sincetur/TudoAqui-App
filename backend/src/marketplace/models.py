"""
TUDOaqui API - Marketplace Models
Módulo Marketplace: Multi-vendedor B2C/B2B
"""
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import UUID
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, Numeric, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.sql import func
import uuid

from src.database import Base


class SellerStatus(str, Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    SUSPENSO = "suspenso"
    REJEITADO = "rejeitado"


class ProductStatus(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    ESGOTADO = "esgotado"


class OrderStatus(str, Enum):
    PENDENTE = "pendente"
    PAGO = "pago"
    PROCESSANDO = "processando"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"
    REEMBOLSADO = "reembolsado"


class Seller(Base):
    """Vendedor do Marketplace"""
    __tablename__ = "sellers"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )
    
    nome_loja: Mapped[str] = mapped_column(String(120), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Localização
    endereco: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cidade: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    provincia: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Configurações
    taxa_entrega_base: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    tempo_preparacao_min: Mapped[int] = mapped_column(Integer, default=30)  # minutos
    
    # Stats
    rating_medio: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=5.00)
    total_vendas: Mapped[int] = mapped_column(Integer, default=0)
    
    status: Mapped[str] = mapped_column(String(20), default=SellerStatus.PENDENTE)
    
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
    user = relationship("User", backref="seller_profile")
    products = relationship("Product", back_populates="seller", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Seller {self.nome_loja} ({self.status})>"


class ProductCategory(Base):
    """Categorias de produtos"""
    __tablename__ = "product_categories"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("product_categories.id"),
        nullable=True
    )
    ordem: Mapped[int] = mapped_column(Integer, default=0)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)


class Product(Base):
    """Produto do Marketplace"""
    __tablename__ = "products"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    seller_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("sellers.id", ondelete="CASCADE"),
        nullable=False
    )
    category_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("product_categories.id"),
        nullable=True
    )
    
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    preco: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    preco_promocional: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    
    stock: Mapped[int] = mapped_column(Integer, default=0)
    stock_minimo: Mapped[int] = mapped_column(Integer, default=5)
    
    # Imagens (JSON array de URLs)
    imagens: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Atributos (cor, tamanho, etc)
    atributos: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Peso para cálculo de frete (kg)
    peso_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 3), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), default=ProductStatus.ATIVO)
    destaque: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Stats
    visualizacoes: Mapped[int] = mapped_column(Integer, default=0)
    vendas: Mapped[int] = mapped_column(Integer, default=0)
    
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
    seller = relationship("Seller", back_populates="products")
    category = relationship("ProductCategory", backref="products")
    
    @property
    def preco_atual(self) -> Decimal:
        """Retorna preço promocional se existir"""
        return self.preco_promocional or self.preco
    
    @property
    def em_promocao(self) -> bool:
        return self.preco_promocional is not None and self.preco_promocional < self.preco
    
    def __repr__(self) -> str:
        return f"<Product {self.nome} ({self.preco} Kz)>"


class MarketplaceOrder(Base):
    """Pedido do Marketplace"""
    __tablename__ = "marketplace_orders"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    buyer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    seller_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("sellers.id"),
        nullable=False
    )
    
    # Valores
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    taxa_entrega: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    desconto: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    # Entrega
    endereco_entrega: Mapped[str] = mapped_column(Text, nullable=False)
    latitude_entrega: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8), nullable=True)
    longitude_entrega: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8), nullable=True)
    
    # Contato
    telefone_contato: Mapped[str] = mapped_column(String(20), nullable=False)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Integração Tuendi Entrega
    tuendi_entrega_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), default=OrderStatus.PENDENTE)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    pago_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    enviado_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    entregue_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelado_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    buyer = relationship("User", backref="marketplace_orders")
    seller = relationship("Seller", backref="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Item de um pedido"""
    __tablename__ = "order_items"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    order_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("marketplace_orders.id", ondelete="CASCADE"),
        nullable=False
    )
    product_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("products.id"),
        nullable=False
    )
    
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    # Snapshot do produto no momento da compra
    produto_nome: Mapped[str] = mapped_column(String(150), nullable=False)
    produto_imagem: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    order = relationship("MarketplaceOrder", back_populates="items")
    product = relationship("Product", backref="order_items")


class ProductReview(Base):
    """Avaliação de produto"""
    __tablename__ = "product_reviews"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    product_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    order_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("marketplace_orders.id"),
        nullable=True
    )
    
    nota: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    comentario: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    product = relationship("Product", backref="reviews")
    user = relationship("User", backref="product_reviews")
