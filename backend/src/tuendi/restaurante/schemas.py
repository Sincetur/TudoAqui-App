"""
TUDOaqui API - Tuendi Restaurante Schemas
"""
from typing import List, Optional
from datetime import datetime, time
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from src.tuendi.restaurante.models import RestaurantStatus, MenuItemStatus, FoodOrderStatus


# ============================================
# Restaurant Schemas
# ============================================

class RestaurantBase(BaseModel):
    """Schema base de restaurante"""
    nome: str = Field(..., min_length=2, max_length=120)
    descricao: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    endereco: str = Field(..., min_length=5)
    cidade: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    hora_abertura: time = time(8, 0)
    hora_fecho: time = time(22, 0)
    dias_funcionamento: Optional[List[int]] = None  # 0=Dom, 1=Seg, etc
    raio_entrega_km: int = Field(10, ge=1, le=50)
    tempo_preparo_min: int = Field(30, ge=5, le=120)
    pedido_minimo: float = 0
    taxa_entrega: float = 0
    categorias: Optional[List[str]] = None
    telefone: str = Field(..., min_length=9)


class RestaurantCreate(RestaurantBase):
    """Schema para criar restaurante"""
    pass


class RestaurantUpdate(BaseModel):
    """Schema para atualizar restaurante"""
    nome: Optional[str] = None
    descricao: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    hora_abertura: Optional[time] = None
    hora_fecho: Optional[time] = None
    dias_funcionamento: Optional[List[int]] = None
    raio_entrega_km: Optional[int] = None
    tempo_preparo_min: Optional[int] = None
    pedido_minimo: Optional[float] = None
    taxa_entrega: Optional[float] = None
    categorias: Optional[List[str]] = None
    telefone: Optional[str] = None
    aberto: Optional[bool] = None


class RestaurantResponse(RestaurantBase):
    """Schema de resposta de restaurante"""
    id: UUID
    owner_id: UUID
    rating_medio: float
    total_pedidos: int
    total_avaliacoes: int
    aberto: bool
    status: RestaurantStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RestaurantListResponse(BaseModel):
    """Lista simplificada"""
    id: UUID
    nome: str
    logo_url: Optional[str]
    categorias: Optional[List[str]]
    rating_medio: float
    tempo_preparo_min: int
    taxa_entrega: float
    aberto: bool
    distancia_km: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Menu Schemas
# ============================================

class MenuCategoryBase(BaseModel):
    """Schema base de categoria"""
    nome: str = Field(..., min_length=2, max_length=80)
    descricao: Optional[str] = None
    ordem: int = 0


class MenuCategoryCreate(MenuCategoryBase):
    pass


class MenuCategoryResponse(MenuCategoryBase):
    id: UUID
    restaurant_id: UUID
    ativo: bool
    items: List["MenuItemResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)


class MenuItemBase(BaseModel):
    """Schema base de item"""
    nome: str = Field(..., min_length=2, max_length=120)
    descricao: Optional[str] = None
    imagem_url: Optional[str] = None
    preco: float = Field(..., gt=0)
    preco_promocional: Optional[float] = None
    tempo_preparo_min: Optional[int] = None
    opcoes: Optional[List[dict]] = None  # [{nome, opcoes: [{nome, preco_adicional}]}]
    info_nutricional: Optional[dict] = None
    popular: bool = False


class MenuItemCreate(MenuItemBase):
    category_id: UUID


class MenuItemUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    imagem_url: Optional[str] = None
    preco: Optional[float] = None
    preco_promocional: Optional[float] = None
    tempo_preparo_min: Optional[int] = None
    opcoes: Optional[List[dict]] = None
    info_nutricional: Optional[dict] = None
    popular: Optional[bool] = None
    status: Optional[MenuItemStatus] = None
    category_id: Optional[UUID] = None


class MenuItemResponse(MenuItemBase):
    id: UUID
    category_id: UUID
    restaurant_id: UUID
    status: MenuItemStatus
    preco_atual: float = 0
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Order Schemas
# ============================================

class OrderItemCreate(BaseModel):
    """Item do pedido"""
    menu_item_id: UUID
    quantidade: int = Field(..., ge=1, le=50)
    opcoes_selecionadas: Optional[List[dict]] = None
    notas: Optional[str] = None


class FoodOrderCreate(BaseModel):
    """Schema para criar pedido"""
    restaurant_id: UUID
    items: List[OrderItemCreate]
    endereco_entrega: str = Field(..., min_length=5)
    latitude_entrega: float = Field(..., ge=-90, le=90)
    longitude_entrega: float = Field(..., ge=-180, le=180)
    referencia_entrega: Optional[str] = None
    telefone_contato: str = Field(..., min_length=9)
    notas: Optional[str] = None


class OrderItemResponse(BaseModel):
    """Resposta de item"""
    id: UUID
    menu_item_id: UUID
    quantidade: int
    preco_unitario: float
    subtotal: float
    opcoes_selecionadas: Optional[List[dict]]
    notas: Optional[str]
    item_nome: str
    
    model_config = ConfigDict(from_attributes=True)


class FoodOrderResponse(BaseModel):
    """Schema de resposta de pedido"""
    id: UUID
    customer_id: UUID
    restaurant_id: UUID
    driver_id: Optional[UUID]
    endereco_entrega: str
    latitude_entrega: float
    longitude_entrega: float
    referencia_entrega: Optional[str]
    subtotal: float
    taxa_entrega: float
    desconto: float
    total: float
    telefone_contato: str
    notas: Optional[str]
    tempo_preparo_estimado: int
    tempo_entrega_estimado: Optional[int]
    codigo_entrega: Optional[str]
    status: FoodOrderStatus
    created_at: datetime
    aceite_at: Optional[datetime]
    pronto_at: Optional[datetime]
    recolhido_at: Optional[datetime]
    entregue_at: Optional[datetime]
    items: List[OrderItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class FoodOrderDetailResponse(FoodOrderResponse):
    """Resposta detalhada"""
    restaurant_nome: str
    restaurant_telefone: str
    driver_nome: Optional[str] = None
    driver_telefone: Optional[str] = None


class FoodOrderListResponse(BaseModel):
    """Lista simplificada"""
    id: UUID
    restaurant_id: UUID
    restaurant_nome: str
    total: float
    status: FoodOrderStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Review Schemas
# ============================================

class ReviewCreate(BaseModel):
    nota_comida: int = Field(..., ge=1, le=5)
    nota_entrega: Optional[int] = Field(None, ge=1, le=5)
    nota_geral: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    id: UUID
    restaurant_id: UUID
    user_id: UUID
    nota_comida: int
    nota_entrega: Optional[int]
    nota_geral: int
    comentario: Optional[str]
    created_at: datetime
    user_nome: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Stats Schemas
# ============================================

class RestaurantStats(BaseModel):
    total_pedidos: int
    pedidos_hoje: int
    pedidos_pendentes: int
    receita_total: float
    receita_hoje: float
    rating_medio: float


# Forward references
MenuCategoryResponse.model_rebuild()
