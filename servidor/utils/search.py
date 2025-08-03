import logging
from typing import List, Dict, Optional
from ..settings import Settings
from ..services.web_search import buscar_web as unified_buscar_web

logger = logging.getLogger(__name__)

class WebSearchError(Exception):
    """Excepci�n personalizada para errores de b�squeda web"""
    pass

# Funci�n de compatibilidad
async def buscar_web(query: str, settings: Settings, top: int = None) -> List[Dict[str, str]]:
    """B�squeda web usando servicio unificado"""
    try:
        return await unified_buscar_web(query, settings, top)
    except Exception as e:
        logger.error(f"Error en b�squeda web: {e}")
        raise WebSearchError(f"Error al buscar informaci�n: {str(e)}")

async def refinar_query(question: str, previous_answer: Optional[str] = None) -> str:
    """Refina la consulta de b�squeda"""
    # Implementaci�n simplificada
    stop_words = ["qu�", "cu�l", "c�mo", "d�nde", "cu�ndo", "por qu�", "qui�n"]
    words = question.lower().split()
    filtered_words = [word for word in words if word not in stop_words]
    refined = " ".join(filtered_words)
    return refined if len(refined.strip()) > 3 else question
