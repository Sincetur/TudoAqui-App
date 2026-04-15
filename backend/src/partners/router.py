"""
TUDOaqui API - Partner Router
Endpoints para parceiros: registo, config pagamento, admin gestao
"""
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sqlfunc
from pydantic import BaseModel

from src.database import get_db
from src.users.models import User, UserRole
from src.auth.dependencies import get_current_user, require_roles
from src.partners import Partner


router = APIRouter(prefix="/partners", tags=["Parceiros"])

PARTNER_ROLES = ["motorista", "motoqueiro", "proprietario", "guia_turista", "agente_imobiliario", "agente_viagem", "staff"]


# ============================================
# Schemas
# ============================================

PARTNER_TIPOS = [
    {"id": "motorista", "label": "Motorista", "desc": "Condutor de taxi ou transporte privado"},
    {"id": "motoqueiro", "label": "Motoqueiro", "desc": "Entregas rapidas de moto ou kupapata"},
    {"id": "proprietario", "label": "Proprietario", "desc": "Dono de alojamento, restaurante ou loja"},
    {"id": "staff", "label": "Staff", "desc": "Funcionario de eventos ou servicos"},
    {"id": "guia_turista", "label": "Guia Turista", "desc": "Guia de experiencias e tours turisticos"},
    {"id": "agente_imobiliario", "label": "Agente Imobiliario", "desc": "Venda e arrendamento de imoveis"},
    {"id": "agente_viagem", "label": "Agente de Viagem", "desc": "Pacotes turisticos e viagens"},
]

PARTNER_TIPO_IDS = [t["id"] for t in PARTNER_TIPOS]


class PartnerRegister(BaseModel):
    tipo: str
    nome_negocio: str
    descricao: Optional[str] = None
    provincia: Optional[str] = None
    cidade: Optional[str] = None
    aceita_dinheiro: bool = True


class PartnerPaymentConfig(BaseModel):
    # Unitel Money
    unitel_money_numero: Optional[str] = None
    unitel_money_titular: Optional[str] = None
    aceita_unitel_money: bool = False
    # Transferencia
    banco_nome: Optional[str] = None
    banco_conta: Optional[str] = None
    banco_iban: Optional[str] = None
    banco_titular: Optional[str] = None
    aceita_transferencia: bool = False
    # Cash
    aceita_dinheiro: bool = True


class PartnerUpdate(BaseModel):
    nome_negocio: Optional[str] = None
    descricao: Optional[str] = None
    provincia: Optional[str] = None
    cidade: Optional[str] = None


class AdminPartnerAction(BaseModel):
    nota: Optional[str] = None


def partner_to_dict(p: Partner, include_payment=False) -> dict:
    """Serializa parceiro para dict"""
    d = {
        "id": str(p.id),
        "user_id": str(p.user_id),
        "tipo": p.tipo,
        "nome_negocio": p.nome_negocio,
        "descricao": p.descricao,
        "provincia": p.provincia,
        "cidade": p.cidade,
        "aceita_unitel_money": p.aceita_unitel_money,
        "aceita_transferencia": p.aceita_transferencia,
        "aceita_dinheiro": p.aceita_dinheiro,
        "status": p.status,
        "plano": p.plano,
        "pagamento_em_dia": p.pagamento_em_dia,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }
    if include_payment:
        d.update({
            "unitel_money_numero": p.unitel_money_numero,
            "unitel_money_titular": p.unitel_money_titular,
            "banco_nome": p.banco_nome,
            "banco_conta": p.banco_conta,
            "banco_iban": p.banco_iban,
            "banco_titular": p.banco_titular,
            "admin_nota": p.admin_nota,
            "taxa_mensal": float(p.taxa_mensal) if p.taxa_mensal else 0,
        })
    return d


def partner_payment_info(p: Partner) -> dict:
    """Retorna dados de pagamento publicos do parceiro (para o cliente)"""
    methods = []
    if p.aceita_unitel_money and p.unitel_money_numero:
        methods.append({
            "id": "unitelmoney",
            "nome": "Unitel Money",
            "icon": "smartphone",
            "dados": {
                "numero": p.unitel_money_numero,
                "titular": p.unitel_money_titular or p.nome_negocio,
            }
        })
    if p.aceita_transferencia and p.banco_iban:
        methods.append({
            "id": "transferencia",
            "nome": "Transferencia Bancaria",
            "icon": "building-2",
            "dados": {
                "banco": p.banco_nome,
                "conta": p.banco_conta,
                "iban": p.banco_iban,
                "titular": p.banco_titular or p.nome_negocio,
            }
        })
    if p.aceita_dinheiro:
        methods.append({
            "id": "dinheiro",
            "nome": "Dinheiro (Cash)",
            "icon": "banknote",
            "dados": {}
        })
    return {
        "parceiro": p.nome_negocio,
        "metodos": methods,
    }


# ============================================
# Partner Registration & Profile
# ============================================

@router.get("/tipos")
async def get_partner_tipos():
    """Lista os tipos de parceiro disponiveis."""
    return {"tipos": PARTNER_TIPOS}


@router.post("/register")
async def register_partner(
    data: PartnerRegister,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Registar como parceiro. Requer role de vendedor/anfitriao/organizador/agente."""
    if current_user.role not in PARTNER_ROLES:
        raise HTTPException(status_code=403, detail=f"Precisa ter um role de parceiro ({', '.join(PARTNER_ROLES)}). Solicite upgrade na sua conta.")

    if data.tipo not in PARTNER_TIPO_IDS:
        raise HTTPException(status_code=400, detail=f"Tipo de parceiro invalido. Opcoes: {PARTNER_TIPO_IDS}")

    existing = await db.execute(select(Partner).where(Partner.user_id == current_user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ja e parceiro registado")

    partner = Partner(
        user_id=current_user.id,
        tipo=data.tipo,
        nome_negocio=data.nome_negocio,
        descricao=data.descricao,
        provincia=data.provincia,
        cidade=data.cidade,
        aceita_dinheiro=data.aceita_dinheiro,
    )
    db.add(partner)
    await db.commit()
    await db.refresh(partner)
    return {"message": "Registo de parceiro enviado. Aguarde aprovacao do admin.", "partner": partner_to_dict(partner, True)}


@router.get("/me")
async def get_my_partner(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obter perfil de parceiro do utilizador."""
    result = await db.execute(select(Partner).where(Partner.user_id == current_user.id))
    partner = result.scalar_one_or_none()
    if not partner:
        return None
    return partner_to_dict(partner, include_payment=True)


@router.put("/me")
async def update_my_partner(
    data: PartnerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar info do negocio."""
    result = await db.execute(select(Partner).where(Partner.user_id == current_user.id))
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Nao e parceiro registado")

    if data.nome_negocio is not None:
        partner.nome_negocio = data.nome_negocio
    if data.descricao is not None:
        partner.descricao = data.descricao
    if data.provincia is not None:
        partner.provincia = data.provincia
    if data.cidade is not None:
        partner.cidade = data.cidade

    await db.commit()
    return {"message": "Dados actualizados", "partner": partner_to_dict(partner, True)}


@router.put("/me/payment")
async def update_payment_config(
    data: PartnerPaymentConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Configurar dados de pagamento do parceiro."""
    result = await db.execute(select(Partner).where(Partner.user_id == current_user.id))
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Nao e parceiro registado")

    # Validacoes
    if data.aceita_unitel_money and not data.unitel_money_numero:
        raise HTTPException(status_code=400, detail="Numero Unitel Money obrigatorio")
    if data.aceita_transferencia and not data.banco_iban:
        raise HTTPException(status_code=400, detail="IBAN obrigatorio para transferencia")

    partner.unitel_money_numero = data.unitel_money_numero
    partner.unitel_money_titular = data.unitel_money_titular
    partner.aceita_unitel_money = data.aceita_unitel_money
    partner.banco_nome = data.banco_nome
    partner.banco_conta = data.banco_conta
    partner.banco_iban = data.banco_iban
    partner.banco_titular = data.banco_titular
    partner.aceita_transferencia = data.aceita_transferencia
    partner.aceita_dinheiro = data.aceita_dinheiro

    await db.commit()
    return {"message": "Dados de pagamento actualizados", "partner": partner_to_dict(partner, True)}


# ============================================
# Public: Get partner payment info (for checkout)
# ============================================

@router.get("/{partner_id}/payment-info")
async def get_partner_payment_info(
    partner_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obter dados de pagamento do parceiro (para checkout). So parceiros aprovados."""
    result = await db.execute(select(Partner).where(Partner.id == partner_id))
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Parceiro nao encontrado")
    if partner.status != "aprovado":
        raise HTTPException(status_code=403, detail="Parceiro nao aprovado para operar")
    return partner_payment_info(partner)


@router.get("/by-user/{user_id}/payment-info")
async def get_partner_payment_info_by_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obter dados de pagamento do parceiro pelo user_id (para checkout)."""
    result = await db.execute(select(Partner).where(Partner.user_id == user_id))
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Parceiro nao encontrado")
    if partner.status != "aprovado":
        raise HTTPException(status_code=403, detail="Parceiro nao aprovado para operar")
    return partner_payment_info(partner)


# ============================================
# Admin: Gerir Parceiros
# ============================================

@router.get("/admin/all")
async def admin_list_partners(
    status_filter: str = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Listar todos os parceiros (admin)."""
    query = select(Partner).order_by(Partner.created_at.desc())
    if status_filter:
        query = query.where(Partner.status == status_filter)
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    partners = result.scalars().all()
    return [partner_to_dict(p, include_payment=True) for p in partners]


@router.get("/admin/stats")
async def admin_partner_stats(
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Estatisticas de parceiros."""
    total = (await db.execute(select(sqlfunc.count()).select_from(Partner))).scalar() or 0
    pendentes = (await db.execute(select(sqlfunc.count()).select_from(Partner).where(Partner.status == "pendente"))).scalar() or 0
    aprovados = (await db.execute(select(sqlfunc.count()).select_from(Partner).where(Partner.status == "aprovado"))).scalar() or 0
    suspensos = (await db.execute(select(sqlfunc.count()).select_from(Partner).where(Partner.status == "suspenso"))).scalar() or 0
    return {"total": total, "pendentes": pendentes, "aprovados": aprovados, "suspensos": suspensos}


@router.put("/admin/{partner_id}/approve")
async def admin_approve_partner(
    partner_id: UUID,
    body: AdminPartnerAction = None,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Aprovar parceiro (admin)."""
    result = await db.execute(select(Partner).where(Partner.id == partner_id))
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Parceiro nao encontrado")

    partner.status = "aprovado"
    partner.approved_by = current_user.id
    partner.approved_at = datetime.now(timezone.utc)
    if body and body.nota:
        partner.admin_nota = body.nota
    await db.commit()
    return {"message": "Parceiro aprovado", "partner": partner_to_dict(partner, True)}


@router.put("/admin/{partner_id}/suspend")
async def admin_suspend_partner(
    partner_id: UUID,
    body: AdminPartnerAction = None,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Suspender parceiro (admin)."""
    result = await db.execute(select(Partner).where(Partner.id == partner_id))
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Parceiro nao encontrado")

    partner.status = "suspenso"
    if body and body.nota:
        partner.admin_nota = body.nota
    await db.commit()
    return {"message": "Parceiro suspenso", "partner": partner_to_dict(partner, True)}


@router.put("/admin/{partner_id}/reject")
async def admin_reject_partner(
    partner_id: UUID,
    body: AdminPartnerAction = None,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Rejeitar parceiro (admin)."""
    result = await db.execute(select(Partner).where(Partner.id == partner_id))
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Parceiro nao encontrado")

    partner.status = "rejeitado"
    if body and body.nota:
        partner.admin_nota = body.nota
    await db.commit()
    return {"message": "Parceiro rejeitado", "partner": partner_to_dict(partner, True)}
