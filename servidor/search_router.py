import logging
from typing import Dict, Any, Optional
import requests
from urllib.parse import quote_plus
import time
import asyncio

from .rag import rag_system
from .metrics import metrics, measure_rag_latency
from .settings import Settings
from .utils.search import buscar_web, WebSearchError
from .usage import DailyTokenCounter
from herramientas.groq_client import GroqClient

logger = logging.getLogger(__name__)
settings = Settings()

class SearchRouter:
    """Router que decide entre RAG y búsqueda web"""
    
    def __init__(self):
        self.rag_system = rag_system
        self.token_counter = DailyTokenCounter()
        self.groq_client = GroqClient(settings, self.token_counter)
    
    @measure_rag_latency('total')
    def search(self, query: str) -> Dict[str, Any]:
        """Busca usando RAG o web según disponibilidad y relevancia"""
        try:
            start_time = time.time()
            
            # Intentar búsqueda RAG primero
            logger.info(f"Procesando consulta: '{query}'")
            
            with measure_rag_latency('rag_router'):
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
                
                with measure_rag_latency('web_search'):
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
        """Búsqueda web usando Bing y respuesta generada con Groq"""
        try:
            # Realizar búsqueda web con Bing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                search_results = loop.run_until_complete(
                    buscar_web(query, settings, top=5)
                )
            finally:
                loop.close()
            
            if not search_results:
                return {
                    "answer": f"No se encontraron resultados web para '{query}'. Intenta reformular tu pregunta.",
                    "source_type": "web_no_results",
                    "query": query,
                    "references": []
                }
            
            # Preparar contexto para Groq
            context = "\n\n".join([
                f"Fuente {i+1}: {result['titulo']}\n{result['snippet']}\nURL: {result['url']}"
                for i, result in enumerate(search_results)
            ])
            
            # Generar respuesta con Groq
            prompt = f"""Responde a la consulta del usuario basándote únicamente en la información proporcionada de las fuentes web.

Consulta: {query}

Información de fuentes web:
{context}

Instrucciones:
- Proporciona una respuesta clara y concisa
- Cita las fuentes relevantes
- Si la información no es suficiente, indícalo
- Mantén un tono informativo y profesional

Respuesta:"""
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                answer = loop.run_until_complete(
                    self.groq_client.chat_completion(prompt, temperature=0.3)
                )
            finally:
                loop.close()
            
            # Preparar referencias
            references = [
                {
                    "title": result["titulo"],
                    "snippet": result["snippet"],
                    "url": result["url"],
                    "similarity": 0.8  # Valor fijo para compatibilidad
                }
                for result in search_results
            ]
            
            return {
                "answer": answer,
                "source_type": "web_search",
                "query": query,
                "references": references
            }
            
        except WebSearchError as e:
            logger.error(f"Error en búsqueda web: {e}")
            return {
                "answer": f"Error en la búsqueda web: {str(e)}. Verifica la configuración de la API de Bing.",
                "source_type": "web_error",
                "query": query,
                "references": []
            }
        except Exception as e:
            logger.error(f"Error inesperado en búsqueda web: {e}")
            return {
                "answer": f"Error inesperado en la búsqueda web. Intenta nuevamente más tarde.",
                "source_type": "web_error",
                "query": query,
                "references": []
            }
    
    def basic_web_search(self, query: str) -> Dict[str, Any]:
        """Búsqueda web básica usando Bing con respuesta simple"""
        try:
            # Realizar búsqueda web con Bing (menos resultados para búsqueda básica)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                search_results = loop.run_until_complete(
                    buscar_web(query, settings, top=3)
                )
            finally:
                loop.close()
            
            if not search_results:
                return {
                    "answer": f"No se encontraron resultados específicos para '{query}'. Intenta reformular tu pregunta o proporciona más contexto.",
                    "source_type": "web_fallback",
                    "query": query,
                    "references": []
                }
            
            # Para búsqueda básica, generar una respuesta más simple
            context = "\n".join([
                f"• {result['titulo']}: {result['snippet']}"
                for result in search_results[:2]  # Solo los primeros 2 resultados
            ])
            
            prompt = f"""Proporciona una respuesta breve y directa basada en esta información web:

Consulta: {query}

Información encontrada:
{context}

Respuesta breve (máximo 2-3 oraciones):"""
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                answer = loop.run_until_complete(
                    self.groq_client.chat_completion(prompt, temperature=0.2)
                )
            finally:
                loop.close()
            
            # Preparar referencias simplificadas
            references = [
                {
                    "title": result["titulo"],
                    "url": result["url"],
                    "similarity": 0.7
                }
                for result in search_results[:2]
            ]
            
            return {
                "answer": answer,
                "source_type": "web_basic",
                "query": query,
                "references": references
            }
            
        except WebSearchError as e:
            logger.error(f"Error en búsqueda web básica: {e}")
            return {
                "answer": f"Búsqueda web no disponible: {str(e)}",
                "source_type": "web_error",
                "query": query,
                "references": []
            }
        except Exception as e:
            logger.error(f"Error en búsqueda web básica: {e}")
            return {
                "answer": f"Error en la búsqueda. Intenta nuevamente.",
                "source_type": "web_error",
                "query": query,
                "references": []
            }
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de búsqueda"""
        try:
            rag_info = self.rag_system.get_collection_info()
            
            # Verificar si Bing está configurado
            bing_configured = (
                settings.SEARCH_API_KEY and 
                settings.SEARCH_API_KEY != "your_bing_api_key_here"
            )
            
            return {
                "rag_system": rag_info,
                "search_router": {
                    "status": "active",
                    "fallback_enabled": bing_configured,
                    "web_search_provider": "bing" if bing_configured else "not_configured",
                    "llm_provider": "groq"
                }
            }
        except Exception as e:
            return {"error": str(e)}

# Instancia global
search_router = SearchRouter()