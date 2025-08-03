import logging
import asyncio
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

from ..settings import Settings
from ..exceptions import WebSearchError

logger = logging.getLogger(__name__)

class SearchStrategy(ABC):
    """Estrategia abstracta para b�squeda web"""
    
    @abstractmethod
    async def search(self, query: str, count: int) -> List[Dict[str, str]]:
        pass

class LegacyBingStrategy(SearchStrategy):
    """Estrategia legacy de Bing (temporal hasta migraci�n Azure)"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def search(self, query: str, count: int) -> List[Dict[str, str]]:
        """B�squeda usando API legacy de Bing"""
        # Implementaci�n temporal que maneja el error 401
        logger.warning("Using legacy Bing API - migration to Azure AI Agents required")
        
        # Retornar resultado vac�o con mensaje informativo
        return [{
            "titulo": "Servicio de b�squeda temporalmente no disponible",
            "snippet": "La API de Bing ha sido retirada. Se requiere migraci�n a Azure AI Agents.",
            "url": "https://docs.microsoft.com/azure/ai-services/"
        }]

class UnifiedSearchService:
    """Servicio unificado de b�squeda web"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.strategy = LegacyBingStrategy(settings)
    
    async def search(self, query: str, count: int = 5) -> List[Dict[str, str]]:
        """Realizar b�squeda web"""
        try:
            return await self.strategy.search(query, count)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise WebSearchError(f"Error en b�squeda: {str(e)}")

# Instancia global
search_service = None

def get_search_service(settings: Settings) -> UnifiedSearchService:
    """Obtener instancia del servicio de b�squeda"""
    global search_service
    if search_service is None:
        search_service = UnifiedSearchService(settings)
    return search_service

# Funci�n de compatibilidad
async def buscar_web(query: str, settings: Settings, top: int = None) -> List[Dict[str, str]]:
    """Funci�n de compatibilidad para b�squeda web"""
    if top is None:
        top = settings.MAX_SEARCH_RESULTS
    
    service = get_search_service(settings)
    return await service.search(query, top)
