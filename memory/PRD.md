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

## DB Producao
- PostgreSQL: user `tudoaqu1_app`, DB `tudoaqu1_tudoaqui`

## Implementado

### Landing Page
- [x] Hero, stats, about, 8 modulos
- [x] Equipa: Nhimi Corporate + Sincesoft + 7 membros
- [x] Investidores: 5.400.000,00 Kz = 0,5%
- [x] Contacto: 3 cards
- [x] **Politica de Privacidade** (/privacidade) - 11 seccoes completas
- [x] **Termos de Servico** (/termos) - 14 seccoes completas
- [x] Footer com links privacidade + termos + NIFs

### Core Backend (15+ modulos, 31 testes)
### Mobile Flutter (7 modulos + carrinho + checkout + GPS)
### Deploy preparado (cPanel + Play Store)

## Backlog
- P2: Push Notifications (FCM)
- P3: Multicaixa Express gateway
- P4: Modo offline (SQLite)
- P5: Wallet B2B
