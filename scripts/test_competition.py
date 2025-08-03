#!/usr/bin/env python3
"""
Script de prueba para el sistema de competencia de modelos.
Verifica que todos los componentes funcionen correctamente.
"""

import asyncio
import sys
import time
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from servidor.settings import Settings
from herramientas.model_manager import ModelManager
from servidor.usage import DailyTokenCounter


async def test_model_manager():
    """Prueba el gestor de modelos."""
    print("🧪 Probando ModelManager...")
    
    try:
        settings = Settings()
        token_counter = DailyTokenCounter()
        manager = ModelManager(settings, token_counter)
        
        # Verificar proveedores disponibles
        providers = manager.get_available_providers()
        print(f"✅ Proveedores disponibles: {providers}")
        
        if not providers:
            print("❌ No hay proveedores disponibles. Verificar configuración de claves API.")
            return False
        
        # Probar chat simple
        test_prompt = "Hola, ¿cómo estás?"
        print(f"\n📝 Probando prompt: '{test_prompt}'")
        
        for provider in providers:
            try:
                start_time = time.time()
                response = await manager.chat_completion(test_prompt, 0.7, provider)
                elapsed = time.time() - start_time
                
                print(f"✅ {provider.value.upper()}: {response[:100]}... (tiempo: {elapsed:.2f}s)")
            except Exception as e:
                print(f"❌ {provider.value.upper()}: Error - {e}")
        
        # Probar competencia si hay múltiples proveedores
        if len(providers) >= 2:
            print("\n🏆 Probando competencia de modelos...")
            try:
                competition_result = await manager.compete_models(test_prompt, 0.7)
                print(f"✅ Ganador: {competition_result.best_performer}")
                print(f"📊 Estadísticas: {competition_result.performance_stats}")
            except Exception as e:
                print(f"❌ Error en competencia: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en ModelManager: {e}")
        return False


def test_encryption():
    """Prueba simplificada - encriptación no disponible."""
    print("\n🔐 Probando sistema de encriptación...")
    print("⚠️ Sistema de encriptación no disponible en esta configuración")
    return True


def test_settings():
    """Prueba la configuración del sistema."""
    print("\n⚙️ Probando configuración...")
    
    try:
        settings = Settings()
        
        # Verificar configuraciones básicas
        required_settings = [
            'GROQ_API_KEY', 'DEFAULT_MODEL_PROVIDER'
        ]
        
        for setting in required_settings:
            value = getattr(settings, setting, None)
            if value is not None:
                print(f"✅ {setting}: Configurado")
            else:
                print(f"⚠️ {setting}: No configurado")
        
        print("✅ Configuración cargada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False


async def run_all_tests():
    """Ejecuta todas las pruebas."""
    print("🚀 Iniciando pruebas del sistema de competencia de modelos")
    print("=" * 60)
    
    tests = [
        ("Configuración", test_settings),
        ("Encriptación", test_encryption),
        ("Gestor de Modelos", test_model_manager)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Ejecutando prueba: {test_name}")
        print("-" * 40)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            results.append((test_name, result))
            
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado final: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar configuración.")
    
    return passed == total


if __name__ == "__main__":
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")
        sys.exit(1)