from pydantic import BaseModel

from fastapi import APIRouter
router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str = "ok"
    
    
@router.get("", response_model=HealthResponse)
def health():
    return HealthResponse()
