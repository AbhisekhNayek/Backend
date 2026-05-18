from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.auth import auth_service
from app.utils.jwt import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class AuthRequest(BaseModel):
    role: str
    username: str
    password: str

@router.post("/register")
async def user_register(payload: AuthRequest):
    account = await auth_service.find_account_by_role(payload.role, payload.username)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_444_NOT_FOUND if hasattr(status, "HTTP_444_NOT_FOUND") else 404,
            detail="Account not found"
        )

    is_match = auth_service.verify_password(payload.password, account.get("password", ""))
    if not is_match:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({"id": str(account["_id"]), "role": payload.role})
    return {
        "success": True,
        "token": token,
        "role": payload.role,
        "id": str(account["_id"])
    }

@router.post("/login")
async def user_login(payload: AuthRequest):
    account = await auth_service.find_account_by_role(payload.role, payload.username)
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    is_match = auth_service.verify_password(payload.password, account.get("password", ""))
    if not is_match:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({"id": str(account["_id"]), "role": payload.role})
    return {
        "success": True,
        "token": token,
        "role": payload.role,
        "id": str(account["_id"])
    }
