## Test Credentials

### Admin
- **Telefone**: +244912000000
- **Role**: admin

### Regular User
- **Telefone**: +244923456789
- **Role**: vendedor (upgraded from cliente)

### Seed Users
- +244911000001 Carlos Mendes (organizador)
- +244911000002 Ana Ferreira (vendedor)
- +244911000003 Manuel Santos (anfitriao)
- +244911000004 Sofia Neto (agente)
- +244911000005 Pedro Gomes (vendedor)
- +244911000006 Joana Silva (anfitriao)

### Test Users (created by testing agent)
- +244911666666 (vendedor)
- +244911777777 (cliente)
- +244911888888 (cliente)
- +244911999999 (organizador)

### Get OTP
```
su - postgres -c "psql -d tudoaqui -t -A -c \"SELECT codigo FROM otp_codes WHERE telefone='+244912000000' AND verificado=false ORDER BY created_at DESC LIMIT 1;\""
```

### API Base
https://7c2cc0aa-d889-4231-8146-9d7173a35f22.preview.emergentagent.com
