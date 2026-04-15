# TUDOaqui SuperApp - PRD

## Visao Geral
SuperApp modular para Angola. Slogan: a sua vida em um so lugar.

## Empresas
- **Dono:** Nhimi Corporate (NIF: 5001193074), Luanda - Joao Nhimi CEO
- **Desenvolvedor:** Sincesoft (NIF: 2403104787), Luanda

## Producao - LIVE
- `app.tudoaqui.ao` -> Frontend React (Landing + App) - VERIFIED
- `tudoaqui.ao` -> Landing + App 
- `admin.tudoaqui.ao` -> Admin Panel React - VERIFIED
- `api.tudoaqui.ao` -> Backend FastAPI (healthy) - VERIFIED
- Server: 95.217.5.136 (cPanel, user: tudoaqu1, SSH key: ~/.ssh/deploy_key)
- DB: PostgreSQL tudoaqu1_app / tudoaqu1_tudoaqui
- Backend: uvicorn (2 workers, port 8000, @reboot cron)
- Admin: +244912000000 / TUDOaqui@2026 (password login)
- Python 3.9 compativel (Optional[] syntax applied to all 48 files)
- Africa's Talking: API key configurada (atsk_dac37...cacd)

## Implementado
- Login Admin por password (telefone + password) - 2026-04-15
- Endpoint: POST /api/v1/auth/admin-login
- Frontend com toggle SMS/OTP e Admin
- Python 3.9 compatibility fix (48 ficheiros corrigidos)
- Africa's Talking API key configurada em producao
- Frontend re-deployado em app.tudoaqui.ao e admin.tudoaqui.ao
- Backend re-deployado com codigo Python 3.9 compatible

## Modulos
- Eventos, Marketplace, Alojamento, Turismo, Real Estate
- Tuendi Entrega, Tuendi Restaurante, Tuendi Taxi
- Admin Panel, Partners, Payments (Bank Transfer/Cash)

## Backlog
- P2: Push Notifications (FCM)
- P3: Multicaixa Express gateway completo
- P4: Modo offline (SQLite) no Flutter
- P5: Wallet B2B (Fase 2)
- Play Store: AAB build pending (keystore needed)
