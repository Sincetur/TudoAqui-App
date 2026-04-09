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
- **Pagamentos:** Multicaixa Express + Mobile Money (pendente)
- **SMS:** Africa's Talking (Sandbox mode)

## Modulos do Sistema

### Core
- [x] Users, Roles, Auth OTP
- [x] Rate Limiting (in-memory)
- [x] SMS Africa's Talking (Sandbox)

### Tuendi
- [x] Taxi (Corridas) - Backend completo, Frontend "Em breve"
- [x] Drivers (Motoristas)
- [x] Entrega (Delivery de pacotes) - Backend + Frontend completos
- [x] Restaurante (Delivery de comida) - Backend + Frontend completos

### Eventos
- [x] Backend completo (Models, Schemas, Service, Router)
- [x] Frontend completo (Lista, Detalhe, Pesquisa)

### Marketplace
- [x] Backend completo (Models, Schemas, Service, Router)
- [x] Frontend completo (Produtos, Categorias, Vendedores)

### Alojamento
- [x] Backend completo (Models, Schemas, Service, Router)
- [x] Frontend completo (Propriedades, Pesquisa, Detalhe)

### Turismo
- [x] Backend completo (Models, Schemas, Service, Router)
- [x] Frontend completo (Experiencias, Pesquisa, Detalhe)

### Real Estate (Imobiliario)
- [x] Backend completo (Models, Schemas, Service, Router)
- [x] Frontend completo (Imoveis, Agentes, Tabs, Pesquisa, Detalhe)

### Payments
- [x] Ledger centralizado
- [ ] Multicaixa Express (pendente integracao)
- [ ] Mobile Money (pendente integracao)

### Notifications
- [x] Push + WebSocket base

## Frontend Implementado

### Estrutura
```
/app/frontend/src/
  App.js                 # Router principal com 8 rotas de modulos
  api.js                 # API client com todos os endpoints
  index.css              # CSS variaveis + animacoes
  components/
    Layout.js            # Sidebar + PageHeader + EmptyState + Badge + ItemCard
  pages/
    Login.js             # Login OTP (telefone + verificacao)
    Dashboard.js         # Dashboard com cards de modulos e stats
    Events.js            # Eventos (lista + detalhe)
    Marketplace.js       # Marketplace (produtos + categorias)
    Alojamento.js        # Alojamento (propriedades)
    Turismo.js           # Turismo (experiencias)
    Imoveis.js           # Imobiliario (imoveis + agentes tabs)
    Entregas.js          # Entregas (lista + estimativa preco)
    Restaurantes.js      # Restaurantes (lista + menu detalhe)
```

### Design System
- Theme: Dark mode (bg-dark-950, surfaces bg-dark-900)
- Primary: Red (#dc2626)
- Accent: Yellow (#eab308)
- Sidebar navigation (desktop) + Bottom nav (mobile)
- Componentes reutilizaveis: PageHeader, EmptyState, LoadingState, ItemCard, Badge

## API Endpoints Validados (Testados)

### Health
- GET /api/health - 200 OK

### Auth
- POST /api/v1/auth/login
- POST /api/v1/auth/verify-otp
- GET /api/v1/auth/me

### Todos os modulos
- GET /api/v1/events, /api/v1/marketplace/products, /api/v1/alojamento/properties
- GET /api/v1/turismo/experiences, /api/v1/realestate/properties, /api/v1/restaurantes
- POST /api/v1/entregas/estimate (auth required)

## Backlog

### P0 - Critico
- [ ] Integracao Multicaixa Express
- [ ] Seed data para demonstracao (popular BD com dados demo)

### P1 - Alta
- [ ] Push notifications Firebase
- [ ] Formularios de criacao (criar evento, produto, propriedade, etc.)

### P2 - Media
- [ ] Wallet B2B
- [ ] Painel Admin Web
- [ ] Modulo Taxi frontend completo

## Historico de Implementacoes

### Abril 2026 (Sessao 2)
1. Frontend completo com 8 paginas de modulos
2. Layout com sidebar + mobile bottom nav
3. Cores atualizadas: Vermelho/Amarelo/Preto/Branco
4. Slogan: "a sua vida em um so lugar"
5. Testes frontend: 100% passed (iteration_2)

### Abril 2026 (Sessao 1)
1. Criacao de server.py (ponte para uvicorn)
2. Instalacao PostgreSQL no ambiente
3. Registo routers entrega/restaurante no main.py
4. Fix atributos Driver no entrega router
5. Frontend React scaffold (Login + Dashboard)
6. Testes backend: 23/23 passed (iteration_1)

### Janeiro 2026
1. Correcoes de seguranca
2. SMS Africa's Talking configurado
3. Todos os modulos backend completos
