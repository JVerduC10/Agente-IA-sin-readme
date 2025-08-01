# Sistema de Competencia de Modelos AI

## Descripción General

Este sistema permite la competencia en tiempo real entre diferentes proveedores de modelos AI (Groq, OpenAI, Bing) para determinar cuál proporciona la mejor respuesta para cada consulta.

## Características Principales

### 🏆 Competencia de Modelos
- **Ejecución Paralela**: Los modelos Groq y OpenAI se ejecutan simultáneamente
- **Selección Automática**: El sistema elige automáticamente la mejor respuesta basada en velocidad y éxito
- **Métricas de Rendimiento**: Seguimiento detallado de tiempos de respuesta y tasas de éxito

### 🔐 Seguridad de Claves API
- **Encriptación**: Las claves API pueden ser encriptadas usando AES-256
- **Contraseña Maestra**: Protección adicional con contraseña del administrador
- **Gestión Segura**: Herramientas para encriptar/desencriptar claves

### 🌐 Múltiples Proveedores
- **Groq**: Modelos DeepSeek, Meta, y otros
- **OpenAI**: GPT-4, GPT-4o-mini
- **Bing**: Búsqueda web con síntesis de respuestas

## Configuración

### Variables de Entorno

```bash
# Configuración de modelos
GROQ_API_KEY=tu_clave_groq
OPENAI_API_KEY=tu_clave_openai
SEARCH_API_KEY=tu_clave_bing

# Modelo por defecto
DEFAULT_MODEL_PROVIDER=groq

# Encriptación (opcional)
USE_ENCRYPTED_KEYS=false
MASTER_PASSWORD=tu_contraseña_segura
```

### Encriptación de Claves

1. **Encriptar claves existentes**:
   ```bash
   python scripts/encrypt_keys.py
   ```

2. **Configurar variables encriptadas**:
   ```bash
   USE_ENCRYPTED_KEYS=true
   GROQ_API_KEY_ENCRYPTED=clave_encriptada_aqui
   OPENAI_API_KEY_ENCRYPTED=clave_encriptada_aqui
   SEARCH_API_KEY_ENCRYPTED=clave_encriptada_aqui
   ```

## Endpoints de la API

### 💬 Chat Estándar
```http
POST /chat
{
  "prompt": "Tu pregunta aquí",
  "model_provider": "groq|openai|compete|bing",
  "temperature": 0.7
}
```

### 🏁 Competencia de Modelos
```http
POST /compete
{
  "prompt": "Tu pregunta aquí",
  "temperature": 0.7
}
```

**Respuesta**:
```json
{
  "groq_response": "Respuesta de Groq",
  "openai_response": "Respuesta de OpenAI",
  "winning_response": "La mejor respuesta",
  "best_performer": "groq|openai",
  "performance_stats": {
    "groq_time": 1.2,
    "openai_time": 1.8,
    "total_time": 2.1
  }
}
```

### 📊 Estadísticas de Rendimiento
```http
GET /performance
```

## Uso del Sistema

### 1. Configuración Inicial

```python
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus claves API
```

### 2. Encriptar Claves (Opcional)

```python
# Ejecutar script de encriptación
python scripts/encrypt_keys.py

# Seguir las instrucciones para encriptar tus claves
# Actualizar .env con las claves encriptadas
```

### 3. Iniciar el Servidor

```bash
uvicorn servidor.main:app --reload --port 8000
```

### 4. Probar la Competencia

```bash
# Usando curl
curl -X POST "http://localhost:8000/compete" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu_api_key" \
  -d '{"prompt": "Explica la inteligencia artificial", "temperature": 0.7}'
```

## Arquitectura del Sistema

### Componentes Principales

1. **ModelManager**: Gestiona múltiples proveedores de AI
2. **APIKeyEncryption**: Maneja la encriptación/desencriptación de claves
3. **GroqClient**: Cliente para modelos Groq
4. **OpenAIClient**: Cliente para modelos OpenAI
5. **BingClient**: Cliente para búsqueda web con Bing

### Flujo de Competencia

```
Usuario → Endpoint /compete → ModelManager → [Groq + OpenAI] → Evaluación → Mejor Respuesta
```

### Criterios de Selección

1. **Éxito**: Respuestas sin errores tienen prioridad
2. **Velocidad**: Entre respuestas exitosas, se elige la más rápida
3. **Calidad**: Métricas adicionales pueden ser implementadas

## Monitoreo y Métricas

### Métricas Rastreadas

- **Tiempo de Respuesta**: Latencia de cada modelo
- **Tasa de Éxito**: Porcentaje de respuestas exitosas
- **Errores**: Tipos y frecuencia de errores
- **Uso de Tokens**: Consumo por modelo

### Logs y Debugging

```python
# Configurar logging
import logging
logging.basicConfig(level=logging.INFO)

# Los logs incluyen:
# - Tiempos de respuesta
# - Errores de API
# - Métricas de competencia
```

## Mejores Prácticas

### Seguridad

1. **Nunca** hardcodear claves API en el código
2. Usar encriptación para claves sensibles
3. Rotar claves API regularmente
4. Monitorear uso de API para detectar anomalías

### Rendimiento

1. Implementar cache para respuestas frecuentes
2. Usar timeouts apropiados para evitar bloqueos
3. Monitorear límites de rate de las APIs
4. Implementar circuit breakers para APIs fallidas

### Escalabilidad

1. Usar async/await para operaciones concurrentes
2. Implementar pooling de conexiones
3. Considerar load balancing para múltiples instancias
4. Usar bases de datos para métricas persistentes

## Troubleshooting

### Errores Comunes

1. **"Invalid API Key"**
   - Verificar que las claves estén correctamente configuradas
   - Si usa encriptación, verificar la contraseña maestra

2. **"Model not available"**
   - Verificar que el proveedor esté disponible
   - Revisar límites de rate de la API

3. **"Timeout errors"**
   - Ajustar timeouts en la configuración
   - Verificar conectividad de red

### Debugging

```python
# Habilitar logs detallados
export LOG_LEVEL=DEBUG

# Verificar estado de APIs
curl http://localhost:8000/performance

# Probar claves individualmente
python -c "from servidor.model_manager import ModelManager; mm = ModelManager(); print(mm.get_available_providers())"
```

## Contribución

Para contribuir al sistema:

1. Fork el repositorio
2. Crear una rama para tu feature
3. Implementar tests para nuevas funcionalidades
4. Enviar pull request con descripción detallada

## Licencia

Este proyecto está bajo licencia MIT. Ver archivo LICENSE para más detalles.