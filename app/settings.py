from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GROQ_API_KEY: str
    API_KEYS: list[str] = []
    MAX_PROMPT_LEN: int = 1000
    ALLOWED_ORIGINS: str = "*"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL: str = "compound-beta"  # Modelo que incluye DeepSeek
    REQUEST_TIMEOUT: int = 30
    
    # Configuraciones RAG
    RAG_COLLECTION: str = "domain_corpus"
    RAG_SCORE_THRESHOLD: float = 0.35  # similitud mínima (cosine)
    RAG_MIN_HITS: int = 2  # nº de fragmentos que deben superar el umbral
    RAG_CHUNK_SIZE: int = 300  # tokens por fragmento
    RAG_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
