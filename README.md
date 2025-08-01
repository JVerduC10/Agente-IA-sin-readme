#  Mi Agente IA con Control de Temperatura

¿Te has preguntado alguna vez por qué a veces la IA te da respuestas demasiado "robóticas" para tareas creativas, o demasiado "imaginativas" cuando necesitas datos precisos? Yo también me frustré con eso, así que construí este agente que ajusta automáticamente su "personalidad" según lo que realmente necesitas.

## Lo que hace especial a este proyecto

<<<<<<< HEAD
### **El cerebro detrás del sistema**
=======
###  **El cerebro detrás del sistema**
>>>>>>> d0d0566485b840daabd8fb158e265e43d931fa5a
He implementado un sistema de temperatura dinámica que funciona así:
- **Modo Scientific (0.1)**: Cuando necesitas hechos duros y precisión matemática
- **Modo Creative (1.3)**: Para cuando quieres que la IA "piense fuera de la caja"
- **Modo General (0.7)**: El punto dulce para conversaciones normales
- **Control Manual**: Porque a veces sabes exactamente qué nivel necesitas (0.0 - 2.0)

###  **Stack técnico que elegí**
Después de probar varias opciones, me decidí por:
- **Backend**: FastAPI con Python (por su velocidad y facilidad de desarrollo)
- **IA Engine**: Groq API (acceso a modelos como DeepSeek-R1, Llama, etc.)
- **Frontend**: React + TypeScript (porque me gusta el tipado fuerte)
- **Styling**: Tailwind CSS (desarrollo rápido sin sacrificar personalización)
- **Build Tool**: Vite (compilación ultrarrápida)
- **Validación**: Pydantic (schemas robustos en el backend)

###  **La experiencia de usuario**
No quería otra interfaz aburrida de chat, así que diseñé:
- Interfaz responsive que se ve bien en cualquier dispositivo
- Tema oscuro/claro (porque todos tenemos preferencias)
- Selector intuitivo de tipos de consulta
- Panel "avanzado" para los que quieren control granular

##  Estructura del Proyecto

```
├── app/                    # Backend FastAPI
│   ├── routers/           # Endpoints de la API
│   │   ├── chat.py        # Endpoint principal de chat
│   │   └── health.py      # Health checks
│   ├── main.py            # Aplicación principal
│   ├── settings.py        # Configuración
│   └── security.py        # Autenticación
├── scripts/               # Utilidades
│   └── groq_client.py     # Cliente Groq API
├── src/                   # Frontend React
│   ├── components/        # Componentes React
│   │   ├── forms/         # ChatWidget con temperatura
│   │   ├── layout/        # Header, Footer
│   │   └── sections/      # Hero, Features, Chat
│   ├── context/           # Estado global
│   │   ├── ChatContext.tsx # Gestión de chat
│   │   └── ThemeContext.tsx # Tema
│   ├── types/             # Tipos TypeScript
│   └── utils/             # Utilidades
├── static/                # Frontend estático alternativo
├── tests/                 # Tests automatizados
└── docs/                  # Documentación
    ├── TEMPERATURE_FEATURE.md
    ├── SETUP_INSTRUCTIONS.md
    └── README-REACT.md
```

##  Cómo poner esto en marcha

### Lo que necesitas tener instalado
Antes de empezar, asegúrate de tener:
- Python 3.8 o superior (yo desarrollo con 3.11)
- Node.js 18+ si quieres usar el frontend React (aunque también incluí una versión estática)
- Una API Key de Groq (es gratis para empezar)

### Configurando el backend
Este es el corazón del sistema, donde ocurre toda la magia:

```bash
# Primero, clona mi repositorio
git clone https://github.com/JVerduC10/Agente-IA-sin-readme.git
cd Agente-IA-sin-readme

# Instala las dependencias (uso un requirements.txt limpio)
pip install -r requirements.txt

# Configura tu entorno - IMPORTANTE: necesitas tu propia API key
cp .env.example .env
# Abre .env y pon tu GROQ_API_KEY ahí

# ¡Y ya está! Arranca el servidor
python -m app.main
```

### Si quieres el frontend completo (React)
El backend funciona perfectamente solo, pero si quieres la experiencia completa:

```bash
# Instala las dependencias de Node
npm install

# Para desarrollo (con hot reload)
npm run dev

# Para producción
npm run build
```

##  Cómo usar el sistema

### La API que construí
Todo gira alrededor de un endpoint principal que diseñé para ser simple pero poderoso:

**POST /api/chat** - Aquí es donde ocurre la conversación
```json
{
  "prompt": "Explica la teoría de la relatividad",
  "query_type": "scientific",
  "temperature": 0.1
}
```

Y te devuelve algo así:
```json
{
  "answer": "La teoría de la relatividad...",
  "query_type": "scientific",
  "temperature": 0.1
}
```

### Los "modos" que programé

Cada modo está calibrado basado en mi experiencia usando diferentes modelos:

| Modo | Temperatura | Cuándo lo uso |
|------|-------------|---------------|
| `scientific` | 0.1 | Cuando necesito datos exactos, fórmulas, o hechos verificables |
| `creative` | 1.3 | Para brainstorming, escritura creativa, o generar ideas |
| `general` | 0.7 | Conversaciones normales, explicaciones balanceadas |
| `custom` | 0.0-2.0 | Cuando sé exactamente qué nivel de "creatividad" necesito |

##  Ejemplos reales de uso

### Cuando necesito precisión científica
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "¿Cuál es la fórmula de la energía cinética y sus unidades en el SI?",
    "query_type": "scientific"
  }'
```

### Para sesiones de brainstorming
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Ideas disruptivas para un startup en el sector de la educación",
    "query_type": "creative"
  }'
```

##  Configuración y personalización

### Variables de entorno que uso
En el archivo `.env` tienes control total sobre el comportamiento:

```env
GROQ_API_KEY=tu_api_key_aqui
MAX_PROMPT_LEN=4000                    # Límite de caracteres por consulta
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173  # CORS para desarrollo
GROQ_MODEL=deepseek-r1-distill-llama-70b  # El modelo que más me gusta usar
```

### Ajustando las temperaturas a tu gusto
Si mis valores por defecto no te convencen, puedes cambiarlos fácilmente en `app/routers/chat.py`:

```python
# Estos son los valores que yo uso, pero puedes experimentar
temperature_map = {
    "scientific": 0.1,    # Casi determinista
    "creative": 1.3,      # Bastante creativo sin volverse loco
    "general": 0.7        # El punto dulce que encontré
}
```

## 🔍 Búsqueda RAG con detección automática de dominio

He implementado un sistema inteligente que decide automáticamente si responder con mi corpus de documentos propio o usar búsqueda web, sin necesidad de listas manuales de palabras clave.

### Cómo funciona la magia

El sistema usa embeddings semánticos para determinar si tu consulta está relacionada con los documentos que he ingestado:

1. **Análisis automático**: Cada consulta se convierte en un vector semántico
2. **Búsqueda por similitud**: Compara con mi base de conocimiento usando similitud coseno
3. **Decisión inteligente**: Si encuentra suficientes documentos relevantes (score ≥ 0.35), responde con RAG
4. **Fallback elegante**: Si no, automáticamente usa búsqueda web

### Subir tus documentos

```bash
# Subir un PDF (requiere API key)
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Authorization: Bearer tu_api_key" \
  -F "file=@documento.pdf" \
  -F "source_name=Mi Documento"

# Formatos soportados: PDF, CSV, Markdown
```

### Usar la búsqueda inteligente

```bash
# El sistema decide automáticamente RAG vs web
curl "http://localhost:8000/api/v1/search?q=¿Qué dice mi documento sobre X?"

# Respuesta RAG (si encuentra documentos relevantes):
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

# Respuesta web (si no hay documentos relevantes):
{
  "answer": "Según la búsqueda web...",
  "source_type": "web",
  "references": [{"url": "..."}]
}
```

### Configuración que puedes ajustar

```env
# En tu archivo .env
RAG_SCORE_THRESHOLD=0.35    # Similitud mínima (0-1)
RAG_MIN_HITS=2              # Mínimo de fragmentos relevantes
RAG_CHUNK_SIZE=300          # Tokens por fragmento
```

### Métricas y monitoreo

Tengo métricas Prometheus integradas para que veas cómo se comporta:

```bash
# Ver métricas
curl http://localhost:8000/api/v1/metrics

# Estadísticas del sistema
curl http://localhost:8000/api/v1/rag/stats
```

**Lo genial**: No necesitas configurar listas de palabras clave ni reglas manuales. El sistema aprende automáticamente qué consultas puede responder con tus documentos y cuáles necesitan búsqueda web.

## 📚 Más documentación técnica

Si quieres profundizar en los detalles de implementación:
- [ Cómo funciona la temperatura dinámica](./TEMPERATURE_FEATURE.md)
- [ Guía detallada de instalación](./SETUP_INSTRUCTIONS.md)
- [ Arquitectura del frontend React](./README-REACT.md)

## Si quieres contribuir

Me encantaría que otros desarrolladores mejoren esto:

1. Haz fork del proyecto
2. Crea tu rama (`git checkout -b feature/TuIdea`)
3. Commitea tus cambios (`git commit -m 'Agregué algo genial'`)
4. Push a tu rama (`git push origin feature/TuIdea`)
5. Abre un Pull Request

##  Licencia

MIT License - básicamente puedes hacer lo que quieras con este código.

##  Créditos donde corresponde

Este proyecto no existiría sin:
- [Groq](https://groq.com/) - por democratizar el acceso a modelos de IA de calidad
- [FastAPI](https://fastapi.tiangolo.com/) - el framework web más elegante que he usado
- [React](https://reactjs.org/) - porque hacer UIs complejas nunca fue tan simple
- [Tailwind CSS](https://tailwindcss.com/) - utility-first CSS que realmente funciona

---

**¿Algo no funciona?** Abre un [issue](https://github.com/JVerduC10/Agente-IA-sin-readme/issues) y lo revisamos juntos.
