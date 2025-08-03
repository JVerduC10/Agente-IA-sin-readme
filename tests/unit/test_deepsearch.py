import pytest
from unittest.mock import Mock, patch, MagicMock
from scripts.search_engine import buscar_bing, BingSearchError
from scripts.extract import leer_contenido, ExtractionError
from scripts.deepsearch import run_deepsearch, DeepSearchError, validate_deepsearch_config
from servidor.settings import Settings


class MockSettings:
    """Configuración mock para tests."""
    def __init__(self):
        self.BING_API_KEY = "test_api_key"
        self.BING_SEARCH_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
        self.WEB_SCRAPE_TIMEOUT = 10
        self.MAX_SEARCH_RESULTS = 3
        self.MAX_PAGE_LENGTH = 1000


@pytest.fixture
def mock_settings():
    """Fixture que proporciona configuración mock."""
    return MockSettings()


@pytest.fixture
def mock_bing_results():
    """Fixture con resultados mock de Bing."""
    return [
        {
            "title": "Obesidad - Organización Mundial de la Salud",
            "url": "https://www.who.int/es/news-room/fact-sheets/detail/obesity-and-overweight",
            "snippet": "La obesidad es una acumulación anormal o excesiva de grasa que puede ser perjudicial para la salud."
        },
        {
            "title": "Datos sobre obesidad - OMS",
            "url": "https://www.who.int/es/health-topics/obesity",
            "snippet": "La obesidad ha alcanzado proporciones epidémicas a nivel mundial."
        }
    ]


@pytest.fixture
def mock_extracted_content():
    """Fixture con contenido extraído mock."""
    return [
        "La obesidad es una acumulación anormal o excesiva de grasa que puede ser perjudicial para la salud. Según la OMS, la obesidad ha alcanzado proporciones epidémicas a nivel mundial.",
        "Los datos de la OMS muestran que la obesidad se ha triplicado en todo el mundo desde 1975. En 2016, más de 1900 millones de adultos tenían sobrepeso."
    ]


class TestBingSearch:
    """Tests para la función buscar_bing."""
    
    def test_bing_busqueda_exitosa(self, mock_bing_results):
        """Test de búsqueda exitosa en Bing."""
        with patch('requests.get') as mock_get:
            # Configurar mock response
            mock_response = Mock()
            mock_response.json.return_value = {
                "webPages": {
                    "value": [
                        {
                            "name": "Obesidad - OMS",
                            "url": "https://www.who.int/obesity",
                            "snippet": "Información sobre obesidad de la OMS"
                        }
                    ]
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Ejecutar búsqueda
            resultados = buscar_bing(
                "última ley de IA europea", 
                api_key="test_key", 
                endpoint="https://api.bing.microsoft.com/v7.0/search"
            )
            
            # Verificaciones
            assert len(resultados) > 0
            assert "url" in resultados[0]
            assert "title" in resultados[0]
            assert "snippet" in resultados[0]
            assert resultados[0]["url"] == "https://www.who.int/obesity"
    
    def test_bing_busqueda_sin_api_key(self):
        """Test de búsqueda sin API key."""
        with pytest.raises(BingSearchError, match="API key de Bing no configurada"):
            buscar_bing("test query", api_key="", endpoint="https://api.bing.microsoft.com/v7.0/search")
    
    def test_bing_busqueda_error_http(self):
        """Test de error HTTP en búsqueda Bing."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("HTTP 401")
            mock_get.return_value = mock_response
            
            with pytest.raises(BingSearchError):
                buscar_bing(
                    "test query", 
                    api_key="invalid_key", 
                    endpoint="https://api.bing.microsoft.com/v7.0/search"
                )


class TestContentExtraction:
    """Tests para extracción de contenido."""
    
    def test_leer_contenido_exitoso(self):
        """Test de extracción exitosa de contenido."""
        mock_html = """
        <html>
            <body>
                <h1>Título de prueba</h1>
                <p>Este es contenido de prueba sobre obesidad y salud.</p>
                <script>console.log('script');</script>
            </body>
        </html>
        """
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = mock_html
            mock_response.headers = {"content-type": "text/html"}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Mock trafilatura para que falle y use BeautifulSoup
            with patch('trafilatura.extract', return_value=None):
                contenido = leer_contenido("https://example.com")
                
                assert contenido is not None
                assert "obesidad" in contenido.lower()
                assert "script" not in contenido  # Scripts deben ser removidos
    
    def test_leer_contenido_error_http(self):
        """Test de error HTTP en extracción."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection error")
            
            contenido = leer_contenido("https://invalid-url.com")
            assert contenido is None


class TestDeepSearch:
    """Tests para el sistema DeepSearch."""
    
    def test_run_deepsearch_minimo(self, mock_settings, mock_bing_results, mock_extracted_content):
        """Test mínimo de run_deepsearch."""
        # Mock de la función del modelo
        def mock_model_fn(prompt: str, temperature: float) -> str:
            if "obesidad" in prompt.lower() or "OMS" in prompt:
                return "Según la OMS, la obesidad es una acumulación anormal de grasa que puede ser perjudicial para la salud."
            return prompt  # Fallback
        
        # Mock de búsqueda Bing
        with patch('scripts.deepsearch.buscar_bing', return_value=mock_bing_results):
            # Mock de extracción de contenido
            with patch('scripts.deepsearch.leer_contenido', side_effect=mock_extracted_content):
                respuesta = run_deepsearch(
                    "¿Qué dice la OMS sobre la obesidad?", 
                    "web", 
                    model_fn=mock_model_fn, 
                    settings=mock_settings
                )
                
                assert "obesidad" in respuesta.lower() or "OMS" in respuesta
                assert len(respuesta) > 10  # Verificar que hay contenido
    
    def test_run_deepsearch_sin_configuracion(self):
        """Test de DeepSearch sin configuración válida."""
        settings_invalidas = MockSettings()
        settings_invalidas.BING_API_KEY = ""  # Sin API key
        
        def mock_model_fn(prompt: str, temperature: float) -> str:
            return "respuesta mock"
        
        with pytest.raises(DeepSearchError, match="BING_API_KEY no configurada"):
            run_deepsearch(
                "test query", 
                "web", 
                model_fn=mock_model_fn, 
                settings=settings_invalidas
            )
    
    def test_run_deepsearch_error_busqueda(self, mock_settings):
        """Test de DeepSearch con error en búsqueda."""
        def mock_model_fn(prompt: str, temperature: float) -> str:
            return "respuesta mock"
        
        # Mock que simula error en búsqueda
        with patch('scripts.deepsearch.buscar_bing', side_effect=BingSearchError("API error")):
            respuesta = run_deepsearch(
                "test query", 
                "web", 
                model_fn=mock_model_fn, 
                settings=mock_settings
            )
            
            assert "no pude realizar la búsqueda web" in respuesta
    
    def test_run_deepsearch_sin_resultados(self, mock_settings):
        """Test de DeepSearch sin resultados de búsqueda."""
        def mock_model_fn(prompt: str, temperature: float) -> str:
            return "respuesta mock"
        
        # Mock que devuelve lista vacía
        with patch('scripts.deepsearch.buscar_bing', return_value=[]):
            respuesta = run_deepsearch(
                "test query", 
                "web", 
                model_fn=mock_model_fn, 
                settings=mock_settings
            )
            
            assert "No encontré información relevante" in respuesta


class TestValidation:
    """Tests para validación de configuración."""
    
    def test_validate_deepsearch_config_valida(self, mock_settings):
        """Test de validación con configuración válida."""
        assert validate_deepsearch_config(mock_settings) is True
    
    def test_validate_deepsearch_config_invalida(self):
        """Test de validación con configuración inválida."""
        settings_invalidas = MockSettings()
        settings_invalidas.BING_API_KEY = ""
        
        assert validate_deepsearch_config(settings_invalidas) is False


if __name__ == "__main__":
    pytest.main([__file__])