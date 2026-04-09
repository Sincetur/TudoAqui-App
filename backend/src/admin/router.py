"""
TUDOaqui API - Admin Router
Painel de administracao do SuperApp
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from src.database import get_db
from src.users.models import User, UserRole, UserStatus
from src.users.role_request import RoleRequest
from src.auth.dependencies import get_current_user, require_roles
from src.events.models import Event
from src.marketplace.models import Product, Seller
from src.alojamento.models import Property as AlojProperty
from src.turismo.models import Experience
from src.realestate.models import RealEstateProperty, RealEstateAgent
from src.tuendi.restaurante.models import Restaurant
from src.tuendi.entrega.models import Delivery


router = APIRouter(prefix="/admin", tags=["Admin"])

require_admin = require_roles(UserRole.ADMIN)


@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Estatisticas globais do SuperApp"""
    counts = {}
    for model, key in [
        (User, "users"), (Event, "events"), (Product, "products"),
        (AlojProperty, "alojamento"), (Experience, "turismo"),
        (RealEstateProperty, "imoveis"), (Restaurant, "restaurantes"),
    ]:
        result = await db.execute(select(func.count()).select_from(model))
        counts[key] = result.scalar()

    role_counts = {}
    for role in UserRole:
        result = await db.execute(
            select(func.count()).select_from(User).where(User.role == role.value)
        )
        role_counts[role.value] = result.scalar()

    return {
        "totais": counts,
        "roles": role_counts,
    }


@router.get("/users")
async def list_users(
    role: str = None,
    status_filter: str = None,
    search: str = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Listar todos os utilizadores"""
    query = select(User)
    if role:
        query = query.where(User.role == role)
    if status_filter:
        query = query.where(User.status == status_filter)
    if search:
        query = query.where(User.telefone.ilike(f"%{search}%") | User.nome.ilike(f"%{search}%"))
    query = query.order_by(User.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    users = result.scalars().all()
    return [
        {
            "id": str(u.id), "telefone": u.telefone, "nome": u.nome,
            "email": u.email, "role": u.role, "status": u.status,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    role: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Alterar role de um utilizador"""
    try:
        target_role = UserRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Role invalido: {role}")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Utilizador nao encontrado")

    user.role = target_role.value
    await db.commit()
    return {"message": f"Role atualizado para {role}", "user_id": str(user_id), "role": role}


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: UUID,
    user_status: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Alterar status de um utilizador"""
    try:
        target_status = UserStatus(user_status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Status invalido: {user_status}")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Utilizador nao encontrado")

    user.status = target_status.value
    await db.commit()
    return {"message": f"Status atualizado para {user_status}", "user_id": str(user_id), "status": user_status}


@router.get("/events")
async def list_all_events(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Listar todos os eventos (admin)"""
    result = await db.execute(
        select(Event).order_by(Event.created_at.desc()).limit(limit).offset(offset)
    )
    events = result.scalars().all()
    return [
        {
            "id": str(e.id), "titulo": e.titulo, "local": e.local,
            "data_evento": str(e.data_evento), "categoria": e.categoria,
            "status": e.status, "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]


@router.get("/restaurants")
async def list_all_restaurants(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Listar todos os restaurantes (admin)"""
    result = await db.execute(
        select(Restaurant).order_by(Restaurant.created_at.desc()).limit(limit)
    )
    restaurants = result.scalars().all()
    return [
        {
            "id": str(r.id), "nome": r.nome, "cidade": r.cidade,
            "status": r.status, "aberto": r.aberto,
            "rating_medio": float(r.rating_medio) if r.rating_medio else 0,
            "total_pedidos": r.total_pedidos,
        }
        for r in restaurants
    ]


@router.get("/sellers")
async def list_all_sellers(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Listar todos os vendedores (admin)"""
    result = await db.execute(
        select(Seller).order_by(Seller.created_at.desc()).limit(limit)
    )
    sellers = result.scalars().all()
    return [
        {
            "id": str(s.id), "nome_loja": s.nome_loja, "cidade": s.cidade,
            "status": s.status, "rating_medio": float(s.rating_medio) if s.rating_medio else 0,
            "total_vendas": s.total_vendas,
        }
        for s in sellers
    ]


@router.get("/agents")
async def list_all_agents(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Listar todos os agentes imobiliarios (admin)"""
    result = await db.execute(
        select(RealEstateAgent).order_by(RealEstateAgent.created_at.desc()).limit(limit)
    )
    agents = result.scalars().all()
    return [
        {
            "id": str(a.id), "nome_profissional": a.nome_profissional,
            "status": a.status, "plano": a.plano,
            "rating_medio": float(a.rating_medio) if a.rating_medio else 0,
            "total_vendas": a.total_vendas, "total_arrendamentos": a.total_arrendamentos,
        }
        for a in agents
    ]


# === ROLE REQUESTS ===

@router.get("/role-requests")
async def list_role_requests(
    status_filter: str = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Listar pedidos de upgrade de role"""
    query = select(RoleRequest).order_by(RoleRequest.created_at.desc()).limit(limit)
    if status_filter:
        query = query.where(RoleRequest.status == status_filter)
    result = await db.execute(query)
    requests = result.scalars().all()

    items = []
    for rr in requests:
        user_result = await db.execute(select(User).where(User.id == rr.user_id))
        user = user_result.scalar_one_or_none()
        items.append({
            "id": str(rr.id),
            "user_id": str(rr.user_id),
            "user_nome": user.nome if user else None,
            "user_telefone": user.telefone if user else None,
            "user_role_atual": user.role if user else None,
            "role_pretendido": rr.role_pretendido,
            "motivo": rr.motivo,
            "status": rr.status,
            "admin_nota": rr.admin_nota,
            "created_at": rr.created_at.isoformat() if rr.created_at else None,
            "reviewed_at": rr.reviewed_at.isoformat() if rr.reviewed_at else None,
        })
    return items


@router.put("/role-requests/{request_id}/approve")
async def approve_role_request(
    request_id: UUID,
    nota: str = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Aprovar pedido de upgrade de role"""
    result = await db.execute(select(RoleRequest).where(RoleRequest.id == request_id))
    rr = result.scalar_one_or_none()
    if not rr:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    if rr.status != "pendente":
        raise HTTPException(status_code=400, detail="Pedido ja foi processado")

    # Update request
    from datetime import datetime, timezone
    rr.status = "aprovado"
    rr.admin_nota = nota
    rr.reviewed_by = current_user.id
    rr.reviewed_at = datetime.now(timezone.utc)

    # Update user role
    user_result = await db.execute(select(User).where(User.id == rr.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.role = rr.role_pretendido

    await db.commit()
    return {"message": f"Pedido aprovado. Role atualizado para {rr.role_pretendido}", "status": "aprovado"}


@router.put("/role-requests/{request_id}/reject")
async def reject_role_request(
    request_id: UUID,
    nota: str = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Rejeitar pedido de upgrade de role"""
    result = await db.execute(select(RoleRequest).where(RoleRequest.id == request_id))
    rr = result.scalar_one_or_none()
    if not rr:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    if rr.status != "pendente":
        raise HTTPException(status_code=400, detail="Pedido ja foi processado")

    from datetime import datetime, timezone
    rr.status = "rejeitado"
    rr.admin_nota = nota
    rr.reviewed_by = current_user.id
    rr.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Pedido rejeitado", "status": "rejeitado"}
