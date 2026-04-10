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
- Testes: pytest (13 testes modulos + auth + rides)
- Deploy: Docker Compose + Nginx + Let's Encrypt SSL

## Implementado

### Core Backend
- [x] Auth OTP, 7 roles + staff + admin, rate limiting (auto Redis/InMemory fallback)
- [x] Seed Data Angola, Admin Panel (6 tabs), Account
- [x] Alembic migrations configurado (29 tabelas detectadas)
- [x] pytest test suite (13 testes passam)
- [x] Multicaixa webhook com validacao HMAC-SHA256

### Sistema de Parceiros
- [x] 7 tipos, config pagamento (Unitel Money + Transferencia + Cash), admin approval

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

### Seguranca e Infra
- [x] API Keys removidas do codigo (env vars / manifest placeholders)
- [x] Rate limiter auto-detect Redis com fallback InMemory
- [x] Docker-compose producao com Redis + PostgreSQL + Backend + Frontend + Nginx
- [x] .env.example e .env.production.example documentados
- [x] Alembic configurado com todos os modelos
- [x] Gradle files completos para Flutter Android

## Auditoria de Seguranca (2026-04-10)
| # | Item | Estado |
|---|------|--------|
| 1 | API Key exposta | RESOLVIDO (codigo limpo, revogar na consola Google) |
| 2 | Redis docker-compose | RESOLVIDO (docker-compose.yml criado) |
| 3 | RedisRateLimiter | RESOLVIDO (auto-detect implementado) |
| 4 | URLs erradas Flutter | RESOLVIDO (3 URLs corrigidas) |
| 5 | /realestate/leads/my | RESOLVIDO (Flutter usa /realestate/leads) |
| 6 | /marketplace/categories | JA EXISTIA no backend |
| 7 | Multicaixa HMAC | RESOLVIDO (validacao implementada) |
| 8 | Alembic | RESOLVIDO (configurado com autogenerate) |
| 9 | /ws/motoqueiro | JA SUPORTADO (role check aceita motoqueiro) |
| 10 | Carrinho + checkout Flutter | PENDENTE (P1) |
| 11 | Compra tickets Flutter | PENDENTE (P1) |
| 12 | Unit tests | RESOLVIDO (13 testes passam) |

## Backlog
- P1: Carrinho + Checkout completo no Flutter (Restaurante, Marketplace, Eventos)
- P2: Push Notifications (FCM)
- P3: Multicaixa Express gateway real
- P4: Modo offline (SQLite)
- P5: Wallet B2B (Fase 2)
