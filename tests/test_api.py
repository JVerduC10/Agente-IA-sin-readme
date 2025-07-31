import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

from app.main import app, get_settings

client = TestClient(app)

@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    settings = MagicMock()
    settings.groq_api_key = "test_key"
    settings.max_prompt_len = 1000
    settings.allowed_origins = ["http://localhost"]
    settings.groq_base_url = "https://api.groq.com/openai/v1/chat/completions"
    return settings

@pytest.fixture
def override_get_settings(mock_settings):
    """Override get_settings dependency"""
    app.dependency_overrides[get_settings] = lambda: mock_settings
    yield
    app.dependency_overrides.clear()

class TestChatEndpoint:
    """Test cases for /chat endpoint"""
    
    @patch('app.main.requests.post')
    def test_chat_happy_path(self, mock_post, override_get_settings):
        """Test successful chat response"""
        # Mock successful Groq API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Esta es una respuesta del asistente de restaurante."
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Test request
        response = client.post(
            "/chat",
            json={"prompt": "¿Cuáles son los mejores ingredientes para pizza?"}
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["answer"] == "Esta es una respuesta del asistente de restaurante."
        
        # Verify API call was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "Bearer test_key" in call_args[1]["headers"]["Authorization"]
    
    def test_chat_long_prompt_validation(self, override_get_settings):
        """Test prompt length validation (422 error)"""
        long_prompt = "a" * 1001  # Exceeds MAX_PROMPT_LEN=1000
        
        response = client.post(
            "/chat",
            json={"prompt": long_prompt}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "Prompt exceeds maximum length" in str(data["detail"])
    
    @patch('app.main.requests.post')
    def test_chat_rate_limit_error(self, mock_post, override_get_settings):
        """Test rate limit handling (503 error)"""
        # Mock rate limit response
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_post.return_value = mock_response
        
        response = client.post(
            "/chat",
            json={"prompt": "Test prompt"}
        )
        
        assert response.status_code == 503
        data = response.json()
        assert "Rate limit exceeded" in data["detail"]
    
    @patch('app.main.requests.post')
    def test_chat_timeout_error(self, mock_post, override_get_settings):
        """Test timeout handling (503 error)"""
        # Mock timeout response
        mock_response = MagicMock()
        mock_response.status_code = 408
        mock_response.text = "Request timeout"
        mock_post.return_value = mock_response
        
        response = client.post(
            "/chat",
            json={"prompt": "Test prompt"}
        )
        
        assert response.status_code == 503
        data = response.json()
        assert "Request timeout" in data["detail"]
    
    def test_chat_invalid_json(self, override_get_settings):
        """Test invalid JSON payload"""
        response = client.post(
            "/chat",
            json={"invalid_field": "test"}
        )
        
        assert response.status_code == 422
    
    def test_chat_empty_prompt(self, override_get_settings):
        """Test empty prompt"""
        response = client.post(
            "/chat",
            json={"prompt": ""}
        )
        
        # Empty prompt should be valid (length = 0 < 1000)
        # But we need to mock the API call
        with patch('app.main.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "Por favor, proporciona una pregunta específica."
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            response = client.post(
                "/chat",
                json={"prompt": ""}
            )
            
            assert response.status_code == 200

@pytest.mark.slow
class TestChatEndpointReal:
    """Real API tests (marked as slow)"""
    
    def test_chat_real_api(self, override_get_settings):
        """Test with real Groq API (requires valid API key)"""
        # This test should only run when explicitly requested
        # and when a real API key is available
        import os
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("Real API key not available")
        
        response = client.post(
            "/chat",
            json={"prompt": "Hola"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 0