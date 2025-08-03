import requests
import logging
from typing import List, Dict
from servidor.settings import Settings

logger = logging.getLogger(__name__)

class BingSearchError(Exception):
    """Excepción personalizada para errores de búsqueda de Bing"""
    pass

def buscar_bing(query: str, api_key: str, endpoint: str, count: int = 5) -> List[Dict[str, str]]:
    """
    Realiza una búsqueda web usando la API oficial de Bing Web Search v7.
    
    Args:
        query: Término de búsqueda
        api_key: Clave de API de Bing
        endpoint: Endpoint de la API de Bing
        count: Número de resultados a devolver (máximo 50)
    
    Returns:
        Lista de diccionarios con título, URL y snippet
    
    Raises:
        BingSearchError: Si hay un error en la búsqueda
    """
    if not api_key:
        raise BingSearchError("API key de Bing no configurada")
    
    if not endpoint:
        raise BingSearchError("Endpoint de Bing no configurado")
    
    try:
        headers = {
            "Ocp-Apim-Subscription-Key": api_key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        params = {
            "q": query,
            "count": min(count, 50),  # Bing permite máximo 50 resultados
            "mkt": "es-ES",  # Mercado en español
            "safeSearch": "Moderate"
        }
        
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extraer resultados de la respuesta de Bing
        web_pages = data.get("webPages", {}).get("value", [])
        
        results = []
        for item in web_pages:
            result = {
                "title": item.get("name", "Sin título"),
                "url": item.get("url", ""),
                "snippet": item.get("snippet", "Sin descripción")
            }
            results.append(result)
        
        logger.info(f"Búsqueda Bing completada: {len(results)} resultados para '{query}'")
        return results
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error HTTP en búsqueda Bing: {e.response.status_code}")
        raise BingSearchError(f"Error HTTP {e.response.status_code} en la API de Bing")
    except requests.exceptions.Timeout:
        logger.error(f"Timeout en búsqueda Bing para query: {query}")
        raise BingSearchError("Timeout en la búsqueda de Bing")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión en búsqueda Bing: {str(e)}")
        raise BingSearchError(f"Error de conexión: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado en búsqueda Bing: {str(e)}")
        raise BingSearchError(f"Error inesperado: {str(e)}")

def refinar_query(query: str, query_type: str = "web") -> str:
    """
    Refina la consulta de búsqueda para obtener mejores resultados.
    
    Args:
        query: Consulta original
        query_type: Tipo de consulta (web, news, etc.)
    
    Returns:
        Consulta refinada
    """
    # Remover palabras de pregunta comunes en español
    stop_words = ["qué", "cuál", "cuáles", "cómo", "dónde", "cuándo", "por qué", "quién"]
    
    words = query.lower().split()
    filtered_words = [word for word in words if word not in stop_words]
    
    refined_query = " ".join(filtered_words)
    
    # Si la consulta es muy corta, mantener la original
    if len(refined_query.strip()) < 3:
        return query
    
    return refined_query