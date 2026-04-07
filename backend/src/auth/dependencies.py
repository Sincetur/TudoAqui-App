"""
TUDOaqui API - Auth Dependencies
"""
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.models import User, UserRole, UserStatus
from src.auth.service import auth_service


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Obtém utilizador atual a partir do token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = auth_service.decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception
    
    result = await db.execute(
        select(User).where(User.id == user_uuid)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if user.status != UserStatus.ATIVO.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada ou suspensa"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Garante que o utilizador está ativo"""
    if current_user.status != UserStatus.ATIVO.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta inativa"
        )
    return current_user


def require_roles(*roles: UserRole):
    """Dependency factory para verificar roles"""
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        user_role = UserRole(current_user.role)
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Requer: {[r.value for r in roles]}"
            )
        return current_user
    return role_checker


# Shortcuts para roles comuns
require_admin = require_roles(UserRole.ADMIN)
require_motorista = require_roles(UserRole.MOTORISTA, UserRole.ADMIN)
require_cliente = require_roles(UserRole.CLIENTE, UserRole.ADMIN)
