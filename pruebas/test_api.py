from unittest.mock import MagicMock, patch
import pytest
from servidor.dependencies import get_settings


@pytest.fixture
def override_get_settings(mock_settings):
    app.dependency_overrides[get_settings] = lambda: mock_settings
    yield
    app.dependency_overrides.clear()


class TestChatEndpoint:
    def test_chat_success(self, mock_settings, test_client):
        """Test successful chat completion"""
        from servidor.main import app
        app.dependency_overrides[get_settings] = lambda: mock_settings
        
        with patch("herramientas.model_manager.ModelManager.chat_completion") as mock_chat:
            mock_chat.return_value = "Test response"
            response = test_client.post("/chat/", json={"prompt": "Hello"})
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert data["answer"] == "Test response"

    def test_chat_long_prompt(self, mock_settings, test_client):
        """Test chat with long prompt"""
        from servidor.main import app
        app.dependency_overrides[get_settings] = lambda: mock_settings
        
        long_prompt = "x" * 1001  # Exceeds MAX_PROMPT_LEN
        response = test_client.post("/chat/", json={"prompt": long_prompt})
        assert response.status_code == 422

    def test_chat_empty_prompt(self, mock_settings, test_client):
        """Test chat with empty prompt"""
        from servidor.main import app
        app.dependency_overrides[get_settings] = lambda: mock_settings
        
        response = test_client.post("/chat/", json={"prompt": ""})
        assert response.status_code == 422


class TestChatEndpointReal:
    def test_chat_real_api(self, mock_settings, test_client):
        """Test chat with real API"""
        import os
        from servidor.main import app
        app.dependency_overrides[get_settings] = lambda: mock_settings

        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("Real API key not available")

        response = test_client.post("/chat/", json={"prompt": "Hola"})
        assert response.status_code == 200
        assert "answer" in response.json()
