"""
TUDOaqui API - Events Schemas
"""
from typing import List, Optional
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
    descricao: Optional[str] = Field(None, max_length=2000)
    local: str = Field(..., min_length=3, max_length=150)
    local_latitude: Optional[float] = Field(None, ge=-90, le=90)
    local_longitude: Optional[float] = Field(None, ge=-180, le=180)
    data_evento: date
    hora_evento: time
    data_fim: Optional[date] = None
    imagem_url: Optional[str] = None
    categoria: Optional[str] = Field(None, max_length=50)


class EventCreate(EventBase):
    """Schema para criar evento"""
    pass


class EventUpdate(BaseModel):
    """Schema para atualizar evento"""
    titulo: Optional[str] = Field(None, max_length=150)
    descricao: Optional[str] = None
    local: Optional[str] = Field(None, max_length=150)
    local_latitude: Optional[float] = None
    local_longitude: Optional[float] = None
    data_evento: Optional[date] = None
    hora_evento: Optional[time] = None
    data_fim: Optional[date] = None
    imagem_url: Optional[str] = None
    categoria: Optional[str] = None
    status: Optional[EventStatus] = None


class EventResponse(EventBase):
    """Schema de resposta de evento"""
    id: UUID
    organizer_id: UUID
    status: EventStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EventDetailResponse(EventResponse):
    """Schema detalhado de evento com tipos de ticket"""
    ticket_types: List["TicketTypeResponse"] = []
    total_vendido: int = 0
    receita_total: float = 0


# ============================================
# TicketType Schemas
# ============================================

class TicketTypeBase(BaseModel):
    """Schema base de tipo de ticket"""
    nome: str = Field(..., min_length=2, max_length=50)
    descricao: Optional[str] = None
    preco: float = Field(..., ge=0)
    quantidade_total: int = Field(..., ge=1)
    max_por_compra: int = Field(10, ge=1, le=50)


class TicketTypeCreate(TicketTypeBase):
    """Schema para criar tipo de ticket"""
    pass


class TicketTypeUpdate(BaseModel):
    """Schema para atualizar tipo de ticket"""
    nome: Optional[str] = Field(None, max_length=50)
    descricao: Optional[str] = None
    preco: Optional[float] = Field(None, ge=0)
    quantidade_total: Optional[int] = Field(None, ge=1)
    max_por_compra: Optional[int] = Field(None, ge=1, le=50)
    ativo: Optional[bool] = None


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
    used_at: Optional[datetime] = None
    
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
    ticket: Optional[TicketDetailResponse] = None


# ============================================
# CheckIn Schemas
# ============================================

class CheckInRequest(BaseModel):
    """Request para fazer check-in"""
    qr_code: str = Field(..., min_length=10)
    device_info: Optional[str] = None


class CheckInResponse(BaseModel):
    """Resposta do check-in"""
    success: bool
    message: str
    ticket: Optional[TicketDetailResponse] = None
    checkin_id: Optional[UUID] = None
    scanned_at: Optional[datetime] = None


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
