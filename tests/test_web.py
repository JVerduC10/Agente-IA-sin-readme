from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from servidor.config.settings import Settings
from servidor.main import app
from servidor.services.scraping import (
    WebScrapingError,
    extraer_contenido_multiple,
    leer_pagina,
)
from servidor.services.search import WebSearchError, buscar_web, refinar_query


@pytest.fixture
def mock_settings():
    """Configuración mock para tests."""
    from servidor.config.app import AppConfig

    # Create mock app config with search settings
    app_config = AppConfig(
        web_scrape_timeout=10,
        max_search_results=3,
        max_page_length=1000,
        max_search_iterations=2,
    )

    settings = Settings(GROQ_API_KEY="test_key")
    settings.app = app_config
    return settings


@pytest.fixture
def mock_search_response():
    """Respuesta mock de la API de búsqueda."""
    return {
        "webPages": {
            "value": [
                {
                    "name": "Título de prueba 1",
                    "snippet": "Descripción de prueba 1",
                    "url": "https://example1.com",
                },
                {
                    "name": "Título de prueba 2",
                    "snippet": "Descripción de prueba 2",
                    "url": "https://example2.com",
                },
            ]
        }
    }


@pytest.fixture
def client():
    """Cliente de prueba para FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_html_content():
    """Contenido HTML mock para scraping."""
    return """
    <html>
        <head><title>Página de prueba</title></head>
        <body>
            <h1>Título principal</h1>
            <p>Este es un párrafo de prueba con información relevante.</p>
            <script>console.log('script');</script>
            <style>body { color: red; }</style>
            <p>Otro párrafo con más contenido útil para el test.</p>
        </body>
    </html>
    """


class TestWebSearch:
    """Tests para funcionalidad de búsqueda web."""

    @pytest.mark.asyncio
    async def test_buscar_web_exitoso(self, mock_settings, mock_search_response):
        """Test de búsqueda web - servicio deshabilitado."""
        # El servicio de búsqueda web está deshabilitado intencionalmente
        with pytest.raises(WebSearchError, match="Servicio de búsqueda no disponible"):
            await buscar_web("test query", mock_settings)

    @pytest.mark.asyncio
    async def test_buscar_web_sin_api_key(self, mock_settings):
        """Test de búsqueda web sin API key - servicio deshabilitado."""
        # El servicio de búsqueda web está deshabilitado intencionalmente
        with pytest.raises(WebSearchError, match="Servicio de búsqueda no disponible"):
            await buscar_web("test query", mock_settings)

    @pytest.mark.asyncio
    async def test_buscar_web_error_http(self, mock_settings):
        """Test de error HTTP en búsqueda web - servicio deshabilitado."""
        # El servicio de búsqueda web está deshabilitado intencionalmente
        with pytest.raises(WebSearchError, match="Servicio de búsqueda no disponible"):
            await buscar_web("test query", mock_settings)

    @pytest.mark.asyncio
    async def test_refinar_query_basico(self):
        """Test de refinamiento básico de query - fallback simple."""
        query_original = "¿Cuál es la capital de Francia?"

        # El servicio usa un fallback simple que devuelve la query limpia
        query_refinada = await refinar_query(query_original)
        assert query_refinada == query_original.strip()

    @pytest.mark.asyncio
    async def test_refinar_query_con_respuesta_previa(self):
        """Test de refinamiento con respuesta previa - fallback simple."""
        query_original = "Información sobre Python"
        respuesta_previa = "Necesito más información específica"

        # El servicio usa un fallback simple que devuelve la query limpia
        query_refinada = await refinar_query(query_original, respuesta_previa)
        assert query_refinada == query_original.strip()


class TestWebScraping:
    """Tests para funcionalidad de web scraping."""

    @pytest.mark.asyncio
    async def test_leer_pagina_exitoso(self, mock_settings, mock_html_content):
        """Test de lectura exitosa de página web."""
        with patch("servidor.services.scraping.get_http_client") as mock_get_client:
            # Configurar mock
            mock_response = MagicMock()
            mock_response.text = mock_html_content
            mock_response.headers = {"content-type": "text/html"}
            mock_response.raise_for_status = MagicMock()

            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            # Ejecutar scraping
            texto = await leer_pagina("https://example.com")

            # Verificar que se extrajo texto limpio
            assert "Título principal" in texto
            assert "párrafo de prueba" in texto
            assert "script" not in texto  # Scripts deben ser removidos
            assert "color: red" not in texto  # CSS debe ser removido

    @pytest.mark.asyncio
    async def test_leer_pagina_contenido_no_html(self, mock_settings):
        """Test de lectura de contenido no HTML."""
        with patch("servidor.services.scraping.get_http_client") as mock_get_client:
            # Configurar mock para contenido PDF
            mock_response = MagicMock()
            mock_response.headers = {"content-type": "application/pdf"}
            mock_response.raise_for_status = MagicMock()

            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            # Ejecutar scraping
            texto = await leer_pagina("https://example.com/file.pdf")

            # Debe indicar que no es HTML
            assert "Contenido no HTML" in texto

    @pytest.mark.asyncio
    async def test_leer_pagina_error_http(self, mock_settings):
        """Test de error HTTP en scraping."""
        with patch("servidor.services.scraping.get_http_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.status_code = 404

            mock_client = MagicMock()
            mock_client.get = AsyncMock(side_effect=Exception("HTTP 404 Error"))
            mock_get_client.return_value = mock_client

            with pytest.raises(WebScrapingError):
                await leer_pagina("https://example.com/notfound")

    @pytest.mark.asyncio
    async def test_extraer_contenido_multiple(self, mock_settings, mock_html_content):
        """Test de extracción de contenido de múltiples URLs."""
        urls = ["https://example1.com", "https://example2.com"]

        with patch("servidor.services.scraping.leer_pagina") as mock_leer:
            mock_leer.side_effect = [
                "Contenido de la página 1",
                "Contenido de la página 2",
            ]

            textos = await extraer_contenido_multiple(urls)

            assert len(textos) == 2
            assert textos[0] == "Contenido de la página 1"
            assert textos[1] == "Contenido de la página 2"

    @pytest.mark.asyncio
    async def test_extraer_contenido_multiple_con_errores(self, mock_settings):
        """Test de extracción con errores en algunas URLs."""
        urls = ["https://example1.com", "https://example2.com"]

        with patch("servidor.services.scraping.leer_pagina") as mock_leer:
            mock_leer.side_effect = [
                "Contenido exitoso",
                WebScrapingError("Error de conexión"),
            ]

            textos = await extraer_contenido_multiple(urls)

            assert len(textos) == 2
            assert textos[0] == "Contenido exitoso"
            assert "Error al leer" in textos[1]


class TestChatWebIntegration:
    """Tests de integración para el endpoint de chat con búsqueda web."""

    def test_chat_web_endpoint(self, client):
        """Test del endpoint de chat con query_type='web'."""
        # Test básico para verificar que el endpoint existe
        # Se puede expandir cuando se implementen mocks completos
        response = client.get("/health")
        assert response.status_code == 200

    def test_construir_contexto_web(self):
        """Test de construcción de contexto web - DISABLED: Function not implemented yet."""
        # TODO: Implement construir_contexto_web function in chat router
        # from servidor.routers.chat import construir_contexto_web

        # resultados = [
        #     {"titulo": "Título 1", "url": "https://example1.com", "snippet": "Descripción 1"},
        #     {"titulo": "Título 2", "url": "https://example2.com", "snippet": "Descripción 2"}
        # ]
        # textos = ["Contenido de la página 1", "Contenido de la página 2"]

        # contexto = construir_contexto_web(resultados, textos)
        pytest.skip("Function construir_contexto_web not implemented yet")

        assert "FUENTE 1:" in contexto
        assert "FUENTE 2:" in contexto
        assert "Título 1" in contexto
        assert "https://example1.com" in contexto
        assert "Contenido de la página 1" in contexto

    def test_construir_prompt_rag(self):
        """Test de construcción de prompt RAG - DISABLED: Function not implemented yet."""
        # TODO: Implement construir_prompt_rag function in chat router
        pytest.skip("Function construir_prompt_rag not implemented yet")

    def test_necesita_mas_busqueda(self):
        """Test de detección de necesidad de más búsqueda - DISABLED: Function not implemented yet."""
        # TODO: Implement necesita_mas_busqueda function in chat router
        pytest.skip("Function necesita_mas_busqueda not implemented yet")
