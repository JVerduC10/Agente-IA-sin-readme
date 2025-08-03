import logging
from typing import Dict, Any
import requests
from urllib.parse import quote_plus
import time

from .rag import rag_system
from .metrics import metrics, measure_rag_latency

logger = logging.getLogger(__name__)

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
        """Búsqueda web usando DuckDuckGo"""
        try:
            # Usar DuckDuckGo Instant Answer API
            encoded_query = quote_plus(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extraer información relevante
            abstract = data.get('Abstract', '')
            abstract_text = data.get('AbstractText', '')
            abstract_url = data.get('AbstractURL', '')
            
            # Si no hay abstract, usar related topics o answer
            if not abstract_text:
                answer = data.get('Answer', '')
                if answer:
                    abstract_text = answer
                elif data.get('RelatedTopics'):
                    # Tomar el primer related topic
                    first_topic = data['RelatedTopics'][0]
                    if isinstance(first_topic, dict) and 'Text' in first_topic:
                        abstract_text = first_topic['Text']
            
            # Preparar respuesta
            if abstract_text:
                result = {
                    "answer": abstract_text,
                    "source_type": "web",
                    "query": query,
                    "references": []
                }
                
                if abstract_url:
                    result["references"].append({
                        "url": abstract_url,
                        "title": abstract or "DuckDuckGo Result",
                        "snippet": abstract_text[:200] + "..." if len(abstract_text) > 200 else abstract_text
                    })
                
                return result
            else:
                # Si no hay resultados útiles, hacer búsqueda básica
                return self.basic_web_search(query)
                
        except Exception as e:
            logger.error(f"Error en búsqueda web: {e}")
            return {
                "error": f"Error en búsqueda web: {str(e)}",
                "source_type": "web_error",
                "query": query
            }
    
    def basic_web_search(self, query: str) -> Dict[str, Any]:
        """Búsqueda web básica cuando DuckDuckGo no devuelve resultados"""
        return {
            "answer": f"No se encontraron resultados específicos para '{query}' en la búsqueda web. Intenta reformular tu pregunta o proporciona más contexto.",
            "source_type": "web_fallback",
            "query": query,
            "references": [{
                "url": f"https://duckduckgo.com/?q={quote_plus(query)}",
                "title": "Buscar en DuckDuckGo",
                "snippet": "Realizar búsqueda manual en DuckDuckGo"
            }]
        }
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de búsqueda"""
        try:
            rag_info = self.rag_system.get_collection_info()
            return {
                "rag_system": rag_info,
                "search_router": {
                    "status": "active",
                    "fallback_enabled": True,
                    "web_search_provider": "DuckDuckGo"
                }
            }
        except Exception as e:
            return {"error": str(e)}

# Instancia global
search_router = SearchRouter()