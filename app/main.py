import logging
import logging.config
from typing import List

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, BaseSettings, validator
import requests
import os
from functools import lru_cache

# Configuración de logging estructurado
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "level": "INFO"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Configuración con Pydantic BaseSettings
class Settings(BaseSettings):
    groq_api_key: str
    max_prompt_len: int = 1000
    allowed_origins: List[str] = ["http://localhost"]
    groq_base_url: str = "https://api.groq.com/openai/v1/chat/completions"
    
    @validator('allowed_origins', pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

# Modelos Pydantic
class Msg(BaseModel):
    prompt: str
    
    @validator('prompt')
    def validate_prompt_length(cls, v, values, config, field):
        settings = get_settings()
        if len(v) > settings.max_prompt_len:
            raise ValueError(f'Prompt exceeds maximum length of {settings.max_prompt_len} characters')
        return v

class ChatResponse(BaseModel):
    answer: str

class HealthResponse(BaseModel):
    status: str

class ErrorResponse(BaseModel):
    detail: str

# Crear aplicación FastAPI
app = FastAPI(
    title="IA Agent - Restaurant Assistant",
    version="2.0.0",
    description="Robust FastAPI restaurant assistant with Groq integration"
)

# Configurar CORS
@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    logger.info(f"Application started with CORS origins: {settings.allowed_origins}")

# System prompt para el asistente de restaurantes
SYSTEM_PROMPT = (
    "Eres un asistente experto para el sector restaurante. "
    "Responde en español de forma concisa y cita siempre la fuente."
)

# Endpoint de salud
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="ok")

# Endpoint principal de chat
@app.post("/chat", response_model=ChatResponse, responses={
    422: {"model": ErrorResponse, "description": "Validation Error"},
    503: {"model": ErrorResponse, "description": "Service Unavailable"}
})
async def chat(msg: Msg, settings: Settings = Depends(get_settings)):
    """Chat endpoint with robust error handling"""
    try:
        logger.info(f"Processing chat request with prompt length: {len(msg.prompt)}")
        
        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192",
            "temperature": 0,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": msg.prompt}
            ]
        }
        
        response = requests.post(
            settings.groq_base_url, 
            headers=headers, 
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            logger.info("Chat request processed successfully")
            return ChatResponse(answer=answer)
        
        elif response.status_code == 429:
            logger.warning("Rate limit exceeded")
            raise HTTPException(
                status_code=503,
                detail="Rate limit exceeded. Please try again later."
            )
        
        elif response.status_code == 408 or response.status_code == 504:
            logger.warning("Request timeout")
            raise HTTPException(
                status_code=503,
                detail="Request timeout. Please try again."
            )
        
        else:
            logger.error(f"Groq API error: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=503,
                detail=f"External API error: {response.status_code}"
            )
    
    except requests.exceptions.Timeout:
        logger.error("Request timeout to Groq API")
        raise HTTPException(
            status_code=503,
            detail="Request timeout. Please try again."
        )
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

# Endpoint raíz
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "IA Agent - Restaurant Assistant API v2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)