#!/usr/bin/env python3
"""
Script de verificación manual para las mejoras implementadas en results.html

Este script permite verificar:
1. Endpoints de progreso
2. Endpoints optimizados de metadatos y detalles
3. Verificación de configuración de API

Uso:
    python scripts/verify_improvements.py
"""

import asyncio
import json
import requests
import time
from datetime import datetime
from pathlib import Path


class ImprovementsVerifier:
    """Verificador de mejoras implementadas"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def print_header(self, title):
        """Imprimir encabezado de sección"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def print_result(self, test_name, success, details=""):
        """Imprimir resultado de prueba"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
    
    def verify_server_running(self):
        """Verificar que el servidor esté ejecutándose"""
        self.print_header("VERIFICACIÓN DEL SERVIDOR")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            success = response.status_code == 200
            self.print_result(
                "Servidor ejecutándose", 
                success,
                f"Status: {response.status_code}" if not success else "Servidor disponible"
            )
            return success
        except requests.exceptions.ConnectionError:
            self.print_result(
                "Servidor ejecutándose", 
                False, 
                "No se puede conectar al servidor. ¿Está ejecutándose?"
            )
            return False
    
    def verify_api_configuration(self):
        """Verificar endpoint de configuración de API"""
        self.print_header("VERIFICACIÓN DE CONFIGURACIÓN API")
        
        try:
            response = self.session.get(f"{self.base_url}/api/results/config-check")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.print_result("Endpoint config-check", True, f"Status: {data.get('status')}")
                
                # Verificar estructura de respuesta
                required_fields = ['status', 'can_run_tests', 'can_run_evaluations', 'details']
                for field in required_fields:
                    field_present = field in data
                    self.print_result(
                        f"Campo '{field}' presente", 
                        field_present,
                        f"Valor: {data.get(field)}" if field_present else "Campo faltante"
                    )
                
                # Verificar detalles de claves API
                if 'details' in data:
                    details = data['details']
                    api_keys = ['groq_api_key', 'openai_api_key', 'anthropic_api_key']
                    for key in api_keys:
                        key_configured = details.get(key, False)
                        self.print_result(
                            f"Clave {key}", 
                            True,  # No es error si no está configurada
                            "Configurada" if key_configured else "No configurada"
                        )
            else:
                self.print_result(
                    "Endpoint config-check", 
                    False, 
                    f"Status: {response.status_code}"
                )
            
            return success
            
        except Exception as e:
            self.print_result("Endpoint config-check", False, f"Error: {str(e)}")
            return False
    
    def verify_metadata_endpoint(self):
        """Verificar endpoint de metadatos optimizado"""
        self.print_header("VERIFICACIÓN DE ENDPOINT DE METADATOS")
        
        try:
            # Verificar endpoint básico
            response = self.session.get(f"{self.base_url}/api/results/metadata")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.print_result("Endpoint metadata básico", True)
                
                # Verificar estructura de respuesta
                required_fields = ['metadata', 'total', 'page', 'limit', 'total_pages']
                for field in required_fields:
                    field_present = field in data
                    self.print_result(
                        f"Campo '{field}' presente", 
                        field_present,
                        f"Valor: {data.get(field)}" if field_present else "Campo faltante"
                    )
                
                # Verificar paginación
                if data.get('total', 0) > 0:
                    # Probar con límite específico
                    paginated_response = self.session.get(
                        f"{self.base_url}/api/results/metadata?page=1&limit=5"
                    )
                    
                    if paginated_response.status_code == 200:
                        paginated_data = paginated_response.json()
                        self.print_result(
                            "Paginación funcional", 
                            True,
                            f"Página 1, límite 5: {len(paginated_data.get('metadata', []))} elementos"
                        )
                    else:
                        self.print_result(
                            "Paginación funcional", 
                            False,
                            f"Status: {paginated_response.status_code}"
                        )
                else:
                    self.print_result(
                        "Paginación funcional", 
                        True,
                        "No hay resultados para paginar"
                    )
            else:
                self.print_result(
                    "Endpoint metadata básico", 
                    False, 
                    f"Status: {response.status_code}"
                )
            
            return success
            
        except Exception as e:
            self.print_result("Endpoint metadata", False, f"Error: {str(e)}")
            return False
    
    def verify_detail_endpoint(self):
        """Verificar endpoint de detalle"""
        self.print_header("VERIFICACIÓN DE ENDPOINT DE DETALLE")
        
        try:
            # Primero obtener lista de metadatos para encontrar un ID válido
            metadata_response = self.session.get(f"{self.base_url}/api/results/metadata?limit=1")
            
            if metadata_response.status_code == 200:
                metadata = metadata_response.json()
                
                if metadata.get('total', 0) > 0:
                    # Usar el primer resultado disponible
                    result_id = metadata['metadata'][0]['id']
                    
                    detail_response = self.session.get(
                        f"{self.base_url}/api/results/detail/{result_id}"
                    )
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        self.print_result("Endpoint detail con ID válido", True)
                        
                        # Verificar estructura
                        required_fields = ['id', 'data', 'metadata']
                        for field in required_fields:
                            field_present = field in detail_data
                            self.print_result(
                                f"Campo '{field}' presente", 
                                field_present
                            )
                    else:
                        self.print_result(
                            "Endpoint detail con ID válido", 
                            False,
                            f"Status: {detail_response.status_code}"
                        )
                else:
                    self.print_result(
                        "Endpoint detail con ID válido", 
                        True,
                        "No hay resultados disponibles para probar"
                    )
            
            # Probar con ID inexistente
            invalid_response = self.session.get(
                f"{self.base_url}/api/results/detail/nonexistent_id_12345"
            )
            
            expected_404 = invalid_response.status_code == 404
            self.print_result(
                "Manejo de ID inexistente (404)", 
                expected_404,
                f"Status: {invalid_response.status_code}"
            )
            
            return True
            
        except Exception as e:
            self.print_result("Endpoint detail", False, f"Error: {str(e)}")
            return False
    
    def verify_progress_endpoints(self):
        """Verificar endpoints de progreso"""
        self.print_header("VERIFICACIÓN DE ENDPOINTS DE PROGRESO")
        
        # Probar con session_id ficticio
        test_session_id = "test_session_verification"
        
        try:
            # Verificar endpoint de progreso de pruebas
            test_progress_response = self.session.get(
                f"{self.base_url}/api/results/test-progress/{test_session_id}"
            )
            
            # Debería devolver 404 para session_id inexistente
            expected_404_tests = test_progress_response.status_code == 404
            self.print_result(
                "Endpoint test-progress (404 para ID inexistente)", 
                expected_404_tests,
                f"Status: {test_progress_response.status_code}"
            )
            
            # Verificar endpoint de progreso de evaluaciones
            eval_progress_response = self.session.get(
                f"{self.base_url}/api/results/evaluation-progress/{test_session_id}"
            )
            
            expected_404_evals = eval_progress_response.status_code == 404
            self.print_result(
                "Endpoint evaluation-progress (404 para ID inexistente)", 
                expected_404_evals,
                f"Status: {eval_progress_response.status_code}"
            )
            
            return expected_404_tests and expected_404_evals
            
        except Exception as e:
            self.print_result("Endpoints de progreso", False, f"Error: {str(e)}")
            return False
    
    def verify_api_key_validation(self):
        """Verificar validación de claves API en run-tests y run-evaluations"""
        self.print_header("VERIFICACIÓN DE VALIDACIÓN DE CLAVES API")
        
        try:
            # Verificar run-tests
            test_response = self.session.post(f"{self.base_url}/api/results/run-tests")
            
            # Puede ser 200 (si hay claves) o 400 (si faltan claves)
            test_valid = test_response.status_code in [200, 400]
            
            if test_response.status_code == 200:
                # Si es 200, debería tener session_id
                test_data = test_response.json()
                has_session = 'session_id' in test_data
                self.print_result(
                    "Endpoint run-tests", 
                    has_session,
                    f"Status: {test_response.status_code}, Session ID presente: {has_session}"
                )
            elif test_response.status_code == 400:
                # Si es 400, debería ser por claves faltantes
                test_data = test_response.json()
                is_api_key_error = 'missing_api_keys' in str(test_data)
                self.print_result(
                    "Endpoint run-tests (validación API)", 
                    is_api_key_error,
                    f"Status: {test_response.status_code}, Error de claves API: {is_api_key_error}"
                )
            else:
                self.print_result(
                    "Endpoint run-tests", 
                    False,
                    f"Status inesperado: {test_response.status_code}"
                )
            
            # Verificar run-evaluations
            eval_response = self.session.post(f"{self.base_url}/api/results/run-evaluations")
            
            eval_valid = eval_response.status_code in [200, 400]
            
            if eval_response.status_code == 200:
                eval_data = eval_response.json()
                has_session = 'session_id' in eval_data
                self.print_result(
                    "Endpoint run-evaluations", 
                    has_session,
                    f"Status: {eval_response.status_code}, Session ID presente: {has_session}"
                )
            elif eval_response.status_code == 400:
                eval_data = eval_response.json()
                is_api_key_error = 'missing_api_keys' in str(eval_data)
                self.print_result(
                    "Endpoint run-evaluations (validación API)", 
                    is_api_key_error,
                    f"Status: {eval_response.status_code}, Error de claves API: {is_api_key_error}"
                )
            else:
                self.print_result(
                    "Endpoint run-evaluations", 
                    False,
                    f"Status inesperado: {eval_response.status_code}"
                )
            
            return test_valid and eval_valid
            
        except Exception as e:
            self.print_result("Validación de claves API", False, f"Error: {str(e)}")
            return False
    
    def verify_frontend_files(self):
        """Verificar que los archivos del frontend tengan las mejoras"""
        self.print_header("VERIFICACIÓN DE ARCHIVOS FRONTEND")
        
        results_html_path = Path("archivos_estaticos/results.html")
        
        if not results_html_path.exists():
            self.print_result(
                "Archivo results.html existe", 
                False, 
                f"No encontrado en {results_html_path}"
            )
            return False
        
        try:
            with open(results_html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar funciones de progreso
            has_track_progress = 'trackProgress' in content
            self.print_result(
                "Función trackProgress presente", 
                has_track_progress
            )
            
            has_check_api = 'checkApiConfiguration' in content
            self.print_result(
                "Función checkApiConfiguration presente", 
                has_check_api
            )
            
            has_metadata_loading = 'loadResultsMetadata' in content
            self.print_result(
                "Función loadResultsMetadata presente", 
                has_metadata_loading
            )
            
            has_detail_loading = 'loadResultDetail' in content
            self.print_result(
                "Función loadResultDetail presente", 
                has_detail_loading
            )
            
            # Verificar estilos CSS para progreso
            has_progress_styles = '.progress-tracker' in content
            self.print_result(
                "Estilos CSS para progreso presentes", 
                has_progress_styles
            )
            
            return all([
                has_track_progress, 
                has_check_api, 
                has_metadata_loading, 
                has_detail_loading,
                has_progress_styles
            ])
            
        except Exception as e:
            self.print_result("Verificación de frontend", False, f"Error: {str(e)}")
            return False
    
    def run_all_verifications(self):
        """Ejecutar todas las verificaciones"""
        print("🔍 VERIFICADOR DE MEJORAS - RESULTS.HTML")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"URL base: {self.base_url}")
        
        results = []
        
        # Verificar servidor
        if not self.verify_server_running():
            print("\n❌ El servidor no está ejecutándose. Iniciando verificaciones offline...")
            
            # Solo verificar archivos frontend si el servidor no está disponible
            results.append(self.verify_frontend_files())
        else:
            # Ejecutar todas las verificaciones
            results.extend([
                self.verify_api_configuration(),
                self.verify_metadata_endpoint(),
                self.verify_detail_endpoint(),
                self.verify_progress_endpoints(),
                self.verify_api_key_validation(),
                self.verify_frontend_files()
            ])
        
        # Resumen final
        self.print_header("RESUMEN FINAL")
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ Verificaciones exitosas: {passed}/{total}")
        
        if passed == total:
            print("🎉 ¡Todas las mejoras están funcionando correctamente!")
        elif passed > total // 2:
            print("⚠️  La mayoría de las mejoras están funcionando, pero hay algunos problemas.")
        else:
            print("❌ Hay problemas significativos con las mejoras implementadas.")
        
        return passed == total


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verificar mejoras implementadas en results.html"
    )
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="URL base del servidor (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--offline", 
        action="store_true",
        help="Solo verificar archivos, sin conectar al servidor"
    )
    
    args = parser.parse_args()
    
    verifier = ImprovementsVerifier(args.url)
    
    if args.offline:
        print("🔍 MODO OFFLINE - Solo verificando archivos")
        success = verifier.verify_frontend_files()
    else:
        success = verifier.run_all_verifications()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())