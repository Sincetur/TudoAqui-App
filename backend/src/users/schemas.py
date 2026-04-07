"""
TUDOaqui API - User Schemas
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from src.users.models import UserRole, UserStatus


# ============================================
# User Schemas
# ============================================

class UserBase(BaseModel):
    """Schema base de utilizador"""
    telefone: str = Field(..., min_length=9, max_length=20, examples=["+244923456789"])
    nome: str | None = Field(None, max_length=120, examples=["João Silva"])
    email: str | None = Field(None, max_length=150, examples=["joao@email.com"])


class UserCreate(UserBase):
    """Schema para criar utilizador"""
    role: UserRole = UserRole.CLIENTE


class UserUpdate(BaseModel):
    """Schema para atualizar utilizador"""
    nome: str | None = Field(None, max_length=120)
    email: str | None = Field(None, max_length=150)
    avatar_url: str | None = None


class UserResponse(UserBase):
    """Schema de resposta de utilizador"""
    id: UUID
    role: UserRole
    status: UserStatus
    avatar_url: str | None = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserProfile(UserResponse):
    """Schema de perfil completo"""
    updated_at: datetime


# ============================================
# Auth Schemas
# ============================================

class LoginRequest(BaseModel):
    """Request para iniciar login"""
    telefone: str = Field(..., min_length=9, max_length=20, examples=["+244923456789"])


class OTPVerifyRequest(BaseModel):
    """Request para verificar OTP"""
    telefone: str = Field(..., min_length=9, max_length=20)
    codigo: str = Field(..., min_length=4, max_length=6, examples=["123456"])


class TokenResponse(BaseModel):
    """Response com tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Request para refresh token"""
    refresh_token: str


class OTPSentResponse(BaseModel):
    """Response quando OTP é enviado"""
    message: str = "OTP enviado com sucesso"
    telefone: str
    expires_in_seconds: int = 300


# ============================================
# Common Schemas
# ============================================

class MessageResponse(BaseModel):
    """Response genérica de mensagem"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Response de erro"""
    detail: str
    error_code: str | None = None
