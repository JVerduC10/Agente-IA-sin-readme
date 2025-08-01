from fastapi.testclient import TestClient

from app.dependencies import get_settings
from app.main import app
from app.settings import Settings


def test_missing_api_key():
    client = TestClient(app)
    app.dependency_overrides[get_settings] = lambda: Settings(
        GROQ_API_KEY="test_key", API_KEYS=["valid_key"]
    )

    try:
        response = client.post("/chat", json={"prompt": "test"})
        assert response.status_code == 401
    finally:
        app.dependency_overrides = {}


def test_valid_api_key():
    client = TestClient(app)
    app.dependency_overrides[get_settings] = lambda: Settings(
        GROQ_API_KEY="test_key", API_KEYS=["valid_key"]
    )

    try:
        response = client.post(
            "/chat", json={"prompt": "test"}, headers={"X-API-Key": "valid_key"}
        )
        assert response.status_code != 401
    finally:
        app.dependency_overrides = {}


def test_no_api_keys_configured():
    client = TestClient(app)
    app.dependency_overrides[get_settings] = lambda: Settings(
        GROQ_API_KEY="test_key", API_KEYS=[]
    )

    try:
        response = client.post("/chat", json={"prompt": "test"})
        assert response.status_code != 401
    finally:
        app.dependency_overrides = {}
