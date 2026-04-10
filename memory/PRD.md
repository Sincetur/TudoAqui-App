# TUDOaqui SuperApp - PRD

## Visao Geral
SuperApp modular para Angola. Logo: TUDOAqui. Slogan: a sua vida em um so lugar.
Cores: Vermelho (#dc2626), Amarelo (#eab308), Preto, Branco.

## Empresas
- **Dono:** Nhimi Corporate (NIF: 5001193074), Luanda - Joao Nhimi CEO
- **Desenvolvedor:** Sincesoft / Sinceridade Service (NIF: 2403104787), Luanda

## Stack
- Frontend Web: React + TailwindCSS + Lucide React + PWA
- Frontend Mobile: Flutter em `mobile/flutter/tudoaqui/`
- Backend: FastAPI + SQLAlchemy + PostgreSQL + Redis
- Deploy: cPanel SSH (4 dominios) + Docker Compose + Play Store

## Dominios
- `tudoaqui.ao` -> Landing + App
- `app.tudoaqui.ao` -> App directo
- `admin.tudoaqui.ao` -> Admin
- `api.tudoaqui.ao` -> Backend API

## Implementado

### Landing Page
- [x] Hero, stats (8 modulos, 18 provincias), about
- [x] 8 modulos com icones e descricao
- [x] Equipa: Nhimi Corporate + Sincesoft + 7 membros
- [x] Investidores: 5.400.000,00 Kz = 0,5% participacao
- [x] Contacto: 3 cards (email, tel, suporte)
- [x] Footer com NIFs
- [x] Navbar com smooth scroll + mobile hamburger
- [x] Botao "Entrar" -> /login

### Core Backend
- [x] Auth OTP, 7 roles + staff + admin, rate limiting
- [x] Alembic migrations (2 versoes)
- [x] pytest (16 testes isolados + 15 endpoint)
- [x] Matching service integrado no rides (haversine + score)

### Deploy Preparado
- [x] `deploy/cpanel_deploy.sh` - Script completo cPanel SSH
- [x] `deploy/build_playstore.sh` - Build APK/AAB
- [x] `deploy/playstore/metadata.md` - Metadata Play Store
- [x] `README-DEPLOY.md` - Guia completo
- [x] Frontend build producao (2.2MB)
- [x] .htaccess SPA + cache + gzip

### Mobile Flutter App
- [x] 7 modulos CRUD + carrinho + checkout
- [x] GPS, Maps, WebSocket, CartProvider
- [x] applicationId: ao.tudoaqui.app

## Backlog
- P2: Push Notifications (FCM)
- P3: Multicaixa Express gateway real
- P4: Modo offline (SQLite)
- P5: Wallet B2B (Fase 2)
