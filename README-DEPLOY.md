# TUDOaqui SuperApp - Guia de Deploy em Producao

## Arquitectura

```
                    Internet
                       |
                    [Nginx]
                    /  |   \
   tudoaqui.ao    api   admin
   app.tudoaqui.ao     .tudoaqui.ao
          |            |         |
      [Frontend]   [Backend]  [Frontend]
       (React)    (FastAPI)   (rota /admin)
                       |
                  [PostgreSQL]
```

## Dominios Necessarios

| Dominio             | Servico               |
|---------------------|-----------------------|
| tudoaqui.ao         | Frontend PWA          |
| app.tudoaqui.ao     | Frontend PWA          |
| api.tudoaqui.ao     | Backend FastAPI       |
| admin.tudoaqui.ao   | Admin Panel (React)   |

## Pre-requisitos no Servidor

- Ubuntu 20.04+ ou Debian 11+
- Minimo 2GB RAM, 20GB disco
- Docker e Docker Compose instalados (o script instala automaticamente)
- Portas 80 e 443 abertas no firewall
- DNS dos 4 dominios a apontar para o IP do servidor

## Passo a Passo

### 1. Configurar DNS

No seu registrar de dominio, criar os registos A:

```
A    tudoaqui.ao         ->  IP_DO_SERVIDOR
A    app.tudoaqui.ao     ->  IP_DO_SERVIDOR
A    api.tudoaqui.ao     ->  IP_DO_SERVIDOR
A    admin.tudoaqui.ao   ->  IP_DO_SERVIDOR
```

### 2. Preparar Variaveis de Ambiente

Copiar o ficheiro de exemplo e preencher com valores reais:

```bash
cp deploy/.env.production .env
nano .env
```

Gerar valores seguros:
```bash
# Gerar SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

# Gerar DB_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

### 3. Deploy Automatico (via SSH)

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh IP_DO_SERVIDOR root
```

O script faz automaticamente:
1. Instala Docker no servidor (se necessario)
2. Envia todos os ficheiros via rsync
3. Configura SSL com Let's Encrypt
4. Faz build e inicia os containers
5. Popula a base de dados com seed data
6. Verifica se tudo esta a funcionar

### 4. Criar Utilizador Admin

Apos o deploy, aceder ao servidor e promover um utilizador:

```bash
ssh root@IP_DO_SERVIDOR
cd /opt/tudoaqui
docker compose exec db psql -U tudoaqui_user -d tudoaqui -c \
  "UPDATE users SET role='admin' WHERE telefone='+244912000000';"
```

### 5. Verificar

- https://tudoaqui.ao - App principal (PWA)
- https://api.tudoaqui.ao/docs - Documentacao API
- https://admin.tudoaqui.ao - Painel Admin

## Scripts Utilitarios

### Actualizar App (sem downtime)
```bash
./deploy/update.sh IP_DO_SERVIDOR root
```

### Backup da Base de Dados
```bash
./deploy/backup.sh IP_DO_SERVIDOR root
```

### Ver Logs
```bash
ssh root@IP_DO_SERVIDOR
cd /opt/tudoaqui
docker compose logs -f backend    # Logs do backend
docker compose logs -f frontend   # Logs do frontend
docker compose logs -f nginx      # Logs do nginx
```

### Reiniciar Servicos
```bash
ssh root@IP_DO_SERVIDOR
cd /opt/tudoaqui
docker compose restart             # Tudo
docker compose restart backend     # So backend
```

## PWA - Progressive Web App

A app esta configurada como PWA. Os utilizadores podem:
1. Abrir tudoaqui.ao no Chrome/Safari
2. Clicar em "Adicionar ao ecra inicial"
3. Usar como app nativa (offline basico incluido)

Ficheiros PWA:
- `frontend/public/manifest.json` - Configuracao da PWA
- `frontend/public/sw.js` - Service Worker (cache offline)
- `frontend/public/logo192.png` e `logo512.png` - Icones

## SSL (HTTPS)

O certificado SSL e obtido automaticamente via Let's Encrypt durante o deploy.
Renovacao automatica configurada no container `certbot` (a cada 12h verifica).

## Seguranca

- Rate limiting: 5 req/min para login, 30 req/s para API geral
- Headers de seguranca: HSTS, X-Frame-Options, X-Content-Type-Options
- CORS restrito aos dominios tudoaqui.ao
- Gzip habilitado para compressao
- Cache de assets estaticos (30 dias)
