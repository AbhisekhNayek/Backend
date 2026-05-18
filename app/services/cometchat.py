import httpx
from app.config import settings

class CometChatService:
    def __init__(self):
        self.base_url = f"https://{settings.cometchat_app_id}.api-{settings.cometchat_region}.cometchat.io/v3"
        self.headers = {
            "apikey": settings.cometchat_rest_api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get_user(self, uid: str) -> dict:
        """Check if a user exists in CometChat"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/users/{uid}", headers=self.headers)
            if response.status_code == 200:
                return response.json().get("data", {})
            return None

    async def create_user(self, uid: str, name: str, avatar: str = "") -> dict:
        """Create a user in CometChat"""
        payload = {
            "uid": uid,
            "name": name,
            "avatar": avatar
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/users", json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json().get("data", {})

    async def create_auth_token(self, uid: str) -> str:
        """Create an Auth Token for a specific user"""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/users/{uid}/auth_tokens", headers=self.headers)
            response.raise_for_status()
            data = response.json().get("data", {})
            return data.get("authToken")

cometchat_service = CometChatService()
