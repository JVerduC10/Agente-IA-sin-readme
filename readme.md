# Sistema de Competencia de Modelos de IA

Un sistema completo para evaluar y comparar diferentes modelos de inteligencia artificial, incluyendo integración con APIs de Groq y Bing Search.

## Características Principales

### 🤖 Integración de Modelos
- **Groq API**: Soporte para modelos como DeepSeek R1, Llama, y otros
- **Bing Search API**: Capacidades de búsqueda web integradas
- **Sistema de Fallback**: Cambio automático entre proveedores en caso de fallos

### 📊 Evaluación Automática
- Sistema de evaluación automática con múltiples categorías:
  - Historia
  - Programación
  - Creatividad
  - Razonamiento
- Métricas de rendimiento en tiempo real
- Generación de reportes detallados en formato JSON

### 🔒 Seguridad
- Sistema de encriptación para claves API
- Gestión segura de credenciales
- Protección contra exposición de secretos

### 🛠️ Herramientas de Desarrollo
- Scripts de prueba automatizados
- Validación de configuración
- Monitoreo de rendimiento de modelos

## Estructura del Proyecto

```
├── configuraciones/          # Archivos de configuración
│   ├── .env.admin            # Variables de entorno (claves API)
│   └── README_COMPETENCIA_MODELOS.md
├── herramientas/             # Clientes y gestores de modelos
│   ├── bing_client.py        # Cliente para Bing Search API
│   ├── groq_client.py        # Cliente para Groq API
│   └── model_manager.py      # Gestor principal de modelos
├── scripts/                  # Scripts de utilidad
│   ├── evaluacion_automatica.py  # Sistema de evaluación
│   ├── test_competition.py   # Pruebas del sistema
│   └── encrypt_keys.py       # Encriptación de claves
├── servidor/                 # Componentes del servidor
│   ├── crypto.py            # Utilidades de encriptación
│   └── encryption.py        # Sistema de encriptación
└── resultados/              # Resultados de evaluaciones
```

## Configuración

### 1. Configurar Variables de Entorno

Edita el archivo `configuraciones/.env.admin`:

```env
# Groq API
GROQ_API_KEY=tu_clave_groq_aqui
GROQ_BASE_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=deepseek-r1-distill-llama-70b

# Bing Search API
SEARCH_API_KEY=tu_clave_bing_aqui
SEARCH_ENDPOINT=https://api.bing.microsoft.com/v7.0/search

# Configuración de competencia
DEFAULT_MODEL_PROVIDER=groq
PRIMARY_MODEL=deepseek-r1-distill-llama-70b
```

### 2. Instalar Dependencias

```bash
pip install requests python-dotenv cryptography
```

### 3. Ejecutar Pruebas

```bash
python scripts/test_competition.py
```

## Uso

### Evaluación Automática

Ejecuta el sistema de evaluación automática:

```bash
python scripts/evaluacion_automatica.py
```

Esto generará:
- Prompts automáticos en diferentes categorías
- Evaluación de respuestas de modelos
- Reporte detallado en `resultados/`

### Uso Programático

```python
from herramientas.model_manager import ModelManager

# Inicializar el gestor de modelos
manager = ModelManager()

# Realizar una consulta
respuesta = manager.chat_completion(
    prompt="¿Cuál es la capital de Francia?",
    provider="groq"
)

print(respuesta)
```

## Métricas y Monitoreo

El sistema rastrea automáticamente:
- Tiempo de respuesta por modelo
- Tasa de éxito/error
- Uso de tokens
- Rendimiento comparativo

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para reportar bugs o solicitar nuevas funcionalidades, por favor abre un issue en GitHub.