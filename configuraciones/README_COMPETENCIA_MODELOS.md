# 🤖 Sistema de Competencia de Modelos AI

## Descripción General

Este sistema implementa una competencia inteligente entre modelos de IA (Groq y OpenAI) con encriptación de claves API para mayor seguridad.

## 🔧 Características Principales

### 1. Competencia de Modelos
- **Groq**: Modelo DeepSeek R1 Distill Llama 70B (rápido y eficiente)
- **OpenAI**: Modelo GPT-4o-mini (alta calidad)
- **Competencia automática**: Ejecuta ambos modelos y selecciona la mejor respuesta
- **Métricas de rendimiento**: Tiempo de respuesta, tasa de éxito, puntuación ponderada

### 2. Seguridad Avanzada
- **Encriptación de claves API**: Las claves se almacenan encriptadas usando Fernet
- **Contraseña maestra**: Protección adicional para el administrador
- **Derivación de claves**: PBKDF2HMAC con salt para mayor seguridad

### 3. Nuevos Endpoints

#### `/chat` (Mejorado)
```json
{
  "message": "Tu pregunta aquí",
  "model_provider": "groq" | "openai" | "compete",
  "query_type": "chat" | "search"
}
```

#### `/compete` (Nuevo)
Ejecuta ambos modelos simultáneamente y devuelve el ganador:
```json
{
  "message": "Tu pregunta aquí",
  "temperature": 0.7
}
```

#### `/performance` (Nuevo)
Obtiene estadísticas de rendimiento de los modelos:
```json
{
  "groq": {
    "requests": 150,
    "success_rate": 0.98,
    "avg_response_time": 1.2,
    "score": 0.85
  },
  "openai": {
    "requests": 120,
    "success_rate": 0.95,
    "avg_response_time": 2.1,
    "score": 0.78
  }
}
```

## 🚀 Configuración

### 1. Variables de Entorno

```bash
# Modelos AI
GROQ_API_KEY=tu_clave_groq
OPENAI_API_KEY=tu_clave_openai
DEFAULT_MODEL_PROVIDER=groq

# Encriptación (Opcional)
MASTER_PASSWORD=tu_contraseña_segura
USE_ENCRYPTED_KEYS=false

# Si usas encriptación
GROQ_API_KEY_ENCRYPTED=clave_encriptada
OPENAI_API_KEY_ENCRYPTED=clave_encriptada
```

### 2. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 3. Encriptación de Claves (Opcional)

Para mayor seguridad, puedes encriptar tus claves API:

```bash
python scripts/encrypt_keys.py
```

Este script te guiará para:
1. Ingresar tu contraseña maestra
2. Proporcionar las claves API
3. Generar las claves encriptadas
4. Configurar el archivo .env

## 📊 Algoritmo de Competencia

El sistema utiliza un algoritmo de puntuación ponderada:

```python
score = (success_rate * 0.7) + (speed_factor * 0.3)
```

Donde:
- **success_rate**: Porcentaje de respuestas exitosas
- **speed_factor**: Factor de velocidad (1 / tiempo_promedio)
- El modelo con mayor puntuación gana la competencia

## 🔒 Seguridad

### Encriptación de Claves
- **Algoritmo**: Fernet (AES 128 en modo CBC)
- **Derivación**: PBKDF2HMAC con SHA256
- **Salt**: Generado aleatoriamente para cada clave
- **Iteraciones**: 100,000 para resistir ataques de fuerza bruta

### Mejores Prácticas
1. Usa contraseñas maestras fuertes (mínimo 16 caracteres)
2. Mantén la contraseña maestra en un gestor de contraseñas
3. Habilita `USE_ENCRYPTED_KEYS=true` en producción
4. Elimina las claves originales después de encriptar

## 🧪 Testing

Prueba los nuevos endpoints:

```bash
# Competencia de modelos
curl -X POST "http://localhost:8000/compete" \
  -H "X-API-Key: tu_api_key" \
  -H "Content-Type: application/json" \
  -d '{"message": "Explica la inteligencia artificial"}'

# Estadísticas de rendimiento
curl -X GET "http://localhost:8000/performance" \
  -H "X-API-Key: tu_api_key"

# Chat con modelo específico
curl -X POST "http://localhost:8000/chat" \
  -H "X-API-Key: tu_api_key" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola", "model_provider": "openai"}'
```

## 📁 Archivos Nuevos

- `servidor/crypto.py`: Sistema de encriptación de claves
- `servidor/openai_client.py`: Cliente para OpenAI
- `servidor/model_manager.py`: Gestor de competencia de modelos
- `scripts/encrypt_keys.py`: Herramienta de encriptación

## 📁 Archivos Modificados

- `servidor/settings.py`: Nuevas configuraciones
- `servidor/routers/chat.py`: Endpoints mejorados
- `requirements.txt`: Nuevas dependencias
- `.env.example`: Configuración actualizada

## 🎯 Beneficios

1. **Redundancia**: Si un modelo falla, el otro toma el control
2. **Optimización**: Selección automática del mejor modelo
3. **Seguridad**: Claves API protegidas con encriptación
4. **Flexibilidad**: Elección manual o automática de modelo
5. **Monitoreo**: Métricas de rendimiento en tiempo real

## 🔧 Mantenimiento

### Monitoreo de Rendimiento
- Revisa las métricas regularmente con `/performance`
- Ajusta la configuración según los resultados
- Considera cambiar el modelo por defecto si uno supera consistentemente al otro

### Rotación de Claves
1. Genera nuevas claves API en los proveedores
2. Usa `encrypt_keys.py` para encriptar las nuevas claves
3. Actualiza el archivo .env
4. Reinicia el servidor

¡El sistema está listo para competir entre modelos de manera segura y eficiente! 🚀