"""
TUDOaqui API - Events Models
Módulo de Eventos: Tickets + QR + Check-in
"""
from datetime import datetime, date, time
from enum import Enum
from uuid import UUID
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, Numeric, Text, ForeignKey, Date, Time, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
import uuid

from src.database import Base


class EventStatus(str, Enum):
    RASCUNHO = "rascunho"
    ATIVO = "ativo"
    ENCERRADO = "encerrado"
    CANCELADO = "cancelado"


class TicketStatus(str, Enum):
    ATIVO = "ativo"
    USADO = "usado"
    CANCELADO = "cancelado"
    EXPIRADO = "expirado"


class Event(Base):
    """Modelo de Evento"""
    __tablename__ = "events"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    organizer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    local: Mapped[str] = mapped_column(String(150), nullable=False)
    local_latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 8), nullable=True)
    local_longitude: Mapped[Decimal | None] = mapped_column(Numeric(11, 8), nullable=True)
    
    data_evento: Mapped[date] = mapped_column(Date, nullable=False)
    hora_evento: Mapped[time] = mapped_column(Time, nullable=False)
    data_fim: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    imagem_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    categoria: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), default=EventStatus.RASCUNHO)
    
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
    organizer = relationship("User", backref="organized_events")
    ticket_types = relationship("TicketType", back_populates="event", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Event {self.titulo} ({self.status})>"


class TicketType(Base):
    """Tipos de ingresso para um evento"""
    __tablename__ = "ticket_types"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    event_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False
    )
    
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    preco: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quantidade_total: Mapped[int] = mapped_column(Integer, nullable=False)
    quantidade_vendida: Mapped[int] = mapped_column(Integer, default=0)
    
    # Limites
    max_por_compra: Mapped[int] = mapped_column(Integer, default=10)
    
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    event = relationship("Event", back_populates="ticket_types")
    tickets = relationship("Ticket", back_populates="ticket_type", cascade="all, delete-orphan")
    
    @property
    def quantidade_disponivel(self) -> int:
        return self.quantidade_total - self.quantidade_vendida
    
    @property
    def esgotado(self) -> bool:
        return self.quantidade_disponivel <= 0


class Ticket(Base):
    """Ingresso comprado"""
    __tablename__ = "tickets"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    ticket_type_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("ticket_types.id", ondelete="CASCADE"),
        nullable=False
    )
    buyer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    
    # QR Code único (hash: ticket_id + event_id + secret)
    qr_code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    status: Mapped[str] = mapped_column(String(20), default=TicketStatus.ATIVO)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    ticket_type = relationship("TicketType", back_populates="tickets")
    buyer = relationship("User", backref="purchased_tickets")
    checkin = relationship("CheckIn", back_populates="ticket", uselist=False)
    
    def __repr__(self) -> str:
        return f"<Ticket {self.qr_code[:8]}... ({self.status})>"


class CheckIn(Base):
    """Registro de check-in no evento"""
    __tablename__ = "checkins"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    ticket_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("tickets.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    event_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("events.id"),
        nullable=False
    )
    staff_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    
    device_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    ticket = relationship("Ticket", back_populates="checkin")
    event = relationship("Event", backref="checkins")
    staff = relationship("User", backref="checkins_realizados")
