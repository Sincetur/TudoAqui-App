"""
TUDOaqui API - Alojamento Schemas
"""
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from src.alojamento.models import PropertyType, PropertyStatus, BookingStatus


# ============================================
# Property Schemas
# ============================================

class PropertyBase(BaseModel):
    """Schema base de propriedade"""
    titulo: str = Field(..., min_length=3, max_length=150)
    descricao: Optional[str] = None
    tipo: PropertyType = PropertyType.CASA
    endereco: str = Field(..., min_length=5)
    cidade: str = Field(..., min_length=2, max_length=100)
    provincia: str = Field(..., min_length=2, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    quartos: int = Field(1, ge=0, le=50)
    camas: int = Field(1, ge=1, le=100)
    banheiros: int = Field(1, ge=0, le=50)
    max_hospedes: int = Field(2, ge=1, le=50)
    preco_noite: float = Field(..., gt=0)
    preco_limpeza: float = Field(0, ge=0)
    desconto_semanal: int = Field(0, ge=0, le=100)
    desconto_mensal: int = Field(0, ge=0, le=100)
    min_noites: int = Field(1, ge=1)
    max_noites: int = Field(30, ge=1, le=365)
    checkin_hora: str = Field("15:00", pattern=r"^\d{2}:\d{2}$")
    checkout_hora: str = Field("11:00", pattern=r"^\d{2}:\d{2}$")
    comodidades: Optional[List[str]] = None
    imagens: Optional[List[str]] = None


class PropertyCreate(PropertyBase):
    """Schema para criar propriedade"""
    pass


class PropertyUpdate(BaseModel):
    """Schema para atualizar propriedade"""
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[PropertyType] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    provincia: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    quartos: Optional[int] = None
    camas: Optional[int] = None
    banheiros: Optional[int] = None
    max_hospedes: Optional[int] = None
    preco_noite: Optional[float] = None
    preco_limpeza: Optional[float] = None
    desconto_semanal: Optional[int] = None
    desconto_mensal: Optional[int] = None
    min_noites: Optional[int] = None
    max_noites: Optional[int] = None
    checkin_hora: Optional[str] = None
    checkout_hora: Optional[str] = None
    comodidades: Optional[List[str]] = None
    imagens: Optional[List[str]] = None
    status: Optional[PropertyStatus] = None


class PropertyResponse(PropertyBase):
    """Schema de resposta de propriedade"""
    id: UUID
    host_id: UUID
    rating_medio: float
    total_reservas: int
    total_avaliacoes: int
    status: PropertyStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PropertyListResponse(BaseModel):
    """Schema simplificado para listagem"""
    id: UUID
    titulo: str
    tipo: PropertyType
    cidade: str
    provincia: str
    preco_noite: float
    quartos: int
    max_hospedes: int
    rating_medio: float
    imagem_principal: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Availability Schemas
# ============================================

class AvailabilityUpdate(BaseModel):
    """Atualizar disponibilidade"""
    data_inicio: date
    data_fim: date
    disponivel: bool = True
    preco_especial: Optional[float] = None
    motivo_bloqueio: Optional[str] = None


class AvailabilityResponse(BaseModel):
    """Resposta de disponibilidade"""
    data: date
    disponivel: bool
    preco: float
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Booking Schemas
# ============================================

class BookingCreate(BaseModel):
    """Schema para criar reserva"""
    property_id: UUID
    data_checkin: date
    data_checkout: date
    adultos: int = Field(1, ge=1, le=20)
    criancas: int = Field(0, ge=0, le=20)
    telefone_contato: str = Field(..., min_length=9)
    notas: Optional[str] = None


class BookingResponse(BaseModel):
    """Schema de resposta de reserva"""
    id: UUID
    property_id: UUID
    guest_id: UUID
    data_checkin: date
    data_checkout: date
    noites: int
    adultos: int
    criancas: int
    preco_noite: float
    subtotal: float
    taxa_limpeza: float
    taxa_servico: float
    desconto: float
    total: float
    telefone_contato: str
    notas: Optional[str]
    status: BookingStatus
    created_at: datetime
    confirmada_at: Optional[datetime]
    checkin_at: Optional[datetime]
    checkout_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class BookingDetailResponse(BookingResponse):
    """Resposta detalhada com info da propriedade"""
    property_titulo: str
    property_endereco: str
    property_cidade: str
    host_nome: Optional[str]
    host_telefone: str


class BookingStatusUpdate(BaseModel):
    """Atualizar status da reserva"""
    status: BookingStatus
    motivo_cancelamento: Optional[str] = None


# ============================================
# Review Schemas
# ============================================

class ReviewCreate(BaseModel):
    """Schema para criar avaliação"""
    nota_geral: int = Field(..., ge=1, le=5)
    nota_limpeza: Optional[int] = Field(None, ge=1, le=5)
    nota_localizacao: Optional[int] = Field(None, ge=1, le=5)
    nota_comunicacao: Optional[int] = Field(None, ge=1, le=5)
    nota_valor: Optional[int] = Field(None, ge=1, le=5)
    comentario: Optional[str] = Field(None, max_length=2000)


class ReviewResponse(BaseModel):
    """Schema de resposta de avaliação"""
    id: UUID
    property_id: UUID
    guest_id: UUID
    nota_geral: int
    nota_limpeza: Optional[int]
    nota_localizacao: Optional[int]
    nota_comunicacao: Optional[int]
    nota_valor: Optional[int]
    comentario: Optional[str]
    created_at: datetime
    guest_nome: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Search Schemas
# ============================================

class PropertySearchParams(BaseModel):
    """Parâmetros de busca"""
    cidade: Optional[str] = None
    provincia: Optional[str] = None
    tipo: Optional[PropertyType] = None
    data_checkin: Optional[date] = None
    data_checkout: Optional[date] = None
    hospedes: Optional[int] = None
    preco_min: Optional[float] = None
    preco_max: Optional[float] = None
    quartos_min: Optional[int] = None


# ============================================
# Stats Schemas
# ============================================

class HostStats(BaseModel):
    """Estatísticas do anfitrião"""
    total_propriedades: int
    total_reservas: int
    reservas_pendentes: int
    receita_total: float
    receita_mes: float
    rating_medio: float
