from unittest.mock import MagicMock, patch
import pytest
from servidor.config.settings import get_settings
from servidor.main import app


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
        
        with patch("servidor.clients.groq.manager.ModelManager.chat_completion") as mock_chat:
            # Mock the expected OpenAI-style response structure
            mock_chat.return_value = {
                "choices": [{
                    "message": {
                        "content": "Test response"
                    }
                }]
            }
            response = test_client.post("/api/chat/completion", json={"messages": [{"role": "user", "content": "Hello"}]})
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert data["answer"] == "Test response"

    def test_chat_long_prompt(self, mock_settings, test_client):
        """Test chat with long prompt"""
        from servidor.main import app
        app.dependency_overrides[get_settings] = lambda: mock_settings
        
        long_prompt = "x" * 10001  # Exceeds reasonable limit
        response = test_client.post("/api/chat/completion", json={"messages": [{"role": "user", "content": long_prompt}]})
        assert response.status_code == 422

    def test_chat_empty_prompt(self, mock_settings, test_client):
        """Test chat with empty prompt"""
        from servidor.main import app
        app.dependency_overrides[get_settings] = lambda: mock_settings
        
        response = test_client.post("/api/chat/completion", json={"messages": [{"role": "user", "content": ""}]})
        assert response.status_code == 422


class TestChatEndpointReal:
    def test_chat_real_api(self, mock_settings, test_client):
        """Test chat with real API"""
        import os
        from servidor.main import app
        app.dependency_overrides[get_settings] = lambda: mock_settings

        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("Real API key not available")

        response = test_client.post("/api/chat/completion", json={"messages": [{"role": "user", "content": "Hola"}]})
        assert response.status_code == 200
        assert "answer" in response.json()
