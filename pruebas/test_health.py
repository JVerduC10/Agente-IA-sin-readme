import pytest
from fastapi.testclient import TestClient

from servidor.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test cases for the health endpoint."""

    def test_health_endpoint_returns_200(self):
        """Test that the health endpoint returns a 200 status code."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_json(self):
        """Test that the health endpoint returns JSON."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_health_endpoint_returns_status_ok(self):
        """Test that the health endpoint returns status 'ok'."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_endpoint_returns_timestamp(self):
        """Test that the health endpoint returns a timestamp."""
        response = client.get("/health")
        data = response.json()
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)
