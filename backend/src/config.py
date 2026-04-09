"""
TUDOaqui API - Configurações
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # App
    APP_NAME: str = "TUDOaqui API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tudoaqui"
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str  # OBRIGATÓRIO via .env - sem default por segurança
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OTP
    OTP_EXPIRE_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 3
    OTP_LENGTH: int = 6
    
    # SMS Provider (configurar com provider real em produção)
    SMS_PROVIDER: str = "mock"  # mock | africastalking
    SMS_API_KEY: str = ""
    SMS_SENDER: str = "TUDOaqui"
    
    # Africa's Talking
    AFRICASTALKING_API_KEY: str = ""
    AFRICASTALKING_USERNAME: str = ""
    AFRICASTALKING_SENDER_ID: str = ""  # Opcional, usar shortcode registado
    AFRICASTALKING_SANDBOX: bool = True  # True para testes, False para produção
    
    # Tuendi Config
    TAXA_PLATAFORMA: float = 0.20  # 20%
    PRECO_BASE_KM: float = 150.0   # Kz por km
    PRECO_BASE_MINUTO: float = 50.0  # Kz por minuto
    TAXA_MINIMA: float = 500.0     # Kz mínimo por corrida
    RAIO_BUSCA_MOTORISTAS: int = 5000  # metros
    
    # Payments
    MULTICAIXA_API_URL: str = ""
    MULTICAIXA_API_KEY: str = ""
    MOBILEMONEY_API_URL: str = ""
    MOBILEMONEY_API_KEY: str = ""
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância de settings (cached)"""
    return Settings()


settings = get_settings()
