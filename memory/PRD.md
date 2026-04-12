# TUDOaqui SuperApp - PRD

## Visao Geral
SuperApp modular para Angola. Slogan: a sua vida em um so lugar.

## Empresas
- **Dono:** Nhimi Corporate (NIF: 5001193074), Luanda - Joao Nhimi CEO
- **Desenvolvedor:** Sincesoft (NIF: 2403104787), Luanda

## Producao - LIVE
- `app.tudoaqui.ao` -> Frontend React (HTTP/2 200)
- `tudoaqui.ao` -> Landing + App (HTTP/2 200)
- `admin.tudoaqui.ao` -> Admin Panel (HTTP/2 200)
- `api.tudoaqui.ao` -> Backend FastAPI (healthy)
- Server: 95.217.5.136 (cPanel, user: tudoaqu1)
- DB: PostgreSQL tudoaqu1_app / tudoaqu1_tudoaqui
- Redis: PONG
- Backend: uvicorn (2 workers, port 8000, @reboot cron)
- Admin: +244912000000 (OTP auth)
- Python 3.9 compativel (Optional[] syntax applied)

## Backlog
- P2: Push Notifications (FCM)
- P3: Multicaixa Express gateway
- P4: Modo offline (SQLite)
- P5: Wallet B2B
- Play Store: AAB build pending (keystore needed)
