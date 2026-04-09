# TUDOaqui - Relatório de Revisão de Código

**Data:** Janeiro 2026  
**Versão Analisada:** 1.0.0 (MVP Fase 1 - Tuendi Taxi)

---

## Resumo Executivo

O codebase do TUDOaqui está **bem estruturado** e segue boas práticas de desenvolvimento. A arquitetura é sólida e escalável, com separação clara de responsabilidades. No entanto, foram identificadas algumas áreas que precisam de atenção.

### Score Geral: 7.5/10

| Categoria | Score | Status |
|-----------|-------|--------|
| Arquitetura | 8/10 | Excelente |
| Segurança | 6/10 | Precisa Melhorias |
| Performance | 7/10 | Bom |
| Manutenibilidade | 8/10 | Excelente |
| Testes | 3/10 | Crítico |
| Documentação | 7/10 | Bom |

---

## 1. Pontos Positivos

### 1.1 Arquitetura
- Estrutura modular bem organizada (auth, tuendi, payments, notifications)
- Separação clara entre models, schemas, services e routers
- Uso correto de async/await com SQLAlchemy 2.0
- Padrão de injeção de dependências bem implementado
- WebSocket manager bem estruturado para tempo real

### 1.2 Código Backend
- Schemas Pydantic com validações adequadas
- Enums para status e tipos (evita magic strings)
- Services encapsulam lógica de negócio corretamente
- Tratamento de erros consistente nos routers
- Cálculos de preço e distância implementados corretamente (Haversine)

### 1.3 Database
- Schema SQL bem normalizado
- Índices criados para queries frequentes
- Triggers para atualização automática de estatísticas
- Views úteis para relatórios
- Uso correto de timezone-aware timestamps

### 1.4 Frontend (Flutter)
- Estrutura organizada com BLoC pattern
- Configuração de temas centralizada
- API client separado

---

## 2. Problemas Críticos

### 2.1 SEGURANÇA - SECRET_KEY Hardcoded

**Arquivo:** `/app/backend/src/config.py` (linha 25)

```python
# PROBLEMA: Secret key hardcoded
SECRET_KEY: str = "tudoaqui-super-secret-key-change-in-production-2025"
```

**Risco:** Compromete toda a autenticação JWT se exposto.

**Solução:**
```python
SECRET_KEY: str  # Sem default, forçar via .env
```

---

### 2.2 SEGURANÇA - OTP Previsível

**Arquivo:** `/app/backend/src/auth/service.py` (linhas 22-24)

```python
# PROBLEMA: random.choices não é criptograficamente seguro
def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=settings.OTP_LENGTH))
```

**Risco:** OTPs podem ser previsíveis em ataques sofisticados.

**Solução:**
```python
import secrets
def generate_otp() -> str:
    return ''.join(secrets.choice(string.digits) for _ in range(settings.OTP_LENGTH))
```

---

### 2.3 SEGURANÇA - Rate Limiting Ausente

**Problema:** Nenhum rate limiting implementado nos endpoints de autenticação.

**Risco:** Vulnerável a:
- Brute force de OTP
- DoS attacks
- Spam de SMS

**Solução:** Implementar SlowAPI ou similar:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(...):
```

---

### 2.4 TESTES - Cobertura Zero

**Problema:** Nenhum teste automatizado foi encontrado.

**Risco:** 
- Regressões não detectadas
- Refactoring arriscado
- Difícil manutenção

**Solução:** Criar testes unitários e de integração:
```
tests/
├── unit/
│   ├── test_auth_service.py
│   ├── test_ride_service.py
│   └── test_payment_service.py
├── integration/
│   ├── test_auth_flow.py
│   └── test_ride_flow.py
└── conftest.py
```

---

## 3. Problemas Médios

### 3.1 DATABASE - Falta Connection Pool Monitoring

**Arquivo:** `/app/backend/src/database.py`

```python
# Problema: Pool sem monitoramento
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
)
```

**Sugestão:** Adicionar eventos para monitorar:
```python
from sqlalchemy import event

@event.listens_for(engine.sync_engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    logging.debug("Connection checked out from pool")
```

---

### 3.2 PERFORMANCE - N+1 Query Potencial

**Arquivo:** `/app/backend/src/tuendi/rides/router.py` (linha 69-114)

```python
# Problema: Busca corrida e depois motorista separadamente
async def get_current_ride(...):
    result = await db.execute(select(Ride)...)
    ride = result.scalar_one_or_none()
    
    if not ride:
        return None
    
    # Segunda query para dados completos
    ride = await ride_service.get_ride(db, ride.id)
```

**Sugestão:** Unificar com eager loading na primeira query.

---

### 3.3 VALIDAÇÃO - Telefone Insuficiente

**Arquivo:** `/app/backend/src/auth/router.py` (linhas 38-40)

```python
# Validação muito básica
telefone = request.telefone.strip()
if not telefone.startswith("+"):
    telefone = f"+244{telefone.lstrip('0')}"
```

**Sugestão:** Usar biblioteca `phonenumbers` (já instalada):
```python
import phonenumbers

def validate_phone(telefone: str) -> str:
    try:
        parsed = phonenumbers.parse(telefone, "AO")
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Número inválido")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except:
        raise HTTPException(400, "Formato de telefone inválido")
```

---

### 3.4 LOGGING - Ausência de Structured Logging

**Problema:** Apenas `print()` statements para logging.

**Arquivo:** `/app/backend/src/auth/service.py` (linha 208)

```python
print(f"[SMS MOCK] Para: {telefone} | Mensagem: {message}")
```

**Sugestão:** Usar logging estruturado:
```python
import logging
import structlog

logger = structlog.get_logger()

logger.info("sms_sent", telefone=telefone, provider=settings.SMS_PROVIDER)
```

---

### 3.5 ERROR HANDLING - Exceções Genéricas

**Problema:** Uso de `ValueError` para erros de negócio.

```python
raise ValueError("Já existe uma corrida em andamento")
```

**Sugestão:** Criar exceções customizadas:
```python
class TUDOaquiException(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code

class RideAlreadyActiveError(TUDOaquiException):
    def __init__(self):
        super().__init__("Já existe uma corrida em andamento", "RIDE_ACTIVE")
```

---

## 4. Melhorias Sugeridas

### 4.1 Adicionar Health Check Completo

**Atual:** Health check básico.

**Sugestão:**
```python
@app.get("/health/detailed")
async def detailed_health(db: AsyncSession = Depends(get_db)):
    checks = {
        "database": await check_database(db),
        "redis": await check_redis(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    healthy = all(c["status"] == "ok" for c in checks.values() if isinstance(c, dict))
    return {"status": "healthy" if healthy else "degraded", "checks": checks}
```

---

### 4.2 Implementar Retry Logic para Pagamentos

**Arquivo:** `/app/backend/src/payments/service.py`

```python
# Atual: Sem retry
async def _init_multicaixa_payment(self, payment: Payment):
    pass  # TODO

# Sugestão: Com retry e circuit breaker
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def _init_multicaixa_payment(self, payment: Payment):
    async with httpx.AsyncClient() as client:
        response = await client.post(settings.MULTICAIXA_API_URL, ...)
```

---

### 4.3 Cache com Redis

**Problema:** Redis configurado mas não utilizado.

**Sugestão:** Implementar cache para:
- Motoristas online (já feito via WebSocket, mas backup em Redis)
- Configurações do sistema
- Sessões de OTP

```python
import redis.asyncio as redis

class RedisCache:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
    
    async def cache_online_drivers(self, drivers: list):
        await self.redis.setex("online_drivers", 60, json.dumps(drivers))
```

---

### 4.4 Adicionar Middleware de Request ID

```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

app.add_middleware(RequestIDMiddleware)
```

---

## 5. Checklist de Ações

### Prioridade Alta (Fazer Agora)
- [ ] Remover SECRET_KEY hardcoded
- [ ] Implementar rate limiting no login/OTP
- [ ] Usar `secrets` para geração de OTP
- [ ] Criar testes básicos para auth e rides

### Prioridade Média (Próxima Sprint)
- [ ] Adicionar structured logging
- [ ] Implementar exceções customizadas
- [ ] Validação de telefone com phonenumbers
- [ ] Health check detalhado

### Prioridade Baixa (Backlog)
- [ ] Cache com Redis
- [ ] Request ID middleware
- [ ] Retry logic para pagamentos
- [ ] Documentação OpenAPI mais detalhada

---

## 6. Módulos Faltando (Conforme Documentação)

| Módulo | Status | Prioridade |
|--------|--------|------------|
| Eventos (Tickets + QR) | Não implementado | Alta |
| Marketplace | Não implementado | Média |
| Alojamento | Não implementado | Média |
| Turismo | Não implementado | Baixa |
| Real Estate | Não implementado | Baixa |

---

## 7. Frontend (Flutter) - Observações

### Arquivos Analisados
- `main.dart` - Bem estruturado com BLoC
- `pubspec.yaml` - Dependências adequadas

### Pendências
- Verificar implementação completa dos BLoCs
- Confirmar integração com WebSocket
- Testar fluxo de corrida completo

---

## Conclusão

O código base está **sólido para um MVP**, com arquitetura bem pensada e código limpo. As principais preocupações são:

1. **Segurança:** Precisa de atenção urgente (secrets, rate limiting)
2. **Testes:** Implementação crítica antes de escalar
3. **Módulos:** Apenas Tuendi implementado dos 8 planejados

**Recomendação:** Corrigir problemas de segurança antes de ir para produção, e estabelecer pipeline de testes antes de implementar novos módulos.

---

*Relatório gerado por revisão de código automatizada*
