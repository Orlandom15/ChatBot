#!/bin/bash

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="chatbot-universitario"

monitor() {
    echo "🔍 Monitoreando: $APP_NAME"
    echo "📅 $(date)"
    echo "---"

    STATUS=$(pm2 jlist | jq -r ".[] | select(.name==\"$APP_NAME\")")
    
    if [ -z "$STATUS" ]; then
        echo "❌ Aplicación no encontrada"
        return 1
    fi

    # Métricas
    PM2_STATUS=$(echo $STATUS | jq -r '.pm2_env.status')
    CPU=$(echo $STATUS | jq -r '.monit.cpu')
    MEMORY_MB=$(( $(echo $STATUS | jq -r '.monit.memory') / 1024 / 1024 ))
    RESTARTS=$(echo $STATUS | jq -r '.pm2_env.restart_time')

    echo "✅ Estado: $PM2_STATUS"
    echo "💻 CPU: ${CPU}%"
    echo "🧠 Memoria: ${MEMORY_MB}MB"
    echo "🔄 Reinicios: $RESTARTS"

    # Health check
    if curl -s http://localhost:5000/health > /dev/null; then
        echo "💚 Health Check: OK"
    else
        echo "💥 Health Check: FAILED"
    fi
    echo ""
}

# Ejecutar
monitor