"""
TUDOaqui API - Alojamento Models
Módulo Alojamento: Modelo Airbnb local
"""
from datetime import datetime, date
from enum import Enum
from uuid import UUID
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, Numeric, Text, ForeignKey, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.sql import func
import uuid

from src.database import Base


class PropertyType(str, Enum):
    CASA = "casa"
    APARTAMENTO = "apartamento"
    QUARTO = "quarto"
    SUITE = "suite"
    VILLA = "villa"
    HOTEL = "hotel"
    HOSTEL = "hostel"


class PropertyStatus(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    PENDENTE = "pendente"


class BookingStatus(str, Enum):
    PENDENTE = "pendente"
    CONFIRMADA = "confirmada"
    EM_ANDAMENTO = "em_andamento"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"


class Property(Base):
    """Propriedade para alojamento"""
    __tablename__ = "alojamento_properties"
    
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
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(String(30), default=PropertyType.CASA)
    
    # Localização
    endereco: Mapped[str] = mapped_column(Text, nullable=False)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False)
    provincia: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(11, 8), nullable=True)
    
    # Capacidade
    quartos: Mapped[int] = mapped_column(Integer, default=1)
    camas: Mapped[int] = mapped_column(Integer, default=1)
    banheiros: Mapped[int] = mapped_column(Integer, default=1)
    max_hospedes: Mapped[int] = mapped_column(Integer, default=2)
    
    # Preços
    preco_noite: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    preco_limpeza: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    desconto_semanal: Mapped[int] = mapped_column(Integer, default=0)  # percentual
    desconto_mensal: Mapped[int] = mapped_column(Integer, default=0)  # percentual
    
    # Regras
    min_noites: Mapped[int] = mapped_column(Integer, default=1)
    max_noites: Mapped[int] = mapped_column(Integer, default=30)
    checkin_hora: Mapped[str] = mapped_column(String(5), default="15:00")
    checkout_hora: Mapped[str] = mapped_column(String(5), default="11:00")
    
    # Comodidades (JSON array)
    comodidades: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # Imagens (JSON array de URLs)
    imagens: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # Stats
    rating_medio: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=5.00)
    total_reservas: Mapped[int] = mapped_column(Integer, default=0)
    total_avaliacoes: Mapped[int] = mapped_column(Integer, default=0)
    
    status: Mapped[str] = mapped_column(String(20), default=PropertyStatus.PENDENTE)
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
    host = relationship("User", backref="properties_hosted")
    bookings = relationship("Booking", back_populates="property", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Property {self.titulo} ({self.preco_noite} Kz/noite)>"


class PropertyAvailability(Base):
    """Disponibilidade/Bloqueio de datas"""
    __tablename__ = "property_availability"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("alojamento_properties.id", ondelete="CASCADE"),
        nullable=False
    )
    
    data: Mapped[date] = mapped_column(Date, nullable=False)
    disponivel: Mapped[bool] = mapped_column(Boolean, default=True)
    preco_especial: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    motivo_bloqueio: Mapped[str | None] = mapped_column(String(100), nullable=True)


class Booking(Base):
    """Reserva de alojamento"""
    __tablename__ = "alojamento_bookings"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("alojamento_properties.id"),
        nullable=False
    )
    guest_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Datas
    data_checkin: Mapped[date] = mapped_column(Date, nullable=False)
    data_checkout: Mapped[date] = mapped_column(Date, nullable=False)
    noites: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Hóspedes
    adultos: Mapped[int] = mapped_column(Integer, default=1)
    criancas: Mapped[int] = mapped_column(Integer, default=0)
    
    # Valores
    preco_noite: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    taxa_limpeza: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    taxa_servico: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    desconto: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    # Contato
    telefone_contato: Mapped[str] = mapped_column(String(20), nullable=False)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Integração Tuendi
    tuendi_ida_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    tuendi_volta_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), default=BookingStatus.PENDENTE)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    confirmada_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    checkin_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    checkout_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelada_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    motivo_cancelamento: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    property = relationship("Property", back_populates="bookings")
    guest = relationship("User", backref="alojamento_bookings")
    
    def __repr__(self) -> str:
        return f"<Booking {self.id} ({self.status})>"


class PropertyReview(Base):
    """Avaliação de propriedade"""
    __tablename__ = "property_reviews"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("alojamento_properties.id", ondelete="CASCADE"),
        nullable=False
    )
    booking_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("alojamento_bookings.id"),
        nullable=False
    )
    guest_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Notas (1-5)
    nota_geral: Mapped[int] = mapped_column(Integer, nullable=False)
    nota_limpeza: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nota_localizacao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nota_comunicacao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nota_valor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    property = relationship("Property", backref="reviews")
    guest = relationship("User", backref="property_reviews")
