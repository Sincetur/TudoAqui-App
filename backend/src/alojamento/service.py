"""
TUDOaqui API - Alojamento Service
"""
from typing import List, Optional, Tuple
from datetime import datetime, timezone, date, timedelta
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.alojamento.models import (
    Property, PropertyStatus, PropertyType,
    PropertyAvailability, Booking, BookingStatus,
    PropertyReview
)
from src.users.models import User, UserRole


class AlojamentoService:
    """Serviço de Alojamento"""
    
    TAXA_SERVICO_PERCENT = Decimal("0.10")  # 10% taxa de serviço
    
    # ============================================
    # Property Management
    # ============================================
    
    async def create_property(
        self,
        db: AsyncSession,
        host_id: UUID,
        data: dict
    ) -> Property:
        """Cria nova propriedade"""
        property_obj = Property(
            host_id=host_id,
            titulo=data["titulo"],
            descricao=data.get("descricao"),
            tipo=data.get("tipo", PropertyType.CASA.value),
            endereco=data["endereco"],
            cidade=data["cidade"],
            provincia=data["provincia"],
            latitude=Decimal(str(data["latitude"])) if data.get("latitude") else None,
            longitude=Decimal(str(data["longitude"])) if data.get("longitude") else None,
            quartos=data.get("quartos", 1),
            camas=data.get("camas", 1),
            banheiros=data.get("banheiros", 1),
            max_hospedes=data.get("max_hospedes", 2),
            preco_noite=Decimal(str(data["preco_noite"])),
            preco_limpeza=Decimal(str(data.get("preco_limpeza", 0))),
            desconto_semanal=data.get("desconto_semanal", 0),
            desconto_mensal=data.get("desconto_mensal", 0),
            min_noites=data.get("min_noites", 1),
            max_noites=data.get("max_noites", 30),
            checkin_hora=data.get("checkin_hora", "15:00"),
            checkout_hora=data.get("checkout_hora", "11:00"),
            comodidades={"items": data.get("comodidades", [])},
            imagens={"urls": data.get("imagens", [])},
            status=PropertyStatus.PENDENTE.value
        )
        
        db.add(property_obj)
        await db.commit()
        await db.refresh(property_obj)
        
        return property_obj
    
    async def get_property(self, db: AsyncSession, property_id: UUID) -> Optional[Property]:
        """Obtém propriedade por ID"""
        result = await db.execute(
            select(Property)
            .where(Property.id == property_id)
            .options(joinedload(Property.host))
        )
        return result.scalar_one_or_none()
    
    async def update_property(
        self,
        db: AsyncSession,
        property_id: UUID,
        data: dict
    ) -> Property:
        """Atualiza propriedade"""
        prop = await self.get_property(db, property_id)
        if not prop:
            raise ValueError("Propriedade não encontrada")
        
        for field, value in data.items():
            if value is not None:
                if field in ["preco_noite", "preco_limpeza", "latitude", "longitude"]:
                    value = Decimal(str(value)) if value else None
                if field == "comodidades":
                    value = {"items": value}
                if field == "imagens":
                    value = {"urls": value}
                setattr(prop, field, value)
        
        await db.commit()
        await db.refresh(prop)
        return prop
    
    async def list_properties(
        self,
        db: AsyncSession,
        cidade: Optional[str] = None,
        provincia: Optional[str] = None,
        tipo: Optional[PropertyType] = None,
        hospedes: Optional[int] = None,
        preco_min: Optional[float] = None,
        preco_max: Optional[float] = None,
        quartos_min: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Property]:
        """Lista propriedades com filtros"""
        query = select(Property).where(
            Property.status == PropertyStatus.ATIVO.value,
            Property.ativo.is_(True)
        )
        
        if cidade:
            query = query.where(Property.cidade.ilike(f"%{cidade}%"))
        if provincia:
            query = query.where(Property.provincia == provincia)
        if tipo:
            query = query.where(Property.tipo == tipo.value)
        if hospedes:
            query = query.where(Property.max_hospedes >= hospedes)
        if preco_min:
            query = query.where(Property.preco_noite >= preco_min)
        if preco_max:
            query = query.where(Property.preco_noite <= preco_max)
        if quartos_min:
            query = query.where(Property.quartos >= quartos_min)
        
        query = query.order_by(Property.rating_medio.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def list_host_properties(
        self,
        db: AsyncSession,
        host_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Property]:
        """Lista propriedades do anfitrião"""
        result = await db.execute(
            select(Property)
            .where(Property.host_id == host_id)
            .order_by(Property.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def publish_property(self, db: AsyncSession, property_id: UUID) -> Property:
        """Publica propriedade"""
        prop = await self.get_property(db, property_id)
        if not prop:
            raise ValueError("Propriedade não encontrada")
        
        prop.status = PropertyStatus.ATIVO.value
        await db.commit()
        await db.refresh(prop)
        return prop
    
    # ============================================
    # Availability
    # ============================================
    
    async def check_availability(
        self,
        db: AsyncSession,
        property_id: UUID,
        data_checkin: date,
        data_checkout: date
    ) -> Tuple[bool, List[date]]:
        """
        Verifica disponibilidade.
        Retorna: (disponível, lista de datas indisponíveis)
        """
        # Busca bloqueios
        result = await db.execute(
            select(PropertyAvailability)
            .where(and_(
                PropertyAvailability.property_id == property_id,
                PropertyAvailability.data >= data_checkin,
                PropertyAvailability.data < data_checkout,
                PropertyAvailability.disponivel.is_(False)
            ))
        )
        blocked_dates = [a.data for a in result.scalars().all()]
        
        # Busca reservas existentes
        bookings_result = await db.execute(
            select(Booking)
            .where(and_(
                Booking.property_id == property_id,
                Booking.status.in_([
                    BookingStatus.PENDENTE.value,
                    BookingStatus.CONFIRMADA.value,
                    BookingStatus.EM_ANDAMENTO.value
                ]),
                or_(
                    and_(Booking.data_checkin <= data_checkin, Booking.data_checkout > data_checkin),
                    and_(Booking.data_checkin < data_checkout, Booking.data_checkout >= data_checkout),
                    and_(Booking.data_checkin >= data_checkin, Booking.data_checkout <= data_checkout)
                )
            ))
        )
        bookings = bookings_result.scalars().all()
        
        for booking in bookings:
            current = booking.data_checkin
            while current < booking.data_checkout:
                if current not in blocked_dates:
                    blocked_dates.append(current)
                current += timedelta(days=1)
        
        return len(blocked_dates) == 0, blocked_dates
    
    async def update_availability(
        self,
        db: AsyncSession,
        property_id: UUID,
        data_inicio: date,
        data_fim: date,
        disponivel: bool,
        preco_especial: Optional[float] = None,
        motivo_bloqueio: Optional[str] = None
    ):
        """Atualiza disponibilidade de um período"""
        current = data_inicio
        while current <= data_fim:
            # Verifica se já existe
            result = await db.execute(
                select(PropertyAvailability)
                .where(and_(
                    PropertyAvailability.property_id == property_id,
                    PropertyAvailability.data == current
                ))
            )
            avail = result.scalar_one_or_none()
            
            if avail:
                avail.disponivel = disponivel
                avail.preco_especial = Decimal(str(preco_especial)) if preco_especial else None
                avail.motivo_bloqueio = motivo_bloqueio
            else:
                avail = PropertyAvailability(
                    property_id=property_id,
                    data=current,
                    disponivel=disponivel,
                    preco_especial=Decimal(str(preco_especial)) if preco_especial else None,
                    motivo_bloqueio=motivo_bloqueio
                )
                db.add(avail)
            
            current += timedelta(days=1)
        
        await db.commit()
    
    # ============================================
    # Bookings
    # ============================================
    
    async def create_booking(
        self,
        db: AsyncSession,
        guest_id: UUID,
        data: dict
    ) -> Booking:
        """Cria reserva"""
        property_id = data["property_id"]
        data_checkin = data["data_checkin"]
        data_checkout = data["data_checkout"]
        
        # Valida propriedade
        prop = await self.get_property(db, property_id)
        if not prop or prop.status != PropertyStatus.ATIVO.value:
            raise ValueError("Propriedade não disponível")
        
        # Valida datas
        if data_checkin >= data_checkout:
            raise ValueError("Data de checkout deve ser após checkin")
        
        noites = (data_checkout - data_checkin).days
        
        if noites < prop.min_noites:
            raise ValueError(f"Mínimo de {prop.min_noites} noites")
        if noites > prop.max_noites:
            raise ValueError(f"Máximo de {prop.max_noites} noites")
        
        # Valida capacidade
        total_hospedes = data.get("adultos", 1) + data.get("criancas", 0)
        if total_hospedes > prop.max_hospedes:
            raise ValueError(f"Máximo de {prop.max_hospedes} hóspedes")
        
        # Verifica disponibilidade
        disponivel, blocked = await self.check_availability(db, property_id, data_checkin, data_checkout)
        if not disponivel:
            raise ValueError("Datas não disponíveis")
        
        # Calcula valores
        preco_noite = prop.preco_noite
        subtotal = preco_noite * noites
        
        # Desconto por período
        desconto = Decimal("0")
        if noites >= 30 and prop.desconto_mensal > 0:
            desconto = subtotal * Decimal(str(prop.desconto_mensal / 100))
        elif noites >= 7 and prop.desconto_semanal > 0:
            desconto = subtotal * Decimal(str(prop.desconto_semanal / 100))
        
        taxa_limpeza = prop.preco_limpeza
        taxa_servico = (subtotal - desconto) * self.TAXA_SERVICO_PERCENT
        total = subtotal - desconto + taxa_limpeza + taxa_servico
        
        # Cria reserva
        booking = Booking(
            property_id=property_id,
            guest_id=guest_id,
            data_checkin=data_checkin,
            data_checkout=data_checkout,
            noites=noites,
            adultos=data.get("adultos", 1),
            criancas=data.get("criancas", 0),
            preco_noite=preco_noite,
            subtotal=subtotal,
            taxa_limpeza=taxa_limpeza,
            taxa_servico=taxa_servico,
            desconto=desconto,
            total=total,
            telefone_contato=data["telefone_contato"],
            notas=data.get("notas"),
            status=BookingStatus.PENDENTE.value
        )
        
        db.add(booking)
        
        # Atualiza stats da propriedade
        prop.total_reservas += 1
        
        await db.commit()
        await db.refresh(booking)
        
        return booking
    
    async def get_booking(self, db: AsyncSession, booking_id: UUID) -> Optional[Booking]:
        """Obtém reserva por ID"""
        result = await db.execute(
            select(Booking)
            .where(Booking.id == booking_id)
            .options(
                joinedload(Booking.property).joinedload(Property.host),
                joinedload(Booking.guest)
            )
        )
        return result.scalar_one_or_none()
    
    async def update_booking_status(
        self,
        db: AsyncSession,
        booking_id: UUID,
        status: BookingStatus,
        motivo_cancelamento: Optional[str] = None
    ) -> Booking:
        """Atualiza status da reserva"""
        booking = await self.get_booking(db, booking_id)
        if not booking:
            raise ValueError("Reserva não encontrada")
        
        booking.status = status.value
        now = datetime.now(timezone.utc)
        
        if status == BookingStatus.CONFIRMADA:
            booking.confirmada_at = now
        elif status == BookingStatus.EM_ANDAMENTO:
            booking.checkin_at = now
        elif status == BookingStatus.FINALIZADA:
            booking.checkout_at = now
        elif status == BookingStatus.CANCELADA:
            booking.cancelada_at = now
            booking.motivo_cancelamento = motivo_cancelamento
        
        await db.commit()
        await db.refresh(booking)
        return booking
    
    async def list_guest_bookings(
        self,
        db: AsyncSession,
        guest_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[Booking]:
        """Lista reservas do hóspede"""
        result = await db.execute(
            select(Booking)
            .where(Booking.guest_id == guest_id)
            .options(joinedload(Booking.property))
            .order_by(Booking.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()
    
    async def list_host_bookings(
        self,
        db: AsyncSession,
        host_id: UUID,
        status: Optional[BookingStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Booking]:
        """Lista reservas das propriedades do anfitrião"""
        query = (
            select(Booking)
            .join(Property)
            .where(Property.host_id == host_id)
        )
        
        if status:
            query = query.where(Booking.status == status.value)
        
        query = query.options(
            joinedload(Booking.property),
            joinedload(Booking.guest)
        ).order_by(Booking.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.unique().scalars().all()
    
    # ============================================
    # Reviews
    # ============================================
    
    async def create_review(
        self,
        db: AsyncSession,
        booking_id: UUID,
        guest_id: UUID,
        data: dict
    ) -> PropertyReview:
        """Cria avaliação"""
        booking = await self.get_booking(db, booking_id)
        if not booking:
            raise ValueError("Reserva não encontrada")
        
        if booking.guest_id != guest_id:
            raise ValueError("Apenas o hóspede pode avaliar")
        
        if booking.status != BookingStatus.FINALIZADA.value:
            raise ValueError("Reserva não finalizada")
        
        # Verifica se já avaliou
        existing = await db.execute(
            select(PropertyReview).where(PropertyReview.booking_id == booking_id)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Já avaliou esta reserva")
        
        review = PropertyReview(
            property_id=booking.property_id,
            booking_id=booking_id,
            guest_id=guest_id,
            nota_geral=data["nota_geral"],
            nota_limpeza=data.get("nota_limpeza"),
            nota_localizacao=data.get("nota_localizacao"),
            nota_comunicacao=data.get("nota_comunicacao"),
            nota_valor=data.get("nota_valor"),
            comentario=data.get("comentario")
        )
        
        db.add(review)
        
        # Atualiza rating da propriedade
        prop = await self.get_property(db, booking.property_id)
        if prop:
            prop.total_avaliacoes += 1
            # Calcula nova média
            avg_result = await db.execute(
                select(func.avg(PropertyReview.nota_geral))
                .where(PropertyReview.property_id == prop.id)
            )
            new_avg = avg_result.scalar() or 5.0
            prop.rating_medio = Decimal(str(round(new_avg, 2)))
        
        await db.commit()
        await db.refresh(review)
        return review
    
    async def list_property_reviews(
        self,
        db: AsyncSession,
        property_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[PropertyReview]:
        """Lista avaliações de uma propriedade"""
        result = await db.execute(
            select(PropertyReview)
            .where(PropertyReview.property_id == property_id)
            .options(joinedload(PropertyReview.guest))
            .order_by(PropertyReview.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()
    
    # ============================================
    # Stats
    # ============================================
    
    async def get_host_stats(self, db: AsyncSession, host_id: UUID) -> dict:
        """Estatísticas do anfitrião"""
        # Total propriedades
        props_result = await db.execute(
            select(func.count(Property.id)).where(Property.host_id == host_id)
        )
        total_propriedades = props_result.scalar() or 0
        
        # Total reservas
        reservas_result = await db.execute(
            select(func.count(Booking.id))
            .join(Property)
            .where(Property.host_id == host_id)
        )
        total_reservas = reservas_result.scalar() or 0
        
        # Reservas pendentes
        pendentes_result = await db.execute(
            select(func.count(Booking.id))
            .join(Property)
            .where(and_(
                Property.host_id == host_id,
                Booking.status == BookingStatus.PENDENTE.value
            ))
        )
        reservas_pendentes = pendentes_result.scalar() or 0
        
        # Receita total
        receita_result = await db.execute(
            select(func.sum(Booking.total))
            .join(Property)
            .where(and_(
                Property.host_id == host_id,
                Booking.status == BookingStatus.FINALIZADA.value
            ))
        )
        receita_total = float(receita_result.scalar() or 0)
        
        # Rating médio
        rating_result = await db.execute(
            select(func.avg(Property.rating_medio))
            .where(Property.host_id == host_id)
        )
        rating_medio = float(rating_result.scalar() or 5.0)
        
        return {
            "total_propriedades": total_propriedades,
            "total_reservas": total_reservas,
            "reservas_pendentes": reservas_pendentes,
            "receita_total": receita_total,
            "receita_mes": 0,
            "rating_medio": round(rating_medio, 2)
        }


# Instância global
alojamento_service = AlojamentoService()
