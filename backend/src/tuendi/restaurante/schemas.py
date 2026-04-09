"""
TUDOaqui API - Tuendi Restaurante Schemas
"""
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
    descricao: str | None = None
    logo_url: str | None = None
    banner_url: str | None = None
    endereco: str = Field(..., min_length=5)
    cidade: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    hora_abertura: time = time(8, 0)
    hora_fecho: time = time(22, 0)
    dias_funcionamento: list[int] | None = None  # 0=Dom, 1=Seg, etc
    raio_entrega_km: int = Field(10, ge=1, le=50)
    tempo_preparo_min: int = Field(30, ge=5, le=120)
    pedido_minimo: float = 0
    taxa_entrega: float = 0
    categorias: list[str] | None = None
    telefone: str = Field(..., min_length=9)


class RestaurantCreate(RestaurantBase):
    """Schema para criar restaurante"""
    pass


class RestaurantUpdate(BaseModel):
    """Schema para atualizar restaurante"""
    nome: str | None = None
    descricao: str | None = None
    logo_url: str | None = None
    banner_url: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    hora_abertura: time | None = None
    hora_fecho: time | None = None
    dias_funcionamento: list[int] | None = None
    raio_entrega_km: int | None = None
    tempo_preparo_min: int | None = None
    pedido_minimo: float | None = None
    taxa_entrega: float | None = None
    categorias: list[str] | None = None
    telefone: str | None = None
    aberto: bool | None = None


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
    logo_url: str | None
    categorias: list[str] | None
    rating_medio: float
    tempo_preparo_min: int
    taxa_entrega: float
    aberto: bool
    distancia_km: float | None = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Menu Schemas
# ============================================

class MenuCategoryBase(BaseModel):
    """Schema base de categoria"""
    nome: str = Field(..., min_length=2, max_length=80)
    descricao: str | None = None
    ordem: int = 0


class MenuCategoryCreate(MenuCategoryBase):
    pass


class MenuCategoryResponse(MenuCategoryBase):
    id: UUID
    restaurant_id: UUID
    ativo: bool
    items: list["MenuItemResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)


class MenuItemBase(BaseModel):
    """Schema base de item"""
    nome: str = Field(..., min_length=2, max_length=120)
    descricao: str | None = None
    imagem_url: str | None = None
    preco: float = Field(..., gt=0)
    preco_promocional: float | None = None
    tempo_preparo_min: int | None = None
    opcoes: list[dict] | None = None  # [{nome, opcoes: [{nome, preco_adicional}]}]
    info_nutricional: dict | None = None
    popular: bool = False


class MenuItemCreate(MenuItemBase):
    category_id: UUID


class MenuItemUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    imagem_url: str | None = None
    preco: float | None = None
    preco_promocional: float | None = None
    tempo_preparo_min: int | None = None
    opcoes: list[dict] | None = None
    info_nutricional: dict | None = None
    popular: bool | None = None
    status: MenuItemStatus | None = None
    category_id: UUID | None = None


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
    opcoes_selecionadas: list[dict] | None = None
    notas: str | None = None


class FoodOrderCreate(BaseModel):
    """Schema para criar pedido"""
    restaurant_id: UUID
    items: list[OrderItemCreate]
    endereco_entrega: str = Field(..., min_length=5)
    latitude_entrega: float = Field(..., ge=-90, le=90)
    longitude_entrega: float = Field(..., ge=-180, le=180)
    referencia_entrega: str | None = None
    telefone_contato: str = Field(..., min_length=9)
    notas: str | None = None


class OrderItemResponse(BaseModel):
    """Resposta de item"""
    id: UUID
    menu_item_id: UUID
    quantidade: int
    preco_unitario: float
    subtotal: float
    opcoes_selecionadas: list[dict] | None
    notas: str | None
    item_nome: str
    
    model_config = ConfigDict(from_attributes=True)


class FoodOrderResponse(BaseModel):
    """Schema de resposta de pedido"""
    id: UUID
    customer_id: UUID
    restaurant_id: UUID
    driver_id: UUID | None
    endereco_entrega: str
    latitude_entrega: float
    longitude_entrega: float
    referencia_entrega: str | None
    subtotal: float
    taxa_entrega: float
    desconto: float
    total: float
    telefone_contato: str
    notas: str | None
    tempo_preparo_estimado: int
    tempo_entrega_estimado: int | None
    codigo_entrega: str | None
    status: FoodOrderStatus
    created_at: datetime
    aceite_at: datetime | None
    pronto_at: datetime | None
    recolhido_at: datetime | None
    entregue_at: datetime | None
    items: list[OrderItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class FoodOrderDetailResponse(FoodOrderResponse):
    """Resposta detalhada"""
    restaurant_nome: str
    restaurant_telefone: str
    driver_nome: str | None = None
    driver_telefone: str | None = None


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
    nota_entrega: int | None = Field(None, ge=1, le=5)
    nota_geral: int = Field(..., ge=1, le=5)
    comentario: str | None = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    id: UUID
    restaurant_id: UUID
    user_id: UUID
    nota_comida: int
    nota_entrega: int | None
    nota_geral: int
    comentario: str | None
    created_at: datetime
    user_nome: str | None = None
    
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
