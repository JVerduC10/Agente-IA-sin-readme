import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class KeyEncryption:
    """Clase para encriptar y desencriptar claves API del administrador"""
    
    def __init__(self, master_password: str = None):
        """Inicializa el sistema de encriptación con una contraseña maestra"""
        if master_password is None:
            # Usar una contraseña por defecto si no se proporciona
            master_password = os.getenv('MASTER_KEY', 'jarvis-admin-2024-secure')
        
        self.master_password = master_password.encode()
        self._key = self._derive_key()
        self.cipher = Fernet(self._key)
    
    def _derive_key(self) -> bytes:
        """Deriva una clave de encriptación desde la contraseña maestra"""
        # Usar un salt fijo para que la clave sea reproducible
        salt = b'jarvis_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password))
        return key
    
    def encrypt_key(self, api_key: str) -> str:
        """Encripta una clave API"""
        try:
            encrypted_key = self.cipher.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted_key).decode()
        except Exception as e:
            logger.error(f"Error encriptando clave: {e}")
            raise
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """Desencripta una clave API"""
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted_key = self.cipher.decrypt(encrypted_data)
            return decrypted_key.decode()
        except Exception as e:
            logger.error(f"Error desencriptando clave: {e}")
            raise
    
    def is_encrypted(self, key: str) -> bool:
        """Verifica si una clave está encriptada"""
        try:
            # Intentar decodificar base64
            base64.urlsafe_b64decode(key.encode())
            # Si no falla, probablemente está encriptada
            return True
        except:
            return False

# Instancia global del encriptador
_encryptor = None

def get_encryptor() -> KeyEncryption:
    """Obtiene la instancia global del encriptador"""
    global _encryptor
    if _encryptor is None:
        _encryptor = KeyEncryption()
    return _encryptor

def encrypt_admin_key(api_key: str) -> str:
    """Función de conveniencia para encriptar claves de administrador"""
    return get_encryptor().encrypt_key(api_key)

def decrypt_admin_key(encrypted_key: str) -> str:
    """Función de conveniencia para desencriptar claves de administrador"""
    return get_encryptor().decrypt_key(encrypted_key)

def safe_decrypt_key(key: str) -> str:
    """Desencripta una clave si está encriptada, sino la devuelve tal como está"""
    encryptor = get_encryptor()
    if encryptor.is_encrypted(key):
        try:
            return encryptor.decrypt_key(key)
        except:
            logger.warning("No se pudo desencriptar la clave, usando valor original")
            return key
    return key