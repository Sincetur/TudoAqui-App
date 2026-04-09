"""
TUDOaqui API - Rides Router
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.users.models import User, UserRole
from src.auth.dependencies import get_current_user, require_roles
from src.tuendi.rides.models import Ride, RideStatus
from src.tuendi.drivers.models import Driver
from src.tuendi.schemas import (
    RideRequestCreate,
    RideResponse,
    RideWithDriverResponse,
    RideEstimateRequest,
    RideEstimateResponse,
    RideCancelRequest,
    RatingCreate,
    RatingResponse,
    DriverPublicResponse
)
from src.tuendi.rides.service import ride_service


router = APIRouter(prefix="/rides", tags=["Tuendi - Corridas"])


# ============================================
# Endpoints do Cliente
# ============================================

@router.post("/estimate", response_model=RideEstimateResponse)
async def estimate_ride(
    request: RideEstimateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calcula estimativa de corrida (preço, distância, tempo).
    """
    return await ride_service.estimate_ride(
        db,
        request.origem.latitude,
        request.origem.longitude,
        request.destino.latitude,
        request.destino.longitude
    )


@router.post("/request", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
async def request_ride(
    request: RideRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Solicita uma nova corrida.
    """
    try:
        ride = await ride_service.request_ride(db, current_user.id, request)
        return RideResponse.model_validate(ride)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/current", response_model=RideWithDriverResponse | None)
async def get_current_ride(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém a corrida atual do utilizador (se existir).
    """
    result = await db.execute(
        select(Ride)
        .where(
            Ride.cliente_id == current_user.id,
            Ride.status.in_([
                RideStatus.SOLICITADA.value,
                RideStatus.ACEITE.value,
                RideStatus.MOTORISTA_A_CAMINHO.value,
                RideStatus.EM_CURSO.value
            ])
        )
    )
    ride = result.scalar_one_or_none()
    
    if not ride:
        return None
    
    # Busca dados completos
    ride = await ride_service.get_ride(db, ride.id)
    response = RideWithDriverResponse.model_validate(ride)
    
    # Adiciona dados do motorista se existir
    if ride.motorista:
        response.motorista = DriverPublicResponse(
            id=ride.motorista.id,
            nome=ride.motorista.user.nome,
            telefone=ride.motorista.user.telefone,
            avatar_url=ride.motorista.user.avatar_url,
            veiculo=ride.motorista.veiculo,
            matricula=ride.motorista.matricula,
            cor_veiculo=ride.motorista.cor_veiculo,
            marca=ride.motorista.marca,
            modelo=ride.motorista.modelo,
            rating_medio=float(ride.motorista.rating_medio),
            total_corridas=ride.motorista.total_corridas
        )
    
    return response


@router.get("/{ride_id}", response_model=RideWithDriverResponse)
async def get_ride(
    ride_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém detalhes de uma corrida específica.
    """
    ride = await ride_service.get_ride(db, ride_id)
    
    if not ride:
        raise HTTPException(status_code=404, detail="Corrida não encontrada")
    
    # Verifica permissão
    is_client = ride.cliente_id == current_user.id
    is_driver = ride.motorista and ride.motorista.user_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN.value
    
    if not (is_client or is_driver or is_admin):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    response = RideWithDriverResponse.model_validate(ride)
    
    if ride.motorista:
        response.motorista = DriverPublicResponse(
            id=ride.motorista.id,
            nome=ride.motorista.user.nome,
            telefone=ride.motorista.user.telefone,
            avatar_url=ride.motorista.user.avatar_url,
            veiculo=ride.motorista.veiculo,
            matricula=ride.motorista.matricula,
            cor_veiculo=ride.motorista.cor_veiculo,
            marca=ride.motorista.marca,
            modelo=ride.motorista.modelo,
            rating_medio=float(ride.motorista.rating_medio),
            total_corridas=ride.motorista.total_corridas
        )
    
    return response


@router.post("/{ride_id}/cancel", response_model=RideResponse)
async def cancel_ride(
    ride_id: UUID,
    request: RideCancelRequest = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancela uma corrida.
    """
    try:
        motivo = request.motivo if request else None
        ride = await ride_service.cancel_ride(db, ride_id, current_user.id, motivo)
        return RideResponse.model_validate(ride)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/client", response_model=list[RideResponse])
async def get_client_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista histórico de corridas do cliente.
    """
    rides = await ride_service.get_client_rides(db, current_user.id, limit, offset)
    return [RideResponse.model_validate(r) for r in rides]


@router.post("/{ride_id}/rate", response_model=RatingResponse)
async def rate_ride(
    ride_id: UUID,
    request: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Avalia uma corrida finalizada.
    """
    ride = await ride_service.get_ride(db, ride_id)
    
    if not ride:
        raise HTTPException(status_code=404, detail="Corrida não encontrada")
    
    if ride.status != RideStatus.FINALIZADA.value:
        raise HTTPException(status_code=400, detail="Corrida não finalizada")
    
    # Determina tipo de avaliação
    if ride.cliente_id == current_user.id:
        tipo = "cliente_para_motorista"
        avaliado_id = ride.motorista.user_id
    elif ride.motorista and ride.motorista.user_id == current_user.id:
        tipo = "motorista_para_cliente"
        avaliado_id = ride.cliente_id
    else:
        raise HTTPException(status_code=403, detail="Não autorizado")
    
    try:
        rating = await ride_service.add_rating(
            db,
            ride_id,
            current_user.id,
            avaliado_id,
            tipo,
            request.nota,
            request.comentario
        )
        return RatingResponse.model_validate(rating)
    except Exception:
        raise HTTPException(status_code=400, detail="Avaliação já realizada")


# ============================================
# Endpoints do Motorista
# ============================================

@router.get("/pending/nearby", response_model=list[RideResponse])
async def get_pending_rides(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista corridas pendentes próximas ao motorista.
    """
    rides = await ride_service.get_pending_rides(db, latitude, longitude)
    return [RideResponse.model_validate(r) for r in rides]


@router.post("/{ride_id}/accept", response_model=RideResponse)
async def accept_ride(
    ride_id: UUID,
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Motorista aceita uma corrida.
    """
    # Busca driver do utilizador
    result = await db.execute(
        select(Driver).where(Driver.user_id == current_user.id)
    )
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(status_code=400, detail="Perfil de motorista não encontrado")
    
    if not driver.online:
        raise HTTPException(status_code=400, detail="Motorista offline")
    
    try:
        ride = await ride_service.accept_ride(db, ride_id, driver.id)
        return RideResponse.model_validate(ride)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{ride_id}/start", response_model=RideResponse)
async def start_ride(
    ride_id: UUID,
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia a corrida (motorista chegou ao cliente).
    """
    ride = await ride_service.get_ride(db, ride_id)
    
    if not ride:
        raise HTTPException(status_code=404, detail="Corrida não encontrada")
    
    if ride.motorista.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        ride = await ride_service.start_ride(db, ride_id)
        return RideResponse.model_validate(ride)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{ride_id}/finish", response_model=RideResponse)
async def finish_ride(
    ride_id: UUID,
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Finaliza a corrida.
    """
    ride = await ride_service.get_ride(db, ride_id)
    
    if not ride:
        raise HTTPException(status_code=404, detail="Corrida não encontrada")
    
    if ride.motorista.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        ride = await ride_service.finish_ride(db, ride_id)
        return RideResponse.model_validate(ride)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/driver", response_model=list[RideResponse])
async def get_driver_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista histórico de corridas do motorista.
    """
    # Busca driver
    result = await db.execute(
        select(Driver).where(Driver.user_id == current_user.id)
    )
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(status_code=400, detail="Perfil de motorista não encontrado")
    
    rides = await ride_service.get_driver_rides(db, driver.id, limit, offset)
    return [RideResponse.model_validate(r) for r in rides]
