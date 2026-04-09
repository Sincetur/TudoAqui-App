"""
TUDOaqui API - Tuendi Entrega Schemas
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from src.tuendi.entrega.models import DeliveryType, DeliveryStatus, DeliveryPriority


# ============================================
# Delivery Schemas
# ============================================

class LocationData(BaseModel):
    """Dados de localização"""
    endereco: str = Field(..., min_length=5)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    referencia: str | None = None
    contato_nome: str = Field(..., min_length=2, max_length=120)
    contato_telefone: str = Field(..., min_length=9)


class DeliveryEstimateRequest(BaseModel):
    """Request para estimar preço"""
    origem_latitude: float = Field(..., ge=-90, le=90)
    origem_longitude: float = Field(..., ge=-180, le=180)
    destino_latitude: float = Field(..., ge=-90, le=90)
    destino_longitude: float = Field(..., ge=-180, le=180)
    tipo: DeliveryType = DeliveryType.PACOTE_PEQUENO
    prioridade: DeliveryPriority = DeliveryPriority.NORMAL
    peso_estimado: float | None = None


class DeliveryEstimateResponse(BaseModel):
    """Resposta da estimativa"""
    distancia_km: float
    duracao_estimada_min: int
    preco_base: float
    taxa_prioridade: float
    taxa_peso: float
    total: float


class DeliveryCreate(BaseModel):
    """Schema para criar entrega"""
    tipo: DeliveryType = DeliveryType.PACOTE_PEQUENO
    prioridade: DeliveryPriority = DeliveryPriority.NORMAL
    descricao: str = Field(..., min_length=5, max_length=500)
    peso_estimado: float | None = None
    
    # Origem
    origem_endereco: str = Field(..., min_length=5)
    origem_latitude: float = Field(..., ge=-90, le=90)
    origem_longitude: float = Field(..., ge=-180, le=180)
    origem_referencia: str | None = None
    origem_contato_nome: str = Field(..., min_length=2, max_length=120)
    origem_contato_telefone: str = Field(..., min_length=9)
    
    # Destino
    destino_endereco: str = Field(..., min_length=5)
    destino_latitude: float = Field(..., ge=-90, le=90)
    destino_longitude: float = Field(..., ge=-180, le=180)
    destino_referencia: str | None = None
    destino_contato_nome: str = Field(..., min_length=2, max_length=120)
    destino_contato_telefone: str = Field(..., min_length=9)
    
    # Instruções
    instrucoes_recolha: str | None = None
    instrucoes_entrega: str | None = None


class DeliveryResponse(BaseModel):
    """Schema de resposta de entrega"""
    id: UUID
    sender_id: UUID
    driver_id: UUID | None
    tipo: DeliveryType
    prioridade: DeliveryPriority
    descricao: str
    peso_estimado: float | None
    
    origem_endereco: str
    origem_latitude: float
    origem_longitude: float
    origem_referencia: str | None
    origem_contato_nome: str
    origem_contato_telefone: str
    
    destino_endereco: str
    destino_latitude: float
    destino_longitude: float
    destino_referencia: str | None
    destino_contato_nome: str
    destino_contato_telefone: str
    
    distancia_km: float
    preco_base: float
    taxa_prioridade: float
    taxa_peso: float
    total: float
    
    instrucoes_recolha: str | None
    instrucoes_entrega: str | None
    
    codigo_recolha: str | None
    codigo_entrega: str | None
    
    status: DeliveryStatus
    created_at: datetime
    aceite_at: datetime | None
    recolhido_at: datetime | None
    entregue_at: datetime | None
    
    model_config = ConfigDict(from_attributes=True)


class DeliveryDetailResponse(DeliveryResponse):
    """Resposta detalhada com info do motorista"""
    driver_nome: str | None = None
    driver_telefone: str | None = None
    driver_foto: str | None = None
    driver_veiculo: str | None = None
    driver_placa: str | None = None


class DeliveryListResponse(BaseModel):
    """Lista simplificada"""
    id: UUID
    tipo: DeliveryType
    prioridade: DeliveryPriority
    origem_endereco: str
    destino_endereco: str
    total: float
    status: DeliveryStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Tracking Schemas
# ============================================

class TrackingResponse(BaseModel):
    """Histórico de tracking"""
    id: UUID
    status: str
    descricao: str | None
    latitude: float | None
    longitude: float | None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Driver Actions
# ============================================

class ConfirmRecolhaRequest(BaseModel):
    """Confirmar recolha"""
    codigo: str = Field(..., min_length=4, max_length=6)
    foto_url: str | None = None


class ConfirmEntregaRequest(BaseModel):
    """Confirmar entrega"""
    codigo: str = Field(..., min_length=4, max_length=6)
    foto_url: str | None = None


class UpdateLocationRequest(BaseModel):
    """Atualizar localização"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
