"""
TUDOaqui API - Drivers Service
"""
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.tuendi.drivers.models import Driver, DriverStatus
from src.tuendi.schemas import DriverCreate, DriverUpdate, DriverOnlineUpdate
from src.users.models import User, UserRole


class DriverService:
    """Serviço de motoristas"""
    
    async def register_driver(
        self,
        db: AsyncSession,
        user_id: UUID,
        data: DriverCreate
    ) -> Driver:
        """Regista novo motorista"""
        # Verifica se já existe
        result = await db.execute(
            select(Driver).where(Driver.user_id == user_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise ValueError("Utilizador já é motorista registado")
        
        # Atualiza role do utilizador
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("Utilizador não encontrado")
        
        user.role = UserRole.MOTORISTA.value
        
        # Cria perfil de motorista
        driver = Driver(
            user_id=user_id,
            veiculo=data.veiculo,
            matricula=data.matricula,
            cor_veiculo=data.cor_veiculo,
            marca=data.marca,
            modelo=data.modelo,
            ano=data.ano,
            carta_conducao=data.carta_conducao,
            documento_veiculo=data.documento_veiculo,
            status=DriverStatus.PENDENTE.value
        )
        
        db.add(driver)
        await db.commit()
        await db.refresh(driver)
        
        return driver
    
    async def get_driver(self, db: AsyncSession, driver_id: UUID) -> Optional[Driver]:
        """Obtém motorista por ID"""
        result = await db.execute(
            select(Driver)
            .where(Driver.id == driver_id)
            .options(joinedload(Driver.user))
        )
        return result.scalar_one_or_none()
    
    async def get_driver_by_user(self, db: AsyncSession, user_id: UUID) -> Optional[Driver]:
        """Obtém motorista pelo user_id"""
        result = await db.execute(
            select(Driver)
            .where(Driver.user_id == user_id)
            .options(joinedload(Driver.user))
        )
        return result.scalar_one_or_none()
    
    async def update_driver(
        self,
        db: AsyncSession,
        driver_id: UUID,
        data: DriverUpdate
    ) -> Driver:
        """Atualiza dados do motorista"""
        driver = await self.get_driver(db, driver_id)
        
        if not driver:
            raise ValueError("Motorista não encontrado")
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(driver, field, value)
        
        await db.commit()
        await db.refresh(driver)
        
        return driver
    
    async def update_online_status(
        self,
        db: AsyncSession,
        driver_id: UUID,
        data: DriverOnlineUpdate
    ) -> Driver:
        """Atualiza status online e localização"""
        driver = await self.get_driver(db, driver_id)
        
        if not driver:
            raise ValueError("Motorista não encontrado")
        
        if driver.status != DriverStatus.APROVADO.value:
            raise ValueError("Motorista não aprovado")
        
        driver.online = data.online
        
        if data.online and data.latitude and data.longitude:
            driver.latitude = Decimal(str(data.latitude))
            driver.longitude = Decimal(str(data.longitude))
            driver.ultima_localizacao_at = datetime.now(timezone.utc)
        
        if not data.online:
            driver.latitude = None
            driver.longitude = None
        
        await db.commit()
        await db.refresh(driver)
        
        return driver
    
    async def update_location(
        self,
        db: AsyncSession,
        driver_id: UUID,
        latitude: float,
        longitude: float
    ) -> Driver:
        """Atualiza apenas localização"""
        driver = await self.get_driver(db, driver_id)
        
        if not driver:
            raise ValueError("Motorista não encontrado")
        
        if not driver.online:
            raise ValueError("Motorista offline")
        
        driver.latitude = Decimal(str(latitude))
        driver.longitude = Decimal(str(longitude))
        driver.ultima_localizacao_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(driver)
        
        return driver
    
    async def approve_driver(self, db: AsyncSession, driver_id: UUID) -> Driver:
        """Aprova motorista (admin)"""
        driver = await self.get_driver(db, driver_id)
        
        if not driver:
            raise ValueError("Motorista não encontrado")
        
        driver.status = DriverStatus.APROVADO.value
        
        await db.commit()
        await db.refresh(driver)
        
        return driver
    
    async def suspend_driver(self, db: AsyncSession, driver_id: UUID) -> Driver:
        """Suspende motorista (admin)"""
        driver = await self.get_driver(db, driver_id)
        
        if not driver:
            raise ValueError("Motorista não encontrado")
        
        driver.status = DriverStatus.SUSPENSO.value
        driver.online = False
        
        await db.commit()
        await db.refresh(driver)
        
        return driver
    
    async def list_drivers(
        self,
        db: AsyncSession,
        status: Optional[DriverStatus] = None,
        online: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Driver]:
        """Lista motoristas com filtros"""
        query = select(Driver).options(joinedload(Driver.user))
        
        if status:
            query = query.where(Driver.status == status.value)
        
        if online is not None:
            query = query.where(Driver.online == online)
        
        query = query.order_by(Driver.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_driver_stats(self, db: AsyncSession, driver_id: UUID) -> dict:
        """Obtém estatísticas do motorista"""
        from src.tuendi.rides.models import Ride, RideStatus
        from src.payments.models import LedgerEntry
        
        driver = await self.get_driver(db, driver_id)
        
        if not driver:
            raise ValueError("Motorista não encontrado")
        
        # Total de corridas finalizadas
        rides_result = await db.execute(
            select(func.count(Ride.id))
            .where(and_(
                Ride.motorista_id == driver_id,
                Ride.status == RideStatus.FINALIZADA.value
            ))
        )
        total_corridas = rides_result.scalar() or 0
        
        # Total de ganhos
        ganhos_result = await db.execute(
            select(func.sum(LedgerEntry.valor))
            .where(and_(
                LedgerEntry.beneficiario_id == driver.user_id,
                LedgerEntry.tipo == "credito"
            ))
        )
        total_ganhos = float(ganhos_result.scalar() or 0)
        
        # Corridas hoje
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        rides_hoje_result = await db.execute(
            select(func.count(Ride.id))
            .where(and_(
                Ride.motorista_id == driver_id,
                Ride.status == RideStatus.FINALIZADA.value,
                Ride.finalizada_at >= today_start
            ))
        )
        corridas_hoje = rides_hoje_result.scalar() or 0
        
        # Ganhos hoje
        ganhos_hoje_result = await db.execute(
            select(func.sum(LedgerEntry.valor))
            .where(and_(
                LedgerEntry.beneficiario_id == driver.user_id,
                LedgerEntry.tipo == "credito",
                LedgerEntry.created_at >= today_start
            ))
        )
        ganhos_hoje = float(ganhos_hoje_result.scalar() or 0)
        
        return {
            "total_corridas": total_corridas,
            "total_ganhos": total_ganhos,
            "rating_medio": float(driver.rating_medio),
            "corridas_hoje": corridas_hoje,
            "ganhos_hoje": ganhos_hoje
        }


# Instância global
driver_service = DriverService()
