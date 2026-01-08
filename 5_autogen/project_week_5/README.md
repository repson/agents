# AI Agent Generator 🤖

Sistema multi-agente basado en Autogen que genera automáticamente 20 agentes de IA especializados en crear ideas de negocio innovadoras utilizando IA Agentic.

## 📋 Descripción

Este proyecto utiliza un sistema de agentes distribuido basado en gRPC donde:

1. Un agente **Creator** genera dinámicamente 20 agentes únicos
2. Cada agente tiene características, intereses y personalidad propia
3. Los agentes colaboran entre sí para refinar ideas (50% de probabilidad)
4. Se generan 20 ideas de negocio innovadoras guardadas en formato Markdown

## 🎯 Características

- **Generación Dinámica**: Crea agentes con personalidades y expertise únicos
- **Colaboración**: Los agentes pueden compartir ideas entre sí para refinamiento
- **Multi-modelo**: Utiliza GPT-4o-mini de OpenAI
- **Dockerizado**: Fácil de ejecutar sin configurar entorno Python
- **Escalable**: Configuración de comunicación gRPC para sistemas distribuidos

## 📦 Requisitos Previos

- [Docker](https://www.docker.com/get-started) instalado
- Cuenta de OpenAI con [API Key](https://platform.openai.com/api-keys)

## 🚀 Instalación y Uso

### 1. Configurar API Key

Crea un archivo `.env` basado en el template:

```bash
cp .env.example .env
```

Edita `.env` y añade tu API key de OpenAI:

```bash
OPENAI_API_KEY=sk-tu-api-key-aqui
```

### 2. Construir la Imagen Docker

```bash
chmod +x build.sh run.sh
./build.sh
```

### 3. Ejecutar el Generador

```bash
./run.sh
```

El proceso:
- Crea 20 agentes únicos con diferentes personalidades
- Genera 20 ideas de negocio innovadoras
- Guarda las ideas en `./output/idea1.md` a `./output/idea20.md`

## 📁 Estructura del Proyecto

```
project_week_5/
├── world.py          # Punto de entrada - Orquestador principal
├── creator.py        # Agente que genera dinámicamente nuevos agentes
├── agent.py          # Template de agente emprendedor
├── messages.py       # Estructura de mensajes entre agentes
├── requirements.txt  # Dependencias Python
├── Dockerfile        # Configuración del contenedor
├── .dockerignore     # Archivos excluidos del build
├── .env.example      # Template de variables de entorno
├── build.sh          # Script de construcción
├── run.sh            # Script de ejecución
└── output/           # Directorio de salida (se crea automáticamente)
    ├── idea1.md
    ├── idea2.md
    └── ...
```

## 🔧 Configuración Avanzada

### Cambiar el Número de Agentes

Edita `world.py` línea 9:

```python
HOW_MANY_AGENTS = 20  # Cambia este número
```

Luego reconstruye la imagen:

```bash
./build.sh
```

### Modificar el Template de Agente

Edita `agent.py` para cambiar:
- `system_message`: Personalidad y características del agente
- `CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER`: Probabilidad de colaboración (0.0 a 1.0)
- `temperature`: Creatividad del modelo (0.0 a 2.0)

## 🐳 Comandos Docker Manuales

Si prefieres ejecutar Docker manualmente:

```bash
# Construir
docker build -t ai-agent-generator .

# Ejecutar
mkdir -p ./output
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  ai-agent-generator
```

## 📊 Variables de Entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `OPENAI_API_KEY` | API key de OpenAI | Sí |

## 🛠️ Troubleshooting

### Error: "API key not found"

**Solución**: Verifica que tu archivo `.env` existe y contiene una API key válida:

```bash
cat .env
# Debe mostrar: OPENAI_API_KEY=sk-...
```

### Error: "docker: command not found"

**Solución**: Instala Docker Desktop desde [docker.com](https://www.docker.com/get-started)

### Error: "Permission denied" al ejecutar scripts

**Solución**: Dale permisos de ejecución:

```bash
chmod +x build.sh run.sh
```

### Los archivos no se generan en output/

**Solución**: Verifica que el directorio `output/` se creó y tiene permisos de escritura:

```bash
ls -la output/
```

### Errores de API de OpenAI (429, 401)

- **401 Unauthorized**: API key inválida o expirada
- **429 Rate limit**: Has excedido tu límite de requests
  - Espera unos minutos antes de reintentar
  - Verifica tu plan en [platform.openai.com](https://platform.openai.com/usage)

## 🏗️ Arquitectura Técnica

- **Runtime**: Autogen gRPC Worker Runtime
- **Comunicación**: gRPC en puerto 50051 (interno)
- **Modelos**: OpenAI GPT-4o-mini
- **Python**: 3.12
- **Framework**: Autogen Core + AgentChat

### Flujo de Ejecución

```
world.py
  ↓
Inicia gRPC Host (localhost:50051)
  ↓
Registra Creator Agent
  ↓
Para i=1 hasta 20:
  ├─ Creator genera código de agent{i}.py
  ├─ Importa dinámicamente el módulo
  ├─ Registra agent{i} en runtime
  ├─ Agent{i} genera idea de negocio
  ├─ 50% probabilidad: comparte con otro agente
  └─ Guarda en /app/output/idea{i}.md
```

## 📝 Ejemplo de Salida

Cada archivo `idea{N}.md` contendrá una idea de negocio generada por IA, por ejemplo:

```markdown
# HealthTech AI Assistant

Una plataforma que utiliza agentes de IA para personalizar planes
de bienestar basados en datos biométricos en tiempo real...

## Propuesta de Valor
- Monitoreo 24/7 de métricas de salud
- Recomendaciones personalizadas...
```

## 🤝 Contribuir

Este es un proyecto educativo. Siéntete libre de:
- Modificar el template de agentes
- Experimentar con diferentes modelos
- Cambiar la lógica de colaboración entre agentes
- Añadir nuevas funcionalidades

## 📄 Licencia

Este proyecto es de código abierto para propósitos educativos.

## 🔗 Referencias

- [Autogen Documentation](https://microsoft.github.io/autogen/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Docker Documentation](https://docs.docker.com/)

---

**Nota**: Este proyecto consume API de OpenAI que tiene costos asociados. El uso de GPT-4o-mini es económico (~$0.15 por 1M tokens de entrada), pero verifica tu uso en [platform.openai.com/usage](https://platform.openai.com/usage).
