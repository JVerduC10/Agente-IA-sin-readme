#!/usr/bin/env python3
"""
Sistema de evaluación automática para DeepSearch.
Evalúa la calidad de respuestas y optimiza el rendimiento del sistema.
"""

import re
import json
import logging
import statistics
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import hashlib

try:
    from textstat import flesch_reading_ease, flesch_kincaid_grade
except ImportError:
    flesch_reading_ease = None
    flesch_kincaid_grade = None

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
except ImportError:
    SentimentIntensityAnalyzer = None

# Configurar logging
logger = logging.getLogger(__name__)

class EvaluationMetric(Enum):
    """Métricas de evaluación disponibles."""
    RELEVANCE = "relevance"
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    READABILITY = "readability"
    COHERENCE = "coherence"
    FACTUALITY = "factuality"
    SOURCE_QUALITY = "source_quality"
    RESPONSE_TIME = "response_time"
    FRESHNESS = "freshness"
    COVERAGE = "coverage"

@dataclass
class EvaluationResult:
    """Resultado de evaluación de una respuesta."""
    query: str
    response: str
    query_type: str
    timestamp: str
    metrics: Dict[str, float]
    overall_score: float
    sources: List[str]
    evaluation_id: str
    feedback: Dict[str, str]
    suggestions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvaluationResult':
        return cls(**data)

class AutoEvaluatorError(Exception):
    """Excepción para errores del evaluador automático."""
    pass

class AutomaticEvaluator:
    """Sistema de evaluación automática para respuestas de DeepSearch."""
    
    def __init__(self, 
                 weights: Dict[str, float] = None,
                 thresholds: Dict[str, float] = None):
        """
        Inicializa el evaluador automático.
        
        Args:
            weights: Pesos para cada métrica en el score final
            thresholds: Umbrales mínimos para cada métrica
        """
        # Configuración por defecto
        default_weights = {
            EvaluationMetric.RELEVANCE.value: 0.25,
            EvaluationMetric.ACCURACY.value: 0.20,
            EvaluationMetric.COMPLETENESS.value: 0.15,
            EvaluationMetric.READABILITY.value: 0.10,
            EvaluationMetric.COHERENCE.value: 0.10,
            EvaluationMetric.SOURCE_QUALITY.value: 0.10,
            EvaluationMetric.FRESHNESS.value: 0.05,
            EvaluationMetric.COVERAGE.value: 0.05
        }
        
        default_thresholds = {
            EvaluationMetric.RELEVANCE.value: 0.6,
            EvaluationMetric.ACCURACY.value: 0.7,
            EvaluationMetric.COMPLETENESS.value: 0.5,
            EvaluationMetric.READABILITY.value: 0.4,
            EvaluationMetric.COHERENCE.value: 0.6
        }
        
        self.weights = weights or default_weights
        self.thresholds = thresholds or default_thresholds
        
        # Inicializar herramientas de análisis si están disponibles
        self.sentiment_analyzer = None
        if SentimentIntensityAnalyzer:
            try:
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
            except Exception as e:
                logger.warning(f"No se pudo inicializar analizador de sentimientos: {e}")
        
        # Patrones compilados para mejor rendimiento
        self.patterns = {
            "factual_indicators": re.compile(
                r"\b(según|de acuerdo con|estudios muestran|investigación indica|estadísticas|datos|porcentaje|cifras|año|fecha|\d{4})\b",
                re.IGNORECASE
            ),
            "uncertainty_indicators": re.compile(
                r"\b(posiblemente|quizás|tal vez|probablemente|puede que|no estoy seguro|no está claro|es incierto)\b",
                re.IGNORECASE
            ),
            "source_citations": re.compile(
                r"https?://[^\s]+|\b(fuente|referencia|enlace|link)\b",
                re.IGNORECASE
            )
        }
        
        logger.info("AutomaticEvaluator inicializado")
    
    def evaluate_relevance(self, query: str, response: str, sources: List[str] = None) -> Tuple[float, str]:
        """
        Evalúa la relevancia de la respuesta con respecto a la consulta.
        
        Args:
            query: Consulta original
            response: Respuesta generada
            sources: Fuentes utilizadas
            
        Returns:
            Tupla (score, feedback)
        """
        try:
            # Extraer términos clave de la consulta
            query_terms = set(re.findall(r'\b\w+\b', query.lower()))
            response_terms = set(re.findall(r'\b\w+\b', response.lower()))
            
            # Calcular intersección de términos
            common_terms = query_terms.intersection(response_terms)
            
            # Score base por coincidencia de términos
            term_overlap = len(common_terms) / max(len(query_terms), 1)
            
            # Bonificación por responder directamente a palabras interrogativas
            question_words = ["qué", "cómo", "cuál", "dónde", "cuándo", "por qué", "quién"]
            addresses_question = any(word in query.lower() for word in question_words)
            
            if addresses_question:
                # Verificar si la respuesta aborda el tipo de pregunta
                if "qué es" in query.lower() and ("es" in response.lower() or "definición" in response.lower()):
                    term_overlap += 0.2
                elif "cómo" in query.lower() and ("proceso" in response.lower() or "pasos" in response.lower()):
                    term_overlap += 0.2
                elif "cuál" in query.lower() and ("tipos" in response.lower() or "ejemplos" in response.lower()):
                    term_overlap += 0.2
            
            # Penalización por respuestas muy cortas o muy largas
            response_length = len(response.split())
            if response_length < 20:
                term_overlap *= 0.8  # Respuesta muy corta
            elif response_length > 500:
                term_overlap *= 0.9  # Respuesta muy larga
            
            score = min(term_overlap, 1.0)
            
            feedback = f"Coincidencia de términos: {len(common_terms)}/{len(query_terms)}"
            if addresses_question:
                feedback += ", aborda pregunta directamente"
            
            return score, feedback
            
        except Exception as e:
            logger.error(f"Error evaluando relevancia: {e}")
            return 0.5, f"Error en evaluación: {e}"
    
    def evaluate_completeness(self, query: str, response: str, sources: List[str] = None) -> Tuple[float, str]:
        """
        Evalúa la completitud de la respuesta.
        
        Args:
            query: Consulta original
            response: Respuesta generada
            sources: Fuentes utilizadas
            
        Returns:
            Tupla (score, feedback)
        """
        try:
            # Aspectos que una respuesta completa debería cubrir
            expected_aspects = []
            
            if "qué es" in query.lower():
                expected_aspects = ["definición", "características", "ejemplos"]
            elif "cómo funciona" in query.lower():
                expected_aspects = ["proceso", "pasos", "mecanismo"]
            elif "cuáles son" in query.lower():
                expected_aspects = ["lista", "tipos", "ejemplos"]
            elif "ventajas" in query.lower() or "beneficios" in query.lower():
                expected_aspects = ["ventajas", "beneficios", "pros"]
            elif "desventajas" in query.lower() or "problemas" in query.lower():
                expected_aspects = ["desventajas", "problemas", "contras"]
            
            if not expected_aspects:
                # Aspectos generales para cualquier consulta
                expected_aspects = ["información", "contexto", "detalles"]
            
            # Verificar presencia de aspectos esperados
            covered_aspects = 0
            response_lower = response.lower()
            
            for aspect in expected_aspects:
                if aspect in response_lower:
                    covered_aspects += 1
            
            # Score base por cobertura de aspectos
            aspect_coverage = covered_aspects / max(len(expected_aspects), 1)
            
            # Bonificación por estructura organizada
            structure_bonus = 0
            if re.search(r'\d+\.\s', response):  # Lista numerada
                structure_bonus += 0.1
            if re.search(r'[-•]\s', response):  # Lista con viñetas
                structure_bonus += 0.1
            if len(re.findall(r'\n\n', response)) >= 2:  # Párrafos separados
                structure_bonus += 0.1
            
            # Bonificación por longitud apropiada
            word_count = len(response.split())
            length_bonus = 0
            if 50 <= word_count <= 300:
                length_bonus = 0.2
            elif 30 <= word_count <= 500:
                length_bonus = 0.1
            
            score = min(aspect_coverage + structure_bonus + length_bonus, 1.0)
            
            feedback = f"Aspectos cubiertos: {covered_aspects}/{len(expected_aspects)}"
            if structure_bonus > 0:
                feedback += ", bien estructurada"
            if length_bonus > 0:
                feedback += ", longitud apropiada"
            
            return score, feedback
            
        except Exception as e:
            logger.error(f"Error evaluando completitud: {e}")
            return 0.5, f"Error en evaluación: {e}"
    
    def evaluate_readability(self, response: str) -> Tuple[float, str]:
        """
        Evalúa la legibilidad de la respuesta.
        
        Args:
            response: Respuesta generada
            
        Returns:
            Tupla (score, feedback)
        """
        try:
            # Métricas básicas de legibilidad
            sentences = len(re.findall(r'[.!?]+', response))
            words = len(response.split())
            characters = len(response)
            
            if sentences == 0 or words == 0:
                return 0.0, "Respuesta vacía o sin estructura"
            
            # Promedio de palabras por oración
            avg_words_per_sentence = words / sentences
            
            # Promedio de caracteres por palabra
            avg_chars_per_word = characters / words
            
            # Score basado en métricas de legibilidad
            readability_score = 1.0
            
            # Penalizar oraciones muy largas
            if avg_words_per_sentence > 25:
                readability_score -= 0.3
            elif avg_words_per_sentence > 20:
                readability_score -= 0.1
            
            # Penalizar palabras muy largas
            if avg_chars_per_word > 7:
                readability_score -= 0.2
            elif avg_chars_per_word > 6:
                readability_score -= 0.1
            
            # Usar textstat si está disponible
            if flesch_reading_ease and flesch_kincaid_grade:
                try:
                    flesch_score = flesch_reading_ease(response)
                    # Normalizar score de Flesch (0-100) a (0-1)
                    flesch_normalized = flesch_score / 100
                    readability_score = (readability_score + flesch_normalized) / 2
                except Exception:
                    pass
            
            # Bonificación por uso de conectores
            connectors = ["además", "sin embargo", "por tanto", "en consecuencia", "por ejemplo"]
            connector_count = sum(1 for conn in connectors if conn in response.lower())
            if connector_count > 0:
                readability_score += min(connector_count * 0.05, 0.2)
            
            score = max(0.0, min(readability_score, 1.0))
            
            feedback = f"Promedio palabras/oración: {avg_words_per_sentence:.1f}, chars/palabra: {avg_chars_per_word:.1f}"
            
            return score, feedback
            
        except Exception as e:
            logger.error(f"Error evaluando legibilidad: {e}")
            return 0.5, f"Error en evaluación: {e}"
    
    def evaluate_source_quality(self, sources: List[str]) -> Tuple[float, str]:
        """
        Evalúa la calidad de las fuentes utilizadas.
        
        Args:
            sources: Lista de URLs de fuentes
            
        Returns:
            Tupla (score, feedback)
        """
        try:
            if not sources:
                return 0.0, "No se proporcionaron fuentes"
            
            # Dominios de alta calidad
            high_quality_domains = {
                "wikipedia.org": 0.9,
                "edu": 0.95,
                "gov": 0.9,
                "org": 0.7,
                "nature.com": 0.95,
                "science.org": 0.95,
                "ieee.org": 0.9,
                "acm.org": 0.9
            }
            
            # Dominios de calidad media
            medium_quality_domains = {
                "com": 0.5,
                "net": 0.4,
                "info": 0.3
            }
            
            total_score = 0
            domain_feedback = []
            
            for source in sources:
                source_score = 0.3  # Score base
                
                # Verificar dominio
                for domain, score in high_quality_domains.items():
                    if domain in source.lower():
                        source_score = score
                        domain_feedback.append(f"{domain}: alta calidad")
                        break
                else:
                    for domain, score in medium_quality_domains.items():
                        if source.lower().endswith(domain):
                            source_score = score
                            domain_feedback.append(f"{domain}: calidad media")
                            break
                
                # Bonificación por HTTPS
                if source.startswith("https://"):
                    source_score += 0.1
                
                total_score += source_score
            
            # Promedio de calidad de fuentes
            avg_score = total_score / len(sources)
            
            # Bonificación por diversidad de fuentes
            unique_domains = set()
            for source in sources:
                try:
                    domain = source.split("//")[1].split("/")[0]
                    unique_domains.add(domain)
                except:
                    pass
            
            diversity_bonus = min(len(unique_domains) * 0.1, 0.3)
            final_score = min(avg_score + diversity_bonus, 1.0)
            
            feedback = f"Fuentes: {len(sources)}, dominios únicos: {len(unique_domains)}"
            if domain_feedback:
                feedback += f", calidad: {', '.join(domain_feedback[:3])}"
            
            return final_score, feedback
            
        except Exception as e:
            logger.error(f"Error evaluando calidad de fuentes: {e}")
            return 0.5, f"Error en evaluación: {e}"
    
    def evaluate_factuality(self, response: str) -> Tuple[float, str]:
        """
        Evalúa la factualidad de la respuesta.
        
        Args:
            response: Respuesta generada
            
        Returns:
            Tupla (score, feedback)
        """
        try:
            # Indicadores de factualidad
            factual_score = 0.5  # Score base
            feedback_items = []
            
            # Buscar indicadores factuales
            factual_indicators = 0
            for pattern in self.patterns["factual_indicators"]:
                matches = len(re.findall(pattern, response.lower()))
                factual_indicators += matches
            
            if factual_indicators > 0:
                factual_score += min(factual_indicators * 0.1, 0.3)
                feedback_items.append(f"indicadores factuales: {factual_indicators}")
            
            # Penalizar indicadores de incertidumbre
            uncertainty_indicators = 0
            for pattern in self.patterns["uncertainty_indicators"]:
                matches = len(re.findall(pattern, response.lower()))
                uncertainty_indicators += matches
            
            if uncertainty_indicators > 0:
                factual_score -= min(uncertainty_indicators * 0.1, 0.2)
                feedback_items.append(f"indicadores de incertidumbre: {uncertainty_indicators}")
            
            # Bonificar presencia de números y fechas específicas
            numbers = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', response))
            dates = len(re.findall(r'\b\d{4}\b|\b\d{1,2}/\d{1,2}/\d{4}\b', response))
            
            if numbers > 0:
                factual_score += min(numbers * 0.05, 0.2)
                feedback_items.append(f"números específicos: {numbers}")
            
            if dates > 0:
                factual_score += min(dates * 0.05, 0.1)
                feedback_items.append(f"fechas específicas: {dates}")
            
            # Verificar presencia de citas o referencias
            citations = 0
            for pattern in self.patterns["source_citations"]:
                matches = len(re.findall(pattern, response))
                citations += matches
            
            if citations > 0:
                factual_score += min(citations * 0.1, 0.2)
                feedback_items.append(f"citas/referencias: {citations}")
            
            final_score = max(0.0, min(factual_score, 1.0))
            feedback = ", ".join(feedback_items) if feedback_items else "análisis básico de factualidad"
            
            return final_score, feedback
            
        except Exception as e:
            logger.error(f"Error evaluando factualidad: {e}")
            return 0.5, f"Error en evaluación: {e}"
    
    def evaluate_coherence(self, response: str) -> Tuple[float, str]:
        """
        Evalúa la coherencia y fluidez de la respuesta.
        
        Args:
            response: Respuesta generada
            
        Returns:
            Tupla (score, feedback)
        """
        try:
            coherence_score = 0.5  # Score base
            feedback_items = []
            
            # Verificar estructura lógica
            paragraphs = response.split('\n\n')
            if len(paragraphs) > 1:
                coherence_score += 0.2
                feedback_items.append("estructura en párrafos")
            
            # Verificar transiciones entre ideas
            transition_words = ["además", "sin embargo", "por otro lado", "en consecuencia", 
                              "por tanto", "finalmente", "en resumen", "por ejemplo"]
            
            transition_count = sum(1 for word in transition_words if word in response.lower())
            if transition_count > 0:
                coherence_score += min(transition_count * 0.1, 0.3)
                feedback_items.append(f"palabras de transición: {transition_count}")
            
            # Verificar repetición excesiva
            words = response.lower().split()
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Solo palabras significativas
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            max_repetition = max(word_freq.values()) if word_freq else 0
            if max_repetition > len(words) * 0.1:  # Más del 10% de repetición
                coherence_score -= 0.2
                feedback_items.append("repetición excesiva detectada")
            
            # Verificar longitud de oraciones variada
            sentences = re.split(r'[.!?]+', response)
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            
            if sentence_lengths:
                length_variance = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0
                if length_variance > 3:  # Buena variación en longitud
                    coherence_score += 0.1
                    feedback_items.append("variación en longitud de oraciones")
            
            # Usar análisis de sentimientos si está disponible
            if self.sentiment_analyzer:
                try:
                    sentiment = self.sentiment_analyzer.polarity_scores(response)
                    # Respuestas neutrales o ligeramente positivas son más coherentes
                    if -0.1 <= sentiment['compound'] <= 0.5:
                        coherence_score += 0.1
                        feedback_items.append("tono apropiado")
                except Exception:
                    pass
            
            final_score = max(0.0, min(coherence_score, 1.0))
            feedback = ", ".join(feedback_items) if feedback_items else "análisis básico de coherencia"
            
            return final_score, feedback
            
        except Exception as e:
            logger.error(f"Error evaluando coherencia: {e}")
            return 0.5, f"Error en evaluación: {e}"
    
    def evaluate_response(self, 
                         query: str, 
                         response: str, 
                         query_type: str,
                         sources: List[str] = None,
                         response_time: float = None) -> EvaluationResult:
        """
        Evalúa una respuesta completa usando todas las métricas.
        
        Args:
            query: Consulta original
            response: Respuesta generada
            query_type: Tipo de consulta
            sources: Fuentes utilizadas
            response_time: Tiempo de respuesta en segundos
            
        Returns:
            EvaluationResult con todas las métricas
        """
        try:
            metrics = {}
            feedback = {}
            suggestions = []
            
            # Evaluar cada métrica
            relevance_score, relevance_feedback = self.evaluate_relevance(query, response, sources)
            metrics[EvaluationMetric.RELEVANCE.value] = relevance_score
            feedback[EvaluationMetric.RELEVANCE.value] = relevance_feedback
            
            completeness_score, completeness_feedback = self.evaluate_completeness(query, response, sources)
            metrics[EvaluationMetric.COMPLETENESS.value] = completeness_score
            feedback[EvaluationMetric.COMPLETENESS.value] = completeness_feedback
            
            readability_score, readability_feedback = self.evaluate_readability(response)
            metrics[EvaluationMetric.READABILITY.value] = readability_score
            feedback[EvaluationMetric.READABILITY.value] = readability_feedback
            
            factuality_score, factuality_feedback = self.evaluate_factuality(response)
            metrics[EvaluationMetric.FACTUALITY.value] = factuality_score
            feedback[EvaluationMetric.FACTUALITY.value] = factuality_feedback
            
            coherence_score, coherence_feedback = self.evaluate_coherence(response)
            metrics[EvaluationMetric.COHERENCE.value] = coherence_score
            feedback[EvaluationMetric.COHERENCE.value] = coherence_feedback
            
            if sources:
                source_quality_score, source_quality_feedback = self.evaluate_source_quality(sources)
                metrics[EvaluationMetric.SOURCE_QUALITY.value] = source_quality_score
                feedback[EvaluationMetric.SOURCE_QUALITY.value] = source_quality_feedback
            
            if response_time is not None:
                # Evaluar tiempo de respuesta (óptimo: 2-10 segundos)
                if response_time <= 2:
                    time_score = 1.0
                elif response_time <= 10:
                    time_score = 1.0 - (response_time - 2) * 0.1
                else:
                    time_score = max(0.2, 1.0 - (response_time - 10) * 0.05)
                
                metrics[EvaluationMetric.RESPONSE_TIME.value] = time_score
                feedback[EvaluationMetric.RESPONSE_TIME.value] = f"Tiempo: {response_time:.2f}s"
            
            # Calcular score general
            overall_score = 0
            for metric, score in metrics.items():
                weight = self.weights.get(metric, 0)
                overall_score += score * weight
            
            # Generar sugerencias basadas en métricas bajas
            for metric, score in metrics.items():
                threshold = self.thresholds.get(metric, 0.5)
                if score < threshold:
                    if metric == EvaluationMetric.RELEVANCE.value:
                        suggestions.append("Mejorar relevancia: incluir más términos de la consulta")
                    elif metric == EvaluationMetric.COMPLETENESS.value:
                        suggestions.append("Mejorar completitud: agregar más detalles y ejemplos")
                    elif metric == EvaluationMetric.READABILITY.value:
                        suggestions.append("Mejorar legibilidad: usar oraciones más cortas y claras")
                    elif metric == EvaluationMetric.FACTUALITY.value:
                        suggestions.append("Mejorar factualidad: agregar datos específicos y referencias")
                    elif metric == EvaluationMetric.COHERENCE.value:
                        suggestions.append("Mejorar coherencia: usar mejores transiciones entre ideas")
            
            # Crear ID único para la evaluación
            evaluation_id = hashlib.md5(
                f"{query}_{response[:100]}_{datetime.now().isoformat()}".encode()
            ).hexdigest()
            
            result = EvaluationResult(
                query=query,
                response=response,
                query_type=query_type,
                timestamp=datetime.now().isoformat(),
                metrics=metrics,
                overall_score=overall_score,
                sources=sources or [],
                evaluation_id=evaluation_id,
                feedback=feedback,
                suggestions=suggestions
            )
            
            logger.info(f"Evaluación completada: {evaluation_id[:8]}... Score: {overall_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error en evaluación completa: {e}")
            raise AutoEvaluatorError(f"Error en evaluación: {e}")
    
    def batch_evaluate(self, evaluations: List[Dict[str, Any]]) -> List[EvaluationResult]:
        """
        Evalúa múltiples respuestas en lote.
        
        Args:
            evaluations: Lista de diccionarios con datos de evaluación
            
        Returns:
            Lista de EvaluationResult
        """
        results = []
        
        for eval_data in evaluations:
            try:
                result = self.evaluate_response(
                    query=eval_data.get("query", ""),
                    response=eval_data.get("response", ""),
                    query_type=eval_data.get("query_type", "unknown"),
                    sources=eval_data.get("sources", []),
                    response_time=eval_data.get("response_time")
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error evaluando elemento del lote: {e}")
                continue
        
        logger.info(f"Evaluación en lote completada: {len(results)}/{len(evaluations)} exitosas")
        return results
    
    def get_evaluation_summary(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Genera un resumen de múltiples evaluaciones.
        
        Args:
            results: Lista de resultados de evaluación
            
        Returns:
            Diccionario con estadísticas resumidas
        """
        if not results:
            return {"error": "No hay resultados para resumir"}
        
        # Calcular estadísticas por métrica
        metric_stats = {}
        for metric in EvaluationMetric:
            scores = [r.metrics.get(metric.value, 0) for r in results if metric.value in r.metrics]
            if scores:
                metric_stats[metric.value] = {
                    "mean": statistics.mean(scores),
                    "median": statistics.median(scores),
                    "min": min(scores),
                    "max": max(scores),
                    "stdev": statistics.stdev(scores) if len(scores) > 1 else 0
                }
        
        # Estadísticas generales
        overall_scores = [r.overall_score for r in results]
        
        summary = {
            "total_evaluations": len(results),
            "overall_stats": {
                "mean_score": statistics.mean(overall_scores),
                "median_score": statistics.median(overall_scores),
                "min_score": min(overall_scores),
                "max_score": max(overall_scores),
                "stdev": statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0
            },
            "metric_stats": metric_stats,
            "query_types": {},
            "common_suggestions": []
        }
        
        # Estadísticas por tipo de consulta
        query_type_scores = {}
        for result in results:
            qt = result.query_type
            if qt not in query_type_scores:
                query_type_scores[qt] = []
            query_type_scores[qt].append(result.overall_score)
        
        for qt, scores in query_type_scores.items():
            summary["query_types"][qt] = {
                "count": len(scores),
                "mean_score": statistics.mean(scores),
                "median_score": statistics.median(scores)
            }
        
        # Sugerencias más comunes
        all_suggestions = []
        for result in results:
            all_suggestions.extend(result.suggestions)
        
        suggestion_counts = {}
        for suggestion in all_suggestions:
            suggestion_counts[suggestion] = suggestion_counts.get(suggestion, 0) + 1
        
        # Top 5 sugerencias más comunes
        top_suggestions = sorted(suggestion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        summary["common_suggestions"] = [s[0] for s in top_suggestions]
        
        return summary

def create_auto_evaluator(settings=None) -> AutomaticEvaluator:
    """
    Factory function para crear un AutomaticEvaluator.
    
    Args:
        settings: Objeto de configuración con parámetros opcionales
        
    Returns:
        AutomaticEvaluator instance
    """
    weights = None
    thresholds = None
    
    if settings:
        if hasattr(settings, 'EVALUATOR_WEIGHTS'):
            weights = settings.EVALUATOR_WEIGHTS
        if hasattr(settings, 'EVALUATOR_THRESHOLDS'):
            thresholds = settings.EVALUATOR_THRESHOLDS
    
    return AutomaticEvaluator(weights=weights, thresholds=thresholds)

if __name__ == "__main__":
    # Ejemplo de uso
    evaluator = AutomaticEvaluator()
    
    # Evaluar una respuesta
    result = evaluator.evaluate_response(
        query="¿Qué es la inteligencia artificial?",
        response="La inteligencia artificial es una rama de la informática que se ocupa de la creación de sistemas inteligentes. Estos sistemas pueden realizar tareas que normalmente requieren inteligencia humana, como el reconocimiento de patrones, el aprendizaje y la toma de decisiones.",
        query_type="web",
        sources=["https://es.wikipedia.org/wiki/Inteligencia_artificial"],
        response_time=3.5
    )
    
    print(f"Score general: {result.overall_score:.2f}")
    print(f"Métricas: {result.metrics}")
    print(f"Sugerencias: {result.suggestions}")