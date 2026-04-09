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
- [x] Admin Panel (stats, gestao users, conteudo, aprovacao upgrades, gestao pagamentos)
- [x] Account (perfil, editar nome/email, solicitar upgrade role, historico, meus pagamentos)

### Frontend (9 Paginas + Admin)
- [x] Login OTP, Dashboard, Eventos, Marketplace, Alojamento, Turismo, Imobiliario, Entregas, Restaurantes
- [x] Conta (perfil + upgrade + pagamentos), Admin (5 tabs: overview, users, pagamentos, upgrades, conteudo)
- [x] Formularios criacao (Eventos, Marketplace, Alojamento, Turismo)
- [x] Carrinho restaurante, estimativa entrega
- [x] CheckoutModal reutilizavel em todos os modulos

### Pagamentos (Transferencia Bancaria + Cash)
- [x] Transferencia Bancaria BAI (Conta: 20967898310001, IBAN: AO06 0040 0000 0967898310151, SWIFT: BAIPAOLU)
- [x] Pagamento em Dinheiro (Cash)
- [x] CheckoutModal com dados bancarios, copy IBAN, comprovativo
- [x] Admin: tab Pagamentos (stats, filtros, confirmar/rejeitar)
- [x] Meus Pagamentos na pagina Conta
- [x] Botoes Comprar/Pagar/Reservar em: Marketplace, Restaurantes, Eventos, Alojamento, Turismo, Entregas
- [x] Multicaixa Express marcado como "em breve"

### Role Upgrade System
- [x] User solicita upgrade com motivo
- [x] Admin aprova/rejeita com nota
- [x] Aprovacao altera role automaticamente
- [x] Historico de pedidos visivel ao user
- [x] Prevencao de pedidos duplicados

### PWA (Progressive Web App)
- [x] manifest.json com icones 192x192 e 512x512
- [x] Service Worker (sw.js) com cache offline
- [x] Splash screen nativo
- [x] Meta tags Apple/Android para instalacao

### Producao Web / Deploy
- [x] Dockerfiles (backend + frontend)
- [x] docker-compose.yml (PostgreSQL, Backend, Frontend, Nginx, Certbot)
- [x] Nginx configs para 4 dominios
- [x] SSL automatico (Let's Encrypt)
- [x] Scripts: deploy.sh, update.sh, backup.sh
- [x] README-DEPLOY.md com instrucoes completas

## API Endpoints
- Auth: login, verify-otp, me
- Account: profile (GET/PUT), role-request (POST), role-requests (GET)
- Admin: stats, users, role-requests, events, restaurants, sellers, agents
- Payments: bank-info, methods, create, list, comprovativo, admin/all, admin/stats, confirm, reject
- Modulos: events, marketplace, alojamento, turismo, realestate, restaurantes, entregas
- Seed: POST /api/v1/seed

## Backlog
- P1: Integracao Multicaixa Express / Mobile Money
- P2: Compilar APK Android/iOS (Play Store: sincesoft1@gmail.com)
- P3: Wallet B2B (Fase 2)
- P4: Push notifications Firebase
