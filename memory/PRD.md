# TUDOaqui SuperApp - Product Requirements Document

## Visão Geral
SuperApp modular para Angola integrando múltiplos serviços numa única plataforma.

## Stack Tecnológica
- **Mobile:** Flutter (Dart) - Android & iOS
- **Backend:** FastAPI (Python) + NestJS (TypeScript)
- **Database:** PostgreSQL + Redis
- **Pagamentos:** Multicaixa Express + Mobile Money

## Módulos do Sistema

### Implementados
- [x] Core (Users, Roles, Auth OTP)
- [x] Tuendi Taxi (Corridas)
- [x] Drivers (Motoristas)
- [x] Payments (Pagamentos + Ledger)
- [x] Notifications (Push + WebSocket)
- [x] Wallet (Fase 2 - preparado)

### Pendentes
- [ ] Tuendi Entrega
- [ ] Tuendi Restaurante
- [ ] Eventos (Tickets + QR + Check-in)
- [ ] Marketplace (Multi-vendedor)
- [ ] Alojamento (modelo Airbnb)
- [ ] Turismo (Experiências)
- [ ] Real Estate (Imobiliário)
- [ ] Wallet B2B completo

## Histórico de Implementações

### Janeiro 2026 - Correções de Segurança
**Vulnerabilidades Corrigidas:**
1. ✅ SECRET_KEY removido do código - agora obrigatório via .env
2. ✅ OTP usando `secrets` (criptograficamente seguro) em vez de `random`
3. ✅ Rate limiting implementado no login e verify-otp
4. ✅ Validação de telefone com biblioteca `phonenumbers`
5. ✅ Lint errors corrigidos em todo o backend

**Arquivos Modificados:**
- `/app/backend/src/config.py` - SECRET_KEY sem default
- `/app/backend/src/auth/service.py` - OTP seguro + correções lint
- `/app/backend/src/auth/router.py` - Rate limiting + validação telefone
- `/app/backend/src/auth/rate_limiter.py` - Novo módulo de rate limiting
- `/app/backend/.env` - Criado com SECRET_KEY segura
- `/app/backend/.env.example` - Atualizado com instruções
- Múltiplos arquivos - Correções de lint (E712, F841, E722)

## User Personas
1. **Cliente** - Solicita corridas, compra tickets, faz pedidos
2. **Motorista** - Aceita corridas, tracking em tempo real
3. **Entregador** - Entregas Tuendi
4. **Organizador** - Cria eventos, gere tickets
5. **Vendedor** - Vende no Marketplace
6. **Anfitrião** - Aloja hóspedes (Airbnb local)
7. **Agente** - Imobiliário
8. **Staff** - Check-in eventos
9. **Admin** - Gestão completa

## Requisitos Core (P0)
- Autenticação OTP via SMS
- Rate limiting em endpoints sensíveis
- Gestão de corridas em tempo real
- Pagamentos Multicaixa/Mobile Money
- WebSocket para tracking

## Backlog

### P0 - Crítico
- [ ] Implementar SMS real (Twilio/Africa's Talking)
- [ ] Integração Multicaixa Express
- [ ] Testes automatizados

### P1 - Alta Prioridade
- [ ] Módulo de Eventos completo
- [ ] Módulo Marketplace
- [ ] Push notifications Firebase

### P2 - Média Prioridade
- [ ] Módulo Alojamento
- [ ] Módulo Turismo
- [ ] Módulo Real Estate
- [ ] Wallet B2B completo

## Próximas Tarefas
1. Configurar SMS provider real
2. Implementar testes de integração para auth
3. Finalizar módulo de Eventos
4. Integrar pagamentos Multicaixa
