#!/usr/bin/env python3
"""
Demostración de integración modular completa:
- Vector store para memoria
- Reescritura iterativa de consultas
- Evaluación automática
- Sistema DeepSearch
"""

import os
import sys
import asyncio
import logging
import webbrowser
from typing import Dict, List, Any, Optional
from datetime import datetime

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from memory_store import VectorMemoryStore, MemoryStoreError
    from query_rewriter import IterativeQueryRewriter, QueryRewriteError, create_query_rewriter
    # Importar auto_evaluator desde tests/
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests'))
    from auto_evaluator import AutomaticEvaluator, EvaluationResult, create_auto_evaluator
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de que los archivos memory_store.py, query_rewriter.py estén en scripts/ y auto_evaluator.py en tests/")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModularDeepSearchSystem:
    """
    Sistema DeepSearch modular que integra:
    - Memoria vectorial para consultas pasadas
    - Reescritura iterativa de consultas
    - Evaluación automática de respuestas
    """
    
    def __init__(self, 
                 memory_store: VectorMemoryStore = None,
                 query_rewriter: IterativeQueryRewriter = None,
                 evaluator: AutomaticEvaluator = None):
        """
        Inicializa el sistema modular.
        
        Args:
            memory_store: Store de memoria vectorial
            query_rewriter: Reescritor de consultas
            evaluator: Evaluador automático
        """
        self.memory_store = memory_store or VectorMemoryStore()
        self.query_rewriter = query_rewriter or create_query_rewriter()
        self.evaluator = evaluator or create_auto_evaluator()
        
        # Estadísticas del sistema
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "memory_hits": 0,
            "query_rewrites": 0,
            "average_score": 0.0
        }
        
        logger.info("ModularDeepSearchSystem inicializado")
    
    def mock_search_function(self, query: str) -> List[Dict[str, Any]]:
        """
        Función de búsqueda simulada para demostración.
        En un sistema real, esto sería la función de búsqueda web.
        
        Args:
            query: Consulta de búsqueda
            
        Returns:
            Lista de resultados simulados
        """
        # Simular diferentes tipos de resultados basados en la consulta
        if "python" in query.lower():
            return [
                {
                    "title": "Python Programming Guide",
                    "url": "https://docs.python.org/3/tutorial/",
                    "snippet": "Python is an easy to learn, powerful programming language."
                },
                {
                    "title": "Real Python Tutorials",
                    "url": "https://realpython.com/",
                    "snippet": "Learn Python programming with tutorials and examples."
                }
            ]
        elif "machine learning" in query.lower() or "ml" in query.lower():
            return [
                {
                    "title": "Introduction to Machine Learning",
                    "url": "https://scikit-learn.org/stable/tutorial/",
                    "snippet": "Machine learning is a method of data analysis that automates analytical model building."
                },
                {
                    "title": "TensorFlow Documentation",
                    "url": "https://www.tensorflow.org/learn",
                    "snippet": "TensorFlow is an end-to-end open source platform for machine learning."
                }
            ]
        elif "web development" in query.lower():
            return [
                {
                    "title": "MDN Web Docs",
                    "url": "https://developer.mozilla.org/",
                    "snippet": "Resources for developers, by developers."
                },
                {
                    "title": "W3Schools Web Development",
                    "url": "https://www.w3schools.com/",
                    "snippet": "Learn web development with tutorials and examples."
                }
            ]
        else:
            return [
                {
                    "title": f"General information about {query}",
                    "url": "https://example.com/info",
                    "snippet": f"This is general information related to {query}."
                }
            ]
    
    def mock_evaluation_function(self, query: str, results: List[Dict[str, Any]]) -> float:
        """
        Función de evaluación simulada para el reescritor de consultas.
        
        Args:
            query: Consulta original
            results: Resultados de búsqueda
            
        Returns:
            Score de calidad (0.0 - 1.0)
        """
        if not results:
            return 0.0
        
        # Simular evaluación basada en número de resultados y relevancia
        base_score = min(len(results) / 5.0, 1.0)  # Más resultados = mejor score
        
        # Bonificar si hay términos clave en los snippets
        query_terms = set(query.lower().split())
        relevance_bonus = 0
        
        for result in results:
            snippet_terms = set(result.get("snippet", "").lower().split())
            overlap = len(query_terms.intersection(snippet_terms))
            relevance_bonus += overlap / max(len(query_terms), 1)
        
        relevance_bonus = min(relevance_bonus / len(results), 0.5)
        
        return min(base_score + relevance_bonus, 1.0)
    
    def generate_response(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        """
        Genera una respuesta basada en los resultados de búsqueda.
        
        Args:
            query: Consulta original
            search_results: Resultados de búsqueda
            
        Returns:
            Respuesta generada
        """
        if not search_results:
            return "Lo siento, no pude encontrar información relevante para tu consulta."
        
        # Construir respuesta basada en los resultados
        response_parts = []
        response_parts.append(f"Basándome en la búsqueda sobre '{query}', aquí tienes la información encontrada:\n")
        
        for i, result in enumerate(search_results[:3], 1):  # Limitar a 3 resultados
            title = result.get("title", "Sin título")
            snippet = result.get("snippet", "Sin descripción")
            url = result.get("url", "")
            
            response_parts.append(f"{i}. **{title}**")
            response_parts.append(f"   {snippet}")
            if url:
                response_parts.append(f"   Fuente: {url}")
            response_parts.append("")
        
        if len(search_results) > 3:
            response_parts.append(f"Y {len(search_results) - 3} resultados adicionales encontrados.")
        
        return "\n".join(response_parts)
    
    async def process_query(self, query: str, use_memory: bool = True, 
                          use_rewriter: bool = True, evaluate: bool = True) -> Dict[str, Any]:
        """
        Procesa una consulta usando todos los componentes modulares.
        
        Args:
            query: Consulta del usuario
            use_memory: Si usar el store de memoria
            use_rewriter: Si usar el reescritor de consultas
            evaluate: Si evaluar la respuesta
            
        Returns:
            Diccionario con resultados completos
        """
        start_time = datetime.now()
        self.stats["total_queries"] += 1
        
        try:
            # 1. Verificar memoria para consultas similares
            memory_results = None
            if use_memory:
                try:
                    memory_results = self.memory_store.search_similar_queries(query, max_results=3)
                    if memory_results:
                        self.stats["memory_hits"] += 1
                        logger.info(f"Encontradas {len(memory_results)} consultas similares en memoria")
                except MemoryStoreError as e:
                    logger.warning(f"Error accediendo a memoria: {e}")
            
            # 2. Reescribir consulta si es necesario
            final_query = query
            rewrite_info = None
            
            if use_rewriter:
                try:
                    rewrite_results = self.query_rewriter.rewrite_query_iteratively(
                        original_query=query,
                        search_function=self.mock_search_function,
                        evaluation_function=self.mock_evaluation_function
                    )
                    
                    if rewrite_results:
                        best_result = max(rewrite_results, key=lambda x: x.confidence)
                        if best_result.confidence > 0.6:  # Solo usar si hay mejora significativa
                            final_query = best_result.rewritten_query
                            self.stats["query_rewrites"] += 1
                            rewrite_info = {
                                "original_query": query,
                                "final_query": final_query,
                                "iterations": len(rewrite_results),
                                "improvement": best_result.confidence,
                                "strategies": [r.rewrite_strategy for r in rewrite_results]
                            }
                            logger.info(f"Consulta reescrita: '{query}' -> '{final_query}'")
                    
                except QueryRewriteError as e:
                    logger.warning(f"Error en reescritura: {e}")
            
            # 3. Realizar búsqueda con la consulta final
            search_results = self.mock_search_function(final_query)
            
            # 4. Generar respuesta
            response = self.generate_response(final_query, search_results)
            
            # 5. Evaluar respuesta
            evaluation_result = None
            if evaluate:
                try:
                    response_time = (datetime.now() - start_time).total_seconds()
                    sources = [r.get("url", "") for r in search_results if r.get("url")]
                    
                    evaluation_result = self.evaluator.evaluate_response(
                        query=query,
                        response=response,
                        query_type="web",
                        sources=sources,
                        response_time=response_time
                    )
                    
                    # Actualizar estadísticas
                    current_avg = self.stats["average_score"]
                    total_successful = self.stats["successful_queries"]
                    new_avg = (current_avg * total_successful + evaluation_result.overall_score) / (total_successful + 1)
                    self.stats["average_score"] = new_avg
                    
                except Exception as e:
                    logger.warning(f"Error en evaluación: {e}")
            
            # 6. Guardar en memoria para futuras consultas
            if use_memory and evaluation_result and evaluation_result.overall_score > 0.6:
                try:
                    sources = [r.get("url", "") for r in search_results if r.get("url")]
                    self.memory_store.store_memory(
                        query=query,
                        response=response,
                        query_type="web",
                        sources=sources,
                        confidence=evaluation_result.overall_score
                    )
                    logger.info("Consulta guardada en memoria")
                except MemoryStoreError as e:
                    logger.warning(f"Error guardando en memoria: {e}")
            
            self.stats["successful_queries"] += 1
            
            # Preparar resultado completo
            result = {
                "query": query,
                "final_query": final_query,
                "response": response,
                "search_results": search_results,
                "memory_results": memory_results,
                "rewrite_info": rewrite_info,
                "evaluation": evaluation_result.to_dict() if evaluation_result else None,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "success": True
            }
            
            logger.info(f"Consulta procesada exitosamente en {result['processing_time']:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error procesando consulta: {e}")
            return {
                "query": query,
                "response": f"Error procesando consulta: {e}",
                "error": str(e),
                "success": False
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del sistema.
        
        Returns:
            Diccionario con estadísticas
        """
        memory_stats = None
        try:
            memory_stats = self.memory_store.get_memory_stats()
        except Exception as e:
            logger.warning(f"Error obteniendo estadísticas de memoria: {e}")
        
        return {
            "system_stats": self.stats.copy(),
            "memory_stats": memory_stats,
            "success_rate": self.stats["successful_queries"] / max(self.stats["total_queries"], 1),
            "memory_hit_rate": self.stats["memory_hits"] / max(self.stats["total_queries"], 1),
            "rewrite_rate": self.stats["query_rewrites"] / max(self.stats["total_queries"], 1)
        }
    
    def cleanup(self):
        """
        Limpia recursos del sistema.
        """
        try:
            if hasattr(self.memory_store, 'cleanup'):
                self.memory_store.cleanup()
            logger.info("Sistema limpiado exitosamente")
        except Exception as e:
            logger.error(f"Error en limpieza: {e}")

async def demo_basic_usage():
    """
    Demostración básica del sistema modular.
    """
    print("\n=== DEMOSTRACIÓN BÁSICA ===")
    
    # Inicializar sistema
    system = ModularDeepSearchSystem()
    
    # Consultas de prueba
    test_queries = [
        "¿Cómo aprender Python?",
        "¿Qué es machine learning?",
        "Tutoriales de desarrollo web",
        "Python para principiantes",  # Similar a la primera
        "Algoritmos de ML",  # Similar a la segunda
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Consulta {i}: {query} ---")
        
        result = await system.process_query(query)
        results.append(result)
        
        if result["success"]:
            print(f"Respuesta: {result['response'][:200]}...")
            
            if result["rewrite_info"]:
                print(f"Consulta reescrita: {result['rewrite_info']['final_query']}")
            
            if result["evaluation"]:
                eval_data = result["evaluation"]
                print(f"Score de evaluación: {eval_data['overall_score']:.2f}")
                if eval_data["suggestions"]:
                    print(f"Sugerencias: {', '.join(eval_data['suggestions'][:2])}")
            
            if result["memory_results"]:
                print(f"Consultas similares en memoria: {len(result['memory_results'])}")
        else:
            print(f"Error: {result['error']}")
    
    # Mostrar estadísticas finales
    print("\n=== ESTADÍSTICAS DEL SISTEMA ===")
    stats = system.get_system_stats()
    
    print(f"Consultas totales: {stats['system_stats']['total_queries']}")
    print(f"Consultas exitosas: {stats['system_stats']['successful_queries']}")
    print(f"Tasa de éxito: {stats['success_rate']:.2%}")
    print(f"Hits de memoria: {stats['memory_hit_rate']:.2%}")
    print(f"Reescrituras: {stats['rewrite_rate']:.2%}")
    print(f"Score promedio: {stats['system_stats']['average_score']:.2f}")
    
    if stats["memory_stats"]:
        print(f"Entradas en memoria: {stats['memory_stats']['total_entries']}")
    
    # Limpiar
    system.cleanup()
    
    return results

async def demo_advanced_features():
    """
    Demostración de características avanzadas.
    """
    print("\n=== DEMOSTRACIÓN AVANZADA ===")
    
    # Configurar sistema con parámetros personalizados
    memory_store = VectorMemoryStore(collection_name="demo_advanced")
    
    # Configurar evaluador con pesos personalizados
    custom_weights = {
        "relevance": 0.3,
        "accuracy": 0.25,
        "completeness": 0.2,
        "readability": 0.15,
        "coherence": 0.1
    }
    evaluator = AutomaticEvaluator(weights=custom_weights)
    
    system = ModularDeepSearchSystem(
        memory_store=memory_store,
        evaluator=evaluator
    )
    
    # Consulta compleja
    complex_query = "Explica las diferencias entre machine learning supervisado y no supervisado con ejemplos prácticos"
    
    print(f"\nProcesando consulta compleja: {complex_query}")
    
    # Procesar con todas las características habilitadas
    result = await system.process_query(
        query=complex_query,
        use_memory=True,
        use_rewriter=True,
        evaluate=True
    )
    
    if result["success"]:
        print("\n--- RESULTADO DETALLADO ---")
        print(f"Consulta original: {result['query']}")
        print(f"Consulta final: {result['final_query']}")
        print(f"Tiempo de procesamiento: {result['processing_time']:.2f}s")
        
        if result["rewrite_info"]:
            rewrite = result["rewrite_info"]
            print(f"\nReescritura:")
            print(f"  Iteraciones: {rewrite['iterations']}")
            print(f"  Mejora: {rewrite['improvement']:.2f}")
            print(f"  Estrategias: {', '.join(rewrite['strategies'])}")
        
        if result["evaluation"]:
            eval_data = result["evaluation"]
            print(f"\nEvaluación:")
            print(f"  Score general: {eval_data['overall_score']:.2f}")
            print(f"  Métricas principales:")
            for metric, score in eval_data["metrics"].items():
                if metric in ["relevance", "accuracy", "completeness"]:
                    print(f"    {metric}: {score:.2f}")
            
            if eval_data["suggestions"]:
                print(f"  Sugerencias: {', '.join(eval_data['suggestions'])}")
        
        print(f"\nRespuesta generada:")
        print(result["response"])
    
    # Procesar consulta similar para probar memoria
    similar_query = "¿Cuál es la diferencia entre aprendizaje supervisado y no supervisado?"
    print(f"\n\nProcesando consulta similar: {similar_query}")
    
    result2 = await system.process_query(similar_query)
    
    if result2["success"] and result2["memory_results"]:
        print(f"¡Encontradas {len(result2['memory_results'])} consultas similares en memoria!")
        for i, mem_result in enumerate(result2["memory_results"], 1):
            print(f"  {i}. Similitud: {mem_result['similarity']:.2f} - {mem_result['query'][:50]}...")
    
    # Estadísticas finales
    stats = system.get_system_stats()
    print(f"\n--- ESTADÍSTICAS FINALES ---")
    print(f"Consultas procesadas: {stats['system_stats']['total_queries']}")
    print(f"Score promedio: {stats['system_stats']['average_score']:.2f}")
    
    system.cleanup()

async def main():
    """
    Función principal de demostración.
    """
    print("[DEMO] DEMOSTRACION DEL SISTEMA DEEPSEARCH MODULAR")
    print("================================================")
    print("")
    print("Este sistema integra:")
    print("[OK] Vector store para memoria de consultas")
    print("[OK] Reescritura iterativa de consultas")
    print("[OK] Evaluacion automatica de respuestas")
    print("[OK] Sistema DeepSearch modular")
    
    try:
        # Ejecutar demostraciones
        await demo_basic_usage()
        await demo_advanced_features()
        
        print("\nDemostración completada exitosamente!")
        print("\nEl sistema modular permite:")
        print("• Recordar consultas pasadas para respuestas más rápidas")
        print("• Mejorar automáticamente las consultas para mejores resultados")
        print("• Evaluar y optimizar continuamente la calidad de las respuestas")
        print("• Integración fácil con sistemas existentes")
        
        # Mostrar enlaces a los resultados en el navegador
        print("\n[OK] Resultados disponibles en el navegador:")
        print("  Página de resultados: http://localhost:8000/results")
        print("  📊 Últimos resultados: http://localhost:8000/results/latest")
        print("  📋 Lista completa: http://localhost:8000/results/list")
        print("  📈 Resumen: http://localhost:8000/results/summary")
        
        try:
            print("\n[INFO] Abriendo resultados en el navegador...")
            webbrowser.open("http://localhost:8000/results")
        except Exception as e:
            print(f"[WARN] No se pudo abrir el navegador automáticamente: {e}")
            print("  Puedes acceder manualmente a: http://localhost:8000/results")
        
    except Exception as e:
        logger.error(f"Error en demostración: {e}")
        print(f"\n[ERROR] Error en demostracion: {e}")

if __name__ == "__main__":
    # Ejecutar demostración
    asyncio.run(main())