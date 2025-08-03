#!/usr/bin/env python3
"""
Sistema de Evaluación Automática de Modelos
Genera prompts automáticamente y evalúa las respuestas de los modelos disponibles.
"""

import asyncio
import logging
import json
import time
import webbrowser
from typing import Dict, List, Any
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from servidor.settings import Settings
from servidor.usage import DailyTokenCounter
from herramientas.model_manager import ModelManager, ModelProvider

# Configurar logging con colores
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Códigos de color ANSI
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
    @classmethod
    def red(cls, text): return f"{cls.RED}{text}{cls.END}"
    
    @classmethod
    def green(cls, text): return f"{cls.GREEN}{text}{cls.END}"
    
    @classmethod
    def yellow(cls, text): return f"{cls.YELLOW}{text}{cls.END}"
    
    @classmethod
    def blue(cls, text): return f"{cls.BLUE}{text}{cls.END}"
    
    @classmethod
    def bold(cls, text): return f"{cls.BOLD}{text}{cls.END}"

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
        respuesta_lower = respuesta.lower()
        palabras_respuesta = respuesta.split()
        
        # Criterios de evaluación básicos
        criterios = {
            "longitud_adecuada": 50 <= len(respuesta) <= 1000,
            "contiene_informacion": len(palabras_respuesta) > 10,
            "no_es_error": "error" not in respuesta_lower and "lo siento" not in respuesta_lower,
            "relevante": any(palabra in respuesta_lower for palabra in prompt.lower().split()[:3])
        }
        
        # Criterios específicos por categoría usando diccionario para evitar if-elif
        criterios_categoria = {
            "creatividad": lambda: any(palabra in respuesta_lower for palabra in 
                                     ["imaginó", "fantástico", "mágico", "increíble", "sorprendente"]),
            "razonamiento": lambda: any(palabra in respuesta_lower for palabra in 
                                       ["porque", "debido", "por tanto", "entonces", "resultado"]),
            "conocimiento": lambda: any(palabra.istitle() for palabra in palabras_respuesta),
            "programacion": lambda: any(codigo in respuesta for codigo in ["def ", "class ", "import "])
        }
        
        if categoria in criterios_categoria:
            criterios[f"criterio_{categoria}"] = criterios_categoria[categoria]()
        
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
        
        print(f"\n{Colors.blue('[TEST] Evaluando modelo:')} {Colors.bold(provider.value)}")
        resultados = {
            "modelo": provider.value,
            "timestamp": datetime.now().isoformat(),
            "categorias": {},
            "resumen": {},
            "errores": []
        }
        
        total_puntuacion = 0
        total_prompts = 0
        total_errores = 0
        
        for categoria, prompts in self.prompts_evaluacion.items():
            print(f"  {Colors.yellow('[EVAL] Evaluando categoría:')} {categoria}")
            resultados_categoria = []
            
            for i, prompt in enumerate(prompts, 1):
                try:
                    print(f"    {Colors.blue(f'Prompt {i}/{len(prompts)}:')} {prompt[:50]}...", end=" ")
                    
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
                    
                    # Mostrar resultado con color según puntuación
                    puntuacion = evaluacion["puntuacion"]
                    if puntuacion >= 80:
                        print(Colors.green(f"[OK] {puntuacion:.1f}/100"))
                    elif puntuacion >= 60:
                        print(Colors.yellow(f"[WARN] {puntuacion:.1f}/100"))
                    else:
                        print(Colors.red(f"[FAIL] {puntuacion:.1f}/100"))
                    
                except Exception as e:
                    total_errores += 1
                    error_msg = str(e)
                    print(Colors.red(f"[ERROR] ERROR: {error_msg}"))
                    
                    resultados_categoria.append({
                        "prompt": prompt,
                        "error": error_msg,
                        "puntuacion": 0,
                        "tiempo_respuesta": 0
                    })
                    resultados["errores"].append({
                        "categoria": categoria,
                        "prompt": prompt[:100],
                        "error": error_msg,
                        "timestamp": datetime.now().isoformat()
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
        prompts_exitosos = sum(1 for cat in resultados["categorias"].values() 
                              for prompt in cat["prompts"] if "error" not in prompt)
        
        resultados["resumen"] = {
            "puntuacion_total": total_puntuacion / total_prompts if total_prompts > 0 else 0,
            "prompts_evaluados": total_prompts,
            "prompts_exitosos": prompts_exitosos,
            "prompts_fallidos": total_errores,
            "tasa_exito": (prompts_exitosos / total_prompts * 100) if total_prompts > 0 else 0
        }
        
        # Mostrar resumen del modelo
        puntuacion_final = resultados["resumen"]["puntuacion_total"]
        tasa_exito = resultados["resumen"]["tasa_exito"]
        
        print(f"\n  {Colors.bold('[STATS] Resumen del modelo:')} {provider.value}")
        if puntuacion_final >= 80:
            print(f"  {Colors.green(f'Puntuación final: {puntuacion_final:.1f}/100')}")
        elif puntuacion_final >= 60:
            print(f"  {Colors.yellow(f'Puntuación final: {puntuacion_final:.1f}/100')}")
        else:
            print(f"  {Colors.red(f'Puntuación final: {puntuacion_final:.1f}/100')}")
            
        if tasa_exito >= 90:
            print(f"  {Colors.green(f'Tasa de éxito: {tasa_exito:.1f}%')}")
        elif tasa_exito >= 70:
            print(f"  {Colors.yellow(f'Tasa de éxito: {tasa_exito:.1f}%')}")
        else:
            print(f"  {Colors.red(f'Tasa de éxito: {tasa_exito:.1f}%')}")
            
        if total_errores > 0:
            print(f"  {Colors.red(f'Errores encontrados: {total_errores}')}")
        
        return resultados
    
    async def ejecutar_evaluacion_completa(self) -> Dict[str, Any]:
        """Ejecuta evaluación completa de todos los modelos disponibles"""
        
        print(f"\n{Colors.bold('[START] INICIANDO EVALUACION AUTOMATICA DE MODELOS')}")
        print(Colors.bold("=" * 60))
        
        # Verificar compatibilidad de modelos
        print(f"\n{Colors.blue('[CHECK] Verificando compatibilidad de modelos...')}")
        
        # Obtener modelos disponibles
        providers_disponibles = self.model_manager.get_available_providers()
        
        if not providers_disponibles:
            error_msg = "No hay modelos disponibles para evaluar"
            print(Colors.red(f"[ERROR] {error_msg}"))
            return {"error": error_msg}
        
        print(f"{Colors.green('[OK] Modelos disponibles:')} {[p.value for p in providers_disponibles]}")
        
        # Verificar configuración de cada modelo
        for provider in providers_disponibles:
            try:
                if provider == ModelProvider.GROQ:
                    if not self.model_manager.groq_client:
                        print(Colors.yellow(f"[WARN] Cliente Groq no inicializado correctamente"))
                    else:
                        print(Colors.green(f"[OK] Groq: Configurado correctamente"))
                elif provider == ModelProvider.BING:
                    if not self.model_manager.bing_client:
                        print(Colors.yellow(f"[WARN] Cliente Bing no inicializado correctamente"))
                    else:
                        print(Colors.green(f"[OK] Bing: Configurado correctamente"))
            except Exception as e:
                print(Colors.red(f"[ERROR] Error verificando {provider.value}: {e}"))
        
        resultados_completos = {
            "evaluacion_id": f"eval_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "modelos_evaluados": {},
            "comparacion": {},
            "configuracion": {
                "categorias": list(self.prompts_evaluacion.keys()),
                "prompts_por_categoria": {k: len(v) for k, v in self.prompts_evaluacion.items()}
            },
            "estadisticas_globales": {
                "total_modelos": len(providers_disponibles),
                "modelos_exitosos": 0,
                "modelos_fallidos": 0
            }
        }
        
        print(f"\n{Colors.bold('[CONFIG] CONFIGURACION DE EVALUACION:')}")
        print(f"  Categorías: {len(self.prompts_evaluacion)}")
        total_prompts = sum(len(prompts) for prompts in self.prompts_evaluacion.values())
        print(f"  Total de prompts: {total_prompts}")
        print(f"  Modelos a evaluar: {len(providers_disponibles)}")
        
        # Evaluar cada modelo
        modelos_exitosos = 0
        modelos_fallidos = 0
        
        for i, provider in enumerate(providers_disponibles, 1):
            try:
                print(f"\n{Colors.bold(f'[{i}/{len(providers_disponibles)}] EVALUANDO MODELO: {provider.value.upper()}')}")
                print("-" * 50)
                
                resultado_modelo = await self.evaluar_modelo(provider)
                resultados_completos["modelos_evaluados"][provider.value] = resultado_modelo
                modelos_exitosos += 1
                
            except Exception as e:
                modelos_fallidos += 1
                error_msg = str(e)
                print(Colors.red(f"[ERROR] ERROR CRITICO evaluando {provider.value}: {error_msg}"))
                
                resultados_completos["modelos_evaluados"][provider.value] = {
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat(),
                    "modelo": provider.value,
                    "resumen": {
                        "puntuacion_total": 0,
                        "prompts_evaluados": 0,
                        "prompts_exitosos": 0,
                        "prompts_fallidos": total_prompts,
                        "tasa_exito": 0
                    }
                }
        
        # Actualizar estadísticas globales
        resultados_completos["estadisticas_globales"].update({
            "modelos_exitosos": modelos_exitosos,
            "modelos_fallidos": modelos_fallidos
        })
        
        # Generar comparación solo si hay modelos exitosos
        modelos_validos = {k: v for k, v in resultados_completos["modelos_evaluados"].items() 
                          if "error" not in v}
        
        if len(modelos_validos) > 1:
            resultados_completos["comparacion"] = self.generar_comparacion(modelos_validos)
        elif len(modelos_validos) == 1:
            print(f"\n{Colors.yellow('[WARN] Solo un modelo fue evaluado exitosamente, no se puede generar comparacion')}") 
        else:
            print(f"\n{Colors.red('[ERROR] Ningun modelo fue evaluado exitosamente')}")
        
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
        
        logger.info(f"Resultados guardados en: {ruta_completa}")
        return ruta_completa
    
    def abrir_resultados_en_navegador(self, archivo: str) -> None:
        """Abre los resultados en el navegador web"""
        try:
            # Obtener solo el nombre del archivo sin la ruta
            nombre_archivo = os.path.basename(archivo)
            
            # URL del servidor local para ver los resultados
            url_resultados_web = "http://localhost:8000/results"
            url_resultados_json = f"http://localhost:8000/results/file/{nombre_archivo}"
            
            print(f"\n{Colors.blue('[INFO] Abriendo resultados en el navegador...')}") 
            print(f"  {Colors.cyan(f'URL: {url_resultados_web}')}") 
            
            # Abrir en el navegador la página web de resultados
            webbrowser.open(url_resultados_web)
            
            # También mostrar URLs adicionales útiles
            print(f"\n{Colors.green('[OK] URLs disponibles:')}") 
            print(f"  Página de resultados: {Colors.cyan(url_resultados_web)}")
            print(f"  [JSON] Resultados JSON: {Colors.cyan(url_resultados_json)}")
            print(f"  [LIST] Lista completa: {Colors.cyan('http://localhost:8000/results/list')}")
            print(f"  [LATEST] Último resultado: {Colors.cyan('http://localhost:8000/results/latest')}")
            print(f"  [SUMMARY] Resumen: {Colors.cyan('http://localhost:8000/results/summary')}")
            
        except Exception as e:
            print(f"{Colors.yellow('[WARN] No se pudo abrir el navegador automáticamente: {str(e)}')}") 
            print(f"  {Colors.blue('Puedes acceder manualmente a: http://localhost:8000/results/latest')}") 
    
    def _get_score_color_and_emoji(self, puntuacion: float) -> tuple:
        """Retorna color y emoji según la puntuación"""
        if puntuacion >= 80:
            return Colors.green, "[OK]"
        elif puntuacion >= 60:
            return Colors.yellow, "[WARN]"
        else:
            return Colors.red, "[FAIL]"
    
    def _get_ranking_emoji(self, posicion: int) -> str:
        """Retorna emoji según la posición en el ranking"""
        emojis = {1: "[1st]", 2: "[2nd]", 3: "[3rd]"}
        return emojis.get(posicion, "    ")
    
    def mostrar_resumen(self, resultados: Dict[str, Any]):
        """Muestra un resumen de los resultados con colores"""
        
        print(f"\n{Colors.bold('=' * 60)}")
        print(f"{Colors.bold('[SUMMARY] RESUMEN FINAL DE EVALUACION AUTOMATICA')}")
        print(f"{Colors.bold('=' * 60)}")
        
        if "error" in resultados:
            print(Colors.red(f"[ERROR] Error: {resultados['error']}"))
            return
        
        # Mostrar estadísticas globales
        if "estadisticas_globales" in resultados:
            stats = resultados["estadisticas_globales"]
            print(f"\n{Colors.bold('[STATS] ESTADISTICAS GLOBALES:')}")
            print(f"  Total de modelos: {stats['total_modelos']}")
            
            if stats['modelos_exitosos'] > 0:
                exitosos = stats['modelos_exitosos']
                print(f"  {Colors.green(f'Modelos exitosos: {exitosos}')}") 
            if stats['modelos_fallidos'] > 0:
                fallidos = stats['modelos_fallidos']
                print(f"  {Colors.red(f'Modelos fallidos: {fallidos}')}")
        
        # Mostrar resumen por modelo
        print(f"\n{Colors.bold('[MODELS] RESUMEN POR MODELO:')}")
        for modelo, datos in resultados["modelos_evaluados"].items():
            if "error" in datos:
                error_msg = datos["error"][:100]
                print(f"  {Colors.red(f'[ERROR] {modelo}: ERROR - {error_msg}...')}")
            else:
                resumen = datos.get("resumen", {})
                puntuacion = resumen.get("puntuacion_total", 0)
                tasa_exito = resumen.get("tasa_exito", 0)
                
                color_func, emoji = self._get_score_color_and_emoji(puntuacion)
                print(f"  {emoji} {color_func(f'{modelo}: {puntuacion:.1f}/100 (Éxito: {tasa_exito:.1f}%)')}")
        
        # Mostrar ranking
        if "comparacion" in resultados and "ranking" in resultados["comparacion"]:
            print(f"\n{Colors.bold('[RANKING] RANKING DE MODELOS:')}")
            for item in resultados["comparacion"]["ranking"]:
                posicion = item['posicion']
                modelo = item['modelo']
                puntuacion = item['puntuacion']
                emoji = self._get_ranking_emoji(posicion)
                color_func, _ = self._get_score_color_and_emoji(puntuacion)
                
                print(f"  {color_func(f'{emoji} {posicion}. {modelo}: {puntuacion:.1f}/100')}")
        
        # Mostrar mejor por categoría
        if "comparacion" in resultados and "mejor_por_categoria" in resultados["comparacion"]:
            print(f"\n{Colors.bold('[BEST] MEJOR POR CATEGORIA:')}")
            for categoria, datos in resultados["comparacion"]["mejor_por_categoria"].items():
                modelo = datos['modelo']
                puntuacion = datos['puntuacion']
                color_func, _ = self._get_score_color_and_emoji(puntuacion)
                emoji = "[OK]" if puntuacion >= 80 else "[WARN]" if puntuacion >= 60 else "[FAIL]"
                
                print(f"  {color_func(f'{emoji} {categoria}: {modelo} ({puntuacion:.1f}/100)')}")
        
        # Mostrar errores si los hay
        errores_totales = sum(len(datos.get("errores", [])) for datos in resultados["modelos_evaluados"].values())
        
        if errores_totales > 0:
            print(f"\n{Colors.red(f'[WARN] TOTAL DE ERRORES ENCONTRADOS: {errores_totales}')}")
            print(f"  {Colors.yellow('Revisa los logs detallados para más información')}")

async def main():
    """Función principal con timeout y mejor manejo de errores"""
    evaluador = EvaluacionAutomatica()
    
    try:
        print(f"{Colors.blue('[TIME] Iniciando evaluacion con timeout de 10 minutos...')}")
        
        # Ejecutar evaluación con timeout de 10 minutos
        resultados = await asyncio.wait_for(
            evaluador.ejecutar_evaluacion_completa(),
            timeout=600  # 10 minutos
        )
        
        # Guardar resultados
        archivo_resultados = evaluador.guardar_resultados(resultados)
        
        # Mostrar resumen
        evaluador.mostrar_resumen(resultados)
        
        # Abrir resultados en el navegador
        evaluador.abrir_resultados_en_navegador(archivo_resultados)
        
        # Mostrar resultado final
        if "error" in resultados:
            print(f"\n{Colors.red('[ERROR] Evaluacion completada con errores')}")
            print(f"  {Colors.yellow(f'Resultados guardados en: {archivo_resultados}')}")
            return 1
        else:
            print(f"\n{Colors.green('[OK] Evaluacion completada exitosamente')}")
            print(f"  {Colors.blue(f'Resultados guardados en: {archivo_resultados}')}")
            return 0
        
    except asyncio.TimeoutError:
        error_msg = "La evaluación excedió el tiempo límite de 10 minutos"
        print(Colors.red(f"\n[TIMEOUT] TIMEOUT: {error_msg}"))
        print(Colors.yellow("  Considera reducir el número de prompts o aumentar el timeout"))
        
        # Intentar guardar resultados parciales si existen
        try:
            resultados_parciales = {
                "error": error_msg,
                "timestamp": datetime.now().isoformat(),
                "evaluacion_id": f"timeout_{int(time.time())}",
                "tipo_error": "timeout"
            }
            archivo_resultados = evaluador.guardar_resultados(resultados_parciales)
            print(f"  {Colors.blue(f'Log de error guardado en: {archivo_resultados}')}")
            evaluador.abrir_resultados_en_navegador(archivo_resultados)
        except:
            pass
            
        return 2
        
    except KeyboardInterrupt:
        print(Colors.yellow("\n[WARN] Evaluacion interrumpida por el usuario"))
        return 3
        
    except Exception as e:
        error_msg = str(e)
        print(Colors.red(f"\n[ERROR] ERROR CRITICO en evaluacion: {error_msg}"))
        
        # Intentar guardar información del error
        try:
            resultados_error = {
                "error": error_msg,
                "timestamp": datetime.now().isoformat(),
                "evaluacion_id": f"error_{int(time.time())}",
                "tipo_error": "excepcion_critica",
                "traceback": str(e.__class__.__name__)
            }
            archivo_resultados = evaluador.guardar_resultados(resultados_error)
            print(f"  {Colors.blue(f'Log de error guardado en: {archivo_resultados}')}")
            evaluador.abrir_resultados_en_navegador(archivo_resultados)
        except:
            print(Colors.red("  No se pudo guardar el log de error"))
            
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)