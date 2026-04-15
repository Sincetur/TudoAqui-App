"""
TUDOaqui API - Auth Router
"""
import phonenumbers
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.config import settings
from src.users.models import User
from src.users.schemas import (
    LoginRequest, 
    AdminLoginRequest,
    OTPVerifyRequest, 
    TokenResponse, 
    RefreshTokenRequest,
    OTPSentResponse,
    UserResponse,
    MessageResponse
)
from src.auth.service import auth_service
from src.auth.dependencies import get_current_user
from src.auth.rate_limiter import rate_limiter


router = APIRouter(prefix="/auth", tags=["Autenticação"])


def validate_and_format_phone(telefone: str) -> str:
    """Valida e formata número de telefone angolano"""
    telefone = telefone.strip()
    
    # Se não tem código de país, assume Angola
    if not telefone.startswith("+"):
        telefone = f"+244{telefone.lstrip('0')}"
    
    try:
        parsed = phonenumbers.parse(telefone, "AO")
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Número inválido")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de telefone inválido. Use: +244XXXXXXXXX"
        )


@router.post("/login", response_model=OTPSentResponse)
async def login(
    request: LoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia o processo de login enviando OTP para o telefone.
    
    - **telefone**: Número de telefone com código do país (+244...)
    
    Rate limit: 5 tentativas por minuto por IP
    """
    # Rate limiting por IP
    client_ip = req.client.host if req.client else "unknown"
    if not await rate_limiter.check_rate_limit(f"login:{client_ip}", limit=5, window=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas. Aguarde 1 minuto."
        )
    
    # Valida e formata telefone
    telefone = validate_and_format_phone(request.telefone)
    
    # Rate limiting por telefone (anti-spam SMS)
    if not await rate_limiter.check_rate_limit(f"otp:{telefone}", limit=3, window=300):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitos OTPs solicitados. Aguarde 5 minutos."
        )
    
    # Envia OTP
    await auth_service.send_otp(db, telefone)
    
    return OTPSentResponse(
        telefone=telefone,
        expires_in_seconds=settings.OTP_EXPIRE_MINUTES * 60
    )


@router.post("/admin-login", response_model=TokenResponse)
async def admin_login(
    request: AdminLoginRequest,
    req: Request,
    user_agent: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Login de administrador por telefone + password.
    
    - **telefone**: Numero de telefone do admin (+244...)
    - **password**: Password do admin
    """
    client_ip = req.client.host if req.client else "unknown"
    if not await rate_limiter.check_rate_limit(f"admin-login:{client_ip}", limit=5, window=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas. Aguarde 1 minuto."
        )
    
    telefone = validate_and_format_phone(request.telefone)
    
    user = await auth_service.authenticate_admin(db, telefone, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas ou utilizador nao e admin"
        )
    
    access_token, expires = auth_service.create_access_token(user.id, user.role)
    refresh = await auth_service.create_refresh_token(db, user.id, user_agent)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh.token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    request: OTPVerifyRequest,
    req: Request,
    user_agent: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica o código OTP e retorna tokens de acesso.
    
    - **telefone**: Número de telefone
    - **codigo**: Código OTP recebido por SMS
    
    Rate limit: 10 tentativas por minuto por IP
    """
    # Rate limiting por IP
    client_ip = req.client.host if req.client else "unknown"
    if not await rate_limiter.check_rate_limit(f"verify:{client_ip}", limit=10, window=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas. Aguarde 1 minuto."
        )
    
    # Valida e formata telefone
    telefone = validate_and_format_phone(request.telefone)
    
    # Verifica OTP
    otp = await auth_service.verify_otp(db, telefone, request.codigo)
    
    if not otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código inválido ou expirado"
        )
    
    # Obtém ou cria utilizador
    user, is_new = await auth_service.get_or_create_user(db, telefone)
    
    # Gera tokens
    access_token, expires = auth_service.create_access_token(user.id, user.role)
    refresh = await auth_service.create_refresh_token(db, user.id, user_agent)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh.token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Renova o access token usando o refresh token.
    """
    # Valida refresh token
    refresh = await auth_service.validate_refresh_token(db, request.refresh_token)
    
    if not refresh:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado"
        )
    
    # Obtém utilizador
    result = await db.execute(
        select(User).where(User.id == refresh.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilizador não encontrado"
        )
    
    # Revoga token antigo
    await auth_service.revoke_refresh_token(db, request.refresh_token)
    
    # Gera novos tokens
    access_token, expires = auth_service.create_access_token(user.id, user.role)
    new_refresh = await auth_service.create_refresh_token(db, user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh.token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Faz logout revogando o refresh token atual.
    """
    await auth_service.revoke_refresh_token(db, request.refresh_token)
    
    return MessageResponse(message="Logout realizado com sucesso")


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Faz logout de todos os dispositivos.
    """
    count = await auth_service.revoke_all_tokens(db, current_user.id)
    
    return MessageResponse(
        message=f"Logout realizado em {count} dispositivo(s)"
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Retorna os dados do utilizador autenticado.
    """
    return UserResponse.model_validate(current_user)
