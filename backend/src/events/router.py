"""
TUDOaqui API - Events Router
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.models import User, UserRole
from src.auth.dependencies import get_current_user, require_roles
from src.events.models import EventStatus
from src.events.schemas import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventDetailResponse,
    TicketTypeCreate,
    TicketTypeUpdate,
    TicketTypeResponse,
    TicketPurchaseRequest,
    TicketResponse,
    TicketDetailResponse,
    CheckInRequest,
    CheckInResponse,
    EventStats
)
from src.events.service import event_service


router = APIRouter(prefix="/events", tags=["Eventos"])


# ============================================
# Eventos Públicos
# ============================================

@router.get("", response_model=list[EventResponse])
async def list_events(
    categoria: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista eventos públicos ativos.
    """
    events = await event_service.list_events(
        db, 
        status=EventStatus.ATIVO,
        categoria=categoria,
        limit=limit, 
        offset=offset
    )
    return [EventResponse.model_validate(e) for e in events]


@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém detalhes de um evento específico.
    """
    event = await event_service.get_event(db, event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Monta resposta com ticket types
    response = EventDetailResponse.model_validate(event)
    response.ticket_types = [
        TicketTypeResponse(
            id=tt.id,
            event_id=tt.event_id,
            nome=tt.nome,
            descricao=tt.descricao,
            preco=float(tt.preco),
            quantidade_total=tt.quantidade_total,
            quantidade_vendida=tt.quantidade_vendida,
            quantidade_disponivel=tt.quantidade_disponivel,
            max_por_compra=tt.max_por_compra,
            ativo=tt.ativo
        )
        for tt in event.ticket_types if tt.ativo
    ]
    
    # Estatísticas básicas
    stats = await event_service.get_event_stats(db, event_id)
    response.total_vendido = stats["total_tickets_vendidos"]
    response.receita_total = stats["receita_total"]
    
    return response


# ============================================
# Gestão de Eventos (Organizador)
# ============================================

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    request: EventCreate,
    current_user: User = Depends(require_roles(UserRole.ORGANIZADOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria novo evento (organizadores e admins).
    """
    event = await event_service.create_event(
        db, 
        current_user.id, 
        request.model_dump()
    )
    return EventResponse.model_validate(event)


@router.get("/my/events", response_model=list[EventResponse])
async def list_my_events(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.ORGANIZADOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista eventos do organizador autenticado.
    """
    events = await event_service.list_organizer_events(
        db, current_user.id, limit, offset
    )
    return [EventResponse.model_validate(e) for e in events]


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    request: EventUpdate,
    current_user: User = Depends(require_roles(UserRole.ORGANIZADOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza evento.
    """
    event = await event_service.get_event(db, event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Verifica permissão
    if event.organizer_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        event = await event_service.update_event(
            db, event_id, request.model_dump(exclude_unset=True)
        )
        return EventResponse.model_validate(event)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{event_id}/publish", response_model=EventResponse)
async def publish_event(
    event_id: UUID,
    current_user: User = Depends(require_roles(UserRole.ORGANIZADOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Publica evento (torna visível ao público).
    """
    event = await event_service.get_event(db, event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if event.organizer_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        event = await event_service.publish_event(db, event_id)
        return EventResponse.model_validate(event)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{event_id}/cancel", response_model=EventResponse)
async def cancel_event(
    event_id: UUID,
    current_user: User = Depends(require_roles(UserRole.ORGANIZADOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancela evento.
    """
    event = await event_service.get_event(db, event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if event.organizer_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        event = await event_service.cancel_event(db, event_id)
        return EventResponse.model_validate(event)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{event_id}/stats", response_model=EventStats)
async def get_event_stats(
    event_id: UUID,
    current_user: User = Depends(require_roles(UserRole.ORGANIZADOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém estatísticas do evento.
    """
    event = await event_service.get_event(db, event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if event.organizer_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    stats = await event_service.get_event_stats(db, event_id)
    return EventStats(**stats)


# ============================================
# Ticket Types
# ============================================

@router.post("/{event_id}/ticket-types", response_model=TicketTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket_type(
    event_id: UUID,
    request: TicketTypeCreate,
    current_user: User = Depends(require_roles(UserRole.ORGANIZADOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria tipo de ticket para evento.
    """
    event = await event_service.get_event(db, event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    if event.organizer_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        ticket_type = await event_service.create_ticket_type(
            db, event_id, request.model_dump()
        )
        return TicketTypeResponse(
            id=ticket_type.id,
            event_id=ticket_type.event_id,
            nome=ticket_type.nome,
            descricao=ticket_type.descricao,
            preco=float(ticket_type.preco),
            quantidade_total=ticket_type.quantidade_total,
            quantidade_vendida=ticket_type.quantidade_vendida,
            quantidade_disponivel=ticket_type.quantidade_disponivel,
            max_por_compra=ticket_type.max_por_compra,
            ativo=ticket_type.ativo
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/ticket-types/{ticket_type_id}", response_model=TicketTypeResponse)
async def update_ticket_type(
    ticket_type_id: UUID,
    request: TicketTypeUpdate,
    current_user: User = Depends(require_roles(UserRole.ORGANIZADOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza tipo de ticket.
    """
    try:
        ticket_type = await event_service.update_ticket_type(
            db, ticket_type_id, request.model_dump(exclude_unset=True)
        )
        return TicketTypeResponse(
            id=ticket_type.id,
            event_id=ticket_type.event_id,
            nome=ticket_type.nome,
            descricao=ticket_type.descricao,
            preco=float(ticket_type.preco),
            quantidade_total=ticket_type.quantidade_total,
            quantidade_vendida=ticket_type.quantidade_vendida,
            quantidade_disponivel=ticket_type.quantidade_disponivel,
            max_por_compra=ticket_type.max_por_compra,
            ativo=ticket_type.ativo
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Compra de Tickets
# ============================================

@router.post("/tickets/purchase", response_model=list[TicketResponse], status_code=status.HTTP_201_CREATED)
async def purchase_tickets(
    request: TicketPurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Compra tickets para um evento.
    
    Nota: Em produção, isto deve integrar com o módulo de pagamentos.
    """
    try:
        tickets = await event_service.purchase_tickets(
            db,
            current_user.id,
            request.ticket_type_id,
            request.quantidade
        )
        return [TicketResponse.model_validate(t) for t in tickets]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tickets/my", response_model=list[TicketResponse])
async def get_my_tickets(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista tickets do usuário autenticado.
    """
    tickets = await event_service.get_user_tickets(
        db, current_user.id, limit, offset
    )
    return [TicketResponse.model_validate(t) for t in tickets]


# ============================================
# Check-in (Staff)
# ============================================

@router.post("/{event_id}/checkin", response_model=CheckInResponse)
async def checkin_ticket(
    event_id: UUID,
    request: CheckInRequest,
    current_user: User = Depends(require_roles(UserRole.STAFF, UserRole.ORGANIZADOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Realiza check-in de ticket via QR code.
    
    Para staff, organizadores e admins.
    """
    success, message, checkin = await event_service.checkin_ticket(
        db,
        request.qr_code,
        event_id,
        current_user.id,
        request.device_info
    )
    
    if not success:
        return CheckInResponse(
            success=False,
            message=message,
            ticket=None
        )
    
    # Busca detalhes do ticket
    ticket = checkin.ticket
    ticket_detail = TicketDetailResponse(
        id=ticket.id,
        ticket_type_id=ticket.ticket_type_id,
        buyer_id=ticket.buyer_id,
        qr_code=ticket.qr_code,
        status=ticket.status,
        created_at=ticket.created_at,
        used_at=ticket.used_at,
        event_titulo=ticket.ticket_type.event.titulo,
        event_data=ticket.ticket_type.event.data_evento,
        event_hora=ticket.ticket_type.event.hora_evento,
        event_local=ticket.ticket_type.event.local,
        ticket_type_nome=ticket.ticket_type.nome,
        ticket_type_preco=float(ticket.ticket_type.preco)
    )
    
    return CheckInResponse(
        success=True,
        message=message,
        ticket=ticket_detail,
        checkin_id=checkin.id,
        scanned_at=checkin.scanned_at
    )


@router.post("/{event_id}/validate-qr")
async def validate_qr(
    event_id: UUID,
    request: CheckInRequest,
    current_user: User = Depends(require_roles(UserRole.STAFF, UserRole.ORGANIZADOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Valida QR code sem fazer check-in.
    """
    valid, message, ticket = await event_service.validate_qr_code(
        db, request.qr_code, event_id
    )
    
    return {
        "valid": valid,
        "message": message,
        "ticket_id": str(ticket.id) if ticket else None
    }
