# TUDOaqui SuperApp - PRD

## Visao Geral
SuperApp modular para Angola. Logo: TUDOAqui. Slogan: a sua vida em um so lugar.
Cores: Vermelho, Amarelo, Preto, Branco.

## Stack
- Frontend Web: React + TailwindCSS + Lucide React + PWA
- Frontend Mobile: Flutter (multi-modulo) em `mobile/flutter/tudoaqui/`
- Backend: FastAPI + SQLAlchemy + PostgreSQL
- SMS: Africa's Talking (Sandbox)
- Deploy: Docker Compose + Nginx + Let's Encrypt SSL

## Implementado

### Core Backend
- [x] Auth OTP, 7 roles + staff + admin, rate limiting (auto Redis/InMemory fallback)
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
- [x] Signing config via env vars (CI/CD) e keystore local

### Mobile Flutter App
- [x] Projecto Flutter completo com 7 modulos por role
- [x] Login OTP (+244) com auto-login e secure storage
- [x] Dashboard Cliente: grid 8 modulos com navegacao para ecras CRUD reais
- [x] Ecras CRUD Cliente: Eventos, Marketplace, Alojamento, Turismo, Imobiliario, Entregas, Restaurantes
- [x] Dashboard Motorista: toggle online/offline, stats corridas/ganhos, Google Maps
- [x] Dashboard Motoqueiro: toggle online/offline, entregas pendentes GPS, aceitar/completar
- [x] Dashboard Proprietario: Pedidos CRUD real, Produtos CRUD com dialogo criar
- [x] Dashboard Guia Turista: Experiencias CRUD com dialogo criar, Reservas lista
- [x] Dashboard Agente Imobiliario: Imoveis CRUD com dialogo criar, Leads/clientes
- [x] Dashboard Agente de Viagem: Experiencias lista, Clientes
- [x] Routing automatico por role (main.dart)
- [x] Tema dark TUDOaqui (vermelho + amarelo + preto)
- [x] Widgets reutilizaveis: StatusBadge, TCard, StatCard, PrimaryButton, EmptyState
- [x] ApiService (HTTP + auth), AuthService (Provider state management)
- [x] ModuleService (CRUD generico para todos 7 modulos)
- [x] Modelos: UserModel, PartnerModel, PaymentModel, RideModel, RideEstimate

### GPS & Google Maps Integration
- [x] Backend: WebSocket persiste localizacao GPS na tabela ride_tracking
- [x] Backend: REST endpoints GET/POST /rides/{id}/tracking
- [x] Flutter: LocationService, WebSocketService, RideService
- [x] Flutter: MotoristaMapScreen (Google Maps dark theme, markers, polylines)
- [x] Flutter: motorista_home.dart integrado com mapa

### Seguranca e Configuracao (2026-04-10)
- [x] Google Maps API Key removida do codigo — via env vars / manifest placeholders
- [x] iOS: leitura de chave via Info.plist com fallback gracioso
- [x] Rate limiter: auto-detect Redis com fallback InMemory
- [x] Android signing: env vars (CI/CD) + key.properties (local)
- [x] Flutter Android: Gradle files completos (build, settings, wrapper, properties)
- [x] .gitignore limpo e completo (sem duplicados)
- [x] .env.example e .env.production.example documentados
- [x] frontend/lib/DEPRECATED.md marca projecto BLoC antigo
- [x] test_credentials.md limpo (sem IDs reais, URLs externas, API keys)

### Deploy
- [x] Docker + Nginx para 4 dominios, scripts deploy/update/backup

## Backlog
- P1: Push Notifications (FCM)
- P2: Multicaixa Express (gateway real)
- P3: Modo offline (SQLite)
- P4: Wallet B2B (Fase 2)
