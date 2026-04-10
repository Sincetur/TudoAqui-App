#!/bin/bash
# ============================================================
# TUDOaqui - Script de Deploy para cPanel via SSH
# Utilizador: tudoaqui
# Dominios:
#   app.tudoaqui.ao   -> Frontend React (PWA)
#   tudoaqui.ao       -> Landing page (mesma build)
#   admin.tudoaqui.ao -> Painel admin (mesma build)
#   api.tudoaqui.ao   -> Backend FastAPI
# ============================================================

set -e

# === CONFIGURACAO ===
CPANEL_USER="tudoaqui"
CPANEL_HOME="/home/$CPANEL_USER"
DOMAIN_APP="app.tudoaqui.ao"
DOMAIN_MAIN="tudoaqui.ao"
DOMAIN_ADMIN="admin.tudoaqui.ao"
DOMAIN_API="api.tudoaqui.ao"

echo "========================================"
echo " TUDOaqui - Deploy Script"
echo "========================================"
echo ""

# === 1. Preparar directorio de deploy ===
echo "[1/6] Preparando ficheiros..."
DEPLOY_DIR="$CPANEL_HOME/deploy_bundle"
mkdir -p "$DEPLOY_DIR"

# === 2. Build Frontend React ===
echo "[2/6] Build frontend React..."
cd /app/frontend

# Definir API URL para producao
echo "REACT_APP_BACKEND_URL=https://api.tudoaqui.ao" > .env.production

yarn build 2>&1 | tail -5

# Copiar build para deploy
cp -r build "$DEPLOY_DIR/frontend_build"

echo "  -> Frontend build: $(du -sh build | cut -f1)"

# === 3. Preparar Backend ===
echo "[3/6] Preparando backend..."
cd /app/backend
mkdir -p "$DEPLOY_DIR/backend"

# Copiar codigo do backend
rsync -a --exclude='__pycache__' --exclude='.pytest_cache' --exclude='tests/' \
  src/ "$DEPLOY_DIR/backend/src/"

# Copiar alembic
rsync -a --exclude='__pycache__' alembic/ "$DEPLOY_DIR/backend/alembic/"
cp alembic.ini "$DEPLOY_DIR/backend/"

# Requirements
pip freeze > "$DEPLOY_DIR/backend/requirements.txt" 2>/dev/null

echo "  -> Backend: $(du -sh $DEPLOY_DIR/backend | cut -f1)"

# === 4. Gerar .env de producao para backend ===
echo "[4/6] Gerando configuracoes..."
cat > "$DEPLOY_DIR/backend/.env.production" << 'ENVEOF'
# === TUDOaqui Backend - Producao ===
# PREENCHER ANTES DO DEPLOY!
DATABASE_URL=postgresql+asyncpg://tudoaqui_user:SUA_SENHA_DB@localhost:5432/tudoaqui
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=GERAR_COM_openssl_rand_hex_64
DEBUG=false
CORS_ORIGINS=["https://tudoaqui.ao","https://app.tudoaqui.ao","https://admin.tudoaqui.ao"]

# SMS (Africa's Talking)
AFRICASTALKING_API_KEY=SUA_CHAVE
AFRICASTALKING_USERNAME=SEU_USERNAME
AFRICASTALKING_SANDBOX=false
SMS_PROVIDER=africastalking
SMS_SENDER=TUDOaqui

# Pagamentos
MULTICAIXA_MERCHANT_ID=SEU_ID
MULTICAIXA_API_KEY=SUA_CHAVE
MULTICAIXA_WEBHOOK_SECRET=SEU_SEGREDO
ENVEOF

# === 5. Script de instalacao no servidor ===
cat > "$DEPLOY_DIR/install_server.sh" << 'INSTALLEOF'
#!/bin/bash
# =================================================================
# TUDOaqui - Instalacao no cPanel (executar via SSH como tudoaqui)
# =================================================================
set -e

CPANEL_HOME="$HOME"
VENV_DIR="$CPANEL_HOME/tudoaqui_venv"
BACKEND_DIR="$CPANEL_HOME/tudoaqui_api"
PUBLIC_APP="$CPANEL_HOME/public_html/app.tudoaqui.ao"
PUBLIC_MAIN="$CPANEL_HOME/public_html/tudoaqui.ao"
PUBLIC_ADMIN="$CPANEL_HOME/public_html/admin.tudoaqui.ao"

echo "=== TUDOaqui Server Install ==="

# 1. Python virtual environment
echo "[1/7] Configurando Python..."
if [ ! -d "$VENV_DIR" ]; then
  python3.11 -m venv "$VENV_DIR" || python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install --upgrade pip

# 2. Instalar backend
echo "[2/7] Instalando backend..."
mkdir -p "$BACKEND_DIR"
cp -r backend/src "$BACKEND_DIR/"
cp -r backend/alembic "$BACKEND_DIR/"
cp backend/alembic.ini "$BACKEND_DIR/"
cp backend/requirements.txt "$BACKEND_DIR/"
cp backend/.env.production "$BACKEND_DIR/.env"

cd "$BACKEND_DIR"
pip install -r requirements.txt

# 3. Migracoes
echo "[3/7] Executando migracoes..."
cd "$BACKEND_DIR"
alembic upgrade head || echo "AVISO: Migracoes podem necessitar revisao manual"

# 4. Deploy frontend para app.tudoaqui.ao
echo "[4/7] Deploy frontend -> app.tudoaqui.ao..."
mkdir -p "$PUBLIC_APP"
rm -rf "$PUBLIC_APP"/*
cp -r frontend_build/* "$PUBLIC_APP/"

# .htaccess para SPA routing
cat > "$PUBLIC_APP/.htaccess" << 'HTEOF'
RewriteEngine On
RewriteBase /
RewriteRule ^index\.html$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]

# Cache static assets
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
  ExpiresByType font/woff2 "access plus 1 year"
</IfModule>

# Gzip
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml
</IfModule>
HTEOF

# 5. Deploy frontend para tudoaqui.ao (landing + app)
echo "[5/7] Deploy frontend -> tudoaqui.ao..."
mkdir -p "$PUBLIC_MAIN"
rm -rf "$PUBLIC_MAIN"/*
cp -r frontend_build/* "$PUBLIC_MAIN/"
cp "$PUBLIC_APP/.htaccess" "$PUBLIC_MAIN/.htaccess"

# 6. Deploy frontend para admin.tudoaqui.ao
echo "[6/7] Deploy frontend -> admin.tudoaqui.ao..."
mkdir -p "$PUBLIC_ADMIN"
rm -rf "$PUBLIC_ADMIN"/*
cp -r frontend_build/* "$PUBLIC_ADMIN/"
cp "$PUBLIC_APP/.htaccess" "$PUBLIC_ADMIN/.htaccess"

# 7. Configurar servico backend (systemd user ou supervisor)
echo "[7/7] Configurando backend service..."
mkdir -p "$CPANEL_HOME/.config/systemd/user"
cat > "$CPANEL_HOME/.config/systemd/user/tudoaqui-api.service" << SVCEOF
[Unit]
Description=TUDOaqui API
After=network.target

[Service]
Type=simple
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$VENV_DIR/bin:/usr/bin
ExecStart=$VENV_DIR/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
SVCEOF

# Tentar activar servico (requer loginctl enable-linger)
systemctl --user daemon-reload 2>/dev/null || true
systemctl --user enable tudoaqui-api 2>/dev/null || true
systemctl --user start tudoaqui-api 2>/dev/null || true

echo ""
echo "============================================"
echo "  Deploy concluido!"
echo "============================================"
echo ""
echo "PROXIMOS PASSOS MANUAIS:"
echo ""
echo "1. Editar $BACKEND_DIR/.env com credenciais reais"
echo ""
echo "2. No cPanel, configurar proxy para api.tudoaqui.ao:"
echo "   Dominio: api.tudoaqui.ao -> http://127.0.0.1:8000"
echo ""
echo "3. Activar SSL para todos os dominios no cPanel"
echo ""
echo "4. Criar base de dados PostgreSQL no cPanel:"
echo "   DB: tudoaqui | User: tudoaqui_user"
echo ""
echo "5. Se systemd nao funcionar, usar cron @reboot:"
echo "   @reboot $VENV_DIR/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000 --workers 2"
echo ""
INSTALLEOF
chmod +x "$DEPLOY_DIR/install_server.sh"

# === 6. Criar pacote final ===
echo "[5/6] Criando pacote deploy..."
cd "$DEPLOY_DIR/.."
tar -czf tudoaqui_deploy.tar.gz -C "$DEPLOY_DIR" .
echo "  -> Pacote: $(du -sh tudoaqui_deploy.tar.gz | cut -f1)"

echo ""
echo "[6/6] Deploy bundle pronto!"
echo ""
echo "============================================"
echo " COMO FAZER DEPLOY:"
echo "============================================"
echo ""
echo " 1. Transferir ficheiro para servidor:"
echo "    scp tudoaqui_deploy.tar.gz tudoaqui@SEU_SERVIDOR:~/"
echo ""
echo " 2. SSH para servidor:"
echo "    ssh tudoaqui@SEU_SERVIDOR"
echo ""
echo " 3. Extrair e instalar:"
echo "    mkdir -p ~/deploy && cd ~/deploy"
echo "    tar -xzf ~/tudoaqui_deploy.tar.gz"
echo "    bash install_server.sh"
echo ""
echo " 4. Configurar proxy no cPanel para api.tudoaqui.ao"
echo ""
echo "============================================"
