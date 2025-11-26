#!/bin/bash

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PM2_DIR="$BASE_DIR/pm2"
APP_NAME="chatbot-universitario"

case "$1" in
    start)
        cd $BASE_DIR
        pm2 start $PM2_DIR/ecosystem.config.js --env production
        ;;
    stop)
        pm2 stop $APP_NAME
        ;;
    restart)
        pm2 restart $APP_NAME
        ;;
    reload)
        pm2 reload $APP_NAME
        ;;
    status)
        pm2 status
        ;;
    logs)
        pm2 logs $APP_NAME --lines 30
        ;;
    monitor)
        $PM2_DIR/monitor-pm2.sh
        ;;
    deploy)
        $PM2_DIR/deploy-pm2.sh
        ;;
    backup)
        pm2 save
        cp ~/.pm2/dump.pm2 "$BASE_DIR/backups/dump_$(date +%Y%m%d_%H%M%S).pm2"
        echo "✅ Backup creado"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|reload|status|logs|monitor|deploy|backup}"
        echo ""
        echo "Comandos PM2 para ChatBot Universitario:"
        echo "  start    - Iniciar aplicación"
        echo "  stop     - Detener aplicación"
        echo "  restart  - Reiniciar aplicación"
        echo "  reload   - Recargar sin downtime"
        echo "  status   - Ver estado"
        echo "  logs     - Ver logs"
        echo "  monitor  - Ver métricas"
        echo "  deploy   - Despliegue completo"
        echo "  backup   - Crear backup"
        ;;
esac