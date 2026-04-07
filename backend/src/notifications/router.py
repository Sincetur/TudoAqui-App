"""
TUDOaqui API - Notifications Router
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from src.database import get_db
from src.users.models import User
from src.auth.dependencies import get_current_user
from src.notifications.service import notification_service
from src.notifications.models import NotificationType


router = APIRouter(prefix="/notifications", tags=["Notificações"])


# Schemas
class NotificationResponse(BaseModel):
    id: UUID
    titulo: str
    mensagem: str
    tipo: str
    dados: dict | None = None
    lida: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UnreadCountResponse(BaseModel):
    count: int


class MarkReadResponse(BaseModel):
    success: bool
    count: int = 0


# Endpoints
@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista notificações do utilizador.
    
    - **unread_only**: Se true, retorna apenas não lidas
    """
    notifications = await notification_service.get_user_notifications(
        db, current_user.id, unread_only, limit, offset
    )
    return [NotificationResponse.model_validate(n) for n in notifications]


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna contagem de notificações não lidas.
    """
    count = await notification_service.get_unread_count(db, current_user.id)
    return UnreadCountResponse(count=count)


@router.post("/{notification_id}/read", response_model=MarkReadResponse)
async def mark_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Marca uma notificação como lida.
    """
    success = await notification_service.mark_as_read(db, notification_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    
    return MarkReadResponse(success=True, count=1)


@router.post("/read-all", response_model=MarkReadResponse)
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Marca todas as notificações como lidas.
    """
    count = await notification_service.mark_all_as_read(db, current_user.id)
    return MarkReadResponse(success=True, count=count)
