#!/usr/bin/env python3

from pathlib import Path
from servidor.config import get_settings

def test_env_loading():
    print("=== Test de carga de variables de entorno ===")
    
    # Verificar la ruta del archivo .env
    env_file_path = Path(__file__).parent / "servidor" / ".env"
    print(f"Ruta del archivo .env: {env_file_path}")
    print(f"¿Existe el archivo .env?: {env_file_path.exists()}")
    
    if env_file_path.exists():
        print("\nContenido del archivo .env:")
        with open(env_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content[:500])  # Primeros 500 caracteres
    
    # Cargar configuración
    print("\n=== Cargando configuración ===")
    settings = get_settings()
    
    # Eliminado Azure - Sistema monocliente Groq
    print("Sistema configurado para Groq únicamente")

if __name__ == "__main__":
    test_env_loading()