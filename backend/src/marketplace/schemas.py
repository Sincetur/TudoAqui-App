"""
TUDOaqui API - Marketplace Schemas
"""
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
    descricao: str | None = None
    logo_url: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    provincia: str | None = None
    taxa_entrega_base: float = 0
    tempo_preparacao_min: int = 30


class SellerCreate(SellerBase):
    """Schema para criar vendedor"""
    pass


class SellerUpdate(BaseModel):
    """Schema para atualizar vendedor"""
    nome_loja: str | None = None
    descricao: str | None = None
    logo_url: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    provincia: str | None = None
    taxa_entrega_base: float | None = None
    tempo_preparacao_min: int | None = None


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
    descricao: str | None = None
    preco: float = Field(..., gt=0)
    preco_promocional: float | None = None
    stock: int = Field(0, ge=0)
    stock_minimo: int = 5
    imagens: list[str] | None = None
    atributos: dict | None = None
    peso_kg: float | None = None
    destaque: bool = False
    category_id: UUID | None = None


class ProductCreate(ProductBase):
    """Schema para criar produto"""
    pass


class ProductUpdate(BaseModel):
    """Schema para atualizar produto"""
    nome: str | None = None
    descricao: str | None = None
    preco: float | None = None
    preco_promocional: float | None = None
    stock: int | None = None
    stock_minimo: int | None = None
    imagens: list[str] | None = None
    atributos: dict | None = None
    peso_kg: float | None = None
    destaque: bool | None = None
    category_id: UUID | None = None
    status: ProductStatus | None = None


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
    items: list[OrderItemCreate]
    endereco_entrega: str = Field(..., min_length=10)
    latitude_entrega: float | None = None
    longitude_entrega: float | None = None
    telefone_contato: str = Field(..., min_length=9)
    notas: str | None = None


class OrderItemResponse(BaseModel):
    """Resposta de item do pedido"""
    id: UUID
    product_id: UUID
    quantidade: int
    preco_unitario: float
    subtotal: float
    produto_nome: str
    produto_imagem: str | None
    
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
    notas: str | None
    status: OrderStatus
    created_at: datetime
    pago_at: datetime | None
    enviado_at: datetime | None
    entregue_at: datetime | None
    items: list[OrderItemResponse] = []
    
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
    descricao: str | None
    icone: str | None
    parent_id: UUID | None
    ordem: int
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Review Schemas
# ============================================

class ReviewCreate(BaseModel):
    """Schema para criar avaliação"""
    nota: int = Field(..., ge=1, le=5)
    comentario: str | None = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    """Schema de resposta de avaliação"""
    id: UUID
    product_id: UUID
    user_id: UUID
    nota: int
    comentario: str | None
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
