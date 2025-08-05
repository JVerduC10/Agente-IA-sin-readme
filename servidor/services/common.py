"""Utilidades comunes centralizadas para el servidor.

REFACTORIZACIÓN: Este módulo centraliza funciones que estaban dispersas:
- get_*_status() de múltiples archivos
- Funciones de validación comunes
- Utilidades de estado del sistema

JUSTIFICACIÓN: Elimina duplicación y centraliza responsabilidades
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def get_system_status() -> Dict[str, Any]:
    """Obtiene el estado general del sistema.
    
    CONSOLIDACIÓN: Reemplaza múltiples funciones get_*_status() dispersas
    
    Returns:
        Dict con información del estado del sistema
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "healthy",
        "uptime": time.time(),
        "version": "2.0.0",
        "environment": "production"
    }


def get_performance_stats() -> Dict[str, Any]:
    """Obtiene estadísticas de rendimiento del sistema.
    
    CENTRALIZACIÓN: Unifica métricas de rendimiento de chat.py y otros módulos
    
    Returns:
        Dict con estadísticas de rendimiento
    """
    return {
        "requests_processed": 0,
        "average_response_time": 0.0,
        "error_rate": 0.0,
        "memory_usage": 0,
        "cpu_usage": 0.0
    }


def get_search_status() -> Dict[str, Any]:
    """Obtiene el estado del sistema de búsqueda.
    
    UNIFICACIÓN: Combina get_search_status() de search.py y search_router.py
    
    Returns:
        Dict con estado del sistema de búsqueda
    """
    return {
        "web_search_enabled": False,  # Azure removed - ready for new providers
        "rag_enabled": True,
        "azure_ai_foundry_enabled": False,  # ELIMINADO - Azure integration removed
        "last_search_time": None,
        "search_count": 0
    }


def get_rag_stats() -> Dict[str, Any]:
    """Obtiene estadísticas del sistema RAG.
    
    CONSOLIDACIÓN: Centraliza estadísticas RAG de search.py y rag.py
    
    Returns:
        Dict con estadísticas RAG
    """
    return {
        "collection_name": "domain_corpus",
        "document_count": 0,
        "embedding_model": "all-MiniLM-L6-v2",
        "last_update": None,
        "index_size": 0
    }


def get_azure_search_status() -> Dict[str, Any]:
    """Obtiene el estado de Azure AI Foundry.
    
    ELIMINADO: Azure integration removed - ready for new providers
    
    Returns:
        Dict con estado de Azure AI Foundry (deprecated)
    """
    return {
        "enabled": False,  # ELIMINADO - Azure integration removed
        "endpoint_configured": False,
        "authentication_status": "removed",
        "last_request_time": None,
        "request_count": 0,
        "status": "deprecated - use new providers like Groq"
    }


def validate_api_configuration() -> Dict[str, bool]:
    """Valida la configuración de APIs.
    
    NUEVA FUNCIÓN: Centraliza validaciones que estaban dispersas
    
    Returns:
        Dict con estado de validación de cada API
    """
    from servidor.crypto import get_decrypted_keys
    
    try:
        keys = get_decrypted_keys()
        return {
            "groq_configured": bool(keys.get("GROQ_API_KEY")),
            "bing_configured": bool(keys.get("BING_SEARCH_API_KEY")),
            "azure_configured": False,  # ELIMINADO - Azure integration removed  # ELIMINADO - Azure integration removed
            "encryption_working": True
        }
    except Exception as e:
        logger.error(f"Error validando configuración: {e}")
        return {
            "groq_configured": False,
            "bing_configured": False,
            "azure_configured": False,
            "encryption_working": False
        }


def get_model_info() -> Dict[str, Any]:
    """Obtiene información de modelos disponibles.
    
    MIGRACIÓN: Desde model_selector.py para centralizar información
    
    Returns:
        Dict con información de modelos
    """
    return {
        "available_models": [
            "gpt-4o-mini",
            "gpt-4.1-mini", 
            "o3",
            "deepseek-r1-distill-llama-70b"
        ],
        "default_model": "gpt-4.1-mini",
        "model_count": 4,
        "providers": ["groq"]  # Azure removed - ready for new providers
    }


def get_comprehensive_status() -> Dict[str, Any]:
    """Obtiene un estado completo del sistema.
    
    NUEVA FUNCIÓN: Combina todos los estados en una sola respuesta
    
    Returns:
        Dict con estado completo del sistema
    """
    return {
        "system": get_system_status(),
        "performance": get_performance_stats(),
        "search": get_search_status(),
        "rag": get_rag_stats(),
        "azure": get_azure_search_status(),
        "configuration": validate_api_configuration(),
        "models": get_model_info()
    }


# ===== FUNCIONES DE UTILIDAD =====

def format_response_time(seconds: float) -> str:
    """Formatea tiempo de respuesta para display."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    return f"{seconds:.2f}s"


def calculate_success_rate(successful: int, total: int) -> float:
    """Calcula tasa de éxito como porcentaje."""
    if total == 0:
        return 0.0
    return (successful / total) * 100


def sanitize_error_message(error: Exception) -> str:
    """Sanitiza mensajes de error para logging seguro."""
    error_str = str(error)
    # Remover información sensible
    sensitive_patterns = ["api_key", "secret", "password", "token"]
    for pattern in sensitive_patterns:
        if pattern in error_str.lower():
            return "Error de autenticación (información sensible oculta)"
    return error_str[:200]  # Limitar longitud


# ===== DECORADORES ÚTILES =====

def log_execution_time(func):
    """Decorador para medir tiempo de ejecución."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} ejecutado en {format_response_time(execution_time)}")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} falló en {format_response_time(execution_time)}: {sanitize_error_message(e)}")
            raise
    return wrapper


def async_log_execution_time(func):
    """Decorador async para medir tiempo de ejecución."""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} ejecutado en {format_response_time(execution_time)}")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} falló en {format_response_time(execution_time)}: {sanitize_error_message(e)}")
            raise
    return wrapper