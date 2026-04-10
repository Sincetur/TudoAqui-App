# TUDOaqui SuperApp - PRD

## Visao Geral
SuperApp modular para Angola. Logo: TUDOAqui. Slogan: a sua vida em um so lugar.
Cores: Vermelho, Amarelo, Preto, Branco.

## Stack
- Frontend Web: React + TailwindCSS + Lucide React + PWA
- Frontend Mobile: Flutter (multi-modulo)
- Backend: FastAPI + SQLAlchemy + PostgreSQL
- SMS: Africa's Talking (Sandbox)
- Deploy: Docker Compose + Nginx + Let's Encrypt SSL

## Implementado

### Core Backend
- [x] Auth OTP, 7 roles + staff + admin, rate limiting
- [x] Roles: Motorista, Motoqueiro, Proprietario, Guia Turista, Agente Imobiliario, Agente de Viagem, Staff, Admin
- [x] Seed Data Angola, Admin Panel (6 tabs), Account (perfil, upgrade, parceiro, pagamentos)

### Sistema de Parceiros
- [x] 7 tipos, config pagamento (Unitel Money + Transferencia + Cash), admin approval

### Pagamentos
- [x] Transferencia BAI, Unitel Money, Cash, admin confirm/reject

### Frontend Web (React PWA)
- [x] 9 paginas + Admin (6 tabs)
- [x] CheckoutModal com suporte parceiros
- [x] PWA (manifest, SW, icones)

### Mobile Android TWA
- [x] Projecto Android completo, icones, splash, assetlinks
- [x] Scripts build + ficha Play Store

### Mobile Flutter App (NOVO)
- [x] Projecto Flutter completo com 7 modulos por role
- [x] Login OTP (+244) com auto-login e secure storage
- [x] Dashboard Cliente: grid 8 modulos, search, promos, pagamentos, perfil
- [x] Dashboard Motorista: toggle online/offline, stats corridas/ganhos, procura corridas
- [x] Dashboard Motoqueiro: toggle online/offline, stats entregas/ganhos
- [x] Dashboard Proprietario: pedidos, produtos/catalogo, receita, avaliacao
- [x] Dashboard Guia Turista: experiencias, reservas, receita
- [x] Dashboard Agente Imobiliario: imoveis, clientes, receita
- [x] Dashboard Agente de Viagem: pacotes, clientes, receita
- [x] Routing automatico por role (main.dart)
- [x] Tema dark TUDOaqui (vermelho + amarelo + preto)
- [x] Widgets reutilizaveis: StatusBadge, TCard, StatCard, PrimaryButton, EmptyState
- [x] ApiService (HTTP + auth), AuthService (Provider state management)
- [x] Modelos: UserModel, PartnerModel, PaymentModel

### Deploy
- [x] Docker + Nginx para 4 dominios, scripts deploy/update/backup

## Backlog
- P1: Integrar Flutter com endpoints reais (CRUD completo cada modulo)
- P2: GPS + Google Maps (motorista/motoqueiro)
- P3: WebSockets real-time (corridas, entregas)
- P4: Push Notifications (FCM)
- P5: Multicaixa Express (gateway real)
- P6: Modo offline (SQLite)
- P7: Wallet B2B (Fase 2)
