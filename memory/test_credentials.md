# TUDOaqui - Test Credentials

## Producao (api.tudoaqui.ao)
- **Admin Login**: Telefone: `+244912000000` | Password: `TUDOaqui@2026`
- **Endpoint**: POST `https://api.tudoaqui.ao/api/v1/auth/admin-login`
- **Body**: `{"telefone": "+244912000000", "password": "TUDOaqui@2026"}`
- DB: tudoaqu1_app / Nhimi1980! @ localhost:5432/tudoaqu1_tudoaqui
- SSH: tudoaqu1@95.217.5.136 (key auth via ~/.ssh/deploy_key)

## Dev (preview)
- Admin: +244912000000 | Password: TUDOaqui@2026
- Endpoint: POST `/api/v1/auth/admin-login`
- OTP login also available via POST `/api/v1/auth/login`

## Auth Endpoints
- POST `/api/v1/auth/login` - OTP login (envia SMS)
- POST `/api/v1/auth/verify-otp` - Verifica OTP
- POST `/api/v1/auth/admin-login` - Admin password login
- GET `/api/v1/auth/me` - Dados do utilizador atual
- POST `/api/v1/auth/refresh-token` - Renovar token
