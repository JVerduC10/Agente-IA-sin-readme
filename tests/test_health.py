import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

class TestHealthEndpoint:
    """Test cases for /health endpoint"""
    
    def test_health_check_returns_200(self):
        """Test that /health endpoint returns 200 OK"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data == {"status": "ok"}
    
    def test_health_check_response_model(self):
        """Test that /health endpoint returns correct response model"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "status" in data
        assert isinstance(data["status"], str)
        assert data["status"] == "ok"
    
    def test_health_check_method_not_allowed(self):
        """Test that /health endpoint only accepts GET requests"""
        # Test POST method (should not be allowed)
        response = client.post("/health")
        assert response.status_code == 405  # Method Not Allowed
        
        # Test PUT method (should not be allowed)
        response = client.put("/health")
        assert response.status_code == 405  # Method Not Allowed
        
        # Test DELETE method (should not be allowed)
        response = client.delete("/health")
        assert response.status_code == 405  # Method Not Allowed