"""Manejadores de autenticación - Fusión de dependencies.py + security.py"""

from typing import Optional

from fastapi import Depends, Header, HTTPException, status

from servidor.config.settings import Settings
from servidor.config.settings import get_settings as _get_settings


def get_app_settings() -> Settings:
    """Get application settings"""
    return _get_settings()


def check_api_key_header(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    settings: Settings = Depends(get_app_settings),
) -> str:
    """Check API key from header - Fusión de dependencies.py"""
    # Si no hay API keys configuradas, permitir acceso
    if not settings.API_KEYS:
        return "no-key-required"

    # Si no se proporciona API key, rechazar
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")

    # Validar API key
    if x_api_key not in settings.API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return x_api_key


def check_api_key(api_key: str, settings: Settings = None) -> bool:
    """Check API key validity - Fusión de security.py"""
    if settings is None:
        settings = _get_settings()

    # Verificar tanto API_KEYS como security.api_keys para compatibilidad
    api_keys = settings.API_KEYS or getattr(settings.security, "api_keys", [])

    if not api_keys:
        return True

    return api_key in api_keys


def require_api_key(api_key: str, settings: Settings = None) -> None:
    """Require valid API key - Fusión de security.py"""
    if not check_api_key(api_key, settings):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )


# ===== ALIAS PARA COMPATIBILIDAD =====
# Mantener nombres originales para compatibilidad con código existente
# get_settings alias removed to prevent circular dependency
