from fastapi.testclient import TestClient

from servidor.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_health_method_not_allowed(self):
        response = client.post("/health")
        assert response.status_code == 405
