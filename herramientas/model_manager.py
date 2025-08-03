import logging
from typing import Dict, Any, Optional
from enum import Enum
import asyncio
import time

from servidor.settings import Settings
from servidor.usage import DailyTokenCounter
from herramientas.groq_client import GroqClient
from herramientas.bing_client import BingClient

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Proveedores de modelos disponibles."""
    GROQ = "groq"
    BING = "bing"


class ModelPerformanceTracker:
    """Rastrea el rendimiento de cada modelo para competencia."""
    
    def __init__(self):
        self.stats = {
            ModelProvider.GROQ: {
                "total_requests": 0,
                "errors": 0,
                "total_response_time": 0.0,
                "avg_response_time": 0.0,
                "success_rate": 0.0
            },
            ModelProvider.BING: {
                "total_requests": 0,
                "errors": 0,
                "total_response_time": 0.0,
                "avg_response_time": 0.0,
                "success_rate": 0.0
            }
        }
    
    def record_request(self, provider: ModelProvider, response_time: float, success: bool):
        """Registra una solicitud y su rendimiento."""
        stats = self.stats[provider]
        stats["total_requests"] += 1
        
        if success:
            stats["total_response_time"] += response_time
            stats["avg_response_time"] = stats["total_response_time"] / stats["total_requests"]
        else:
            stats["errors"] += 1
        
        # Calcular tasa de éxito
        stats["success_rate"] = (stats["total_requests"] - stats["errors"]) / stats["total_requests"]
    
    def get_best_performer(self) -> ModelProvider:
        """Determina el mejor modelo basado en rendimiento."""
        groq_score = self._calculate_score(ModelProvider.GROQ)
        
        logger.info(f"Groq score: {groq_score:.3f}")
        
        return ModelProvider.GROQ  # Solo Groq disponible
    
    def _calculate_score(self, provider: ModelProvider) -> float:
        """Calcula un score de rendimiento combinado."""
        stats = self.stats[provider]
        
        if stats["total_requests"] == 0:
            return 0.0
        
        # Score basado en tasa de éxito (70%) y velocidad (30%)
        success_weight = 0.7
        speed_weight = 0.3
        
        success_score = stats["success_rate"]
        
        # Score de velocidad (invertido - menor tiempo es mejor)
        # Normalizar entre 0 y 1, asumiendo que 10 segundos es muy lento
        max_acceptable_time = 10.0
        speed_score = max(0, 1 - (stats["avg_response_time"] / max_acceptable_time))
        
        return (success_score * success_weight) + (speed_score * speed_weight)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas completas."""
        return {
            "groq": self.stats[ModelProvider.GROQ].copy(),
            "openai": self.stats[ModelProvider.OPENAI].copy(),
            "best_performer": self.get_best_performer().value
        }


class ModelManager:
    """Administrador de modelos que gestiona la competencia entre Groq y OpenAI."""
    
    def __init__(self, settings: Settings, token_counter: DailyTokenCounter):
        self.settings = settings
        self.token_counter = token_counter
        self.performance_tracker = ModelPerformanceTracker()
        
        # Obtener claves desencriptadas
        decrypted_keys = settings.get_decrypted_keys()
        
        # Inicializar cliente Groq
        self.groq_client = None
        
        if decrypted_keys["GROQ_API_KEY"]:
            # Crear configuración temporal para Groq
            groq_settings = Settings(
                GROQ_API_KEY=decrypted_keys["GROQ_API_KEY"],
                GROQ_MODEL=settings.GROQ_MODEL,
                GROQ_BASE_URL=settings.GROQ_BASE_URL
            )
            self.groq_client = GroqClient(groq_settings, token_counter)
        
        # Inicializar cliente Bing
        self.bing_client = None
        if decrypted_keys["SEARCH_API_KEY"]:
            self.bing_client = BingClient(settings, token_counter)
    
    async def chat_completion(self, prompt: str, temperature: float = 1.0, 
                            preferred_provider: Optional[ModelProvider] = None) -> str:
        """Genera respuesta usando el mejor modelo disponible o el preferido."""
        
        # Determinar qué proveedor usar
        if preferred_provider:
            provider = preferred_provider
        else:
            # Usar el mejor proveedor disponible
            provider = self.performance_tracker.get_best_performer()
        
        # Intentar con el proveedor seleccionado
        try:
            return await self._execute_with_provider(provider, prompt, temperature)
        except Exception as e:
            logger.warning(f"Error con {provider.value}: {e}. Intentando con fallback.")
            
            # Fallback al otro proveedor disponible
            available_providers = self.get_available_providers()
            fallback_providers = [p for p in available_providers if p != provider]
            
            if fallback_providers:
                fallback_provider = fallback_providers[0]
                try:
                    return await self._execute_with_provider(fallback_provider, prompt, temperature)
                except Exception as fallback_error:
                    logger.error(f"Error también con fallback {fallback_provider.value}: {fallback_error}")
                    raise Exception(f"Ambos modelos fallaron. Último error: {fallback_error}")
            else:
                raise Exception(f"Error ejecutando con {provider.value}: {e}")
    
    async def _execute_with_provider(self, provider: ModelProvider, prompt: str, temperature: float) -> str:
        """Ejecuta la solicitud con un proveedor específico y registra métricas."""
        start_time = time.time()
        success = False
        
        try:
            if provider == ModelProvider.GROQ:
                if not self.groq_client:
                    raise ValueError("Cliente Groq no disponible")
                response = await self.groq_client.chat_completion(prompt, temperature)
            elif provider == ModelProvider.BING:
                if not self.bing_client:
                    raise ValueError("Cliente Bing no disponible")
                response = await self.bing_client.chat_completion(prompt, temperature)
            else:
                raise ValueError(f"Proveedor desconocido: {provider}")
            
            success = True
            return response
            
        finally:
            # Registrar métricas de rendimiento
            response_time = time.time() - start_time
            self.performance_tracker.record_request(provider, response_time, success)
            
            logger.info(f"Solicitud a {provider.value}: {response_time:.3f}s, éxito: {success}")
    
    async def compete_models(self, prompt: str, temperature: float = 1.0) -> Dict[str, Any]:
        """Ejecuta solo con Groq ya que OpenAI no está disponible."""
        if not self.groq_client:
            raise ValueError("Cliente Groq no está disponible")
        
        try:
            # Solo ejecutar con Groq
            groq_response = await self._execute_with_provider(ModelProvider.GROQ, prompt, temperature)
            
            result = {
                "groq_response": groq_response,
                "openai_response": "OpenAI no disponible - API key no configurada",
                "best_performer": "groq",
                "winning_response": groq_response,
                "performance_stats": self.performance_tracker.get_stats()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error ejecutando con Groq: {e}")
            raise
    
    def get_available_providers(self) -> list[ModelProvider]:
        """Retorna lista de proveedores disponibles con verificación mejorada."""
        providers = []
        
        # Verificar Groq
        if self.groq_client:
            try:
                # Verificar que el cliente tiene configuración válida
                if hasattr(self.groq_client, 'settings') and self.groq_client.settings.GROQ_API_KEY:
                    providers.append(ModelProvider.GROQ)
                    logger.info("✅ Groq client disponible")
                else:
                    logger.warning("⚠️ Groq client sin API key válida")
            except Exception as e:
                logger.error(f"❌ Error verificando Groq client: {e}")
        else:
            logger.warning("⚠️ Groq client no inicializado")
            
        # Verificar Bing
        if self.bing_client:
            try:
                # Verificar que el cliente tiene configuración válida
                if hasattr(self.bing_client, 'settings') and hasattr(self.bing_client.settings, 'get_decrypted_keys'):
                    decrypted_keys = self.bing_client.settings.get_decrypted_keys()
                    if decrypted_keys.get("SEARCH_API_KEY"):
                        providers.append(ModelProvider.BING)
                        logger.info("✅ Bing client disponible")
                    else:
                        logger.warning("⚠️ Bing client sin API key válida")
                else:
                    logger.warning("⚠️ Bing client sin configuración válida")
            except Exception as e:
                logger.error(f"❌ Error verificando Bing client: {e}")
        else:
            logger.warning("⚠️ Bing client no inicializado")
            
        logger.info(f"Proveedores disponibles: {[p.value for p in providers]}")
        return providers
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de rendimiento."""
        return self.performance_tracker.get_stats()