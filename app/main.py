import logging
import sys
from functools import lru_cache

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
    ALLOWED_ORIGINS: str = "http://localhost"
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


# Constantes
SYSTEM_PROMPT = (
    "Eres un asistente experto para el sector restaurante. "
    "Responde en español de forma concisa y cita siempre la fuente."
)

# Crear aplicación FastAPI
app = FastAPI(
    title="IA Agent - Restaurant Assistant",
    version="2.0.0",
    description="Robust FastAPI restaurant assistant with Groq integration",
)

# Configurar CORS al inicializar
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
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
    """Maneja la respuesta de la API de Groq."""
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]

    # Manejo específico de códigos de error
    if response.status_code == 429:
        logger.warning("Rate limit exceeded")
        raise HTTPException(
            status_code=503, detail="Rate limit exceeded. Please try again later."
        )

    if response.status_code == 408:
        logger.warning("Request timeout")
        raise HTTPException(
            status_code=503, detail="Request timeout. Please try again."
        )

    # Para otros códigos de error, mantener el mensaje genérico
    logger.error(f"Groq API error: {response.status_code} - {response.text}")
    raise HTTPException(
        status_code=503, detail=f"External API error: {response.status_code}"
    )


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
    """Chat endpoint with optimized error handling"""
    logger.info(f"Processing chat request with prompt length: {len(msg.prompt)}")

    try:
        response = requests.post(
            settings.GROQ_BASE_URL,
            headers=_create_headers(settings.GROQ_API_KEY),
            json=_create_groq_payload(msg.prompt, settings),
            timeout=settings.REQUEST_TIMEOUT,
        )

        answer = _handle_groq_response(response)
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
    return {"message": "IA Agent - Restaurant Assistant API v2.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
