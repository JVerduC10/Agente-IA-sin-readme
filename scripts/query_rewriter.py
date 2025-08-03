#!/usr/bin/env python3
"""
Sistema de reescritura iterativa de consultas para DeepSearch.
Mejora automáticamente las consultas basándose en los resultados obtenidos.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class QueryRewriteResult:
    """Resultado de una reescritura de consulta."""
    original_query: str
    rewritten_query: str
    rewrite_strategy: str
    confidence: float
    reasoning: str
    iteration: int

class QueryRewriteError(Exception):
    """Excepción para errores de reescritura de consultas."""
    pass

class IterativeQueryRewriter:
    """Sistema de reescritura iterativa de consultas."""
    
    def __init__(self, max_iterations: int = 3, min_confidence: float = 0.6):
        """
        Inicializa el reescritor de consultas.
        
        Args:
            max_iterations: Máximo número de iteraciones de reescritura
            min_confidence: Confianza mínima para aceptar una reescritura
        """
        self.max_iterations = max_iterations
        self.min_confidence = min_confidence
        
        # Patrones para diferentes tipos de mejoras
        self.improvement_patterns = {
            "specificity": [
                (r"\b(qué|que)\s+es\b", "definición características"),
                (r"\b(cómo|como)\s+funciona\b", "funcionamiento proceso mecanismo"),
                (r"\b(cuáles|cuales)\s+son\b", "tipos ejemplos lista"),
                (r"\b(dónde|donde)\b", "ubicación lugar localización"),
                (r"\b(cuándo|cuando)\b", "fecha tiempo momento"),
                (r"\b(por\s+qué|porque)\b", "razones causas motivos")
            ],
            "temporal": [
                (r"\b(actual|actualidad|hoy|ahora)\b", "2024 reciente último"),
                (r"\b(futuro|próximo)\b", "tendencias predicciones 2024 2025"),
                (r"\b(pasado|historia|histórico)\b", "evolución desarrollo historia")
            ],
            "technical": [
                (r"\b(IA|AI)\b", "inteligencia artificial machine learning"),
                (r"\b(ML)\b", "machine learning aprendizaje automático"),
                (r"\b(DL)\b", "deep learning aprendizaje profundo"),
                (r"\b(NLP)\b", "procesamiento lenguaje natural"),
                (r"\b(API)\b", "interfaz programación aplicaciones")
            ]
        }
        
        # Palabras de parada que pueden ser removidas para mejorar búsquedas
        self.stop_words = {
            "es", "son", "está", "están", "fue", "fueron", "ser", "estar",
            "el", "la", "los", "las", "un", "una", "unos", "unas",
            "de", "del", "en", "con", "por", "para", "sin", "sobre",
            "muy", "más", "menos", "tanto", "tan", "también", "además"
        }
        
        logger.info(f"IterativeQueryRewriter inicializado: max_iter={max_iterations}, min_conf={min_confidence}")
    
    def analyze_query_quality(self, query: str, search_results: List[Dict] = None) -> Dict[str, Any]:
        """
        Analiza la calidad de una consulta y sus resultados.
        
        Args:
            query: Consulta a analizar
            search_results: Resultados de búsqueda obtenidos
            
        Returns:
            Diccionario con métricas de calidad
        """
        analysis = {
            "query_length": len(query.split()),
            "has_question_words": bool(re.search(r"\b(qué|cómo|cuál|dónde|cuándo|por qué|quién)\b", query.lower())),
            "has_specific_terms": len(re.findall(r"\b[A-Z]{2,}\b", query)) > 0,  # Acrónimos
            "has_temporal_context": bool(re.search(r"\b(2024|2023|actual|reciente|último|nuevo)\b", query.lower())),
            "word_count": len(query.split()),
            "char_count": len(query),
            "complexity_score": 0.0
        }
        
        # Calcular puntuación de complejidad
        complexity = 0
        if analysis["query_length"] >= 5:
            complexity += 0.3
        if analysis["has_question_words"]:
            complexity += 0.2
        if analysis["has_specific_terms"]:
            complexity += 0.3
        if analysis["has_temporal_context"]:
            complexity += 0.2
        
        analysis["complexity_score"] = complexity
        
        # Analizar resultados si están disponibles
        if search_results:
            analysis["result_count"] = len(search_results)
            analysis["avg_snippet_length"] = sum(len(r.get("snippet", "")) for r in search_results) / max(len(search_results), 1)
            
            # Verificar relevancia de resultados
            query_terms = set(query.lower().split())
            relevant_results = 0
            
            for result in search_results:
                title = result.get("title", "").lower()
                snippet = result.get("snippet", "").lower()
                result_terms = set((title + " " + snippet).split())
                
                # Calcular intersección de términos
                intersection = query_terms.intersection(result_terms)
                if len(intersection) >= len(query_terms) * 0.3:  # Al menos 30% de coincidencia
                    relevant_results += 1
            
            analysis["relevance_ratio"] = relevant_results / max(len(search_results), 1)
        
        return analysis
    
    def generate_rewrite_strategies(self, query: str, analysis: Dict[str, Any]) -> List[Tuple[str, str, float]]:
        """
        Genera estrategias de reescritura basadas en el análisis de la consulta.
        
        Args:
            query: Consulta original
            analysis: Análisis de calidad de la consulta
            
        Returns:
            Lista de tuplas (estrategia, consulta_reescrita, confianza)
        """
        strategies = []
        
        # Estrategia 1: Agregar especificidad
        if analysis["complexity_score"] < 0.5:
            rewritten = self._add_specificity(query)
            if rewritten != query:
                strategies.append(("add_specificity", rewritten, 0.8))
        
        # Estrategia 2: Agregar contexto temporal
        if not analysis["has_temporal_context"]:
            rewritten = self._add_temporal_context(query)
            if rewritten != query:
                strategies.append(("add_temporal", rewritten, 0.7))
        
        # Estrategia 3: Expandir términos técnicos
        if analysis["has_specific_terms"]:
            rewritten = self._expand_technical_terms(query)
            if rewritten != query:
                strategies.append(("expand_technical", rewritten, 0.9))
        
        # Estrategia 4: Reformular pregunta
        if analysis["has_question_words"]:
            rewritten = self._reformulate_question(query)
            if rewritten != query:
                strategies.append(("reformulate_question", rewritten, 0.6))
        
        # Estrategia 5: Simplificar consulta compleja
        if analysis["word_count"] > 10:
            rewritten = self._simplify_query(query)
            if rewritten != query:
                strategies.append(("simplify", rewritten, 0.7))
        
        # Estrategia 6: Agregar sinónimos
        rewritten = self._add_synonyms(query)
        if rewritten != query:
            strategies.append(("add_synonyms", rewritten, 0.6))
        
        # Ordenar por confianza
        strategies.sort(key=lambda x: x[2], reverse=True)
        
        return strategies
    
    def _add_specificity(self, query: str) -> str:
        """Agrega especificidad a la consulta."""
        for pattern, replacement in self.improvement_patterns["specificity"]:
            if re.search(pattern, query.lower()):
                # Agregar términos específicos al final
                return f"{query} {replacement}"
        return query
    
    def _add_temporal_context(self, query: str) -> str:
        """Agrega contexto temporal a la consulta."""
        temporal_terms = ["2024", "actual", "reciente", "último"]
        
        # Verificar si ya tiene contexto temporal
        if any(term in query.lower() for term in temporal_terms):
            return query
        
        # Agregar contexto temporal apropiado
        if re.search(r"\b(tendencia|futuro|próximo)\b", query.lower()):
            return f"{query} 2024 2025"
        else:
            return f"{query} 2024 actual"
    
    def _expand_technical_terms(self, query: str) -> str:
        """Expande términos técnicos con sus formas completas."""
        expanded = query
        
        for pattern, expansion in self.improvement_patterns["technical"]:
            if re.search(pattern, query):
                # Extraer el patrón sin los delimitadores \b
                clean_pattern = pattern.strip('\\b')
                replacement = f"{clean_pattern} {expansion}"
                expanded = re.sub(pattern, replacement, expanded, flags=re.IGNORECASE)
        
        return expanded
    
    def _reformulate_question(self, query: str) -> str:
        """Reformula preguntas para mejorar los resultados de búsqueda."""
        # Convertir preguntas en declaraciones de búsqueda
        reformulations = {
            r"\b¿?qué es\b": "definición concepto",
            r"\b¿?cómo funciona\b": "funcionamiento proceso",
            r"\b¿?cuáles son\b": "tipos ejemplos lista",
            r"\b¿?dónde está\b": "ubicación localización",
            r"\b¿?cuándo ocurre\b": "fecha momento tiempo",
            r"\b¿?por qué\b": "razones causas motivos"
        }
        
        reformulated = query
        for pattern, replacement in reformulations.items():
            reformulated = re.sub(pattern, replacement, reformulated, flags=re.IGNORECASE)
        
        # Remover signos de interrogación
        reformulated = re.sub(r"[¿?]", "", reformulated)
        
        return reformulated.strip()
    
    def _simplify_query(self, query: str) -> str:
        """Simplifica consultas complejas removiendo palabras innecesarias."""
        words = query.split()
        
        # Remover palabras de parada
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        
        # Mantener al menos 3 palabras
        if len(filtered_words) < 3:
            return query
        
        return " ".join(filtered_words)
    
    def _add_synonyms(self, query: str) -> str:
        """Agrega sinónimos relevantes a la consulta."""
        synonym_map = {
            "inteligencia artificial": "IA AI machine learning",
            "aprendizaje automático": "machine learning ML algoritmos",
            "tecnología": "tech innovación digital",
            "desarrollo": "programación coding software",
            "análisis": "estudio investigación evaluación",
            "datos": "información data analytics"
        }
        
        enhanced = query
        for term, synonyms in synonym_map.items():
            if term.lower() in query.lower():
                enhanced += f" {synonyms}"
        
        return enhanced
    
    def rewrite_query_iteratively(self, 
                                 original_query: str,
                                 search_function,
                                 evaluation_function=None) -> List[QueryRewriteResult]:
        """
        Reescribe una consulta iterativamente hasta obtener mejores resultados.
        
        Args:
            original_query: Consulta original
            search_function: Función que realiza la búsqueda
            evaluation_function: Función opcional para evaluar resultados
            
        Returns:
            Lista de resultados de reescritura por iteración
        """
        results = []
        current_query = original_query
        best_score = 0.0
        best_query = original_query
        
        logger.info(f"Iniciando reescritura iterativa para: {original_query}")
        
        for iteration in range(self.max_iterations):
            try:
                # Realizar búsqueda con la consulta actual
                search_results = search_function(current_query)
                
                # Analizar calidad de la consulta y resultados
                analysis = self.analyze_query_quality(current_query, search_results)
                
                # Evaluar resultados si se proporciona función de evaluación
                evaluation_score = 0.5  # Score por defecto
                if evaluation_function:
                    evaluation_score = evaluation_function(current_query, search_results)
                else:
                    # Evaluación básica basada en análisis
                    evaluation_score = (
                        analysis.get("relevance_ratio", 0.5) * 0.4 +
                        min(analysis.get("result_count", 0) / 10, 1.0) * 0.3 +
                        analysis.get("complexity_score", 0.5) * 0.3
                    )
                
                # Registrar resultado de esta iteración
                rewrite_result = QueryRewriteResult(
                    original_query=original_query,
                    rewritten_query=current_query,
                    rewrite_strategy=f"iteration_{iteration}",
                    confidence=evaluation_score,
                    reasoning=f"Analysis: {analysis}",
                    iteration=iteration
                )
                results.append(rewrite_result)
                
                # Actualizar mejor resultado
                if evaluation_score > best_score:
                    best_score = evaluation_score
                    best_query = current_query
                
                # Si el score es suficientemente bueno, terminar
                if evaluation_score >= 0.8:
                    logger.info(f"Score satisfactorio alcanzado: {evaluation_score:.2f}")
                    break
                
                # Generar estrategias de reescritura para la siguiente iteración
                strategies = self.generate_rewrite_strategies(current_query, analysis)
                
                if not strategies:
                    logger.info("No hay más estrategias de reescritura disponibles")
                    break
                
                # Seleccionar la mejor estrategia
                best_strategy = strategies[0]
                strategy_name, new_query, confidence = best_strategy
                
                if confidence < self.min_confidence:
                    logger.info(f"Confianza de reescritura muy baja: {confidence:.2f}")
                    break
                
                logger.info(f"Iteración {iteration + 1}: {strategy_name} -> {new_query[:50]}...")
                current_query = new_query
                
            except Exception as e:
                logger.error(f"Error en iteración {iteration}: {e}")
                break
        
        # Asegurar que el mejor resultado esté al final
        if best_query != current_query:
            final_result = QueryRewriteResult(
                original_query=original_query,
                rewritten_query=best_query,
                rewrite_strategy="best_overall",
                confidence=best_score,
                reasoning="Mejor resultado de todas las iteraciones",
                iteration=-1
            )
            results.append(final_result)
        
        logger.info(f"Reescritura completada: {len(results)} iteraciones, mejor score: {best_score:.2f}")
        return results
    
    def get_best_query(self, rewrite_results: List[QueryRewriteResult]) -> str:
        """Obtiene la mejor consulta de los resultados de reescritura."""
        if not rewrite_results:
            return ""
        
        best_result = max(rewrite_results, key=lambda x: x.confidence)
        return best_result.rewritten_query
    
    def explain_rewrite_process(self, rewrite_results: List[QueryRewriteResult]) -> str:
        """Genera una explicación del proceso de reescritura."""
        if not rewrite_results:
            return "No se realizaron reescrituras."
        
        explanation = f"Proceso de reescritura para: '{rewrite_results[0].original_query}'\n\n"
        
        for i, result in enumerate(rewrite_results):
            explanation += f"Iteración {result.iteration + 1}:\n"
            explanation += f"  Estrategia: {result.rewrite_strategy}\n"
            explanation += f"  Consulta: {result.rewritten_query}\n"
            explanation += f"  Confianza: {result.confidence:.2f}\n"
            explanation += f"  Razonamiento: {result.reasoning[:100]}...\n\n"
        
        best_result = max(rewrite_results, key=lambda x: x.confidence)
        explanation += f"Mejor resultado: '{best_result.rewritten_query}' (confianza: {best_result.confidence:.2f})"
        
        return explanation

def create_query_rewriter(settings=None) -> IterativeQueryRewriter:
    """
    Factory function para crear un IterativeQueryRewriter.
    
    Args:
        settings: Objeto de configuración con parámetros opcionales
        
    Returns:
        IterativeQueryRewriter instance
    """
    config = {
        "max_iterations": 3,
        "min_confidence": 0.6
    }
    
    if settings:
        if hasattr(settings, 'REWRITER_MAX_ITERATIONS'):
            config["max_iterations"] = settings.REWRITER_MAX_ITERATIONS
        if hasattr(settings, 'REWRITER_MIN_CONFIDENCE'):
            config["min_confidence"] = settings.REWRITER_MIN_CONFIDENCE
    
    return IterativeQueryRewriter(**config)

if __name__ == "__main__":
    # Ejemplo de uso
    def mock_search(query: str) -> List[Dict]:
        """Función de búsqueda mock para testing."""
        return [
            {"title": f"Resultado para {query}", "snippet": f"Información sobre {query}", "url": "https://example.com"}
        ]
    
    def mock_evaluation(query: str, results: List[Dict]) -> float:
        """Función de evaluación mock."""
        return len(results) * 0.2 + len(query.split()) * 0.1
    
    rewriter = IterativeQueryRewriter()
    
    # Probar reescritura iterativa
    results = rewriter.rewrite_query_iteratively(
        "¿Qué es IA?",
        mock_search,
        mock_evaluation
    )
    
    print(f"Resultados de reescritura: {len(results)}")
    print(f"Mejor consulta: {rewriter.get_best_query(results)}")
    print(f"\nExplicación:\n{rewriter.explain_rewrite_process(results)}")