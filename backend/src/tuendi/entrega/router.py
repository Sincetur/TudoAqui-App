"""
TUDOaqui API - Tuendi Entrega Router
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.models import User, UserRole
from src.auth.dependencies import get_current_user, require_roles
from src.tuendi.drivers.models import Driver
from src.tuendi.entrega.models import Delivery, DeliveryStatus, DeliveryType, DeliveryPriority
from src.tuendi.entrega.schemas import (
    DeliveryEstimateRequest, DeliveryEstimateResponse,
    DeliveryCreate, DeliveryResponse, DeliveryDetailResponse, DeliveryListResponse,
    TrackingResponse, ConfirmRecolhaRequest, ConfirmEntregaRequest, UpdateLocationRequest
)
from src.tuendi.entrega.service import entrega_service
from src.tuendi.drivers.service import driver_service


router = APIRouter(prefix="/entregas", tags=["Tuendi Entrega"])


# ============================================
# Estimativa
# ============================================

@router.post("/estimate", response_model=DeliveryEstimateResponse)
async def estimate_delivery(
    request: DeliveryEstimateRequest,
    current_user: User = Depends(get_current_user)
):
    """Estima preço da entrega."""
    estimate = entrega_service.estimate_delivery(
        request.origem_latitude,
        request.origem_longitude,
        request.destino_latitude,
        request.destino_longitude,
        request.tipo,
        request.prioridade,
        request.peso_estimado
    )
    return DeliveryEstimateResponse(**estimate)


# ============================================
# Cliente - Criar e Gerir Entregas
# ============================================

@router.post("", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery(
    request: DeliveryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cria nova entrega."""
    delivery = await entrega_service.create_delivery(db, current_user.id, request.model_dump())
    return _delivery_to_response(delivery)


@router.get("/my", response_model=List[DeliveryListResponse])
async def list_my_deliveries(
    status: Optional[DeliveryStatus] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista entregas do cliente."""
    deliveries = await entrega_service.list_sender_deliveries(
        db, current_user.id, status, limit, offset
    )
    return [
        DeliveryListResponse(
            id=d.id,
            tipo=d.tipo,
            prioridade=d.prioridade,
            origem_endereco=d.origem_endereco,
            destino_endereco=d.destino_endereco,
            total=float(d.total),
            status=d.status,
            created_at=d.created_at
        )
        for d in deliveries
    ]


@router.get("/{delivery_id}", response_model=DeliveryDetailResponse)
async def get_delivery(
    delivery_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtém detalhes de uma entrega."""
    delivery = await entrega_service.get_delivery(db, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
    
    # Verifica permissão
    if delivery.sender_id != current_user.id:
        driver = await driver_service.get_driver_by_user(db, current_user.id)
        if not driver or delivery.driver_id != driver.id:
            raise HTTPException(status_code=403, detail="Acesso negado")
    
    return _delivery_to_detail_response(delivery)


@router.get("/{delivery_id}/tracking", response_model=List[TrackingResponse])
async def get_tracking(
    delivery_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtém histórico de tracking."""
    delivery = await entrega_service.get_delivery(db, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
    
    tracking = await entrega_service.get_tracking_history(db, delivery_id)
    return [
        TrackingResponse(
            id=t.id,
            status=t.status,
            descricao=t.descricao,
            latitude=float(t.latitude) if t.latitude else None,
            longitude=float(t.longitude) if t.longitude else None,
            created_at=t.created_at
        )
        for t in tracking
    ]


@router.post("/{delivery_id}/cancel")
async def cancel_delivery(
    delivery_id: UUID,
    motivo: str = Query(..., min_length=5),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancela entrega."""
    try:
        await entrega_service.cancel_delivery(db, delivery_id, current_user.id, motivo)
        return {"status": "success", "message": "Entrega cancelada"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Motorista - Gerir Entregas
# ============================================

@router.get("/driver/available", response_model=List[DeliveryListResponse])
async def list_available_deliveries(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    raio_km: float = Query(10, ge=1, le=50),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Lista entregas disponíveis próximas."""
    deliveries = await entrega_service.list_available_deliveries(
        db, latitude, longitude, raio_km, limit
    )
    return [
        DeliveryListResponse(
            id=d.id,
            tipo=d.tipo,
            prioridade=d.prioridade,
            origem_endereco=d.origem_endereco,
            destino_endereco=d.destino_endereco,
            total=float(d.total),
            status=d.status,
            created_at=d.created_at
        )
        for d in deliveries
    ]


@router.get("/driver/my", response_model=List[DeliveryListResponse])
async def list_driver_deliveries(
    status: Optional[DeliveryStatus] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Lista entregas do motorista."""
    driver = await driver_service.get_driver_by_user(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=400, detail="Perfil de motorista não encontrado")
    
    deliveries = await entrega_service.list_driver_deliveries(
        db, driver.id, status, limit, offset
    )
    return [
        DeliveryListResponse(
            id=d.id,
            tipo=d.tipo,
            prioridade=d.prioridade,
            origem_endereco=d.origem_endereco,
            destino_endereco=d.destino_endereco,
            total=float(d.total),
            status=d.status,
            created_at=d.created_at
        )
        for d in deliveries
    ]


@router.post("/{delivery_id}/accept", response_model=DeliveryResponse)
async def accept_delivery(
    delivery_id: UUID,
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Aceita entrega."""
    driver = await driver_service.get_driver_by_user(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=400, detail="Perfil de motorista não encontrado")
    
    try:
        delivery = await entrega_service.accept_delivery(db, delivery_id, driver.id)
        return _delivery_to_response(delivery)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{delivery_id}/start-pickup", response_model=DeliveryResponse)
async def start_pickup(
    delivery_id: UUID,
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Inicia ida para recolha."""
    driver = await driver_service.get_driver_by_user(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=400, detail="Perfil de motorista não encontrado")
    
    try:
        delivery = await entrega_service.start_pickup(db, delivery_id, driver.id)
        return _delivery_to_response(delivery)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{delivery_id}/confirm-pickup", response_model=DeliveryResponse)
async def confirm_pickup(
    delivery_id: UUID,
    request: ConfirmRecolhaRequest,
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Confirma recolha do pacote."""
    driver = await driver_service.get_driver_by_user(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=400, detail="Perfil de motorista não encontrado")
    
    try:
        delivery = await entrega_service.confirm_pickup(
            db, delivery_id, driver.id, request.codigo, request.foto_url
        )
        return _delivery_to_response(delivery)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{delivery_id}/start-transit", response_model=DeliveryResponse)
async def start_transit(
    delivery_id: UUID,
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Inicia trânsito para destino."""
    driver = await driver_service.get_driver_by_user(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=400, detail="Perfil de motorista não encontrado")
    
    try:
        delivery = await entrega_service.start_transit(db, delivery_id, driver.id)
        return _delivery_to_response(delivery)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{delivery_id}/confirm-delivery", response_model=DeliveryResponse)
async def confirm_delivery_endpoint(
    delivery_id: UUID,
    request: ConfirmEntregaRequest,
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Confirma entrega do pacote."""
    driver = await driver_service.get_driver_by_user(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=400, detail="Perfil de motorista não encontrado")
    
    try:
        delivery = await entrega_service.confirm_delivery(
            db, delivery_id, driver.id, request.codigo, request.foto_url
        )
        return _delivery_to_response(delivery)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{delivery_id}/location")
async def update_location(
    delivery_id: UUID,
    request: UpdateLocationRequest,
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza localização do motorista."""
    driver = await driver_service.get_driver_by_user(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=400, detail="Perfil de motorista não encontrado")
    
    await entrega_service.update_driver_location(
        db, delivery_id, driver.id, request.latitude, request.longitude
    )
    return {"status": "success"}


# ============================================
# Helpers
# ============================================

def _delivery_to_response(delivery: Delivery) -> DeliveryResponse:
    """Converte Delivery para resposta"""
    return DeliveryResponse(
        id=delivery.id,
        sender_id=delivery.sender_id,
        driver_id=delivery.driver_id,
        tipo=delivery.tipo,
        prioridade=delivery.prioridade,
        descricao=delivery.descricao,
        peso_estimado=float(delivery.peso_estimado) if delivery.peso_estimado else None,
        origem_endereco=delivery.origem_endereco,
        origem_latitude=float(delivery.origem_latitude),
        origem_longitude=float(delivery.origem_longitude),
        origem_referencia=delivery.origem_referencia,
        origem_contato_nome=delivery.origem_contato_nome,
        origem_contato_telefone=delivery.origem_contato_telefone,
        destino_endereco=delivery.destino_endereco,
        destino_latitude=float(delivery.destino_latitude),
        destino_longitude=float(delivery.destino_longitude),
        destino_referencia=delivery.destino_referencia,
        destino_contato_nome=delivery.destino_contato_nome,
        destino_contato_telefone=delivery.destino_contato_telefone,
        distancia_km=float(delivery.distancia_km),
        preco_base=float(delivery.preco_base),
        taxa_prioridade=float(delivery.taxa_prioridade),
        taxa_peso=float(delivery.taxa_peso),
        total=float(delivery.total),
        instrucoes_recolha=delivery.instrucoes_recolha,
        instrucoes_entrega=delivery.instrucoes_entrega,
        codigo_recolha=delivery.codigo_recolha,
        codigo_entrega=delivery.codigo_entrega,
        status=delivery.status,
        created_at=delivery.created_at,
        aceite_at=delivery.aceite_at,
        recolhido_at=delivery.recolhido_at,
        entregue_at=delivery.entregue_at
    )


def _delivery_to_detail_response(delivery: Delivery) -> DeliveryDetailResponse:
    """Converte Delivery para resposta detalhada"""
    base = _delivery_to_response(delivery)
    
    driver_nome = None
    driver_telefone = None
    driver_foto = None
    driver_veiculo = None
    driver_placa = None
    
    if delivery.driver:
        driver_nome = delivery.driver.user.nome if delivery.driver.user else None
        driver_telefone = delivery.driver.user.telefone if delivery.driver.user else None
        driver_foto = delivery.driver.user.avatar_url if delivery.driver.user else None
        driver_veiculo = f"{delivery.driver.marca or ''} {delivery.driver.modelo or ''}".strip() or delivery.driver.veiculo
        driver_placa = delivery.driver.matricula
    
    return DeliveryDetailResponse(
        **base.model_dump(),
        driver_nome=driver_nome,
        driver_telefone=driver_telefone,
        driver_foto=driver_foto,
        driver_veiculo=driver_veiculo,
        driver_placa=driver_placa
    )
