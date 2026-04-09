"""
TUDOaqui API - Alojamento Router
"""
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.models import User, UserRole
from src.auth.dependencies import get_current_user, require_roles
from src.alojamento.models import PropertyType, PropertyStatus, BookingStatus
from src.alojamento.schemas import (
    PropertyCreate, PropertyUpdate, PropertyResponse, PropertyListResponse,
    AvailabilityUpdate, AvailabilityResponse,
    BookingCreate, BookingResponse, BookingDetailResponse, BookingStatusUpdate,
    ReviewCreate, ReviewResponse,
    HostStats
)
from src.alojamento.service import alojamento_service


router = APIRouter(prefix="/alojamento", tags=["Alojamento"])


# ============================================
# Properties - Público
# ============================================

@router.get("/properties", response_model=list[PropertyListResponse])
async def list_properties(
    cidade: str | None = None,
    provincia: str | None = None,
    tipo: PropertyType | None = None,
    hospedes: int | None = None,
    preco_min: float | None = None,
    preco_max: float | None = None,
    quartos_min: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Lista propriedades disponíveis."""
    properties = await alojamento_service.list_properties(
        db, cidade=cidade, provincia=provincia, tipo=tipo,
        hospedes=hospedes, preco_min=preco_min, preco_max=preco_max,
        quartos_min=quartos_min, limit=limit, offset=offset
    )
    return [
        PropertyListResponse(
            id=p.id,
            titulo=p.titulo,
            tipo=p.tipo,
            cidade=p.cidade,
            provincia=p.provincia,
            preco_noite=float(p.preco_noite),
            quartos=p.quartos,
            max_hospedes=p.max_hospedes,
            rating_medio=float(p.rating_medio),
            imagem_principal=p.imagens.get("urls", [None])[0] if p.imagens else None
        )
        for p in properties
    ]


@router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Obtém detalhes de uma propriedade."""
    prop = await alojamento_service.get_property(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
    
    return PropertyResponse(
        id=prop.id,
        host_id=prop.host_id,
        titulo=prop.titulo,
        descricao=prop.descricao,
        tipo=prop.tipo,
        endereco=prop.endereco,
        cidade=prop.cidade,
        provincia=prop.provincia,
        latitude=float(prop.latitude) if prop.latitude else None,
        longitude=float(prop.longitude) if prop.longitude else None,
        quartos=prop.quartos,
        camas=prop.camas,
        banheiros=prop.banheiros,
        max_hospedes=prop.max_hospedes,
        preco_noite=float(prop.preco_noite),
        preco_limpeza=float(prop.preco_limpeza),
        desconto_semanal=prop.desconto_semanal,
        desconto_mensal=prop.desconto_mensal,
        min_noites=prop.min_noites,
        max_noites=prop.max_noites,
        checkin_hora=prop.checkin_hora,
        checkout_hora=prop.checkout_hora,
        comodidades=prop.comodidades.get("items", []) if prop.comodidades else None,
        imagens=prop.imagens.get("urls", []) if prop.imagens else None,
        rating_medio=float(prop.rating_medio),
        total_reservas=prop.total_reservas,
        total_avaliacoes=prop.total_avaliacoes,
        status=prop.status,
        created_at=prop.created_at
    )


@router.get("/properties/{property_id}/availability")
async def check_availability(
    property_id: UUID,
    checkin: date,
    checkout: date,
    db: AsyncSession = Depends(get_db)
):
    """Verifica disponibilidade de datas."""
    prop = await alojamento_service.get_property(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
    
    disponivel, blocked_dates = await alojamento_service.check_availability(
        db, property_id, checkin, checkout
    )
    
    return {
        "disponivel": disponivel,
        "datas_indisponiveis": [d.isoformat() for d in blocked_dates]
    }


@router.get("/properties/{property_id}/reviews", response_model=list[ReviewResponse])
async def list_property_reviews(
    property_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Lista avaliações de uma propriedade."""
    reviews = await alojamento_service.list_property_reviews(db, property_id, limit, offset)
    return [
        ReviewResponse(
            id=r.id,
            property_id=r.property_id,
            guest_id=r.guest_id,
            nota_geral=r.nota_geral,
            nota_limpeza=r.nota_limpeza,
            nota_localizacao=r.nota_localizacao,
            nota_comunicacao=r.nota_comunicacao,
            nota_valor=r.nota_valor,
            comentario=r.comentario,
            created_at=r.created_at,
            guest_nome=r.guest.nome if r.guest else None
        )
        for r in reviews
    ]


# ============================================
# Properties - Gestão (Anfitrião)
# ============================================

@router.post("/properties", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    request: PropertyCreate,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Cria nova propriedade."""
    prop = await alojamento_service.create_property(db, current_user.id, request.model_dump())
    return await get_property(prop.id, db)


@router.get("/properties/my/list", response_model=list[PropertyResponse])
async def list_my_properties(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Lista propriedades do anfitrião."""
    properties = await alojamento_service.list_host_properties(db, current_user.id, limit, offset)
    results = []
    for prop in properties:
        results.append(PropertyResponse(
            id=prop.id,
            host_id=prop.host_id,
            titulo=prop.titulo,
            descricao=prop.descricao,
            tipo=prop.tipo,
            endereco=prop.endereco,
            cidade=prop.cidade,
            provincia=prop.provincia,
            latitude=float(prop.latitude) if prop.latitude else None,
            longitude=float(prop.longitude) if prop.longitude else None,
            quartos=prop.quartos,
            camas=prop.camas,
            banheiros=prop.banheiros,
            max_hospedes=prop.max_hospedes,
            preco_noite=float(prop.preco_noite),
            preco_limpeza=float(prop.preco_limpeza),
            desconto_semanal=prop.desconto_semanal,
            desconto_mensal=prop.desconto_mensal,
            min_noites=prop.min_noites,
            max_noites=prop.max_noites,
            checkin_hora=prop.checkin_hora,
            checkout_hora=prop.checkout_hora,
            comodidades=prop.comodidades.get("items", []) if prop.comodidades else None,
            imagens=prop.imagens.get("urls", []) if prop.imagens else None,
            rating_medio=float(prop.rating_medio),
            total_reservas=prop.total_reservas,
            total_avaliacoes=prop.total_avaliacoes,
            status=prop.status,
            created_at=prop.created_at
        ))
    return results


@router.put("/properties/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: UUID,
    request: PropertyUpdate,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza propriedade."""
    prop = await alojamento_service.get_property(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
    
    if prop.host_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        prop = await alojamento_service.update_property(db, property_id, request.model_dump(exclude_unset=True))
        return await get_property(prop.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/properties/{property_id}/publish", response_model=PropertyResponse)
async def publish_property(
    property_id: UUID,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Publica propriedade."""
    prop = await alojamento_service.get_property(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
    
    if prop.host_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    prop = await alojamento_service.publish_property(db, property_id)
    return await get_property(prop.id, db)


@router.put("/properties/{property_id}/availability")
async def update_availability(
    property_id: UUID,
    request: AvailabilityUpdate,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza disponibilidade de datas."""
    prop = await alojamento_service.get_property(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
    
    if prop.host_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    await alojamento_service.update_availability(
        db, property_id,
        request.data_inicio, request.data_fim,
        request.disponivel, request.preco_especial, request.motivo_bloqueio
    )
    
    return {"status": "success", "message": "Disponibilidade atualizada"}


@router.get("/host/stats", response_model=HostStats)
async def get_host_stats(
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Obtém estatísticas do anfitrião."""
    stats = await alojamento_service.get_host_stats(db, current_user.id)
    return HostStats(**stats)


# ============================================
# Bookings - Hóspede
# ============================================

@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    request: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cria reserva."""
    try:
        booking = await alojamento_service.create_booking(db, current_user.id, request.model_dump())
        return BookingResponse(
            id=booking.id,
            property_id=booking.property_id,
            guest_id=booking.guest_id,
            data_checkin=booking.data_checkin,
            data_checkout=booking.data_checkout,
            noites=booking.noites,
            adultos=booking.adultos,
            criancas=booking.criancas,
            preco_noite=float(booking.preco_noite),
            subtotal=float(booking.subtotal),
            taxa_limpeza=float(booking.taxa_limpeza),
            taxa_servico=float(booking.taxa_servico),
            desconto=float(booking.desconto),
            total=float(booking.total),
            telefone_contato=booking.telefone_contato,
            notas=booking.notas,
            status=booking.status,
            created_at=booking.created_at,
            confirmada_at=booking.confirmada_at,
            checkin_at=booking.checkin_at,
            checkout_at=booking.checkout_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bookings/my", response_model=list[BookingResponse])
async def list_my_bookings(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista reservas do hóspede."""
    bookings = await alojamento_service.list_guest_bookings(db, current_user.id, limit, offset)
    return [
        BookingResponse(
            id=b.id,
            property_id=b.property_id,
            guest_id=b.guest_id,
            data_checkin=b.data_checkin,
            data_checkout=b.data_checkout,
            noites=b.noites,
            adultos=b.adultos,
            criancas=b.criancas,
            preco_noite=float(b.preco_noite),
            subtotal=float(b.subtotal),
            taxa_limpeza=float(b.taxa_limpeza),
            taxa_servico=float(b.taxa_servico),
            desconto=float(b.desconto),
            total=float(b.total),
            telefone_contato=b.telefone_contato,
            notas=b.notas,
            status=b.status,
            created_at=b.created_at,
            confirmada_at=b.confirmada_at,
            checkin_at=b.checkin_at,
            checkout_at=b.checkout_at
        )
        for b in bookings
    ]


@router.post("/bookings/{booking_id}/review", response_model=ReviewResponse)
async def create_review(
    booking_id: UUID,
    request: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Avalia uma estadia."""
    try:
        review = await alojamento_service.create_review(db, booking_id, current_user.id, request.model_dump())
        return ReviewResponse(
            id=review.id,
            property_id=review.property_id,
            guest_id=review.guest_id,
            nota_geral=review.nota_geral,
            nota_limpeza=review.nota_limpeza,
            nota_localizacao=review.nota_localizacao,
            nota_comunicacao=review.nota_comunicacao,
            nota_valor=review.nota_valor,
            comentario=review.comentario,
            created_at=review.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Bookings - Anfitrião
# ============================================

@router.get("/bookings/host", response_model=list[BookingResponse])
async def list_host_bookings(
    status: BookingStatus | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Lista reservas das propriedades do anfitrião."""
    bookings = await alojamento_service.list_host_bookings(db, current_user.id, status, limit, offset)
    return [
        BookingResponse(
            id=b.id,
            property_id=b.property_id,
            guest_id=b.guest_id,
            data_checkin=b.data_checkin,
            data_checkout=b.data_checkout,
            noites=b.noites,
            adultos=b.adultos,
            criancas=b.criancas,
            preco_noite=float(b.preco_noite),
            subtotal=float(b.subtotal),
            taxa_limpeza=float(b.taxa_limpeza),
            taxa_servico=float(b.taxa_servico),
            desconto=float(b.desconto),
            total=float(b.total),
            telefone_contato=b.telefone_contato,
            notas=b.notas,
            status=b.status,
            created_at=b.created_at,
            confirmada_at=b.confirmada_at,
            checkin_at=b.checkin_at,
            checkout_at=b.checkout_at
        )
        for b in bookings
    ]


@router.put("/bookings/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: UUID,
    request: BookingStatusUpdate,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza status da reserva."""
    booking = await alojamento_service.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    if booking.property.host_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        booking = await alojamento_service.update_booking_status(
            db, booking_id, request.status, request.motivo_cancelamento
        )
        return BookingResponse(
            id=booking.id,
            property_id=booking.property_id,
            guest_id=booking.guest_id,
            data_checkin=booking.data_checkin,
            data_checkout=booking.data_checkout,
            noites=booking.noites,
            adultos=booking.adultos,
            criancas=booking.criancas,
            preco_noite=float(booking.preco_noite),
            subtotal=float(booking.subtotal),
            taxa_limpeza=float(booking.taxa_limpeza),
            taxa_servico=float(booking.taxa_servico),
            desconto=float(booking.desconto),
            total=float(booking.total),
            telefone_contato=booking.telefone_contato,
            notas=booking.notas,
            status=booking.status,
            created_at=booking.created_at,
            confirmada_at=booking.confirmada_at,
            checkin_at=booking.checkin_at,
            checkout_at=booking.checkout_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
