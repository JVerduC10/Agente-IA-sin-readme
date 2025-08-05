"""Configuración unificada del sistema - FUSIÓN de settings.py + base.py"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic_settings import BaseSettings

from .app import AppConfig
from .rag import RAGConfig
from .security import SecurityConfig


class Settings(BaseSettings):
    """Configuración unificada del sistema - FUSIÓN de settings.py + base.py"""

    # ===== CONFIGURACIONES GROQ (FUSIONADAS) =====
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    # ===== CONFIGURACIONES DE TEMPERATURA =====
    DEFAULT_TEMPERATURE: float = 0.7
    MIN_TEMPERATURE: float = 0.0
    MAX_TEMPERATURE: float = 2.0

    # ===== CONFIGURACIONES DE TOKENS =====
    DEFAULT_MAX_TOKENS: Optional[int] = 1024

    # ===== CONFIGURACIONES DEL SERVIDOR =====
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 8000
    DEBUG: bool = False

    # ===== CONFIGURACIONES DE API =====
    API_KEYS: list = []

    # ===== CONFIGURACIONES MODULARES =====
    rag: RAGConfig = RAGConfig()
    security: SecurityConfig = SecurityConfig()
    app: AppConfig = AppConfig()

    class Config:
        env_file = (
            Path(__file__).parent.parent.parent / ".env"
        )  # Apunta a raíz del proyecto
        env_file_encoding = "utf-8"
        case_sensitive = True  # Mantener case_sensitive=True para compatibilidad
        extra = "ignore"
        env_nested_delimiter = "__"

    @property
    def temperature_map(self) -> Dict[str, float]:
        """Mapa de temperaturas por tipo de consulta"""
        return {
            "scientific": 0.1,  # Muy baja para respuestas precisas
            "creative": 1.3,  # Alta para creatividad
            "general": 0.7,  # Moderada para uso general
            "web": 0.3,  # Baja para búsquedas web precisas
        }

    @property
    def allowed_origins_list(self) -> List[str]:
        """Lista de orígenes permitidos para CORS"""
        return [origin.strip() for origin in self.app.allowed_origins.split(",")]

    def validate_settings(self) -> dict:
        """Valida las configuraciones críticas del sistema.

        Returns:
            Diccionario con el estado de validación
        """
        validation = {
            "groq_api_key": bool(self.GROQ_API_KEY),
            "groq_model": bool(self.GROQ_MODEL),
            "temperature_range": self.MIN_TEMPERATURE
            <= self.DEFAULT_TEMPERATURE
            <= self.MAX_TEMPERATURE,
            "server_config": bool(self.SERVER_HOST and self.SERVER_PORT),
        }

        validation["all_valid"] = all(validation.values())

        return validation


@lru_cache()
def get_settings() -> Settings:
    """Obtiene la instancia de configuración (cached)"""
    return Settings()


# ===== VARIABLES DE COMPATIBILIDAD =====
# Mantener para compatibilidad con código existente
settings = get_settings()
GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_MODEL = settings.GROQ_MODEL
GROQ_BASE_URL = settings.GROQ_BASE_URL
DEFAULT_TEMPERATURE = settings.DEFAULT_TEMPERATURE
MIN_TEMPERATURE = settings.MIN_TEMPERATURE
MAX_TEMPERATURE = settings.MAX_TEMPERATURE
DEFAULT_MAX_TOKENS = settings.DEFAULT_MAX_TOKENS
SERVER_HOST = settings.SERVER_HOST
SERVER_PORT = settings.SERVER_PORT
DEBUG = settings.DEBUG
API_KEYS = settings.API_KEYS

# Configuraciones de CORS (fusionadas)
ALLOWED_ORIGINS: list = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Configuraciones para desarrollo
if settings.DEBUG:
    print(f"Configuraciones cargadas:")
    print(f"- GROQ_API_KEY: {'✓' if settings.GROQ_API_KEY else '✗'}")
    print(f"- GROQ_MODEL: {settings.GROQ_MODEL}")
    print(f"- DEFAULT_TEMPERATURE: {settings.DEFAULT_TEMPERATURE}")
    print(f"- SERVER: {settings.SERVER_HOST}:{settings.SERVER_PORT}")