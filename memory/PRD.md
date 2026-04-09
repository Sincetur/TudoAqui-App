# TUDOaqui SuperApp - Product Requirements Document

## Visão Geral
SuperApp modular para Angola integrando múltiplos serviços numa única plataforma.

## Stack Tecnológica
- **Mobile:** Flutter (Dart) - Android & iOS
- **Backend:** FastAPI (Python) + NestJS (TypeScript)
- **Database:** PostgreSQL + Redis
- **Pagamentos:** Multicaixa Express + Mobile Money

## Módulos do Sistema

### Implementados
- [x] Core (Users, Roles, Auth OTP)
- [x] Tuendi Taxi (Corridas)
- [x] Drivers (Motoristas)
- [x] Payments (Pagamentos + Ledger)
- [x] Notifications (Push + WebSocket)
- [x] Wallet (preparado)
- [x] **Eventos** (Tickets + QR + Check-in) - COMPLETO
- [x] **Marketplace** (Multi-vendedor B2C/B2B) - COMPLETO
- [x] **Alojamento** (modelo Airbnb) - Models prontos
- [x] **Turismo** (Experiências) - Models prontos
- [x] **Real Estate** (Imobiliário) - Models prontos

### Pendentes (Routers/Services)
- [ ] Tuendi Entrega (router/service)
- [ ] Tuendi Restaurante (router/service)
- [ ] Alojamento (router/service)
- [ ] Turismo (router/service)
- [ ] Real Estate (router/service)

## Histórico de Implementações

### Janeiro 2026 - Correções de Segurança + Módulos

**Segurança:**
1. SECRET_KEY obrigatório via .env
2. OTP criptograficamente seguro (secrets)
3. Rate limiting (login, OTP, verify)
4. Validação telefone com phonenumbers

**Módulos Completos:**
- Eventos: Models + Schemas + Service + Router
- Marketplace: Models + Schemas + Service + Router

**Módulos (Models Prontos):**
- Alojamento, Turismo, Real Estate

## User Personas
1. **Cliente** - Corridas, tickets, pedidos
2. **Motorista** - Corridas
3. **Organizador** - Eventos
4. **Vendedor** - Marketplace
5. **Anfitrião** - Alojamento
6. **Agente** - Imobiliário
7. **Staff** - Check-in
8. **Admin** - Gestão

## Backlog

### P0 - Crítico
- [x] SMS real (Africa's Talking) - IMPLEMENTADO
- [ ] Integração Multicaixa
- [ ] Testes automatizados

### P1 - Alta
- [ ] Completar Alojamento
- [ ] Completar Turismo
- [ ] Completar Real Estate

### P2 - Média
- [ ] Tuendi Entrega/Restaurante
- [ ] Wallet B2B
