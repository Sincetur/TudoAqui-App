"""
TUDOaqui API - User Models
"""
from datetime import datetime
from enum import Enum
from uuid import UUID
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
import uuid

from src.database import Base


class UserRole(str, Enum):
    CLIENTE = "cliente"
    MOTORISTA = "motorista"
    MOTOQUEIRO = "motoqueiro"
    PROPRIETARIO = "proprietario"
    GUIA_TURISTA = "guia_turista"
    AGENTE_IMOBILIARIO = "agente_imobiliario"
    AGENTE_VIAGEM = "agente_viagem"
    STAFF = "staff"
    ADMIN = "admin"


class UserStatus(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    SUSPENSO = "suspenso"
    PENDENTE = "pendente"


class User(Base):
    """Modelo de Utilizador"""
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    telefone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nome: Mapped[str | None] = mapped_column(String(120), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default=UserRole.CLIENTE)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=UserStatus.ATIVO)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    def __repr__(self) -> str:
        return f"<User {self.telefone} ({self.role})>"


class OTPCode(Base):
    """Modelo de código OTP"""
    __tablename__ = "otp_codes"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    codigo: Mapped[str] = mapped_column(String(6), nullable=False)
    tentativas: Mapped[int] = mapped_column(default=0)
    verificado: Mapped[bool] = mapped_column(default=False)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )


class RefreshToken(Base):
    """Modelo de refresh token"""
    __tablename__ = "refresh_tokens"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    device_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revogado: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
