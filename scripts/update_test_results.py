#!/usr/bin/env python3
"""
Script para actualizar los resultados de pruebas y generar reportes HTML - OPTIMIZADO
"""

import json
import re
import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Variables globales para progreso
_progress_callback = None
_start_time = None
_total_steps = 4  # run_tests, parse_results, update_cache, generate_reports
_completed_steps = 0
_step_lock = threading.Lock()


def set_progress_callback(callback):
    """Establece la función de callback para reportar progreso"""
    global _progress_callback
    _progress_callback = callback


def _update_progress(message: str):
    """Actualiza el progreso y reporta el estado actual"""
    global _completed_steps, _start_time
    
    with _step_lock:
        if _start_time is None:
            _start_time = time.time()
        
        elapsed_time = time.time() - _start_time
        progress_percentage = (_completed_steps / _total_steps) * 100
        
        # Estimar tiempo restante
        if _completed_steps > 0:
            avg_time_per_step = elapsed_time / _completed_steps
            remaining_steps = _total_steps - _completed_steps
            eta = avg_time_per_step * remaining_steps
        else:
            eta = 0
        
        progress_info = {
            "message": message,
            "progress_percentage": progress_percentage,
            "completed_steps": _completed_steps,
            "total_steps": _total_steps,
            "elapsed_time": elapsed_time,
            "eta_seconds": eta
        }
        
        # Llamar callback si está disponible
        if _progress_callback:
            _progress_callback(progress_info)
        
        # Log por defecto
        print(f"[{progress_percentage:.1f}%] {message} (Paso {_completed_steps}/{_total_steps})")
        if eta > 0:
            print(f"    ⏱️ Tiempo transcurrido: {elapsed_time:.1f}s, ETA: {eta:.1f}s")


def _complete_step(step_name: str):
    """Marca un paso como completado"""
    global _completed_steps
    with _step_lock:
        _completed_steps += 1
        _update_progress(f"✅ {step_name} completado")


def run_tests_and_capture_results() -> Optional[subprocess.CompletedProcess]:
    """Ejecuta las pruebas y captura los resultados - OPTIMIZADO con progreso"""
    _update_progress("🧪 Iniciando ejecución de pruebas...")
    
    try:
        start_time = time.time()
        
        # Ejecutar pytest con formato JSON y progreso
        _update_progress("📋 Ejecutando pytest con formato JSON...")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "--json-report",
                "--json-report-file=test_output.json",
                "--disable-warnings",  # Reducir ruido en output
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
            timeout=300  # Timeout de 5 minutos
        )

        # Si no hay plugin json-report, usar formato de texto
        if result.returncode != 0 and "json-report" in result.stderr:
            _update_progress("⚠️ Plugin json-report no disponible, usando formato de texto...")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "--disable-warnings"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=300
            )

        execution_time = time.time() - start_time
        _update_progress(f"⚡ Pruebas ejecutadas en {execution_time:.2f}s (código: {result.returncode})")
        
        return result
        
    except subprocess.TimeoutExpired:
        _update_progress("⏰ Timeout: Las pruebas tardaron más de 5 minutos")
        return None
    except Exception as e:
        _update_progress(f"❌ Error ejecutando pruebas: {e}")
        return None


def parse_pytest_output(output_text):
    """Parsea la salida de pytest para extraer resultados"""
    lines = output_text.split("\n")

    # Buscar la línea de resumen
    summary_line = ""
    for line in lines:
        if "passed" in line and (
            "failed" in line or "skipped" in line or "warnings" in line
        ):
            summary_line = line
            break

    if not summary_line:
        # Buscar línea que termine con "passed"
        for line in lines:
            if line.strip().endswith("passed"):
                summary_line = line
                break

    # Extraer números usando regex
    passed = 0
    failed = 0
    skipped = 0

    if summary_line:
        passed_match = re.search(r"(\d+)\s+passed", summary_line)
        failed_match = re.search(r"(\d+)\s+failed", summary_line)
        skipped_match = re.search(r"(\d+)\s+skipped", summary_line)

        if passed_match:
            passed = int(passed_match.group(1))
        if failed_match:
            failed = int(failed_match.group(1))
        if skipped_match:
            skipped = int(skipped_match.group(1))

    # Extraer detalles de pruebas individuales
    test_details = []
    unit_tests = []
    integration_tests = []

    for line in lines:
        # Buscar líneas que contengan :: y algún estado de test
        if "::" in line:
            # Verificar si la línea contiene un resultado de test
            if " PASSED " in line or " FAILED " in line or " SKIPPED " in line or line.strip().endswith(" PASSED") or line.strip().endswith(" FAILED") or line.strip().endswith(" SKIPPED"):
                # Extraer el nombre del test (parte antes del estado)
                if " PASSED" in line:
                    test_name = line.split(" PASSED")[0].strip()
                    status = "passed"
                elif " FAILED" in line:
                    test_name = line.split(" FAILED")[0].strip()
                    status = "failed"
                elif " SKIPPED" in line:
                    test_name = line.split(" SKIPPED")[0].strip()
                    status = "skipped"
                else:
                    continue

                test_info = {
                    "name": test_name,
                    "status": status,
                    "category": "unit" if "test_" in test_name else "integration",
                }

                test_details.append(test_info)

                if "unit" in test_info["category"]:
                    unit_tests.append(test_info)
                else:
                    integration_tests.append(test_info)

    return {
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "total": passed + failed + skipped,
        "test_details": test_details,
        "unit_tests": unit_tests,
        "integration_tests": integration_tests,
    }


def update_test_cache(test_results):
    """Actualiza el archivo de cache de resultados de pruebas"""
    cache_data = {
        "timestamp": datetime.now().isoformat(),
        "passed_tests": test_results["passed"],
        "failed_tests": test_results["failed"],
        "skipped_tests": test_results["skipped"],
        "total_tests": test_results["total"],
        "test_details": test_results["test_details"],
        "categories": {
            "unit_tests": {
                "passed": len(
                    [t for t in test_results["unit_tests"] if t["status"] == "passed"]
                ),
                "failed": len(
                    [t for t in test_results["unit_tests"] if t["status"] == "failed"]
                ),
                "skipped": len(
                    [t for t in test_results["unit_tests"] if t["status"] == "skipped"]
                ),
                "tests": test_results["unit_tests"],
            },
            "integration_tests": {
                "passed": len(
                    [
                        t
                        for t in test_results["integration_tests"]
                        if t["status"] == "passed"
                    ]
                ),
                "failed": len(
                    [
                        t
                        for t in test_results["integration_tests"]
                        if t["status"] == "failed"
                    ]
                ),
                "skipped": len(
                    [
                        t
                        for t in test_results["integration_tests"]
                        if t["status"] == "skipped"
                    ]
                ),
                "tests": test_results["integration_tests"],
            },
        },
        "success": test_results["failed"] == 0,
    }

    # Guardar en cache principal
    with open("test_results_cache.json", "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)

    # Guardar en cache del servidor
    servidor_cache = Path("servidor/test_results_cache.json")
    if servidor_cache.parent.exists():
        with open(servidor_cache, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

    return cache_data


def generate_html_reports(cache_data):
    """Genera reportes HTML a partir de los datos de cache"""
    try:
        # Importar el convertidor
        sys.path.append(str(Path("scripts").absolute()))
        from json_to_html_converter import convert_json_to_html

        # Generar reporte principal
        html_content = convert_json_to_html(cache_data)
        with open("archivos_estaticos/test_results_report.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        # Generar reporte del servidor si existe
        servidor_cache = Path("servidor/test_results_cache.json")
        if servidor_cache.exists():
            with open(servidor_cache, "r", encoding="utf-8") as f:
                servidor_data = json.load(f)
            servidor_html = convert_json_to_html(servidor_data)
            with open("archivos_estaticos/servidor_test_results_report.html", "w", encoding="utf-8") as f:
                f.write(servidor_html)

        print("✅ Reportes HTML generados exitosamente")

    except Exception as e:
        print(f"❌ Error generando reportes HTML: {e}")


def main(progress_callback=None) -> Dict[str, Any]:
    """Función principal - OPTIMIZADA con progreso en tiempo real"""
    global _progress_callback, _start_time, _completed_steps
    
    # Reiniciar variables globales
    _progress_callback = progress_callback
    _start_time = time.time()
    _completed_steps = 0
    
    _update_progress("🚀 Iniciando actualización de resultados de pruebas...")
    
    execution_summary = {
        "start_time": datetime.now().isoformat(),
        "success": False,
        "steps_completed": 0,
        "total_steps": _total_steps,
        "errors": [],
        "metrics": {}
    }
    
    try:
        # Paso 1: Ejecutar pruebas
        _update_progress("📋 Paso 1/4: Ejecutando pruebas...")
        result = run_tests_and_capture_results()
        if not result:
            error_msg = "Error ejecutando pruebas"
            execution_summary["errors"].append(error_msg)
            _update_progress(f"❌ {error_msg}")
            return execution_summary
        
        _complete_step("Ejecución de pruebas")
        execution_summary["steps_completed"] = 1
        
        # Paso 2: Parsear resultados
        _update_progress("📊 Paso 2/4: Parseando resultados...")
        parse_start = time.time()
        test_results = parse_pytest_output(result.stdout)
        parse_time = time.time() - parse_start
        
        _update_progress(
            f"📈 Resultados: {test_results['passed']} ✅, {test_results['failed']} ❌, {test_results['skipped']} ⏭️"
        )
        
        _complete_step("Parseo de resultados")
        execution_summary["steps_completed"] = 2
        execution_summary["metrics"]["parse_time"] = parse_time
        execution_summary["test_results"] = test_results
        
        # Paso 3: Actualizar cache
        _update_progress("💾 Paso 3/4: Actualizando cache...")
        cache_start = time.time()
        cache_data = update_test_cache(test_results)
        cache_time = time.time() - cache_start
        
        _complete_step("Actualización de cache")
        execution_summary["steps_completed"] = 3
        execution_summary["metrics"]["cache_time"] = cache_time
        
        # Paso 4: Generar reportes HTML
        _update_progress("📄 Paso 4/4: Generando reportes HTML...")
        report_start = time.time()
        generate_html_reports(cache_data)
        report_time = time.time() - report_start
        
        _complete_step("Generación de reportes")
        execution_summary["steps_completed"] = 4
        execution_summary["metrics"]["report_time"] = report_time
        
        # Finalización exitosa
        total_time = time.time() - _start_time
        execution_summary["success"] = True
        execution_summary["end_time"] = datetime.now().isoformat()
        execution_summary["metrics"]["total_time"] = total_time
        
        _update_progress(f"🎉 Proceso completado exitosamente en {total_time:.2f}s")
        
        # Mostrar resumen de rendimiento
        print("\n📊 Resumen de rendimiento:")
        print(f"  ⏱️ Tiempo total: {total_time:.2f}s")
        print(f"  📋 Parseo: {parse_time:.2f}s")
        print(f"  💾 Cache: {cache_time:.2f}s")
        print(f"  📄 Reportes: {report_time:.2f}s")
        print(f"  🧪 Pruebas: {test_results['passed']} ✅ | {test_results['failed']} ❌ | {test_results['skipped']} ⏭️")
        
        return execution_summary
        
    except Exception as e:
        error_msg = f"Error inesperado: {e}"
        execution_summary["errors"].append(error_msg)
        _update_progress(f"💥 {error_msg}")
        return execution_summary


if __name__ == "__main__":
    main()
