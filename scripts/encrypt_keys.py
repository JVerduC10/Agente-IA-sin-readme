#!/usr/bin/env python3
"""
Script para encriptar claves API existentes.
Este script ayuda al administrador a codificar las claves para evitar su exposición.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from servidor.crypto import APIKeyEncryption


def main():
    print("🔐 Herramienta de Encriptación de Claves API")
    print("=" * 50)
    
    # Solicitar contraseña maestra
    master_password = input("Ingrese la contraseña maestra del administrador: ").strip()
    if not master_password:
        print("❌ Error: La contraseña maestra no puede estar vacía.")
        return
    
    # Crear instancia de encriptación
    encryption = APIKeyEncryption(master_password)
    
    print("\n📝 Ingrese las claves API a encriptar (presione Enter para omitir):")
    
    # Recopilar claves
    keys_to_encrypt = {}
    
    groq_key = input("GROQ_API_KEY: ").strip()
    if groq_key:
        keys_to_encrypt["GROQ_API_KEY"] = groq_key
    
    openai_key = input("OPENAI_API_KEY: ").strip()
    if openai_key:
        keys_to_encrypt["OPENAI_API_KEY"] = openai_key
    
    search_key = input("SEARCH_API_KEY: ").strip()
    if search_key:
        keys_to_encrypt["SEARCH_API_KEY"] = search_key
    
    if not keys_to_encrypt:
        print("❌ No se proporcionaron claves para encriptar.")
        return
    
    print("\n🔄 Encriptando claves...")
    
    try:
        # Encriptar claves
        encrypted_keys = encryption.encrypt_multiple_keys(keys_to_encrypt)
        
        print("\n✅ Claves encriptadas exitosamente!")
        print("\n📋 Agregue estas líneas a su archivo .env:")
        print("=" * 50)
        
        # Mostrar configuración para .env
        print("# Configuración de encriptación")
        print(f'MASTER_PASSWORD="{master_password}"')
        print("USE_ENCRYPTED_KEYS=true")
        print()
        print("# Claves encriptadas")
        
        for key_name, encrypted_value in encrypted_keys.items():
            if encrypted_value:
                print(f'{key_name}_ENCRYPTED="{encrypted_value}"')
        
        print("\n⚠️  IMPORTANTE:")
        print("1. Guarde la contraseña maestra en un lugar seguro")
        print("2. Elimine las claves originales del archivo .env")
        print("3. Configure USE_ENCRYPTED_KEYS=true")
        print("4. Reinicie el servidor para aplicar los cambios")
        
        # Verificar encriptación
        print("\n🔍 Verificando encriptación...")
        decrypted_keys = encryption.decrypt_multiple_keys(encrypted_keys)
        
        verification_success = True
        for key_name, original_value in keys_to_encrypt.items():
            if decrypted_keys.get(key_name) != original_value:
                print(f"❌ Error: Verificación falló para {key_name}")
                verification_success = False
        
        if verification_success:
            print("✅ Verificación exitosa: Todas las claves se pueden desencriptar correctamente")
        
    except Exception as e:
        print(f"❌ Error durante la encriptación: {e}")
        return


def decrypt_keys():
    """Función para desencriptar claves (para verificación)."""
    print("🔓 Herramienta de Desencriptación de Claves API")
    print("=" * 50)
    
    master_password = input("Ingrese la contraseña maestra: ").strip()
    if not master_password:
        print("❌ Error: La contraseña maestra no puede estar vacía.")
        return
    
    encryption = APIKeyEncryption(master_password)
    
    print("\n📝 Ingrese las claves encriptadas:")
    
    encrypted_keys = {}
    
    groq_encrypted = input("GROQ_API_KEY_ENCRYPTED: ").strip()
    if groq_encrypted:
        encrypted_keys["GROQ_API_KEY"] = groq_encrypted
    
    openai_encrypted = input("OPENAI_API_KEY_ENCRYPTED: ").strip()
    if openai_encrypted:
        encrypted_keys["OPENAI_API_KEY"] = openai_encrypted
    
    search_encrypted = input("SEARCH_API_KEY_ENCRYPTED: ").strip()
    if search_encrypted:
        encrypted_keys["SEARCH_API_KEY"] = search_encrypted
    
    if not encrypted_keys:
        print("❌ No se proporcionaron claves encriptadas.")
        return
    
    try:
        decrypted_keys = encryption.decrypt_multiple_keys(encrypted_keys)
        
        print("\n✅ Claves desencriptadas:")
        print("=" * 30)
        
        for key_name, decrypted_value in decrypted_keys.items():
            if decrypted_value:
                # Mostrar solo los primeros y últimos caracteres por seguridad
                masked_value = decrypted_value[:8] + "..." + decrypted_value[-4:] if len(decrypted_value) > 12 else "***"
                print(f"{key_name}: {masked_value}")
        
    except Exception as e:
        print(f"❌ Error durante la desencriptación: {e}")


if __name__ == "__main__":
    print("Seleccione una opción:")
    print("1. Encriptar claves")
    print("2. Desencriptar claves (verificación)")
    
    choice = input("\nOpción (1 o 2): ").strip()
    
    if choice == "1":
        main()
    elif choice == "2":
        decrypt_keys()
    else:
        print("❌ Opción inválida. Use 1 o 2.")