"""Modelos de datos para el sistema de preguntas automáticas."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class QuestionCategory(str, Enum):
    """Categorías de preguntas."""
    GENERAL = "general"
    TECHNICAL = "technical"
    FOLLOWUP = "followup"
    CLARIFICATION = "clarification"
    EXPLORATION = "exploration"
    SUMMARY = "summary"


class QuestionTrigger(str, Enum):
    """Tipos de triggers para activación automática."""
    KEYWORD = "keyword"
    MESSAGE_COUNT = "message_count"
    RAG_CONTEXT = "rag_context"
    WEB_SEARCH = "web_search"
    MANUAL = "manual"
    TIME_BASED = "time_based"


class Question(BaseModel):
    """Modelo para una pregunta del sistema."""
    id: str = Field(..., description="Identificador único de la pregunta")
    text: str = Field(..., description="Texto de la pregunta")
    category: QuestionCategory = Field(default=QuestionCategory.GENERAL, description="Categoría de la pregunta")
    priority: int = Field(default=5, ge=1, le=10, description="Prioridad de la pregunta (1-10)")
    is_active: bool = Field(default=True, description="Si la pregunta está activa")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    metadata: Dict = Field(default_factory=dict, description="Metadatos adicionales")
    triggers: List[str] = Field(default_factory=list, description="Keywords o condiciones que activan la pregunta")
    trigger_type: QuestionTrigger = Field(default=QuestionTrigger.MANUAL, description="Tipo de trigger")
    context_keywords: List[str] = Field(default_factory=list, description="Keywords de contexto")
    usage_count: int = Field(default=0, description="Número de veces que se ha usado")
    last_used: Optional[datetime] = Field(default=None, description="Última vez que se usó")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class QuestionResponse(BaseModel):
    """Modelo para la respuesta a una pregunta."""
    question_id: str = Field(..., description="ID de la pregunta")
    response: str = Field(..., description="Respuesta generada")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confianza en la respuesta")
    sources: List[str] = Field(default_factory=list, description="Fuentes utilizadas")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de la respuesta")
    context_used: str = Field(default="", description="Contexto utilizado para generar la respuesta")
    rag_sources: List[Dict] = Field(default_factory=list, description="Fuentes RAG utilizadas")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class QuestionSuggestion(BaseModel):
    """Modelo para sugerencias de preguntas."""
    questions: List[Question] = Field(default_factory=list, description="Lista de preguntas sugeridas")
    context: str = Field(default="", description="Contexto que generó las sugerencias")
    trigger_reason: str = Field(default="", description="Razón del trigger")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confianza en las sugerencias")


class QuestionCreateRequest(BaseModel):
    """Modelo para crear una nueva pregunta."""
    text: str = Field(..., description="Texto de la pregunta")
    category: QuestionCategory = Field(default=QuestionCategory.GENERAL)
    priority: int = Field(default=5, ge=1, le=10)
    triggers: List[str] = Field(default_factory=list)
    trigger_type: QuestionTrigger = Field(default=QuestionTrigger.MANUAL)
    context_keywords: List[str] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)


class QuestionUpdateRequest(BaseModel):
    """Modelo para actualizar una pregunta."""
    text: Optional[str] = None
    category: Optional[QuestionCategory] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    is_active: Optional[bool] = None
    triggers: Optional[List[str]] = None
    trigger_type: Optional[QuestionTrigger] = None
    context_keywords: Optional[List[str]] = None
    metadata: Optional[Dict] = None