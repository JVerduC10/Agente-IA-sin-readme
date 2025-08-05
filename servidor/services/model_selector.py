#!/usr/bin/env python3
"""
Selector de modelos - Integración con Groq

Este módulo implementa la lógica de selección inteligente de modelos Groq
basada en el contenido del mensaje y parámetros contextuales.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def select_model_from_message(
    message: str, 
    *, 
    has_image: bool = False, 
    is_critical: bool = False, 
    context_length: int = 0, 
    tokens_remaining: int = 1_000_000
) -> Dict[str, Any]:
    """
    Selecciona el mejor modelo Groq disponible en función del mensaje y parámetros contextuales.
    
    Parámetros:
    - message: texto del mensaje del usuario
    - has_image: True si el mensaje incluye imagen o requiere visión artificial
    - is_critical: True si el resultado es crítico (output final, decisión sensible, cliente)
    - context_length: número de tokens estimado del input (útil para textos largos)
    - tokens_remaining: tokens disponibles en presupuesto

    Retorna:
    - Diccionario con 'model_selected', 'reason', y 'task_summary'
    """
    
    message_lower = message.lower()
    
    logger.info(f"Seleccionando modelo para mensaje: {message[:50]}...")
    logger.debug(f"Parámetros: has_image={has_image}, is_critical={is_critical}, context_length={context_length}, tokens_remaining={tokens_remaining}")
    
    # --- Reglas para modelos Groq ---
    # Nota: Groq actualmente no soporta visión, usar modelo de texto más capaz
    if has_image:
        result = {
            "model_selected": "llama-3.1-70b-versatile",
            "reason": "Imagen detectada - usando modelo más capaz (Groq no soporta visión actualmente).",
            "task_summary": message[:100]
        }
        logger.info(f"Modelo seleccionado: {result['model_selected']} - {result['reason']}")
        return result
    
    # Detectar contenido visual por palabras clave
    visual_keywords = ["foto", "imagen", "gráfico", "visual", "diagrama", "captura", "screenshot"]
    if any(keyword in message_lower for keyword in visual_keywords):
        result = {
            "model_selected": "llama-3.1-70b-versatile",
            "reason": "El mensaje sugiere contenido visual - usando modelo más capaz.",
            "task_summary": message[:100]
        }
        logger.info(f"Modelo seleccionado: {result['model_selected']} - {result['reason']}")
        return result
    
    # Detectar OCR o procesamiento de imagen
    ocr_keywords = ["ocr", "ver imagen", "leer texto", "extraer texto", "reconocer texto"]
    if any(keyword in message_lower for keyword in ocr_keywords):
        result = {
            "model_selected": "llama-3.1-70b-versatile",
            "reason": "OCR o procesamiento de texto requerido.",
            "task_summary": message[:100]
        }
        logger.info(f"Modelo seleccionado: {result['model_selected']} - {result['reason']}")
        return result
    
    # --- Reglas para tareas complejas (razonamiento complejo, contexto largo o tarea crítica)
    complex_keywords = [
        "análisis profundo", "resumen largo", "decisión", "clasificación múltiple", 
        "pipeline", "estrategia", "documento legal", "jurídico", "multietapa", 
        "resumen extenso", "procesamiento complejo", "razonamiento", "lógica compleja",
        "investigación", "análisis detallado", "evaluación crítica", "comparación exhaustiva"
    ]
    
    if (is_critical or 
        context_length > 50_000 or 
        any(keyword in message_lower for keyword in complex_keywords)):
        
        result = {
            "model_selected": "deepseek-r1-distill-llama-70b",
            "reason": "Tarea crítica o con razonamiento complejo o contexto muy largo.",
            "task_summary": message[:100]
        }
        logger.info(f"Modelo seleccionado: {result['model_selected']} - {result['reason']}")
        return result
    
    # Detectar tareas que requieren velocidad
    speed_keywords = ["rápido", "urgente", "inmediato", "quick", "fast"]
    if any(keyword in message_lower for keyword in speed_keywords):
        result = {
            "model_selected": "llama-3.1-8b-instant",
            "reason": "Tarea que requiere respuesta rápida.",
            "task_summary": message[:100]
        }
        logger.info(f"Modelo seleccionado: {result['model_selected']} - {result['reason']}")
        return result
    
    # --- Modelo por defecto
    result = {
        "model_selected": "llama-3.1-70b-versatile",
        "reason": "Tarea general, redacción, resumen normal o soporte conversacional.",
        "task_summary": message[:100]
    }
    logger.info(f"Modelo seleccionado: {result['model_selected']} - {result['reason']}")
    return result


def get_available_models() -> List[str]:
    """
    Retorna la lista de modelos Groq disponibles.
    """
    models = [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant", 
        "deepseek-r1-distill-llama-70b",
        "llama-3.2-90b-text-preview",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    
    logger.info(f"Modelos Groq disponibles: {models}")
    return models


def validate_model_selection(model_name: str) -> bool:
    """
    Valida que el modelo seleccionado esté disponible.
    
    Args:
        model_name: Nombre del modelo a validar
        
    Returns:
        True si el modelo está disponible, False en caso contrario
    """
    available_models = get_available_models()
    is_valid = model_name in available_models
    
    if not is_valid:
        logger.error(f"Modelo no válido: {model_name}. Modelos disponibles: {list(available_models.keys())}")
    
    return is_valid


def get_model_info(model_name: str) -> Dict[str, Any]:
    """
    Retorna información detallada sobre un modelo Groq específico.
    """
    model_info = {
        "llama-3.1-70b-versatile": {
            "description": "Modelo versátil de 70B parámetros para tareas generales y complejas",
            "capabilities": ["general_purpose", "conversation", "writing", "complex_reasoning"],
            "max_tokens": 131072,
            "cost_tier": "medium"
        },
        "llama-3.1-8b-instant": {
            "description": "Modelo rápido de 8B parámetros para respuestas instantáneas",
            "capabilities": ["fast_response", "conversation", "simple_tasks"],
            "max_tokens": 131072,
            "cost_tier": "low"
        },
        "deepseek-r1-distill-llama-70b": {
            "description": "Modelo especializado en razonamiento complejo y tareas críticas",
            "capabilities": ["complex_reasoning", "critical_tasks", "analysis"],
            "max_tokens": 131072,
            "cost_tier": "high"
        },
        "llama-3.2-90b-text-preview": {
            "description": "Modelo de 90B parámetros para procesamiento de texto avanzado",
            "capabilities": ["text_processing", "long_context", "analysis"],
            "max_tokens": 131072,
            "cost_tier": "high"
        },
        "mixtral-8x7b-32768": {
            "description": "Modelo Mixtral con arquitectura de expertos para tareas diversas",
            "capabilities": ["general_purpose", "multilingual", "reasoning"],
            "max_tokens": 32768,
            "cost_tier": "medium"
        },
        "gemma2-9b-it": {
            "description": "Modelo Gemma2 optimizado para instrucciones y conversación",
            "capabilities": ["instruction_following", "conversation", "general_purpose"],
            "max_tokens": 8192,
            "cost_tier": "low"
        }
    }
    
    return model_info.get(model_name, {
        "description": "Modelo no encontrado",
        "capabilities": [],
        "max_tokens": 0,
        "cost_tier": "unknown"
    })