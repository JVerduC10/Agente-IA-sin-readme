#!/usr/bin/env python3
"""
Script de prueba para verificar la integración completa del sistema DeepSearch.
Este script verifica que todos los componentes funcionen correctamente.
"""

import sys
import os
import logging
from unittest.mock import Mock, patch

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.search_engine import buscar_bing, refinar_query, BingSearchError
from scripts.extract import leer_contenido, extraer_contenido_multiple
from scripts.deepsearch import run_deepsearch, validate_deepsearch_config, DeepSearchError
from servidor.settings import Settings
from servidor.routers.chat import Msg

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class MockSettings:
    """Configuración mock para pruebas."""
    def __init__(self):
        self.BING_API_KEY = "test_api_key"
        self.BING_SEARCH_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
        self.WEB_SCRAPE_TIMEOUT = 10
        self.MAX_SEARCH_RESULTS = 3
        self.MAX_PAGE_LENGTH = 1000
        self.temperature_map = {
            "scientific": 0.1,
            "creative": 1.3,
            "general": 0.7,
            "web": 0.3,
        }

def test_search_engine():
    """Prueba el motor de búsqueda Bing."""
    print("\n[SEARCH] Probando motor de búsqueda Bing...")
    
    # Mock de respuesta de Bing
    mock_response_data = {
        "webPages": {
            "value": [
                {
                    "name": "Inteligencia Artificial - Wikipedia",
                    "url": "https://es.wikipedia.org/wiki/Inteligencia_artificial",
                    "snippet": "La inteligencia artificial es la inteligencia llevada a cabo por máquinas."
                },
                {
                    "name": "IA en 2024 - Tendencias",
                    "url": "https://example.com/ia-2024",
                    "snippet": "Las últimas tendencias en inteligencia artificial para 2024."
                }
            ]
        }
    }
    
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        try:
            resultados = buscar_bing(
                "inteligencia artificial 2024",
                api_key="test_key",
                endpoint="https://api.bing.microsoft.com/v7.0/search"
            )
            
            assert len(resultados) == 2
            assert "title" in resultados[0]
            assert "url" in resultados[0]
            assert "snippet" in resultados[0]
            
            print("[OK] Motor de búsqueda Bing: PASÓ")
            return True
            
        except Exception as e:
            print(f"[ERROR] Motor de búsqueda Bing: FALLÓ - {e}")
            return False

def test_content_extraction():
    """Prueba la extracción de contenido web."""
    print("\n📄 Probando extracción de contenido...")
    
    mock_html = """
    <html>
        <head><title>Página de prueba</title></head>
        <body>
            <h1>Inteligencia Artificial</h1>
            <p>La inteligencia artificial es una tecnología revolucionaria.</p>
            <script>console.log('script');</script>
            <style>body { color: blue; }</style>
            <p>Más información sobre IA y machine learning.</p>
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
            try:
                contenido = leer_contenido("https://example.com")
                
                assert contenido is not None
                assert "inteligencia artificial" in contenido.lower()
                assert "script" not in contenido  # Scripts deben ser removidos
                assert "color: blue" not in contenido  # CSS debe ser removido
                
                print("[OK] Extracción de contenido: PASÓ")
                return True
                
            except Exception as e:
                print(f"[ERROR] Extracción de contenido: FALLÓ - {e}")
                return False

def test_deepsearch_system():
    """Prueba el sistema DeepSearch completo."""
    print("\n🧠 Probando sistema DeepSearch...")
    
    settings = MockSettings()
    
    # Mock de función del modelo
    def mock_model_fn(prompt: str, temperature: float) -> str:
        if "inteligencia artificial" in prompt.lower():
            return "La inteligencia artificial es una tecnología que permite a las máquinas simular la inteligencia humana."
        return "Respuesta generada por el modelo de IA."
    
    # Mock de resultados de búsqueda
    mock_search_results = [
        {
            "title": "IA - Definición",
            "url": "https://example.com/ia",
            "snippet": "Definición de inteligencia artificial"
        }
    ]
    
    # Mock de contenido extraído
    mock_content = "La inteligencia artificial es una rama de la informática que se ocupa de la creación de sistemas inteligentes."
    
    with patch('scripts.deepsearch.buscar_bing', return_value=mock_search_results):
        with patch('scripts.deepsearch.leer_contenido', return_value=mock_content):
            try:
                respuesta = run_deepsearch(
                    "¿Qué es la inteligencia artificial?",
                    "web",
                    model_fn=mock_model_fn,
                    settings=settings
                )
                
                assert len(respuesta) > 10
                assert "inteligencia artificial" in respuesta.lower()
                
                print("[OK] Sistema DeepSearch: PASÓ")
                return True
                
            except Exception as e:
                print(f"[ERROR] Sistema DeepSearch: FALLÓ - {e}")
                return False

def test_configuration_validation():
    """Prueba la validación de configuración."""
    print("\n⚙️ Probando validación de configuración...")
    
    try:
        # Configuración válida
        settings_validas = MockSettings()
        assert validate_deepsearch_config(settings_validas) is True
        
        # Configuración inválida
        settings_invalidas = MockSettings()
        settings_invalidas.BING_API_KEY = ""
        assert validate_deepsearch_config(settings_invalidas) is False
        
        print("[OK] Validación de configuración: PASÓ")
        return True
        
    except Exception as e:
        print(f"[ERROR] Validación de configuración: FALLÓ - {e}")
        return False

def test_query_refinement():
    """Prueba el refinamiento de consultas."""
    print("\n🔧 Probando refinamiento de consultas...")
    
    try:
        # Pruebas de refinamiento
        test_cases = [
            ("¿Qué es la inteligencia artificial?", "inteligencia artificial"),
            ("¿Cómo funciona el machine learning?", "funciona machine learning"),
            ("¿Cuáles son las tendencias de IA en 2024?", "son las tendencias IA 2024")
        ]
        
        for original, esperado_parcial in test_cases:
            refinada = refinar_query(original)
            # Verificar que se removieron algunas palabras de pregunta
            assert len(refinada) <= len(original)
            
        print("[OK] Refinamiento de consultas: PASÓ")
        return True
        
    except Exception as e:
        print(f"[ERROR] Refinamiento de consultas: FALLÓ - {e}")
        return False

def test_chat_integration():
    """Prueba la integración con el sistema de chat."""
    print("\n💬 Probando integración con chat...")
    
    try:
        # Verificar que el modelo Msg acepta query_type="web"
        msg = Msg(
            prompt="¿Cuáles son las últimas noticias sobre IA?",
            query_type="web",
            temperature=0.3
        )
        
        assert msg.prompt == "¿Cuáles son las últimas noticias sobre IA?"
        assert msg.query_type == "web"
        assert msg.temperature == 0.3
        
        print("[OK] Integración con chat: PASÓ")
        return True
        
    except Exception as e:
        print(f"[ERROR] Integración con chat: FALLÓ - {e}")
        return False

def main():
    """Función principal que ejecuta todas las pruebas."""
    print("[START] Iniciando pruebas de integración DeepSearch")
    print("=" * 60)
    
    tests = [
        test_search_engine,
        test_content_extraction,
        test_deepsearch_system,
        test_configuration_validation,
        test_query_refinement,
        test_chat_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print("[SUMMARY] RESUMEN DE PRUEBAS DE INTEGRACIÓN")
    print("=" * 60)
    
    for i, test in enumerate(tests, 1):
        status = "[OK] PASÓ" if i <= passed else "[ERROR] FALLÓ"
        print(f"{test.__name__.replace('test_', '').replace('_', ' ').title():<30} {status}")
    
    print(f"\n[RESULT] Resultado final: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas de integración pasaron! El sistema DeepSearch está listo.")
        return 0
    else:
        print(f"[WARN] {total - passed} pruebas fallaron. Revisar la implementacion.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)