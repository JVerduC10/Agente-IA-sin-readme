import pytest
from unittest.mock import patch
from servidor.config.settings import get_settings, Settings
from servidor.auth.handlers import get_app_settings


@patch("servidor.routers.chat.model_manager.chat_completion")
def test_missing_api_key(mock_chat_completion, test_client):
    """Test that requests without API key are rejected."""
    mock_chat_completion.return_value = {"choices": [{"message": {"content": "Test response"}}], "model": "test-model", "usage": {"total_tokens": 10}}
    
    from servidor.main import app
    app.dependency_overrides[get_app_settings] = lambda: Settings(
        GROQ_API_KEY="test-key",
        API_KEYS=["valid-key"]
    )
    
    response = test_client.post("/api/chat/completion", json={"messages": [{"role": "user", "content": "test"}]})
    assert response.status_code == 401


@patch("servidor.routers.chat.model_manager.chat_completion")
def test_valid_api_key(mock_chat_completion, test_client):
    """Test that requests with valid API key are accepted."""
    mock_chat_completion.return_value = {"choices": [{"message": {"content": "Test response"}}], "model": "test-model", "usage": {"total_tokens": 10}}
    
    from servidor.main import app
    app.dependency_overrides[get_settings] = lambda: Settings(
        GROQ_API_KEY="test-key",
        API_KEYS=["valid-key"]
    )
    
    headers = {"X-API-Key": "valid-key"}
    response = test_client.post("/api/chat/completion", json={"messages": [{"role": "user", "content": "test"}]}, headers=headers)
    assert response.status_code == 200


@patch("servidor.routers.chat.model_manager.chat_completion")
def test_no_api_keys_configured(mock_chat_completion, test_client):
    """Test that when no API keys are configured, requests are allowed."""
    mock_chat_completion.return_value = {"choices": [{"message": {"content": "Test response"}}], "model": "test-model", "usage": {"total_tokens": 10}}
    
    from servidor.main import app
    app.dependency_overrides[get_app_settings] = lambda: Settings(
        GROQ_API_KEY="test-key",
        API_KEYS=[]
    )
    
    response = test_client.post("/api/chat/completion", json={"messages": [{"role": "user", "content": "test"}]})
    assert response.status_code == 200
