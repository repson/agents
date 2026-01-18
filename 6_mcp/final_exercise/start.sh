#!/bin/bash

# Script para iniciar el sistema de trading completo
# Ejecuta tanto el motor de trading como la interfaz web
# Uso: ./start.sh [SERVER_HOST]
# Ejemplo: ./start.sh 0.0.0.0

echo "🚀 Iniciando sistema de trading..."

# Configurar PYTHONPATH para que Python encuentre el módulo src
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Configurar SERVER_HOST si se pasa como parámetro
if [ -n "$1" ]; then
    export SERVER_HOST="$1"
    echo "📡 Usando IP personalizada: $SERVER_HOST"
fi

# Inicia el trading floor en segundo plano
echo "Iniciando trading floor..."
uv run python -m src.orchestration.trading_floor &
TRADING_FLOOR_PID=$!

# Espera un momento para que se inicialice
sleep 2

# Inicia la interfaz web
echo "Iniciando interfaz web..."
uv run python -m src.ui.app &
WEB_UI_PID=$!

echo ""
echo "Sistema iniciado correctamente"
echo "   - Trading Floor PID: $TRADING_FLOOR_PID"
echo "   - Web UI PID: $WEB_UI_PID"
echo ""
echo "Para detener el sistema, presiona Ctrl+C"
echo ""

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "Deteniendo sistema..."
    kill $TRADING_FLOOR_PID 2>/dev/null
    kill $WEB_UI_PID 2>/dev/null
    echo "Sistema detenido"
    exit 0
}

# Captura Ctrl+C
trap cleanup SIGINT SIGTERM

# Espera a que alguno de los procesos termine
wait
