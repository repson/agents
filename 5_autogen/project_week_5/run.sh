#!/bin/bash

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo "Archivo .env no encontrado"
    echo "Por favor crea un archivo .env basado en .env.example"
    echo "   cp .env.example .env"
    echo "   # Edita .env y añade tu OPENAI_API_KEY"
    exit 1
fi

# Crear directorio output si no existe
mkdir -p ./output

echo "Ejecutando AI Agent Generator..."
echo "Las ideas generadas se guardarán en: ./output/"
echo ""

# Ejecutar contenedor con volumen montado
podman run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  ai-agent-generator

if [ $? -eq 0 ]; then
    echo ""
    echo "Generación completada!"
    echo "Revisa las ideas en: ./output/idea1.md - idea20.md"
else
    echo ""
    echo "Error durante la ejecución"
    exit 1
fi
