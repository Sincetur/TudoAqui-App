"""
TUDOaqui API - Turismo Schemas
"""
from datetime import datetime, date, time
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from src.turismo.models import ExperienceType, ExperienceStatus, ExperienceBookingStatus


# ============================================
# Experience Schemas
# ============================================

class ExperienceBase(BaseModel):
    """Schema base de experiência"""
    titulo: str = Field(..., min_length=3, max_length=150)
    descricao: str | None = None
    tipo: ExperienceType = ExperienceType.TOUR
    local: str = Field(..., min_length=2, max_length=150)
    cidade: str = Field(..., min_length=2, max_length=100)
    ponto_encontro: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    duracao_horas: int = Field(2, ge=1, le=72)
    min_participantes: int = Field(1, ge=1)
    max_participantes: int = Field(10, ge=1, le=100)
    preco: float = Field(..., gt=0)
    preco_crianca: float | None = None
    inclui: list[str] | None = None
    nao_inclui: list[str] | None = None
    requisitos: list[str] | None = None
    imagens: list[str] | None = None
    idiomas: list[str] | None = None


class ExperienceCreate(ExperienceBase):
    """Schema para criar experiência"""
    pass


class ExperienceUpdate(BaseModel):
    """Schema para atualizar experiência"""
    titulo: str | None = None
    descricao: str | None = None
    tipo: ExperienceType | None = None
    local: str | None = None
    cidade: str | None = None
    ponto_encontro: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    duracao_horas: int | None = None
    min_participantes: int | None = None
    max_participantes: int | None = None
    preco: float | None = None
    preco_crianca: float | None = None
    inclui: list[str] | None = None
    nao_inclui: list[str] | None = None
    requisitos: list[str] | None = None
    imagens: list[str] | None = None
    idiomas: list[str] | None = None
    status: ExperienceStatus | None = None


class ExperienceResponse(ExperienceBase):
    """Schema de resposta de experiência"""
    id: UUID
    host_id: UUID
    rating_medio: float
    total_reservas: int
    total_avaliacoes: int
    status: ExperienceStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ExperienceListResponse(BaseModel):
    """Schema simplificado para listagem"""
    id: UUID
    titulo: str
    tipo: ExperienceType
    cidade: str
    duracao_horas: int
    preco: float
    rating_medio: float
    imagem_principal: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Schedule Schemas
# ============================================

class ScheduleCreate(BaseModel):
    """Schema para criar horário"""
    data: date
    hora_inicio: time
    vagas_disponiveis: int = Field(..., ge=1)
    preco_especial: float | None = None


class ScheduleResponse(BaseModel):
    """Schema de resposta de horário"""
    id: UUID
    experience_id: UUID
    data: date
    hora_inicio: time
    vagas_disponiveis: int
    vagas_reservadas: int
    vagas_livres: int = 0
    preco_especial: float | None
    ativo: bool
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Booking Schemas
# ============================================

class ExperienceBookingCreate(BaseModel):
    """Schema para criar reserva"""
    experience_id: UUID
    schedule_id: UUID
    adultos: int = Field(1, ge=1, le=20)
    criancas: int = Field(0, ge=0, le=20)
    telefone_contato: str = Field(..., min_length=9)
    notas: str | None = None


class ExperienceBookingResponse(BaseModel):
    """Schema de resposta de reserva"""
    id: UUID
    experience_id: UUID
    schedule_id: UUID
    user_id: UUID
    adultos: int
    criancas: int
    preco_unitario: float
    preco_crianca: float
    subtotal: float
    taxa_servico: float
    total: float
    qr_voucher: str
    telefone_contato: str
    notas: str | None
    status: ExperienceBookingStatus
    created_at: datetime
    confirmada_at: datetime | None
    validada_at: datetime | None
    
    model_config = ConfigDict(from_attributes=True)


class ExperienceBookingDetailResponse(ExperienceBookingResponse):
    """Resposta detalhada com info da experiência"""
    experience_titulo: str
    experience_local: str
    experience_cidade: str
    schedule_data: date
    schedule_hora: time
    host_nome: str | None


class BookingValidateRequest(BaseModel):
    """Request para validar voucher"""
    qr_voucher: str


# ============================================
# Review Schemas
# ============================================

class ExperienceReviewCreate(BaseModel):
    """Schema para criar avaliação"""
    nota: int = Field(..., ge=1, le=5)
    comentario: str | None = Field(None, max_length=2000)


class ExperienceReviewResponse(BaseModel):
    """Schema de resposta de avaliação"""
    id: UUID
    experience_id: UUID
    user_id: UUID
    nota: int
    comentario: str | None
    created_at: datetime
    user_nome: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Stats Schemas
# ============================================

class TurismoHostStats(BaseModel):
    """Estatísticas do anfitrião de turismo"""
    total_experiencias: int
    total_reservas: int
    reservas_pendentes: int
    receita_total: float
    rating_medio: float
