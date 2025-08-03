import logging
from typing import List, Dict, Optional
from ..settings import Settings
from ..services.web_search import buscar_web as unified_buscar_web

logger = logging.getLogger(__name__)

class WebSearchError(Exception):
    """Excepción personalizada para errores de búsqueda web"""
    pass

# Función de compatibilidad
async def buscar_web(query: str, settings: Settings, top: int = None) -> List[Dict[str, str]]:
    """Búsqueda web usando servicio unificado"""
    try:
        return await unified_buscar_web(query, settings, top)
    except Exception as e:
        logger.error(f"Error en búsqueda web: {e}")
        raise WebSearchError(f"Error al buscar información: {str(e)}")

async def refinar_query(question: str, previous_answer: Optional[str] = None) -> str:
    """Refina la consulta de búsqueda"""
    # Implementación simplificada
    stop_words = ["qué", "cuál", "cómo", "dónde", "cuándo", "por qué", "quién"]
    words = question.lower().split()
    filtered_words = [word for word in words if word not in stop_words]
    refined = " ".join(filtered_words)
    return refined if len(refined.strip()) > 3 else question
