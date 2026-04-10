# TUDOaqui SuperApp - PRD

## Visao Geral
SuperApp modular para Angola. Logo: TUDOAqui. Slogan: a sua vida em um so lugar.
Cores: Vermelho, Amarelo, Preto, Branco.

## Stack
- Frontend Web: React + TailwindCSS + Lucide React + PWA
- Frontend Mobile: Flutter (multi-modulo) em `mobile/flutter/tudoaqui/`
- Backend: FastAPI + SQLAlchemy + PostgreSQL + Redis
- SMS: Africa's Talking (Sandbox)
- Migrations: Alembic (2 migrations versionadas)
- Testes: pytest (16 testes isolados + 15 testes endpoint = 31 total)
- Deploy: Docker Compose + Nginx + Let's Encrypt SSL

## Implementado

### Core Backend
- [x] Auth OTP, 7 roles + staff + admin, rate limiting (auto Redis/InMemory fallback)
- [x] Seed Data Angola, Admin Panel (6 tabs), Account
- [x] Alembic migrations (2 versoes: initial_schema + sync_all_models)
- [x] pytest test suite (31 testes, test_isolated.py usa httpx.AsyncClient)
- [x] Multicaixa webhook com validacao HMAC-SHA256
- [x] Matching service integrado no rides/service.py (haversine + score 40/40/20)

### Sistema de Parceiros
- [x] 7 tipos, config pagamento (Unitel Money + Transferencia + Cash), admin approval
- [x] Partner model em models.py (padrao consistente com outros modulos)

### Pagamentos
- [x] Transferencia BAI, Unitel Money, Cash, admin confirm/reject
- [x] Webhook Multicaixa com HMAC validation

### Frontend Web (React PWA)
- [x] 9 paginas + Admin (6 tabs), CheckoutModal, PWA

### Mobile Android TWA
- [x] Projecto Android completo, signing via env vars

### Mobile Flutter App
- [x] 7 modulos CRUD por role com API real
- [x] Google Maps, GPS tracking, WebSocket real-time
- [x] CartProvider global no main.dart (MultiProvider)
- [x] CartService + CheckoutScreen unificado (cash, transferencia, unitel money)
- [x] Marketplace: add-to-cart + badge + checkout
- [x] Restaurantes: + por item do menu + FAB checkout
- [x] Eventos: seletor bilhetes + purchaseTicket API
- [x] Alojamento: date pickers + contador adultos/criancas
- [x] Turismo: seletor horarios + contador participantes
- [x] Imobiliario: checkout com CartProvider + contactar agente
- [x] Home screen: dashboard com stats reais da API (eventos, produtos, restaurantes, experiencias)
- [x] Motoqueiro: stats de entregas/ganhos via API (nao hardcoded)
- [x] Proprietario: stats produtos/pedidos via API
- [x] Guia: stats experiencias/reservas via API
- [x] Agente: stats imoveis/experiencias via API
- [x] Login screen: OTP via AuthService (sendOtp + verifyOtp)

### Seguranca e Infra
- [x] API Keys removidas do codigo (env vars)
- [x] Redis no docker-compose raiz com healthcheck + timeout 3s + start_period
- [x] Redis no docker-compose producao com restart: unless-stopped
- [x] .gitignore: test_reports/ + key.properties + *.keystore
- [x] WS /motoqueiro/{token} como alias de /driver/
- [x] test_all_modules.py e test_iteration9_endpoints.py URLs corrigidas (env vars)
- [x] Testes isolados com httpx.AsyncClient (sem servidor activo)

## Auditoria Completa (2026-04-10)
| # | Item | Estado |
|---|------|--------|
| 1 | URL hardcoded test_iteration9 | RESOLVIDO |
| 2 | test_reports/ no .gitignore | RESOLVIDO |
| 3 | Matching integrado no rides | RESOLVIDO |
| 4 | Alembic migrations SQL | RESOLVIDO (2 versoes) |
| 5 | Login screen sem API | JA EXISTIA (sendOtp/verifyOtp) |
| 6 | Home screen sem dados reais | RESOLVIDO (4 stats API) |
| 7 | key.properties no .gitignore | RESOLVIDO |
| 8 | Redis healthcheck timeout | RESOLVIDO (3s + start_period) |
| 9 | Dashboards hardcoded | RESOLVIDO (motoqueiro API) |
| 10 | Real Estate sem checkout | RESOLVIDO (CartProvider) |
| 11 | Notifications FCM | P2 (backlog) |
| 12 | Unit tests isolados | RESOLVIDO (16 testes) |
| 13 | URL hardcoded test_all_modules | RESOLVIDO |

## Backlog
- P2: Push Notifications (FCM) - Firebase Admin SDK + flutter_local_notifications
- P3: Multicaixa Express gateway real
- P4: Modo offline (SQLite)
- P5: Wallet B2B (Fase 2)
- P6: Flutter widget tests (UI automation)
