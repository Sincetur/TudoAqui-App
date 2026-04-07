"""
TUDOaqui API - Tuendi Schemas
"""
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
    cor_veiculo: str | None = Field(None, max_length=50, examples=["Branco"])
    marca: str | None = Field(None, max_length=50, examples=["Toyota"])
    modelo: str | None = Field(None, max_length=50, examples=["Corolla"])
    ano: int | None = Field(None, ge=1990, le=2030, examples=[2020])


class DriverCreate(DriverBase):
    """Schema para criar motorista"""
    carta_conducao: str | None = Field(None, max_length=50)
    documento_veiculo: str | None = Field(None, max_length=100)


class DriverUpdate(BaseModel):
    """Schema para atualizar motorista"""
    veiculo: str | None = Field(None, max_length=100)
    cor_veiculo: str | None = Field(None, max_length=50)
    marca: str | None = Field(None, max_length=50)
    modelo: str | None = Field(None, max_length=50)
    ano: int | None = Field(None, ge=1990, le=2030)


class DriverLocationUpdate(LocationBase):
    """Schema para atualizar localização do motorista"""
    pass


class DriverOnlineUpdate(BaseModel):
    """Schema para atualizar status online"""
    online: bool
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)


class DriverResponse(DriverBase):
    """Schema de resposta de motorista"""
    id: UUID
    user_id: UUID
    online: bool
    latitude: float | None = None
    longitude: float | None = None
    rating_medio: float = 5.00
    total_corridas: int = 0
    status: DriverStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DriverPublicResponse(BaseModel):
    """Schema público de motorista (para cliente)"""
    id: UUID
    nome: str | None = None
    telefone: str | None = None
    avatar_url: str | None = None
    veiculo: str
    matricula: str
    cor_veiculo: str | None = None
    marca: str | None = None
    modelo: str | None = None
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
    motorista_id: UUID | None = None
    
    origem_endereco: str
    origem_latitude: float
    origem_longitude: float
    destino_endereco: str
    destino_latitude: float
    destino_longitude: float
    
    distancia_km: float | None = None
    duracao_estimada_min: int | None = None
    valor_estimado: float | None = None
    valor_final: float | None = None
    
    status: RideStatus
    
    solicitada_at: datetime
    aceite_at: datetime | None = None
    iniciada_at: datetime | None = None
    finalizada_at: datetime | None = None
    cancelada_at: datetime | None = None
    motivo_cancelamento: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


class RideWithDriverResponse(RideResponse):
    """Corrida com dados do motorista"""
    motorista: DriverPublicResponse | None = None


class RideCancelRequest(BaseModel):
    """Request para cancelar corrida"""
    motivo: str | None = Field(None, max_length=500)


class RideTrackingPoint(BaseModel):
    """Ponto de tracking"""
    latitude: float
    longitude: float
    velocidade: float | None = None
    bearing: float | None = None
    timestamp: datetime


# ============================================
# Rating Schemas
# ============================================

class RatingCreate(BaseModel):
    """Schema para criar avaliação"""
    nota: int = Field(..., ge=1, le=5)
    comentario: str | None = Field(None, max_length=500)


class RatingResponse(BaseModel):
    """Schema de resposta de avaliação"""
    id: UUID
    ride_id: UUID
    nota: int
    comentario: str | None = None
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
