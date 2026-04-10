# TUDOaqui SuperApp - PRD

## Visao Geral
SuperApp modular para Angola. Logo: TUDOAqui. Slogan: a sua vida em um so lugar.
Cores: Vermelho, Amarelo, Preto, Branco.

## Stack
- Frontend: React + TailwindCSS + Lucide React + PWA
- Backend: FastAPI + SQLAlchemy + PostgreSQL
- SMS: Africa's Talking (Sandbox)
- Deploy: Docker Compose + Nginx + Let's Encrypt SSL
- Mobile: Android TWA (Trusted Web Activity)

## Implementado

### Core
- [x] Auth OTP (telefone), 7 roles + staff + admin, rate limiting
- [x] Roles: Motorista, Motoqueiro, Proprietario, Guia Turista, Agente Imobiliario, Agente de Viagem, Staff, Admin
- [x] Seed Data Angola
- [x] Admin Panel (6 tabs: overview, users, parceiros, pagamentos, upgrades, conteudo)
- [x] Account (perfil, upgrade, parceiro, pagamentos)

### Modulos Frontend (9 Paginas + Admin)
- [x] Login OTP, Dashboard, Eventos, Marketplace, Alojamento, Turismo, Imobiliario, Entregas, Restaurantes
- [x] CheckoutModal reutilizavel com suporte parceiros

### Sistema de Parceiros (7 tipos)
- [x] Motorista, Motoqueiro, Proprietario, Staff, Guia Turista, Agente Imobiliario, Agente de Viagem
- [x] Config pagamento: Unitel Money + Transferencia Bancaria + Dinheiro
- [x] Admin: listar, aprovar, suspender, rejeitar
- [x] Cliente paga directamente ao parceiro

### Pagamentos
- [x] Transferencia Bancaria BAI (TUDOaqui)
- [x] Unitel Money (parceiro)
- [x] Cash (dinheiro)
- [x] Admin: confirmar/rejeitar pagamentos

### Mobile Android (TWA)
- [x] Projecto Android completo (Gradle, AndroidManifest, resources)
- [x] Icones em 5 resolucoes (mdpi a xxxhdpi) + Play Store 512x512
- [x] Splash screen TUDOaqui (fundo preto, logo vermelho)
- [x] Cores nativas (statusbar vermelho, navbar preto)
- [x] Digital Asset Links (assetlinks.json) para verificacao TWA
- [x] Scripts: generate-keystore.sh, build-apk.sh
- [x] Ficha Play Store pronta (descricao, palavras-chave, assets)
- [x] Guia completo README-BUILD.md
- [x] twa-manifest.json com shortcuts (Eventos, Marketplace, Restaurantes)
- [x] Permissoes: Internet, Camera, Localizacao, Notificacoes
- [x] Deep links para app.tudoaqui.ao
- [x] Nginx configurado para servir assetlinks.json

### PWA + Deploy
- [x] PWA (manifest, SW, icones)
- [x] Docker + Nginx para 4 dominios
- [x] Scripts deploy/update/backup

## API Endpoints
- Auth: login, verify-otp, me
- Account: profile, role-request
- Admin: stats, users, role-requests, payments, partners
- Payments: bank-info, methods, create, list, comprovativo, admin/all, confirm, reject
- Partners: tipos, register, me, me/payment, {id}/payment-info, admin/all, admin/stats, admin/{id}/approve|suspend|reject
- Modulos: events, marketplace, alojamento, turismo, realestate, restaurantes, entregas

## Mobile Config
- Package: ao.tudoaqui.app
- Min SDK: 23 (Android 6.0)
- Target SDK: 34
- Dominio: app.tudoaqui.ao
- Conta Play Store: sincesoft1@gmail.com

## Backlog
- P1: Integracao Multicaixa Express / Mobile Money (gateway real)
- P2: Versao iOS (Apple Developer + Mac necessario)
- P3: Wallet B2B (Fase 2)
- P4: Push Notifications Firebase
