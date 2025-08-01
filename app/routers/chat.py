import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, field_validator
from typing import Optional, Literal

from app.dependencies import get_settings
from app.security import check_api_key
from app.settings import Settings
from app.usage import DailyTokenCounter
from scripts.groq_client import GroqClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


class Msg(BaseModel):
    prompt: str
    query_type: Optional[Literal["scientific", "creative", "general"]] = "general"
    temperature: Optional[float] = None

    @field_validator("prompt")
    @classmethod
    def validate_prompt_length(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        if len(v) > 1000:
            raise ValueError("Prompt too long")
        return v
    
    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 0 or v > 2):
            raise ValueError("Temperature must be between 0 and 2")
        return v


class ChatResponse(BaseModel):
    answer: str


class ErrorResponse(BaseModel):
    detail: str


@router.post(
    "/",
    response_model=ChatResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def chat_endpoint(
    request: Request, msg: Msg, settings: Settings = Depends(get_settings)
) -> ChatResponse:
    api_key = request.headers.get("X-API-Key")
    if settings.API_KEYS and not check_api_key(api_key or "", settings):
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        # Determinar temperatura basada en el tipo de consulta
        if msg.temperature is not None:
            temperature = msg.temperature
        else:
            # Temperatura automática basada en el tipo de consulta
            temperature_map = {
                "scientific": 0.1,  # Muy baja para respuestas precisas
                "creative": 1.3,    # Alta para creatividad
                "general": 0.7      # Moderada para uso general
            }
            temperature = temperature_map.get(msg.query_type, 0.7)
        
        token_counter = DailyTokenCounter()
        groq_client = GroqClient(settings, token_counter)
        response = await groq_client.chat_completion(msg.prompt, temperature=temperature)
        return ChatResponse(answer=response)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
