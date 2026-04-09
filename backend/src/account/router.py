"""
TUDOaqui API - Account Router
Endpoints da conta do utilizador (perfil, pedidos de upgrade)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from src.database import get_db
from src.users.models import User, UserRole
from src.users.role_request import RoleRequest
from src.auth.dependencies import get_current_user


router = APIRouter(prefix="/account", tags=["Account"])

UPGRADABLE_ROLES = ["organizador", "vendedor", "anfitriao", "agente", "motorista", "entregador"]


class RoleRequestCreate(BaseModel):
    role_pretendido: str
    motivo: str


class ProfileUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Obter perfil do utilizador"""
    return {
        "id": str(current_user.id),
        "telefone": current_user.telefone,
        "nome": current_user.nome,
        "email": current_user.email,
        "role": current_user.role,
        "status": current_user.status,
        "avatar_url": current_user.avatar_url,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }


@router.put("/profile")
async def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Atualizar perfil do utilizador"""
    if data.nome is not None:
        current_user.nome = data.nome
    if data.email is not None:
        current_user.email = data.email
    await db.commit()
    return {"message": "Perfil atualizado"}


@router.post("/role-request")
async def create_role_request(
    data: RoleRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Solicitar upgrade de role"""
    if data.role_pretendido not in UPGRADABLE_ROLES:
        raise HTTPException(status_code=400, detail=f"Role invalido. Opcoes: {UPGRADABLE_ROLES}")

    if current_user.role == data.role_pretendido:
        raise HTTPException(status_code=400, detail="Ja tem este role")

    if current_user.role == "admin":
        raise HTTPException(status_code=400, detail="Admin nao precisa de upgrade")

    # Check for existing pending request
    existing = await db.execute(
        select(RoleRequest).where(
            RoleRequest.user_id == current_user.id,
            RoleRequest.status == "pendente"
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ja tem um pedido pendente")

    rr = RoleRequest(
        user_id=current_user.id,
        role_pretendido=data.role_pretendido,
        motivo=data.motivo,
    )
    db.add(rr)
    await db.commit()
    return {"message": "Pedido de upgrade enviado com sucesso", "status": "pendente"}


@router.get("/role-requests")
async def my_role_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar meus pedidos de upgrade"""
    result = await db.execute(
        select(RoleRequest)
        .where(RoleRequest.user_id == current_user.id)
        .order_by(RoleRequest.created_at.desc())
    )
    requests = result.scalars().all()
    return [
        {
            "id": str(rr.id),
            "role_pretendido": rr.role_pretendido,
            "motivo": rr.motivo,
            "status": rr.status,
            "admin_nota": rr.admin_nota,
            "created_at": rr.created_at.isoformat() if rr.created_at else None,
            "reviewed_at": rr.reviewed_at.isoformat() if rr.reviewed_at else None,
        }
        for rr in requests
    ]
