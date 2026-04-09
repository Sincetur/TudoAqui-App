## Test Credentials

### User 1 (Test Cliente)
- **Telefone**: +244923456789
- **Role**: cliente
- **Auth Flow**: OTP-based (phone number login, verify OTP from DB)

### User 2 (Test Cliente - created by testing agent)
- **Telefone**: +244922334455
- **Role**: cliente

### How to get OTP for testing
```sql
su - postgres -c "psql -d tudoaqui -t -A -c \"SELECT codigo FROM otp_codes WHERE telefone='+244923456789' AND verificado=false ORDER BY created_at DESC LIMIT 1;\""
```

### API Base URL
- External: https://7c2cc0aa-d889-4231-8146-9d7173a35f22.preview.emergentagent.com
- Internal: http://localhost:8001

### Auth Flow
1. POST /api/v1/auth/login with {"telefone": "+244923456789"}
2. Get OTP from database (see SQL above)
3. POST /api/v1/auth/verify-otp with {"telefone": "+244923456789", "codigo": "<OTP>"}
4. Use access_token from response as Bearer token

### Notes
- SMS is in SANDBOX mode (Africa's Talking) - OTPs stored in DB, not sent via real SMS
- Rate limiter: 5 login attempts/min per IP, 3 OTPs/5min per phone
