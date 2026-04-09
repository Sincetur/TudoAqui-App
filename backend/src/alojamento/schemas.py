"""
TUDOaqui API - Alojamento Schemas
"""
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
    descricao: str | None = None
    tipo: PropertyType = PropertyType.CASA
    endereco: str = Field(..., min_length=5)
    cidade: str = Field(..., min_length=2, max_length=100)
    provincia: str = Field(..., min_length=2, max_length=100)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
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
    comodidades: list[str] | None = None
    imagens: list[str] | None = None


class PropertyCreate(PropertyBase):
    """Schema para criar propriedade"""
    pass


class PropertyUpdate(BaseModel):
    """Schema para atualizar propriedade"""
    titulo: str | None = None
    descricao: str | None = None
    tipo: PropertyType | None = None
    endereco: str | None = None
    cidade: str | None = None
    provincia: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    quartos: int | None = None
    camas: int | None = None
    banheiros: int | None = None
    max_hospedes: int | None = None
    preco_noite: float | None = None
    preco_limpeza: float | None = None
    desconto_semanal: int | None = None
    desconto_mensal: int | None = None
    min_noites: int | None = None
    max_noites: int | None = None
    checkin_hora: str | None = None
    checkout_hora: str | None = None
    comodidades: list[str] | None = None
    imagens: list[str] | None = None
    status: PropertyStatus | None = None


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
    imagem_principal: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Availability Schemas
# ============================================

class AvailabilityUpdate(BaseModel):
    """Atualizar disponibilidade"""
    data_inicio: date
    data_fim: date
    disponivel: bool = True
    preco_especial: float | None = None
    motivo_bloqueio: str | None = None


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
    notas: str | None = None


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
    notas: str | None
    status: BookingStatus
    created_at: datetime
    confirmada_at: datetime | None
    checkin_at: datetime | None
    checkout_at: datetime | None
    
    model_config = ConfigDict(from_attributes=True)


class BookingDetailResponse(BookingResponse):
    """Resposta detalhada com info da propriedade"""
    property_titulo: str
    property_endereco: str
    property_cidade: str
    host_nome: str | None
    host_telefone: str


class BookingStatusUpdate(BaseModel):
    """Atualizar status da reserva"""
    status: BookingStatus
    motivo_cancelamento: str | None = None


# ============================================
# Review Schemas
# ============================================

class ReviewCreate(BaseModel):
    """Schema para criar avaliação"""
    nota_geral: int = Field(..., ge=1, le=5)
    nota_limpeza: int | None = Field(None, ge=1, le=5)
    nota_localizacao: int | None = Field(None, ge=1, le=5)
    nota_comunicacao: int | None = Field(None, ge=1, le=5)
    nota_valor: int | None = Field(None, ge=1, le=5)
    comentario: str | None = Field(None, max_length=2000)


class ReviewResponse(BaseModel):
    """Schema de resposta de avaliação"""
    id: UUID
    property_id: UUID
    guest_id: UUID
    nota_geral: int
    nota_limpeza: int | None
    nota_localizacao: int | None
    nota_comunicacao: int | None
    nota_valor: int | None
    comentario: str | None
    created_at: datetime
    guest_nome: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Search Schemas
# ============================================

class PropertySearchParams(BaseModel):
    """Parâmetros de busca"""
    cidade: str | None = None
    provincia: str | None = None
    tipo: PropertyType | None = None
    data_checkin: date | None = None
    data_checkout: date | None = None
    hospedes: int | None = None
    preco_min: float | None = None
    preco_max: float | None = None
    quartos_min: int | None = None


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
