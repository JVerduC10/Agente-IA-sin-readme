"""Configuración común para todas las pruebas."""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from servidor.dependencies import get_settings
from servidor.main import app


@pytest.fixture
def test_client():
    """Cliente de pruebas reutilizable."""
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """Configuración mock común para todas las pruebas."""
    class MockSettings:
        GROQ_API_KEY = "test_key"
        API_KEYS = []
        MAX_PROMPT_LEN = 1000
        ALLOWED_ORIGINS = "*"
        GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
        GROQ_MODEL = "deepseek-r1-distill-llama-70b"
        REQUEST_TIMEOUT = 30
        BURST_SIZE = 10
        TOKENS_DAILY_LIMIT = 200_000
        MAX_CONCURRENT_SCRAPERS = 10
        CACHE_LATENCY_THRESHOLD = 3.0
        BREAKER_FAIL_PCT = 50
        BREAKER_WINDOW = 12
        PAGERDUTY_WEBHOOK = ""
        DEFAULT_MODEL_PROVIDER = "groq"
        MAX_SEARCH_ITERATIONS = 3
        
        # Configuraciones de búsqueda web
        SEARCH_API_KEY = "test_search_key"
        SEARCH_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
        SEARCH_TIMEOUT = 10
        SEARCH_MAX_RESULTS = 5
        
        # Mapa de temperaturas
        temperature_map = {
            "scientific": 0.1,
            "creative": 1.2,
            "general": 0.7,
            "web": 0.3
        }
        
        def get_decrypted_keys(self):
            return {
                "GROQ_API_KEY": self.GROQ_API_KEY,
                "SEARCH_API_KEY": self.SEARCH_API_KEY
            }
    
    return MockSettings()


@pytest.fixture(autouse=True)
def cleanup_overrides():
    """Limpia automáticamente las dependencias sobrescritas después de cada prueba."""
    yield
    app.dependency_overrides.clear()