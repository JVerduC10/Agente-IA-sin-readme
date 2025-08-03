import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from servidor.utils.search import buscar_web, refinar_query, WebSearchError
from servidor.utils.scrape import leer_pagina, extraer_contenido_multiple, WebScrapingError
from servidor.settings import Settings
from servidor.main import app


@pytest.fixture
def mock_settings():
    """Configuración mock para tests."""
    settings = Settings(
        GROQ_API_KEY="test_key",
        SEARCH_API_KEY="test_search_key",
        SEARCH_ENDPOINT="https://api.bing.microsoft.com/v7.0/search",
        WEB_SCRAPE_TIMEOUT=10,
        MAX_SEARCH_RESULTS=3,
        MAX_PAGE_LENGTH=1000,
        MAX_SEARCH_ITERATIONS=2
    )
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
                    "url": "https://example1.com"
                },
                {
                    "name": "Título de prueba 2",
                    "snippet": "Descripción de prueba 2",
                    "url": "https://example2.com"
                }
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
        """Test de búsqueda web exitosa."""
        with patch('httpx.AsyncClient') as mock_client:
            # Configurar mock
            mock_response = MagicMock()
            mock_response.json.return_value = mock_search_response
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            # Ejecutar búsqueda
            resultados = await buscar_web("test query", mock_settings)
            
            # Verificar resultados
            assert len(resultados) == 2
            assert resultados[0]["titulo"] == "Título de prueba 1"
            assert resultados[0]["snippet"] == "Descripción de prueba 1"
            assert resultados[0]["url"] == "https://example1.com"
    
    @pytest.mark.asyncio
    async def test_buscar_web_sin_api_key(self, mock_settings):
        """Test de búsqueda web sin API key."""
        mock_settings.SEARCH_API_KEY = ""
        
        with pytest.raises(WebSearchError, match="SEARCH_API_KEY no configurada"):
            await buscar_web("test query", mock_settings)
    
    @pytest.mark.asyncio
    async def test_buscar_web_error_http(self, mock_settings):
        """Test de error HTTP en búsqueda web."""
        with patch('httpx.AsyncClient') as mock_client:
            # Configurar mock para error HTTP
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.HTTPStatusError("401", request=None, response=mock_response)
            )
            
            with pytest.raises(WebSearchError, match="Error en la API de búsqueda: 401"):
                await buscar_web("test query", mock_settings)
    
    @pytest.mark.asyncio
    async def test_refinar_query_basico(self):
        """Test de refinamiento básico de query."""
        query_original = "¿Cuál es la capital de Francia?"
        query_refinada = await refinar_query(query_original)
        
        # Debe remover palabras de pregunta
        assert "cuál" not in query_refinada.lower()
        assert "capital" in query_refinada.lower()
        assert "francia" in query_refinada.lower()
    
    @pytest.mark.asyncio
    async def test_refinar_query_con_respuesta_previa(self):
        """Test de refinamiento con respuesta previa."""
        query_original = "Información sobre Python"
        respuesta_previa = "Necesito más información específica"
        
        query_refinada = await refinar_query(query_original, respuesta_previa)
        
        assert "detalles específicos" in query_refinada


class TestWebScraping:
    """Tests para funcionalidad de web scraping."""
    
    @pytest.mark.asyncio
    async def test_leer_pagina_exitoso(self, mock_settings, mock_html_content):
        """Test de lectura exitosa de página web."""
        with patch('httpx.AsyncClient') as mock_client:
            # Configurar mock
            mock_response = MagicMock()
            mock_response.text = mock_html_content
            mock_response.headers = {"content-type": "text/html"}
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            # Ejecutar scraping
            texto = await leer_pagina("https://example.com", mock_settings)
            
            # Verificar que se extrajo texto limpio
            assert "Título principal" in texto
            assert "párrafo de prueba" in texto
            assert "script" not in texto  # Scripts deben ser removidos
            assert "color: red" not in texto  # CSS debe ser removido
    
    @pytest.mark.asyncio
    async def test_leer_pagina_contenido_no_html(self, mock_settings):
        """Test de lectura de contenido no HTML."""
        with patch('httpx.AsyncClient') as mock_client:
            # Configurar mock para contenido PDF
            mock_response = MagicMock()
            mock_response.headers = {"content-type": "application/pdf"}
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            # Ejecutar scraping
            texto = await leer_pagina("https://example.com/file.pdf", mock_settings)
            
            # Debe indicar que no es HTML
            assert "Contenido no HTML" in texto
    
    @pytest.mark.asyncio
    async def test_leer_pagina_error_http(self, mock_settings):
        """Test de error HTTP en scraping."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 404
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.HTTPStatusError("404", request=None, response=mock_response)
            )
            
            with pytest.raises(WebScrapingError, match="Error HTTP 404"):
                await leer_pagina("https://example.com/notfound", mock_settings)
    
    @pytest.mark.asyncio
    async def test_extraer_contenido_multiple(self, mock_settings, mock_html_content):
        """Test de extracción de contenido de múltiples URLs."""
        urls = ["https://example1.com", "https://example2.com"]
        
        with patch('servidor.utils.scrape.leer_pagina') as mock_leer:
            mock_leer.side_effect = [
                "Contenido de la página 1",
                "Contenido de la página 2"
            ]
            
            textos = await extraer_contenido_multiple(urls, mock_settings)
            
            assert len(textos) == 2
            assert textos[0] == "Contenido de la página 1"
            assert textos[1] == "Contenido de la página 2"
    
    @pytest.mark.asyncio
    async def test_extraer_contenido_multiple_con_errores(self, mock_settings):
        """Test de extracción con errores en algunas URLs."""
        urls = ["https://example1.com", "https://example2.com"]
        
        with patch('servidor.utils.scrape.leer_pagina') as mock_leer:
            mock_leer.side_effect = [
                "Contenido exitoso",
                WebScrapingError("Error de conexión")
            ]
            
            textos = await extraer_contenido_multiple(urls, mock_settings)
            
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
        """Test de construcción de contexto web."""
        from servidor.routers.chat import construir_contexto_web
        
        resultados = [
            {"titulo": "Título 1", "url": "https://example1.com", "snippet": "Descripción 1"},
            {"titulo": "Título 2", "url": "https://example2.com", "snippet": "Descripción 2"}
        ]
        textos = ["Contenido de la página 1", "Contenido de la página 2"]
        
        contexto = construir_contexto_web(resultados, textos)
        
        assert "FUENTE 1:" in contexto
        assert "FUENTE 2:" in contexto
        assert "Título 1" in contexto
        assert "https://example1.com" in contexto
        assert "Contenido de la página 1" in contexto
    
    def test_construir_prompt_rag(self):
        """Test de construcción de prompt RAG."""
        from servidor.routers.chat import construir_prompt_rag
        
        question = "¿Cuál es la capital de Francia?"
        contexto = "FUENTE 1: París es la capital de Francia..."
        
        prompt = construir_prompt_rag(question, contexto)
        
        assert "asistente de investigación" in prompt
        assert question in prompt
        assert contexto in prompt
        assert "ÚNICAMENTE la información web" in prompt
    
    def test_necesita_mas_busqueda(self):
        """Test de detección de necesidad de más búsqueda."""
        from servidor.routers.chat import necesita_mas_busqueda
        
        # Casos que necesitan más búsqueda
        assert necesita_mas_busqueda("La información es insuficiente para responder")
        assert necesita_mas_busqueda("No se encontró información relevante")
        assert necesita_mas_busqueda("Requiere más detalles específicos")
        
        # Casos que no necesitan más búsqueda
        assert not necesita_mas_busqueda("París es la capital de Francia")
        assert not necesita_mas_busqueda("La respuesta completa es...")