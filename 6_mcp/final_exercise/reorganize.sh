#!/bin/bash

# Script de reorganización del proyecto
# Solo crea carpetas, mueve archivos y actualiza imports

set -e  # Detener si hay errores

echo "Iniciando reorganización del proyecto..."

# Crear estructura de carpetas
echo "Creando estructura de carpetas..."
mkdir -p src/core
mkdir -p src/agents
mkdir -p src/mcp
mkdir -p src/ui
mkdir -p src/orchestration
mkdir -p scripts
mkdir -p data/memory

# Crear archivos __init__.py
echo "Creando archivos __init__.py..."
touch src/__init__.py
touch src/core/__init__.py
touch src/agents/__init__.py
touch src/mcp/__init__.py
touch src/ui/__init__.py
touch src/orchestration/__init__.py

# Mover archivos a sus carpetas correspondientes
echo "Moviendo archivos..."

# Core
mv accounts.py src/core/
mv market.py src/core/
mv database.py src/core/

# Agents
mv traders.py src/agents/
mv templates.py src/agents/
mv tracers.py src/agents/

# MCP
mv accounts_server.py src/mcp/
mv accounts_client.py src/mcp/
mv market_server.py src/mcp/
mv push_server.py src/mcp/
mv mcp_params.py src/mcp/

# UI
mv app.py src/ui/
mv util.py src/ui/

# Orchestration
mv trading_floor.py src/orchestration/

# Scripts
mv reset.py scripts/
mv start.sh scripts/

# Data
mv accounts.db data/ 2>/dev/null || echo "accounts.db no existe aún"
touch data/memory/.gitkeep

# Mover requirements.txt a raíz (ya está ahí)

echo "Archivos movidos correctamente"

# Actualizar imports en los archivos
echo "Actualizando imports..."

# Función para actualizar imports en un archivo
update_imports() {
    local file=$1

    # Core imports
    sed -i 's/^from accounts import/from src.core.accounts import/g' "$file"
    sed -i 's/^from market import/from src.core.market import/g' "$file"
    sed -i 's/^from database import/from src.core.database import/g' "$file"

    # Agents imports
    sed -i 's/^from traders import/from src.agents.traders import/g' "$file"
    sed -i 's/^from templates import/from src.agents.templates import/g' "$file"
    sed -i 's/^from tracers import/from src.agents.tracers import/g' "$file"

    # MCP imports
    sed -i 's/^from accounts_client import/from src.mcp.accounts_client import/g' "$file"
    sed -i 's/^from mcp_params import/from src.mcp.mcp_params import/g' "$file"

    # UI imports
    sed -i 's/^from util import/from src.ui.util import/g' "$file"
    sed -i 's/^from trading_floor import/from src.orchestration.trading_floor import/g' "$file"
}

# Actualizar todos los archivos Python
for file in src/**/*.py; do
    if [ -f "$file" ]; then
        echo "  Actualizando $file..."
        update_imports "$file"
    fi
done

# Actualizar rutas de base de datos
echo "Actualizando rutas de base de datos..."
sed -i 's/DB = "accounts.db"/DB = "data\/accounts.db"/g' src/core/database.py

# Actualizar rutas en mcp_params.py para memoria
sed -i 's/"LIBSQL_URL": f"file:\.\/memory\/{name}\.db"/"LIBSQL_URL": f"file:\.\/data\/memory\/{name}.db"/g' src/mcp/mcp_params.py

# Actualizar scripts para ejecutar desde raíz
echo "Actualizando scripts..."
sed -i 's/uv run trading_floor.py/uv run src\/orchestration\/trading_floor.py/g' scripts/start.sh
sed -i 's/uv run app.py/uv run src\/ui\/app.py/g' scripts/start.sh

# Actualizar comandos en servidores MCP
sed -i 's/"uv", "run", "accounts_server.py"/"uv", "run", "src\/mcp\/accounts_server.py"/g' src/mcp/mcp_params.py
sed -i 's/"uv", "run", "market_server.py"/"uv", "run", "src\/mcp\/market_server.py"/g' src/mcp/mcp_params.py
sed -i 's/"uv", "run", "push_server.py"/"uv", "run", "src\/mcp\/push_server.py"/g' src/mcp/mcp_params.py

echo ""
echo "Reorganización completada!"
echo ""
echo "Próximos pasos:"
echo "   1. Ejecutar: chmod +x scripts/start.sh"
echo "   2. Ejecutar: ./scripts/start.sh"
echo ""
