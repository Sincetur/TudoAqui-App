"""
TUDOaqui API - Partner Models
Sistema de parceiros com dados de pagamento
"""
from typing import Optional
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Text, ForeignKey, Boolean, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func

from src.database import Base


class Partner(Base):
    """Parceiro TUDOaqui - vendedores, anfitrioes, organizadores, agentes"""
    __tablename__ = "partners"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)

    # Tipo de parceiro
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default="proprietario")

    # Info do negocio
    nome_negocio: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provincia: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cidade: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Dados de pagamento - Unitel Money
    unitel_money_numero: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    unitel_money_titular: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # Dados de pagamento - Transferencia Bancaria
    banco_nome: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    banco_conta: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    banco_iban: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    banco_titular: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # Metodos aceites
    aceita_unitel_money: Mapped[bool] = mapped_column(Boolean, default=False)
    aceita_transferencia: Mapped[bool] = mapped_column(Boolean, default=False)
    aceita_dinheiro: Mapped[bool] = mapped_column(Boolean, default=True)

    # Aprovacao
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pendente")  # pendente, aprovado, suspenso, rejeitado
    admin_nota: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Taxa mensal
    plano: Mapped[str] = mapped_column(String(30), default="basico")  # basico, profissional, premium
    taxa_mensal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    proximo_pagamento: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    pagamento_em_dia: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="partner_profile")
