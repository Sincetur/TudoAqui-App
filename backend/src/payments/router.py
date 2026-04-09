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
    PaymentSubmitComprovativo,
    AdminPaymentAction,
    BankInfoResponse,
    LedgerEntryResponse,
    WalletResponse,
    WalletTopUp
)
from src.payments.service import payment_service


router = APIRouter(prefix="/payments", tags=["Pagamentos"])

# ============================================
# Dados Bancarios
# ============================================

BANK_INFO = {
    "banco": "BAI - Banco Angolano de Investimentos",
    "conta": "20967898310001",
    "iban": "AO06 0040 0000 0967898310151",
    "swift": "BAIPAOLU",
    "titular": "TUDOaqui, Lda",
    "instrucoes": "Apos efectuar a transferencia, registe o comprovativo no seu pedido. O pagamento sera confirmado em ate 24h."
}


@router.get("/bank-info", response_model=BankInfoResponse)
async def get_bank_info(
    current_user: User = Depends(get_current_user),
):
    """Retorna dados bancarios para transferencia."""
    return BANK_INFO


@router.get("/methods")
async def get_payment_methods(
    current_user: User = Depends(get_current_user),
):
    """Retorna metodos de pagamento disponiveis."""
    return {
        "metodos": [
            {
                "id": "transferencia",
                "nome": "Transferencia Bancaria",
                "descricao": "Transferencia via BAI. Confirmacao em ate 24h.",
                "ativo": True,
                "icon": "building-2",
            },
            {
                "id": "dinheiro",
                "nome": "Dinheiro (Cash)",
                "descricao": "Pagamento em dinheiro na entrega ou no local.",
                "ativo": True,
                "icon": "banknote",
            },
            {
                "id": "multicaixa",
                "nome": "Multicaixa Express",
                "descricao": "Pagamento via Multicaixa Express (em breve).",
                "ativo": False,
                "icon": "credit-card",
            },
        ]
    }


# ============================================
# Payment Endpoints
# ============================================

@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    request: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cria um novo pagamento."""
    try:
        payment = await payment_service.create_payment(
            db,
            current_user.id,
            request.origem_tipo,
            request.origem_id,
            request.metodo,
            Decimal(str(request.valor)),
            comprovativo_ref=request.comprovativo_ref,
            notas=request.notas,
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
    """Obtem detalhes de um pagamento."""
    payment = await payment_service.get_payment(db, payment_id)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento nao encontrado")
    
    # Verifica permissao
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
    """Lista pagamentos do utilizador autenticado."""
    payments = await payment_service.get_user_payments(db, current_user.id, limit, offset)
    return [PaymentResponse.model_validate(p) for p in payments]


@router.put("/{payment_id}/comprovativo", response_model=PaymentResponse)
async def submit_comprovativo(
    payment_id: UUID,
    request: PaymentSubmitComprovativo,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submete comprovativo de transferencia bancaria."""
    try:
        payment = await payment_service.submit_comprovativo(
            db, payment_id, current_user.id,
            request.comprovativo_ref, request.notas
        )
        return PaymentResponse.model_validate(payment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Webhook Endpoints (para providers externos)
# ============================================

@router.post("/webhook/multicaixa")
async def multicaixa_webhook(
    request: PaymentConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Webhook para confirmacao de pagamento Multicaixa."""
    payment = await payment_service.get_payment_by_ref(db, request.referencia)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento nao encontrado")
    
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
    """Lista entradas do ledger do utilizador."""
    entries = await payment_service.get_user_ledger(db, current_user.id, limit, offset)
    return [LedgerEntryResponse.model_validate(e) for e in entries]


@router.get("/balance/me")
async def get_my_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtem saldo do utilizador."""
    return await payment_service.get_user_balance(db, current_user.id)


# ============================================
# Wallet Endpoints
# ============================================

@router.get("/wallet/me", response_model=WalletResponse)
async def get_my_wallet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtem carteira do utilizador."""
    wallet = await payment_service.get_or_create_wallet(db, current_user.id)
    return WalletResponse.from_orm_with_available(wallet)


@router.post("/wallet/topup", response_model=WalletResponse)
async def topup_wallet(
    request: WalletTopUp,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Carrega a carteira."""
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

@router.get("/admin/all", response_model=list[PaymentResponse])
async def admin_list_all_payments(
    status_filter: str = None,
    metodo: str = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Lista todos os pagamentos (admin)."""
    payments = await payment_service.get_all_payments(
        db, status_filter, metodo, limit, offset
    )
    return [PaymentResponse.model_validate(p) for p in payments]


@router.get("/admin/stats")
async def admin_payment_stats(
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Estatisticas de pagamentos (admin)."""
    return await payment_service.get_payment_stats(db)


@router.put("/{payment_id}/confirm", response_model=PaymentResponse)
async def admin_confirm_payment(
    payment_id: UUID,
    body: AdminPaymentAction = None,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Confirma pagamento manualmente (admin)."""
    try:
        payment = await payment_service.confirm_payment(db, payment_id)
        if body and body.nota:
            payment.admin_nota = body.nota
            await db.commit()
            await db.refresh(payment)
        return PaymentResponse.model_validate(payment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{payment_id}/reject", response_model=PaymentResponse)
async def admin_reject_payment(
    payment_id: UUID,
    body: AdminPaymentAction = None,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Rejeita pagamento (admin)."""
    try:
        reason = body.nota if body else None
        payment = await payment_service.fail_payment(db, payment_id, reason)
        if body and body.nota:
            payment.admin_nota = body.nota
            await db.commit()
            await db.refresh(payment)
        return PaymentResponse.model_validate(payment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
