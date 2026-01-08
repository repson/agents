#!/bin/bash

echo "Construyendo imagen Docker para AI Agent Generator..."
podman build -t ai-agent-generator .

if [ $? -eq 0 ]; then
    echo "Imagen construida exitosamente: ai-agent-generator"
else
    echo "Error al construir la imagen"
    exit 1
fi
