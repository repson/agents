#!/bin/bash

# Script para iniciar el sistema de trading completo
# Ejecuta tanto el motor de trading como la interfaz web
# Uso: ./start.sh [SERVER_HOST | stop]
# Ejemplos:
#   ./start.sh                  # Inicia con IP por defecto
#   ./start.sh 0.0.0.0          # Inicia con IP personalizada
#   ./start.sh stop             # Detiene todos los procesos

# Función para limpiar procesos
cleanup() {
    echo ""
    echo "Deteniendo sistema de trading..."

    # Matar procesos Python del proyecto
    echo "   - Deteniendo procesos Python..."
    pkill -f "src.orchestration.trading_floor" 2>/dev/null
    pkill -f "src.ui.app" 2>/dev/null
    pkill -f "src.mcp" 2>/dev/null

    # Matar servidores MCP
    echo "   - Deteniendo servidores MCP..."
    pkill -f "mcp-server-filesystem" 2>/dev/null
    pkill -f "mcp-server-fetch" 2>/dev/null
    pkill -f "mcp-server-brave-search" 2>/dev/null
    pkill -f "mcp-memory-libsql" 2>/dev/null
    pkill -f "@modelcontextprotocol" 2>/dev/null

    sleep 1
    echo "Sistema detenido"
    exit 0
}

# Si el primer parámetro es "stop" o "cleanup", ejecutar limpieza y salir
if [ "$1" = "stop" ] || [ "$1" = "cleanup" ]; then
    cleanup
fi

echo "Iniciando sistema de trading..."

# Configurar PYTHONPATH para que Python encuentre el módulo src
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Configurar SERVER_HOST si se pasa como parámetro
if [ -n "$1" ]; then
    export SERVER_HOST="$1"
    echo "Usando IP personalizada: $SERVER_HOST"
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
echo "Para detener el sistema, presiona Ctrl+C o ejecuta: ./start.sh stop"
echo ""

# Captura Ctrl+C y llama a cleanup
trap cleanup SIGINT SIGTERM

# Espera a que alguno de los procesos termine
wait
