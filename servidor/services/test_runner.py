"""Test runner optimizado con paralelización y visualización de progreso."""

import asyncio
import concurrent.futures
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from servidor.core.progress_tracker import ProgressTracker, ProgressStatus

logger = logging.getLogger(__name__)


class OptimizedTestRunner:
    """Runner de tests optimizado con paralelización y progreso visual."""
    
    def __init__(self, test_directory: str = "tests", max_workers: int = None):
        self.test_directory = Path(test_directory)
        self.max_workers = max_workers or min(4, os.cpu_count() or 1)
        self.session_id: Optional[str] = None
        self.progress_tracker: Optional[ProgressTracker] = None
    
    async def run_all_tests(
        self, 
        session_id: str,
        progress_callback: Optional[Callable] = None,
        parallel: bool = True,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """Ejecuta todos los tests con visualización de progreso."""
        self.session_id = session_id
        start_time = time.time()
        
        try:
            # Descubrir archivos de test
            test_files = self._discover_test_files()
            
            # Inicializar tracker de progreso
            self.progress_tracker = ProgressTracker(
                session_id=session_id,
                total=len(test_files),
                description="Ejecutando tests",
                use_tqdm=True
            )
            
            if progress_callback:
                self.progress_tracker.add_callback(progress_callback)
            
            self.progress_tracker.start()
            
            # Ejecutar tests
            if parallel and len(test_files) > 1:
                results = await self._run_tests_parallel(test_files, verbose)
            else:
                results = await self._run_tests_sequential(test_files, verbose)
            
            # Compilar resultados finales
            final_result = self._compile_results(results, start_time)
            
            self.progress_tracker.complete("Tests completados exitosamente")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error ejecutando tests: {e}")
            if self.progress_tracker:
                self.progress_tracker.error(str(e))
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def _discover_test_files(self) -> List[Path]:
        """Descubre archivos de test en el directorio."""
        test_files = []
        
        if self.test_directory.exists():
            # Buscar archivos test_*.py
            test_files.extend(self.test_directory.glob("test_*.py"))
            # Buscar archivos *_test.py
            test_files.extend(self.test_directory.glob("*_test.py"))
        
        # Filtrar archivos válidos y ordenar
        valid_files = [
            f for f in test_files 
            if f.is_file() and not f.name.startswith('.')
        ]
        
        return sorted(valid_files)
    
    async def _run_tests_parallel(self, test_files: List[Path], verbose: bool) -> List[Dict[str, Any]]:
        """Ejecuta tests en paralelo usando ThreadPoolExecutor."""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Crear tareas para cada archivo de test
            future_to_file = {
                executor.submit(self._run_single_test_file, test_file, verbose): test_file
                for test_file in test_files
            }
            
            # Procesar resultados conforme se completan
            for future in concurrent.futures.as_completed(future_to_file):
                test_file = future_to_file[future]
                try:
                    result = future.result()
                    result['file'] = str(test_file)
                    results.append(result)
                    
                    # Actualizar progreso
                    if self.progress_tracker:
                        self.progress_tracker.update(
                            1, 
                            f"Completado: {test_file.name}",
                            completed_file=str(test_file)
                        )
                    
                except Exception as e:
                    logger.error(f"Error ejecutando {test_file}: {e}")
                    results.append({
                        'file': str(test_file),
                        'success': False,
                        'error': str(e),
                        'execution_time': 0
                    })
                    
                    if self.progress_tracker:
                        self.progress_tracker.update(
                            1, 
                            f"Error en: {test_file.name}",
                            error_file=str(test_file)
                        )
        
        return results
    
    async def _run_tests_sequential(self, test_files: List[Path], verbose: bool) -> List[Dict[str, Any]]:
        """Ejecuta tests secuencialmente."""
        results = []
        
        for i, test_file in enumerate(test_files, 1):
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, self._run_single_test_file, test_file, verbose
                )
                result['file'] = str(test_file)
                results.append(result)
                
                # Actualizar progreso
                if self.progress_tracker:
                    self.progress_tracker.set_progress(
                        i, 
                        f"Completado: {test_file.name} ({i}/{len(test_files)})",
                        completed_file=str(test_file)
                    )
                
            except Exception as e:
                logger.error(f"Error ejecutando {test_file}: {e}")
                results.append({
                    'file': str(test_file),
                    'success': False,
                    'error': str(e),
                    'execution_time': 0
                })
                
                if self.progress_tracker:
                    self.progress_tracker.set_progress(
                        i, 
                        f"Error en: {test_file.name} ({i}/{len(test_files)})",
                        error_file=str(test_file)
                    )
        
        return results
    
    def _run_single_test_file(self, test_file: Path, verbose: bool) -> Dict[str, Any]:
        """Ejecuta un archivo de test individual."""
        start_time = time.time()
        
        try:
            cmd = [
                "python", "-m", "pytest", 
                str(test_file),
                "-v" if verbose else "-q",
                "--tb=short",
                "--no-header",
                "--disable-warnings"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                timeout=300  # 5 minutos timeout por archivo
            )
            
            execution_time = time.time() - start_time
            
            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Test timeout (5 minutos)',
                'execution_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
    
    def _compile_results(self, results: List[Dict[str, Any]], start_time: float) -> Dict[str, Any]:
        """Compila los resultados finales."""
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get('success', False))
        failed_tests = total_tests - successful_tests
        total_execution_time = time.time() - start_time
        
        # Extraer estadísticas detalladas del stdout
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_warnings = 0
        
        for result in results:
            stdout = result.get('stdout', '')
            # Parsear salida de pytest para estadísticas
            if 'passed' in stdout:
                # Buscar patrones como "5 passed, 2 skipped"
                import re
                passed_match = re.search(r'(\d+) passed', stdout)
                if passed_match:
                    total_passed += int(passed_match.group(1))
                
                failed_match = re.search(r'(\d+) failed', stdout)
                if failed_match:
                    total_failed += int(failed_match.group(1))
                
                skipped_match = re.search(r'(\d+) skipped', stdout)
                if skipped_match:
                    total_skipped += int(skipped_match.group(1))
                
                warnings_match = re.search(r'(\d+) warnings?', stdout)
                if warnings_match:
                    total_warnings += int(warnings_match.group(1))
        
        return {
            'success': failed_tests == 0,
            'summary': {
                'total_test_files': total_tests,
                'successful_files': successful_tests,
                'failed_files': failed_tests,
                'total_passed': total_passed,
                'total_failed': total_failed,
                'total_skipped': total_skipped,
                'total_warnings': total_warnings
            },
            'execution_time': total_execution_time,
            'average_time_per_file': total_execution_time / total_tests if total_tests > 0 else 0,
            'timestamp': datetime.now().isoformat(),
            'detailed_results': results,
            'session_id': self.session_id
        }


# Función de conveniencia para uso directo
async def run_optimized_tests(
    session_id: str,
    test_directory: str = "tests",
    progress_callback: Optional[Callable] = None,
    parallel: bool = True,
    max_workers: int = None
) -> Dict[str, Any]:
    """Función de conveniencia para ejecutar tests optimizados."""
    runner = OptimizedTestRunner(test_directory, max_workers)
    return await runner.run_all_tests(session_id, progress_callback, parallel)