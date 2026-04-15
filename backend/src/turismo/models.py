"""
TUDOaqui API - Turismo Models
Módulo Turismo: Experiências & Pacotes
"""
from typing import Optional
from datetime import datetime, date, time
from enum import Enum
from uuid import UUID
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, Numeric, Text, ForeignKey, Boolean, Date, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.sql import func
import uuid

from src.database import Base


class ExperienceType(str, Enum):
    TOUR = "tour"
    AVENTURA = "aventura"
    CULTURAL = "cultural"
    GASTRONOMIA = "gastronomia"
    NATUREZA = "natureza"
    WORKSHOP = "workshop"
    PACOTE = "pacote"


class ExperienceStatus(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    RASCUNHO = "rascunho"


class ExperienceBookingStatus(str, Enum):
    PENDENTE = "pendente"
    CONFIRMADA = "confirmada"
    REALIZADA = "realizada"
    CANCELADA = "cancelada"
    NO_SHOW = "no_show"


class Experience(Base):
    """Experiência turística"""
    __tablename__ = "experiences"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    host_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(String(30), default=ExperienceType.TOUR)
    
    # Localização
    local: Mapped[str] = mapped_column(String(150), nullable=False)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False)
    ponto_encontro: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8), nullable=True)
    
    # Duração e capacidade
    duracao_horas: Mapped[int] = mapped_column(Integer, default=2)
    min_participantes: Mapped[int] = mapped_column(Integer, default=1)
    max_participantes: Mapped[int] = mapped_column(Integer, default=10)
    
    # Preço
    preco: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    preco_crianca: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    
    # O que está incluído (JSON array)
    inclui: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    nao_inclui: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    requisitos: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Imagens
    imagens: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Idiomas disponíveis
    idiomas: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Stats
    rating_medio: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=5.00)
    total_reservas: Mapped[int] = mapped_column(Integer, default=0)
    total_avaliacoes: Mapped[int] = mapped_column(Integer, default=0)
    
    status: Mapped[str] = mapped_column(String(20), default=ExperienceStatus.RASCUNHO)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    host = relationship("User", backref="experiences_hosted")
    schedules = relationship("ExperienceSchedule", back_populates="experience", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Experience {self.titulo} ({self.preco} Kz)>"


class ExperienceSchedule(Base):
    """Horários disponíveis para experiência"""
    __tablename__ = "experience_schedules"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    experience_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("experiences.id", ondelete="CASCADE"),
        nullable=False
    )
    
    data: Mapped[date] = mapped_column(Date, nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    
    vagas_disponiveis: Mapped[int] = mapped_column(Integer, nullable=False)
    vagas_reservadas: Mapped[int] = mapped_column(Integer, default=0)
    
    preco_especial: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    experience = relationship("Experience", back_populates="schedules")
    
    @property
    def vagas_livres(self) -> int:
        return self.vagas_disponiveis - self.vagas_reservadas
    
    @property
    def esgotado(self) -> bool:
        return self.vagas_livres <= 0


class ExperienceBooking(Base):
    """Reserva de experiência"""
    __tablename__ = "experience_bookings"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    experience_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("experiences.id"),
        nullable=False
    )
    schedule_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("experience_schedules.id"),
        nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Participantes
    adultos: Mapped[int] = mapped_column(Integer, default=1)
    criancas: Mapped[int] = mapped_column(Integer, default=0)
    
    # Valores
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    preco_crianca: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    taxa_servico: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    # QR Voucher
    qr_voucher: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    # Contato
    telefone_contato: Mapped[str] = mapped_column(String(20), nullable=False)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Integração Tuendi
    tuendi_transporte_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), default=ExperienceBookingStatus.PENDENTE)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    confirmada_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    validada_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelada_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    experience = relationship("Experience", backref="bookings")
    schedule = relationship("ExperienceSchedule", backref="bookings")
    user = relationship("User", backref="experience_bookings")


class ExperienceReview(Base):
    """Avaliação de experiência"""
    __tablename__ = "experience_reviews"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    experience_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("experiences.id", ondelete="CASCADE"),
        nullable=False
    )
    booking_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("experience_bookings.id"),
        nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    
    nota: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    comentario: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
