#!/usr/bin/env python3
"""
Servicio de búsqueda web - Fusión de search.py + search_router.py

Este módulo proporciona funcionalidades completas de búsqueda web y routing
entre RAG y búsqueda web usando ModelManager y Groq.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from servidor.config.settings import get_settings
from servidor.clients.groq.manager import ModelManager
from servidor.rag import rag_system
from servidor.metrics import metrics, measure_rag_latency

logger = logging.getLogger(__name__)
settings = get_settings()
model_manager = ModelManager()


class WebSearchError(Exception):
    """Excepción personalizada para errores de búsqueda web"""
    pass


class SearchRouter:
    """Router que decide entre RAG y búsqueda web"""
    
    def __init__(self):
        self.rag_system = rag_system
    
    @measure_rag_latency('total')
    def search(self, query: str) -> Dict[str, Any]:
        """Busca usando RAG o web según disponibilidad y relevancia"""
        try:
            start_time = time.time()
            
            # Intentar búsqueda RAG primero
            logger.info(f"Procesando consulta: '{query}'")
            
            rag_result = self.rag_system.rag_router(query)
            
            if rag_result is not None:
                # RAG encontró resultados relevantes
                metrics.record_rag_query('rag')
                metrics.record_rag_used()
                
                # Registrar métricas de similitud si están disponibles
                if 'references' in rag_result:
                    similarities = [ref['similarity'] for ref in rag_result['references']]
                    metrics.record_similarity_scores(similarities)
                    metrics.record_hits_count(len(similarities))
                
                logger.info(f"RAG respondió en {time.time() - start_time:.3f}s con {rag_result.get('hits_used', 0)} hits")
                return rag_result
            else:
                # Fallback a búsqueda web
                metrics.record_rag_query('web')
                metrics.record_rag_fallback()
                
                web_result = self.search_web(query)
                
                logger.info(f"Búsqueda web respondió en {time.time() - start_time:.3f}s")
                return web_result
                
        except Exception as e:
            logger.error(f"Error en search router: {e}")
            return {
                "error": f"Error en búsqueda: {str(e)}",
                "source_type": "error",
                "query": query
            }
    
    def search_web(self, query: str) -> Dict[str, Any]:
        """
        Búsqueda web usando nuevos proveedores
        
        NOTA: Todas las integraciones con Azure han sido eliminadas.
        Esta función está preparada para integración con nuevos proveedores.
        """
        try:
            logger.info(f"Búsqueda web solicitada: '{query}'")
            
            return {
                "error": "Servicio de búsqueda web no disponible. Todas las integraciones con Azure han sido eliminadas. Preparado para integración con nuevos proveedores como Groq.",
                "source_type": "service_unavailable",
                "query": query,
                "next_steps": [
                    "Configurar GROQ_API_KEY en variables de entorno",
                    "Implementar GroqClient en servidor/clients/groq/",
                    "Actualizar lógica de búsqueda web"
                ]
            }
                
        except Exception as e:
            logger.error(f"Error inesperado en búsqueda web: {e}")
            return {
                "error": f"Error en búsqueda web: {str(e)}",
                "source_type": "web_error",
                "query": query
            }
    
    def get_search_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del sistema de búsqueda
        
        NOTA: Estadísticas de Azure eliminadas, preparado para nuevos proveedores.
        """
        try:
            rag_info = self.rag_system.get_collection_info()
            return {
                "rag_system": rag_info,
                "search_router": {
                    "status": "partial_service",
                    "rag_available": True,
                    "web_search_available": False,
                    "fallback_enabled": False,
                    "web_search_provider": "none_configured",
                    "azure_status": "removed",
                    "ready_for_integration": ["groq", "openai"]
                }
            }
        except Exception as e:
            return {"error": str(e)}


# ===== FUNCIONES DE BÚSQUEDA WEB =====

async def buscar_web(
    query: str, settings=None, top: int = None
) -> List[Dict[str, str]]:
    """
    Función principal de búsqueda web.

    NOTA: Todas las integraciones con Azure han sido eliminadas.
    Esta función está preparada para integración con nuevos proveedores.

    Args:
        query: Consulta de búsqueda
        settings: Configuración del sistema (opcional)
        top: Número máximo de resultados (opcional)

    Returns:
        Lista de diccionarios con resultados de búsqueda
    """
    try:
        logger.info(f"Búsqueda web solicitada: {query}")

        raise WebSearchError(
            "Servicio de búsqueda no disponible. "
            "Todas las integraciones con Azure han sido eliminadas. "
            "Preparado para integración con nuevos proveedores como Groq."
        )

    except Exception as e:
        logger.error(f"Error en búsqueda web: {e}")
        raise WebSearchError(f"Error en búsqueda web: {str(e)}")


async def buscar_web_completa(
    query: str, settings=None, top: int = None
) -> Dict[str, Any]:
    """
    Realiza búsqueda web completa.

    NOTA: Todas las integraciones con Azure han sido eliminadas.
    Esta función está preparada para integración con nuevos proveedores.

    Args:
        query: Consulta de búsqueda
        settings: Configuración del sistema (opcional)
        top: Número máximo de resultados

    Returns:
        Diccionario con resultados completos de búsqueda
    """
    try:
        logger.info(f"Búsqueda web completa solicitada: {query}")

        raise WebSearchError(
            "Servicio de búsqueda completa no disponible. "
            "Todas las integraciones con Azure han sido eliminadas. "
            "Preparado para integración con nuevos proveedores."
        )

    except Exception as e:
        logger.error(f"Error en búsqueda completa: {e}")
        raise WebSearchError(f"Error en búsqueda completa: {str(e)}")


async def refinar_query(query: str, settings=None) -> str:
    """
    Refina una consulta de búsqueda.

    NOTA: Todas las integraciones con Azure han sido eliminadas.
    Esta función está preparada para integración con nuevos proveedores.

    Args:
        query: Consulta original
        settings: Configuración del sistema (opcional)

    Returns:
        Consulta refinada
    """
    try:
        logger.info(f"Refinamiento de consulta solicitado: '{query}'")

        logger.warning("Usando refinamiento básico - proveedores Azure eliminados")
        return query.strip()

    except Exception as e:
        logger.error(f"Error refinando consulta: {e}")
        # Fallback simple si hay error
        return query.strip()


# ===== FUNCIONES DE CHAT Y GENERACIÓN =====

async def generar_respuesta(
    messages: List[Dict[str, str]], model: str = None, **kwargs
) -> Dict[str, Any]:
    """
    Genera una respuesta usando proveedores de IA.

    NOTA: Todas las integraciones con Azure han sido eliminadas.
    Esta función está preparada para integración con nuevos proveedores.

    Args:
        messages: Lista de mensajes de conversación
        model: Modelo específico a usar (opcional)
        **kwargs: Argumentos adicionales

    Returns:
        Respuesta generada
    """
    try:
        logger.info("Generación de respuesta solicitada")
        raise WebSearchError(
            "Servicio de generación de respuestas no disponible. "
            "Todas las integraciones con Azure han sido eliminadas. "
            "Preparado para integración con nuevos proveedores."
        )

    except Exception as e:
        logger.error(f"Error generando respuesta: {e}")
        raise WebSearchError(f"Error en generación de respuesta: {str(e)}")


async def chat_completion(
    messages: List[Dict[str, str]], model: str = None, **kwargs
) -> Dict[str, Any]:
    """
    Completación de chat usando ModelManager y Groq.

    Args:
        messages: Lista de mensajes de conversación
        model: Modelo específico a usar (opcional)
        **kwargs: Argumentos adicionales

    Returns:
        Respuesta de chat completion
    """
    try:
        logger.info("Chat completion solicitado")
        
        # Validar configuraciones
        config_status = settings.validate_settings()
        if not config_status["groq_api_key"]:
            raise WebSearchError(
                "GROQ_API_KEY no configurada. "
                "Configurar la API key para usar el servicio de chat."
            )
        
        # Usar ModelManager para chat completion
        response = await model_manager.chat_completion(
            messages=messages,
            model=model,
            **kwargs
        )
        
        return response

    except Exception as e:
        logger.error(f"Error en chat completion: {e}")
        raise WebSearchError(f"Error en chat completion: {str(e)}")


# ===== FUNCIONES DE ESTADO =====

async def get_search_status() -> Dict[str, Any]:
    """
    Obtiene el estado del servicio de búsqueda.

    Returns:
        Estado del servicio de búsqueda
    """
    try:
        # Validar configuraciones
        config_status = settings.validate_settings()
        
        # Obtener información de proveedores
        provider_info = model_manager.get_provider_info()
        
        # Validar conexiones
        provider_status = model_manager.validate_providers()
        
        status = "operational" if config_status["all_valid"] and any(provider_status.values()) else "degraded"
        
        return {
            "status": status,
            "message": "Servicio de búsqueda con integración Groq",
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
                "content_analysis": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de búsqueda: {e}")
        return {"status": "error", "message": str(e)}


# ===== INSTANCIA GLOBAL =====
search_router = SearchRouter()


# ===== COMENTARIOS PARA FUTURAS IMPLEMENTACIONES =====
# 
# async def groq_web_search_full(query, settings):
#     """Implementar búsqueda web completa con Groq"""
#     # Aquí se conectará GroqClient + herramientas de búsqueda
#     # Retornará formato compatible con el router actual
#     pass
# 
# async def groq_search_status():
#     """Verificar estado de Groq search"""
#     # Verificar GROQ_API_KEY y conectividad
#     pass
# 
# async def fallback_web_search(query, settings):
#     """Búsqueda web usando APIs públicas como fallback"""
#     # Implementar usando DuckDuckGo, SerpAPI, etc.
#     pass