from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt import verify_token
from typing import List, Dict, Any

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    try:
        payload = verify_token(token)
        return payload
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

def role_required(allowed_roles: List[str]):
    async def dependency(current_user: Dict[str, Any] = Depends(get_current_user)):
        role = current_user.get("role")
        # Normalize comparison to match Node.js roles (which can be 'ADMIN', 'admin', 'user', 'DOCTOR', 'NURSE' etc.)
        if not role or role.upper() not in [r.upper() for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: You do not have the required role"
            )
        return current_user
    return dependency

# Helper for Admin Only access
async def admin_only(current_user: Dict[str, Any] = Depends(get_current_user)):
    role = current_user.get("role")
    if not role or role.upper() != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return current_user
