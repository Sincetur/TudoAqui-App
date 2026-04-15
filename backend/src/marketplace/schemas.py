"""
TUDOaqui API - Marketplace Schemas
"""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from src.marketplace.models import SellerStatus, ProductStatus, OrderStatus


# ============================================
# Seller Schemas
# ============================================

class SellerBase(BaseModel):
    """Schema base de vendedor"""
    nome_loja: str = Field(..., min_length=2, max_length=120)
    descricao: Optional[str] = None
    logo_url: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    provincia: Optional[str] = None
    taxa_entrega_base: float = 0
    tempo_preparacao_min: int = 30


class SellerCreate(SellerBase):
    """Schema para criar vendedor"""
    pass


class SellerUpdate(BaseModel):
    """Schema para atualizar vendedor"""
    nome_loja: Optional[str] = None
    descricao: Optional[str] = None
    logo_url: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    provincia: Optional[str] = None
    taxa_entrega_base: Optional[float] = None
    tempo_preparacao_min: Optional[int] = None


class SellerResponse(SellerBase):
    """Schema de resposta de vendedor"""
    id: UUID
    user_id: UUID
    rating_medio: float
    total_vendas: int
    status: SellerStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Product Schemas
# ============================================

class ProductBase(BaseModel):
    """Schema base de produto"""
    nome: str = Field(..., min_length=2, max_length=150)
    descricao: Optional[str] = None
    preco: float = Field(..., gt=0)
    preco_promocional: Optional[float] = None
    stock: int = Field(0, ge=0)
    stock_minimo: int = 5
    imagens: Optional[List[str]] = None
    atributos: Optional[dict] = None
    peso_kg: Optional[float] = None
    destaque: bool = False
    category_id: Optional[UUID] = None


class ProductCreate(ProductBase):
    """Schema para criar produto"""
    pass


class ProductUpdate(BaseModel):
    """Schema para atualizar produto"""
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[float] = None
    preco_promocional: Optional[float] = None
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    imagens: Optional[List[str]] = None
    atributos: Optional[dict] = None
    peso_kg: Optional[float] = None
    destaque: Optional[bool] = None
    category_id: Optional[UUID] = None
    status: Optional[ProductStatus] = None


class ProductResponse(ProductBase):
    """Schema de resposta de produto"""
    id: UUID
    seller_id: UUID
    status: ProductStatus
    visualizacoes: int
    vendas: int
    preco_atual: float = 0
    em_promocao: bool = False
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProductDetailResponse(ProductResponse):
    """Schema detalhado com info do vendedor"""
    seller_nome: str
    seller_rating: float


# ============================================
# Order Schemas
# ============================================

class OrderItemCreate(BaseModel):
    """Item do pedido"""
    product_id: UUID
    quantidade: int = Field(..., ge=1, le=100)


class OrderCreate(BaseModel):
    """Schema para criar pedido"""
    seller_id: UUID
    items: List[OrderItemCreate]
    endereco_entrega: str = Field(..., min_length=10)
    latitude_entrega: Optional[float] = None
    longitude_entrega: Optional[float] = None
    telefone_contato: str = Field(..., min_length=9)
    notas: Optional[str] = None


class OrderItemResponse(BaseModel):
    """Resposta de item do pedido"""
    id: UUID
    product_id: UUID
    quantidade: int
    preco_unitario: float
    subtotal: float
    produto_nome: str
    produto_imagem: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    """Schema de resposta de pedido"""
    id: UUID
    buyer_id: UUID
    seller_id: UUID
    subtotal: float
    taxa_entrega: float
    desconto: float
    total: float
    endereco_entrega: str
    telefone_contato: str
    notas: Optional[str]
    status: OrderStatus
    created_at: datetime
    pago_at: Optional[datetime]
    enviado_at: Optional[datetime]
    entregue_at: Optional[datetime]
    items: List[OrderItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    """Atualização de status do pedido"""
    status: OrderStatus


# ============================================
# Category Schemas
# ============================================

class CategoryResponse(BaseModel):
    """Schema de categoria"""
    id: UUID
    nome: str
    descricao: Optional[str]
    icone: Optional[str]
    parent_id: Optional[UUID]
    ordem: int
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Review Schemas
# ============================================

class ReviewCreate(BaseModel):
    """Schema para criar avaliação"""
    nota: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    """Schema de resposta de avaliação"""
    id: UUID
    product_id: UUID
    user_id: UUID
    nota: int
    comentario: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Stats Schemas
# ============================================

class SellerStats(BaseModel):
    """Estatísticas do vendedor"""
    total_produtos: int
    total_pedidos: int
    pedidos_pendentes: int
    receita_total: float
    receita_mes: float
