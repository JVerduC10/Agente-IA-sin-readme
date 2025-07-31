import logging
import re
import sys
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Optional

# Compatibility for Python 3.8
if sys.version_info < (3, 9):
    from typing_extensions import Dict, List
else:
    from typing import Dict, List

import requests
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, field_validator
from pydantic_settings import BaseSettings

from scripts.extract import aggregate, scrape_pct
from scripts.search_engine import search_web

# Configuración simplificada de logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# Configuración optimizada con Pydantic BaseSettings
class Settings(BaseSettings):
    GROQ_API_KEY: str = "test_key"
    MAX_PROMPT_LEN: int = 1000
    ALLOWED_ORIGINS: str = "*"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL: str = "llama3-8b-8192"
    REQUEST_TIMEOUT: int = 30

    @property
    def allowed_origins_list(self) -> List[str]:
        """Convierte ALLOWED_ORIGINS en lista, optimizado como property."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    model_config = ConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    """Singleton para configuración con cache."""
    return Settings()


# Modelos Pydantic optimizados
class Msg(BaseModel):
    prompt: str
    session_id: Optional[str] = None

    @field_validator("prompt")
    @classmethod
    def validate_prompt_length(cls, v: str) -> str:
        settings = get_settings()
        if len(v) > settings.MAX_PROMPT_LEN:
            raise ValueError(
                f"Prompt exceeds maximum length of {settings.MAX_PROMPT_LEN} characters"
            )
        return v


class ChatResponse(BaseModel):
    answer: str


class HealthResponse(BaseModel):
    status: str = "ok"


class ErrorResponse(BaseModel):
    detail: str


# Memoria de conversación simple (en producción usar Redis o base de datos)
conversation_memory: Dict[str, List[Dict[str, str]]] = {}
MEMORY_CLEANUP_INTERVAL = timedelta(hours=2)
last_cleanup = datetime.now()

# Constantes
SYSTEM_PROMPT = (
    "Eres un asistente de búsqueda de información y análisis de datos. "
    "Responde en español de forma concisa y cita siempre la fuente. "
    "Si tienes información de búsquedas web recientes, úsala para dar respuestas más actualizadas."
)

# Palabras clave que indican necesidad de búsqueda web
WEB_SEARCH_KEYWORDS = [
    "actualidad", "reciente", "últimas noticias", "hoy", "2024", "2025", 
    "actual", "ahora", "últimamente", "recientemente", "novedades",
    "qué pasó", "qué está pasando", "situación actual", "estado actual"
]

# Crear aplicación FastAPI
app = FastAPI(
    title="IA Agent - Information Search & Analytics",
    version="2.0.0",
    description="Robust FastAPI information search and analytics assistant with Groq integration",
)

# Configurar CORS al inicializar
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Endpoint de salud optimizado
@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse()


# Funciones auxiliares
def _create_groq_payload(prompt: str, settings: Settings) -> dict:
    """Crea el payload para la API de Groq."""
    return {
        "model": settings.GROQ_MODEL,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }


def _create_headers(api_key: str) -> dict:
    """Crea headers para la API de Groq."""
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def _handle_groq_response(response: requests.Response) -> str:
    """Handle Groq API response and extract answer."""
    # Check for HTTP errors first
    if response.status_code == 401:
        logger.error("Invalid API key")
        raise HTTPException(status_code=401, detail="Invalid API key")
    elif response.status_code == 429:
        logger.error("Rate limit exceeded")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    elif response.status_code >= 400:
        logger.error(f"HTTP error from Groq API: {response.status_code}")
        raise HTTPException(status_code=502, detail="AI service error")
    
    try:
        data = response.json()
        
        if "choices" not in data or not data["choices"]:
            logger.error("Invalid response structure from Groq API")
            raise HTTPException(
                status_code=502, detail="Invalid response from AI service"
            )
        
        choice = data["choices"][0]
        if "message" not in choice or "content" not in choice["message"]:
            logger.error("Missing content in Groq API response")
            raise HTTPException(
                status_code=502, detail="Invalid response structure from AI service"
            )
        
        return choice["message"]["content"].strip()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Groq response: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing AI response")


def _cleanup_old_conversations():
    """Limpia conversaciones antiguas de la memoria."""
    global last_cleanup, conversation_memory
    now = datetime.now()
    if now - last_cleanup > MEMORY_CLEANUP_INTERVAL:
        # Mantener solo las últimas 100 conversaciones para evitar uso excesivo de memoria
        if len(conversation_memory) > 100:
            # Mantener solo las 50 más recientes
            sorted_sessions = sorted(conversation_memory.items(), 
                                   key=lambda x: len(x[1]), reverse=True)
            conversation_memory = dict(sorted_sessions[:50])
        last_cleanup = now


def _get_conversation_context(session_id: str) -> str:
    """Obtiene el contexto de la conversación para una sesión."""
    if not session_id or session_id not in conversation_memory:
        return ""
    
    messages = conversation_memory[session_id]
    if not messages:
        return ""
    
    # Incluir solo los últimos 4 intercambios para no sobrecargar el contexto
    recent_messages = messages[-8:]  # 4 preguntas + 4 respuestas
    context_parts = []
    
    for msg in recent_messages:
        if msg["role"] == "user":
            context_parts.append(f"Usuario: {msg['content']}")
        else:
            context_parts.append(f"Asistente: {msg['content']}")
    
    return "\n".join(context_parts)


def _save_to_conversation(session_id: str, role: str, content: str):
    """Guarda un mensaje en la memoria de conversación."""
    if not session_id:
        return
    
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []
    
    conversation_memory[session_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    
    # Mantener solo los últimos 20 mensajes por sesión
    if len(conversation_memory[session_id]) > 20:
        conversation_memory[session_id] = conversation_memory[session_id][-20:]


def _needs_web_search(prompt: str) -> bool:
    """Determina si una consulta necesita búsqueda web."""
    prompt_lower = prompt.lower()
    return any(keyword in prompt_lower for keyword in WEB_SEARCH_KEYWORDS)


def _perform_web_search(query: str) -> str:
    """Realiza búsqueda web y retorna información relevante."""
    try:
        hits = search_web(query, num_results=5)
        if not hits:
            return ""
        
        # Formatear resultados de búsqueda
        search_results = []
        for hit in hits[:3]:  # Solo los 3 primeros resultados
            search_results.append(f"- {hit['title']}: {hit.get('snippet', 'Sin descripción')} ({hit['url']})")
        
        return "\n".join(search_results)
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        return ""


# Endpoint principal de chat optimizado
@app.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation Error"},
        503: {"model": ErrorResponse, "description": "Service Unavailable"},
    },
)
async def chat(msg: Msg, settings: Settings = Depends(get_settings)) -> ChatResponse:
    """Endpoint principal para chat con memoria y búsqueda web mejorada."""
    logger.info(f"Chat request received: {msg.prompt[:50]}...")
    
    # Limpiar conversaciones antiguas periódicamente
    _cleanup_old_conversations()
    
    # Guardar mensaje del usuario en memoria
    if msg.session_id:
        _save_to_conversation(msg.session_id, "user", msg.prompt)
    
    # Obtener contexto de conversación
    conversation_context = _get_conversation_context(msg.session_id) if msg.session_id else ""
    
    # Detectar si el prompt contiene consultas de porcentajes
    prompt_lower = msg.prompt.lower()
    is_percentage_query = ("%" in msg.prompt or "porcentaje" in prompt_lower) and (
        "mujer" in prompt_lower or "hombre" in prompt_lower
    )

    if is_percentage_query:
        try:
            logger.info("Processing percentage query with web search")
            hits = await search_web(msg.prompt, k=8)
            vals = []
            for h in hits:
                try:
                    vals.extend(await scrape_pct(h["url"]))
                except Exception as e:
                    logger.warning(f"Failed to scrape {h['url']}: {str(e)}")
                    continue

            pct = aggregate(vals)
            if pct is None:
                raise HTTPException(404, "Datos insuficientes")

            fuentes = "\n".join(f"- {h['title']} ({h['url']})" for h in hits[:3])
            answer = f"{pct:.1f}% (mediana)\n{fuentes}"
            
            # Guardar respuesta en memoria
            if msg.session_id:
                _save_to_conversation(msg.session_id, "assistant", answer)
            
            return ChatResponse(answer=answer)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in percentage search: {str(e)}")
            # Fallback to normal LLM processing
    
    # Verificar si necesita búsqueda web para información reciente
    web_search_results = ""
    if _needs_web_search(msg.prompt):
        logger.info("Web search needed for recent information")
        web_search_results = _perform_web_search(msg.prompt)
    
    # Construir prompt con contexto y búsqueda web si aplica
    enhanced_prompt = msg.prompt
    if conversation_context:
        enhanced_prompt = f"Contexto de conversación anterior:\n{conversation_context}\n\nPregunta actual: {msg.prompt}"
    
    if web_search_results:
        enhanced_prompt += f"\n\nInformación web reciente encontrada:\n{web_search_results}\n\nUsa esta información para dar una respuesta actualizada."

    # Flujo LLM habitual
    try:
        response = requests.post(
            settings.GROQ_BASE_URL,
            headers=_create_headers(settings.GROQ_API_KEY),
            json=_create_groq_payload(enhanced_prompt, settings),
            timeout=settings.REQUEST_TIMEOUT,
        )

        answer = _handle_groq_response(response)
        
        # Guardar respuesta en memoria
        if msg.session_id:
            _save_to_conversation(msg.session_id, "assistant", answer)
        
        logger.info("Chat request processed successfully")
        return ChatResponse(answer=answer)

    except requests.exceptions.Timeout:
        logger.error("Request timeout to Groq API")
        raise HTTPException(
            status_code=503, detail="Request timeout. Please try again."
        )

    except HTTPException:
        raise

    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception: {str(e)}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Endpoint raíz optimizado
@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {"message": "IA Agent - Information Search & Analytics API v2.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
