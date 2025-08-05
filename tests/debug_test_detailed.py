import requests
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from servidor.main import app
from servidor.config.settings import get_settings

# Mock settings
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
    
    def validate_settings(self):
        """Mock validate_settings method"""
        return {
            "groq_api_key": True,
            "model": True,
            "temperature": True,
            "server": True
        }

mock_settings = MockSettings()

# Override settings
app.dependency_overrides[get_settings] = lambda: mock_settings

# Create test client
client = TestClient(app)

# Test with mock
with patch("servidor.clients.groq.manager.ModelManager.chat_completion") as mock_chat:
    # Mock the expected OpenAI-style response structure
    mock_chat.return_value = {
        "choices": [{
            "message": {
                "content": "Test response"
            }
        }]
    }
    
    print("Testing with mocked ModelManager...")
    response = client.post("/api/chat/completion", json={"messages": [{"role": "user", "content": "Hello"}]})
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Answer: {data.get('answer', 'No answer field')}")
    else:
        print("Test failed!")

# Clean up
app.dependency_overrides.clear()