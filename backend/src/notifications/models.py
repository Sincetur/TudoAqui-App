"""
TUDOaqui API - Notification Models
"""
from datetime import datetime
from enum import Enum
from uuid import UUID
from sqlalchemy import String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.sql import func
import uuid

from src.database import Base


class NotificationType(str, Enum):
    RIDE_STATUS = "ride_status"
    PAYMENT = "payment"
    PROMO = "promo"
    SYSTEM = "system"
    RATING = "rating"


class Notification(Base):
    """Modelo de Notificação"""
    __tablename__ = "notifications"
    
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
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    dados: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    lida: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    def __repr__(self) -> str:
        return f"<Notification {self.tipo}: {self.titulo[:30]}>"
