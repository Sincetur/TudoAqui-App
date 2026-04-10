# TUDOaqui SuperApp - PRD

## Visao Geral
SuperApp modular para Angola. Logo: TUDOAqui. Slogan: a sua vida em um so lugar.
Cores: Vermelho, Amarelo, Preto, Branco.

## Stack
- Frontend Web: React + TailwindCSS + Lucide React + PWA
- Frontend Mobile: Flutter (multi-modulo) em `mobile/flutter/tudoaqui/`
- Backend: FastAPI + SQLAlchemy + PostgreSQL + Redis
- SMS: Africa's Talking (Sandbox)
- Migrations: Alembic (configurado com autogenerate)
- Testes: pytest (15+ testes modulos + auth + rides + endpoints)
- Deploy: Docker Compose + Nginx + Let's Encrypt SSL

## Implementado

### Core Backend
- [x] Auth OTP, 7 roles + staff + admin, rate limiting (auto Redis/InMemory fallback)
- [x] Seed Data Angola, Admin Panel (6 tabs), Account
- [x] Alembic migrations configurado (29 tabelas detectadas)
- [x] pytest test suite (15+ testes passam, iteration_9 100%)
- [x] Multicaixa webhook com validacao HMAC-SHA256
- [x] Matching service com geo-filter e prioridade (40% distancia + 40% rating + 20% experiencia)

### Sistema de Parceiros
- [x] 7 tipos, config pagamento (Unitel Money + Transferencia + Cash), admin approval
- [x] Partner model refactored para models.py (padrao consistente)

### Pagamentos
- [x] Transferencia BAI, Unitel Money, Cash, admin confirm/reject
- [x] Webhook Multicaixa com HMAC validation (X-Multicaixa-Signature)

### Frontend Web (React PWA)
- [x] 9 paginas + Admin (6 tabs), CheckoutModal, PWA

### Mobile Android TWA
- [x] Projecto Android completo, signing via env vars (CI/CD)

### Mobile Flutter App
- [x] 7 modulos CRUD por role com API real
- [x] URLs corrigidas: /entregas/driver/available, /start-pickup, /confirm-delivery, /realestate/leads
- [x] Google Maps, GPS tracking, WebSocket real-time
- [x] CartProvider global registado no main.dart
- [x] CartService + CheckoutScreen unificado (cash, transferencia, unitel money)
- [x] Marketplace: botao "Adicionar ao Carrinho" + badge + checkout
- [x] Restaurantes: botao "+" por item do menu + FAB checkout + badge
- [x] Eventos: seletor de bilhetes + compra com purchaseTicket API
- [x] Alojamento: date pickers (checkin/checkout) + contador adultos/criancas + reserva
- [x] Turismo: seletor de horarios + contador participantes + reserva

### Seguranca e Infra
- [x] API Keys removidas do codigo (env vars / manifest placeholders)
- [x] Rate limiter auto-detect Redis com fallback InMemory
- [x] Docker-compose raiz COM Redis (healthcheck + restart: unless-stopped)
- [x] Docker-compose producao com Redis + PostgreSQL + Backend + Frontend + Nginx
- [x] .env.example e .env.production.example documentados
- [x] Alembic configurado com todos os modelos
- [x] Gradle files completos para Flutter Android
- [x] WS /motoqueiro/{token} adicionado como alias de /driver/
- [x] test_all_modules.py URL hardcoded corrigida (usa env vars)

## Auditoria de Seguranca (2026-04-10)
| # | Item | Estado |
|---|------|--------|
| 1 | API Key exposta | RESOLVIDO |
| 2 | Redis docker-compose raiz | RESOLVIDO (adicionado) |
| 3 | RedisRateLimiter | RESOLVIDO (auto-detect) |
| 4 | URLs erradas Flutter | RESOLVIDO |
| 5 | /realestate/leads/my | RESOLVIDO |
| 6 | /marketplace/categories | RESOLVIDO (endpoint existe e funciona) |
| 7 | Multicaixa HMAC | RESOLVIDO |
| 8 | Alembic | RESOLVIDO |
| 9 | /ws/motoqueiro | RESOLVIDO (alias adicionado) |
| 10 | Carrinho + checkout Flutter | RESOLVIDO (5 modulos integrados) |
| 11 | Compra tickets Flutter | RESOLVIDO (purchaseTicket + CartItem.ticket) |
| 12 | Unit tests | RESOLVIDO (15+ testes) |
| 13 | URL hardcoded test_all_modules | RESOLVIDO (env var) |
| 14 | Partner model em __init__.py | RESOLVIDO (movido para models.py) |
| 15 | Matching service vazio | RESOLVIDO (geo-filter + score implementado) |

## Backlog
- P2: Push Notifications (FCM)
- P3: Multicaixa Express gateway real
- P4: Modo offline (SQLite)
- P5: Wallet B2B (Fase 2)
- P6: Flutter widget tests
- P7: Dashboards Flutter com dados reais da API (stats)
