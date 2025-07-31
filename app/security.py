from fastapi import HTTPException, status
from app.settings import Settings

def check_api_key(api_key: str, settings: Settings) -> bool:
    if not settings.API_KEYS:
        return True
    return api_key in settings.API_KEYS

def require_api_key(api_key: str) -> None:
    if not check_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )