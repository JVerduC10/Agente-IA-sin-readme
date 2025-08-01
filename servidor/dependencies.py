from functools import lru_cache
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from servidor.settings import Settings

security = HTTPBearer()

@lru_cache()
def get_settings() -> Settings:
    return Settings()

def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Validate API key from Authorization header"""
    settings = get_settings()
    if credentials.credentials not in settings.API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials
