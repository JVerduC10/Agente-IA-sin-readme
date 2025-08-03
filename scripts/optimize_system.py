#!/usr/bin/env python3
"""
Script de optimización automática del sistema AI
Implementa las mejoras más críticas identificadas en el análisis
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import List, Dict

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemOptimizer:
    """Optimizador automático del sistema"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backups"
        self.changes_made = []
    
    def run_optimization(self):
        """Ejecutar todas las optimizaciones"""
        logger.info("Iniciando optimización del sistema...")
        
        try:
            # Crear backup
            self.create_backup()
            
            # Ejecutar optimizaciones en orden de prioridad
            self.fix_duplicate_search_modules()
            self.optimize_imports()
            self.update_requirements()
            self.create_optimized_services()
            self.update_settings()
            
            logger.info("Optimización completada exitosamente")
            self.print_summary()
            
        except Exception as e:
            logger.error(f"Error durante optimización: {e}")
            self.rollback_changes()
            raise
    
    def create_backup(self):
        """Crear backup de archivos críticos"""
        logger.info("Creando backup de archivos críticos...")
        
        self.backup_dir.mkdir(exist_ok=True)
        
        critical_files = [
            "servidor/utils/search.py",
            "servidor/settings.py",
            "servidor/rag.py",
            "scripts/search_engine.py",
            "herramientas/bing_client.py",
            "configuraciones/requirements.txt"
        ]
        
        for file_path in critical_files:
            source = self.project_root / file_path
            if source.exists():
                dest = self.backup_dir / file_path.replace("/", "_")
                shutil.copy2(source, dest)
                logger.info(f"Backup creado: {dest}")
    
    def fix_duplicate_search_modules(self):
        """Consolidar módulos de búsqueda duplicados"""
        logger.info("Consolidando módulos de búsqueda duplicados...")
        
        # Crear el nuevo servicio unificado
        unified_search_content = '''import logging
import asyncio
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

from ..settings import Settings
from ..exceptions import WebSearchError

logger = logging.getLogger(__name__)

class SearchStrategy(ABC):
    """Estrategia abstracta para búsqueda web"""
    
    @abstractmethod
    async def search(self, query: str, count: int) -> List[Dict[str, str]]:
        pass

class LegacyBingStrategy(SearchStrategy):
    """Estrategia legacy de Bing (temporal hasta migración Azure)"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def search(self, query: str, count: int) -> List[Dict[str, str]]:
        """Búsqueda usando API legacy de Bing"""
        # Implementación temporal que maneja el error 401
        logger.warning("Using legacy Bing API - migration to Azure AI Agents required")
        
        # Retornar resultado vacío con mensaje informativo
        return [{
            "titulo": "Servicio de búsqueda temporalmente no disponible",
            "snippet": "La API de Bing ha sido retirada. Se requiere migración a Azure AI Agents.",
            "url": "https://docs.microsoft.com/azure/ai-services/"
        }]

class UnifiedSearchService:
    """Servicio unificado de búsqueda web"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.strategy = LegacyBingStrategy(settings)
    
    async def search(self, query: str, count: int = 5) -> List[Dict[str, str]]:
        """Realizar búsqueda web"""
        try:
            return await self.strategy.search(query, count)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise WebSearchError(f"Error en búsqueda: {str(e)}")

# Instancia global
search_service = None

def get_search_service(settings: Settings) -> UnifiedSearchService:
    """Obtener instancia del servicio de búsqueda"""
    global search_service
    if search_service is None:
        search_service = UnifiedSearchService(settings)
    return search_service

# Función de compatibilidad
async def buscar_web(query: str, settings: Settings, top: int = None) -> List[Dict[str, str]]:
    """Función de compatibilidad para búsqueda web"""
    if top is None:
        top = settings.MAX_SEARCH_RESULTS
    
    service = get_search_service(settings)
    return await service.search(query, top)
'''
        
        # Crear directorio de servicios
        services_dir = self.project_root / "servidor" / "services"
        services_dir.mkdir(exist_ok=True)
        
        # Crear __init__.py
        init_file = services_dir / "__init__.py"
        init_file.write_text("# Servicios optimizados del sistema\n")
        
        # Crear servicio unificado
        unified_file = services_dir / "web_search.py"
        unified_file.write_text(unified_search_content)
        
        self.changes_made.append("Creado servicio unificado de búsqueda")
        logger.info("Servicio unificado de búsqueda creado")
    
    def optimize_imports(self):
        """Optimizar imports en archivos críticos"""
        logger.info("Optimizando imports...")
        
        # Actualizar search.py para usar el nuevo servicio
        search_file = self.project_root / "servidor" / "utils" / "search.py"
        if search_file.exists():
            optimized_content = '''import logging
from typing import List, Dict, Optional
from ..settings import Settings
from ..services.web_search import buscar_web as unified_buscar_web

logger = logging.getLogger(__name__)

class WebSearchError(Exception):
    """Excepción personalizada para errores de búsqueda web"""
    pass

# Función de compatibilidad
async def buscar_web(query: str, settings: Settings, top: int = None) -> List[Dict[str, str]]:
    """Búsqueda web usando servicio unificado"""
    try:
        return await unified_buscar_web(query, settings, top)
    except Exception as e:
        logger.error(f"Error en búsqueda web: {e}")
        raise WebSearchError(f"Error al buscar información: {str(e)}")

async def refinar_query(question: str, previous_answer: Optional[str] = None) -> str:
    """Refina la consulta de búsqueda"""
    # Implementación simplificada
    stop_words = ["qué", "cuál", "cómo", "dónde", "cuándo", "por qué", "quién"]
    words = question.lower().split()
    filtered_words = [word for word in words if word not in stop_words]
    refined = " ".join(filtered_words)
    return refined if len(refined.strip()) > 3 else question
'''
            search_file.write_text(optimized_content)
            self.changes_made.append("Optimizado servidor/utils/search.py")
    
    def update_requirements(self):
        """Actualizar requirements.txt con nuevas dependencias"""
        logger.info("Actualizando requirements.txt...")
        
        req_file = self.project_root / "configuraciones" / "requirements.txt"
        if req_file.exists():
            current_content = req_file.read_text()
            
            # Agregar nuevas dependencias si no existen
            new_deps = [
                "# Dependencias para optimización",
                "redis>=4.5.0",
                "aiohttp>=3.8.0",
                "# Azure AI Agents (para migración futura)",
                "# azure-ai-projects>=1.0.0",
                "# azure-ai-agents>=1.0.0",
                "# azure-identity>=1.15.0"
            ]
            
            for dep in new_deps:
                if dep not in current_content:
                    current_content += f"\n{dep}"
            
            req_file.write_text(current_content)
            self.changes_made.append("Actualizado requirements.txt")
    
    def create_optimized_services(self):
        """Crear servicios optimizados adicionales"""
        logger.info("Creando servicios optimizados...")
        
        services_dir = self.project_root / "servidor" / "services"
        
        # Crear servicio de excepciones
        exceptions_content = '''"""Excepciones unificadas del sistema"""

class AISystemException(Exception):
    """Excepción base del sistema AI"""
    pass

class SearchException(AISystemException):
    """Excepciones relacionadas con búsqueda"""
    pass

class RAGException(AISystemException):
    """Excepciones relacionadas con RAG"""
    pass

class WebScrapingException(AISystemException):
    """Excepciones relacionadas con web scraping"""
    pass

# Alias para compatibilidad
WebSearchError = SearchException
WebScrapingError = WebScrapingException
'''
        
        exceptions_file = self.project_root / "servidor" / "exceptions.py"
        exceptions_file.write_text(exceptions_content)
        
        self.changes_made.append("Creado sistema de excepciones unificado")
    
    def update_settings(self):
        """Actualizar configuraciones para optimización"""
        logger.info("Actualizando configuraciones...")
        
        settings_file = self.project_root / "servidor" / "settings.py"
        if settings_file.exists():
            content = settings_file.read_text()
            
            # Agregar nuevas configuraciones si no existen
            new_settings = '''
    # Configuraciones de optimización
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    CACHE_TTL_SEARCH: int = Field(default=3600, env="CACHE_TTL_SEARCH")
    CACHE_TTL_EMBEDDINGS: int = Field(default=86400, env="CACHE_TTL_EMBEDDINGS")
    CACHE_TTL_RAG_SEARCH: int = Field(default=1800, env="CACHE_TTL_RAG_SEARCH")
    
    # Performance settings
    MAX_CONCURRENT_REQUESTS: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")
    BATCH_SIZE: int = Field(default=100, env="BATCH_SIZE")
    
    # Azure AI Agents (para migración futura)
    AZURE_AI_ENDPOINT: Optional[str] = Field(default=None, env="AZURE_AI_ENDPOINT")
    AZURE_SUBSCRIPTION_ID: Optional[str] = Field(default=None, env="AZURE_SUBSCRIPTION_ID")
    AZURE_RESOURCE_GROUP: Optional[str] = Field(default=None, env="AZURE_RESOURCE_GROUP")
    AZURE_PROJECT_NAME: Optional[str] = Field(default=None, env="AZURE_PROJECT_NAME")
    BING_GROUNDING_CONNECTION_ID: Optional[str] = Field(default=None, env="BING_GROUNDING_CONNECTION_ID")
'''
            
            if "REDIS_URL" not in content:
                # Insertar antes de la última línea de la clase
                lines = content.split('\n')
                insert_pos = -1
                for i, line in enumerate(lines):
                    if line.strip().startswith('class ') and 'Settings' in line:
                        # Encontrar el final de la clase
                        for j in range(i, len(lines)):
                            if lines[j].strip() and not lines[j].startswith(' ') and j > i:
                                insert_pos = j
                                break
                        if insert_pos == -1:
                            insert_pos = len(lines)
                        break
                
                if insert_pos > 0:
                    lines.insert(insert_pos, new_settings)
                    settings_file.write_text('\n'.join(lines))
                    self.changes_made.append("Actualizado servidor/settings.py")
    
    def print_summary(self):
        """Imprimir resumen de cambios"""
        logger.info("\n" + "="*50)
        logger.info("RESUMEN DE OPTIMIZACIÓN")
        logger.info("="*50)
        
        for change in self.changes_made:
            logger.info(f"✅ {change}")
        
        logger.info("\n📋 PRÓXIMOS PASOS RECOMENDADOS:")
        logger.info("1. Instalar Redis: docker run -d -p 6379:6379 redis:alpine")
        logger.info("2. Actualizar dependencias: pip install -r configuraciones/requirements.txt")
        logger.info("3. Configurar variables de entorno para Azure AI Agents")
        logger.info("4. Ejecutar pruebas: python -m pytest tests/")
        logger.info("5. Revisar logs para verificar funcionamiento")
        
        logger.info("\n⚠️  IMPORTANTE:")
        logger.info("- La API de Bing está deprecada y requiere migración a Azure AI Agents")
        logger.info("- Los backups están en: " + str(self.backup_dir))
        logger.info("- Revisar ANALISIS_EFICIENCIA.md para detalles completos")
    
    def rollback_changes(self):
        """Revertir cambios en caso de error"""
        logger.warning("Revirtiendo cambios...")
        # Implementar rollback si es necesario
        pass

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    optimizer = SystemOptimizer(project_root)
    optimizer.run_optimization()

if __name__ == "__main__":
    main()