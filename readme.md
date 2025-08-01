# Sistema Inteligente de IA con Competencia de Modelos

Un sistema completo y avanzado que combina evaluación de modelos de IA, búsqueda web inteligente, RAG (Retrieval-Augmented Generation) y una interfaz moderna. Diseñado para ser tanto una herramienta de desarrollo como una plataforma de producción.

## 🚀 Características Principales

### 🤖 Integración Avanzada de Modelos
- **Groq API**: Soporte completo para modelos como DeepSeek R1, Llama, y otros
- **Bing Search API**: Capacidades de búsqueda web integradas con scraping inteligente
- **Sistema de Fallback**: Cambio automático entre proveedores en caso de fallos
- **Control de Temperatura**: Modos preconfigurados (científico, creativo, general) y control granular
- **Gestión de Tokens**: Monitoreo y optimización automática del uso de tokens

### 📊 Evaluación Automática de Modelos
- Sistema de evaluación automática con múltiples categorías:
  - Historia
  - Programación
  - Creatividad
  - Razonamiento
- Métricas de rendimiento en tiempo real
- Generación de reportes detallados en formato JSON
- Comparación automática entre diferentes proveedores
- Análisis de rendimiento y costos

### 🌐 Motor de Búsqueda Web Inteligente
- **Búsqueda iterativa**: Refinamiento automático de consultas
- **Extracción concurrente**: Lectura paralela de múltiples páginas web
- **Limpieza inteligente**: Extracción de contenido relevante eliminando ruido
- **Integración RAG**: Uso del contenido web como contexto para respuestas precisas
- **Manejo robusto de errores**: Continuidad ante fallos de páginas individuales

### 🔍 Sistema RAG con Detección Automática
- **Detección inteligente de dominio**: Decide automáticamente entre RAG local y búsqueda web
- **Embeddings semánticos**: Análisis de similitud para determinar relevancia
- **Ingestión de documentos**: Soporte para PDF, CSV, Markdown
- **Búsqueda por similitud**: Algoritmos avanzados de recuperación de información
- **Métricas integradas**: Monitoreo con Prometheus

### 🎨 Interfaz de Usuario Moderna
- **Frontend React**: Interfaz responsive con TypeScript
- **Tema oscuro/claro**: Cambio dinámico de temas
- **Componentes modulares**: Arquitectura basada en componentes reutilizables
- **Experiencia optimizada**: Diseño centrado en el usuario
- **Accesibilidad**: Cumple estándares WCAG AA

### 🔒 Seguridad y Encriptación
- Sistema de encriptación avanzado para claves API
- Gestión segura de credenciales con múltiples capas
- Protección contra exposición de secretos
- Autenticación y autorización integradas
- Validación de entrada y sanitización

### 🛠️ Herramientas de Desarrollo
- Scripts de prueba automatizados
- Validación completa de configuración
- Monitoreo de rendimiento de modelos
- Métricas detalladas y logging
- Documentación técnica completa

## 📁 Estructura Completa del Proyecto

```
├── servidor/                    # Backend FastAPI
│   ├── routers/                # Endpoints de la API
│   │   ├── chat.py            # Endpoint principal de chat
│   │   ├── health.py          # Health checks
│   │   └── search.py          # Endpoints de búsqueda
│   ├── utils/                 # Utilidades del servidor
│   │   ├── scrape.py          # Web scraping
│   │   └── search.py          # Utilidades de búsqueda
│   ├── main.py                # Aplicación principal FastAPI
│   ├── settings.py            # Configuración del sistema
│   ├── security.py            # Autenticación y seguridad
│   ├── crypto.py              # Utilidades de encriptación
│   ├── encryption.py          # Sistema de encriptación
│   ├── rag.py                 # Sistema RAG
│   ├── ingest.py              # Ingestión de documentos
│   ├── metrics.py             # Métricas y monitoreo
│   ├── search_router.py       # Router de búsqueda
│   ├── usage.py               # Gestión de uso
│   └── dependencies.py        # Dependencias del sistema
├── herramientas/               # Clientes y gestores de modelos
│   ├── groq_client.py         # Cliente Groq API
│   ├── bing_client.py         # Cliente para Bing Search API
│   └── model_manager.py       # Gestor principal de modelos
├── interfaz/                   # Frontend React
│   ├── components/            # Componentes React
│   │   ├── ui/               # Componentes base (shadcn/ui)
│   │   ├── common/           # Componentes reutilizables
│   │   ├── forms/            # ChatWidget con temperatura
│   │   ├── layout/           # Header, Footer
│   │   └── sections/         # Hero, Features, Chat
│   ├── context/              # Estado global
│   │   ├── ChatContext.tsx   # Gestión de chat
│   │   └── ThemeContext.tsx  # Gestión de temas
│   ├── hooks/                # Custom React hooks
│   │   └── theme/           # Hooks de tema
│   ├── types/                # Tipos TypeScript
│   │   ├── global.d.ts       # Tipos globales
│   │   ├── modules.d.ts      # Tipos de módulos
│   │   └── react-types.d.ts  # Tipos React
│   ├── utils/                # Utilidades frontend
│   │   ├── cn.ts             # Utilidades de clases CSS
│   │   ├── format.ts         # Formateo de datos
│   │   └── validation.ts     # Validaciones
│   ├── constants/            # Constantes de la aplicación
│   ├── App.tsx               # Componente principal
│   ├── main.tsx              # Punto de entrada React
│   ├── index.css             # Estilos principales
│   ├── index.html            # HTML base
│   ├── vite-env.d.ts         # Tipos de Vite
│   └── README.md             # Documentación del frontend
├── configuraciones/           # Archivos de configuración
│   ├── .env.admin            # Variables de entorno (claves API)
│   ├── .env.example          # Ejemplo de configuración
│   ├── .gitignore            # Archivos ignorados por Git
│   ├── pytest.ini           # Configuración de pytest
│   └── requirements.txt      # Dependencias Python
├── scripts/                   # Scripts de utilidad
│   ├── evaluacion_automatica.py  # Sistema de evaluación
│   ├── test_competition.py   # Pruebas del sistema
│   ├── test_groq_simple.py   # Pruebas específicas Groq
│   ├── test_model_manager.py # Pruebas del gestor de modelos
│   └── encrypt_keys.py       # Encriptación de claves
├── pruebas/                   # Tests automatizados
│   ├── test_api.py           # Pruebas de API
│   ├── test_auth.py          # Pruebas de autenticación
│   ├── test_health.py        # Pruebas de health checks
│   ├── test_rag.py           # Pruebas del sistema RAG
│   └── test_web.py           # Pruebas de búsqueda web
├── archivos_estaticos/        # Frontend estático alternativo
│   ├── index.html            # Página principal estática
│   ├── chat.js               # JavaScript del chat
│   └── styles.css            # Estilos CSS
├── documentacion/             # Documentación técnica
│   ├── README.md             # Documentación principal
│   ├── README-REACT.md       # Documentación React
│   ├── SETUP_INSTRUCTIONS.md # Instrucciones de instalación
│   ├── TEMPERATURE_FEATURE.md # Documentación de temperatura
│   ├── EVALUACION_SISTEMA.md # Documentación de evaluación
│   ├── NUEVAS_FUNCIONALIDADES.txt # Nuevas funcionalidades
│   └── COMANDOS_SISTEMA.txt  # Comandos del sistema
├── base_datos/                # Base de datos
│   └── chroma.sqlite3        # Base de datos vectorial
├── resultados/                # Resultados de evaluaciones
│   └── evaluacion_automatica_20250801_222100.json # Último reporte
└── .github/                   # Configuración GitHub
    └── workflows/            # GitHub Actions
        └── ci.yml            # Pipeline CI/CD
```

## ⚙️ Configuración e Instalación

### Requisitos del Sistema
Antes de empezar, asegúrate de tener:
- **Python 3.8+** (recomendado 3.11)
- **Node.js 18+** (para el frontend React)
- **Git** para clonar el repositorio
- **API Keys**: Groq API (gratis para empezar) y Bing Search API (opcional)

### 1. Clonar e Instalar

```bash
# Clonar el repositorio
git clone https://github.com/JVerduC10/Agente-IA-sin-readme.git
cd Agente-IA-sin-readme

# Instalar dependencias del backend
pip install -r configuraciones/requirements.txt

# Instalar dependencias del frontend (opcional)
npm install
```

### 2. Configurar Variables de Entorno

Copia y edita el archivo de configuración:

```bash
cp configuraciones/.env.example configuraciones/.env.admin
```

Edita `configuraciones/.env.admin` con tus claves:

```env
# === APIs de Modelos ===
# Groq API (Requerido)
GROQ_API_KEY=tu_clave_groq_aqui
GROQ_BASE_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=deepseek-r1-distill-llama-70b

# === Búsqueda Web ===
# Bing Search API (Opcional - para búsqueda web)
SEARCH_API_KEY=tu_clave_bing_aqui
SEARCH_ENDPOINT=https://api.bing.microsoft.com/v7.0/search

# === Configuración del Sistema ===
# Configuración de competencia de modelos
DEFAULT_MODEL_PROVIDER=groq
PRIMARY_MODEL=deepseek-r1-distill-llama-70b

# Configuración del servidor
MAX_PROMPT_LEN=4000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# === Configuración RAG ===
# Configuración de búsqueda RAG
RAG_SCORE_THRESHOLD=0.35    # Similitud mínima (0-1)
RAG_MIN_HITS=2              # Mínimo de fragmentos relevantes
RAG_CHUNK_SIZE=300          # Tokens por fragmento

# === Configuración de Búsqueda Web ===
# Configuración de scraping web
WEB_SCRAPE_TIMEOUT=10           # Timeout para leer páginas
MAX_SEARCH_RESULTS=5            # Resultados por búsqueda
MAX_PAGE_LENGTH=8000            # Caracteres máximos por página
MAX_SEARCH_ITERATIONS=3         # Máximo de iteraciones de búsqueda

# === Configuración Frontend ===
# Variables para el frontend React
VITE_API_URL=http://localhost:8000  # URL del backend
VITE_DEV_MODE=true                  # Habilitar características de desarrollo
VITE_ENABLE_CHAT=true              # Habilitar widget de chat
```

### 3. Inicializar el Sistema

```bash
# Ejecutar pruebas del sistema
python scripts/test_competition.py

# Inicializar la base de datos (si usas RAG)
python -c "from servidor.ingest import init_db; init_db()"
```

### 4. Ejecutar el Sistema

#### Opción A: Solo Backend (API)
```bash
# Iniciar el servidor FastAPI
python -m uvicorn servidor.main:app --host 0.0.0.0 --port 8000 --reload

# El API estará disponible en: http://localhost:8000
# Documentación automática: http://localhost:8000/docs
```

#### Opción B: Sistema Completo (Backend + Frontend)
```bash
# Terminal 1: Iniciar backend
python -m uvicorn servidor.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Iniciar frontend React
npm run dev

# Frontend disponible en: http://localhost:3000
# Backend API en: http://localhost:8000
```

#### Opción C: Frontend Estático (Alternativa simple)
```bash
# Usar el frontend estático incluido
python -m http.server 3000 --directory archivos_estaticos

# Disponible en: http://localhost:3000
```

## 🚀 Guía de Uso Completa

### 🎯 Modos de Consulta Inteligentes

El sistema incluye modos preconfigurados optimizados para diferentes tipos de consultas:

| Modo | Temperatura | Uso Recomendado |
|------|-------------|------------------|
| `scientific` | 0.1 | Datos exactos, fórmulas, hechos verificables |
| `creative` | 1.3 | Brainstorming, escritura creativa, ideas |
| `general` | 0.7 | Conversaciones normales, explicaciones balanceadas |
| `web` | 0.7 | Búsqueda web con información actualizada |
| `custom` | 0.0-2.0 | Control granular de creatividad |

### 📡 API REST - Endpoints Principales

#### Chat Principal
```bash
# Consulta científica precisa
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "¿Cuál es la fórmula de la energía cinética?",
    "query_type": "scientific"
  }'

# Sesión creativa
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Ideas para un startup innovador",
    "query_type": "creative"
  }'

# Búsqueda web con información actualizada
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Últimas noticias sobre inteligencia artificial",
    "query_type": "web"
  }'
```

#### Búsqueda RAG Inteligente
```bash
# El sistema decide automáticamente entre RAG local y búsqueda web
curl "http://localhost:8000/api/v1/search?q=¿Qué información tienes sobre X?"

# Respuesta RAG (documentos locales):
{
  "answer": "Según tus documentos...",
  "source_type": "rag",
  "references": [
    {
      "source": "documento.pdf",
      "similarity": 0.87,
      "snippet": "Fragmento relevante..."
    }
  ]
}

# Respuesta Web (búsqueda externa):
{
  "answer": "Según la búsqueda web...",
  "source_type": "web",
  "references": [{"url": "..."}]
}
```

#### Ingestión de Documentos
```bash
# Subir documentos para RAG (requiere autenticación)
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Authorization: Bearer tu_api_key" \
  -F "file=@documento.pdf" \
  -F "source_name=Mi Documento"

# Formatos soportados: PDF, CSV, Markdown
```

### 🔬 Evaluación Automática de Modelos

#### Evaluación Completa
```bash
# Ejecutar evaluación automática completa
python scripts/evaluacion_automatica.py

# Esto genera:
# - Prompts automáticos en 4 categorías (historia, programación, creatividad, razonamiento)
# - Evaluación de respuestas de todos los modelos configurados
# - Métricas de rendimiento (tiempo, precisión, tokens)
# - Reporte detallado en resultados/evaluacion_YYYYMMDD_HHMMSS.json
```

#### Pruebas del Sistema
```bash
# Verificar configuración completa
python scripts/test_competition.py

# Pruebas específicas
python scripts/test_groq_simple.py      # Solo Groq
python scripts/test_model_manager.py    # Gestor de modelos
```

### 💻 Uso Programático Avanzado

#### Gestor de Modelos
```python
from herramientas.model_manager import ModelManager

# Inicializar el gestor
manager = ModelManager()

# Consulta básica
respuesta = manager.chat_completion(
    prompt="¿Cuál es la capital de Francia?",
    provider="groq"
)

# Consulta con temperatura personalizada
respuesta = manager.chat_completion(
    prompt="Escribe un poema sobre la tecnología",
    provider="groq",
    temperature=1.2
)

# Obtener métricas de rendimiento
metricas = manager.get_performance_metrics()
print(f"Tiempo promedio: {metricas['groq']['avg_response_time']}s")
print(f"Tasa de éxito: {metricas['groq']['success_rate']}%")
```

#### Cliente Groq Directo
```python
from herramientas.groq_client import GroqClient

# Inicializar cliente
client = GroqClient()

# Consulta directa
respuesta = client.chat_completion(
    messages=[
        {"role": "user", "content": "Explica la relatividad"}
    ],
    temperature=0.1
)

print(respuesta)
```

#### Cliente Bing Search
```python
from herramientas.bing_client import BingClient

# Inicializar cliente de búsqueda
client = BingClient()

# Búsqueda web
resultados = client.search("inteligencia artificial 2024")

for resultado in resultados:
    print(f"Título: {resultado['name']}")
    print(f"URL: {resultado['url']}")
    print(f"Snippet: {resultado['snippet']}")
```

### 🎨 Interfaz de Usuario

#### Frontend React
- **Acceso**: http://localhost:3000 (después de `npm run dev`)
- **Características**:
  - Tema oscuro/claro automático
  - Selector de modos de consulta
  - Control granular de temperatura
  - Historial de conversaciones
  - Respuestas en tiempo real

#### Frontend Estático
- **Acceso**: http://localhost:3000 (con `python -m http.server`)
- **Características**:
  - Interfaz simple y rápida
  - Chat básico funcional
  - Sin dependencias de Node.js

### 📊 Monitoreo y Métricas

```bash
# Ver métricas del sistema
curl http://localhost:8000/api/v1/metrics

# Estadísticas RAG
curl http://localhost:8000/api/v1/rag/stats

# Health check
curl http://localhost:8000/api/health
```

## 📊 Métricas y Monitoreo Avanzado

El sistema incluye un completo sistema de métricas y monitoreo en tiempo real:

### 🎯 Métricas de Rendimiento

- **⚡ Tiempo de respuesta**: Medición precisa de latencia por modelo
- **✅ Tasa de éxito**: Porcentaje de respuestas exitosas vs errores
- **🔢 Uso de tokens**: Tracking detallado de consumo de API
- **🏆 Rendimiento por modelo**: Comparativas y rankings automáticos
- **📈 Tendencias temporales**: Análisis de rendimiento histórico
- **🔍 Métricas RAG**: Precisión de búsqueda y relevancia de documentos

### 📈 Dashboard de Métricas

```python
from herramientas.model_manager import ModelManager
from herramientas.performance_tracker import ModelPerformanceTracker

# Obtener métricas completas
manager = ModelManager()
tracker = ModelPerformanceTracker()

# Métricas por proveedor
metricas = manager.get_performance_metrics()
for provider, stats in metricas.items():
    print(f"📊 {provider.upper()}:")
    print(f"   ⚡ Tiempo promedio: {stats['avg_response_time']:.2f}s")
    print(f"   ✅ Tasa de éxito: {stats['success_rate']:.1f}%")
    print(f"   🔢 Tokens promedio: {stats['avg_tokens']:.0f}")
    print(f"   🏆 Puntuación: {stats['performance_score']:.2f}/10")

# Métricas RAG
rag_stats = tracker.get_rag_metrics()
print(f"\n🔍 RAG METRICS:")
print(f"   📚 Documentos indexados: {rag_stats['total_documents']}")
print(f"   🎯 Precisión promedio: {rag_stats['avg_similarity']:.2f}")
print(f"   ⚡ Tiempo de búsqueda: {rag_stats['avg_search_time']:.3f}s")
```

### 🔄 Monitoreo en Tiempo Real

```bash
# API de métricas en vivo
curl http://localhost:8000/api/v1/metrics/live

# Respuesta ejemplo:
{
  "timestamp": "2024-01-15T10:30:00Z",
  "system_status": "healthy",
  "active_models": ["groq"],
  "current_load": {
    "requests_per_minute": 45,
    "avg_response_time": 1.2,
    "error_rate": 0.02
  },
  "rag_status": {
    "documents_indexed": 1250,
    "last_update": "2024-01-15T09:15:00Z",
    "index_health": "optimal"
  }
}
```

## 🤝 Contribuir al Proyecto

¡Agradecemos todas las contribuciones! Aquí te explicamos cómo participar:

### 🚀 Proceso de Contribución

1. **Fork el repositorio**
   ```bash
   git clone https://github.com/JVerduC10/Agente-IA-sin-readme.git
   cd Agente-IA-sin-readme
   ```

2. **Configura el entorno de desarrollo**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Crea una rama para tu feature**
   ```bash
   git checkout -b feature/nombre-descriptivo
   # Ejemplos:
   # git checkout -b feature/nuevo-modelo-ai
   # git checkout -b fix/error-rag-search
   # git checkout -b docs/api-documentation
   ```

4. **Desarrolla y prueba**
   ```bash
   # Ejecuta las pruebas antes de hacer cambios
   python scripts/test_competition.py
   
   # Haz tus cambios...
   
   # Ejecuta las pruebas después de los cambios
   python scripts/test_competition.py
   python scripts/evaluacion_automatica.py
   ```

5. **Commit con mensajes descriptivos**
   ```bash
   git add .
   git commit -m "feat: agregar soporte para modelo Claude"
   # Usa prefijos: feat:, fix:, docs:, style:, refactor:, test:
   ```

6. **Push y Pull Request**
   ```bash
   git push origin feature/nombre-descriptivo
   # Luego abre un Pull Request en GitHub
   ```

### 🎯 Áreas de Contribución

- **🤖 Nuevos Modelos**: Integración de APIs adicionales (OpenAI, Claude, etc.)
- **🔍 Mejoras RAG**: Algoritmos de búsqueda más avanzados
- **🎨 Frontend**: Mejoras en la interfaz de usuario
- **📊 Analytics**: Nuevas métricas y visualizaciones
- **🔒 Seguridad**: Auditorías y mejoras de seguridad
- **📚 Documentación**: Guías, tutoriales y ejemplos
- **🧪 Testing**: Casos de prueba y automatización

### 📋 Estándares de Código

- **Python**: Seguir PEP 8, usar type hints
- **JavaScript/React**: ESLint + Prettier
- **Documentación**: Docstrings detallados
- **Tests**: Cobertura mínima del 80%

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT** - ver el archivo [LICENSE](LICENSE) para detalles completos.

### Resumen de la Licencia
- ✅ Uso comercial permitido
- ✅ Modificación permitida
- ✅ Distribución permitida
- ✅ Uso privado permitido
- ❌ Sin garantía
- ❌ Sin responsabilidad del autor

## 🆘 Soporte y Comunidad

### 📞 Canales de Soporte

- **🐛 Reportar Bugs**: [GitHub Issues](https://github.com/JVerduC10/Agente-IA-sin-readme/issues)
- **💡 Solicitar Features**: [GitHub Discussions](https://github.com/JVerduC10/Agente-IA-sin-readme/discussions)
- **📖 Documentación**: Ver carpeta `documentacion/`
- **💬 Comunidad**: [Discord Server](#) (próximamente)

### 🔧 Solución de Problemas Comunes

#### Error de API Keys
```bash
# Verificar configuración
python scripts/test_groq_simple.py

# Si falla, revisar:
# 1. Archivo .env.admin existe
# 2. API keys son válidas
# 3. Permisos de archivo correctos
```

#### Problemas con RAG
```bash
# Verificar índice de documentos
curl http://localhost:8000/api/v1/rag/stats

# Reindexar si es necesario
python scripts/reindex_documents.py
```

#### Frontend no carga
```bash
# Verificar dependencias
npm install
npm run build

# O usar frontend estático
cd interfaz && python -m http.server 3000
```

### 📚 Recursos Adicionales

- **🎓 Tutoriales**: `documentacion/tutoriales/`
- **🔧 API Reference**: `documentacion/api/`
- **🏗️ Arquitectura**: `documentacion/arquitectura.md`
- **🚀 Deployment**: `documentacion/deployment.md`

### 🌟 Reconocimientos

Gracias a todos los contribuidores que han hecho posible este proyecto:

- **Groq**: Por su excelente API de modelos de lenguaje
- **Microsoft Bing**: Por la API de búsqueda web
- **FastAPI**: Por el framework web robusto
- **React**: Por la interfaz de usuario moderna
- **Comunidad Open Source**: Por las librerías y herramientas

---

<div align="center">

**🚀 ¡Gracias por usar nuestro Sistema Inteligente de IA con Competencia de Modelos! 🚀**

*Construido con ❤️ para la comunidad de desarrolladores de IA*

[![GitHub Stars](https://img.shields.io/github/stars/JVerduC10/Agente-IA-sin-readme?style=social)](https://github.com/JVerduC10/Agente-IA-sin-readme/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/JVerduC10/Agente-IA-sin-readme?style=social)](https://github.com/JVerduC10/Agente-IA-sin-readme/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/JVerduC10/Agente-IA-sin-readme)](https://github.com/JVerduC10/Agente-IA-sin-readme/issues)

</div>