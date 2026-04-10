## Test Credentials

### Admin
- **Telefone**: +244912000000
- **Role**: admin (also has approved driver profile)
- **Driver ID**: 7b73672d-708d-41b3-9c7b-ab4ba2f8099a

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

### Test Ride
- **Ride ID**: 9b47196d-5d07-4f25-840c-e46a7cecbcfc (finalizada, 5 tracking points)

### Get OTP
```
su - postgres -c "psql -d tudoaqui -t -A -c \"SELECT codigo FROM otp_codes WHERE telefone='+244912000000' AND verificado=false ORDER BY created_at DESC LIMIT 1;\""
```

### API Base
https://read-store-15.preview.emergentagent.com

### Google Maps API Key
AIzaSyAqBpyaGG4CxLjfzUwSH4JgUnLWkxUcub0
