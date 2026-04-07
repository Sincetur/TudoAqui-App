"""
TUDOaqui API - Rides Service
"""
from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal
import math

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.config import settings
from src.tuendi.rides.models import Ride, RideStatus, RideTracking, Rating
from src.tuendi.drivers.models import Driver, DriverStatus
from src.tuendi.schemas import RideRequestCreate, RideEstimateResponse
from src.users.models import User


class RideService:
    """Serviço de corridas"""
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distância em km usando Haversine"""
        R = 6371  # Raio da Terra em km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def calculate_price(distancia_km: float, duracao_min: int) -> Decimal:
        """Calcula preço da corrida"""
        preco = (
            distancia_km * settings.PRECO_BASE_KM + 
            duracao_min * settings.PRECO_BASE_MINUTO
        )
        return Decimal(max(preco, settings.TAXA_MINIMA)).quantize(Decimal("0.01"))
    
    @staticmethod
    def estimate_duration(distancia_km: float) -> int:
        """Estima duração em minutos (média 30 km/h em Luanda)"""
        return max(int(distancia_km / 0.5), 5)  # Mínimo 5 minutos
    
    async def get_nearby_drivers(
        self, 
        db: AsyncSession, 
        latitude: float, 
        longitude: float,
        raio_metros: int = None
    ) -> list[Driver]:
        """Busca motoristas próximos disponíveis"""
        raio = raio_metros or settings.RAIO_BUSCA_MOTORISTAS
        raio_graus = raio / 111000  # Aproximação grosseira
        
        result = await db.execute(
            select(Driver)
            .join(User, Driver.user_id == User.id)
            .where(and_(
                Driver.online == True,
                Driver.status == DriverStatus.APROVADO.value,
                User.status == "ativo",
                Driver.latitude.isnot(None),
                Driver.longitude.isnot(None),
                Driver.latitude.between(latitude - raio_graus, latitude + raio_graus),
                Driver.longitude.between(longitude - raio_graus, longitude + raio_graus)
            ))
            .options(joinedload(Driver.user))
        )
        drivers = result.scalars().all()
        
        # Filtra por distância real
        nearby = []
        for driver in drivers:
            dist = self.calculate_distance(
                latitude, longitude,
                float(driver.latitude), float(driver.longitude)
            ) * 1000  # Converte para metros
            
            if dist <= raio:
                driver._distance = dist
                nearby.append(driver)
        
        # Ordena por distância
        nearby.sort(key=lambda d: d._distance)
        return nearby
    
    async def estimate_ride(
        self, 
        db: AsyncSession,
        origem_lat: float,
        origem_lon: float,
        destino_lat: float,
        destino_lon: float
    ) -> RideEstimateResponse:
        """Calcula estimativa de corrida"""
        # Calcula distância
        distancia_km = self.calculate_distance(
            origem_lat, origem_lon,
            destino_lat, destino_lon
        )
        
        # Estima duração
        duracao_min = self.estimate_duration(distancia_km)
        
        # Calcula preço
        valor = self.calculate_price(distancia_km, duracao_min)
        
        # Conta motoristas disponíveis
        drivers = await self.get_nearby_drivers(db, origem_lat, origem_lon)
        
        return RideEstimateResponse(
            distancia_km=round(distancia_km, 2),
            duracao_estimada_min=duracao_min,
            valor_estimado=float(valor),
            motoristas_disponiveis=len(drivers)
        )
    
    async def request_ride(
        self,
        db: AsyncSession,
        cliente_id: UUID,
        data: RideRequestCreate
    ) -> Ride:
        """Solicita nova corrida"""
        # Verifica se cliente tem corrida ativa
        result = await db.execute(
            select(Ride)
            .where(and_(
                Ride.cliente_id == cliente_id,
                Ride.status.in_([
                    RideStatus.SOLICITADA.value,
                    RideStatus.ACEITE.value,
                    RideStatus.MOTORISTA_A_CAMINHO.value,
                    RideStatus.EM_CURSO.value
                ])
            ))
        )
        if result.scalar_one_or_none():
            raise ValueError("Já existe uma corrida em andamento")
        
        # Calcula estimativas
        distancia_km = self.calculate_distance(
            data.origem_latitude, data.origem_longitude,
            data.destino_latitude, data.destino_longitude
        )
        duracao_min = self.estimate_duration(distancia_km)
        valor = self.calculate_price(distancia_km, duracao_min)
        
        # Cria corrida
        ride = Ride(
            cliente_id=cliente_id,
            origem_endereco=data.origem_endereco,
            origem_latitude=Decimal(str(data.origem_latitude)),
            origem_longitude=Decimal(str(data.origem_longitude)),
            destino_endereco=data.destino_endereco,
            destino_latitude=Decimal(str(data.destino_latitude)),
            destino_longitude=Decimal(str(data.destino_longitude)),
            distancia_km=Decimal(str(round(distancia_km, 2))),
            duracao_estimada_min=duracao_min,
            valor_estimado=valor,
            status=RideStatus.SOLICITADA.value
        )
        
        db.add(ride)
        await db.commit()
        await db.refresh(ride)
        
        return ride
    
    async def get_ride(self, db: AsyncSession, ride_id: UUID) -> Ride | None:
        """Obtém corrida por ID"""
        result = await db.execute(
            select(Ride)
            .where(Ride.id == ride_id)
            .options(joinedload(Ride.motorista).joinedload(Driver.user))
        )
        return result.scalar_one_or_none()
    
    async def accept_ride(
        self,
        db: AsyncSession,
        ride_id: UUID,
        driver_id: UUID
    ) -> Ride:
        """Motorista aceita corrida"""
        ride = await self.get_ride(db, ride_id)
        
        if not ride:
            raise ValueError("Corrida não encontrada")
        
        if ride.status != RideStatus.SOLICITADA.value:
            raise ValueError("Corrida não está disponível")
        
        ride.motorista_id = driver_id
        ride.status = RideStatus.ACEITE.value
        ride.aceite_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(ride)
        
        return ride
    
    async def start_ride(self, db: AsyncSession, ride_id: UUID) -> Ride:
        """Inicia corrida (motorista chegou ao cliente)"""
        ride = await self.get_ride(db, ride_id)
        
        if not ride:
            raise ValueError("Corrida não encontrada")
        
        if ride.status not in [RideStatus.ACEITE.value, RideStatus.MOTORISTA_A_CAMINHO.value]:
            raise ValueError("Corrida não pode ser iniciada")
        
        ride.status = RideStatus.EM_CURSO.value
        ride.iniciada_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(ride)
        
        return ride
    
    async def finish_ride(self, db: AsyncSession, ride_id: UUID) -> Ride:
        """Finaliza corrida"""
        ride = await self.get_ride(db, ride_id)
        
        if not ride:
            raise ValueError("Corrida não encontrada")
        
        if ride.status != RideStatus.EM_CURSO.value:
            raise ValueError("Corrida não está em curso")
        
        ride.status = RideStatus.FINALIZADA.value
        ride.finalizada_at = datetime.now(timezone.utc)
        ride.valor_final = ride.valor_estimado  # Pode ser recalculado
        
        await db.commit()
        await db.refresh(ride)
        
        return ride
    
    async def cancel_ride(
        self,
        db: AsyncSession,
        ride_id: UUID,
        user_id: UUID,
        motivo: str | None = None
    ) -> Ride:
        """Cancela corrida"""
        ride = await self.get_ride(db, ride_id)
        
        if not ride:
            raise ValueError("Corrida não encontrada")
        
        if ride.status in [RideStatus.FINALIZADA.value, RideStatus.CANCELADA_CLIENTE.value, RideStatus.CANCELADA_MOTORISTA.value]:
            raise ValueError("Corrida já finalizada ou cancelada")
        
        # Determina quem cancelou
        if ride.cliente_id == user_id:
            ride.status = RideStatus.CANCELADA_CLIENTE.value
        elif ride.motorista and ride.motorista.user_id == user_id:
            ride.status = RideStatus.CANCELADA_MOTORISTA.value
        else:
            raise ValueError("Não autorizado a cancelar esta corrida")
        
        ride.cancelada_at = datetime.now(timezone.utc)
        ride.motivo_cancelamento = motivo
        
        await db.commit()
        await db.refresh(ride)
        
        return ride
    
    async def get_client_rides(
        self,
        db: AsyncSession,
        cliente_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> list[Ride]:
        """Lista corridas do cliente"""
        result = await db.execute(
            select(Ride)
            .where(Ride.cliente_id == cliente_id)
            .order_by(Ride.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(joinedload(Ride.motorista).joinedload(Driver.user))
        )
        return result.scalars().all()
    
    async def get_driver_rides(
        self,
        db: AsyncSession,
        driver_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> list[Ride]:
        """Lista corridas do motorista"""
        result = await db.execute(
            select(Ride)
            .where(Ride.motorista_id == driver_id)
            .order_by(Ride.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_pending_rides(
        self,
        db: AsyncSession,
        driver_latitude: float,
        driver_longitude: float
    ) -> list[Ride]:
        """Lista corridas pendentes próximas ao motorista"""
        raio_graus = settings.RAIO_BUSCA_MOTORISTAS / 111000
        
        result = await db.execute(
            select(Ride)
            .where(and_(
                Ride.status == RideStatus.SOLICITADA.value,
                Ride.origem_latitude.between(
                    driver_latitude - raio_graus, 
                    driver_latitude + raio_graus
                ),
                Ride.origem_longitude.between(
                    driver_longitude - raio_graus, 
                    driver_longitude + raio_graus
                )
            ))
            .order_by(Ride.solicitada_at.asc())
            .limit(10)
        )
        return result.scalars().all()
    
    async def add_rating(
        self,
        db: AsyncSession,
        ride_id: UUID,
        avaliador_id: UUID,
        avaliado_id: UUID,
        tipo: str,
        nota: int,
        comentario: str | None = None
    ) -> Rating:
        """Adiciona avaliação"""
        rating = Rating(
            ride_id=ride_id,
            avaliador_id=avaliador_id,
            avaliado_id=avaliado_id,
            tipo=tipo,
            nota=nota,
            comentario=comentario
        )
        
        db.add(rating)
        await db.commit()
        await db.refresh(rating)
        
        return rating
    
    async def add_tracking_point(
        self,
        db: AsyncSession,
        ride_id: UUID,
        latitude: float,
        longitude: float,
        velocidade: float | None = None,
        bearing: float | None = None
    ) -> RideTracking:
        """Adiciona ponto de tracking"""
        point = RideTracking(
            ride_id=ride_id,
            latitude=Decimal(str(latitude)),
            longitude=Decimal(str(longitude)),
            velocidade=Decimal(str(velocidade)) if velocidade else None,
            bearing=Decimal(str(bearing)) if bearing else None
        )
        
        db.add(point)
        await db.commit()
        
        return point


# Instância global
ride_service = RideService()
