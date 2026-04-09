#!/bin/bash
# =============================================
# TUDOaqui - Atualizar App (sem downtime)
# =============================================
# Uso: ./update.sh [IP] [USER]
# =============================================

set -e

SERVER_IP=${1:-"SEU_IP_AQUI"}
SERVER_USER=${2:-"root"}
APP_DIR="/opt/tudoaqui"

echo "TUDOaqui - A atualizar..."

# Enviar ficheiros atualizados
rsync -avz --exclude='node_modules' --exclude='.git' --exclude='__pycache__' \
    --exclude='.emergent' --exclude='build' --exclude='.env' \
    ./ $SERVER_USER@$SERVER_IP:$APP_DIR/

# Rebuild e restart
ssh $SERVER_USER@$SERVER_IP << REMOTE
cd $APP_DIR

# Rebuild apenas os servicos alterados
docker compose build
docker compose up -d --remove-orphans

# Limpar imagens antigas
docker image prune -f

echo ""
docker compose ps
echo ""
echo "Atualizacao concluida!"
REMOTE
