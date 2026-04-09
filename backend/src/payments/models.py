"""
TUDOaqui API - Payment Models
"""
from datetime import datetime
from enum import Enum
from uuid import UUID
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.sql import func
import uuid

from src.database import Base


class PaymentMethod(str, Enum):
    MULTICAIXA = "multicaixa"
    MOBILEMONEY = "mobilemoney"
    WALLET = "wallet"
    DINHEIRO = "dinheiro"
    TRANSFERENCIA = "transferencia"


class PaymentStatus(str, Enum):
    INICIADO = "iniciado"
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    CONFIRMADO = "confirmado"
    FALHADO = "falhado"
    REEMBOLSADO = "reembolsado"


class OrigemTipo(str, Enum):
    RIDE = "ride"
    TICKET = "ticket"
    MARKETPLACE = "marketplace"
    BOOKING = "booking"
    EXPERIENCE = "experience"
    ENTREGA = "entrega"
    RESTAURANTE = "restaurante"
    ALOJAMENTO = "alojamento"
    TURISMO = "turismo"
    REALESTATE = "realestate"


class Payment(Base):
    """Modelo de Pagamento"""
    __tablename__ = "payments"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    referencia: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    origem_tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    origem_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=False
    )
    
    metodo: Mapped[str] = mapped_column(String(30), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    taxa_servico: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    status: Mapped[str] = mapped_column(String(20), default=PaymentStatus.INICIADO)
    
    # Dados externos
    external_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    external_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Comprovativo (para transferencias)
    comprovativo_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    admin_nota: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    confirmado_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    def __repr__(self) -> str:
        return f"<Payment {self.referencia} ({self.status})>"


class LedgerEntry(Base):
    """Entrada no Livro Razão"""
    __tablename__ = "ledger_entries"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    payment_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("payments.id"),
        nullable=True
    )
    origem_tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    origem_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    beneficiario_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=True  # NULL = plataforma
    )
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)  # credito | debito
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )


class Wallet(Base):
    """Carteira do Utilizador"""
    __tablename__ = "wallets"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    saldo: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    saldo_bloqueado: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
