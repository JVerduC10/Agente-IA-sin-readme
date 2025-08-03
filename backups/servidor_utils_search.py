import logging
import httpx
from typing import List, Dict, Optional
from ..settings import Settings

logger = logging.getLogger(__name__)


class WebSearchError(Exception):
    """Excepción personalizada para errores de búsqueda web"""
    pass


async def buscar_web(query: str, settings: Settings, top: int = None) -> List[Dict[str, str]]:
    """
    Realiza una búsqueda web usando la API de Bing.
    
    Args:
        query: Término de búsqueda
        settings: Configuración de la aplicación
        top: Número máximo de resultados (por defecto usa MAX_SEARCH_RESULTS)
    
    Returns:
        Lista de diccionarios con título, snippet y URL
    
    Raises:
        WebSearchError: Si hay un error en la búsqueda
    """
    if top is None:
        top = settings.MAX_SEARCH_RESULTS
    
    # Check if Bing API key is configured and valid
    if not settings.SEARCH_API_KEY or settings.SEARCH_API_KEY == "your_bing_api_key_here":
        raise WebSearchError("Búsqueda web no disponible: API key de Bing no configurada")
    
    try:
        return await _buscar_bing(query, settings, top)
    except WebSearchError:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en búsqueda web: {e}")
        raise WebSearchError(f"Error al buscar información: {str(e)}")


async def _buscar_bing(query: str, settings: Settings, top: int) -> List[Dict[str, str]]:
    """
    Búsqueda usando la API de Bing.
    """
    try:
        url = f"{settings.SEARCH_ENDPOINT}?q={query}&count={top}&mkt=es-ES"
        headers = {
            "Ocp-Apim-Subscription-Key": settings.SEARCH_API_KEY,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with httpx.AsyncClient(timeout=settings.WEB_SCRAPE_TIMEOUT) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
        data = response.json()
        
        # Extraer resultados de la respuesta de Bing
        web_pages = data.get("webPages", {}).get("value", [])
        
        results = []
        for page in web_pages[:top]:
            result = {
                "titulo": page.get("name", "Sin título"),
                "snippet": page.get("snippet", "Sin descripción"),
                "url": page.get("url", "")
            }
            results.append(result)
            
        logger.info(f"Búsqueda Bing completada: {len(results)} resultados para '{query}'")
        return results
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Error HTTP en búsqueda Bing: {e.response.status_code} - {e.response.text}")
        raise WebSearchError(f"Error en la API de Bing: {e.response.status_code}")
    except httpx.TimeoutException:
        logger.error(f"Timeout en búsqueda Bing para query: {query}")
        raise WebSearchError("Timeout en la búsqueda Bing")
    except Exception as e:
        logger.error(f"Error inesperado en búsqueda Bing: {str(e)}")
        raise WebSearchError(f"Error en búsqueda Bing: {str(e)}")





async def refinar_query(question: str, previous_answer: Optional[str] = None) -> str:
    """
    Refina la consulta de búsqueda basándose en la pregunta original y respuesta previa.
    
    Args:
        question: Pregunta original del usuario
        previous_answer: Respuesta previa (para iteraciones adicionales)
    
    Returns:
        Query refinada para búsqueda
    """
    # Lógica simple de refinamiento
    # En una implementación más avanzada, esto podría usar el LLM
    
    if previous_answer and "más información" in previous_answer.lower():
        # Si la respuesta anterior indica que necesita más información
        return f"{question} detalles específicos"
    
    # Limpiar la pregunta para búsqueda
    import re
    query = question.strip()
    
    # Remover signos de puntuación y normalizar
    query = re.sub(r'[¿?¡!.,;:]', ' ', query)
    query = re.sub(r'\s+', ' ', query).strip()
    
    # Remover palabras de pregunta comunes en español
    stop_words = ["qué", "cuál", "cómo", "dónde", "cuándo", "por", "qué", "quién", "es", "la", "el", "de"]
    words = query.split()
    filtered_words = [word for word in words if word.lower() not in stop_words and len(word) > 2]
    
    refined_query = " ".join(filtered_words) if filtered_words else query
    
    logger.info(f"Query refinada: '{question}' -> '{refined_query}'")
    return refined_query