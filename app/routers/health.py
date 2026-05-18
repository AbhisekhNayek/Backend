from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api/health", tags=["Health"])

@router.get("")
async def health_check():
    return {
        "status": "UP",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Docton Python Backend"
    }
