# IA.AGENT - Asistente para Restaurantes

Asistente de IA especializado en el sector restaurante, powered by Groq.

## Características

- API REST con FastAPI
- Integración con Groq (Llama3-8b-8192)
- Respuestas especializadas para restaurantes
- Documentación automática con Swagger

## Ejecutar local

### Prerrequisitos

1. Python 3.8+
2. Clave API de Groq

### Instalación

```bash
pip install -r requirements.txt
```

### Configuración

1. Copia `.env.example` a `.env`
2. Añade tu clave API de Groq:
   ```
   GROQ_API_KEY=tu_clave_api_aqui
   ```

### Ejecutar servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: http://localhost:8000

### Documentación API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Ejemplo de uso

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "¿Cómo puedo mejorar el servicio al cliente en mi restaurante?"}'
```

## Estructura del proyecto

```
├── app/
│   ├── __init__.py
│   └── main.py
├── static/
├── scripts/
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```