# 🤖 Agente IA con Temperatura Dinámica

Un agente de inteligencia artificial avanzado con capacidades de ajuste dinámico de temperatura basado en el tipo de consulta. Combina un backend robusto en Python con FastAPI y un frontend moderno en React con TypeScript.

## ✨ Características Principales

### 🎯 **Temperatura Dinámica Inteligente**
- **Scientific (0.1)**: Respuestas precisas y factuales para consultas científicas
- **Creative (1.3)**: Máxima creatividad para brainstorming e ideas innovadoras
- **General (0.7)**: Equilibrio perfecto entre precisión y creatividad
- **Custom**: Control manual de temperatura (0.0 - 2.0)

### 🚀 **Tecnologías**
- **Backend**: Python, FastAPI, Groq API, Pydantic
- **Frontend**: React, TypeScript, Tailwind CSS, Vite
- **IA**: Modelos avanzados via Groq (DeepSeek, Meta, etc.)
- **Seguridad**: Validación de API keys, CORS configurado

### 🎨 **Interfaz Moderna**
- Diseño responsive y accesible
- Modo oscuro/claro
- Selección intuitiva de tipos de consulta
- Panel avanzado para control fino de temperatura

## 📁 Estructura del Proyecto

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

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.8+
- Node.js 18+ (opcional, para frontend React)
- API Key de Groq

### Backend (FastAPI)
```bash
# Clonar repositorio
git clone https://github.com/JVerduC10/Agente-IA-sin-readme.git
cd Agente-IA-sin-readme

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu GROQ_API_KEY

# Ejecutar servidor
python -m app.main
```

### Frontend React (Opcional)
```bash
# Instalar dependencias
npm install

# Modo desarrollo
npm run dev

# Build para producción
npm run build
```

## 💡 Uso

### API Endpoints

**POST /api/chat**
```json
{
  "prompt": "Explica la teoría de la relatividad",
  "query_type": "scientific",
  "temperature": 0.1
}
```

**Respuesta:**
```json
{
  "answer": "La teoría de la relatividad...",
  "query_type": "scientific",
  "temperature": 0.1
}
```

### Tipos de Consulta

| Tipo | Temperatura | Uso Ideal |
|------|-------------|----------|
| `scientific` | 0.1 | Preguntas técnicas, datos precisos |
| `creative` | 1.3 | Brainstorming, escritura creativa |
| `general` | 0.7 | Conversación general, consultas mixtas |
| `custom` | 0.0-2.0 | Control manual completo |

## 🎯 Ejemplos Prácticos

### Consulta Científica
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "¿Cuál es la fórmula de la energía cinética?",
    "query_type": "scientific"
  }'
```

### Sesión Creativa
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Ideas para un startup innovador",
    "query_type": "creative"
  }'
```

## 🔧 Configuración

### Variables de Entorno (.env)
```env
GROQ_API_KEY=tu_api_key_aqui
MAX_PROMPT_LEN=4000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
GROQ_MODEL=deepseek-r1-distill-llama-70b
```

### Personalización de Temperaturas
Edita `app/routers/chat.py` para ajustar el mapeo de temperaturas:

```python
temperature_map = {
    "scientific": 0.1,    # Muy preciso
    "creative": 1.3,      # Muy creativo
    "general": 0.7        # Equilibrado
}
```

## 📚 Documentación Adicional

- [🔥 Funcionalidad de Temperatura](./TEMPERATURE_FEATURE.md)
- [⚙️ Instrucciones de Setup](./SETUP_INSTRUCTIONS.md)
- [⚛️ Documentación React](./README-REACT.md)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🙏 Agradecimientos

- [Groq](https://groq.com/) por la API de IA
- [FastAPI](https://fastapi.tiangolo.com/) por el framework web
- [React](https://reactjs.org/) por la interfaz de usuario
- [Tailwind CSS](https://tailwindcss.com/) por el diseño

---

**¿Preguntas?** Abre un [issue](https://github.com/JVerduC10/Agente-IA-sin-readme/issues) o contacta al equipo de desarrollo.
