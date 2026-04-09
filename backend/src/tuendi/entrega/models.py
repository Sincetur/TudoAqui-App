"""
TUDOaqui API - Tuendi Entrega Models
Módulo de Entregas de Pacotes
"""
from datetime import datetime
from enum import Enum
from uuid import UUID
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, Numeric, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.sql import func
import uuid

from src.database import Base


class DeliveryType(str, Enum):
    DOCUMENTO = "documento"
    PACOTE_PEQUENO = "pacote_pequeno"
    PACOTE_MEDIO = "pacote_medio"
    PACOTE_GRANDE = "pacote_grande"
    FRAGIL = "fragil"


class DeliveryStatus(str, Enum):
    PENDENTE = "pendente"
    ACEITE = "aceite"
    RECOLHA = "recolha"  # A caminho para recolher
    RECOLHIDO = "recolhido"
    EM_TRANSITO = "em_transito"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"
    FALHOU = "falhou"


class DeliveryPriority(str, Enum):
    NORMAL = "normal"
    EXPRESS = "express"
    URGENTE = "urgente"


class Delivery(Base):
    """Entrega de pacote"""
    __tablename__ = "deliveries"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    sender_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    driver_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("drivers.id"),
        nullable=True
    )
    
    # Tipo e prioridade
    tipo: Mapped[str] = mapped_column(String(30), default=DeliveryType.PACOTE_PEQUENO)
    prioridade: Mapped[str] = mapped_column(String(20), default=DeliveryPriority.NORMAL)
    
    # Descrição do pacote
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    peso_estimado: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)  # kg
    
    # Origem (recolha)
    origem_endereco: Mapped[str] = mapped_column(Text, nullable=False)
    origem_latitude: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    origem_longitude: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    origem_referencia: Mapped[str | None] = mapped_column(Text, nullable=True)
    origem_contato_nome: Mapped[str] = mapped_column(String(120), nullable=False)
    origem_contato_telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Destino (entrega)
    destino_endereco: Mapped[str] = mapped_column(Text, nullable=False)
    destino_latitude: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    destino_longitude: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    destino_referencia: Mapped[str | None] = mapped_column(Text, nullable=True)
    destino_contato_nome: Mapped[str] = mapped_column(String(120), nullable=False)
    destino_contato_telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Distância e valores
    distancia_km: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    preco_base: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    taxa_prioridade: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    taxa_peso: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    # Notas
    instrucoes_recolha: Mapped[str | None] = mapped_column(Text, nullable=True)
    instrucoes_entrega: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Código de confirmação
    codigo_recolha: Mapped[str | None] = mapped_column(String(6), nullable=True)
    codigo_entrega: Mapped[str | None] = mapped_column(String(6), nullable=True)
    
    # Foto de confirmação
    foto_recolha_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    foto_entrega_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Integração (marketplace, etc)
    marketplace_order_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), default=DeliveryStatus.PENDENTE)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    aceite_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recolhido_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    entregue_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelado_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    motivo_cancelamento: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    sender = relationship("User", backref="deliveries_sent", foreign_keys=[sender_id])
    driver = relationship("Driver", backref="deliveries")
    tracking = relationship("DeliveryTracking", back_populates="delivery", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Delivery {self.id} ({self.status})>"


class DeliveryTracking(Base):
    """Histórico de tracking da entrega"""
    __tablename__ = "delivery_tracking"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    delivery_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("deliveries.id", ondelete="CASCADE"),
        nullable=False
    )
    
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(11, 8), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    delivery = relationship("Delivery", back_populates="tracking")
