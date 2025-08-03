import logging
from typing import Callable, Any
from scripts.search_engine import buscar_bing, refinar_query, BingSearchError
from scripts.extract import leer_contenido, extraer_contenido_multiple
from servidor.settings import Settings

logger = logging.getLogger(__name__)

class DeepSearchError(Exception):
    """Excepción personalizada para errores de DeepSearch"""
    pass

def run_deepsearch(
    prompt: str, 
    query_type: str, 
    model_fn: Callable[[str, float], str], 
    settings: Settings,
    temperature: float = 0.3
) -> str:
    """
    Ejecuta una búsqueda profunda web usando Bing API + scraping + LLM.
    
    Args:
        prompt: Consulta del usuario
        query_type: Tipo de consulta (debe ser "web")
        model_fn: Función del modelo LLM que toma (prompt, temperature) y devuelve respuesta
        settings: Configuración del sistema
        temperature: Temperatura para el modelo (por defecto 0.3 para factualidad)
    
    Returns:
        Respuesta generada basada en información web
    
    Raises:
        DeepSearchError: Si hay errores en el proceso de búsqueda
    """
    try:
        # Validar configuración
        if not settings.BING_API_KEY:
            raise DeepSearchError("BING_API_KEY no configurada")
        
        if not settings.BING_SEARCH_ENDPOINT:
            raise DeepSearchError("BING_SEARCH_ENDPOINT no configurado")
        
        # Paso 1: Refinar la consulta de búsqueda
        query_rewritten = refinar_query(prompt, query_type)
        logger.info(f"Consulta refinada: '{prompt}' -> '{query_rewritten}'")
        
        # Paso 2: Realizar búsqueda web con Bing
        try:
            resultados = buscar_bing(
                query_rewritten, 
                settings.BING_API_KEY, 
                settings.BING_SEARCH_ENDPOINT,
                count=5
            )
        except BingSearchError as e:
            logger.error(f"Error en búsqueda Bing: {e}")
            return f"Lo siento, no pude realizar la búsqueda web: {e}"
        
        if not resultados:
            return "No encontré información relevante para tu consulta en la web."
        
        # Paso 3: Extraer contenido de las páginas más relevantes
        urls = [r["url"] for r in resultados[:3]]  # Limitar a 3 URLs para eficiencia
        logger.info(f"Extrayendo contenido de {len(urls)} URLs")
        
        fragmentos = []
        for i, url in enumerate(urls):
            contenido = leer_contenido(url, max_len=1500)
            if contenido and len(contenido.strip()) > 50:
                # Agregar contexto del resultado de búsqueda
                fragmento_con_contexto = f"""[FUENTE {i+1}: {resultados[i]['title']}]
URL: {url}
Descripción: {resultados[i]['snippet']}
Contenido: {contenido}
"""
                fragmentos.append(fragmento_con_contexto)
            
            # Limitar a 3 fragmentos exitosos para no sobrecargar el contexto
            if len(fragmentos) >= 3:
                break
        
        if not fragmentos:
            return "No pude extraer contenido útil de las páginas encontradas."
        
        # Paso 4: Construir contexto para el LLM
        contexto = "\n\n".join(fragmentos)
        
        prompt_final = f"""[INFORMACIÓN RECOPILADA DE LA WEB]
{contexto}

[CONSULTA DEL USUARIO]
{prompt}

[INSTRUCCIONES]
Basándote en la información web proporcionada arriba, responde de manera precisa y factual a la consulta del usuario. Si la información no es suficiente para responder completamente, indícalo claramente. Cita las fuentes cuando sea relevante."""
        
        # Paso 5: Generar respuesta usando el modelo LLM
        try:
            respuesta = model_fn(prompt_final, temperature)
            logger.info(f"DeepSearch completado exitosamente para: '{prompt}'")
            return respuesta
        except Exception as e:
            logger.error(f"Error en generación de respuesta LLM: {e}")
            raise DeepSearchError(f"Error al generar respuesta: {e}")
        
    except DeepSearchError:
        raise  # Re-lanzar errores específicos de DeepSearch
    except Exception as e:
        logger.error(f"Error inesperado en DeepSearch: {e}")
        raise DeepSearchError(f"Error inesperado: {e}")

def rewrite_query(prompt: str, query_type: str) -> str:
    """
    Reescribe la consulta del usuario para optimizar la búsqueda web.
    Esta es una versión simple que puede ser mejorada en el futuro.
    
    Args:
        prompt: Consulta original del usuario
        query_type: Tipo de consulta
    
    Returns:
        Consulta optimizada para búsqueda web
    """
    # Por ahora, usar la función de refinamiento existente
    return refinar_query(prompt, query_type)

def validate_deepsearch_config(settings: Settings) -> bool:
    """
    Valida que la configuración necesaria para DeepSearch esté presente.
    
    Args:
        settings: Configuración del sistema
    
    Returns:
        True si la configuración es válida, False en caso contrario
    """
    required_settings = [
        (settings.BING_API_KEY, "BING_API_KEY"),
        (settings.BING_SEARCH_ENDPOINT, "BING_SEARCH_ENDPOINT")
    ]
    
    for value, name in required_settings:
        if not value:
            logger.error(f"Configuración faltante: {name}")
            return False
    
    return True