# TUDOaqui SuperApp - Product Requirements Document

## Visão Geral
SuperApp modular para Angola integrando múltiplos serviços numa única plataforma.

## Stack Tecnológica
- **Mobile:** Flutter (Dart) - Android & iOS
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL + Redis
- **Pagamentos:** Multicaixa Express + Mobile Money
- **SMS:** Africa's Talking

## Módulos do Sistema - TODOS COMPLETOS

### Core
- [x] Users, Roles, Auth OTP
- [x] Rate Limiting
- [x] SMS Africa's Talking

### Tuendi
- [x] Taxi (Corridas)
- [x] Drivers (Motoristas)
- [ ] Entrega (pendente)
- [ ] Restaurante (pendente)

### Eventos
- [x] Models (Event, TicketType, Ticket, CheckIn)
- [x] Schemas completos
- [x] Service (CRUD, compra, check-in QR)
- [x] Router (todos endpoints)

### Marketplace
- [x] Models (Seller, Product, Category, Order, OrderItem, Review)
- [x] Schemas completos
- [x] Service (vendedores, produtos, pedidos)
- [x] Router (todos endpoints)

### Alojamento
- [x] Models (Property, Availability, Booking, Review)
- [x] Schemas completos
- [x] Service (propriedades, disponibilidade, reservas)
- [x] Router (todos endpoints)

### Turismo
- [x] Models (Experience, Schedule, Booking, Review)
- [x] Schemas completos
- [x] Service (experiências, horários, vouchers)
- [x] Router (todos endpoints)

### Real Estate (Imobiliário)
- [x] Models (Agent, Property, Lead, Favorite)
- [x] Schemas completos
- [x] Service (agentes, imóveis, leads, favoritos)
- [x] Router (todos endpoints)

### Payments
- [x] Ledger centralizado
- [ ] Multicaixa Express (pendente integração)
- [ ] Mobile Money (pendente integração)

### Notifications
- [x] Push + WebSocket

## API Endpoints por Módulo

### Auth
- POST /api/v1/auth/login
- POST /api/v1/auth/verify-otp
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout

### Eventos
- GET/POST /api/v1/events
- GET/PUT /api/v1/events/{id}
- POST /api/v1/events/{id}/publish
- POST /api/v1/events/{id}/ticket-types
- POST /api/v1/tickets/purchase
- POST /api/v1/events/{id}/checkin

### Marketplace
- GET/POST /api/v1/marketplace/sellers
- GET/POST /api/v1/marketplace/products
- GET/POST /api/v1/marketplace/orders
- PUT /api/v1/marketplace/orders/{id}/status

### Alojamento
- GET/POST /api/v1/alojamento/properties
- GET /api/v1/alojamento/properties/{id}/availability
- POST /api/v1/alojamento/bookings
- PUT /api/v1/alojamento/bookings/{id}/status

### Turismo
- GET/POST /api/v1/turismo/experiences
- POST /api/v1/turismo/experiences/{id}/schedules
- POST /api/v1/turismo/bookings
- POST /api/v1/turismo/experiences/{id}/use-voucher

### Real Estate
- GET/POST /api/v1/realestate/agents
- GET/POST /api/v1/realestate/properties
- GET/POST /api/v1/realestate/leads
- GET/POST/DELETE /api/v1/realestate/favorites

## Histórico de Implementações

### Janeiro 2026
1. Correções de segurança (SECRET_KEY, OTP, Rate Limiting)
2. SMS Africa's Talking configurado
3. Módulo Eventos completo
4. Módulo Marketplace completo
5. Módulo Alojamento completo
6. Módulo Turismo completo
7. Módulo Real Estate completo

## Backlog

### P0 - Crítico
- [ ] Integração Multicaixa Express
- [ ] Testes automatizados

### P1 - Alta
- [ ] Tuendi Entrega
- [ ] Tuendi Restaurante
- [ ] Push notifications Firebase

### P2 - Média
- [ ] Wallet B2B
- [ ] Painel Admin Web

## Arquivos Criados (Janeiro 2026)

### Alojamento
- src/alojamento/schemas.py
- src/alojamento/service.py
- src/alojamento/router.py

### Turismo
- src/turismo/schemas.py
- src/turismo/service.py
- src/turismo/router.py

### Real Estate
- src/realestate/schemas.py
- src/realestate/service.py
- src/realestate/router.py

### SMS
- src/common/sms_provider.py
