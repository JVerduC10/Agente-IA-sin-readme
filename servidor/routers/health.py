from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from servidor.settings import Settings
from servidor.usage import DailyTokenCounter
from herramientas.groq_client import GroqClient
from herramientas.bing_client import BingClient
import asyncio

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: str


class APIHealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(timestamp=datetime.now().isoformat())


@router.get("/health/groq", response_model=APIHealthResponse)
async def groq_health_check() -> APIHealthResponse:
    """Verificar el estado de la API de Groq"""
    try:
        settings = Settings()
        token_counter = DailyTokenCounter()
        
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
            return APIHealthResponse(
                status="error",
                message="Clave API de Groq no configurada",
                timestamp=datetime.now().isoformat()
            )
        
        # Crear cliente y hacer una prueba simple
        client = GroqClient(settings, token_counter)
        
        # Hacer una consulta de prueba muy simple
        try:
            response = await client.chat_completion("Hi", temperature=0.1)
            if response and len(response) > 0:
                return APIHealthResponse(
                    status="working",
                    message="API funcionando correctamente",
                    timestamp=datetime.now().isoformat()
                )
            else:
                return APIHealthResponse(
                    status="error",
                    message="API no respondió correctamente",
                    timestamp=datetime.now().isoformat()
                )
        except Exception as e:
            return APIHealthResponse(
                status="error",
                message=f"Error en API: {str(e)[:100]}",
                timestamp=datetime.now().isoformat()
            )
            
    except Exception as e:
        return APIHealthResponse(
            status="error",
            message=f"Error de configuración: {str(e)[:100]}",
            timestamp=datetime.now().isoformat()
        )


@router.get("/health/bing", response_model=APIHealthResponse)
async def bing_health_check() -> APIHealthResponse:
    """Verificar el estado de la API de Bing Search"""
    try:
        settings = Settings()
        token_counter = DailyTokenCounter()
        
        if not settings.SEARCH_API_KEY or settings.SEARCH_API_KEY in ["your_bing_api_key_here", ""]:
            return APIHealthResponse(
                status="error",
                message="Clave API de Bing no configurada",
                timestamp=datetime.now().isoformat()
            )
        
        # Crear cliente y hacer una prueba simple
        client = BingClient(settings, token_counter)
        
        # Hacer una búsqueda de prueba muy simple
        try:
            response = await client.chat_completion("test", temperature=0.1)
            if response and "Error" not in response:
                return APIHealthResponse(
                    status="working",
                    message="API funcionando correctamente",
                    timestamp=datetime.now().isoformat()
                )
            else:
                return APIHealthResponse(
                    status="error",
                    message="API no configurada o sin clave válida",
                    timestamp=datetime.now().isoformat()
                )
        except Exception as e:
            return APIHealthResponse(
                status="error",
                message=f"Error en API: {str(e)[:100]}",
                timestamp=datetime.now().isoformat()
            )
            
    except Exception as e:
        return APIHealthResponse(
            status="error",
            message=f"Error de configuración: {str(e)[:100]}",
            timestamp=datetime.now().isoformat()
        )


# @router.get("/")
# async def root():
#     return {"message": "Simple Chat API v1.0"}
