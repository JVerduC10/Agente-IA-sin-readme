#!/usr/bin/env python3
"""
Sistema de Evaluación Automática de Modelos - OPTIMIZADO
Genera prompts automáticamente y evalúa las respuestas de los modelos disponibles.
Incluye progreso en tiempo real, paralelización y optimizaciones de rendimiento.
"""

import asyncio
import json
import logging
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List

from tqdm.asyncio import tqdm

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from servidor.clients.groq.manager import ModelManager
from servidor.config.settings import Settings
from servidor.usage import DailyTokenCounter

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Cache para resultados de evaluación
_evaluation_cache = {}
_cache_lock = threading.Lock()


class EvaluacionAutomatica:
    """Sistema de evaluación automática de modelos - OPTIMIZADO"""

    def __init__(self, max_concurrent_requests: int = 3, enable_cache: bool = True):
        self.settings = Settings()
        self.token_counter = DailyTokenCounter()
        self.model_manager = ModelManager()
        self.max_concurrent_requests = max_concurrent_requests
        self.enable_cache = enable_cache
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.progress_callback = None
        self.start_time = None
        self.total_prompts = 0
        self.completed_prompts = 0

        # Prompts de evaluación categorizados
        self.prompts_evaluacion = {
            "creatividad": [
                "Escribe un cuento corto sobre un robot que descubre emociones",
                "Inventa una receta de cocina con ingredientes imposibles",
                "Describe un día en la vida de una nube",
            ],
            "razonamiento": [
                "Si un tren sale de Madrid a las 10:00 AM a 120 km/h y otro de Barcelona a las 11:00 AM a 100 km/h, ¿cuándo se encuentran?",
                "Explica por qué el agua hierve a diferentes temperaturas según la altitud",
                "¿Cuál es la diferencia entre correlación y causalidad?",
            ],
            "conocimiento": [
                "¿Quién escribió 'Cien años de soledad' y en qué año?",
                "Explica qué es la fotosíntesis en términos simples",
                "¿Cuáles son los planetas del sistema solar en orden?",
            ],
            "programacion": [
                "Escribe una función en Python que calcule el factorial de un número",
                "Explica qué es la programación orientada a objetos",
                "¿Cuál es la diferencia entre una lista y un diccionario en Python?",
            ],
        }

    def set_progress_callback(self, callback):
        """Establece una función callback para reportar progreso"""
        self.progress_callback = callback

    def _update_progress(self, message: str = ""):
        """Actualiza el progreso y llama al callback si está definido"""
        self.completed_prompts += 1
        if self.progress_callback and self.total_prompts > 0:
            progress_percent = (self.completed_prompts / self.total_prompts) * 100
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            estimated_total = (
                (elapsed_time / self.completed_prompts) * self.total_prompts
                if self.completed_prompts > 0
                else 0
            )
            remaining_time = estimated_total - elapsed_time

            self.progress_callback(
                {
                    "completed": self.completed_prompts,
                    "total": self.total_prompts,
                    "percent": progress_percent,
                    "elapsed_time": elapsed_time,
                    "remaining_time": max(0, remaining_time),
                    "message": message,
                }
            )

    @lru_cache(maxsize=128)
    def _get_cache_key(self, prompt: str, categoria: str) -> str:
        """Genera una clave de cache para un prompt y categoría"""
        return f"{hash(prompt)}_{categoria}"

    def evaluar_respuesta(
        self, prompt: str, respuesta: str, categoria: str
    ) -> Dict[str, Any]:
        """Evalúa una respuesta según criterios específicos"""

        # Criterios de evaluación básicos
        criterios = {
            "longitud_adecuada": 50 <= len(respuesta) <= 1000,
            "contiene_informacion": len(respuesta.split()) > 10,
            "no_es_error": "error" not in respuesta.lower()
            and "lo siento" not in respuesta.lower(),
            "relevante": any(
                palabra in respuesta.lower() for palabra in prompt.lower().split()[:3]
            ),
        }

        # Criterios específicos por categoría
        if categoria == "creatividad":
            criterios["es_creativo"] = any(
                palabra in respuesta.lower()
                for palabra in [
                    "imaginó",
                    "fantástico",
                    "mágico",
                    "increíble",
                    "sorprendente",
                ]
            )
        elif categoria == "razonamiento":
            criterios["tiene_logica"] = any(
                palabra in respuesta.lower()
                for palabra in [
                    "porque",
                    "debido",
                    "por tanto",
                    "entonces",
                    "resultado",
                ]
            )
        elif categoria == "conocimiento":
            criterios["es_factual"] = (
                len([palabra for palabra in respuesta.split() if palabra.istitle()]) > 0
            )
        elif categoria == "programacion":
            criterios["tiene_codigo"] = (
                "def " in respuesta or "class " in respuesta or "import " in respuesta
            )

        # Calcular puntuación
        puntuacion = sum(criterios.values()) / len(criterios) * 100

        return {
            "puntuacion": puntuacion,
            "criterios": criterios,
            "longitud_respuesta": len(respuesta),
            "tiempo_evaluacion": datetime.now().isoformat(),
        }

    async def _evaluar_prompt_individual(
        self,
        prompt: str,
        categoria: str,
        prompt_index: int,
        total_prompts_categoria: int,
    ) -> Dict[str, Any]:
        """Evalúa un prompt individual con control de concurrencia"""
        async with self.semaphore:
            try:
                # Verificar cache si está habilitado
                cache_key = (
                    self._get_cache_key(prompt, categoria)
                    if self.enable_cache
                    else None
                )
                if cache_key and cache_key in _evaluation_cache:
                    with _cache_lock:
                        cached_result = _evaluation_cache[cache_key].copy()
                    self._update_progress(
                        f"Cache hit: {categoria} {prompt_index}/{total_prompts_categoria}"
                    )
                    return cached_result

                # Generar respuesta
                start_time = time.time()
                messages = [{"role": "user", "content": prompt}]
                response = await self.model_manager.chat_completion(
                    messages=messages, temperature=0.7
                )
                respuesta = response["choices"][0]["message"]["content"]
                response_time = time.time() - start_time

                # Evaluar respuesta
                evaluacion = self.evaluar_respuesta(prompt, respuesta, categoria)
                evaluacion["prompt"] = prompt
                evaluacion["respuesta"] = respuesta
                evaluacion["tiempo_respuesta"] = response_time
                evaluacion["prompt_index"] = prompt_index

                # Guardar en cache si está habilitado
                if cache_key and self.enable_cache:
                    with _cache_lock:
                        _evaluation_cache[cache_key] = evaluacion.copy()

                self._update_progress(
                    f"✅ {categoria} {prompt_index}/{total_prompts_categoria}: {evaluacion['puntuacion']:.1f}/100"
                )
                return evaluacion

            except Exception as e:
                error_result = {
                    "prompt": prompt,
                    "error": str(e),
                    "puntuacion": 0,
                    "tiempo_respuesta": 0,
                    "prompt_index": prompt_index,
                }
                self._update_progress(
                    f"❌ Error en {categoria} {prompt_index}/{total_prompts_categoria}: {str(e)[:50]}"
                )
                return error_result

    async def evaluar_modelo(self, provider_name: str = "groq") -> Dict[str, Any]:
        """Evalúa un modelo específico con todos los prompts - OPTIMIZADO con paralelización"""

        logger.info(f"🧪 Evaluando modelo: {provider_name}")

        # Calcular total de prompts para progreso
        self.total_prompts = sum(
            len(prompts) for prompts in self.prompts_evaluacion.values()
        )
        self.completed_prompts = 0
        self.start_time = time.time()

        resultados = {
            "modelo": provider_name,
            "timestamp": datetime.now().isoformat(),
            "categorias": {},
            "resumen": {},
            "configuracion": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "cache_enabled": self.enable_cache,
            },
        }

        total_puntuacion = 0
        total_prompts = 0

        # Procesar cada categoría
        for categoria, prompts in self.prompts_evaluacion.items():
            logger.info(
                f"  📝 Evaluando categoría: {categoria} ({len(prompts)} prompts)"
            )

            # Crear tareas para evaluación paralela
            tasks = [
                self._evaluar_prompt_individual(prompt, categoria, i + 1, len(prompts))
                for i, prompt in enumerate(prompts)
            ]

            # Ejecutar tareas con progreso
            resultados_categoria = await asyncio.gather(*tasks, return_exceptions=True)

            # Procesar resultados y manejar excepciones
            resultados_procesados = []
            for resultado in resultados_categoria:
                if isinstance(resultado, Exception):
                    resultados_procesados.append(
                        {
                            "error": str(resultado),
                            "puntuacion": 0,
                            "tiempo_respuesta": 0,
                        }
                    )
                else:
                    resultados_procesados.append(resultado)
                    total_puntuacion += resultado.get("puntuacion", 0)
                total_prompts += 1

            # Calcular estadísticas de la categoría
            puntuaciones = [r.get("puntuacion", 0) for r in resultados_procesados]
            resultados["categorias"][categoria] = {
                "prompts": resultados_procesados,
                "puntuacion_promedio": (
                    sum(puntuaciones) / len(puntuaciones) if puntuaciones else 0
                ),
                "mejor_puntuacion": max(puntuaciones) if puntuaciones else 0,
                "peor_puntuacion": min(puntuaciones) if puntuaciones else 0,
                "total_prompts": len(prompts),
            }

        # Resumen general
        resultados["resumen"] = {
            "puntuacion_total": (
                total_puntuacion / total_prompts if total_prompts > 0 else 0
            ),
            "prompts_evaluados": total_prompts,
            "prompts_exitosos": sum(
                1
                for cat in resultados["categorias"].values()
                for prompt in cat["prompts"]
                if "error" not in prompt
            ),
            "tiempo_total": time.time() - self.start_time,
            "prompts_por_segundo": (
                total_prompts / (time.time() - self.start_time)
                if self.start_time
                else 0
            ),
        }

        logger.info(
            f"✅ Evaluación completada en {resultados['resumen']['tiempo_total']:.2f}s"
        )
        return resultados

    async def ejecutar_evaluacion_completa(
        self, modelo: str = "groq"
    ) -> Dict[str, Any]:
        """Ejecuta una evaluación completa del modelo especificado - OPTIMIZADO"""

        start_time = time.time()
        logger.info(f"🚀 Iniciando evaluación completa del modelo: {modelo}")

        # Configuración de la evaluación
        config_evaluacion = {
            "modelo": modelo,
            "timestamp_inicio": datetime.now().isoformat(),
            "total_categorias": len(self.prompts_evaluacion),
            "total_prompts": sum(
                len(prompts) for prompts in self.prompts_evaluacion.values()
            ),
            "max_concurrent_requests": self.max_concurrent_requests,
            "cache_enabled": self.enable_cache,
        }

        logger.info(
            f"📊 Configuración: {config_evaluacion['total_prompts']} prompts en {config_evaluacion['total_categorias']} categorías"
        )
        logger.info(f"⚡ Concurrencia máxima: {self.max_concurrent_requests} requests")
        logger.info(f"💾 Cache habilitado: {self.enable_cache}")

        try:
            # Ejecutar evaluación con progreso
            resultados = await self.evaluar_modelo(modelo)

            # Agregar configuración y métricas de rendimiento
            resultados["configuracion_evaluacion"] = config_evaluacion
            resultados["metricas_rendimiento"] = {
                "tiempo_total_segundos": time.time() - start_time,
                "prompts_por_segundo": config_evaluacion["total_prompts"]
                / (time.time() - start_time),
                "cache_hits": (
                    len([k for k in _evaluation_cache.keys() if k])
                    if self.enable_cache
                    else 0
                ),
                "eficiencia_cache": (
                    (len(_evaluation_cache) / config_evaluacion["total_prompts"]) * 100
                    if self.enable_cache and config_evaluacion["total_prompts"] > 0
                    else 0
                ),
            }

            # TODO: Implementar comparación con otros modelos
            # resultados["comparacion"] = await self.comparar_con_otros_modelos(resultados)

            logger.info(
                f"✅ Evaluación completa finalizada en {time.time() - start_time:.2f}s"
            )
            logger.info(
                f"📈 Rendimiento: {resultados['metricas_rendimiento']['prompts_por_segundo']:.2f} prompts/segundo"
            )

            return resultados

        except Exception as e:
            logger.error(f"❌ Error durante la evaluación: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "configuracion_evaluacion": config_evaluacion,
                "tiempo_transcurrido": time.time() - start_time,
            }

    def generar_comparacion(self, resultados_modelos: Dict[str, Any]) -> Dict[str, Any]:
        """Genera comparación entre modelos"""

        comparacion = {"ranking": [], "mejor_por_categoria": {}, "estadisticas": {}}

        # Ranking general
        modelos_validos = {}
        for modelo, datos in resultados_modelos.items():
            if "resumen" in datos and "puntuacion_total" in datos["resumen"]:
                modelos_validos[modelo] = datos["resumen"]["puntuacion_total"]

        ranking = sorted(modelos_validos.items(), key=lambda x: x[1], reverse=True)
        comparacion["ranking"] = [
            {"posicion": i + 1, "modelo": modelo, "puntuacion": puntuacion}
            for i, (modelo, puntuacion) in enumerate(ranking)
        ]

        # Mejor por categoría
        categorias = set()
        for datos in resultados_modelos.values():
            if "categorias" in datos:
                categorias.update(datos["categorias"].keys())

        for categoria in categorias:
            mejor_modelo = None
            mejor_puntuacion = -1

            for modelo, datos in resultados_modelos.items():
                if (
                    "categorias" in datos
                    and categoria in datos["categorias"]
                    and "puntuacion_promedio" in datos["categorias"][categoria]
                ):

                    puntuacion = datos["categorias"][categoria]["puntuacion_promedio"]
                    if puntuacion > mejor_puntuacion:
                        mejor_puntuacion = puntuacion
                        mejor_modelo = modelo

            if mejor_modelo:
                comparacion["mejor_por_categoria"][categoria] = {
                    "modelo": mejor_modelo,
                    "puntuacion": mejor_puntuacion,
                }

        return comparacion

    def guardar_resultados(
        self, resultados: Dict[str, Any], archivo: str = None
    ) -> str:
        """Guarda los resultados en un archivo JSON"""

        if archivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"evaluacion_automatica_{timestamp}.json"

        ruta_completa = os.path.join("resultados", archivo)
        os.makedirs("resultados", exist_ok=True)

        with open(ruta_completa, "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Resultados guardados en: {ruta_completa}")
        return ruta_completa

    def mostrar_resumen(self, resultados: Dict[str, Any]):
        """Muestra un resumen de los resultados"""

        print("\n" + "=" * 60)
        print("📊 RESUMEN DE EVALUACIÓN AUTOMÁTICA")
        print("=" * 60)

        if "error" in resultados:
            print(f"❌ Error: {resultados['error']}")
            return

        # Mostrar ranking
        if "comparacion" in resultados and "ranking" in resultados["comparacion"]:
            print("\n🏆 RANKING DE MODELOS:")
            for item in resultados["comparacion"]["ranking"]:
                print(
                    f"  {item['posicion']}. {item['modelo']}: {item['puntuacion']:.1f}/100"
                )

        # Mostrar mejor por categoría
        if (
            "comparacion" in resultados
            and "mejor_por_categoria" in resultados["comparacion"]
        ):
            print("\n🎯 MEJOR POR CATEGORÍA:")
            for categoria, datos in resultados["comparacion"][
                "mejor_por_categoria"
            ].items():
                print(
                    f"  {categoria}: {datos['modelo']} ({datos['puntuacion']:.1f}/100)"
                )

        # Mostrar estadísticas generales
        print("\n📈 ESTADÍSTICAS:")
        if "resumen" in resultados:
            print(f"  Total de prompts evaluados: {resultados['resumen'].get('prompts_evaluados', 0)}")
            print(f"  Prompts exitosos: {resultados['resumen'].get('prompts_exitosos', 0)}")
            print(f"  Tiempo total: {resultados['resumen'].get('tiempo_total', 0):.2f}s")
            print(f"  Prompts por segundo: {resultados['resumen'].get('prompts_por_segundo', 0):.2f}")
        if "categorias" in resultados:
            print(f"  Categorías evaluadas: {len(resultados['categorias'])}")
        if "modelo" in resultados:
            print(f"  Modelo evaluado: {resultados['modelo']}")
        if "configuracion_evaluacion" in resultados:
            print(f"  Concurrencia máxima: {resultados['configuracion_evaluacion'].get('max_concurrent_requests', 'N/A')}")
            print(f"  Cache habilitado: {resultados['configuracion_evaluacion'].get('cache_enabled', 'N/A')}")


async def main():
    """Función principal"""
    evaluador = EvaluacionAutomatica()

    try:
        # Ejecutar evaluación
        resultados = await evaluador.ejecutar_evaluacion_completa()

        # Guardar resultados
        archivo_resultados = evaluador.guardar_resultados(resultados)

        # Mostrar resumen
        evaluador.mostrar_resumen(resultados)

        print(f"\n✅ Evaluación completada. Resultados en: {archivo_resultados}")

    except Exception as e:
        logger.error(f"❌ Error en evaluación: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
