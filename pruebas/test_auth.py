import pytest
from unittest.mock import patch
from servidor.dependencies import get_settings
from servidor.settings import Settings


def test_missing_api_key(test_client):
    """Test that requests without API key are rejected."""
    from servidor.main import app
    app.dependency_overrides[get_settings] = lambda: Settings(
        GROQ_API_KEY="test-key",
        API_KEYS=["valid-key"]
    )
    
    response = test_client.post("/chat/", json={"prompt": "test"})
    assert response.status_code == 401


@patch("herramientas.groq_client.GroqClient.chat_completion")
def test_valid_api_key(mock_chat_completion, test_client):
    """Test that requests with valid API key are accepted."""
    mock_chat_completion.return_value = "Test response"
    
    from servidor.main import app
    app.dependency_overrides[get_settings] = lambda: Settings(
        GROQ_API_KEY="test-key",
        API_KEYS=["valid-key"]
    )
    
    headers = {"X-API-Key": "valid-key"}
    response = test_client.post("/chat", json={"prompt": "test"}, headers=headers)
    assert response.status_code == 200


@patch("herramientas.groq_client.GroqClient.chat_completion")
def test_no_api_keys_configured(mock_chat_completion, test_client):
    """Test that when no API keys are configured, requests are allowed."""
    mock_chat_completion.return_value = "Test response"
    
    from servidor.main import app
    app.dependency_overrides[get_settings] = lambda: Settings(
        GROQ_API_KEY="test-key",
        API_KEYS=[]
    )
    
    response = test_client.post("/chat/", json={"prompt": "test"})
    assert response.status_code == 200
