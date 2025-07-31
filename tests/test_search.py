import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@patch("app.main.search_web", new_callable=AsyncMock)
@patch("app.main.scrape_pct", new_callable=AsyncMock)
def test_porcentaje_mujeres(mock_scrape, mock_search):
    mock_search.return_value = [
        {"url": "https://example.com/a", "title": "A", "snippet": ""},
        {"url": "https://example.com/b", "title": "B", "snippet": ""},
    ]
    mock_scrape.side_effect = [[40.0], [42.0]]
    client = TestClient(app)
    r = client.post("/chat", json={"prompt": "% de mujeres que votó X"})
    assert r.status_code == 200
    assert "41.0%" in r.json()["answer"]


@patch("app.main.search_web", new_callable=AsyncMock)
@patch("app.main.scrape_pct", new_callable=AsyncMock)
def test_porcentaje_hombres(mock_scrape, mock_search):
    mock_search.return_value = [
        {"url": "https://example.com/c", "title": "C", "snippet": ""},
        {"url": "https://example.com/d", "title": "D", "snippet": ""},
    ]
    mock_scrape.side_effect = [[30.0], [35.0]]
    client = TestClient(app)
    r = client.post("/chat", json={"prompt": "porcentaje de hombres en el sector"})
    assert r.status_code == 200
    assert "32.5%" in r.json()["answer"]


@patch("app.main.search_web", new_callable=AsyncMock)
@patch("app.main.scrape_pct", new_callable=AsyncMock)
def test_datos_insuficientes(mock_scrape, mock_search):
    mock_search.return_value = [
        {"url": "https://example.com/e", "title": "E", "snippet": ""},
    ]
    mock_scrape.side_effect = [[]]
    client = TestClient(app)
    r = client.post("/chat", json={"prompt": "% de mujeres en política"})
    assert r.status_code == 404
    assert "Datos insuficientes" in r.json()["detail"]


def test_consulta_normal():
    """Test que consultas normales siguen el flujo LLM habitual"""
    client = TestClient(app)
    r = client.post("/chat", json={"prompt": "¿Cómo hacer una pizza?"})
    # Debería seguir el flujo normal (aunque falle por API key de test)
    assert r.status_code in [200, 503]  # 503 por API key de test
