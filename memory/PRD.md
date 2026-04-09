# TUDOaqui SuperApp - PRD

## Visao Geral
SuperApp modular para Angola. Logo: TUDOAqui. Slogan: a sua vida em um so lugar.
Cores: Vermelho, Amarelo, Preto, Branco.

## Stack
- Frontend: React + TailwindCSS + Lucide React + PWA
- Backend: FastAPI + SQLAlchemy + PostgreSQL
- SMS: Africa's Talking (Sandbox)
- Deploy: Docker Compose + Nginx + Let's Encrypt SSL

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

### PWA (Progressive Web App)
- [x] manifest.json com icones 192x192 e 512x512
- [x] Service Worker (sw.js) com cache offline (stale-while-revalidate)
- [x] Splash screen nativo
- [x] Meta tags Apple/Android para instalacao
- [x] Categorias: lifestyle, shopping, food, travel

### Producao Web / Deploy
- [x] Dockerfile.backend (Python 3.11 + uvicorn)
- [x] Dockerfile.frontend (Node 20 build + Nginx serve)
- [x] docker-compose.yml (PostgreSQL, Backend, Frontend, Nginx, Certbot)
- [x] Nginx configs para 4 dominios (tudoaqui.ao, app, api, admin)
- [x] nginx-spa.conf (cache assets, no-cache SW, SPA fallback)
- [x] Rate limiting (5r/m login, 30r/s API)
- [x] SSL automatico (Let's Encrypt + renovacao)
- [x] Security headers (HSTS, X-Frame-Options, CSP)
- [x] Scripts: deploy.sh, update.sh, backup.sh
- [x] .env.production template
- [x] README-DEPLOY.md com instrucoes completas

## API Endpoints
- Auth: login, verify-otp, me
- Account: profile (GET/PUT), role-request (POST), role-requests (GET)
- Admin: stats, users (GET/PUT role/status), role-requests (GET/approve/reject), events, restaurants, sellers, agents
- Modulos: events, marketplace/products, alojamento/properties, turismo/experiences, realestate/properties, restaurantes, entregas/estimate
- Seed: POST /api/v1/seed

## Dominios Producao
- tudoaqui.ao -> Frontend PWA
- app.tudoaqui.ao -> Frontend PWA
- api.tudoaqui.ao -> Backend FastAPI
- admin.tudoaqui.ao -> Admin Panel

## Backlog
- P1: Integracao Multicaixa Express / Mobile Money
- P2: Compilar APK Android/iOS (Play Store: sincesoft1@gmail.com)
- P3: Wallet B2B (Fase 2)
- P4: Push notifications Firebase
