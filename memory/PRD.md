# TUDOaqui SuperApp - PRD

## Visao Geral
SuperApp modular para Angola. Logo: TUDOAqui. Slogan: a sua vida em um so lugar.
Cores: Vermelho, Amarelo, Preto, Branco.

## Stack
- Frontend: React + TailwindCSS + Lucide React
- Backend: FastAPI + SQLAlchemy + PostgreSQL
- SMS: Africa's Talking (Sandbox)

## Implementado

### Core
- [x] Auth OTP (telefone), 9 roles, rate limiting
- [x] Seed Data Angola (eventos, produtos, alojamento, turismo, imoveis, restaurantes c/ menus)
- [x] Admin Panel (stats, gestao users, conteudo, aprovacao upgrades)
- [x] Account (perfil, editar nome/email, solicitar upgrade role, historico)

### Frontend (9 Paginas + Admin)
- [x] Login OTP, Dashboard, Eventos, Marketplace, Alojamento, Turismo, Imobiliario, Entregas, Restaurantes
- [x] Conta (perfil + upgrade), Admin (4 tabs: overview, users, upgrades, conteudo)
- [x] Formularios criacao (Eventos, Marketplace, Alojamento, Turismo)
- [x] Carrinho restaurante, estimativa entrega

### Role Upgrade System
- [x] User solicita upgrade com motivo
- [x] Admin aprova/rejeita com nota
- [x] Aprovacao altera role automaticamente
- [x] Historico de pedidos visivel ao user
- [x] Prevencao de pedidos duplicados

## API Endpoints
- Auth: login, verify-otp, me
- Account: profile (GET/PUT), role-request (POST), role-requests (GET)
- Admin: stats, users (GET/PUT role/status), role-requests (GET/approve/reject), events, restaurants, sellers, agents
- Modulos: events, marketplace/products, alojamento/properties, turismo/experiences, realestate/properties, restaurantes, entregas/estimate
- Seed: POST /api/v1/seed

## Backlog
- P0: Integracao Multicaixa Express
- P1: Push notifications Firebase
- P2: Wallet B2B, Taxi frontend
