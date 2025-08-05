from pydantic_settings import BaseSettings
from typing import Optional
import os

class RAGConfig(BaseSettings):
    """Configuración específica para el sistema RAG"""
    
    # Configuración de la colección
    collection_name: str = "domain_corpus"
    
    # Configuración de similitud y filtrado
    score_threshold: float = 0.35  # similitud mínima (cosine)
    min_hits: int = 2  # nº de fragmentos que deben superar el umbral
    
    # Configuración de chunking
    chunk_size: int = 300  # tokens por fragmento
    chunk_overlap: int = 50  # solapamiento entre fragmentos
    
    # Configuración de embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384  # dimensión del modelo por defecto
    
    # Configuración de ChromaDB
    chroma_persist_dir: str = "./chroma_db"
    chroma_host: Optional[str] = None  # Para modo cliente
    chroma_port: Optional[int] = None  # Para modo cliente
    
    # Configuración de búsqueda
    max_results: int = 5
    search_timeout: int = 10
    
    # Configuración de cache
    enable_cache: bool = True
    cache_ttl: int = 3600  # TTL en segundos
    max_cache_size: int = 1000  # Máximo número de entradas en cache
    
    class Config:
        env_prefix = "RAG_"
        case_sensitive = False
    
    @property
    def chroma_settings(self) -> dict:
        """Configuración para ChromaDB"""
        settings = {
            "anonymized_telemetry": False,
            "allow_reset": True
        }
        
        if self.chroma_host and self.chroma_port:
            # Modo cliente
            settings.update({
                "chroma_server_host": self.chroma_host,
                "chroma_server_http_port": self.chroma_port
            })
        
        return settings
    
    @property
    def is_client_mode(self) -> bool:
        """Indica si ChromaDB debe ejecutarse en modo cliente"""
        return bool(self.chroma_host and self.chroma_port)
    
    def validate_configuration(self) -> bool:
        """Valida la configuración RAG"""
        # Validar que el directorio de persistencia existe o se puede crear
        if not self.is_client_mode:
            try:
                os.makedirs(self.chroma_persist_dir, exist_ok=True)
                return True
            except (OSError, PermissionError):
                return False
        
        return True
    
    def get_collection_metadata(self) -> dict:
        """Metadatos para la colección ChromaDB"""
        return {
            "hnsw:space": "cosine",
            "description": f"Colección RAG con modelo {self.embedding_model}",
            "embedding_model": self.embedding_model,
            "chunk_size": self.chunk_size,
            "created_by": "servidor_ai"
        }