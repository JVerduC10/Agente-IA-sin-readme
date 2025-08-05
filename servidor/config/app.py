from pydantic_settings import BaseSettings
from typing import Optional
import os

class AppConfig(BaseSettings):
    """Configuración general de la aplicación"""
    
    # Información básica de la aplicación
    app_name: str = "Jarvis Analyst API"
    app_version: str = "1.0.0"
    app_description: str = "API de análisis inteligente - Preparado para nuevos proveedores"
    
    # Configuración del servidor
    host: str = "0.0.0.0"
    port: int = 8003
    debug: bool = False
    reload: bool = False
    
    # Configuración de CORS
    allowed_origins: str = "*"
    
    # Configuración de logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    
    # Configuración de archivos estáticos
    static_files_enabled: bool = True
    static_files_directory: str = "archivos_estaticos"
    static_files_path: str = "/static"
    
    # Configuración de web scraping
    web_scrape_timeout: int = 10
    max_search_results: int = 5
    max_page_length: int = 1000
    max_search_iterations: int = 2
    
    # Configuración de cache
    cache_enabled: bool = True
    cache_ttl: int = 3600  # TTL en segundos
    cache_max_size: int = 1000
    
    # Configuración de métricas
    metrics_enabled: bool = True
    metrics_endpoint: str = "/metrics"
    
    # Configuración de health checks
    health_check_enabled: bool = True
    health_check_interval: int = 30  # segundos
    
    # Configuración de documentación
    docs_enabled: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    class Config:
        env_prefix = "APP_"
        case_sensitive = False
    
    @property
    def is_development(self) -> bool:
        """Indica si la aplicación está en modo desarrollo"""
        return self.debug or self.reload
    
    @property
    def log_config(self) -> dict:
        """Configuración de logging"""
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.log_format,
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": self.log_level,
                "handlers": ["default"],
            },
        }
        
        # Añadir handler de archivo si está configurado
        if self.log_file:
            config["handlers"]["file"] = {
                "formatter": "detailed",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": self.log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            }
            config["root"]["handlers"].append("file")
        
        return config
    
    def get_static_files_path(self) -> str:
        """Obtiene la ruta completa a los archivos estáticos"""
        if os.path.isabs(self.static_files_directory):
            return self.static_files_directory
        
        # Ruta relativa desde el directorio del proyecto
        return os.path.join(os.getcwd(), self.static_files_directory)
    
    def validate_static_files(self) -> bool:
        """Valida que el directorio de archivos estáticos existe"""
        if not self.static_files_enabled:
            return True
        
        static_path = self.get_static_files_path()
        return os.path.exists(static_path) and os.path.isdir(static_path)
    
    @property
    def server_config(self) -> dict:
        """Configuración para Uvicorn"""
        return {
            "host": self.host,
            "port": self.port,
            "reload": self.reload,
            "log_level": self.log_level.lower(),
            "access_log": True,
        }