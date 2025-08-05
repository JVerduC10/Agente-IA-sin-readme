#!/usr/bin/env python3
"""
Demo del conversor JSON a HTML
Ejemplo de uso del conversor con datos de prueba
"""

import json
from pathlib import Path
from json_to_html_converter import convert_json_to_html


def create_sample_data():
    """Crea datos de ejemplo para demostrar el conversor"""
    
    # Ejemplo 1: Pruebas exitosas
    sample_success = {
        "timestamp": "2025-01-15T14:30:45.123456",
        "passed_tests": 15,
        "failed_tests": 1,
        "skipped_tests": 2,
        "total_tests": 18,
        "test_details": [
            "test_auth.py::test_valid_api_key",
            "test_auth.py::test_missing_api_key",
            "test_rag.py::test_search_functionality"
        ],
        "categories": {
            "unit_tests": {
                "passed": 10,
                "failed": 1,
                "skipped": 1,
                "tests": [
                    "test_auth.py::test_valid_api_key",
                    "test_auth.py::test_missing_api_key",
                    "test_auth.py::test_no_api_keys_configured",
                    "test_models.py::test_chat_request_validation",
                    "test_models.py::test_temperature_validation",
                    "test_utils.py::test_format_response",
                    "test_utils.py::test_error_handling",
                    "test_config.py::test_settings_loading",
                    "test_config.py::test_environment_variables",
                    "test_security.py::test_api_key_validation",
                    "test_security.py::test_unauthorized_access",
                    "test_handlers.py::test_check_api_key_header"
                ]
            },
            "integration_tests": {
                "passed": 5,
                "failed": 0,
                "skipped": 1,
                "tests": [
                    "test_rag.py::test_search_functionality",
                    "test_rag.py::test_document_retrieval",
                    "test_rag.py::test_embedding_generation",
                    "test_api.py::test_chat_endpoint_integration",
                    "test_api.py::test_search_endpoint_integration",
                    "test_web.py::test_web_scraping_integration"
                ]
            }
        },
        "success": True
    }
    
    # Ejemplo 2: Sin pruebas ejecutadas
    sample_no_tests = {
        "timestamp": "2025-01-15T14:35:12.789012",
        "passed_tests": 0,
        "failed_tests": 0,
        "skipped_tests": 0,
        "total_tests": 0,
        "test_details": [],
        "categories": {
            "unit_tests": {
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "tests": []
            },
            "integration_tests": {
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "tests": []
            }
        },
        "success": False
    }
    
    # Ejemplo 3: Pruebas con fallos
    sample_failures = {
        "timestamp": "2025-01-15T14:40:33.456789",
        "passed_tests": 8,
        "failed_tests": 5,
        "skipped_tests": 3,
        "total_tests": 16,
        "test_details": [
            "test_auth.py::test_invalid_credentials - FAILED",
            "test_api.py::test_malformed_request - FAILED",
            "test_rag.py::test_empty_query - SKIPPED"
        ],
        "categories": {
            "unit_tests": {
                "passed": 5,
                "failed": 3,
                "skipped": 2,
                "tests": [
                    "test_auth.py::test_valid_credentials - PASSED",
                    "test_auth.py::test_invalid_credentials - FAILED",
                    "test_auth.py::test_missing_credentials - FAILED",
                    "test_models.py::test_valid_request - PASSED",
                    "test_models.py::test_invalid_request - FAILED",
                    "test_utils.py::test_format_success - PASSED",
                    "test_utils.py::test_format_error - PASSED",
                    "test_config.py::test_valid_config - PASSED",
                    "test_config.py::test_missing_config - SKIPPED",
                    "test_security.py::test_rate_limiting - SKIPPED"
                ]
            },
            "integration_tests": {
                "passed": 3,
                "failed": 2,
                "skipped": 1,
                "tests": [
                    "test_rag.py::test_full_search_flow - PASSED",
                    "test_rag.py::test_document_indexing - PASSED",
                    "test_rag.py::test_empty_query - SKIPPED",
                    "test_api.py::test_chat_flow - PASSED",
                    "test_api.py::test_malformed_request - FAILED",
                    "test_web.py::test_scraping_timeout - FAILED"
                ]
            }
        },
        "success": False
    }
    
    return {
        "success": sample_success,
        "no_tests": sample_no_tests,
        "failures": sample_failures
    }


def main():
    """Genera ejemplos HTML usando el conversor"""
    
    # Crear directorio de salida
    output_dir = Path("resultados/html_examples")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar datos de ejemplo
    samples = create_sample_data()
    
    print("🚀 Generando ejemplos HTML...\n")
    
    for name, data in samples.items():
        # Guardar JSON de ejemplo
        json_file = output_dir / f"sample_{name}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Generar HTML
        html_content = convert_json_to_html(data)
        html_file = output_dir / f"report_{name}.html"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ {name.upper()}:")
        print(f"   📄 JSON: {json_file}")
        print(f"   🌐 HTML: {html_file}")
        print(f"   📊 Tests: {data['total_tests']} total, {data['passed_tests']} exitosos")
        print()
    
    print("🎉 ¡Ejemplos generados exitosamente!")
    print(f"📁 Revisa la carpeta: {output_dir.absolute()}")
    print("\n💡 Para usar el conversor:")
    print("   python scripts/json_to_html_converter.py <archivo.json> <salida.html>")


if __name__ == "__main__":
    main()