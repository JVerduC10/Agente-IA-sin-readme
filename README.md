# Chat API

API de chat simple con FastAPI y Groq.

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

Crea un archivo `.env`:
```
GROQ_API_KEY=tu_clave_aqui
API_KEYS=clave1,clave2
```

## Uso

```bash
uvicorn app.main:app --reload
```

Endpoint: `POST /chat`
```json
{"prompt": "Tu pregunta"}
```