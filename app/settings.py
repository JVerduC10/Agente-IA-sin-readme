from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GROQ_API_KEY: str
    API_KEYS: list[str] = []
    MAX_PROMPT_LEN: int = 1000
    ALLOWED_ORIGINS: str = "*"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL: str = "llama3-8b-8192"
    REQUEST_TIMEOUT: int = 30

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
