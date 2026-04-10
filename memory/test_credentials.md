## Test Credentials

> Este ficheiro contém apenas dados de teste locais.
> Nunca colocar API keys, passwords, ou IDs de produção aqui.

### Roles de seed (telefones fictícios para desenvolvimento local)

| Telefone | Nome | Role |
|----------|------|------|
| +244912000000 | Admin TUDOaqui | admin |
| +244911000001 | Carlos Mendes | organizador |
| +244911000002 | Ana Ferreira | vendedor |
| +244911000003 | Manuel Santos | anfitriao |
| +244911000004 | Sofia Neto | agente |
| +244911000005 | Pedro Gomes | vendedor |
| +244911000006 | Joana Silva | anfitriao |

### Obter OTP em ambiente local

```bash
# Substitui <PHONE> pelo número pretendido
docker exec tudoaqui-db psql -U tudoaqui_user -d tudoaqui \
  -t -A -c "SELECT codigo FROM otp_codes WHERE telefone='<PHONE>' AND verificado=false ORDER BY created_at DESC LIMIT 1;"
```

### API local

```
http://localhost:8000
http://localhost:8000/docs
```

### Notas

- Google Maps API Key: configurar em `mobile/flutter/tudoaqui/android/app/src/main/AndroidManifest.xml` via variável de ambiente (ver README-BUILD.md)
- Nunca commitar `.env`, keystores ou chaves reais
