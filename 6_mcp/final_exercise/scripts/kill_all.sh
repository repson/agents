#!/bin/bash

# Script para matar todos los procesos relacionados con el trading system
echo "Matando todos los procesos del sistema de trading..."

# Matar procesos Python del proyecto
pkill -f "src.orchestration.trading_floor" 2>/dev/null
pkill -f "src.ui.app" 2>/dev/null
pkill -f "src.mcp" 2>/dev/null

# Matar servidores MCP
pkill -f "mcp-server-filesystem" 2>/dev/null
pkill -f "mcp-server-fetch" 2>/dev/null
pkill -f "mcp-server-brave-search" 2>/dev/null
pkill -f "mcp-memory-libsql" 2>/dev/null

# Matar procesos npm/node relacionados
pkill -f "@modelcontextprotocol" 2>/dev/null

echo "Procesos eliminados"
echo ""
echo "Verificando procesos restantes..."
ps aux | grep -E "(src\.|mcp-)" | grep -v grep
