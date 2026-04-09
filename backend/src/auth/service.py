"""
TUDOaqui API - Auth Service
"""
import string
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.users.models import User, OTPCode, RefreshToken, UserRole


class AuthService:
    """Serviço de autenticação"""
    
    @staticmethod
    def generate_otp() -> str:
        """Gera código OTP de 6 dígitos (criptograficamente seguro)"""
        return ''.join(secrets.choice(string.digits) for _ in range(settings.OTP_LENGTH))
    
    @staticmethod
    def generate_refresh_token() -> str:
        """Gera refresh token seguro"""
        return secrets.token_urlsafe(64)
    
    @staticmethod
    def create_access_token(user_id: UUID, role: str) -> tuple[str, datetime]:
        """Cria access token JWT"""
        expires = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expires,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token, expires
    
    @staticmethod
    def decode_token(token: str) -> dict | None:
        """Decodifica e valida token JWT"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    async def send_otp(self, db: AsyncSession, telefone: str) -> OTPCode:
        """Envia OTP para o telefone"""
        # Invalida OTPs anteriores
        await db.execute(
            OTPCode.__table__.update()
            .where(and_(
                OTPCode.telefone == telefone,
                OTPCode.verificado.is_(False)
            ))
            .values(verificado=True)
        )
        
        # Gera novo OTP
        codigo = self.generate_otp()
        expira_em = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        
        otp = OTPCode(
            telefone=telefone,
            codigo=codigo,
            expira_em=expira_em
        )
        db.add(otp)
        await db.commit()
        await db.refresh(otp)
        
        # Enviar SMS (mock em desenvolvimento)
        await self._send_sms(telefone, f"TUDOaqui: O seu código é {codigo}. Válido por {settings.OTP_EXPIRE_MINUTES} minutos.")
        
        return otp
    
    async def verify_otp(self, db: AsyncSession, telefone: str, codigo: str) -> OTPCode | None:
        """Verifica código OTP"""
        result = await db.execute(
            select(OTPCode)
            .where(and_(
                OTPCode.telefone == telefone,
                OTPCode.verificado.is_(False),
                OTPCode.expira_em > datetime.now(timezone.utc)
            ))
            .order_by(OTPCode.created_at.desc())
            .limit(1)
        )
        otp = result.scalar_one_or_none()
        
        if not otp:
            return None
        
        # Verifica tentativas
        if otp.tentativas >= settings.OTP_MAX_ATTEMPTS:
            return None
        
        # Incrementa tentativas
        otp.tentativas += 1
        
        # Verifica código
        if otp.codigo != codigo:
            await db.commit()
            return None
        
        # Marca como verificado
        otp.verificado = True
        await db.commit()
        
        return otp
    
    async def get_or_create_user(
        self, 
        db: AsyncSession, 
        telefone: str, 
        role: UserRole = UserRole.CLIENTE
    ) -> tuple[User, bool]:
        """Obtém ou cria utilizador"""
        result = await db.execute(
            select(User).where(User.telefone == telefone)
        )
        user = result.scalar_one_or_none()
        
        if user:
            return user, False
        
        # Cria novo utilizador
        user = User(
            telefone=telefone,
            role=role.value
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user, True
    
    async def create_refresh_token(
        self, 
        db: AsyncSession, 
        user_id: UUID,
        device_info: str | None = None
    ) -> RefreshToken:
        """Cria refresh token"""
        token = self.generate_refresh_token()
        expira_em = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        refresh = RefreshToken(
            user_id=user_id,
            token=token,
            device_info=device_info,
            expira_em=expira_em
        )
        db.add(refresh)
        await db.commit()
        await db.refresh(refresh)
        
        return refresh
    
    async def validate_refresh_token(self, db: AsyncSession, token: str) -> RefreshToken | None:
        """Valida refresh token"""
        result = await db.execute(
            select(RefreshToken)
            .where(and_(
                RefreshToken.token == token,
                RefreshToken.revogado.is_(False),
                RefreshToken.expira_em > datetime.now(timezone.utc)
            ))
        )
        return result.scalar_one_or_none()
    
    async def revoke_refresh_token(self, db: AsyncSession, token: str) -> bool:
        """Revoga refresh token"""
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        refresh = result.scalar_one_or_none()
        
        if refresh:
            refresh.revogado = True
            await db.commit()
            return True
        return False
    
    async def revoke_all_tokens(self, db: AsyncSession, user_id: UUID) -> int:
        """Revoga todos os tokens do utilizador"""
        result = await db.execute(
            RefreshToken.__table__.update()
            .where(and_(
                RefreshToken.user_id == user_id,
                RefreshToken.revogado.is_(False)
            ))
            .values(revogado=True)
        )
        await db.commit()
        return result.rowcount
    
    async def _send_sms(self, telefone: str, message: str) -> bool:
        """
        Envia SMS usando o provider configurado.
        Suporta: mock (dev) e africastalking (produção)
        """
        from src.common.sms_provider import sms_provider
        
        result = await sms_provider.send_sms(telefone, message)
        
        if result["status"] == "success":
            return True
        else:
            # Log do erro mas não falha (OTP fica no banco para retry)
            print(f"[SMS ERROR] {result.get('message', 'Unknown error')}")
            return False


# Instância global
auth_service = AuthService()
