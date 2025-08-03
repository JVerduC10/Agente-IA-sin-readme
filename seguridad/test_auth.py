import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from seguridad.dependencies import get_settings
from servidor.main import app
from servidor.settings import Settings


def test_missing_api_key():
    """Test that requests without API key are rejected."""
    client = TestClient(app)
    app.dependency_overrides[get_settings] = lambda: Settings(
        GROQ_API_KEY="test-key",
        API_KEYS="valid-key"
    )
    
    response = client.post("/chat", json={"prompt": "test"})
    assert response.status_code == 401
    
    # Clean up
    app.dependency_overrides.clear()


@patch("herramientas.groq_client.GroqClient.chat_completion")
def test_valid_api_key(mock_chat_completion):
    """Test that requests with valid API key are accepted."""
    mock_chat_completion.return_value = "Test response"
    
    client = TestClient(app)
    app.dependency_overrides[get_settings] = lambda: Settings(
        GROQ_API_KEY="test-key",
        API_KEYS="valid-key"
    )
    
    headers = {"X-API-Key": "valid-key"}
    response = client.post("/chat", json={"prompt": "test"}, headers=headers)
    assert response.status_code == 200
    
    # Clean up
    app.dependency_overrides.clear()


@patch("herramientas.groq_client.GroqClient.chat_completion")
def test_no_api_keys_configured(mock_chat_completion):
    """Test that when no API keys are configured, requests are allowed."""
    mock_chat_completion.return_value = "Test response"
    
    client = TestClient(app)
    app.dependency_overrides[get_settings] = lambda: Settings(
        GROQ_API_KEY="test-key",
        API_KEYS=""
    )
    
    response = client.post("/chat", json={"prompt": "test"})
    assert response.status_code == 200
    
    # Clean up
    app.dependency_overrides.clear()
