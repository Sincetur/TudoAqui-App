"""
TUDOaqui API - Tuendi Entrega Schemas
"""
from typing import Optional
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
    referencia: Optional[str] = None
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
    peso_estimado: Optional[float] = None


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
    peso_estimado: Optional[float] = None
    
    # Origem
    origem_endereco: str = Field(..., min_length=5)
    origem_latitude: float = Field(..., ge=-90, le=90)
    origem_longitude: float = Field(..., ge=-180, le=180)
    origem_referencia: Optional[str] = None
    origem_contato_nome: str = Field(..., min_length=2, max_length=120)
    origem_contato_telefone: str = Field(..., min_length=9)
    
    # Destino
    destino_endereco: str = Field(..., min_length=5)
    destino_latitude: float = Field(..., ge=-90, le=90)
    destino_longitude: float = Field(..., ge=-180, le=180)
    destino_referencia: Optional[str] = None
    destino_contato_nome: str = Field(..., min_length=2, max_length=120)
    destino_contato_telefone: str = Field(..., min_length=9)
    
    # Instruções
    instrucoes_recolha: Optional[str] = None
    instrucoes_entrega: Optional[str] = None


class DeliveryResponse(BaseModel):
    """Schema de resposta de entrega"""
    id: UUID
    sender_id: UUID
    driver_id: Optional[UUID]
    tipo: DeliveryType
    prioridade: DeliveryPriority
    descricao: str
    peso_estimado: Optional[float]
    
    origem_endereco: str
    origem_latitude: float
    origem_longitude: float
    origem_referencia: Optional[str]
    origem_contato_nome: str
    origem_contato_telefone: str
    
    destino_endereco: str
    destino_latitude: float
    destino_longitude: float
    destino_referencia: Optional[str]
    destino_contato_nome: str
    destino_contato_telefone: str
    
    distancia_km: float
    preco_base: float
    taxa_prioridade: float
    taxa_peso: float
    total: float
    
    instrucoes_recolha: Optional[str]
    instrucoes_entrega: Optional[str]
    
    codigo_recolha: Optional[str]
    codigo_entrega: Optional[str]
    
    status: DeliveryStatus
    created_at: datetime
    aceite_at: Optional[datetime]
    recolhido_at: Optional[datetime]
    entregue_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class DeliveryDetailResponse(DeliveryResponse):
    """Resposta detalhada com info do motorista"""
    driver_nome: Optional[str] = None
    driver_telefone: Optional[str] = None
    driver_foto: Optional[str] = None
    driver_veiculo: Optional[str] = None
    driver_placa: Optional[str] = None


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
    descricao: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Driver Actions
# ============================================

class ConfirmRecolhaRequest(BaseModel):
    """Confirmar recolha"""
    codigo: str = Field(..., min_length=4, max_length=6)
    foto_url: Optional[str] = None


class ConfirmEntregaRequest(BaseModel):
    """Confirmar entrega"""
    codigo: str = Field(..., min_length=4, max_length=6)
    foto_url: Optional[str] = None


class UpdateLocationRequest(BaseModel):
    """Atualizar localização"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
