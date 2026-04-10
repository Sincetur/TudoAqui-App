# TUDOaqui - Guia de Deploy para Producao

## Arquitectura

```
tudoaqui.ao         -> Frontend React (Landing + App)
app.tudoaqui.ao     -> Frontend React (App directo)
admin.tudoaqui.ao   -> Frontend React (Admin panel)
api.tudoaqui.ao     -> Backend FastAPI (API REST)
```

Todos os dominios do frontend usam a **mesma build React**. A diferenciacao e feita pela rota:
- `/` -> Landing page (utilizadores nao autenticados)
- `/login` -> Login OTP
- `/admin` -> Admin panel (requer role admin)
- `/*` -> Modulos da app

---

## 1. Deploy cPanel via SSH

### Pre-requisitos no servidor:
- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (ou instalar via yum/apt)
- Node.js 18+ (para build, ja incluido na build)

### Passo a passo:

```bash
# 1. No ambiente de desenvolvimento, gerar o pacote:
bash /app/deploy/cpanel_deploy.sh

# 2. Transferir para o servidor:
scp ~/deploy_bundle/../tudoaqui_deploy.tar.gz tudoaqui@servidor:~/

# 3. No servidor via SSH:
ssh tudoaqui@servidor
mkdir -p ~/deploy && cd ~/deploy
tar -xzf ~/tudoaqui_deploy.tar.gz
bash install_server.sh
```

### Configuracao manual no cPanel:

1. **PostgreSQL**:
   - Criar base de dados: `tudoaqui`
   - Criar utilizador: `tudoaqui_user`
   - Atribuir permissoes

2. **Proxy reverso para api.tudoaqui.ao**:
   - No cPanel > Application Manager ou .htaccess:
   ```apache
   # .htaccess em public_html/api.tudoaqui.ao/
   RewriteEngine On
   RewriteRule ^(.*)$ http://127.0.0.1:8000/$1 [P,L]
   ```

3. **SSL**: Activar Let's Encrypt para todos os 4 dominios

4. **Editar .env**: `~/tudoaqui_api/.env` com credenciais reais

5. **Redis**: Se nao disponivel no cPanel:
   ```bash
   # Instalar Redis (se tem acesso root)
   sudo apt install redis-server
   sudo systemctl enable redis
   ```

---

## 2. Deploy Play Store (Android)

### Pre-requisitos:
- Conta Google Play Developer ($25)
- Flutter SDK 3.2+
- Java 17+
- Keystore de assinatura

### Gerar keystore:
```bash
keytool -genkey -v \
  -keystore keystore/tudoaqui-release.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias tudoaqui \
  -dname "CN=TUDOaqui, OU=Nhimi Corporate, O=Nhimi Corporate, L=Luanda, C=AO"
```

### Configurar key.properties:
```properties
storePassword=SUA_SENHA
keyPassword=SUA_SENHA
keyAlias=tudoaqui
storeFile=../../keystore/tudoaqui-release.jks
```

### Build:
```bash
cd /app/mobile/flutter/tudoaqui
flutter clean && flutter pub get
flutter build appbundle --release  # AAB para Play Store
flutter build apk --release --split-per-abi  # APK directo
```

### Upload para Play Console:
1. Ir a https://play.google.com/console
2. Criar app > Preencher metadata (ver `/app/deploy/playstore/metadata.md`)
3. Internal testing > Upload AAB
4. Testar em dispositivos reais
5. Production > Submit for review

---

## 3. Ficheiros Importantes

| Ficheiro | Descricao |
|----------|-----------|
| `deploy/cpanel_deploy.sh` | Script que gera pacote de deploy |
| `deploy/playstore/metadata.md` | Metadata para Google Play Store |
| `deploy/build_playstore.sh` | Script de build APK/AAB |
| `deploy/docker-compose.yml` | Docker Compose producao |
| `frontend/build/` | Frontend compilado |
| `backend/.env.production` | Template .env backend |

---

## 4. Informacoes da Empresa

**Dono:** Nhimi Corporate (NIF: 5001193074)
- Representante: Joao Nhimi (CEO)
- Email: nhimi@nhimi.com | Tel: +244 924 865 667

**Desenvolvedor:** Sincesoft - Sinceridade Service (NIF: 2403104787)
- Email: apoioaocliente@3s-ao.com | Tel: +244 951 064 945
- Website: https://3s-ao.com
