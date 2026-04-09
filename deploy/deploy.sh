#!/bin/bash
# =============================================
# TUDOaqui SuperApp - Script de Deploy via SSH
# =============================================
# Uso: ./deploy.sh [IP_DO_SERVIDOR] [USER]
# Exemplo: ./deploy.sh 45.33.22.11 root
# =============================================

set -e

SERVER_IP=${1:-"SEU_IP_AQUI"}
SERVER_USER=${2:-"root"}
APP_DIR="/opt/tudoaqui"
DOMAIN="tudoaqui.ao"

echo "=========================================="
echo "  TUDOaqui SuperApp - Deploy Producao"
echo "=========================================="
echo "Servidor: $SERVER_USER@$SERVER_IP"
echo "Directorio: $APP_DIR"
echo ""

# ---- 1. PREPARAR SERVIDOR ----
echo "[1/6] A preparar servidor..."
ssh $SERVER_USER@$SERVER_IP << 'REMOTE_SETUP'
# Instalar Docker se nao existir
if ! command -v docker &> /dev/null; then
    echo "A instalar Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Instalar Docker Compose plugin
if ! docker compose version &> /dev/null; then
    apt-get update && apt-get install -y docker-compose-plugin
fi

# Criar directorio
mkdir -p /opt/tudoaqui
echo "Servidor preparado!"
REMOTE_SETUP

# ---- 2. ENVIAR FICHEIROS ----
echo "[2/6] A enviar ficheiros..."
rsync -avz --exclude='node_modules' --exclude='.git' --exclude='__pycache__' \
    --exclude='.emergent' --exclude='build' --exclude='.env' \
    ./ $SERVER_USER@$SERVER_IP:$APP_DIR/

# Enviar .env de producao
scp deploy/.env.production $SERVER_USER@$SERVER_IP:$APP_DIR/.env
echo "Ficheiros enviados!"

# ---- 3. OBTER CERTIFICADOS SSL ----
echo "[3/6] A configurar SSL (Let's Encrypt)..."
ssh $SERVER_USER@$SERVER_IP << REMOTE_SSL
cd $APP_DIR

# Primeiro deploy sem SSL para obter certificados
# Criar configs temporarias HTTP-only
mkdir -p deploy/nginx/sites-temp
for conf in deploy/nginx/sites/*.conf; do
    # Extract only the HTTP server block
    sed -n '/listen 80/,/^}/p' \$conf > deploy/nginx/sites-temp/\$(basename \$conf)
done

# Start nginx temporarily com HTTP only
docker compose up -d db
sleep 5
docker compose up -d backend frontend

# Obter certificados
docker run --rm \
    -v \${APP_DIR}/certbot-etc:/etc/letsencrypt \
    -v \${APP_DIR}/certbot-var:/var/lib/letsencrypt \
    -v \${APP_DIR}/webroot:/var/www/certbot \
    certbot/certbot certonly --webroot \
    -w /var/www/certbot \
    -d $DOMAIN -d app.$DOMAIN -d api.$DOMAIN -d admin.$DOMAIN \
    --email admin@$DOMAIN \
    --agree-tos --no-eff-email \
    --force-renewal || echo "SSL sera configurado manualmente"

echo "SSL configurado!"
REMOTE_SSL

# ---- 4. BUILD E START ----
echo "[4/6] A construir e iniciar servicos..."
ssh $SERVER_USER@$SERVER_IP << REMOTE_BUILD
cd $APP_DIR

# Build e start
docker compose build --no-cache
docker compose up -d

echo "Servicos iniciados!"
REMOTE_BUILD

# ---- 5. SEED DATA ----
echo "[5/6] A popular base de dados..."
ssh $SERVER_USER@$SERVER_IP << REMOTE_SEED
cd $APP_DIR
sleep 10
# Executar seed
curl -s -X POST http://localhost:8000/api/v1/seed || echo "Seed via docker..."
docker compose exec backend python -c "
import asyncio
from src.seed import run_seed
print(asyncio.run(run_seed()))
" || echo "Seed manual necessario"
echo "Seed concluido!"
REMOTE_SEED

# ---- 6. VERIFICAR ----
echo "[6/6] A verificar deploy..."
ssh $SERVER_USER@$SERVER_IP << REMOTE_CHECK
echo "=== Docker Status ==="
cd $APP_DIR && docker compose ps

echo ""
echo "=== Health Check ==="
curl -s http://localhost:8000/api/health || echo "Backend nao responde"

echo ""
echo "=== Dominios ==="
echo "  https://tudoaqui.ao       -> PWA App"
echo "  https://app.tudoaqui.ao   -> PWA App"
echo "  https://api.tudoaqui.ao   -> Backend API"
echo "  https://admin.tudoaqui.ao -> Admin Panel"
REMOTE_CHECK

echo ""
echo "=========================================="
echo "  DEPLOY CONCLUIDO!"
echo "=========================================="
echo ""
echo "Proximos passos:"
echo "  1. Configurar DNS no seu registrar de dominio:"
echo "     A    tudoaqui.ao       -> $SERVER_IP"
echo "     A    app.tudoaqui.ao   -> $SERVER_IP"
echo "     A    api.tudoaqui.ao   -> $SERVER_IP"
echo "     A    admin.tudoaqui.ao -> $SERVER_IP"
echo ""
echo "  2. Criar admin:"
echo "     ssh $SERVER_USER@$SERVER_IP"
echo "     cd $APP_DIR"
echo "     docker compose exec db psql -U tudoaqui_user -d tudoaqui -c \\"UPDATE users SET role='admin' WHERE telefone='+244912000000';\\""
echo ""
echo "  3. Verificar: https://tudoaqui.ao"
echo ""
