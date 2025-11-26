#!/bin/bash

set -e

# Configuración
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PM2_DIR="$BASE_DIR/pm2"
LOG_DIR="$BASE_DIR/logs"
BACKUP_DIR="$BASE_DIR/backups"
APP_NAME="chatbot-universitario"

echo "🚀 Iniciando despliegue desde: $BASE_DIR"

# Crear directorios
mkdir -p $LOG_DIR $BACKUP_DIR

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%T')]${NC} $1"; }
error() { echo -e "${RED}[$(date +'%T')] ERROR:${NC} $1"; }

# Verificar PM2
if ! command -v pm2 &> /dev/null; then
    error "PM2 no está instalado. Ejecuta: npm install pm2 -g"
    exit 1
fi

# Instalar dependencias
log "Instalando dependencias de Python..."
pip install -r requirements.txt

# Backup
log "Creando backup..."
if pm2 list | grep -q $APP_NAME; then
    pm2 save
    cp ~/.pm2/dump.pm2 "$BACKUP_DIR/dump_$(date +%Y%m%d_%H%M%S).pm2"
fi

# Detener app si existe
log "Deteniendo aplicación..."
pm2 stop $APP_NAME 2>/dev/null || true
pm2 delete $APP_NAME 2>/dev/null || true

# Iniciar aplicación
log "Iniciando aplicación..."
cd $BASE_DIR
pm2 start $PM2_DIR/ecosystem.config.js --env production

# Esperar y verificar
log "Verificando salud..."
sleep 10

if curl -s http://localhost:5000/health | grep -q "healthy"; then
    log "✅ Aplicación saludable"
else
    error "❌ Health check falló"
    pm2 logs $APP_NAME --lines 20
    exit 1
fi

# Configurar startup
log "Configurando inicio automático..."
pm2 startup 2>/dev/null || true
pm2 save

log "✅ Despliegue completado!"
echo ""
echo "📊 Comandos útiles:"
echo "  pm2 status"
echo "  pm2 logs $APP_NAME"
echo "  pm2 monitor $APP_NAME"