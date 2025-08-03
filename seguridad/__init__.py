"""Módulo de Seguridad del Sistema AI

Este módulo contiene todos los componentes relacionados con la seguridad del sistema,
incluyendo autenticación, encriptación y gestión de API keys.
"""

# Importaciones principales del módulo de seguridad
from .security import check_api_key, require_api_key
from .dependencies import get_api_key, get_settings
from .crypto import get_encryption_instance, APIKeyEncryption
from .encryption import (
    KeyEncryption,
    get_encryptor,
    encrypt_admin_key,
    decrypt_admin_key,
    safe_decrypt_key
)

__all__ = [
    # Funciones de autenticación
    'check_api_key',
    'require_api_key',
    'get_api_key',
    'get_settings',
    
    # Clases y funciones de encriptación
    'get_encryption_instance',
    'APIKeyEncryption',
    'KeyEncryption',
    'get_encryptor',
    'encrypt_admin_key',
    'decrypt_admin_key',
    'safe_decrypt_key'
]

__version__ = '1.0.0'
__author__ = 'FlowautoMate Team'
__description__ = 'Módulo de seguridad para el sistema AI con encriptación y autenticación'