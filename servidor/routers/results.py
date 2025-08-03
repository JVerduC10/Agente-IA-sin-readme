from datetime import datetime
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import json
import os
import subprocess
import asyncio
import logging
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/results", tags=["results"])

# Directorio donde se guardan los resultados
RESULTS_DIR = Path("resultados")


@router.get("/list")
async def list_results() -> Dict[str, Any]:
    """Lista todos los archivos de resultados disponibles."""
    try:
        if not RESULTS_DIR.exists():
            return {"files": [], "count": 0}
        
        files = []
        for file_path in RESULTS_DIR.glob("*.json"):
            stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "url": f"/results/file/{file_path.name}"
            })
        
        # Ordenar por fecha de modificación (más reciente primero)
        files.sort(key=lambda x: x["modified"], reverse=True)
        
        return {
            "files": files,
            "count": len(files),
            "latest": files[0] if files else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing results: {str(e)}")


@router.get("/file/{filename}")
async def get_result_file(filename: str) -> JSONResponse:
    """Obtiene un archivo de resultados específico en formato JSON."""
    try:
        file_path = RESULTS_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not file_path.suffix == ".json":
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return JSONResponse(content=data)
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@router.get("/file/{filename}/download")
async def download_result_file(filename: str) -> FileResponse:
    """Descarga un archivo de resultados como archivo de texto."""
    try:
        file_path = RESULTS_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not file_path.suffix == ".json":
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/json"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")


@router.get("/latest")
async def get_latest_result() -> JSONResponse:
    """Obtiene el resultado más reciente."""
    try:
        logger.info("[DEBUG] Endpoint /latest llamado")
        
        if not RESULTS_DIR.exists():
            logger.error(f"[DEBUG] Directorio de resultados no existe: {RESULTS_DIR}")
            raise HTTPException(status_code=404, detail="No results directory found")
        
        json_files = list(RESULTS_DIR.glob("*.json"))
        logger.info(f"[DEBUG] Archivos JSON encontrados: {len(json_files)}")
        
        if not json_files:
            logger.error("[DEBUG] No se encontraron archivos JSON")
            raise HTTPException(status_code=404, detail="No result files found")
        
        # Encontrar el archivo más reciente
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"[DEBUG] Archivo más reciente: {latest_file}")
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"[DEBUG] Archivo JSON leído correctamente")
        except UnicodeDecodeError as e:
            logger.error(f"[DEBUG] Error de codificación Unicode: {e}")
            # Intentar con diferentes codificaciones
            try:
                with open(latest_file, 'r', encoding='latin-1') as f:
                    data = json.load(f)
                logger.info(f"[DEBUG] Archivo leído con codificación latin-1")
            except Exception as e2:
                logger.error(f"[DEBUG] Error al leer con latin-1: {e2}")
                raise HTTPException(status_code=500, detail=f"Error de codificación en archivo: {str(e)}")
        
        return JSONResponse(content={
            "filename": latest_file.name,
            "data": data,
            "timestamp": datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat()
        })
    
    except json.JSONDecodeError as e:
        logger.error(f"[DEBUG] Error JSON: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DEBUG] Error inesperado en /latest: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading latest result: {str(e)}")


@router.get("/summary")
async def get_results_summary() -> Dict[str, Any]:
    """Obtiene un resumen de todos los resultados."""
    try:
        if not RESULTS_DIR.exists():
            return {"total_files": 0, "summary": []}
        
        json_files = list(RESULTS_DIR.glob("*.json"))
        if not json_files:
            return {"total_files": 0, "summary": []}
        
        summary = []
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extraer información clave del resultado
                file_summary = {
                    "filename": file_path.name,
                    "timestamp": data.get("timestamp", ""),
                    "evaluation_id": data.get("evaluacion_id", ""),
                    "models_evaluated": list(data.get("modelos_evaluados", {}).keys()),
                    "global_stats": data.get("estadisticas_globales", {})
                }
                
                # Agregar ranking si existe
                if "comparacion" in data and "ranking" in data["comparacion"]:
                    file_summary["ranking"] = data["comparacion"]["ranking"]
                
                summary.append(file_summary)
            
            except (json.JSONDecodeError, KeyError):
                # Saltar archivos con formato incorrecto
                continue
        
        # Ordenar por timestamp
        summary.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "total_files": len(summary),
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@router.post("/test-endpoint")
async def test_endpoint() -> Dict[str, Any]:
    """Endpoint de prueba simple."""
    logger.info("[DEBUG] Test endpoint llamado exitosamente")
    return {"success": True, "message": "Test endpoint funcionando"}

@router.get("/test-status")
async def get_test_status() -> Dict[str, Any]:
    """Obtiene el estado actual de los tests sin ejecutarlos."""
    try:
        # Leer resultados desde archivo cache si existe
        cache_file = Path.cwd() / "test_results_cache.json"
        
        if cache_file.exists():
            import json
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            return {
                "status": "ready",
                "running": False,
                "last_run": cached_data.get("timestamp"),
                "passed_tests": cached_data.get("passed_tests", 0),
                "failed_tests": cached_data.get("failed_tests", 0),
                "skipped_tests": cached_data.get("skipped_tests", 0),
                "total_tests": cached_data.get("total_tests", 0),
                "test_details": cached_data.get("test_details", []),
                "categories": cached_data.get("categories", {"unit_tests": {"passed": 0, "failed": 0, "skipped": 0, "tests": []}, "integration_tests": {"passed": 0, "failed": 0, "skipped": 0, "tests": []}}),
                "message": "Resultados de tests disponibles"
            }
        else:
            return {
                "status": "ready",
                "running": False,
                "last_run": None,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "total_tests": 0,
                "test_details": [],
                "categories": {"unit_tests": {"passed": 0, "failed": 0, "skipped": 0, "tests": []}, "integration_tests": {"passed": 0, "failed": 0, "skipped": 0, "tests": []}},
                "message": "No hay resultados de tests disponibles. Ejecuta los tests primero."
            }
    except Exception as e:
        logger.error(f"Error getting test status: {str(e)}")
        return {
            "status": "error",
            "running": False,
            "last_run": None,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "total_tests": 0,
            "test_details": [],
            "categories": {"unit_tests": {"passed": 0, "failed": 0, "skipped": 0, "tests": []}, "integration_tests": {"passed": 0, "failed": 0, "skipped": 0, "tests": []}},
            "message": f"Error: {str(e)}"
        }

@router.post("/run-tests")
async def run_tests() -> Dict[str, Any]:
    """Ejecuta todos los tests del sistema."""
    print("[DEBUG] Endpoint run_tests llamado - INICIO")
    
    try:
        print("[DEBUG] Dentro del try block")
        print("[DEBUG] Iniciando ejecución real de tests...")
        
        # Verificar que el archivo existe
        test_file = Path.cwd() / "run_all_tests.py"
        print(f"[DEBUG] Verificando archivo: {test_file}, existe: {test_file.exists()}")
        
        if not test_file.exists():
            return {
                "success": False,
                "error": "Archivo run_all_tests.py no encontrado",
                "output": "Error: No se encontró el archivo run_all_tests.py",
                "timestamp": datetime.now().isoformat()
            }
        
        # Ejecutar pytest directamente para obtener resultados precisos
        print("[DEBUG] Ejecutando tests con pytest directamente...")
        import subprocess
        
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        print(f"[DEBUG] Código de salida: {result.returncode}")
        print(f"[DEBUG] Longitud de salida: {len(result.stdout)}")
        print(f"[DEBUG] Primeros 200 chars de salida: {result.stdout[:200]}")
        print(f"[DEBUG] Error output: {result.stderr[:200]}..." if result.stderr else "[DEBUG] Sin errores en stderr")
        
        success = result.returncode == 0
        
        # Procesar la salida para extraer información de tests
        test_data = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "test_details": [],
            "categories": {
                "unit_tests": {"passed": 0, "failed": 0, "skipped": 0, "tests": []},
                "integration_tests": {"passed": 0, "failed": 0, "skipped": 0, "tests": []}
            }
        }
        
        if result.stdout:
            lines = result.stdout.split('\n')
            
            # Buscar el resumen final de pytest
            for line in lines:
                if 'passed' in line and ('skipped' in line or 'warnings' in line) and '=' in line:
                    # Línea como: "56 passed, 4 skipped, 22 warnings in 2.27s"
                    import re
                    passed_match = re.search(r'(\d+)\s+passed', line)
                    failed_match = re.search(r'(\d+)\s+failed', line)
                    skipped_match = re.search(r'(\d+)\s+skipped', line)
                    
                    if passed_match:
                        test_data["passed_tests"] = int(passed_match.group(1))
                    if failed_match:
                        test_data["failed_tests"] = int(failed_match.group(1))
                    if skipped_match:
                        test_data["skipped_tests"] = int(skipped_match.group(1))
                    
                    test_data["total_tests"] = test_data["passed_tests"] + test_data["failed_tests"] + test_data["skipped_tests"]
                    break
            
            # Procesar tests individuales para categorización
            for line in lines:
                if '::' in line and ('PASSED' in line or 'FAILED' in line or 'SKIPPED' in line):
                    parts = line.split('::')
                    if len(parts) >= 2:
                        full_path = parts[0]
                        test_name = parts[-1].split()[0]
                        
                        # Determinar status
                        if 'PASSED' in line:
                            status = 'PASSED'
                        elif 'FAILED' in line:
                            status = 'FAILED'
                        elif 'SKIPPED' in line:
                            status = 'SKIPPED'
                        else:
                            continue
                        
                        # Categorizar por tipo de test
                        category = "unit_tests" if "tests/unit/" in full_path else "integration_tests"
                        
                        test_detail = {
                            "name": test_name,
                            "full_name": line.split()[0],
                            "category": category,
                            "status": status,
                            "passed": status == 'PASSED'
                        }
                        
                        test_data["test_details"].append(test_detail)
                        test_data["categories"][category]["tests"].append(test_detail)
                        
                        # Actualizar contadores por categoría
                        if status == 'PASSED':
                            test_data["categories"][category]["passed"] += 1
                        elif status == 'FAILED':
                            test_data["categories"][category]["failed"] += 1
                        elif status == 'SKIPPED':
                            test_data["categories"][category]["skipped"] += 1
        
        # Limitar el tamaño de la salida para evitar problemas en el navegador
        output_truncated = result.stdout[:10000] if result.stdout else ""
        if len(result.stdout or "") > 10000:
            output_truncated += "\n\n... (salida truncada por tamaño)"
        
        stderr_truncated = result.stderr[:5000] if result.stderr else ""
        if len(result.stderr or "") > 5000:
            stderr_truncated += "\n\n... (error truncado por tamaño)"
        
        # Guardar resultados en cache para test-status
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "passed_tests": test_data["passed_tests"],
            "failed_tests": test_data["failed_tests"],
            "skipped_tests": test_data["skipped_tests"],
            "total_tests": test_data["total_tests"],
            "test_details": test_data["test_details"][:50] if test_data["test_details"] else [],
            "categories": test_data["categories"],
            "success": success
        }
        
        try:
            import json
            cache_file = Path.cwd() / "test_results_cache.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as cache_error:
            logger.error(f"Error saving test cache: {cache_error}")
        
        return {
            "success": success,
            "output": output_truncated,
            "stderr": stderr_truncated,
            "return_code": result.returncode,
            "total_tests": test_data["total_tests"],
            "passed_tests": test_data["passed_tests"],
            "failed_tests": test_data["failed_tests"],
            "skipped_tests": test_data["skipped_tests"],
            "test_details": test_data["test_details"][:50] if test_data["test_details"] else [],
            "categories": test_data["categories"],
            "execution_time": "N/A",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"[ERROR] Excepción en run_tests: {str(e)}")
        import traceback
        print("[ERROR] Traceback completo:")
        print(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "output": f"Error ejecutando tests: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@router.post("/run-evaluations")
async def run_evaluations() -> Dict[str, Any]:
    """Ejecuta las evaluaciones automáticas del sistema."""
    try:
        start_time = datetime.now()
        
        # Ejecutar el script de evaluaciones
        process = await asyncio.create_subprocess_exec(
            "python", "tests/evaluacion_automatica.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=Path.cwd()
        )
        
        stdout, _ = await process.communicate()
        output = stdout.decode('utf-8', errors='replace')
        
        end_time = datetime.now()
        execution_time = str(end_time - start_time)
        
        success = process.returncode == 0
        
        # Intentar cargar el último archivo de evaluación generado
        evaluation_data = None
        try:
            if RESULTS_DIR.exists():
                json_files = list(RESULTS_DIR.glob("evaluacion_automatica_*.json"))
                if json_files:
                    # Obtener el archivo más reciente
                    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        evaluation_data = json.load(f)
        except Exception:
            pass
        
        # Contar evaluaciones exitosas y fallidas
        total_evaluations = 0
        successful_evaluations = 0
        failed_evaluations = 0
        
        if evaluation_data and 'resultados_por_modelo' in evaluation_data:
            for modelo_data in evaluation_data['resultados_por_modelo'].values():
                if isinstance(modelo_data, dict) and 'resultados' in modelo_data:
                    for resultado in modelo_data['resultados']:
                        total_evaluations += 1
                        if resultado.get('exito', False):
                            successful_evaluations += 1
                        else:
                            failed_evaluations += 1
        
        return {
            "success": success,
            "total_evaluations": total_evaluations,
            "successful_evaluations": successful_evaluations,
            "failed_evaluations": failed_evaluations,
            "execution_time": execution_time,
            "output": output,
            "evaluation_data": evaluation_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "output": f"Error ejecutando evaluaciones: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }