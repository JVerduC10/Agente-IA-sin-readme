from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_settings

client = TestClient(app)

@pytest.fixture
def mock_settings():
    class MockSettings:
        GROQ_API_KEY = "test_key"
        API_KEYS = []
        MAX_PROMPT_LEN = 1000
        ALLOWED_ORIGINS = "*"
        GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
        GROQ_MODEL = "llama3-8b-8192"
        REQUEST_TIMEOUT = 30
        BURST_SIZE = 10
        TOKENS_DAILY_LIMIT = 200_000
        MAX_CONCURRENT_SCRAPERS = 10
        CACHE_LATENCY_THRESHOLD = 3.0
        BREAKER_FAIL_PCT = 50
        BREAKER_WINDOW = 12
        PAGERDUTY_WEBHOOK = ""
        
        @property
        def allowed_origins_list(self):
            return ["*"]
    return MockSettings()

@pytest.fixture
def override_get_settings(mock_settings):
    app.dependency_overrides[get_settings] = lambda: mock_settings
    yield
    app.dependency_overrides.clear()


class TestChatEndpoint:
    @patch("scripts.groq_client.GroqClient.chat_completion")
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
    def test_chat_real_api(self, override_get_settings):
        import os
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("Real API key not available")

        response = client.post("/chat", json={"prompt": "Hola"})
        assert response.status_code == 200
        assert "answer" in response.json()
