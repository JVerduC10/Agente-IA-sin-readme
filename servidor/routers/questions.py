"""Router para el sistema de preguntas automáticas."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ..config.settings import get_settings
from ..models.questions import (
    Question,
    QuestionCategory,
    QuestionCreateRequest,
    QuestionSuggestion,
    QuestionUpdateRequest
)
from ..services.question_manager import question_manager

router = APIRouter(prefix="/questions", tags=["questions"])
settings = get_settings()


@router.get("/", response_model=List[Question])
async def get_questions(
    category: Optional[QuestionCategory] = Query(None, description="Filtrar por categoría"),
    active_only: bool = Query(True, description="Solo preguntas activas")
):
    """Obtiene todas las preguntas con filtros opcionales."""
    if not settings.QUESTIONS_ENABLED:
        raise HTTPException(status_code=503, detail="Sistema de preguntas deshabilitado")
    
    try:
        questions = question_manager.get_all_questions(category=category, active_only=active_only)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo preguntas: {str(e)}")


@router.get("/health")
async def questions_health_check():
    """Verifica el estado del sistema de preguntas."""
    try:
        stats = question_manager.get_statistics()
        return {
            "status": "healthy",
            "enabled": settings.QUESTIONS_ENABLED,
            "auto_trigger": settings.QUESTIONS_AUTO_TRIGGER,
            "total_questions": stats["total_questions"],
            "active_questions": stats["active_questions"],
            "storage_path": settings.QUESTIONS_STORAGE_PATH
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "enabled": settings.QUESTIONS_ENABLED
        }


@router.get("/statistics")
async def get_question_statistics():
    """Obtiene estadísticas del sistema de preguntas."""
    if not settings.QUESTIONS_ENABLED:
        raise HTTPException(status_code=503, detail="Sistema de preguntas deshabilitado")
    
    try:
        stats = question_manager.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@router.get("/categories", response_model=List[str])
async def get_question_categories():
    """Obtiene todas las categorías de preguntas disponibles."""
    if not settings.QUESTIONS_ENABLED:
        raise HTTPException(status_code=503, detail="Sistema de preguntas deshabilitado")
    
    return [category.value for category in QuestionCategory]


@router.get("/suggestions/context", response_model=QuestionSuggestion)
async def get_question_suggestions(
    context: str = Query(..., description="Contexto para generar sugerencias"),
    limit: int = Query(5, ge=1, le=10, description="Número máximo de sugerencias")
):
    """Obtiene sugerencias de preguntas basadas en contexto."""
    if not settings.QUESTIONS_ENABLED:
        raise HTTPException(status_code=503, detail="Sistema de preguntas deshabilitado")
    
    try:
        # Simular historial de chat con el contexto proporcionado
        chat_history = [context]
        suggestion = await question_manager.evaluate_context(chat_history)
        
        # Limitar el número de sugerencias
        if len(suggestion.questions) > limit:
            suggestion.questions = suggestion.questions[:limit]
        
        # Filtrar por confianza mínima
        if suggestion.confidence < settings.QUESTIONS_MIN_CONFIDENCE:
            suggestion.questions = []
            suggestion.trigger_reason = "confidence_too_low"
        
        return suggestion
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando sugerencias: {str(e)}")


@router.get("/suggestions/relevant", response_model=List[Question])
async def get_relevant_questions(
    context: str = Query(..., description="Contexto para buscar preguntas relevantes"),
    limit: int = Query(5, ge=1, le=10, description="Número máximo de preguntas")
):
    """Obtiene preguntas relevantes basadas en contexto."""
    if not settings.QUESTIONS_ENABLED:
        raise HTTPException(status_code=503, detail="Sistema de preguntas deshabilitado")
    
    try:
        questions = await question_manager.get_relevant_questions(context, limit)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo preguntas relevantes: {str(e)}")


@router.get("/{question_id}", response_model=Question)
async def get_question(question_id: str):
    """Obtiene una pregunta específica por ID."""
    if not settings.QUESTIONS_ENABLED:
        raise HTTPException(status_code=503, detail="Sistema de preguntas deshabilitado")
    
    question = question_manager.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    return question


@router.post("/", response_model=Question, status_code=201)
async def create_question(request: QuestionCreateRequest):
    """Crea una nueva pregunta."""
    if not settings.QUESTIONS_ENABLED:
        raise HTTPException(status_code=503, detail="Sistema de preguntas deshabilitado")
    
    try:
        question = question_manager.create_question(request)
        return question
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando pregunta: {str(e)}")


@router.put("/{question_id}", response_model=Question)
async def update_question(question_id: str, request: QuestionUpdateRequest):
    """Actualiza una pregunta existente."""
    if not settings.QUESTIONS_ENABLED:
        raise HTTPException(status_code=503, detail="Sistema de preguntas deshabilitado")
    
    question = question_manager.update_question(question_id, request)
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    return question


@router.delete("/{question_id}")
async def delete_question(question_id: str):
    """Elimina una pregunta."""
    if not settings.QUESTIONS_ENABLED:
        raise HTTPException(status_code=503, detail="Sistema de preguntas deshabilitado")
    
    success = question_manager.delete_question(question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    return JSONResponse(content={"message": "Pregunta eliminada exitosamente"})


@router.put("/{question_id}/activate")
async def activate_question(question_id: str):
    """Activa una pregunta y actualiza estadísticas de uso."""
    if not settings.QUESTIONS_ENABLED:
        raise HTTPException(status_code=503, detail="Sistema de preguntas deshabilitado")
    
    success = question_manager.activate_question(question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    return JSONResponse(content={"message": "Pregunta activada exitosamente"})


@router.post("/evaluate")
async def evaluate_context_for_questions(
    chat_history: List[str],
    message_count: int = 0
):
    """Evalúa un contexto de chat para determinar si sugerir preguntas."""
    if not settings.QUESTIONS_ENABLED:
        raise HTTPException(status_code=503, detail="Sistema de preguntas deshabilitado")
    
    if not settings.QUESTIONS_AUTO_TRIGGER:
        return QuestionSuggestion(trigger_reason="auto_trigger_disabled")
    
    try:
        suggestion = await question_manager.evaluate_context(chat_history, message_count)
        
        # Filtrar por confianza mínima
        if suggestion.confidence < settings.QUESTIONS_MIN_CONFIDENCE:
            suggestion.questions = []
            suggestion.trigger_reason = "confidence_too_low"
        
        return suggestion
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluando contexto: {str(e)}")