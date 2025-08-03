from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from seguridad.dependencies import get_settings
from servidor.main import app

client = TestClient(app)


@pytest.fixture
def mock_settings():
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
        
        # Configuraciones de búsqueda web
        SEARCH_API_KEY = "test_search_key"
        SEARCH_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
        WEB_SCRAPE_TIMEOUT = 10
        MAX_SEARCH_RESULTS = 5
        MAX_PAGE_LENGTH = 8000
        MAX_SEARCH_ITERATIONS = 3

        @property
        def api_keys_list(self):
            return []
            
        @property
        def allowed_origins_list(self):
            return ["*"]
            
        @property
        def temperature_map(self):
            return {
                "scientific": 0.1,
                "creative": 1.3,
                "general": 0.7,
                "web": 0.7
            }
            
        def get_decrypted_keys(self):
            """Mock method for decrypted keys."""
            return {
                "GROQ_API_KEY": self.GROQ_API_KEY,
                "SEARCH_API_KEY": self.SEARCH_API_KEY
            }

    return MockSettings()


@pytest.fixture
def override_get_settings(mock_settings):
    app.dependency_overrides[get_settings] = lambda: mock_settings
    yield
    app.dependency_overrides.clear()


class TestChatEndpoint:
    @patch("herramientas.groq_client.GroqClient.chat_completion")
    def test_chat_success(self, mock_chat_completion, override_get_settings):
        mock_chat_completion.return_value = "Test response"
        response = client.post("/chat", json={"prompt": "test"})
        assert response.status_code == 200
        assert "answer" in response.json()

    def test_chat_long_prompt(self, override_get_settings):
        long_prompt = "a" * 1001
        response = client.post("/chat", json={"prompt": long_prompt})
        assert response.status_code == 422

    def test_chat_empty_prompt(self, override_get_settings):
        response = client.post("/chat", json={"prompt": ""})
        assert response.status_code == 422


class TestChatEndpointReal:
    def test_chat_real_api_with_valid_key(self, override_get_settings):
        """Test chat endpoint with real API when valid key is available"""
        from seguridad.dependencies import get_settings
        
        settings = get_settings()
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "test_key":
            pytest.skip("🔑 Real API key not available - using mock key")

        response = client.post("/chat", json={"prompt": "Hola"})
        assert response.status_code == 200
        assert "answer" in response.json()
from servidor.main import app
