from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(timestamp=datetime.now().isoformat())


# @router.get("/")
# async def root():
#     return {"message": "Simple Chat API v1.0"}
