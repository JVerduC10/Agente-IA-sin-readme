# IA.AGENT - Asistente de Restaurante

Un agente de IA robusto y especializado para el sector restaurante, construido con FastAPI y la API de Groq.

## Características

- 🤖 **Asistente especializado**: Enfocado en consultas del sector restaurante
- ⚡ **FastAPI**: Framework moderno y rápido para APIs
- 🧠 **Groq API**: Integración con modelos de IA de alta velocidad
- 📝 **Documentación automática**: Swagger UI y ReDoc incluidos
- 🔧 **Configuración robusta**: Variables de entorno con validación
- 🛡️ **Manejo de errores**: Rate limiting, timeouts y errores de API
- 🌐 **CORS configurado**: Orígenes permitidos configurables
- 📊 **Logging estructurado**: Logs en formato JSON
- 🧪 **Tests completos**: Suite de tests con pytest

## Variables de entorno y ajustes

El proyecto utiliza las siguientes variables de entorno:

- **`GROQ_API_KEY`** (requerido): Tu clave API de Groq
- **`MAX_PROMPT_LEN`** (opcional, default: 1000): Longitud máxima permitida para prompts
- **`ALLOWED_ORIGINS`** (opcional, default: "http://localhost"): Orígenes CORS permitidos (separados por comas)

### Validación de prompts

El sistema valida que los prompts no excedan `MAX_PROMPT_LEN` caracteres. Si un prompt es demasiado largo, la API devuelve un error HTTP 422 con detalles del problema.

## Ejecutar local

### Prerrequisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

### Instalación

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variables de entorno**:
   - Copia `.env.example` a `.env`
   - Edita `.env` y añade tu configuración:
     ```
     GROQ_API_KEY=tu_clave_aqui
     MAX_PROMPT_LEN=1000
     ALLOWED_ORIGINS=http://localhost,http://127.0.0.1:3000
     ```

3. **Ejecutar el servidor**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Acceder a la API**:
   - **Servidor**: http://localhost:8000
   - **Health check**: http://localhost:8000/health
   - **Documentación interactiva**: http://localhost:8000/docs
   - **Documentación alternativa**: http://localhost:8000/redoc

### Endpoints disponibles

#### `GET /health`
Endpoint de verificación de salud que devuelve:
```json
{"status": "ok"}
```

#### `POST /chat`
Endpoint principal para interactuar con el asistente:

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "¿Cuáles son los mejores ingredientes para una pizza margherita?"}'
```

**Respuesta exitosa (200)**:
```json
{
  "answer": "Los mejores ingredientes para una pizza margherita son..."
}
```

**Error de validación (422)** - prompt demasiado largo:
```json
{
  "detail": "Prompt exceeds maximum length of 1000 characters"
}
```

**Error de servicio (503)** - rate limiting o timeout:
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

## Tests

El proyecto incluye una suite completa de tests usando pytest.

### Ejecutar todos los tests
```bash
pytest -q
```

### Ejecutar tests específicos
```bash
# Solo tests de API
pytest tests/test_api.py -q

# Solo tests de health
pytest tests/test_health.py -q

# Solo tests de rate limiting
pytest tests/test_rate_limit.py -q
```

### Tests con API real (marcados como lentos)
```bash
# Ejecutar tests que requieren API key real
pytest -q -m slow
```

**Nota**: Los tests marcados con `@pytest.mark.slow` requieren una clave API válida en la variable de entorno `GROQ_API_KEY`.

## Estructura del proyecto

```
IA.AGENT/
├── app/
│   ├── __init__.py
│   └── main.py          # Aplicación FastAPI principal
├── tests/
│   ├── __init__.py
│   ├── test_api.py      # Tests del endpoint /chat
│   ├── test_health.py   # Tests del endpoint /health
│   └── test_rate_limit.py # Tests de manejo de errores
├── scripts/
├── static/
├── .env.example         # Plantilla de variables de entorno
├── .gitignore
├── README.md
├── requirements.txt     # Dependencias del proyecto
└── pyproject.toml
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Ejecuta los tests (`pytest -q`)
4. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
5. Push a la rama (`git push origin feature/AmazingFeature`)
6. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.