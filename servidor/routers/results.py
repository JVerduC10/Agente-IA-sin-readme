import logging
import os
import json
import subprocess
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/results", tags=["results"])


class TestResult(BaseModel):
    title: str
    timestamp: str
    status: str
    details: Dict[str, Any]


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
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        results.append({
                            "title": f"Evaluación - {file_path.stem}",
                            "timestamp": data.get("timestamp", file_path.stat().st_mtime),
                            "file": str(file_path),
                            "data": data
                        })
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")
        
        # Buscar archivos de cache de pruebas
        cache_file = Path("test_results_cache.json")
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results.append({
                        "title": "Cache de Pruebas",
                        "timestamp": datetime.fromtimestamp(cache_file.stat().st_mtime).isoformat(),
                        "file": str(cache_file),
                        "data": data
                    })
            except Exception as e:
                logger.error(f"Error reading cache file: {e}")
        
        # Ordenar por timestamp (más reciente primero)
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return results
        
    except Exception as e:
        logger.error(f"Error listing results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-tests")
async def run_tests() -> Dict[str, Any]:
    """Ejecuta las pruebas del sistema"""
    try:
        # Ejecutar pytest
        result = subprocess.run(
            ["python", "-m", "pytest", "pruebas/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        # Procesar resultados y actualizar cache
        await _update_test_cache(result)
        
        return {
            "status": "completed",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _update_test_cache(pytest_result):
    """Actualiza el cache de resultados de pruebas"""
    try:
        logger.info(f"Updating test cache. Exit code: {pytest_result.returncode}")
        logger.info(f"Stdout length: {len(pytest_result.stdout)}")
        logger.info(f"Stderr: {pytest_result.stderr[:500]}")
        
        # Parsear la salida de pytest para extraer información
        stdout_lines = pytest_result.stdout.split('\n')
        
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
            failed_match = re.search(r'(\d+) failed', summary_line)
            passed_match = re.search(r'(\d+) passed', summary_line)
            skipped_match = re.search(r'(\d+) skipped', summary_line)
            
            if failed_match:
                failed_tests = int(failed_match.group(1))
            if passed_match:
                passed_tests = int(passed_match.group(1))
            if skipped_match:
                skipped_tests = int(skipped_match.group(1))
        
        # Extraer detalles de pruebas individuales
        for line in stdout_lines:
            if '::' in line and ('PASSED' in line or 'FAILED' in line or 'SKIPPED' in line):
                parts = line.split('::')
                if len(parts) >= 2:
                    file_path = parts[0].strip()
                    test_name = parts[1].split(' ')[0]
                    
                    if 'PASSED' in line:
                        status = 'passed'
                    elif 'FAILED' in line:
                        status = 'failed'
                    elif 'SKIPPED' in line:
                        status = 'skipped'
                    else:
                        continue
                        
                    test_details.append({
                        'name': test_name,
                        'status': status,
                        'file': file_path
                    })
        
        total_tests = passed_tests + failed_tests + skipped_tests
        
        # Categorizar pruebas
        unit_tests = {'passed': 0, 'failed': 0, 'skipped': 0, 'tests': []}
        integration_tests = {'passed': 0, 'failed': 0, 'skipped': 0, 'tests': []}
        
        for test in test_details:
            if 'unit' in test['file'] or 'test_' in test['name']:
                unit_tests[test['status']] += 1
                unit_tests['tests'].append(test)
            else:
                integration_tests[test['status']] += 1
                integration_tests['tests'].append(test)
        
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
                "integration_tests": integration_tests
            },
            "success": pytest_result.returncode == 0
        }
        
        # Guardar en archivo cache
        with open('test_results_cache.json', 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Test cache updated: {total_tests} tests, {passed_tests} passed, {failed_tests} failed")
        
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
                "integration_tests": {"passed": 0, "failed": 0, "skipped": 0, "tests": []}
            },
            "success": False
        }
        
        with open('test_results_cache.json', 'w', encoding='utf-8') as f:
            json.dump(basic_cache, f, indent=2, ensure_ascii=False)


@router.post("/run-evaluations")
async def run_evaluations() -> Dict[str, Any]:
    """Ejecuta las evaluaciones automáticas del sistema"""
    try:
        # Ejecutar script de evaluación automática
        result = subprocess.run(
            ["python", "scripts/evaluacion_automatica.py"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        return {
            "status": "completed",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error running evaluations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-status")
async def get_test_status() -> Dict[str, Any]:
    """Obtiene el estado actual de las pruebas"""
    try:
        cache_file = Path("test_results_cache.json")
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    "status": "available",
                    "last_run": datetime.fromtimestamp(cache_file.stat().st_mtime).isoformat(),
                    "data": data
                }
        else:
            return {
                "status": "no_data",
                "message": "No hay datos de pruebas disponibles"
            }
            
    except Exception as e:
        logger.error(f"Error getting test status: {e}")
        raise HTTPException(status_code=500, detail=str(e))