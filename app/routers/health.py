from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(prefix="/api/health", tags=["Health"])

@router.get("")
async def health_check():
    return {
        "status": "UP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "Docton Python Backend"
    }
