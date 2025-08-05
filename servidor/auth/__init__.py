"""Módulo de autenticación - Fusión de dependencies.py + security.py"""

from .handlers import (
    get_app_settings,
    check_api_key_header,
    check_api_key,
    require_api_key
)

__all__ = [
    'get_app_settings',
    'check_api_key_header', 
    'check_api_key',
    'require_api_key'
]