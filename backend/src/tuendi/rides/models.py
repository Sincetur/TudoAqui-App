"""
TUDOaqui API - Ride Models
"""
from datetime import datetime
from enum import Enum
from uuid import UUID
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, Numeric, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
import uuid

from src.database import Base


class RideStatus(str, Enum):
    SOLICITADA = "solicitada"
    ACEITE = "aceite"
    MOTORISTA_A_CAMINHO = "motorista_a_caminho"
    EM_CURSO = "em_curso"
    FINALIZADA = "finalizada"
    CANCELADA_CLIENTE = "cancelada_cliente"
    CANCELADA_MOTORISTA = "cancelada_motorista"


class Ride(Base):
    """Modelo de Corrida"""
    __tablename__ = "rides"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    cliente_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    motorista_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("drivers.id"),
        nullable=True
    )
    
    # Origem
    origem_endereco: Mapped[str] = mapped_column(Text, nullable=False)
    origem_latitude: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    origem_longitude: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    
    # Destino
    destino_endereco: Mapped[str] = mapped_column(Text, nullable=False)
    destino_latitude: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    destino_longitude: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    
    # Valores
    distancia_km: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    duracao_estimada_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    valor_estimado: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    valor_final: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20), 
        default=RideStatus.SOLICITADA
    )
    
    # Timestamps
    solicitada_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    aceite_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    iniciada_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finalizada_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelada_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    motivo_cancelamento: Mapped[str | None] = mapped_column(Text, nullable=True)
    
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
    cliente = relationship("User", foreign_keys=[cliente_id], backref="rides_as_client")
    motorista = relationship("Driver", backref="rides")
    
    def __repr__(self) -> str:
        return f"<Ride {self.id} ({self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Verifica se corrida está ativa"""
        return self.status in [
            RideStatus.SOLICITADA.value,
            RideStatus.ACEITE.value,
            RideStatus.MOTORISTA_A_CAMINHO.value,
            RideStatus.EM_CURSO.value
        ]
    
    @property
    def is_completed(self) -> bool:
        """Verifica se corrida foi finalizada"""
        return self.status == RideStatus.FINALIZADA.value
    
    @property
    def is_cancelled(self) -> bool:
        """Verifica se corrida foi cancelada"""
        return self.status in [
            RideStatus.CANCELADA_CLIENTE.value,
            RideStatus.CANCELADA_MOTORISTA.value
        ]


class RideTracking(Base):
    """Histórico de localização durante corrida"""
    __tablename__ = "ride_tracking"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    ride_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("rides.id", ondelete="CASCADE"),
        nullable=False
    )
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    velocidade: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    bearing: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )


class Rating(Base):
    """Avaliações de corridas"""
    __tablename__ = "ratings"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    ride_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("rides.id", ondelete="CASCADE"),
        nullable=False
    )
    avaliador_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    avaliado_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    nota: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
