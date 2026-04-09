"""
TUDOaqui API - Turismo Service
"""
import hashlib
import secrets
from datetime import datetime, timezone, date
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.config import settings
from src.turismo.models import (
    Experience, ExperienceType, ExperienceStatus,
    ExperienceSchedule, ExperienceBooking, ExperienceBookingStatus,
    ExperienceReview
)


class TurismoService:
    """Serviço de Turismo"""
    
    TAXA_SERVICO_PERCENT = Decimal("0.10")
    
    @staticmethod
    def generate_qr_voucher(booking_id: UUID, experience_id: UUID) -> str:
        """Gera QR voucher único"""
        random_part = secrets.token_hex(8)
        data = f"{booking_id}:{experience_id}:{settings.SECRET_KEY}:{random_part}"
        hash_value = hashlib.sha256(data.encode()).hexdigest()[:24]
        return f"TDQ-EXP-{hash_value.upper()}"
    
    # ============================================
    # Experience Management
    # ============================================
    
    async def create_experience(
        self,
        db: AsyncSession,
        host_id: UUID,
        data: dict
    ) -> Experience:
        """Cria nova experiência"""
        experience = Experience(
            host_id=host_id,
            titulo=data["titulo"],
            descricao=data.get("descricao"),
            tipo=data.get("tipo", ExperienceType.TOUR.value),
            local=data["local"],
            cidade=data["cidade"],
            ponto_encontro=data.get("ponto_encontro"),
            latitude=Decimal(str(data["latitude"])) if data.get("latitude") else None,
            longitude=Decimal(str(data["longitude"])) if data.get("longitude") else None,
            duracao_horas=data.get("duracao_horas", 2),
            min_participantes=data.get("min_participantes", 1),
            max_participantes=data.get("max_participantes", 10),
            preco=Decimal(str(data["preco"])),
            preco_crianca=Decimal(str(data["preco_crianca"])) if data.get("preco_crianca") else None,
            inclui={"items": data.get("inclui", [])},
            nao_inclui={"items": data.get("nao_inclui", [])},
            requisitos={"items": data.get("requisitos", [])},
            imagens={"urls": data.get("imagens", [])},
            idiomas={"items": data.get("idiomas", ["Português"])},
            status=ExperienceStatus.RASCUNHO.value
        )
        
        db.add(experience)
        await db.commit()
        await db.refresh(experience)
        return experience
    
    async def get_experience(self, db: AsyncSession, experience_id: UUID) -> Experience | None:
        """Obtém experiência por ID"""
        result = await db.execute(
            select(Experience)
            .where(Experience.id == experience_id)
            .options(joinedload(Experience.host), joinedload(Experience.schedules))
        )
        return result.scalar_one_or_none()
    
    async def update_experience(
        self,
        db: AsyncSession,
        experience_id: UUID,
        data: dict
    ) -> Experience:
        """Atualiza experiência"""
        exp = await self.get_experience(db, experience_id)
        if not exp:
            raise ValueError("Experiência não encontrada")
        
        for field, value in data.items():
            if value is not None:
                if field in ["preco", "preco_crianca", "latitude", "longitude"]:
                    value = Decimal(str(value)) if value else None
                if field in ["inclui", "nao_inclui", "requisitos", "idiomas"]:
                    value = {"items": value}
                if field == "imagens":
                    value = {"urls": value}
                setattr(exp, field, value)
        
        await db.commit()
        await db.refresh(exp)
        return exp
    
    async def list_experiences(
        self,
        db: AsyncSession,
        cidade: str | None = None,
        tipo: ExperienceType | None = None,
        preco_max: float | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[Experience]:
        """Lista experiências"""
        query = select(Experience).where(
            Experience.status == ExperienceStatus.ATIVO.value,
            Experience.ativo.is_(True)
        )
        
        if cidade:
            query = query.where(Experience.cidade.ilike(f"%{cidade}%"))
        if tipo:
            query = query.where(Experience.tipo == tipo.value)
        if preco_max:
            query = query.where(Experience.preco <= preco_max)
        
        query = query.order_by(Experience.rating_medio.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def list_host_experiences(
        self,
        db: AsyncSession,
        host_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> list[Experience]:
        """Lista experiências do anfitrião"""
        result = await db.execute(
            select(Experience)
            .where(Experience.host_id == host_id)
            .order_by(Experience.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def publish_experience(self, db: AsyncSession, experience_id: UUID) -> Experience:
        """Publica experiência"""
        exp = await self.get_experience(db, experience_id)
        if not exp:
            raise ValueError("Experiência não encontrada")
        
        # Verifica se tem horários
        if not exp.schedules:
            raise ValueError("Adicione pelo menos um horário antes de publicar")
        
        exp.status = ExperienceStatus.ATIVO.value
        await db.commit()
        await db.refresh(exp)
        return exp
    
    # ============================================
    # Schedules
    # ============================================
    
    async def create_schedule(
        self,
        db: AsyncSession,
        experience_id: UUID,
        data: dict
    ) -> ExperienceSchedule:
        """Cria horário para experiência"""
        exp = await self.get_experience(db, experience_id)
        if not exp:
            raise ValueError("Experiência não encontrada")
        
        schedule = ExperienceSchedule(
            experience_id=experience_id,
            data=data["data"],
            hora_inicio=data["hora_inicio"],
            vagas_disponiveis=data["vagas_disponiveis"],
            preco_especial=Decimal(str(data["preco_especial"])) if data.get("preco_especial") else None
        )
        
        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)
        return schedule
    
    async def list_schedules(
        self,
        db: AsyncSession,
        experience_id: UUID,
        data_inicio: date | None = None
    ) -> list[ExperienceSchedule]:
        """Lista horários de uma experiência"""
        query = select(ExperienceSchedule).where(
            ExperienceSchedule.experience_id == experience_id,
            ExperienceSchedule.ativo.is_(True)
        )
        
        if data_inicio:
            query = query.where(ExperienceSchedule.data >= data_inicio)
        
        query = query.order_by(ExperienceSchedule.data, ExperienceSchedule.hora_inicio)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    # ============================================
    # Bookings
    # ============================================
    
    async def create_booking(
        self,
        db: AsyncSession,
        user_id: UUID,
        data: dict
    ) -> ExperienceBooking:
        """Cria reserva de experiência"""
        experience_id = data["experience_id"]
        schedule_id = data["schedule_id"]
        
        # Busca schedule com lock
        result = await db.execute(
            select(ExperienceSchedule)
            .where(ExperienceSchedule.id == schedule_id)
            .with_for_update()
        )
        schedule = result.scalar_one_or_none()
        
        if not schedule or schedule.experience_id != experience_id:
            raise ValueError("Horário não encontrado")
        
        if not schedule.ativo:
            raise ValueError("Horário não disponível")
        
        # Valida vagas
        total_participantes = data.get("adultos", 1) + data.get("criancas", 0)
        vagas_livres = schedule.vagas_disponiveis - schedule.vagas_reservadas
        
        if total_participantes > vagas_livres:
            raise ValueError(f"Apenas {vagas_livres} vagas disponíveis")
        
        # Busca experiência
        exp = await self.get_experience(db, experience_id)
        if not exp or exp.status != ExperienceStatus.ATIVO.value:
            raise ValueError("Experiência não disponível")
        
        # Calcula valores
        preco_unitario = schedule.preco_especial or exp.preco
        preco_crianca = exp.preco_crianca or preco_unitario
        
        subtotal_adultos = preco_unitario * data.get("adultos", 1)
        subtotal_criancas = preco_crianca * data.get("criancas", 0)
        subtotal = subtotal_adultos + subtotal_criancas
        
        taxa_servico = subtotal * self.TAXA_SERVICO_PERCENT
        total = subtotal + taxa_servico
        
        # Cria booking
        booking = ExperienceBooking(
            experience_id=experience_id,
            schedule_id=schedule_id,
            user_id=user_id,
            adultos=data.get("adultos", 1),
            criancas=data.get("criancas", 0),
            preco_unitario=preco_unitario,
            preco_crianca=preco_crianca,
            subtotal=subtotal,
            taxa_servico=taxa_servico,
            total=total,
            qr_voucher=self.generate_qr_voucher(schedule_id, experience_id),
            telefone_contato=data["telefone_contato"],
            notas=data.get("notas"),
            status=ExperienceBookingStatus.PENDENTE.value
        )
        
        db.add(booking)
        
        # Atualiza vagas
        schedule.vagas_reservadas += total_participantes
        
        # Atualiza stats
        exp.total_reservas += 1
        
        await db.commit()
        await db.refresh(booking)
        return booking
    
    async def get_booking(self, db: AsyncSession, booking_id: UUID) -> ExperienceBooking | None:
        """Obtém reserva por ID"""
        result = await db.execute(
            select(ExperienceBooking)
            .where(ExperienceBooking.id == booking_id)
            .options(
                joinedload(ExperienceBooking.experience).joinedload(Experience.host),
                joinedload(ExperienceBooking.schedule),
                joinedload(ExperienceBooking.user)
            )
        )
        return result.scalar_one_or_none()
    
    async def validate_voucher(
        self,
        db: AsyncSession,
        qr_voucher: str,
        experience_id: UUID
    ) -> tuple[bool, str, ExperienceBooking | None]:
        """Valida QR voucher"""
        result = await db.execute(
            select(ExperienceBooking)
            .where(ExperienceBooking.qr_voucher == qr_voucher)
            .options(
                joinedload(ExperienceBooking.experience),
                joinedload(ExperienceBooking.schedule)
            )
        )
        booking = result.scalar_one_or_none()
        
        if not booking:
            return False, "Voucher inválido", None
        
        if booking.experience_id != experience_id:
            return False, "Voucher não é desta experiência", None
        
        if booking.status == ExperienceBookingStatus.REALIZADA.value:
            return False, "Voucher já utilizado", booking
        
        if booking.status == ExperienceBookingStatus.CANCELADA.value:
            return False, "Reserva cancelada", booking
        
        if booking.status == ExperienceBookingStatus.NO_SHOW.value:
            return False, "Marcado como no-show", booking
        
        return True, "Voucher válido", booking
    
    async def use_voucher(
        self,
        db: AsyncSession,
        qr_voucher: str,
        experience_id: UUID
    ) -> tuple[bool, str, ExperienceBooking | None]:
        """Usa voucher (marca como realizada)"""
        valid, message, booking = await self.validate_voucher(db, qr_voucher, experience_id)
        
        if not valid:
            return False, message, booking
        
        booking.status = ExperienceBookingStatus.REALIZADA.value
        booking.validada_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(booking)
        
        return True, "Check-in realizado com sucesso", booking
    
    async def list_user_bookings(
        self,
        db: AsyncSession,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> list[ExperienceBooking]:
        """Lista reservas do usuário"""
        result = await db.execute(
            select(ExperienceBooking)
            .where(ExperienceBooking.user_id == user_id)
            .options(
                joinedload(ExperienceBooking.experience),
                joinedload(ExperienceBooking.schedule)
            )
            .order_by(ExperienceBooking.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()
    
    async def list_host_bookings(
        self,
        db: AsyncSession,
        host_id: UUID,
        status: ExperienceBookingStatus | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[ExperienceBooking]:
        """Lista reservas das experiências do anfitrião"""
        query = (
            select(ExperienceBooking)
            .join(Experience)
            .where(Experience.host_id == host_id)
        )
        
        if status:
            query = query.where(ExperienceBooking.status == status.value)
        
        query = query.options(
            joinedload(ExperienceBooking.experience),
            joinedload(ExperienceBooking.schedule),
            joinedload(ExperienceBooking.user)
        ).order_by(ExperienceBooking.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.unique().scalars().all()
    
    # ============================================
    # Reviews
    # ============================================
    
    async def create_review(
        self,
        db: AsyncSession,
        booking_id: UUID,
        user_id: UUID,
        data: dict
    ) -> ExperienceReview:
        """Cria avaliação"""
        booking = await self.get_booking(db, booking_id)
        if not booking:
            raise ValueError("Reserva não encontrada")
        
        if booking.user_id != user_id:
            raise ValueError("Apenas o participante pode avaliar")
        
        if booking.status != ExperienceBookingStatus.REALIZADA.value:
            raise ValueError("Experiência não realizada")
        
        # Verifica se já avaliou
        existing = await db.execute(
            select(ExperienceReview).where(ExperienceReview.booking_id == booking_id)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Já avaliou esta experiência")
        
        review = ExperienceReview(
            experience_id=booking.experience_id,
            booking_id=booking_id,
            user_id=user_id,
            nota=data["nota"],
            comentario=data.get("comentario")
        )
        
        db.add(review)
        
        # Atualiza rating
        exp = booking.experience
        exp.total_avaliacoes += 1
        
        avg_result = await db.execute(
            select(func.avg(ExperienceReview.nota))
            .where(ExperienceReview.experience_id == exp.id)
        )
        new_avg = avg_result.scalar() or 5.0
        exp.rating_medio = Decimal(str(round(new_avg, 2)))
        
        await db.commit()
        await db.refresh(review)
        return review
    
    async def list_experience_reviews(
        self,
        db: AsyncSession,
        experience_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> list[ExperienceReview]:
        """Lista avaliações de uma experiência"""
        result = await db.execute(
            select(ExperienceReview)
            .where(ExperienceReview.experience_id == experience_id)
            .options(joinedload(ExperienceReview.user))
            .order_by(ExperienceReview.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()
    
    # ============================================
    # Stats
    # ============================================
    
    async def get_host_stats(self, db: AsyncSession, host_id: UUID) -> dict:
        """Estatísticas do anfitrião"""
        # Total experiências
        exp_result = await db.execute(
            select(func.count(Experience.id)).where(Experience.host_id == host_id)
        )
        total_experiencias = exp_result.scalar() or 0
        
        # Total reservas
        reservas_result = await db.execute(
            select(func.count(ExperienceBooking.id))
            .join(Experience)
            .where(Experience.host_id == host_id)
        )
        total_reservas = reservas_result.scalar() or 0
        
        # Reservas pendentes
        pendentes_result = await db.execute(
            select(func.count(ExperienceBooking.id))
            .join(Experience)
            .where(and_(
                Experience.host_id == host_id,
                ExperienceBooking.status.in_([
                    ExperienceBookingStatus.PENDENTE.value,
                    ExperienceBookingStatus.CONFIRMADA.value
                ])
            ))
        )
        reservas_pendentes = pendentes_result.scalar() or 0
        
        # Receita total
        receita_result = await db.execute(
            select(func.sum(ExperienceBooking.total))
            .join(Experience)
            .where(and_(
                Experience.host_id == host_id,
                ExperienceBooking.status == ExperienceBookingStatus.REALIZADA.value
            ))
        )
        receita_total = float(receita_result.scalar() or 0)
        
        # Rating médio
        rating_result = await db.execute(
            select(func.avg(Experience.rating_medio))
            .where(Experience.host_id == host_id)
        )
        rating_medio = float(rating_result.scalar() or 5.0)
        
        return {
            "total_experiencias": total_experiencias,
            "total_reservas": total_reservas,
            "reservas_pendentes": reservas_pendentes,
            "receita_total": receita_total,
            "rating_medio": round(rating_medio, 2)
        }


# Instância global
turismo_service = TurismoService()
