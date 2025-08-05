# 🤖 Jarvis Analyst API - Sistema Inteligente de IA Conversacional

## 📋 Descripción del Proyecto

Jarvis Analyst API es un sistema inteligente de IA conversacional que integra múltiples modelos de lenguaje con capacidades avanzadas de búsqueda web, sistema RAG (Retrieval-Augmented Generation) y evaluación automática de modelos. El proyecto combina un backend robusto en FastAPI con una interfaz moderna en React.

## 🚀 Características Principales

### 🧠 Integración Avanzada de Modelos
- **Groq API**: Acceso a modelos de última generación (Llama, Mixtral, Gemma)
- **Sistema monocliente**: Enfocado exclusivamente en Groq
- **Evaluación Automática**: Sistema de competencia entre modelos
- **Selección Inteligente**: Algoritmo que elige el mejor modelo por tarea

### 🔍 Motor de Búsqueda Inteligente
- **Bing Search API**: Búsquedas web en tiempo real
- **Web Scraping Optimizado**: Extracción inteligente de contenido
- **Filtrado de Resultados**: Eliminación automática de contenido irrelevante
- **Cache Inteligente**: Optimización de consultas repetidas

### 📚 Sistema RAG Avanzado
- **ChromaDB**: Base de datos vectorial para embeddings
- **Detección Automática**: Identifica cuándo usar RAG vs búsqueda web
- **Sentence Transformers**: Embeddings de alta calidad
- **Ingesta Automática**: Procesamiento de documentos PDF y texto

### 🎨 Interfaz de Usuario Moderna
- **React Frontend**: Interfaz responsive y moderna
- **Tailwind CSS**: Diseño elegante y consistente
- **Componentes Reutilizables**: Arquitectura modular
- **Experiencia Optimizada**: UX diseñada para productividad

### 🔒 Seguridad y Encriptación
- **Encriptación de API Keys**: Protección de credenciales sensibles
- **Autenticación Robusta**: Sistema de tokens y validación
- **Headers de Seguridad**: Configuración CORS y CSP
- **Validación de Entrada**: Sanitización automática de datos

## 📁 Estructura del Proyecto

```
📦 jarvis-analyst-api/
├── 📁 servidor/                    # Backend FastAPI
│   ├── 📁 auth/                   # Autenticación y autorización
│   ├── 📁 clients/                # Clientes de APIs externas
│   │   └── 📁 groq/              # Cliente Groq específico
│   ├── 📁 config/                # Configuraciones del sistema
│   ├── 📁 core/                  # Funcionalidades centrales
│   ├── 📁 routers/               # Endpoints de la API
│   ├── 📁 services/              # Lógica de negocio
│   └── 📁 providers/             # Proveedores de servicios
├── 📁 interfaz/                   # Frontend React
│   ├── 📁 components/            # Componentes reutilizables
│   ├── 📁 context/               # Contextos de React
│   ├── 📁 hooks/                 # Hooks personalizados
│   ├── 📁 types/                 # Definiciones TypeScript
│   └── 📁 utils/                 # Utilidades del frontend
├── 📁 tests/                     # Tests del proyecto
├── 📁 docs/                      # Documentación
├── 📁 scripts/                   # Scripts de utilidad
├── 📁 archivos_estaticos/        # Archivos estáticos
└── 📁 resultados/                # Resultados de evaluaciones
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework web moderno y rápido
- **Python 3.8+**: Lenguaje principal
- **Pydantic**: Validación de datos y configuración
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **ChromaDB**: Base de datos vectorial
- **Sentence Transformers**: Modelos de embeddings
- **Cryptography**: Encriptación de datos sensibles

### Frontend
- **React 18+**: Biblioteca de interfaz de usuario
- **Node.js 18+**: Entorno de ejecución
- **Tailwind CSS**: Framework de estilos
- **Vite**: Herramienta de construcción rápida

### APIs y Servicios
- **Groq API**: Modelos de lenguaje avanzados
- **Bing Search API**: Búsqueda web
- **Groq**: Único proveedor de IA integrado

### Herramientas de Desarrollo
- **Pytest**: Framework de testing
- **Black**: Formateo automático de código
- **ESLint**: Linting para JavaScript
- **Docker**: Containerización
- **GitHub Actions**: CI/CD

## 📁 Estructura del Proyecto

```
proyecto/
├── README.md                    # Documentación principal
├── requirements.txt             # Dependencias Python
├── LICENSE                      # Licencia del proyecto
├── configuraciones/             # Configuraciones del sistema
│   ├── .env.example            # Plantilla de variables de entorno
│   └── .env.admin              # Configuración real (no versionado)
├── servidor/                    # Backend FastAPI
│   ├── config/                 # Configuración modular
│   │   ├── base.py            # Configuración principal
│   │   ├── (eliminado azure.py) # Sistema monocliente Groq
│   │   ├── rag.py             # Configuración sistema RAG
│   │   ├── security.py        # Configuración de seguridad
│   │   └── app.py             # Configuración de aplicación
│   ├── core/                   # Componentes centrales
│   │   ├── http_client.py     # Cliente HTTP unificado
│   │   └── error_handler.py   # Manejo de errores
│   ├── routers/               # Endpoints de la API
│   │   ├── chat.py           # Endpoints de chat
│   │   ├── search.py         # Endpoints de búsqueda
│   │   └── models.py         # Endpoints de modelos
│   ├── utils/                 # Utilidades
│   │   └── scrape.py         # Web scraping
│   ├── main.py               # Aplicación principal
│   ├── rag.py                # Sistema RAG
│   ├── crypto.py             # Encriptación
│   └── dependencies.py       # Dependencias FastAPI
├── interfaz/                   # Frontend React
│   ├── src/                   # Código fuente
│   ├── public/               # Archivos estáticos
│   ├── package.json          # Dependencias Node.js
│   └── vite.config.js        # Configuración Vite
├── pruebas/                   # Tests automatizados
├── documentacion/             # Documentación técnica
├── herramientas/             # Scripts de utilidad
└── resultados/               # Resultados de evaluaciones
```

## ⚙️ Requisitos del Sistema

- **Python 3.8+**
- **Node.js 18+**
- **Git**
- **API Keys**:
  - Groq API Key
  - Bing Search API Key (opcional)
  - Groq (requerido)

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd programacion
```

### 2. Configurar Backend
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp configuraciones/.env.example configuraciones/.env.admin
# Editar .env.admin con tus API keys
```

### 3. Configurar Frontend
```bash
cd interfaz
npm install
```

### 4. Variables de Entorno Requeridas

Edita `configuraciones/.env.admin`:

```env
# API Keys
GROQ_API_KEY=tu_groq_api_key
BING_SEARCH_API_KEY=tu_bing_api_key
# Eliminado Azure - Solo Groq requerido

# Configuración del Servidor
MASTER_PASSWORD=tu_password_seguro
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Configuración RAG
RAG_COLLECTION_NAME=jarvis_knowledge
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
```

## 🏃‍♂️ Ejecución

### Desarrollo Completo (Backend + Frontend)
```bash
# Terminal 1: Backend
cd servidor
python main.py

# Terminal 2: Frontend
cd interfaz
npm run dev
```

### Solo Backend
```bash
cd servidor
python main.py
```

### Solo Frontend (Modo Estático)
```bash
cd interfaz
npm run build
npm run preview
```

## 🧪 Testing

```bash
# Ejecutar todas las pruebas
pytest pruebas/

# Pruebas con cobertura
pytest pruebas/ --cov=servidor

# Validar configuración
python herramientas/setup-check.py
```

## 📊 Monitoreo y Métricas

- **Prometheus**: Métricas de rendimiento en `/metrics`
- **Health Check**: Estado del sistema en `/health`
- **Logs Estructurados**: Logging detallado para debugging
- **Evaluación Automática**: Métricas de calidad de respuestas

## 🔧 Configuración de VS Code

El proyecto incluye configuración optimizada para VS Code:

- **Extensiones Recomendadas**: Python, FastAPI, React, Prettier
- **Tareas Configuradas**: Formateo, testing, linting
- **Debugging**: Configuración para backend y frontend
- **Snippets**: Fragmentos de código para desarrollo rápido

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Estándares de Código
- **Python**: Black formatter, isort para imports, flake8 para linting
- **JavaScript**: Prettier formatter, ESLint para linting
- **Tests**: Cobertura mínima del 80%
- **Documentación**: Docstrings en todas las funciones públicas

## 📝 Estado Actual

- **Versión**: 2.0.0 (Refactorizada)
- **Estado**: Producción
- **Última Actualización**: Diciembre 2024
- **Dependencias**: Actualizadas y optimizadas
- **Arquitectura**: Modular y escalable

## 👥 Créditos

- **Desarrollador Principal**: [Tu Nombre]
- **Arquitectura**: Sistema modular con separación de responsabilidades
- **Inspiración**: Mejores prácticas de desarrollo de APIs y sistemas de IA

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Para reportar bugs o solicitar features:
1. Abre un issue en GitHub
2. Incluye información detallada del problema
3. Proporciona pasos para reproducir el error
4. Incluye logs relevantes

## 🔮 Roadmap

- [ ] Integración con más modelos de IA
- [ ] Sistema de plugins extensible
- [ ] Dashboard de administración
- [ ] API GraphQL
- [ ] Soporte para múltiples idiomas
- [ ] Integración con bases de datos externas
- [ ] Sistema de cache distribuido
- [ ] Métricas avanzadas y alertas