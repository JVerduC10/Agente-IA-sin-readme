import sys

# Compatibility for Python 3.8 - MUST be before any other imports
if sys.version_info < (3, 9):
    from typing_extensions import Dict, List
else:
    from typing import Dict, List

from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi.testclient import TestClient

from app.main import app, get_settings

client = TestClient(app)


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    settings = MagicMock()
    settings.GROQ_API_KEY = "test_key"
    settings.MAX_PROMPT_LEN = 1000
    settings.ALLOWED_ORIGINS = ["http://localhost"]
    settings.GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
    settings.GROQ_MODEL = "llama3-8b-8192"
    settings.REQUEST_TIMEOUT = 30
    return settings


@pytest.fixture
def override_get_settings(mock_settings):
    """Override get_settings dependency"""
    app.dependency_overrides[get_settings] = lambda: mock_settings
    yield
    app.dependency_overrides.clear()


class TestRateLimitHandling:
    """Test cases for rate limit error handling"""

    @patch("app.main.requests.post")
    def test_rate_limit_error_returns_503(self, mock_post, override_get_settings):
        """Test that rate limit error returns 429 Rate Limit Exceeded"""
        # Mock rate limit response from Groq API
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response

        # Make request to /chat endpoint
        response = client.post(
            "/chat", json={"prompt": "Test prompt for rate limiting"}
        )

        # Assertions
        assert response.status_code == 429
        data = response.json()
        assert "detail" in data
        assert "Rate limit exceeded" in data["detail"]

    @patch("app.main.requests.post")
    def test_timeout_error_returns_503(self, mock_post, override_get_settings):
        """Test that timeout errors return 503 Service Unavailable"""
        # Mock timeout exception
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        # Make request to /chat endpoint
        response = client.post("/chat", json={"prompt": "Test prompt for timeout"})

        # Assertions
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "Request timeout" in data["detail"]

    @patch("app.main.requests.post")
    def test_connection_error_returns_503(self, mock_post, override_get_settings):
        """Test that connection errors return 503 Service Unavailable"""
        # Mock connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        # Make request to /chat endpoint
        response = client.post(
            "/chat", json={"prompt": "Test prompt for connection error"}
        )

        # Assertions
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "Service temporarily unavailable" in data["detail"]

    @patch("app.main.requests.post")
    def test_api_error_codes_return_503(self, mock_post, override_get_settings):
        """Test that various API error codes return 502"""
        error_codes = [500, 502, 503, 504]

        for error_code in error_codes:
            # Mock API error response
            mock_response = MagicMock()
            mock_response.status_code = error_code
            mock_post.return_value = mock_response

            # Make request to /chat endpoint
            response = client.post(
                "/chat", json={"prompt": f"Test prompt for error {error_code}"}
            )

            # Assertions
            assert response.status_code == 502
            data = response.json()
            assert "detail" in data
            assert "AI service error" in data["detail"]

    @patch("app.main.requests.post")
    def test_unexpected_exception_returns_500(self, mock_post, override_get_settings):
        """Test that unexpected exceptions return 500 Internal Server Error"""
        # Mock unexpected exception
        mock_post.side_effect = Exception("Unexpected error")

        # Make request to /chat endpoint
        response = client.post(
            "/chat", json={"prompt": "Test prompt for unexpected error"}
        )

        # Assertions
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Internal server error" in data["detail"]

    def test_monkeypatch_example(self, monkeypatch, override_get_settings):
        """Example using monkeypatch instead of @patch decorator"""

        # Create a mock function that raises RateLimitError
        def mock_requests_post(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.status_code = 429
            return mock_response

        # Use monkeypatch to replace requests.post
        monkeypatch.setattr("app.main.requests.post", mock_requests_post)

        # Make request to /chat endpoint
        response = client.post("/chat", json={"prompt": "Test prompt with monkeypatch"})

        # Assertions
        assert response.status_code == 429
        data = response.json()
        assert "Rate limit exceeded" in data["detail"]
