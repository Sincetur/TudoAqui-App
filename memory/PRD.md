# TUDOaqui SuperApp - Product Requirements Document

## Visao Geral
SuperApp modular para Angola integrando multiplos servicos numa unica plataforma.
- **Logo**: TUDOAqui
- **Slogan**: a sua vida em um so lugar
- **Cores**: Vermelho (primary), Amarelo (accent), Preto (background), Branco (texto)

## Stack Tecnologica
- **Frontend:** React (CRA) + TailwindCSS + Lucide React
- **Backend:** FastAPI (Python) + SQLAlchemy ORM
- **Database:** PostgreSQL (asyncpg)
- **SMS:** Africa's Talking (Sandbox mode)

## Modulos Implementados

### Core
- [x] Users, Roles (9 tipos), Auth OTP
- [x] Rate Limiting
- [x] SMS Africa's Talking (Sandbox)
- [x] Seed Data (Dados demo Angola)
- [x] Admin Panel (3 tabs: Visao Geral, Utilizadores, Conteudo)

### Frontend (8 Modulos + Admin)
- [x] Dashboard com cards e stats
- [x] Eventos - Lista, detalhe, pesquisa, formulario criacao
- [x] Marketplace - Produtos, categorias, pesquisa, formulario criacao
- [x] Alojamento - Propriedades, pesquisa, formulario criacao
- [x] Turismo - Experiencias, pesquisa, formulario criacao
- [x] Imobiliario - Imoveis + Agentes (tabs), pesquisa
- [x] Entregas - Lista + Estimativa preco
- [x] Restaurantes - Lista + Menu + Carrinho
- [x] Admin Panel - Stats, gestao utilizadores (role/status), conteudo

### Admin Panel
- [x] Visao Geral: Stat cards (7 modulos) + Distribuicao de roles
- [x] Utilizadores: Tabela CRUD, pesquisa, filtro role, alterar role inline, suspender/ativar
- [x] Conteudo: Eventos, restaurantes, vendedores, agentes
- [x] Acesso restrito a role=admin (sidebar link condicional + route guard + API 403)

### Seed Data
- 8 Utilizadores (admin + 7 roles)
- 5 Eventos, 8 Produtos, 5 Categorias, 4 Alojamentos, 4 Experiencias, 5 Imoveis, 3 Restaurantes c/ menus

## API Endpoints
- GET /api/health, POST /api/v1/seed
- POST /api/v1/auth/login, /api/v1/auth/verify-otp, GET /api/v1/auth/me
- GET /api/v1/events, /api/v1/marketplace/products, /api/v1/alojamento/properties
- GET /api/v1/turismo/experiences, /api/v1/realestate/properties, /api/v1/restaurantes
- POST /api/v1/entregas/estimate
- GET /api/v1/admin/stats, /api/v1/admin/users, /api/v1/admin/events, /api/v1/admin/restaurants
- PUT /api/v1/admin/users/{id}/role, /api/v1/admin/users/{id}/status

## Backlog
### P0
- [ ] Integracao Multicaixa Express (pagamentos)

### P1
- [ ] Push notifications Firebase
- [ ] Upgrade de role self-service

### P2
- [ ] Wallet B2B
- [ ] Modulo Taxi frontend

## Testes
- iteration_1: Backend 23/23 (100%)
- iteration_2: Frontend empty states (100%)
- iteration_3: Frontend+Backend seed data (100%)
- iteration_4: Admin Panel backend+frontend (100%)
