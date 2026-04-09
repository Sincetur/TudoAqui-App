"""
TUDOaqui API - Main Application
Fase 1 MVP: Tuendi Taxi
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.config import settings
from src.database import engine, Base, init_db, close_db

# Import routers
from src.auth.router import router as auth_router
from src.tuendi.drivers.router import router as drivers_router
from src.tuendi.rides.router import router as rides_router
from src.payments.router import router as payments_router
from src.notifications.router import router as notifications_router
from src.common.ws_router import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager para startup e shutdown"""
    # Startup
    print("🚀 Iniciando TUDOaqui API...")
    
    # Criar tabelas (em produção usar migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Base de dados conectada")
    print("📍 Servidor: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    
    yield
    
    # Shutdown
    print("🛑 Encerrando TUDOaqui API...")
    await close_db()
    print("✅ Conexões fechadas")


# Criar aplicação
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## TUDOaqui SuperApp API - Fase 1 MVP

### 🚕 Tuendi Taxi
API para o módulo de mobilidade do TUDOaqui SuperApp.

### Módulos Disponíveis:
- **Auth**: Autenticação via OTP + JWT
- **Drivers**: Gestão de motoristas
- **Rides**: Gestão de corridas
- **Payments**: Pagamentos e Ledger

### Fluxo de Autenticação:
1. `POST /api/v1/auth/login` - Envia OTP para telefone
2. `POST /api/v1/auth/verify-otp` - Verifica OTP e retorna tokens
3. Use `Authorization: Bearer {access_token}` nas requisições

### Fluxo de Corrida:
1. Cliente: `POST /api/v1/rides/estimate` - Estima preço
2. Cliente: `POST /api/v1/rides/request` - Solicita corrida
3. Motorista: `POST /api/v1/rides/{id}/accept` - Aceita corrida
4. Motorista: `POST /api/v1/rides/{id}/start` - Inicia corrida
5. Motorista: `POST /api/v1/rides/{id}/finish` - Finaliza corrida
6. Cliente: `POST /api/v1/rides/{id}/rate` - Avalia corrida
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Erro de validação",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler geral para exceções"""
    if settings.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor"}
    )


# Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica se a API está online"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Incluir routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(drivers_router, prefix="/api/v1")
app.include_router(rides_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/api/v1")


# Para rodar com: uv run uvicorn src.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
