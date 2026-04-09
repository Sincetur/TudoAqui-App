"""
TUDOaqui API - Events Schemas
"""
from datetime import datetime, date, time
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from src.events.models import EventStatus, TicketStatus


# ============================================
# Event Schemas
# ============================================

class EventBase(BaseModel):
    """Schema base de evento"""
    titulo: str = Field(..., min_length=3, max_length=150)
    descricao: str | None = Field(None, max_length=2000)
    local: str = Field(..., min_length=3, max_length=150)
    local_latitude: float | None = Field(None, ge=-90, le=90)
    local_longitude: float | None = Field(None, ge=-180, le=180)
    data_evento: date
    hora_evento: time
    data_fim: date | None = None
    imagem_url: str | None = None
    categoria: str | None = Field(None, max_length=50)


class EventCreate(EventBase):
    """Schema para criar evento"""
    pass


class EventUpdate(BaseModel):
    """Schema para atualizar evento"""
    titulo: str | None = Field(None, max_length=150)
    descricao: str | None = None
    local: str | None = Field(None, max_length=150)
    local_latitude: float | None = None
    local_longitude: float | None = None
    data_evento: date | None = None
    hora_evento: time | None = None
    data_fim: date | None = None
    imagem_url: str | None = None
    categoria: str | None = None
    status: EventStatus | None = None


class EventResponse(EventBase):
    """Schema de resposta de evento"""
    id: UUID
    organizer_id: UUID
    status: EventStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EventDetailResponse(EventResponse):
    """Schema detalhado de evento com tipos de ticket"""
    ticket_types: list["TicketTypeResponse"] = []
    total_vendido: int = 0
    receita_total: float = 0


# ============================================
# TicketType Schemas
# ============================================

class TicketTypeBase(BaseModel):
    """Schema base de tipo de ticket"""
    nome: str = Field(..., min_length=2, max_length=50)
    descricao: str | None = None
    preco: float = Field(..., ge=0)
    quantidade_total: int = Field(..., ge=1)
    max_por_compra: int = Field(10, ge=1, le=50)


class TicketTypeCreate(TicketTypeBase):
    """Schema para criar tipo de ticket"""
    pass


class TicketTypeUpdate(BaseModel):
    """Schema para atualizar tipo de ticket"""
    nome: str | None = Field(None, max_length=50)
    descricao: str | None = None
    preco: float | None = Field(None, ge=0)
    quantidade_total: int | None = Field(None, ge=1)
    max_por_compra: int | None = Field(None, ge=1, le=50)
    ativo: bool | None = None


class TicketTypeResponse(TicketTypeBase):
    """Schema de resposta de tipo de ticket"""
    id: UUID
    event_id: UUID
    quantidade_vendida: int
    quantidade_disponivel: int = 0
    ativo: bool
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Ticket Schemas
# ============================================

class TicketPurchaseRequest(BaseModel):
    """Request para comprar tickets"""
    ticket_type_id: UUID
    quantidade: int = Field(..., ge=1, le=10)


class TicketResponse(BaseModel):
    """Schema de resposta de ticket"""
    id: UUID
    ticket_type_id: UUID
    buyer_id: UUID
    qr_code: str
    status: TicketStatus
    created_at: datetime
    used_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class TicketDetailResponse(TicketResponse):
    """Schema detalhado do ticket com info do evento"""
    event_titulo: str
    event_data: date
    event_hora: time
    event_local: str
    ticket_type_nome: str
    ticket_type_preco: float


class TicketValidationResponse(BaseModel):
    """Resposta da validação de ticket"""
    valid: bool
    message: str
    ticket: TicketDetailResponse | None = None


# ============================================
# CheckIn Schemas
# ============================================

class CheckInRequest(BaseModel):
    """Request para fazer check-in"""
    qr_code: str = Field(..., min_length=10)
    device_info: str | None = None


class CheckInResponse(BaseModel):
    """Resposta do check-in"""
    success: bool
    message: str
    ticket: TicketDetailResponse | None = None
    checkin_id: UUID | None = None
    scanned_at: datetime | None = None


# ============================================
# Stats Schemas
# ============================================

class EventStats(BaseModel):
    """Estatísticas do evento"""
    total_tickets_vendidos: int
    total_checkins: int
    receita_total: float
    taxa_checkin: float  # percentual


# Update forward references
EventDetailResponse.model_rebuild()
