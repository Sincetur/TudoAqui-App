## Test Credentials

### Admin User
- **Telefone**: +244912000000
- **Nome**: Admin TUDOaqui
- **Role**: admin
- **Auth Flow**: OTP-based

### User 1 (Test Cliente)
- **Telefone**: +244923456789
- **Role**: cliente
- **Auth Flow**: OTP-based

### Seed Users (criados pelo seed)
- +244912000000 - Admin TUDOaqui (admin)
- +244911000001 - Carlos Mendes (organizador)
- +244911000002 - Ana Ferreira (vendedor)
- +244911000003 - Manuel Santos (anfitriao)
- +244911000004 - Sofia Neto (agente)
- +244911000005 - Pedro Gomes (vendedor)
- +244911000006 - Joana Silva (anfitriao)

### How to get OTP
```sql
su - postgres -c "psql -d tudoaqui -t -A -c \"SELECT codigo FROM otp_codes WHERE telefone='+244923456789' AND verificado=false ORDER BY created_at DESC LIMIT 1;\""
```

### API Base URL
- External: https://7c2cc0aa-d889-4231-8146-9d7173a35f22.preview.emergentagent.com

### Auth Flow
1. POST /api/v1/auth/login with {"telefone": "+244923456789"}
2. Get OTP from database (see SQL above)
3. POST /api/v1/auth/verify-otp with {"telefone": "+244923456789", "codigo": "<OTP>"}
4. Use access_token as Bearer token

### Notes
- SMS in SANDBOX mode - OTPs stored in DB
- PostgreSQL must be running: pg_ctlcluster 15 main start
- Seed data: POST /api/v1/seed
