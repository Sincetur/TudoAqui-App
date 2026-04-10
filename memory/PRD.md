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

### Mobile Flutter App
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

### GPS & Google Maps Integration (NOVO - 2026-04-10)
- [x] Backend: WebSocket persiste localizacao GPS na tabela ride_tracking
- [x] Backend: REST endpoints GET/POST /rides/{id}/tracking (fallback WS)
- [x] Backend: ws_router suporta motorista + motoqueiro + admin
- [x] Flutter: LocationService (GPS com geolocator, tracking continuo)
- [x] Flutter: WebSocketService (conexao WS, envio localizacao, join/leave ride)
- [x] Flutter: RideService (API corridas: estimate, request, accept, start, finish, cancel)
- [x] Flutter: RideModel + RideEstimate (modelos Dart)
- [x] Flutter: MotoristaMapScreen (Google Maps com dark theme, markers, polylines, corrida activa, corridas pendentes)
- [x] Flutter: motorista_home.dart integrado com mapa (botao "Abrir Mapa", stats reais do API)
- [x] Android: AndroidManifest.xml com API key Google Maps
- [x] iOS: AppDelegate.swift com API key Google Maps
- [x] Flutter: api_config.dart com endpoints rides/drivers/ws
- [x] Flutter: pubspec.yaml com web_socket_channel dependency
- [x] Bug fix: entrega/router.py - adicionado import Delivery (lint error)

### Deploy
- [x] Docker + Nginx para 4 dominios, scripts deploy/update/backup

## Backlog
- P1: Sincronizar todos os modulos (Backend, Frontend React, e Flutter App)
- P2: Push Notifications (FCM)
- P3: Multicaixa Express (gateway real)
- P4: Modo offline (SQLite)
- P5: Wallet B2B (Fase 2)
