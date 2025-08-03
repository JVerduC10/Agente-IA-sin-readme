#!/usr/bin/env python3
"""
Sistema de Evaluación Automática de Modelos
Genera prompts automáticamente y evalúa las respuestas de los modelos disponibles.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from servidor.settings import Settings
from servidor.usage import DailyTokenCounter
from herramientas.model_manager import ModelManager, ModelProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvaluacionAutomatica:
    """Sistema de evaluación automática de modelos"""
    
    def __init__(self):
        self.settings = Settings()
        self.token_counter = DailyTokenCounter()
        self.model_manager = ModelManager(self.settings, self.token_counter)
        
        # Prompts de evaluación categorizados
        self.prompts_evaluacion = {
            "creatividad": [
                "Escribe un cuento corto sobre un robot que descubre emociones",
                "Inventa una receta de cocina con ingredientes imposibles",
                "Describe un día en la vida de una nube"
            ],
            "razonamiento": [
                "Si un tren sale de Madrid a las 10:00 AM a 120 km/h y otro de Barcelona a las 11:00 AM a 100 km/h, ¿cuándo se encuentran?",
                "Explica por qué el agua hierve a diferentes temperaturas según la altitud",
                "¿Cuál es la diferencia entre correlación y causalidad?"
            ],
            "conocimiento": [
                "¿Quién escribió 'Cien años de soledad' y en qué año?",
                "Explica qué es la fotosíntesis en términos simples",
                "¿Cuáles son los planetas del sistema solar en orden?"
            ],
            "programacion": [
                "Escribe una función en Python que calcule el factorial de un número",
                "Explica qué es la programación orientada a objetos",
                "¿Cuál es la diferencia entre una lista y un diccionario en Python?"
            ]
        }
    
    def evaluar_respuesta(self, prompt: str, respuesta: str, categoria: str) -> Dict[str, Any]:
        """Evalúa una respuesta según criterios específicos"""
        
        # Criterios de evaluación básicos
        criterios = {
            "longitud_adecuada": 50 <= len(respuesta) <= 1000,
            "contiene_informacion": len(respuesta.split()) > 10,
            "no_es_error": "error" not in respuesta.lower() and "lo siento" not in respuesta.lower(),
            "relevante": any(palabra in respuesta.lower() for palabra in prompt.lower().split()[:3])
        }
        
        # Criterios específicos por categoría
        if categoria == "creatividad":
            criterios["es_creativo"] = any(palabra in respuesta.lower() for palabra in 
                                          ["imaginó", "fantástico", "mágico", "increíble", "sorprendente"])
        elif categoria == "razonamiento":
            criterios["tiene_logica"] = any(palabra in respuesta.lower() for palabra in 
                                           ["porque", "debido", "por tanto", "entonces", "resultado"])
        elif categoria == "conocimiento":
            criterios["es_factual"] = len([palabra for palabra in respuesta.split() if palabra.istitle()]) > 0
        elif categoria == "programacion":
            criterios["tiene_codigo"] = "def " in respuesta or "class " in respuesta or "import " in respuesta
        
        # Calcular puntuación
        puntuacion = sum(criterios.values()) / len(criterios) * 100
        
        return {
            "puntuacion": puntuacion,
            "criterios": criterios,
            "longitud_respuesta": len(respuesta),
            "tiempo_evaluacion": datetime.now().isoformat()
        }
    
    async def evaluar_modelo(self, provider: ModelProvider) -> Dict[str, Any]:
        """Evalúa un modelo específico con todos los prompts"""
        
        logger.info(f"🧪 Evaluando modelo: {provider.value}")
        resultados = {
            "modelo": provider.value,
            "timestamp": datetime.now().isoformat(),
            "categorias": {},
            "resumen": {}
        }
        
        total_puntuacion = 0
        total_prompts = 0
        
        for categoria, prompts in self.prompts_evaluacion.items():
            logger.info(f"  📝 Evaluando categoría: {categoria}")
            resultados_categoria = []
            
            for i, prompt in enumerate(prompts, 1):
                try:
                    logger.info(f"    Prompt {i}/{len(prompts)}: {prompt[:50]}...")
                    
                    # Generar respuesta
                    start_time = time.time()
                    respuesta = await self.model_manager.chat_completion(
                        prompt, 
                        temperature=0.7, 
                        preferred_provider=provider
                    )
                    response_time = time.time() - start_time
                    
                    # Evaluar respuesta
                    evaluacion = self.evaluar_respuesta(prompt, respuesta, categoria)
                    evaluacion["prompt"] = prompt
                    evaluacion["respuesta"] = respuesta
                    evaluacion["tiempo_respuesta"] = response_time
                    
                    resultados_categoria.append(evaluacion)
                    total_puntuacion += evaluacion["puntuacion"]
                    total_prompts += 1
                    
                    logger.info(f"    ✅ Puntuación: {evaluacion['puntuacion']:.1f}/100")
                    
                except Exception as e:
                    logger.error(f"    ❌ Error en prompt: {e}")
                    resultados_categoria.append({
                        "prompt": prompt,
                        "error": str(e),
                        "puntuacion": 0,
                        "tiempo_respuesta": 0
                    })
                    total_prompts += 1
            
            # Calcular estadísticas de la categoría
            puntuaciones = [r.get("puntuacion", 0) for r in resultados_categoria]
            resultados["categorias"][categoria] = {
                "prompts": resultados_categoria,
                "puntuacion_promedio": sum(puntuaciones) / len(puntuaciones) if puntuaciones else 0,
                "mejor_puntuacion": max(puntuaciones) if puntuaciones else 0,
                "peor_puntuacion": min(puntuaciones) if puntuaciones else 0
            }
        
        # Resumen general
        resultados["resumen"] = {
            "puntuacion_total": total_puntuacion / total_prompts if total_prompts > 0 else 0,
            "prompts_evaluados": total_prompts,
            "prompts_exitosos": sum(1 for cat in resultados["categorias"].values() 
                               for prompt in cat["prompts"] if "error" not in prompt)
        }
        
        return resultados
    
    async def ejecutar_evaluacion_completa(self) -> Dict[str, Any]:
        """Ejecuta evaluación completa de todos los modelos disponibles"""
        
        logger.info("🚀 Iniciando evaluación automática de modelos")
        logger.info("=" * 60)
        
        # Obtener modelos disponibles
        providers_disponibles = self.model_manager.get_available_providers()
        
        if not providers_disponibles:
            logger.error("❌ No hay modelos disponibles para evaluar")
            return {"error": "No hay modelos disponibles"}
        
        logger.info(f"📋 Modelos a evaluar: {[p.value for p in providers_disponibles]}")
        
        resultados_completos = {
            "evaluacion_id": f"eval_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "modelos_evaluados": {},
            "comparacion": {},
            "configuracion": {
                "categorias": list(self.prompts_evaluacion.keys()),
                "prompts_por_categoria": {k: len(v) for k, v in self.prompts_evaluacion.items()}
            }
        }
        
        # Evaluar cada modelo
        for provider in providers_disponibles:
            try:
                resultado_modelo = await self.evaluar_modelo(provider)
                resultados_completos["modelos_evaluados"][provider.value] = resultado_modelo
            except Exception as e:
                logger.error(f"❌ Error evaluando {provider.value}: {e}")
                resultados_completos["modelos_evaluados"][provider.value] = {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        # Generar comparación
        if len(resultados_completos["modelos_evaluados"]) > 1:
            resultados_completos["comparacion"] = self.generar_comparacion(
                resultados_completos["modelos_evaluados"]
            )
        
        return resultados_completos
    
    def generar_comparacion(self, resultados_modelos: Dict[str, Any]) -> Dict[str, Any]:
        """Genera comparación entre modelos"""
        
        comparacion = {
            "ranking": [],
            "mejor_por_categoria": {},
            "estadisticas": {}
        }
        
        # Ranking general
        modelos_validos = {}
        for modelo, datos in resultados_modelos.items():
            if "resumen" in datos and "puntuacion_total" in datos["resumen"]:
                modelos_validos[modelo] = datos["resumen"]["puntuacion_total"]
        
        ranking = sorted(modelos_validos.items(), key=lambda x: x[1], reverse=True)
        comparacion["ranking"] = [{
            "posicion": i + 1,
            "modelo": modelo,
            "puntuacion": puntuacion
        } for i, (modelo, puntuacion) in enumerate(ranking)]
        
        # Mejor por categoría
        categorias = set()
        for datos in resultados_modelos.values():
            if "categorias" in datos:
                categorias.update(datos["categorias"].keys())
        
        for categoria in categorias:
            mejor_modelo = None
            mejor_puntuacion = -1
            
            for modelo, datos in resultados_modelos.items():
                if ("categorias" in datos and 
                    categoria in datos["categorias"] and 
                    "puntuacion_promedio" in datos["categorias"][categoria]):
                    
                    puntuacion = datos["categorias"][categoria]["puntuacion_promedio"]
                    if puntuacion > mejor_puntuacion:
                        mejor_puntuacion = puntuacion
                        mejor_modelo = modelo
            
            if mejor_modelo:
                comparacion["mejor_por_categoria"][categoria] = {
                    "modelo": mejor_modelo,
                    "puntuacion": mejor_puntuacion
                }
        
        return comparacion
    
    def guardar_resultados(self, resultados: Dict[str, Any], archivo: str = None) -> str:
        """Guarda los resultados en un archivo JSON"""
        
        if archivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"evaluacion_automatica_{timestamp}.json"
        
        ruta_completa = os.path.join("resultados", archivo)
        os.makedirs("resultados", exist_ok=True)
        
        with open(ruta_completa, 'w', encoding='utf-8') as f:
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
                print(f"  {item['posicion']}. {item['modelo']}: {item['puntuacion']:.1f}/100")
        
        # Mostrar mejor por categoría
        if "comparacion" in resultados and "mejor_por_categoria" in resultados["comparacion"]:
            print("\n🎯 MEJOR POR CATEGORÍA:")
            for categoria, datos in resultados["comparacion"]["mejor_por_categoria"].items():
                print(f"  {categoria}: {datos['modelo']} ({datos['puntuacion']:.1f}/100)")
        
        # Mostrar estadísticas generales
        print("\n📈 ESTADÍSTICAS:")
        total_prompts = sum(
            datos.get("resumen", {}).get("prompts_evaluados", 0)
            for datos in resultados["modelos_evaluados"].values()
        )
        print(f"  Total de prompts evaluados: {total_prompts}")
        print(f"  Modelos evaluados: {len(resultados['modelos_evaluados'])}")
        print(f"  Categorías: {len(resultados['configuracion']['categorias'])}")

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