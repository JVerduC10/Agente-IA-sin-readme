import json
import logging
import os
import subprocess
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel

# Configurar logging
logger = logging.getLogger(__name__)

# Importar funciones optimizadas
try:
    import sys
    sys.path.append(os.path.join(os.getcwd(), 'scripts'))
    from update_test_results import main as run_optimized_tests, set_progress_callback
    from evaluacion_automatica import EvaluacionAutomatica
    OPTIMIZED_AVAILABLE = True
    logger.info("Módulos optimizados cargados exitosamente")
except ImportError as e:
    logger.warning(f"Módulos optimizados no disponibles: {e}")
    OPTIMIZED_AVAILABLE = False

# Variables globales para progreso
_test_progress = {}
_evaluation_progress = {}
_progress_lock = asyncio.Lock()

router = APIRouter(prefix="/api/results", tags=["results"])


class TestResult(BaseModel):
    title: str
    timestamp: str
    status: str
    details: Dict[str, Any]


@router.get("/test-results")
async def get_test_results() -> List[Dict[str, Any]]:
    """Obtiene los reportes HTML de resultados de pruebas"""
    try:
        test_reports = []
        
        # Buscar archivos HTML de reportes de pruebas
        html_files = [
            ("test_results_report.html", "Reporte Principal de Pruebas"),
            ("servidor_test_results_report.html", "Reporte del Servidor")
        ]
        
        for filename, title in html_files:
            file_path = Path("archivos_estaticos") / filename
            if file_path.exists():
                test_reports.append({
                    "name": title,
                    "url": f"/static/{filename}",
                    "timestamp": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "file": str(file_path)
                })
        
        return test_reports
        
    except Exception as e:
        logger.error(f"Error getting test results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_results() -> List[Dict[str, Any]]:
    """Lista todos los resultados disponibles"""
    try:
        results = []

        # Buscar archivos de resultados en el directorio resultados/
        results_dir = Path("resultados")
        if results_dir.exists():
            for file_path in results_dir.glob("*.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        results.append(
                            {
                                "title": f"Evaluación - {file_path.stem}",
                                "timestamp": data.get(
                                    "timestamp", file_path.stat().st_mtime
                                ),
                                "file": str(file_path),
                                "data": data,
                            }
                        )
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")

        # Buscar archivos de cache de pruebas
        cache_file = Path("test_results_cache.json")
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    results.append(
                        {
                            "title": "Cache de Pruebas",
                            "timestamp": datetime.fromtimestamp(
                                cache_file.stat().st_mtime
                            ).isoformat(),
                            "file": str(cache_file),
                            "data": data,
                        }
                    )
            except Exception as e:
                logger.error(f"Error reading cache file: {e}")

        # Ordenar por timestamp (más reciente primero)
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return results

    except Exception as e:
        logger.error(f"Error listing results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-progress/{session_id}")
async def get_test_progress(session_id: str) -> Dict[str, Any]:
    """Obtiene el progreso actual de las pruebas"""
    async with _progress_lock:
        return _test_progress.get(session_id, {"status": "not_found"})


@router.get("/evaluation-progress/{session_id}")
async def get_evaluation_progress(session_id: str) -> Dict[str, Any]:
    """Obtiene el progreso actual de las evaluaciones"""
    async with _progress_lock:
        return _evaluation_progress.get(session_id, {"status": "not_found"})


async def _update_test_progress(session_id: str, progress_info: Dict[str, Any]):
    """Actualiza el progreso de las pruebas"""
    async with _progress_lock:
        _test_progress[session_id] = {
            **progress_info,
            "last_updated": datetime.now().isoformat()
        }


async def _update_evaluation_progress(session_id: str, progress_info: Dict[str, Any]):
    """Actualiza el progreso de las evaluaciones"""
    async with _progress_lock:
        _evaluation_progress[session_id] = {
            **progress_info,
            "last_updated": datetime.now().isoformat()
        }


@router.post("/run-tests")
async def run_tests(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Ejecuta las pruebas del sistema - OPTIMIZADO con progreso en tiempo real"""
    # Verificar configuración de API antes de ejecutar
    config_check = await check_api_configuration()
    if not config_check["can_run_tests"]:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "missing_api_keys",
                "message": "No se pueden ejecutar pruebas: faltan claves API",
                "details": config_check["details"]
            }
        )
    
    session_id = f"test_{int(time.time())}_{os.getpid()}"
    
    # Inicializar progreso
    await _update_test_progress(session_id, {
        "status": "starting",
        "progress_percentage": 0,
        "message": "Iniciando ejecución de pruebas...",
        "session_id": session_id
    })
    
    if OPTIMIZED_AVAILABLE:
        # Usar versión optimizada
        background_tasks.add_task(_run_optimized_tests_background, session_id)
        return {
            "status": "started",
            "session_id": session_id,
            "message": "Pruebas iniciadas en segundo plano con progreso optimizado",
            "progress_endpoint": f"/api/results/test-progress/{session_id}",
            "timestamp": datetime.now().isoformat(),
        }
    else:
        # Fallback a versión original
        background_tasks.add_task(_run_legacy_tests_background, session_id)
        return {
            "status": "started",
            "session_id": session_id,
            "message": "Pruebas iniciadas en segundo plano (modo legacy)",
            "progress_endpoint": f"/api/results/test-progress/{session_id}",
            "timestamp": datetime.now().isoformat(),
        }


async def _run_optimized_tests_background(session_id: str):
    """Ejecuta pruebas optimizadas en segundo plano"""
    try:
        # Configurar callback de progreso thread-safe
        def progress_callback(progress_info):
            try:
                loop = asyncio.get_running_loop()
                asyncio.run_coroutine_threadsafe(
                    _update_test_progress(session_id, {
                        "status": "running",
                        "session_id": session_id,
                        **progress_info
                    }),
                    loop
                )
            except RuntimeError:
                # No hay loop activo, actualizar directamente el progreso
                _test_progress[session_id] = {
                    "status": "running",
                    "session_id": session_id,
                    **progress_info
                }
        
        # Ejecutar pruebas optimizadas
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: run_optimized_tests(progress_callback)
        )
        
        # Actualizar progreso final
        await _update_test_progress(session_id, {
            "status": "completed",
            "session_id": session_id,
            "progress_percentage": 100,
            "message": "Pruebas completadas exitosamente",
            "result": result,
            "success": result.get("success", False)
        })
        
    except Exception as e:
        logger.error(f"Error in optimized tests: {e}")
        await _update_test_progress(session_id, {
            "status": "error",
            "session_id": session_id,
            "message": f"Error: {str(e)}",
            "error": str(e)
        })


async def _run_legacy_tests_background(session_id: str):
    """Ejecuta pruebas en modo legacy en segundo plano"""
    try:
        await _update_test_progress(session_id, {
            "status": "running",
            "session_id": session_id,
            "progress_percentage": 25,
            "message": "Ejecutando pytest..."
        })
        
        # Ejecutar pytest
        result = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )
        )
        
        await _update_test_progress(session_id, {
            "status": "running",
            "session_id": session_id,
            "progress_percentage": 75,
            "message": "Actualizando cache..."
        })
        
        # Actualizar cache
        await _update_test_cache(result)
        
        await _update_test_progress(session_id, {
            "status": "completed",
            "session_id": session_id,
            "progress_percentage": 100,
            "message": "Pruebas completadas",
            "result": {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error in legacy tests: {e}")
        await _update_test_progress(session_id, {
            "status": "error",
            "session_id": session_id,
            "message": f"Error: {str(e)}",
            "error": str(e)
        })


async def _update_test_cache(pytest_result):
    """Actualiza el cache de resultados de pruebas"""
    try:
        logger.info(f"Updating test cache. Exit code: {pytest_result.returncode}")
        logger.info(f"Stdout length: {len(pytest_result.stdout)}")
        logger.info(f"Stderr: {pytest_result.stderr[:500]}")

        # Parsear la salida de pytest para extraer información
        stdout_lines = pytest_result.stdout.split("\n")

        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        test_details = []

        # Buscar el resumen final de pytest
        summary_line = ""
        for line in stdout_lines:
            if "failed" in line and "passed" in line and "in" in line:
                summary_line = line
                break

        # Parsear el resumen (ej: "1 failed, 36 passed, 1 skipped, 11 warnings in 1.95s")
        if summary_line:
            import re

            failed_match = re.search(r"(\d+) failed", summary_line)
            passed_match = re.search(r"(\d+) passed", summary_line)
            skipped_match = re.search(r"(\d+) skipped", summary_line)

            if failed_match:
                failed_tests = int(failed_match.group(1))
            if passed_match:
                passed_tests = int(passed_match.group(1))
            if skipped_match:
                skipped_tests = int(skipped_match.group(1))

        # Extraer detalles de pruebas individuales
        for line in stdout_lines:
            if "::" in line and (
                "PASSED" in line or "FAILED" in line or "SKIPPED" in line
            ):
                parts = line.split("::")
                if len(parts) >= 2:
                    file_path = parts[0].strip()
                    test_name = parts[1].split(" ")[0]

                    if "PASSED" in line:
                        status = "passed"
                    elif "FAILED" in line:
                        status = "failed"
                    elif "SKIPPED" in line:
                        status = "skipped"
                    else:
                        continue

                    test_details.append(
                        {"name": test_name, "status": status, "file": file_path}
                    )

        total_tests = passed_tests + failed_tests + skipped_tests

        # Categorizar pruebas
        unit_tests = {"passed": 0, "failed": 0, "skipped": 0, "tests": []}
        integration_tests = {"passed": 0, "failed": 0, "skipped": 0, "tests": []}

        for test in test_details:
            if "unit" in test["file"] or "test_" in test["name"]:
                unit_tests[test["status"]] += 1
                unit_tests["tests"].append(test)
            else:
                integration_tests[test["status"]] += 1
                integration_tests["tests"].append(test)

        # Crear estructura de datos para el cache
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "total_tests": total_tests,
            "test_details": test_details,
            "categories": {
                "unit_tests": unit_tests,
                "integration_tests": integration_tests,
            },
            "success": pytest_result.returncode == 0,
        }

        # Guardar en archivo cache
        with open("test_results_cache.json", "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Test cache updated: {total_tests} tests, {passed_tests} passed, {failed_tests} failed"
        )

    except Exception as e:
        logger.error(f"Error updating test cache: {e}")
        # Crear cache básico en caso de error
        basic_cache = {
            "timestamp": datetime.now().isoformat(),
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "total_tests": 0,
            "test_details": [],
            "categories": {
                "unit_tests": {"passed": 0, "failed": 0, "skipped": 0, "tests": []},
                "integration_tests": {
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "tests": [],
                },
            },
            "success": False,
        }

        with open("test_results_cache.json", "w", encoding="utf-8") as f:
            json.dump(basic_cache, f, indent=2, ensure_ascii=False)


@router.post("/run-evaluations")
async def run_evaluations(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Ejecuta las evaluaciones automáticas - OPTIMIZADO con progreso en tiempo real"""
    # Verificar configuración de API antes de ejecutar
    config_check = await check_api_configuration()
    if not config_check["can_run_evaluations"]:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "missing_api_keys",
                "message": "No se pueden ejecutar evaluaciones: falta clave API de Groq",
                "details": config_check["details"]
            }
        )
    
    session_id = f"eval_{int(time.time())}_{os.getpid()}"
    
    # Inicializar progreso
    await _update_evaluation_progress(session_id, {
        "status": "starting",
        "progress_percentage": 0,
        "message": "Iniciando evaluaciones automáticas...",
        "session_id": session_id
    })
    
    if OPTIMIZED_AVAILABLE:
        # Usar versión optimizada
        background_tasks.add_task(_run_optimized_evaluations_background, session_id)
        return {
            "status": "started",
            "session_id": session_id,
            "message": "Evaluaciones iniciadas en segundo plano con progreso optimizado",
            "progress_endpoint": f"/api/results/evaluation-progress/{session_id}",
            "timestamp": datetime.now().isoformat(),
        }
    else:
        # Fallback a versión original
        background_tasks.add_task(_run_legacy_evaluations_background, session_id)
        return {
            "status": "started",
            "session_id": session_id,
            "message": "Evaluaciones iniciadas en segundo plano (modo legacy)",
            "progress_endpoint": f"/api/results/evaluation-progress/{session_id}",
            "timestamp": datetime.now().isoformat(),
        }


async def _run_optimized_evaluations_background(session_id: str):
    """Ejecuta evaluaciones optimizadas en segundo plano"""
    try:
        # Configurar callback de progreso thread-safe
        def progress_callback(progress_info):
            try:
                loop = asyncio.get_running_loop()
                asyncio.run_coroutine_threadsafe(
                    _update_evaluation_progress(session_id, {
                        "status": "running",
                        "session_id": session_id,
                        **progress_info
                    }),
                    loop
                )
            except RuntimeError:
                # No hay loop activo, actualizar directamente el progreso
                _evaluation_progress[session_id] = {
                    "status": "running",
                    "session_id": session_id,
                    **progress_info
                }
        
        # Crear instancia de evaluación optimizada
        evaluacion = EvaluacionAutomatica(
            max_concurrent_requests=5,
            enable_cache=True
        )
        evaluacion.set_progress_callback(progress_callback)
        
        # Ejecutar evaluaciones
        resultado = await evaluacion.ejecutar_evaluacion_completa("groq")
        
        # Actualizar progreso final
        await _update_evaluation_progress(session_id, {
            "status": "completed",
            "session_id": session_id,
            "progress_percentage": 100,
            "message": "Evaluaciones completadas exitosamente",
            "result": resultado,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Error in optimized evaluations: {e}")
        await _update_evaluation_progress(session_id, {
            "status": "error",
            "session_id": session_id,
            "message": f"Error: {str(e)}",
            "error": str(e)
        })


async def _run_legacy_evaluations_background(session_id: str):
    """Ejecuta evaluaciones en modo legacy en segundo plano"""
    try:
        await _update_evaluation_progress(session_id, {
            "status": "running",
            "session_id": session_id,
            "progress_percentage": 50,
            "message": "Ejecutando script de evaluación..."
        })
        
        # Ejecutar script original
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: subprocess.run(
                ["python", "scripts/evaluacion_automatica.py"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )
        )
        
        await _update_evaluation_progress(session_id, {
            "status": "completed",
            "session_id": session_id,
            "progress_percentage": 100,
            "message": "Evaluaciones completadas",
            "result": {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error in legacy evaluations: {e}")
        await _update_evaluation_progress(session_id, {
            "status": "error",
            "session_id": session_id,
            "message": f"Error: {str(e)}",
            "error": str(e)
        })


@router.get("/test-status")
async def get_test_status() -> Dict[str, Any]:
    """Obtiene el estado actual de las pruebas"""
    try:
        cache_file = Path("test_results_cache.json")
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "status": "available",
                    "last_run": datetime.fromtimestamp(
                        cache_file.stat().st_mtime
                    ).isoformat(),
                    "data": data,
                }
        else:
            return {
                "status": "no_data",
                "message": "No hay datos de pruebas disponibles",
            }

    except Exception as e:
        logger.error(f"Error getting test status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata")
async def get_results_metadata(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Elementos por página")
) -> Dict[str, Any]:
    """Obtiene metadatos de resultados con paginación"""
    try:
        results_dir = Path("resultados")
        if not results_dir.exists():
            return {
                "metadata": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "total_pages": 0
            }
        
        # Obtener archivos JSON
        json_files = list(results_dir.glob("*.json"))
        json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        total = len(json_files)
        total_pages = (total + limit - 1) // limit
        
        # Calcular offset
        offset = (page - 1) * limit
        page_files = json_files[offset:offset + limit]
        
        # Generar metadatos
        metadata = []
        for file_path in page_files:
            try:
                stat = file_path.stat()
                # Leer solo las primeras líneas para obtener metadatos básicos
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read(500)  # Solo primeros 500 caracteres
                    try:
                        partial_data = json.loads(content + "}" if not content.endswith("}") else content)
                    except:
                        partial_data = {}
                
                metadata.append({
                    "id": file_path.stem,
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "type": "evaluation" if "evaluacion" in file_path.name else "test",
                    "status": "completed",
                    "summary": {
                        "timestamp": partial_data.get("timestamp", ""),
                        "models": len(partial_data.get("modelos_evaluados", {})),
                        "categories": len(partial_data.get("categorias", {}))
                    }
                })
            except Exception as e:
                logger.warning(f"Error reading metadata for {file_path}: {e}")
                continue
        
        return {
            "metadata": metadata,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
        
    except Exception as e:
        logger.error(f"Error getting results metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{result_id}")
async def get_result_detail(result_id: str) -> Dict[str, Any]:
    """Obtiene el detalle completo de un resultado específico"""
    try:
        results_dir = Path("resultados")
        result_file = results_dir / f"{result_id}.json"
        
        if not result_file.exists():
            raise HTTPException(status_code=404, detail="Resultado no encontrado")
        
        with open(result_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return {
            "id": result_id,
            "data": data,
            "metadata": {
                "size": result_file.stat().st_size,
                "modified": datetime.fromtimestamp(result_file.stat().st_mtime).isoformat()
            }
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")
    except Exception as e:
        logger.error(f"Error getting result detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config-check")
async def check_api_configuration() -> Dict[str, Any]:
    """Verifica la configuración de las claves API"""
    try:
        from servidor.config.settings import get_settings
        settings = get_settings()
        
        # Verificar claves API necesarias
        config_status = {
            "groq_api_key": bool(getattr(settings, 'GROQ_API_KEY', None)),
            "openai_api_key": bool(getattr(settings, 'OPENAI_API_KEY', None)),
            "anthropic_api_key": bool(getattr(settings, 'ANTHROPIC_API_KEY', None))
        }
        
        # Determinar si hay al menos una clave configurada
        has_any_key = any(config_status.values())
        
        return {
            "status": "ready" if has_any_key else "missing_keys",
            "message": "Configuración lista" if has_any_key else "Faltan claves API",
            "details": config_status,
            "can_run_tests": has_any_key,
            "can_run_evaluations": config_status.get("groq_api_key", False)
        }
        
    except Exception as e:
        logger.error(f"Error checking API configuration: {e}")
        return {
            "status": "error",
            "message": f"Error verificando configuración: {str(e)}",
            "details": {},
            "can_run_tests": False,
            "can_run_evaluations": False
        }
