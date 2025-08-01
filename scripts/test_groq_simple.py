#!/usr/bin/env python3
"""
Prueba simple del cliente Groq
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from servidor.settings import Settings
from servidor.usage import DailyTokenCounter
from herramientas.groq_client import GroqClient

async def test_groq():
    print("🧪 Probando cliente Groq...")
    
    try:
        settings = Settings()
        token_counter = DailyTokenCounter()
        
        print(f"API Key configurada: {settings.GROQ_API_KEY[:10]}..." if settings.GROQ_API_KEY else "No API Key")
        print(f"Modelo: {settings.GROQ_MODEL}")
        
        client = GroqClient(settings, token_counter)
        
        prompt = "Hola, ¿cómo estás?"
        print(f"Enviando prompt: {prompt}")
        
        response = await client.chat_completion(prompt, temperature=0.7)
        print(f"Respuesta: {response}")
        
        print("✅ Prueba exitosa")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_groq())