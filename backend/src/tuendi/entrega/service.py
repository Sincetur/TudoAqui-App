"""
TUDOaqui API - Tuendi Entrega Service
"""
import secrets
import math
from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.config import settings
from src.tuendi.entrega.models import (
    Delivery, DeliveryStatus, DeliveryType, DeliveryPriority,
    DeliveryTracking
)
from src.tuendi.drivers.models import Driver, DriverStatus


class EntregaService:
    """Serviço de Entregas"""
    
    # Preços base por km
    PRECO_BASE_KM = Decimal("100")  # Kz por km
    PRECO_MINIMO = Decimal("500")  # Kz
    
    # Multiplicadores por tipo de pacote
    TIPO_MULTIPLICADOR = {
        DeliveryType.DOCUMENTO.value: Decimal("1.0"),
        DeliveryType.PACOTE_PEQUENO.value: Decimal("1.0"),
        DeliveryType.PACOTE_MEDIO.value: Decimal("1.3"),
        DeliveryType.PACOTE_GRANDE.value: Decimal("1.6"),
        DeliveryType.FRAGIL.value: Decimal("1.5"),
    }
    
    # Multiplicadores por prioridade
    PRIORIDADE_MULTIPLICADOR = {
        DeliveryPriority.NORMAL.value: Decimal("1.0"),
        DeliveryPriority.EXPRESS.value: Decimal("1.5"),
        DeliveryPriority.URGENTE.value: Decimal("2.0"),
    }
    
    # Taxa por kg acima de 5kg
    TAXA_PESO_KG = Decimal("50")  # Kz por kg acima de 5kg
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distância usando Haversine"""
        R = 6371  # Raio da Terra em km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    @staticmethod
    def generate_code() -> str:
        """Gera código de 4 dígitos"""
        return ''.join(secrets.choice('0123456789') for _ in range(4))
    
    def estimate_delivery(
        self,
        origem_lat: float,
        origem_lon: float,
        destino_lat: float,
        destino_lon: float,
        tipo: DeliveryType,
        prioridade: DeliveryPriority,
        peso_kg: float | None = None
    ) -> dict:
        """Estima preço da entrega"""
        # Calcula distância
        distancia = self.calculate_distance(origem_lat, origem_lon, destino_lat, destino_lon)
        
        # Preço base
        preco_base = max(self.PRECO_BASE_KM * Decimal(str(distancia)), self.PRECO_MINIMO)
        preco_base *= self.TIPO_MULTIPLICADOR.get(tipo.value, Decimal("1.0"))
        
        # Taxa de prioridade
        taxa_prioridade = preco_base * (self.PRIORIDADE_MULTIPLICADOR.get(prioridade.value, Decimal("1.0")) - 1)
        
        # Taxa de peso
        taxa_peso = Decimal("0")
        if peso_kg and peso_kg > 5:
            taxa_peso = self.TAXA_PESO_KG * Decimal(str(peso_kg - 5))
        
        total = preco_base + taxa_prioridade + taxa_peso
        
        # Duração estimada (média 30km/h em Luanda)
        duracao_min = int((distancia / 30) * 60) + 15  # +15 min para recolha
        
        return {
            "distancia_km": round(distancia, 2),
            "duracao_estimada_min": duracao_min,
            "preco_base": float(preco_base),
            "taxa_prioridade": float(taxa_prioridade),
            "taxa_peso": float(taxa_peso),
            "total": float(total)
        }
    
    async def create_delivery(
        self,
        db: AsyncSession,
        sender_id: UUID,
        data: dict
    ) -> Delivery:
        """Cria nova entrega"""
        # Calcula estimativa
        estimate = self.estimate_delivery(
            data["origem_latitude"],
            data["origem_longitude"],
            data["destino_latitude"],
            data["destino_longitude"],
            DeliveryType(data.get("tipo", "pacote_pequeno")),
            DeliveryPriority(data.get("prioridade", "normal")),
            data.get("peso_estimado")
        )
        
        delivery = Delivery(
            sender_id=sender_id,
            tipo=data.get("tipo", DeliveryType.PACOTE_PEQUENO.value),
            prioridade=data.get("prioridade", DeliveryPriority.NORMAL.value),
            descricao=data["descricao"],
            peso_estimado=Decimal(str(data["peso_estimado"])) if data.get("peso_estimado") else None,
            
            origem_endereco=data["origem_endereco"],
            origem_latitude=Decimal(str(data["origem_latitude"])),
            origem_longitude=Decimal(str(data["origem_longitude"])),
            origem_referencia=data.get("origem_referencia"),
            origem_contato_nome=data["origem_contato_nome"],
            origem_contato_telefone=data["origem_contato_telefone"],
            
            destino_endereco=data["destino_endereco"],
            destino_latitude=Decimal(str(data["destino_latitude"])),
            destino_longitude=Decimal(str(data["destino_longitude"])),
            destino_referencia=data.get("destino_referencia"),
            destino_contato_nome=data["destino_contato_nome"],
            destino_contato_telefone=data["destino_contato_telefone"],
            
            distancia_km=Decimal(str(estimate["distancia_km"])),
            preco_base=Decimal(str(estimate["preco_base"])),
            taxa_prioridade=Decimal(str(estimate["taxa_prioridade"])),
            taxa_peso=Decimal(str(estimate["taxa_peso"])),
            total=Decimal(str(estimate["total"])),
            
            instrucoes_recolha=data.get("instrucoes_recolha"),
            instrucoes_entrega=data.get("instrucoes_entrega"),
            
            codigo_recolha=self.generate_code(),
            codigo_entrega=self.generate_code(),
            
            status=DeliveryStatus.PENDENTE.value
        )
        
        db.add(delivery)
        
        # Adiciona tracking inicial
        tracking = DeliveryTracking(
            delivery_id=delivery.id,
            status=DeliveryStatus.PENDENTE.value,
            descricao="Entrega solicitada"
        )
        db.add(tracking)
        
        await db.commit()
        await db.refresh(delivery)
        return delivery
    
    async def get_delivery(self, db: AsyncSession, delivery_id: UUID) -> Delivery | None:
        """Obtém entrega por ID"""
        result = await db.execute(
            select(Delivery)
            .where(Delivery.id == delivery_id)
            .options(
                joinedload(Delivery.driver).joinedload(Driver.user),
                joinedload(Delivery.sender)
            )
        )
        return result.scalar_one_or_none()
    
    async def list_sender_deliveries(
        self,
        db: AsyncSession,
        sender_id: UUID,
        status: DeliveryStatus | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[Delivery]:
        """Lista entregas do remetente"""
        query = select(Delivery).where(Delivery.sender_id == sender_id)
        
        if status:
            query = query.where(Delivery.status == status.value)
        
        query = query.order_by(Delivery.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def list_available_deliveries(
        self,
        db: AsyncSession,
        driver_lat: float,
        driver_lon: float,
        raio_km: float = 10,
        limit: int = 20
    ) -> list[Delivery]:
        """Lista entregas disponíveis próximas ao motorista"""
        # Converte raio para graus (aproximação)
        raio_graus = raio_km / 111
        
        result = await db.execute(
            select(Delivery)
            .where(and_(
                Delivery.status == DeliveryStatus.PENDENTE.value,
                Delivery.driver_id.is_(None),
                Delivery.origem_latitude.between(
                    Decimal(str(driver_lat - raio_graus)),
                    Decimal(str(driver_lat + raio_graus))
                ),
                Delivery.origem_longitude.between(
                    Decimal(str(driver_lon - raio_graus)),
                    Decimal(str(driver_lon + raio_graus))
                )
            ))
            .order_by(Delivery.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def list_driver_deliveries(
        self,
        db: AsyncSession,
        driver_id: UUID,
        status: DeliveryStatus | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[Delivery]:
        """Lista entregas do motorista"""
        query = select(Delivery).where(Delivery.driver_id == driver_id)
        
        if status:
            query = query.where(Delivery.status == status.value)
        
        query = query.order_by(Delivery.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def accept_delivery(
        self,
        db: AsyncSession,
        delivery_id: UUID,
        driver_id: UUID
    ) -> Delivery:
        """Motorista aceita entrega"""
        delivery = await self.get_delivery(db, delivery_id)
        if not delivery:
            raise ValueError("Entrega não encontrada")
        
        if delivery.status != DeliveryStatus.PENDENTE.value:
            raise ValueError("Entrega não está disponível")
        
        if delivery.driver_id:
            raise ValueError("Entrega já foi aceite")
        
        delivery.driver_id = driver_id
        delivery.status = DeliveryStatus.ACEITE.value
        delivery.aceite_at = datetime.now(timezone.utc)
        
        # Tracking
        tracking = DeliveryTracking(
            delivery_id=delivery_id,
            status=DeliveryStatus.ACEITE.value,
            descricao="Entrega aceite pelo motorista"
        )
        db.add(tracking)
        
        await db.commit()
        await db.refresh(delivery)
        return delivery
    
    async def start_pickup(
        self,
        db: AsyncSession,
        delivery_id: UUID,
        driver_id: UUID
    ) -> Delivery:
        """Motorista a caminho da recolha"""
        delivery = await self.get_delivery(db, delivery_id)
        if not delivery:
            raise ValueError("Entrega não encontrada")
        
        if delivery.driver_id != driver_id:
            raise ValueError("Não é o motorista desta entrega")
        
        if delivery.status != DeliveryStatus.ACEITE.value:
            raise ValueError("Status inválido")
        
        delivery.status = DeliveryStatus.RECOLHA.value
        
        tracking = DeliveryTracking(
            delivery_id=delivery_id,
            status=DeliveryStatus.RECOLHA.value,
            descricao="Motorista a caminho para recolha"
        )
        db.add(tracking)
        
        await db.commit()
        await db.refresh(delivery)
        return delivery
    
    async def confirm_pickup(
        self,
        db: AsyncSession,
        delivery_id: UUID,
        driver_id: UUID,
        codigo: str,
        foto_url: str | None = None
    ) -> Delivery:
        """Confirma recolha do pacote"""
        delivery = await self.get_delivery(db, delivery_id)
        if not delivery:
            raise ValueError("Entrega não encontrada")
        
        if delivery.driver_id != driver_id:
            raise ValueError("Não é o motorista desta entrega")
        
        if delivery.status not in [DeliveryStatus.ACEITE.value, DeliveryStatus.RECOLHA.value]:
            raise ValueError("Status inválido")
        
        if delivery.codigo_recolha != codigo:
            raise ValueError("Código de recolha inválido")
        
        delivery.status = DeliveryStatus.RECOLHIDO.value
        delivery.recolhido_at = datetime.now(timezone.utc)
        delivery.foto_recolha_url = foto_url
        
        tracking = DeliveryTracking(
            delivery_id=delivery_id,
            status=DeliveryStatus.RECOLHIDO.value,
            descricao="Pacote recolhido"
        )
        db.add(tracking)
        
        await db.commit()
        await db.refresh(delivery)
        return delivery
    
    async def start_transit(
        self,
        db: AsyncSession,
        delivery_id: UUID,
        driver_id: UUID
    ) -> Delivery:
        """Inicia trânsito para destino"""
        delivery = await self.get_delivery(db, delivery_id)
        if not delivery:
            raise ValueError("Entrega não encontrada")
        
        if delivery.driver_id != driver_id:
            raise ValueError("Não é o motorista desta entrega")
        
        if delivery.status != DeliveryStatus.RECOLHIDO.value:
            raise ValueError("Status inválido")
        
        delivery.status = DeliveryStatus.EM_TRANSITO.value
        
        tracking = DeliveryTracking(
            delivery_id=delivery_id,
            status=DeliveryStatus.EM_TRANSITO.value,
            descricao="Pacote em trânsito para destino"
        )
        db.add(tracking)
        
        await db.commit()
        await db.refresh(delivery)
        return delivery
    
    async def confirm_delivery(
        self,
        db: AsyncSession,
        delivery_id: UUID,
        driver_id: UUID,
        codigo: str,
        foto_url: str | None = None
    ) -> Delivery:
        """Confirma entrega do pacote"""
        delivery = await self.get_delivery(db, delivery_id)
        if not delivery:
            raise ValueError("Entrega não encontrada")
        
        if delivery.driver_id != driver_id:
            raise ValueError("Não é o motorista desta entrega")
        
        if delivery.status not in [DeliveryStatus.RECOLHIDO.value, DeliveryStatus.EM_TRANSITO.value]:
            raise ValueError("Status inválido")
        
        if delivery.codigo_entrega != codigo:
            raise ValueError("Código de entrega inválido")
        
        delivery.status = DeliveryStatus.ENTREGUE.value
        delivery.entregue_at = datetime.now(timezone.utc)
        delivery.foto_entrega_url = foto_url
        
        tracking = DeliveryTracking(
            delivery_id=delivery_id,
            status=DeliveryStatus.ENTREGUE.value,
            descricao="Pacote entregue com sucesso"
        )
        db.add(tracking)
        
        await db.commit()
        await db.refresh(delivery)
        return delivery
    
    async def cancel_delivery(
        self,
        db: AsyncSession,
        delivery_id: UUID,
        user_id: UUID,
        motivo: str
    ) -> Delivery:
        """Cancela entrega"""
        delivery = await self.get_delivery(db, delivery_id)
        if not delivery:
            raise ValueError("Entrega não encontrada")
        
        # Só pode cancelar se for o remetente ou antes da recolha
        if delivery.sender_id != user_id:
            if delivery.status not in [DeliveryStatus.PENDENTE.value, DeliveryStatus.ACEITE.value]:
                raise ValueError("Não é possível cancelar após recolha")
        
        delivery.status = DeliveryStatus.CANCELADO.value
        delivery.cancelado_at = datetime.now(timezone.utc)
        delivery.motivo_cancelamento = motivo
        
        tracking = DeliveryTracking(
            delivery_id=delivery_id,
            status=DeliveryStatus.CANCELADO.value,
            descricao=f"Entrega cancelada: {motivo}"
        )
        db.add(tracking)
        
        await db.commit()
        await db.refresh(delivery)
        return delivery
    
    async def update_driver_location(
        self,
        db: AsyncSession,
        delivery_id: UUID,
        driver_id: UUID,
        latitude: float,
        longitude: float
    ):
        """Atualiza localização do motorista"""
        delivery = await self.get_delivery(db, delivery_id)
        if not delivery or delivery.driver_id != driver_id:
            return
        
        if delivery.status not in [
            DeliveryStatus.RECOLHA.value,
            DeliveryStatus.EM_TRANSITO.value
        ]:
            return
        
        tracking = DeliveryTracking(
            delivery_id=delivery_id,
            status=delivery.status,
            descricao="Localização atualizada",
            latitude=Decimal(str(latitude)),
            longitude=Decimal(str(longitude))
        )
        db.add(tracking)
        await db.commit()
    
    async def get_tracking_history(
        self,
        db: AsyncSession,
        delivery_id: UUID
    ) -> list[DeliveryTracking]:
        """Obtém histórico de tracking"""
        result = await db.execute(
            select(DeliveryTracking)
            .where(DeliveryTracking.delivery_id == delivery_id)
            .order_by(DeliveryTracking.created_at.asc())
        )
        return result.scalars().all()


# Instância global
entrega_service = EntregaService()
