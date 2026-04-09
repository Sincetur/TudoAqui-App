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
- [x] Seed Data Angola
- [x] Admin Panel (stats, users, conteudo, upgrades, pagamentos, parceiros)
- [x] Account (perfil, upgrade, pagamentos, parceiro)

### Modulos Frontend (9 Paginas + Admin)
- [x] Login OTP, Dashboard, Eventos, Marketplace, Alojamento, Turismo, Imobiliario, Entregas, Restaurantes
- [x] Conta + Admin (6 tabs)
- [x] CheckoutModal reutilizavel com suporte parceiros

### Sistema de Parceiros
- [x] Modelo Partner com dados negocio + pagamento
- [x] Registo parceiro (roles: vendedor, anfitriao, organizador, agente, motorista, entregador)
- [x] Config dados pagamento: Unitel Money (numero+titular), Transferencia Bancaria (banco, conta, IBAN, titular), Dinheiro
- [x] Admin: listar, aprovar, suspender, rejeitar parceiros com stats
- [x] Checkout mostra dados pagamento do parceiro (cliente paga directamente)
- [x] Frontend: secção Parceiro na conta, formulario registo, config pagamento
- [x] Frontend: Admin tab Parceiros com cards, metodos pagamento, acções

### Pagamentos
- [x] Transferencia Bancaria BAI (TUDOaqui)
- [x] Unitel Money (parceiro)
- [x] Cash (dinheiro)
- [x] Admin: confirmar/rejeitar pagamentos
- [x] Meus Pagamentos na conta

### Role Upgrade + PWA + Deploy
- [x] Upgrade de role com aprovacao admin
- [x] PWA (manifest, SW, icones)
- [x] Docker + Nginx para 4 dominios
- [x] Scripts deploy/update/backup

## API Endpoints
- Auth: login, verify-otp, me
- Account: profile, role-request
- Admin: stats, users, role-requests, payments, partners
- Payments: bank-info, methods, create, list, comprovativo, admin/all, confirm, reject
- Partners: register, me, me/payment, {id}/payment-info, admin/all, admin/stats, admin/{id}/approve|suspend|reject
- Modulos: events, marketplace, alojamento, turismo, realestate, restaurantes, entregas

## Backlog
- P1: Integracao Multicaixa Express / Mobile Money
- P2: Compilar APK Android/iOS (Play Store: sincesoft1@gmail.com)
- P3: Wallet B2B (Fase 2)
- P4: Push notifications Firebase
