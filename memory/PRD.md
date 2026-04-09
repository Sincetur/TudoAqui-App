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
- [x] Users, Roles, Auth OTP
- [x] Rate Limiting
- [x] SMS Africa's Talking (Sandbox)
- [x] Seed Data (Dados demo Angola)

### Frontend Completo (8 Modulos)
- [x] Dashboard com cards de modulos e stats
- [x] Eventos - Lista (5 seed), detalhe, pesquisa, formulario criacao
- [x] Marketplace - Produtos (8 seed), categorias (5), pesquisa, formulario criacao
- [x] Alojamento - Propriedades (4 seed), pesquisa, formulario criacao
- [x] Turismo - Experiencias (4 seed), pesquisa, formulario criacao
- [x] Imobiliario - Imoveis (5 seed) + Agentes (1), tabs, pesquisa
- [x] Entregas - Lista + Estimativa preco com formulario
- [x] Restaurantes - Lista (3 seed) + Menu + Carrinho de compras

### Design System
- Theme: Dark mode (bg-dark-950)
- Primary: Red (#dc2626), Accent: Yellow (#eab308)
- Sidebar desktop + Bottom nav mobile
- Componentes: Layout, PageHeader, EmptyState, LoadingState, ItemCard, Badge, FormModal

### Backend Completo
- [x] Todos os routers registados e funcionais
- [x] Seed data com dados reais de Angola (Luanda)
- [x] Endpoint POST /api/v1/seed (idempotente)

## Seed Data
- 5 Eventos (Festival Musica, Expo Tech, Semba, Maratona, Feira Livro)
- 8 Produtos (Moda, Electronica, Casa, Alimentacao, Desporto)
- 5 Categorias Marketplace
- 4 Propriedades Alojamento (Ilha, Talatona, Miramar, Cabo Ledo)
- 4 Experiencias Turismo (Tour Luanda, Safari Kissama, Workshop Culinaria, Barco)
- 5 Imoveis (Apartamentos, Vivenda, Terreno, Escritorio)
- 1 Agente Imobiliario
- 3 Restaurantes com menus completos (Muamba da Mama, Sushi Lounge, Burger Republic)

## API Endpoints

### Health & Admin
- GET /api/health
- POST /api/v1/seed

### Auth
- POST /api/v1/auth/login
- POST /api/v1/auth/verify-otp
- GET /api/v1/auth/me

### Modulos
- GET /api/v1/events
- GET /api/v1/marketplace/products, /api/v1/marketplace/categories
- GET /api/v1/alojamento/properties
- GET /api/v1/turismo/experiences
- GET /api/v1/realestate/properties, /api/v1/realestate/agents
- GET /api/v1/restaurantes, /api/v1/restaurantes/{id}/menu
- POST /api/v1/entregas/estimate

## Backlog

### P0 - Critico
- [ ] Integracao Multicaixa Express (pagamentos)

### P1 - Alta
- [ ] Push notifications Firebase
- [ ] Upgrade de role do utilizador (cliente -> organizador/vendedor)

### P2 - Media
- [ ] Wallet B2B
- [ ] Painel Admin Web
- [ ] Modulo Taxi frontend completo

## Testes
- iteration_1.json: Backend 23/23 (100%)
- iteration_2.json: Frontend empty states (100%)
- iteration_3.json: Backend 12/12 + Frontend seed data + forms + cart (100%)
