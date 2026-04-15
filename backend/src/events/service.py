"""
TUDOaqui API - Events Service
"""
from typing import List, Optional, Tuple
import hashlib
import secrets
from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.config import settings
from src.events.models import Event, EventStatus, TicketType, Ticket, TicketStatus, CheckIn


class EventService:
    """Serviço de eventos"""
    
    @staticmethod
    def generate_qr_code(ticket_id: UUID, event_id: UUID) -> str:
        """
        Gera QR code único e seguro para o ticket.
        QR = hash(ticket_id + event_id + secret + random)
        """
        random_part = secrets.token_hex(8)
        data = f"{ticket_id}:{event_id}:{settings.SECRET_KEY}:{random_part}"
        hash_value = hashlib.sha256(data.encode()).hexdigest()[:32]
        return f"TDQ-{hash_value.upper()}"
    
    # ============================================
    # Event CRUD
    # ============================================
    
    async def create_event(
        self,
        db: AsyncSession,
        organizer_id: UUID,
        data: dict
    ) -> Event:
        """Cria novo evento"""
        event = Event(
            organizer_id=organizer_id,
            **data,
            status=EventStatus.RASCUNHO.value
        )
        
        db.add(event)
        await db.commit()
        await db.refresh(event)
        
        return event
    
    async def get_event(self, db: AsyncSession, event_id: UUID) -> Optional[Event]:
        """Obtém evento por ID"""
        result = await db.execute(
            select(Event)
            .where(Event.id == event_id)
            .options(joinedload(Event.ticket_types))
        )
        return result.scalar_one_or_none()
    
    async def list_events(
        self,
        db: AsyncSession,
        status: Optional[EventStatus] = None,
        categoria: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Event]:
        """Lista eventos públicos"""
        query = select(Event).options(joinedload(Event.ticket_types))
        
        # Filtros
        filters = []
        if status:
            filters.append(Event.status == status.value)
        else:
            # Por padrão, só mostra eventos ativos
            filters.append(Event.status == EventStatus.ATIVO.value)
        
        if categoria:
            filters.append(Event.categoria == categoria)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(Event.data_evento.asc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.unique().scalars().all()
    
    async def list_organizer_events(
        self,
        db: AsyncSession,
        organizer_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Event]:
        """Lista eventos do organizador"""
        result = await db.execute(
            select(Event)
            .where(Event.organizer_id == organizer_id)
            .options(joinedload(Event.ticket_types))
            .order_by(Event.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()
    
    async def update_event(
        self,
        db: AsyncSession,
        event_id: UUID,
        data: dict
    ) -> Event:
        """Atualiza evento"""
        event = await self.get_event(db, event_id)
        
        if not event:
            raise ValueError("Evento não encontrado")
        
        for field, value in data.items():
            if value is not None:
                setattr(event, field, value)
        
        await db.commit()
        await db.refresh(event)
        
        return event
    
    async def publish_event(self, db: AsyncSession, event_id: UUID) -> Event:
        """Publica evento (rascunho -> ativo)"""
        event = await self.get_event(db, event_id)
        
        if not event:
            raise ValueError("Evento não encontrado")
        
        if event.status != EventStatus.RASCUNHO.value:
            raise ValueError("Apenas eventos em rascunho podem ser publicados")
        
        # Verifica se tem pelo menos um tipo de ticket
        if not event.ticket_types:
            raise ValueError("Evento precisa ter pelo menos um tipo de ticket")
        
        event.status = EventStatus.ATIVO.value
        await db.commit()
        await db.refresh(event)
        
        return event
    
    async def cancel_event(self, db: AsyncSession, event_id: UUID) -> Event:
        """Cancela evento"""
        event = await self.get_event(db, event_id)
        
        if not event:
            raise ValueError("Evento não encontrado")
        
        if event.status == EventStatus.CANCELADO.value:
            raise ValueError("Evento já cancelado")
        
        event.status = EventStatus.CANCELADO.value
        
        # Cancela todos os tickets
        await db.execute(
            Ticket.__table__.update()
            .where(Ticket.ticket_type_id.in_(
                select(TicketType.id).where(TicketType.event_id == event_id)
            ))
            .values(status=TicketStatus.CANCELADO.value)
        )
        
        await db.commit()
        await db.refresh(event)
        
        return event
    
    # ============================================
    # Ticket Types
    # ============================================
    
    async def create_ticket_type(
        self,
        db: AsyncSession,
        event_id: UUID,
        data: dict
    ) -> TicketType:
        """Cria tipo de ticket para evento"""
        event = await self.get_event(db, event_id)
        
        if not event:
            raise ValueError("Evento não encontrado")
        
        ticket_type = TicketType(
            event_id=event_id,
            nome=data["nome"],
            descricao=data.get("descricao"),
            preco=Decimal(str(data["preco"])),
            quantidade_total=data["quantidade_total"],
            max_por_compra=data.get("max_por_compra", 10)
        )
        
        db.add(ticket_type)
        await db.commit()
        await db.refresh(ticket_type)
        
        return ticket_type
    
    async def update_ticket_type(
        self,
        db: AsyncSession,
        ticket_type_id: UUID,
        data: dict
    ) -> TicketType:
        """Atualiza tipo de ticket"""
        result = await db.execute(
            select(TicketType).where(TicketType.id == ticket_type_id)
        )
        ticket_type = result.scalar_one_or_none()
        
        if not ticket_type:
            raise ValueError("Tipo de ticket não encontrado")
        
        for field, value in data.items():
            if value is not None:
                if field == "preco":
                    value = Decimal(str(value))
                setattr(ticket_type, field, value)
        
        await db.commit()
        await db.refresh(ticket_type)
        
        return ticket_type
    
    # ============================================
    # Ticket Purchase
    # ============================================
    
    async def purchase_tickets(
        self,
        db: AsyncSession,
        buyer_id: UUID,
        ticket_type_id: UUID,
        quantidade: int
    ) -> List[Ticket]:
        """Compra tickets"""
        # Busca tipo de ticket com lock
        result = await db.execute(
            select(TicketType)
            .where(TicketType.id == ticket_type_id)
            .with_for_update()
        )
        ticket_type = result.scalar_one_or_none()
        
        if not ticket_type:
            raise ValueError("Tipo de ticket não encontrado")
        
        if not ticket_type.ativo:
            raise ValueError("Tipo de ticket não disponível")
        
        if quantidade > ticket_type.max_por_compra:
            raise ValueError(f"Máximo de {ticket_type.max_por_compra} tickets por compra")
        
        disponivel = ticket_type.quantidade_total - ticket_type.quantidade_vendida
        if quantidade > disponivel:
            raise ValueError(f"Apenas {disponivel} tickets disponíveis")
        
        # Busca evento
        event_result = await db.execute(
            select(Event).where(Event.id == ticket_type.event_id)
        )
        event = event_result.scalar_one_or_none()
        
        if not event or event.status != EventStatus.ATIVO.value:
            raise ValueError("Evento não está disponível para compra")
        
        # Cria tickets
        tickets = []
        for _ in range(quantidade):
            ticket = Ticket(
                ticket_type_id=ticket_type_id,
                buyer_id=buyer_id,
                qr_code=self.generate_qr_code(UUID(str(ticket_type_id)), event.id),
                status=TicketStatus.ATIVO.value
            )
            db.add(ticket)
            tickets.append(ticket)
        
        # Atualiza quantidade vendida
        ticket_type.quantidade_vendida += quantidade
        
        await db.commit()
        
        for ticket in tickets:
            await db.refresh(ticket)
        
        return tickets
    
    async def get_user_tickets(
        self,
        db: AsyncSession,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Ticket]:
        """Lista tickets do usuário"""
        result = await db.execute(
            select(Ticket)
            .where(Ticket.buyer_id == user_id)
            .options(
                joinedload(Ticket.ticket_type).joinedload(TicketType.event)
            )
            .order_by(Ticket.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()
    
    # ============================================
    # Check-in / QR Validation
    # ============================================
    
    async def validate_qr_code(
        self,
        db: AsyncSession,
        qr_code: str,
        event_id: UUID
    ) -> Tuple[bool, str, Optional[Ticket]]:
        """
        Valida QR code do ticket.
        Retorna: (válido, mensagem, ticket)
        """
        # Busca ticket pelo QR
        result = await db.execute(
            select(Ticket)
            .where(Ticket.qr_code == qr_code)
            .options(
                joinedload(Ticket.ticket_type).joinedload(TicketType.event)
            )
        )
        ticket = result.scalar_one_or_none()
        
        if not ticket:
            return False, "QR Code inválido", None
        
        # Verifica se é do evento correto
        if ticket.ticket_type.event_id != event_id:
            return False, "Ticket não é deste evento", None
        
        # Verifica status
        if ticket.status == TicketStatus.USADO.value:
            return False, "Ticket já utilizado", ticket
        
        if ticket.status == TicketStatus.CANCELADO.value:
            return False, "Ticket cancelado", ticket
        
        if ticket.status == TicketStatus.EXPIRADO.value:
            return False, "Ticket expirado", ticket
        
        return True, "Ticket válido", ticket
    
    async def checkin_ticket(
        self,
        db: AsyncSession,
        qr_code: str,
        event_id: UUID,
        staff_id: UUID,
        device_info: Optional[str] = None
    ) -> Tuple[bool, str, Optional[CheckIn]]:
        """
        Realiza check-in do ticket.
        Retorna: (sucesso, mensagem, checkin)
        """
        # Valida QR
        valid, message, ticket = await self.validate_qr_code(db, qr_code, event_id)
        
        if not valid:
            return False, message, None
        
        # Verifica se já tem check-in (double check)
        existing_result = await db.execute(
            select(CheckIn).where(CheckIn.ticket_id == ticket.id)
        )
        if existing_result.scalar_one_or_none():
            return False, "Ticket já utilizado (check-in existente)", None
        
        # Cria check-in
        checkin = CheckIn(
            ticket_id=ticket.id,
            event_id=event_id,
            staff_id=staff_id,
            device_info=device_info
        )
        db.add(checkin)
        
        # Atualiza status do ticket
        ticket.status = TicketStatus.USADO.value
        ticket.used_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(checkin)
        
        return True, "Check-in realizado com sucesso", checkin
    
    # ============================================
    # Statistics
    # ============================================
    
    async def get_event_stats(self, db: AsyncSession, event_id: UUID) -> dict:
        """Obtém estatísticas do evento"""
        # Total de tickets vendidos
        vendidos_result = await db.execute(
            select(func.count(Ticket.id))
            .join(TicketType)
            .where(TicketType.event_id == event_id)
        )
        total_vendidos = vendidos_result.scalar() or 0
        
        # Total de check-ins
        checkins_result = await db.execute(
            select(func.count(CheckIn.id))
            .where(CheckIn.event_id == event_id)
        )
        total_checkins = checkins_result.scalar() or 0
        
        # Receita total
        receita_result = await db.execute(
            select(func.sum(TicketType.preco))
            .join(Ticket)
            .where(TicketType.event_id == event_id)
        )
        receita_total = float(receita_result.scalar() or 0)
        
        # Taxa de check-in
        taxa_checkin = (total_checkins / total_vendidos * 100) if total_vendidos > 0 else 0
        
        return {
            "total_tickets_vendidos": total_vendidos,
            "total_checkins": total_checkins,
            "receita_total": receita_total,
            "taxa_checkin": round(taxa_checkin, 2)
        }


# Instância global
event_service = EventService()
