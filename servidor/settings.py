from typing import List
import os
from pydantic_settings import BaseSettings
from servidor.crypto import get_encryption_instance, APIKeyEncryption


class Settings(BaseSettings):
    # Claves API (pueden estar encriptadas)
    GROQ_API_KEY: str
    # OpenAI removido - solo Groq disponible
    SEARCH_API_KEY: str = ""  # Clave de Bing ya existente
    
    # Configuración de encriptación
    MASTER_PASSWORD: str = "default_admin_key_2024"
    USE_ENCRYPTED_KEYS: bool = True
    
    # Configuración de modelos competitivos
    PRIMARY_MODEL: str = "groq"  # solo groq disponible
    GROQ_MODEL: str = "deepseek-r1-distill-llama-70b"  # Modelo DeepSeek como especificado
    
    # Configuración general
    API_KEYS: list[str] = []
    MAX_PROMPT_LEN: int = 1000
    ALLOWED_ORIGINS: str = "*"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    REQUEST_TIMEOUT: int = 30
    
    # Configuraciones para búsqueda web
    SEARCH_API_KEY: str = ""
    SEARCH_ENDPOINT: str = "https://api.bing.microsoft.com/v7.0/search"
    WEB_SCRAPE_TIMEOUT: int = 10
    MAX_SEARCH_RESULTS: int = 3
    MAX_PAGE_LENGTH: int = 1000
    MAX_SEARCH_ITERATIONS: int = 2
    
    # Configuraciones RAG
    RAG_COLLECTION: str = "domain_corpus"
    RAG_SCORE_THRESHOLD: float = 0.35  # similitud mínima (cosine)
    RAG_MIN_HITS: int = 2  # nº de fragmentos que deben superar el umbral
    RAG_CHUNK_SIZE: int = 300  # tokens por fragmento
    RAG_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # Mapa de temperaturas por tipo de consulta
    @property
    def temperature_map(self) -> dict[str, float]:
        return {
            "scientific": 0.1,  # Muy baja para respuestas precisas
            "creative": 1.3,    # Alta para creatividad
            "general": 0.7,     # Moderada para uso general
            "web": 0.3,         # Baja para búsquedas web precisas
        }
    
    def get_decrypted_keys(self) -> dict[str, str]:
        """Obtiene las claves API desencriptadas si está habilitada la encriptación."""
        if not self.USE_ENCRYPTED_KEYS:
            return {
            "GROQ_API_KEY": self.GROQ_API_KEY,
            "SEARCH_API_KEY": self.SEARCH_API_KEY,
        }
        
        # Importar aquí para evitar dependencias circulares
        from servidor.crypto import get_encryption_instance
        
        encryption = get_encryption_instance()
        encrypted_keys = {
            "GROQ_API_KEY": self.GROQ_API_KEY,
            "SEARCH_API_KEY": self.SEARCH_API_KEY
        }
        
        return encryption.decrypt_multiple_keys(encrypted_keys)

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = "configuraciones/.env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
