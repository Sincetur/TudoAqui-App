"""
TUDOaqui API - Driver Models
"""
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import UUID
from decimal import Decimal
from sqlalchemy import String, DateTime, Boolean, Integer, Numeric, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
import uuid

from src.database import Base


class DriverStatus(str, Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"
    SUSPENSO = "suspenso"


class Driver(Base):
    """Modelo de Motorista"""
    __tablename__ = "drivers"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Dados do veículo
    veiculo: Mapped[str] = mapped_column(String(100), nullable=False)
    matricula: Mapped[str] = mapped_column(String(30), nullable=False)
    cor_veiculo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    marca: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    modelo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ano: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Documentos
    carta_conducao: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    documento_veiculo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Status online
    online: Mapped[bool] = mapped_column(Boolean, default=False)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8), nullable=True)
    ultima_localizacao_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    # Estatísticas
    rating_medio: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=5.00)
    total_corridas: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20), 
        default=DriverStatus.PENDENTE
    )
    
    # Timestamps
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
    user = relationship("User", backref="driver_profile", lazy="joined")
    
    def __repr__(self) -> str:
        return f"<Driver {self.matricula} ({self.status})>"
    
    @property
    def is_available(self) -> bool:
        """Verifica se motorista está disponível"""
        return (
            self.online and 
            self.status == DriverStatus.APROVADO.value and
            self.latitude is not None and
            self.longitude is not None
        )
