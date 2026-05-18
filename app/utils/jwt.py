import jwt
from datetime import datetime, timezone, timedelta
from app.config import settings
from typing import Dict, Any, Optional

def generate_token(payload: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = payload.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    try:
        decoded_payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

create_access_token = generate_token

