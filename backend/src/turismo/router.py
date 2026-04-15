"""
TUDOaqui API - Turismo Router
"""
from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.models import User, UserRole
from src.auth.dependencies import get_current_user, require_roles
from src.turismo.models import ExperienceType, ExperienceBookingStatus
from src.turismo.schemas import (
    ExperienceCreate, ExperienceUpdate, ExperienceResponse, ExperienceListResponse,
    ScheduleCreate, ScheduleResponse,
    ExperienceBookingCreate, ExperienceBookingResponse, ExperienceBookingDetailResponse,
    BookingValidateRequest, ExperienceReviewCreate, ExperienceReviewResponse,
    TurismoHostStats
)
from src.turismo.service import turismo_service


router = APIRouter(prefix="/turismo", tags=["Turismo"])


# ============================================
# Experiences - Público
# ============================================

@router.get("/experiences", response_model=List[ExperienceListResponse])
async def list_experiences(
    cidade: Optional[str] = None,
    tipo: Optional[ExperienceType] = None,
    preco_max: Optional[float] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Lista experiências disponíveis."""
    experiences = await turismo_service.list_experiences(
        db, cidade=cidade, tipo=tipo, preco_max=preco_max, limit=limit, offset=offset
    )
    return [
        ExperienceListResponse(
            id=e.id,
            titulo=e.titulo,
            tipo=e.tipo,
            cidade=e.cidade,
            duracao_horas=e.duracao_horas,
            preco=float(e.preco),
            rating_medio=float(e.rating_medio),
            imagem_principal=e.imagens.get("urls", [None])[0] if e.imagens else None
        )
        for e in experiences
    ]


@router.get("/experiences/{experience_id}", response_model=ExperienceResponse)
async def get_experience(
    experience_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Obtém detalhes de uma experiência."""
    exp = await turismo_service.get_experience(db, experience_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiência não encontrada")
    
    return ExperienceResponse(
        id=exp.id,
        host_id=exp.host_id,
        titulo=exp.titulo,
        descricao=exp.descricao,
        tipo=exp.tipo,
        local=exp.local,
        cidade=exp.cidade,
        ponto_encontro=exp.ponto_encontro,
        latitude=float(exp.latitude) if exp.latitude else None,
        longitude=float(exp.longitude) if exp.longitude else None,
        duracao_horas=exp.duracao_horas,
        min_participantes=exp.min_participantes,
        max_participantes=exp.max_participantes,
        preco=float(exp.preco),
        preco_crianca=float(exp.preco_crianca) if exp.preco_crianca else None,
        inclui=exp.inclui.get("items", []) if exp.inclui else None,
        nao_inclui=exp.nao_inclui.get("items", []) if exp.nao_inclui else None,
        requisitos=exp.requisitos.get("items", []) if exp.requisitos else None,
        imagens=exp.imagens.get("urls", []) if exp.imagens else None,
        idiomas=exp.idiomas.get("items", []) if exp.idiomas else None,
        rating_medio=float(exp.rating_medio),
        total_reservas=exp.total_reservas,
        total_avaliacoes=exp.total_avaliacoes,
        status=exp.status,
        created_at=exp.created_at
    )


@router.get("/experiences/{experience_id}/schedules", response_model=List[ScheduleResponse])
async def list_schedules(
    experience_id: UUID,
    data_inicio: Optional[date] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lista horários disponíveis."""
    schedules = await turismo_service.list_schedules(db, experience_id, data_inicio)
    return [
        ScheduleResponse(
            id=s.id,
            experience_id=s.experience_id,
            data=s.data,
            hora_inicio=s.hora_inicio,
            vagas_disponiveis=s.vagas_disponiveis,
            vagas_reservadas=s.vagas_reservadas,
            vagas_livres=s.vagas_livres,
            preco_especial=float(s.preco_especial) if s.preco_especial else None,
            ativo=s.ativo
        )
        for s in schedules
    ]


@router.get("/experiences/{experience_id}/reviews", response_model=List[ExperienceReviewResponse])
async def list_reviews(
    experience_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Lista avaliações de uma experiência."""
    reviews = await turismo_service.list_experience_reviews(db, experience_id, limit, offset)
    return [
        ExperienceReviewResponse(
            id=r.id,
            experience_id=r.experience_id,
            user_id=r.user_id,
            nota=r.nota,
            comentario=r.comentario,
            created_at=r.created_at,
            user_nome=r.user.nome if r.user else None
        )
        for r in reviews
    ]


# ============================================
# Experiences - Gestão (Anfitrião)
# ============================================

@router.post("/experiences", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
async def create_experience(
    request: ExperienceCreate,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Cria nova experiência."""
    exp = await turismo_service.create_experience(db, current_user.id, request.model_dump())
    return await get_experience(exp.id, db)


@router.get("/experiences/my/list", response_model=List[ExperienceResponse])
async def list_my_experiences(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Lista experiências do anfitrião."""
    experiences = await turismo_service.list_host_experiences(db, current_user.id, limit, offset)
    results = []
    for exp in experiences:
        results.append(ExperienceResponse(
            id=exp.id,
            host_id=exp.host_id,
            titulo=exp.titulo,
            descricao=exp.descricao,
            tipo=exp.tipo,
            local=exp.local,
            cidade=exp.cidade,
            ponto_encontro=exp.ponto_encontro,
            latitude=float(exp.latitude) if exp.latitude else None,
            longitude=float(exp.longitude) if exp.longitude else None,
            duracao_horas=exp.duracao_horas,
            min_participantes=exp.min_participantes,
            max_participantes=exp.max_participantes,
            preco=float(exp.preco),
            preco_crianca=float(exp.preco_crianca) if exp.preco_crianca else None,
            inclui=exp.inclui.get("items", []) if exp.inclui else None,
            nao_inclui=exp.nao_inclui.get("items", []) if exp.nao_inclui else None,
            requisitos=exp.requisitos.get("items", []) if exp.requisitos else None,
            imagens=exp.imagens.get("urls", []) if exp.imagens else None,
            idiomas=exp.idiomas.get("items", []) if exp.idiomas else None,
            rating_medio=float(exp.rating_medio),
            total_reservas=exp.total_reservas,
            total_avaliacoes=exp.total_avaliacoes,
            status=exp.status,
            created_at=exp.created_at
        ))
    return results


@router.put("/experiences/{experience_id}", response_model=ExperienceResponse)
async def update_experience(
    experience_id: UUID,
    request: ExperienceUpdate,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza experiência."""
    exp = await turismo_service.get_experience(db, experience_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiência não encontrada")
    
    if exp.host_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        exp = await turismo_service.update_experience(db, experience_id, request.model_dump(exclude_unset=True))
        return await get_experience(exp.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/experiences/{experience_id}/publish", response_model=ExperienceResponse)
async def publish_experience(
    experience_id: UUID,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Publica experiência."""
    exp = await turismo_service.get_experience(db, experience_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiência não encontrada")
    
    if exp.host_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        exp = await turismo_service.publish_experience(db, experience_id)
        return await get_experience(exp.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/experiences/{experience_id}/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    experience_id: UUID,
    request: ScheduleCreate,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Cria horário para experiência."""
    exp = await turismo_service.get_experience(db, experience_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiência não encontrada")
    
    if exp.host_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        schedule = await turismo_service.create_schedule(db, experience_id, request.model_dump())
        return ScheduleResponse(
            id=schedule.id,
            experience_id=schedule.experience_id,
            data=schedule.data,
            hora_inicio=schedule.hora_inicio,
            vagas_disponiveis=schedule.vagas_disponiveis,
            vagas_reservadas=schedule.vagas_reservadas,
            vagas_livres=schedule.vagas_livres,
            preco_especial=float(schedule.preco_especial) if schedule.preco_especial else None,
            ativo=schedule.ativo
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/host/stats", response_model=TurismoHostStats)
async def get_host_stats(
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Estatísticas do anfitrião."""
    stats = await turismo_service.get_host_stats(db, current_user.id)
    return TurismoHostStats(**stats)


# ============================================
# Bookings - Usuário
# ============================================

@router.post("/bookings", response_model=ExperienceBookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    request: ExperienceBookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reserva experiência."""
    try:
        booking = await turismo_service.create_booking(db, current_user.id, request.model_dump())
        return ExperienceBookingResponse(
            id=booking.id,
            experience_id=booking.experience_id,
            schedule_id=booking.schedule_id,
            user_id=booking.user_id,
            adultos=booking.adultos,
            criancas=booking.criancas,
            preco_unitario=float(booking.preco_unitario),
            preco_crianca=float(booking.preco_crianca),
            subtotal=float(booking.subtotal),
            taxa_servico=float(booking.taxa_servico),
            total=float(booking.total),
            qr_voucher=booking.qr_voucher,
            telefone_contato=booking.telefone_contato,
            notas=booking.notas,
            status=booking.status,
            created_at=booking.created_at,
            confirmada_at=booking.confirmada_at,
            validada_at=booking.validada_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bookings/my", response_model=List[ExperienceBookingResponse])
async def list_my_bookings(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista reservas do usuário."""
    bookings = await turismo_service.list_user_bookings(db, current_user.id, limit, offset)
    return [
        ExperienceBookingResponse(
            id=b.id,
            experience_id=b.experience_id,
            schedule_id=b.schedule_id,
            user_id=b.user_id,
            adultos=b.adultos,
            criancas=b.criancas,
            preco_unitario=float(b.preco_unitario),
            preco_crianca=float(b.preco_crianca),
            subtotal=float(b.subtotal),
            taxa_servico=float(b.taxa_servico),
            total=float(b.total),
            qr_voucher=b.qr_voucher,
            telefone_contato=b.telefone_contato,
            notas=b.notas,
            status=b.status,
            created_at=b.created_at,
            confirmada_at=b.confirmada_at,
            validada_at=b.validada_at
        )
        for b in bookings
    ]


@router.post("/bookings/{booking_id}/review", response_model=ExperienceReviewResponse)
async def create_review(
    booking_id: UUID,
    request: ExperienceReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Avalia uma experiência."""
    try:
        review = await turismo_service.create_review(db, booking_id, current_user.id, request.model_dump())
        return ExperienceReviewResponse(
            id=review.id,
            experience_id=review.experience_id,
            user_id=review.user_id,
            nota=review.nota,
            comentario=review.comentario,
            created_at=review.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Bookings - Anfitrião (Check-in)
# ============================================

@router.get("/bookings/host", response_model=List[ExperienceBookingResponse])
async def list_host_bookings(
    status: Optional[ExperienceBookingStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Lista reservas das experiências do anfitrião."""
    bookings = await turismo_service.list_host_bookings(db, current_user.id, status, limit, offset)
    return [
        ExperienceBookingResponse(
            id=b.id,
            experience_id=b.experience_id,
            schedule_id=b.schedule_id,
            user_id=b.user_id,
            adultos=b.adultos,
            criancas=b.criancas,
            preco_unitario=float(b.preco_unitario),
            preco_crianca=float(b.preco_crianca),
            subtotal=float(b.subtotal),
            taxa_servico=float(b.taxa_servico),
            total=float(b.total),
            qr_voucher=b.qr_voucher,
            telefone_contato=b.telefone_contato,
            notas=b.notas,
            status=b.status,
            created_at=b.created_at,
            confirmada_at=b.confirmada_at,
            validada_at=b.validada_at
        )
        for b in bookings
    ]


@router.post("/experiences/{experience_id}/validate-voucher")
async def validate_voucher(
    experience_id: UUID,
    request: BookingValidateRequest,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Valida voucher sem usar."""
    valid, message, booking = await turismo_service.validate_voucher(db, request.qr_voucher, experience_id)
    return {
        "valid": valid,
        "message": message,
        "booking_id": str(booking.id) if booking else None
    }


@router.post("/experiences/{experience_id}/use-voucher")
async def use_voucher(
    experience_id: UUID,
    request: BookingValidateRequest,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Usa voucher (check-in)."""
    exp = await turismo_service.get_experience(db, experience_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiência não encontrada")
    
    if exp.host_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    success, message, booking = await turismo_service.use_voucher(db, request.qr_voucher, experience_id)
    
    return {
        "success": success,
        "message": message,
        "booking_id": str(booking.id) if booking else None
    }
