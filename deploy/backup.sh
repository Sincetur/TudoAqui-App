#!/bin/bash
# =============================================
# TUDOaqui - Backup da Base de Dados
# =============================================
# Uso: ./backup.sh [IP] [USER]
# =============================================

set -e

SERVER_IP=${1:-"SEU_IP_AQUI"}
SERVER_USER=${2:-"root"}
APP_DIR="/opt/tudoaqui"
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "TUDOaqui - Backup da BD..."

ssh $SERVER_USER@$SERVER_IP << REMOTE
cd $APP_DIR
docker compose exec -T db pg_dump -U tudoaqui_user tudoaqui > /tmp/tudoaqui_backup_$DATE.sql
echo "Backup criado no servidor"
REMOTE

scp $SERVER_USER@$SERVER_IP:/tmp/tudoaqui_backup_$DATE.sql $BACKUP_DIR/

echo "Backup guardado em: $BACKUP_DIR/tudoaqui_backup_$DATE.sql"
echo "Tamanho: $(ls -lh $BACKUP_DIR/tudoaqui_backup_$DATE.sql | awk '{print $5}')"
