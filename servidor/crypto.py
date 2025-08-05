import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class APIKeyEncryption:
    """Clase para encriptar y desencriptar claves API del administrador."""
    
    def __init__(self, master_password: str):
        """Inicializa el sistema de encriptación con una contraseña maestra."""
        self.master_password = master_password.encode()
        self._fernet = None
    
    def _get_fernet(self) -> Fernet:
        """Genera o retorna la instancia de Fernet para encriptación."""
        if self._fernet is None:
            # Generar salt fijo basado en la contraseña maestra para consistencia
            salt = hashes.Hash(hashes.SHA256())
            salt.update(self.master_password)
            salt_bytes = salt.finalize()[:16]  # Usar primeros 16 bytes como salt
            
            # Derivar clave de encriptación
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_bytes,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.master_password))
            self._fernet = Fernet(key)
        
        return self._fernet
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encripta una clave API."""
        try:
            fernet = self._get_fernet()
            encrypted_key = fernet.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted_key).decode()
        except Exception as e:
            logger.error(f"Error encriptando clave API: {e}")
            raise ValueError("Error en la encriptación de la clave API")
    
    def decrypt_api_key(self, encrypted_api_key: str) -> str:
        """Desencripta una clave API."""
        try:
            fernet = self._get_fernet()
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_api_key.encode())
            decrypted_key = fernet.decrypt(encrypted_bytes)
            return decrypted_key.decode()
        except Exception as e:
            logger.error(f"Error desencriptando clave API: {e}")
            raise ValueError("Error en la desencriptación de la clave API")
    
    def encrypt_multiple_keys(self, keys_dict: dict) -> dict:
        """Encripta múltiples claves API."""
        encrypted_dict = {}
        for key_name, key_value in keys_dict.items():
            if key_value:  # Solo encriptar si la clave no está vacía
                encrypted_dict[key_name] = self.encrypt_api_key(key_value)
            else:
                encrypted_dict[key_name] = key_value
        return encrypted_dict
    
    def decrypt_multiple_keys(self, encrypted_keys_dict: dict) -> dict:
        """Desencripta múltiples claves API."""
        decrypted_dict = {}
        for key_name, encrypted_value in encrypted_keys_dict.items():
            if encrypted_value:  # Solo desencriptar si hay valor
                try:
                    decrypted_dict[key_name] = self.decrypt_api_key(encrypted_value)
                except ValueError:
                    # Si falla la desencriptación, asumir que ya está en texto plano
                    logger.warning(f"Clave {key_name} no pudo ser desencriptada, usando valor original")
                    decrypted_dict[key_name] = encrypted_value
            else:
                decrypted_dict[key_name] = encrypted_value
        return decrypted_dict


def get_encryption_instance() -> APIKeyEncryption:
    """Obtiene una instancia del sistema de encriptación usando la contraseña maestra del entorno."""
    master_password = os.getenv("MASTER_PASSWORD", "default_admin_key_2024")
    return APIKeyEncryption(master_password)


def get_decrypted_keys() -> Dict[str, str]:
    """Función centralizada para obtener claves desencriptadas.
    
    REFACTORIZACIÓN: Esta función reemplaza las implementaciones duplicadas en:
    - servidor/settings.py (ELIMINADO)
    - servidor/config/base.py (debe usar esta función)
    
    Returns:
        Dict[str, str]: Diccionario con las claves API desencriptadas
    """
    encryption = get_encryption_instance()
    
    # Claves encriptadas desde variables de entorno
    encrypted_keys = {
        # "AZURE_CLIENT_SECRET": os.getenv("AZURE_CLIENT_SECRET", ""),  # ELIMINADO - Azure integration removed
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
        "BING_SEARCH_API_KEY": os.getenv("BING_SEARCH_API_KEY", ""),
    }
    
    try:
        return encryption.decrypt_multiple_keys(encrypted_keys)
    except Exception as e:
        logger.error(f"Error desencriptando claves: {e}")
        # Fallback: retornar claves sin desencriptar (asumiendo texto plano)
        return encrypted_keys


def encrypt_env_keys():
    """Utilidad para encriptar claves en el archivo .env"""
    encryption = get_encryption_instance()
    
    # Claves que necesitan ser encriptadas
    keys_to_encrypt = {
        # "AZURE_CLIENT_SECRET": os.getenv("AZURE_CLIENT_SECRET", ""),  # ELIMINADO - Azure integration removed
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
    }
    
    encrypted_keys = encryption.encrypt_multiple_keys(keys_to_encrypt)
    
    print("Claves encriptadas:")
    for key_name, encrypted_value in encrypted_keys.items():
        if encrypted_value:
            print(f"{key_name}_ENCRYPTED={encrypted_value}")


if __name__ == "__main__":
    # Script para encriptar claves existentes
    encrypt_env_keys()