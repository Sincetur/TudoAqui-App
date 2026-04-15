"""
TUDOaqui API - Tuendi Schemas
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from src.tuendi.drivers.models import DriverStatus
from src.tuendi.rides.models import RideStatus


# ============================================
# Location Schemas
# ============================================

class LocationBase(BaseModel):
    """Schema base de localização"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class LocationWithAddress(LocationBase):
    """Localização com endereço"""
    endereco: str = Field(..., min_length=5, max_length=500)


# ============================================
# Driver Schemas
# ============================================

class DriverBase(BaseModel):
    """Schema base de motorista"""
    veiculo: str = Field(..., min_length=2, max_length=100, examples=["Toyota Corolla"])
    matricula: str = Field(..., min_length=4, max_length=30, examples=["LD-00-00-AA"])
    cor_veiculo: Optional[str] = Field(None, max_length=50, examples=["Branco"])
    marca: Optional[str] = Field(None, max_length=50, examples=["Toyota"])
    modelo: Optional[str] = Field(None, max_length=50, examples=["Corolla"])
    ano: Optional[int] = Field(None, ge=1990, le=2030, examples=[2020])


class DriverCreate(DriverBase):
    """Schema para criar motorista"""
    carta_conducao: Optional[str] = Field(None, max_length=50)
    documento_veiculo: Optional[str] = Field(None, max_length=100)


class DriverUpdate(BaseModel):
    """Schema para atualizar motorista"""
    veiculo: Optional[str] = Field(None, max_length=100)
    cor_veiculo: Optional[str] = Field(None, max_length=50)
    marca: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None, max_length=50)
    ano: Optional[int] = Field(None, ge=1990, le=2030)


class DriverLocationUpdate(LocationBase):
    """Schema para atualizar localização do motorista"""
    pass


class DriverOnlineUpdate(BaseModel):
    """Schema para atualizar status online"""
    online: bool
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class DriverResponse(DriverBase):
    """Schema de resposta de motorista"""
    id: UUID
    user_id: UUID
    online: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating_medio: float = 5.00
    total_corridas: int = 0
    status: DriverStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DriverPublicResponse(BaseModel):
    """Schema público de motorista (para cliente)"""
    id: UUID
    nome: Optional[str] = None
    telefone: Optional[str] = None
    avatar_url: Optional[str] = None
    veiculo: str
    matricula: str
    cor_veiculo: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    rating_medio: float = 5.00
    total_corridas: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class NearbyDriver(BaseModel):
    """Motorista próximo"""
    driver_id: UUID
    latitude: float
    longitude: float
    distancia_metros: float
    tempo_estimado_min: int


# ============================================
# Ride Schemas
# ============================================

class RideEstimateRequest(BaseModel):
    """Request para estimativa de corrida"""
    origem: LocationWithAddress
    destino: LocationWithAddress


class RideEstimateResponse(BaseModel):
    """Response com estimativa de corrida"""
    distancia_km: float
    duracao_estimada_min: int
    valor_estimado: float
    motoristas_disponiveis: int


class RideRequestCreate(BaseModel):
    """Schema para solicitar corrida"""
    origem_endereco: str = Field(..., min_length=5)
    origem_latitude: float = Field(..., ge=-90, le=90)
    origem_longitude: float = Field(..., ge=-180, le=180)
    destino_endereco: str = Field(..., min_length=5)
    destino_latitude: float = Field(..., ge=-90, le=90)
    destino_longitude: float = Field(..., ge=-180, le=180)


class RideResponse(BaseModel):
    """Schema de resposta de corrida"""
    id: UUID
    cliente_id: UUID
    motorista_id: Optional[UUID] = None
    
    origem_endereco: str
    origem_latitude: float
    origem_longitude: float
    destino_endereco: str
    destino_latitude: float
    destino_longitude: float
    
    distancia_km: Optional[float] = None
    duracao_estimada_min: Optional[int] = None
    valor_estimado: Optional[float] = None
    valor_final: Optional[float] = None
    
    status: RideStatus
    
    solicitada_at: datetime
    aceite_at: Optional[datetime] = None
    iniciada_at: Optional[datetime] = None
    finalizada_at: Optional[datetime] = None
    cancelada_at: Optional[datetime] = None
    motivo_cancelamento: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class RideWithDriverResponse(RideResponse):
    """Corrida com dados do motorista"""
    motorista: Optional[DriverPublicResponse] = None


class RideCancelRequest(BaseModel):
    """Request para cancelar corrida"""
    motivo: Optional[str] = Field(None, max_length=500)


class RideTrackingPoint(BaseModel):
    """Ponto de tracking"""
    latitude: float
    longitude: float
    velocidade: Optional[float] = None
    bearing: Optional[float] = None
    timestamp: datetime


# ============================================
# Rating Schemas
# ============================================

class RatingCreate(BaseModel):
    """Schema para criar avaliação"""
    nota: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = Field(None, max_length=500)


class RatingResponse(BaseModel):
    """Schema de resposta de avaliação"""
    id: UUID
    ride_id: UUID
    nota: int
    comentario: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Stats Schemas
# ============================================

class DriverStats(BaseModel):
    """Estatísticas do motorista"""
    total_corridas: int
    total_ganhos: float
    rating_medio: float
    corridas_hoje: int
    ganhos_hoje: float


class ClientStats(BaseModel):
    """Estatísticas do cliente"""
    total_corridas: int
    total_gasto: float
    corridas_mes: int
