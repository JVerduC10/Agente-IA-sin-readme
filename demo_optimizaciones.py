#!/usr/bin/env python3
"""
Demo de las optimizaciones implementadas

Este script demuestra las mejoras de rendimiento y progreso en tiempo real
implementadas en el sistema de evaluaciones y pruebas.
"""

import asyncio
import time

from scripts.evaluacion_automatica import EvaluacionAutomatica
from scripts.update_test_results import main as run_optimized_tests
from scripts.update_test_results import set_progress_callback


def demo_progress_callback(progress_info):
    """Callback de demostración para mostrar progreso"""
    print(
        f"\r[{progress_info.get('progress_percentage', 0):3.0f}%] "
        f"{progress_info.get('message', 'Procesando...')} "
        f"({progress_info.get('completed', 0)}/{progress_info.get('total', 0)}) "
        f"ETA: {progress_info.get('eta_formatted', 'N/A')}",
        end="",
        flush=True,
    )


async def demo_evaluaciones_optimizadas():
    """Demuestra las evaluaciones optimizadas con progreso"""
    print("\n=== DEMO: Evaluaciones Automáticas Optimizadas ===")
    print("Características implementadas:")
    print("✓ Paralelización con control de concurrencia")
    print("✓ Cache de resultados para evitar re-evaluaciones")
    print("✓ Progreso en tiempo real con ETA")
    print("✓ Manejo robusto de errores")
    print("✓ Métricas de rendimiento detalladas")

    # Crear instancia optimizada
    evaluacion = EvaluacionAutomatica(
        max_concurrent_requests=3, enable_cache=True  # Limitar concurrencia para demo
    )

    # Configurar callback de progreso
    evaluacion.set_progress_callback(demo_progress_callback)

    print("\n🚀 Iniciando evaluaciones...")
    start_time = time.time()

    try:
        # Ejecutar evaluación completa
        resultado = await evaluacion.ejecutar_evaluacion_completa("groq")

        end_time = time.time()
        print(
            f"\n\n✅ Evaluaciones completadas en {end_time - start_time:.2f} segundos"
        )

        # Mostrar resumen de resultados
        print("\n📊 Resumen de resultados:")
        if "configuracion" in resultado:
            config = resultado["configuracion"]
            print(f"   • Modelo evaluado: {config.get('modelo', 'N/A')}")
            print(
                f"   • Concurrencia máxima: {config.get('max_concurrent_requests', 'N/A')}"
            )
            print(f"   • Cache habilitado: {config.get('enable_cache', 'N/A')}")

        if "metricas" in resultado:
            metricas = resultado["metricas"]
            print(f"   • Tiempo total: {metricas.get('tiempo_total_segundos', 0):.2f}s")
            print(
                f"   • Prompts por segundo: {metricas.get('prompts_por_segundo', 0):.2f}"
            )
            print(f"   • Hits de cache: {metricas.get('cache_hits', 0)}")
            print(
                f"   • Eficiencia de cache: {metricas.get('cache_efficiency', 0):.1f}%"
            )

        if "resumen_general" in resultado:
            resumen = resultado["resumen_general"]
            print(
                f"   • Puntuación promedio: {resumen.get('puntuacion_promedio', 0):.2f}"
            )
            print(
                f"   • Tiempo promedio de respuesta: {resumen.get('tiempo_promedio_respuesta', 0):.2f}s"
            )

    except Exception as e:
        print(f"\n❌ Error durante las evaluaciones: {e}")


def demo_pruebas_optimizadas():
    """Demuestra las pruebas optimizadas con progreso"""
    print("\n\n=== DEMO: Pruebas Optimizadas ===")
    print("Características implementadas:")
    print("✓ Ejecución paralela de pruebas")
    print("✓ Progreso en tiempo real")
    print("✓ Timeout configurable")
    print("✓ Generación automática de reportes")
    print("✓ Cache de resultados")

    print("\n🧪 Iniciando pruebas optimizadas...")

    # Configurar callback de progreso
    set_progress_callback(demo_progress_callback)

    start_time = time.time()

    try:
        # Ejecutar pruebas optimizadas
        resultado = run_optimized_tests()

        end_time = time.time()
        print(f"\n\n✅ Pruebas completadas en {end_time - start_time:.2f} segundos")

        # Mostrar resumen
        print("\n📊 Resumen de pruebas:")
        print(f"   • Éxito: {resultado.get('success', False)}")
        print(f"   • Pasos completados: {resultado.get('steps_completed', 0)}")

        if "metrics" in resultado:
            metrics = resultado["metrics"]
            print(f"   • Tiempo total: {metrics.get('total_time', 0):.2f}s")
            print(f"   • Tiempo de parsing: {metrics.get('parse_time', 0):.2f}s")
            print(f"   • Tiempo de cache: {metrics.get('cache_update_time', 0):.2f}s")
            print(
                f"   • Tiempo de reportes: {metrics.get('report_generation_time', 0):.2f}s"
            )

        if "errors" in resultado and resultado["errors"]:
            print(f"   ⚠️  Errores encontrados: {len(resultado['errors'])}")
            for error in resultado["errors"][:3]:  # Mostrar solo los primeros 3
                print(f"      - {error}")

    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")


def mostrar_comparacion_rendimiento():
    """Muestra una comparación teórica del rendimiento"""
    print("\n\n=== COMPARACIÓN DE RENDIMIENTO ===")
    print("\n📈 Mejoras implementadas:")
    print("\n1. PARALELIZACIÓN:")
    print("   • Antes: Evaluaciones secuenciales (1 por vez)")
    print("   • Ahora: Hasta 5 evaluaciones concurrentes")
    print("   • Mejora estimada: 3-5x más rápido")

    print("\n2. CACHE DE RESULTADOS:")
    print("   • Antes: Re-evaluación completa en cada ejecución")
    print("   • Ahora: Cache inteligente de respuestas")
    print("   • Mejora estimada: 50-90% reducción en tiempo para re-ejecuciones")

    print("\n3. PROGRESO EN TIEMPO REAL:")
    print("   • Antes: Sin feedback durante ejecución")
    print("   • Ahora: Progreso detallado con ETA")
    print("   • Mejora: Mejor experiencia de usuario")

    print("\n4. OPTIMIZACIONES DE CÓDIGO:")
    print("   • Async/await para operaciones I/O")
    print("   • Eliminación de redundancias")
    print("   • Manejo eficiente de memoria")
    print("   • Mejora estimada: 20-40% reducción en uso de recursos")

    print("\n5. API MEJORADA:")
    print("   • Ejecución en segundo plano")
    print("   • Endpoints de progreso en tiempo real")
    print("   • Mejor manejo de errores")
    print("   • Fallback automático a versión legacy")


async def main():
    """Función principal de demostración"""
    print("🎯 DEMOSTRACIÓN DE OPTIMIZACIONES IMPLEMENTADAS")
    print("=" * 60)

    # Mostrar comparación de rendimiento
    mostrar_comparacion_rendimiento()

    # Preguntar al usuario qué demo ejecutar
    print("\n\n🔧 ¿Qué demostración deseas ejecutar?")
    print("1. Evaluaciones automáticas optimizadas")
    print("2. Pruebas optimizadas")
    print("3. Ambas")
    print("4. Solo mostrar información (sin ejecutar)")

    try:
        opcion = input("\nSelecciona una opción (1-4): ").strip()

        if opcion == "1":
            await demo_evaluaciones_optimizadas()
        elif opcion == "2":
            demo_pruebas_optimizadas()
        elif opcion == "3":
            await demo_evaluaciones_optimizadas()
            demo_pruebas_optimizadas()
        elif opcion == "4":
            print("\n✅ Información mostrada. No se ejecutaron pruebas.")
        else:
            print("\n❌ Opción no válida.")

    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrumpida por el usuario.")
    except Exception as e:
        print(f"\n❌ Error durante la demo: {e}")

    print("\n\n🎉 Demo completada. ¡Gracias por probar las optimizaciones!")


if __name__ == "__main__":
    asyncio.run(main())
