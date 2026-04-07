"""
TUDOaqui API - Drivers Router
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.models import User, UserRole
from src.auth.dependencies import get_current_user, require_roles
from src.tuendi.drivers.models import Driver, DriverStatus
from src.tuendi.schemas import (
    DriverCreate,
    DriverUpdate,
    DriverResponse,
    DriverOnlineUpdate,
    DriverLocationUpdate,
    DriverStats
)
from src.tuendi.drivers.service import driver_service


router = APIRouter(prefix="/drivers", tags=["Tuendi - Motoristas"])


# ============================================
# Endpoints Públicos / Cliente
# ============================================

@router.post("/register", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def register_driver(
    request: DriverCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Regista-se como motorista.
    Cria perfil de motorista com status 'pendente' (aguarda aprovação).
    """
    try:
        driver = await driver_service.register_driver(db, current_user.id, request)
        return DriverResponse.model_validate(driver)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=DriverResponse)
async def get_my_driver_profile(
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém o próprio perfil de motorista.
    """
    driver = await driver_service.get_driver_by_user(db, current_user.id)
    
    if not driver:
        raise HTTPException(status_code=404, detail="Perfil de motorista não encontrado")
    
    return DriverResponse.model_validate(driver)


@router.put("/me", response_model=DriverResponse)
async def update_my_driver_profile(
    request: DriverUpdate,
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza o próprio perfil de motorista.
    """
    driver = await driver_service.get_driver_by_user(db, current_user.id)
    
    if not driver:
        raise HTTPException(status_code=404, detail="Perfil de motorista não encontrado")
    
    try:
        driver = await driver_service.update_driver(db, driver.id, request)
        return DriverResponse.model_validate(driver)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/me/online", response_model=DriverResponse)
async def set_online_status(
    request: DriverOnlineUpdate,
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Define status online/offline do motorista.
    
    - **online**: true para ficar disponível, false para ficar offline
    - **latitude/longitude**: obrigatórios quando online=true
    """
    driver = await driver_service.get_driver_by_user(db, current_user.id)
    
    if not driver:
        raise HTTPException(status_code=404, detail="Perfil de motorista não encontrado")
    
    try:
        driver = await driver_service.update_online_status(db, driver.id, request)
        return DriverResponse.model_validate(driver)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/me/location", response_model=DriverResponse)
async def update_location(
    request: DriverLocationUpdate,
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza localização do motorista (usado para tracking contínuo).
    """
    driver = await driver_service.get_driver_by_user(db, current_user.id)
    
    if not driver:
        raise HTTPException(status_code=404, detail="Perfil de motorista não encontrado")
    
    try:
        driver = await driver_service.update_location(
            db, driver.id, request.latitude, request.longitude
        )
        return DriverResponse.model_validate(driver)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me/stats", response_model=DriverStats)
async def get_my_stats(
    current_user: User = Depends(require_roles(UserRole.MOTORISTA, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém estatísticas do motorista (corridas, ganhos, rating).
    """
    driver = await driver_service.get_driver_by_user(db, current_user.id)
    
    if not driver:
        raise HTTPException(status_code=404, detail="Perfil de motorista não encontrado")
    
    try:
        stats = await driver_service.get_driver_stats(db, driver.id)
        return DriverStats(**stats)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Endpoints Admin
# ============================================

@router.get("", response_model=list[DriverResponse])
async def list_drivers(
    status: DriverStatus | None = None,
    online: bool | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista motoristas (admin).
    """
    drivers = await driver_service.list_drivers(db, status, online, limit, offset)
    return [DriverResponse.model_validate(d) for d in drivers]


@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(
    driver_id: UUID,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém motorista por ID (admin).
    """
    driver = await driver_service.get_driver(db, driver_id)
    
    if not driver:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")
    
    return DriverResponse.model_validate(driver)


@router.post("/{driver_id}/approve", response_model=DriverResponse)
async def approve_driver(
    driver_id: UUID,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Aprova motorista (admin).
    """
    try:
        driver = await driver_service.approve_driver(db, driver_id)
        return DriverResponse.model_validate(driver)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{driver_id}/suspend", response_model=DriverResponse)
async def suspend_driver(
    driver_id: UUID,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Suspende motorista (admin).
    """
    try:
        driver = await driver_service.suspend_driver(db, driver_id)
        return DriverResponse.model_validate(driver)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
