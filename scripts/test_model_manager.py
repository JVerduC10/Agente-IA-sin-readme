#!/usr/bin/env python3
"""
Prueba específica del ModelManager
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from servidor.settings import Settings
from servidor.usage import DailyTokenCounter
from herramientas.model_manager import ModelManager, ModelProvider

async def test_model_manager():
    print("🧪 Probando ModelManager...")
    
    try:
        settings = Settings()
        token_counter = DailyTokenCounter()
        
        print("Inicializando ModelManager...")
        model_manager = ModelManager(settings, token_counter)
        
        print("Proveedores disponibles:", model_manager.get_available_providers())
        
        prompt = "Hola, ¿cómo estás?"
        print(f"Enviando prompt: {prompt}")
        
        # Probar directamente con Groq
        print("\nProbando directamente con Groq...")
        try:
            response = await model_manager._execute_with_provider(
                ModelProvider.GROQ, prompt, 0.7
            )
            print(f"Respuesta directa: {response}")
        except Exception as e:
            print(f"Error directo: {e}")
            import traceback
            traceback.print_exc()
        
        # Probar con chat_completion
        print("\nProbando con chat_completion...")
        try:
            response = await model_manager.chat_completion(prompt, temperature=0.7)
            print(f"Respuesta chat_completion: {response}")
        except Exception as e:
            print(f"Error chat_completion: {e}")
            import traceback
            traceback.print_exc()
        
        print("✅ Prueba completada")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_model_manager())