"""
TUDOaqui API - Notifications Service
"""
from uuid import UUID
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.notifications.models import Notification, NotificationType
from src.common.websocket import ws_manager


class NotificationService:
    """Serviço de notificações"""
    
    async def create(
        self,
        db: AsyncSession,
        user_id: UUID,
        titulo: str,
        mensagem: str,
        tipo: NotificationType,
        dados: dict = None,
        send_push: bool = True
    ) -> Notification:
        """Cria nova notificação"""
        notification = Notification(
            user_id=user_id,
            titulo=titulo,
            mensagem=mensagem,
            tipo=tipo.value,
            dados=dados
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        
        # Envia via WebSocket se utilizador estiver online
        if send_push and ws_manager.is_user_online(user_id):
            await ws_manager.send_personal(user_id, {
                "type": "notification",
                "notification": {
                    "id": str(notification.id),
                    "titulo": titulo,
                    "mensagem": mensagem,
                    "tipo": tipo.value,
                    "dados": dados
                }
            })
        
        # TODO: Enviar push notification via Firebase se offline
        
        return notification
    
    async def get_user_notifications(
        self,
        db: AsyncSession,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> list[Notification]:
        """Lista notificações do utilizador"""
        query = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            query = query.where(Notification.lida == False)
        
        query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def mark_as_read(self, db: AsyncSession, notification_id: UUID, user_id: UUID) -> bool:
        """Marca notificação como lida"""
        result = await db.execute(
            update(Notification)
            .where(and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ))
            .values(lida=True)
        )
        await db.commit()
        return result.rowcount > 0
    
    async def mark_all_as_read(self, db: AsyncSession, user_id: UUID) -> int:
        """Marca todas as notificações como lidas"""
        result = await db.execute(
            update(Notification)
            .where(and_(
                Notification.user_id == user_id,
                Notification.lida == False
            ))
            .values(lida=True)
        )
        await db.commit()
        return result.rowcount
    
    async def get_unread_count(self, db: AsyncSession, user_id: UUID) -> int:
        """Conta notificações não lidas"""
        from sqlalchemy import func
        
        result = await db.execute(
            select(func.count(Notification.id))
            .where(and_(
                Notification.user_id == user_id,
                Notification.lida == False
            ))
        )
        return result.scalar() or 0
    
    # ============================================
    # Notificações específicas do Tuendi
    # ============================================
    
    async def notify_ride_accepted(
        self,
        db: AsyncSession,
        client_id: UUID,
        driver_name: str,
        ride_id: UUID
    ):
        """Notifica cliente que corrida foi aceite"""
        await self.create(
            db,
            client_id,
            "Motorista a caminho! 🚗",
            f"{driver_name} aceitou a sua corrida e está a caminho.",
            NotificationType.RIDE_STATUS,
            {"ride_id": str(ride_id)}
        )
    
    async def notify_ride_arrived(
        self,
        db: AsyncSession,
        client_id: UUID,
        driver_name: str,
        ride_id: UUID
    ):
        """Notifica cliente que motorista chegou"""
        await self.create(
            db,
            client_id,
            "O motorista chegou! 📍",
            f"{driver_name} está à sua espera.",
            NotificationType.RIDE_STATUS,
            {"ride_id": str(ride_id)}
        )
    
    async def notify_ride_completed(
        self,
        db: AsyncSession,
        user_id: UUID,
        valor: float,
        ride_id: UUID
    ):
        """Notifica que corrida foi finalizada"""
        await self.create(
            db,
            user_id,
            "Corrida finalizada! ✅",
            f"Obrigado por viajar connosco. Valor: {valor:.2f} Kz",
            NotificationType.RIDE_STATUS,
            {"ride_id": str(ride_id), "valor": valor}
        )
    
    async def notify_ride_cancelled(
        self,
        db: AsyncSession,
        user_id: UUID,
        reason: str,
        ride_id: UUID
    ):
        """Notifica cancelamento de corrida"""
        await self.create(
            db,
            user_id,
            "Corrida cancelada ❌",
            reason or "A corrida foi cancelada.",
            NotificationType.RIDE_STATUS,
            {"ride_id": str(ride_id)}
        )
    
    async def notify_payment_confirmed(
        self,
        db: AsyncSession,
        user_id: UUID,
        valor: float,
        payment_id: UUID
    ):
        """Notifica pagamento confirmado"""
        await self.create(
            db,
            user_id,
            "Pagamento confirmado! 💰",
            f"Recebemos o seu pagamento de {valor:.2f} Kz.",
            NotificationType.PAYMENT,
            {"payment_id": str(payment_id), "valor": valor}
        )
    
    async def notify_new_ride_request(
        self,
        db: AsyncSession,
        driver_id: UUID,
        origem: str,
        valor: float,
        ride_id: UUID
    ):
        """Notifica motorista de nova corrida"""
        await self.create(
            db,
            driver_id,
            "Nova corrida! 🚕",
            f"Corrida de {origem} - {valor:.2f} Kz",
            NotificationType.RIDE_STATUS,
            {"ride_id": str(ride_id), "valor": valor}
        )


# Instância global
notification_service = NotificationService()
