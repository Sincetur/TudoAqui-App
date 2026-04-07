"""
TUDOaqui API - Payment Schemas
"""
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from src.payments.models import PaymentMethod, PaymentStatus, OrigemTipo


# ============================================
# Payment Schemas
# ============================================

class PaymentCreate(BaseModel):
    """Schema para criar pagamento"""
    origem_tipo: OrigemTipo
    origem_id: UUID
    metodo: PaymentMethod
    valor: float = Field(..., gt=0)


class PaymentResponse(BaseModel):
    """Schema de resposta de pagamento"""
    id: UUID
    referencia: str
    origem_tipo: str
    origem_id: UUID
    user_id: UUID
    metodo: str
    valor: float
    taxa_servico: float
    valor_total: float
    status: PaymentStatus
    external_ref: str | None = None
    created_at: datetime
    confirmado_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class PaymentConfirm(BaseModel):
    """Schema para confirmar pagamento (webhook)"""
    referencia: str
    external_ref: str | None = None
    external_status: str | None = None


# ============================================
# Ledger Schemas
# ============================================

class LedgerEntryResponse(BaseModel):
    """Schema de entrada no ledger"""
    id: UUID
    payment_id: UUID | None = None
    origem_tipo: str
    origem_id: UUID
    beneficiario_id: UUID | None = None
    tipo: str
    valor: float
    descricao: str | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Wallet Schemas
# ============================================

class WalletResponse(BaseModel):
    """Schema de carteira"""
    id: UUID
    user_id: UUID
    saldo: float
    saldo_bloqueado: float
    saldo_disponivel: float
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm_with_available(cls, wallet):
        return cls(
            id=wallet.id,
            user_id=wallet.user_id,
            saldo=float(wallet.saldo),
            saldo_bloqueado=float(wallet.saldo_bloqueado),
            saldo_disponivel=float(wallet.saldo - wallet.saldo_bloqueado),
            created_at=wallet.created_at
        )


class WalletTopUp(BaseModel):
    """Schema para carregar carteira"""
    valor: float = Field(..., gt=0, le=1000000)
    metodo: PaymentMethod


# ============================================
# Stats Schemas
# ============================================

class PaymentStats(BaseModel):
    """Estatísticas de pagamentos"""
    total_recebido: float
    total_pago: float
    pendentes: int
    confirmados: int
