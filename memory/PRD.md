# TUDOaqui SuperApp - Product Requirements Document

## Visao Geral
SuperApp modular para Angola integrando multiplos servicos numa unica plataforma.

## Stack Tecnologica
- **Frontend:** React (CRA) + TailwindCSS
- **Backend:** FastAPI (Python) + SQLAlchemy ORM
- **Database:** PostgreSQL (asyncpg)
- **Pagamentos:** Multicaixa Express + Mobile Money (pendente)
- **SMS:** Africa's Talking (Sandbox mode)

## Modulos do Sistema

### Core
- [x] Users, Roles, Auth OTP
- [x] Rate Limiting (in-memory)
- [x] SMS Africa's Talking (Sandbox)

### Tuendi
- [x] Taxi (Corridas)
- [x] Drivers (Motoristas)
- [x] Entrega (Delivery de pacotes)
- [x] Restaurante (Delivery de comida)

### Eventos
- [x] Models (Event, TicketType, Ticket, CheckIn)
- [x] Schemas, Service, Router completos

### Marketplace
- [x] Models (Seller, Product, Category, Order, OrderItem, Review)
- [x] Schemas, Service, Router completos

### Alojamento
- [x] Models (Property, Availability, Booking, Review)
- [x] Schemas, Service, Router completos

### Turismo
- [x] Models (Experience, Schedule, Booking, Review)
- [x] Schemas, Service, Router completos

### Real Estate (Imobiliario)
- [x] Models (Agent, Property, Lead, Favorite)
- [x] Schemas, Service, Router completos

### Payments
- [x] Ledger centralizado
- [ ] Multicaixa Express (pendente integracao)
- [ ] Mobile Money (pendente integracao)

### Notifications
- [x] Push + WebSocket base

## API Endpoints Validados (Testados)

### Health
- GET /api/health - 200 OK

### Auth
- POST /api/v1/auth/login
- POST /api/v1/auth/verify-otp
- GET /api/v1/auth/me
- POST /api/v1/auth/refresh-token
- POST /api/v1/auth/logout

### Eventos
- GET /api/v1/events

### Marketplace
- GET /api/v1/marketplace/products
- GET /api/v1/marketplace/sellers
- GET /api/v1/marketplace/categories

### Alojamento
- GET /api/v1/alojamento/properties

### Turismo
- GET /api/v1/turismo/experiences

### Real Estate
- GET /api/v1/realestate/properties
- GET /api/v1/realestate/agents

### Entrega
- POST /api/v1/entregas/estimate (auth required)

### Restaurante
- GET /api/v1/restaurantes

### Drivers
- POST /api/v1/drivers/register (auth required)

## Historico de Implementacoes

### Abril 2026
1. Criacao de server.py (ponte para uvicorn)
2. Instalacao PostgreSQL no ambiente
3. Criacao __init__.py para modulo restaurante
4. Registo routers entrega/restaurante no main.py
5. Fix atributos Driver no entrega router
6. Frontend React com TailwindCSS (Login + Dashboard)
7. Testes backend: 23/23 passed

### Janeiro 2026
1. Correcoes de seguranca (SECRET_KEY, OTP, Rate Limiting)
2. SMS Africa's Talking configurado (Sandbox)
3. Modulo Eventos completo
4. Modulo Marketplace completo
5. Modulo Alojamento completo
6. Modulo Turismo completo
7. Modulo Real Estate completo
8. Modulo Entrega completo
9. Modulo Restaurante completo

## Backlog

### P0 - Critico
- [ ] Integracao Multicaixa Express
- [ ] Testes end-to-end completos

### P1 - Alta
- [ ] Push notifications Firebase
- [ ] Seed data para demonstracao

### P2 - Media
- [ ] Wallet B2B
- [ ] Painel Admin Web
- [ ] Frontend completo para cada modulo

## Arquitetura

### Backend
```
/app/backend/
  server.py              # Ponte uvicorn -> src.main
  src/
    main.py              # FastAPI app + routers
    config.py            # Pydantic settings
    database.py          # SQLAlchemy async engine
    auth/                # OTP auth + JWT + rate limiting
    users/               # User models + schemas
    tuendi/
      schemas.py         # Schemas partilhados
      drivers/           # Motoristas
      rides/             # Corridas taxi
      entrega/           # Delivery pacotes
      restaurante/       # Delivery comida
      matching/          # Matching motoristas
    events/              # Eventos + tickets
    marketplace/         # Multi-vendedor
    alojamento/          # Reservas estadias
    turismo/             # Tours + experiencias
    realestate/          # Imoveis
    payments/            # Pagamentos + ledger
    notifications/       # Push + WebSocket
    common/              # SMS provider, utils
```

### Frontend
```
/app/frontend/
  src/
    App.js               # Router principal
    api.js               # API client
    pages/
      Login.js           # Login OTP
      Dashboard.js       # Dashboard SuperApp
```
