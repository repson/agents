FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar extensiones nativas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos del proyecto
COPY world.py .
COPY creator.py .
COPY agent.py .
COPY messages.py .

# Crear directorio para archivos de salida
RUN mkdir -p /app/output

# Exponer puerto gRPC (usado internamente)
EXPOSE 50051

# Variable de entorno para API key (se pasa en runtime)
ENV OPENAI_API_KEY=""

# Comando de inicio
CMD ["python", "world.py"]
