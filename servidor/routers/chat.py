#!/usr/bin/env python3
"""
Router de chat - Integración completa con Groq

Este módulo maneja las conversaciones de chat usando GroqClient y ModelManager.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, field_validator

from servidor.config.settings import get_settings, Settings
from servidor.auth.handlers import check_api_key_header
from servidor.services.scraping import WebScrapingError, extraer_contenido_multiple
from servidor.clients.groq.manager import ModelManager

# Importar sistema de preguntas
try:
    from servidor.services.question_manager import question_manager
    from servidor.models.questions import Question
    questions_available = True
except ImportError:
    questions_available = False

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

# Inicializar ModelManager
model_manager = ModelManager()

class ChatMessage(BaseModel):
    """Modelo para mensajes de chat"""
    model_config = ConfigDict(extra="forbid")
    
    role: Literal["user", "assistant", "system"]
    content: str
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El contenido del mensaje no puede estar vacío")
        if len(v) > 10000:
            raise ValueError("El contenido del mensaje no puede exceder 10000 caracteres")
        return v.strip()

class ChatRequest(BaseModel):
    """Modelo para solicitudes de chat"""
    model_config = ConfigDict(extra="forbid")
    
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    stream: Optional[bool] = False
    web_search: Optional[bool] = False
    # Eliminado engine_type - Sistema monocliente Groq
    
    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: List[ChatMessage]) -> List[ChatMessage]:
        if not v:
            raise ValueError("Debe proporcionar al menos un mensaje")
        return v

class ChatResponse(BaseModel):
    """Modelo para respuestas de chat"""
    model_config = ConfigDict(extra="forbid", protected_namespaces=())
    
    response: str
    answer: str  # Alias para compatibilidad con tests
    model_used: str
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    web_search_results: Optional[List[Dict[str, Any]]] = None
    suggested_questions: Optional[List[Dict[str, Any]]] = None
    
    def __init__(self, **data):
        if 'response' in data and 'answer' not in data:
            data['answer'] = data['response']
        super().__init__(**data)

@router.post("/completion", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    settings: Settings = Depends(get_settings),
    api_key: str = Depends(check_api_key_header)
) -> ChatResponse:
    """
    Endpoint principal de chat completion usando Groq
    """
    start_time = time.time()
    
    try:
        # Validar configuraciones
        config_status = settings.validate_settings()
        if not config_status["groq_api_key"]:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Configuración incompleta",
                    "message": "GROQ_API_KEY no configurada",
                    "config_status": config_status
                }
            )
        
        # Convertir mensajes al formato requerido
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Realizar búsqueda web si se solicita
        web_results = None
        if request.web_search:
            try:
                # Obtener el último mensaje del usuario para la búsqueda
                user_query = next(
                    (msg.content for msg in reversed(request.messages) if msg.role == "user"),
                    ""
                )
                if user_query:
                    web_results = await extraer_contenido_multiple([user_query])
                    # Agregar contexto web al sistema
                    web_context = "\n".join([
                        f"Fuente: {result.get('url', 'N/A')}\nContenido: {result.get('content', '')}"
                        for result in web_results[:3]  # Limitar a 3 resultados
                    ])
                    if web_context:
                        messages.insert(0, {
                            "role": "system",
                            "content": f"Contexto web relevante:\n{web_context}\n\nUsa esta información para enriquecer tu respuesta."
                        })
            except WebScrapingError as e:
                logger.warning(f"Error en búsqueda web: {e}")
                # Continuar sin búsqueda web
        
        # Realizar chat completion con Groq
        response = await model_manager.chat_completion(
            messages=messages,
            provider="groq",
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        # Extraer respuesta
        if request.stream:
            # Para streaming, necesitaríamos manejar esto diferente
            # Por ahora, convertimos a respuesta normal
            response_text = ""
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    response_text += chunk.choices[0].delta.content
        else:
            response_text = response["choices"][0]["message"]["content"]
        
        response_time = time.time() - start_time
        
        # Generar sugerencias de preguntas si está habilitado
        suggested_questions = None
        if (questions_available and 
            settings.QUESTIONS_ENABLED and 
            settings.QUESTIONS_AUTO_TRIGGER):
            try:
                # Crear historial de chat para el contexto
                chat_history = [msg.content for msg in request.messages if msg.role == "user"]
                chat_history.append(response_text)  # Incluir la respuesta actual
                
                # Evaluar contexto para sugerencias
                suggestion = question_manager.evaluate_context(
                    chat_history, 
                    len(request.messages)
                )
                
                if suggestion.questions and suggestion.confidence >= settings.QUESTIONS_MIN_CONFIDENCE:
                    suggested_questions = [
                        {
                            "id": q.id,
                            "text": q.text,
                            "category": q.category.value,
                            "priority": q.priority
                        }
                        for q in suggestion.questions[:settings.QUESTIONS_MAX_SUGGESTIONS]
                    ]
                    
                    # Activar las preguntas sugeridas para estadísticas
                    for question in suggestion.questions[:settings.QUESTIONS_MAX_SUGGESTIONS]:
                        question_manager.activate_question(question.id)
                        
            except Exception as e:
                logger.warning(f"Error generando sugerencias de preguntas: {e}")
        
        return ChatResponse(
            response=response_text,
            answer=response_text,
            model_used=response.get("model", "groq-model"),
            tokens_used=response.get("usage", {}).get("total_tokens"),
            response_time=response_time,
            web_search_results=web_results,
            suggested_questions=suggested_questions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en chat completion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/status")
async def get_chat_status(
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """
    Obtiene el estado del sistema de chat
    """
    try:
        # Validar configuraciones
        config_status = validate_settings()
        
        # Obtener información de proveedores
        provider_info = model_manager.get_provider_info()
        
        # Validar conexiones
        provider_status = model_manager.validate_providers()
        
        status = "operational" if config_status["all_valid"] and any(provider_status.values()) else "degraded"
        
        return {
            "status": status,
            "message": "Sistema de chat con integración Groq",
            "configuration": config_status,
            "providers": {
                "available": provider_info["available_providers"],
                "default": provider_info["default_provider"],
                "status": provider_status,
                "models": provider_info["available_models"]
            },
            "features": {
                "chat_completion": True,
                "web_search": True,
                "streaming": True,
                "temperature_control": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del chat: {e}")
        return {
            "status": "error",
            "message": f"Error obteniendo estado: {str(e)}",
            "providers": {},
            "features": {}
        }