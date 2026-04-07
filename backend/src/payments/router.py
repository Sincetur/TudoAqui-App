"""
TUDOaqui API - Payments Router
"""
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.models import User, UserRole
from src.auth.dependencies import get_current_user, require_roles
from src.payments.models import PaymentMethod, OrigemTipo
from src.payments.schemas import (
    PaymentCreate,
    PaymentResponse,
    PaymentConfirm,
    LedgerEntryResponse,
    WalletResponse,
    WalletTopUp
)
from src.payments.service import payment_service


router = APIRouter(prefix="/payments", tags=["Pagamentos"])


# ============================================
# Payment Endpoints
# ============================================

@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    request: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria um novo pagamento.
    """
    try:
        payment = await payment_service.create_payment(
            db,
            current_user.id,
            request.origem_tipo,
            request.origem_id,
            request.metodo,
            Decimal(str(request.valor))
        )
        return PaymentResponse.model_validate(payment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém detalhes de um pagamento.
    """
    payment = await payment_service.get_payment(db, payment_id)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    # Verifica permissão
    if payment.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return PaymentResponse.model_validate(payment)


@router.get("", response_model=list[PaymentResponse])
async def list_my_payments(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista pagamentos do utilizador autenticado.
    """
    payments = await payment_service.get_user_payments(db, current_user.id, limit, offset)
    return [PaymentResponse.model_validate(p) for p in payments]


# ============================================
# Webhook Endpoints (para providers externos)
# ============================================

@router.post("/webhook/multicaixa")
async def multicaixa_webhook(
    request: PaymentConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook para confirmação de pagamento Multicaixa.
    """
    payment = await payment_service.get_payment_by_ref(db, request.referencia)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    try:
        await payment_service.confirm_payment(
            db, 
            payment.id, 
            request.external_ref,
            request.external_status
        )
        return {"status": "confirmed"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook/mobilemoney")
async def mobilemoney_webhook(
    request: PaymentConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook para confirmação de pagamento Mobile Money.
    """
    payment = await payment_service.get_payment_by_ref(db, request.referencia)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    try:
        await payment_service.confirm_payment(
            db, 
            payment.id, 
            request.external_ref,
            request.external_status
        )
        return {"status": "confirmed"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Ledger Endpoints
# ============================================

@router.get("/ledger/me", response_model=list[LedgerEntryResponse])
async def get_my_ledger(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista entradas do ledger do utilizador (ganhos/gastos).
    """
    entries = await payment_service.get_user_ledger(db, current_user.id, limit, offset)
    return [LedgerEntryResponse.model_validate(e) for e in entries]


@router.get("/balance/me")
async def get_my_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém saldo do utilizador (total de ganhos - gastos).
    """
    return await payment_service.get_user_balance(db, current_user.id)


# ============================================
# Wallet Endpoints
# ============================================

@router.get("/wallet/me", response_model=WalletResponse)
async def get_my_wallet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém carteira do utilizador.
    """
    wallet = await payment_service.get_or_create_wallet(db, current_user.id)
    return WalletResponse.from_orm_with_available(wallet)


@router.post("/wallet/topup", response_model=WalletResponse)
async def topup_wallet(
    request: WalletTopUp,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Carrega a carteira (cria pagamento para adicionar saldo).
    
    Nota: Em produção, isto criaria um pagamento que após confirmação
    adicionaria o valor à carteira.
    """
    # TODO: Criar fluxo completo de carregamento
    # Por agora, simula carregamento direto
    try:
        wallet = await payment_service.add_to_wallet(
            db,
            current_user.id,
            Decimal(str(request.valor)),
            f"Carregamento via {request.metodo.value}"
        )
        return WalletResponse.from_orm_with_available(wallet)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Admin Endpoints
# ============================================

@router.post("/{payment_id}/confirm", response_model=PaymentResponse)
async def admin_confirm_payment(
    payment_id: UUID,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Confirma pagamento manualmente (admin).
    """
    try:
        payment = await payment_service.confirm_payment(db, payment_id)
        return PaymentResponse.model_validate(payment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/fail", response_model=PaymentResponse)
async def admin_fail_payment(
    payment_id: UUID,
    reason: str = None,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Marca pagamento como falhado (admin).
    """
    try:
        payment = await payment_service.fail_payment(db, payment_id, reason)
        return PaymentResponse.model_validate(payment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
