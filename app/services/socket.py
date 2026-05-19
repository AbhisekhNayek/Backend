import socketio
import logging
from datetime import datetime, timezone
from typing import Any
from app.utils.jwt import verify_token

logger = logging.getLogger(__name__)

# Initialize Socket.IO AsyncServer with CORS allowed origins
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ, auth=None):
    token = None
    if auth and isinstance(auth, dict):
        token = auth.get("token")
        
    if not token:
        # Check query string parameters
        from urllib.parse import parse_qs
        query_string = environ.get("QUERY_STRING", "")
        params = parse_qs(query_string)
        token_list = params.get("token")
        if token_list:
            token = token_list[0]
            
    if not token:
        # Check handshake headers in ASGI scope
        asgi_scope = environ.get("asgi.scope", {})
        headers = asgi_scope.get("headers", [])
        for k, v in headers:
            if k == b"token":
                token = v.decode("utf-8")
                break

    if not token:
        logger.warning("[SOCKET] Connection rejected: No authentication token found")
        raise socketio.exceptions.ConnectionRefusedError("Auth error")

    try:
        payload = verify_token(token)
        user_id = payload.get("id")
        if not user_id:
            raise ValueError("No user ID in token payload")
            
        await sio.save_session(sid, {"user": payload})
        
        # Join target and unified rooms
        await sio.enter_room(sid, f"user-{user_id}")
        await sio.enter_room(sid, "live-tracking")
        
        role = payload.get("role", "UNKNOWN")
        await sio.enter_room(sid, f"role-{role.upper()}")
        await sio.enter_room(sid, "role-ALL")
        
        # Check if Admin to join CCTV room
        if role == "ADMIN":
            await sio.enter_room(sid, "admin-cctv")
            logger.info(f"[SOCKET] Admin connected to CCTV room: {user_id} (SID: {sid})")
        else:
            # Broadcast user connection to CCTV room
            await sio.emit("user_connected", {
                "userId": user_id,
                "role": role,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, room="admin-cctv")
            
        logger.info(f"[SOCKET] User connected: {user_id} (SID: {sid})")
    except Exception as e:
        logger.warning(f"[SOCKET] Connection rejected: {str(e)}")
        raise socketio.exceptions.ConnectionRefusedError("Invalid token")

@sio.event
async def update_location(sid, data):
    try:
        session = await sio.get_session(sid)
        user = session.get("user", {})
        user_id = user.get("id")
        
        if not user_id:
            return
            
        broadcast_payload = {
            **data,
            "userId": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await sio.emit("live_location_update", broadcast_payload, room="live-tracking")
        logger.debug(f"[SOCKET] Location updated for user: {user_id}")
    except Exception as e:
        logger.error(f"[SOCKET] Location update error: {str(e)}")

@sio.event
async def disconnect(sid):
    try:
        session = await sio.get_session(sid)
        user = session.get("user", {})
        user_id = user.get("id")
        role = user.get("role", "UNKNOWN")
        
        if role != "ADMIN":
            # Broadcast user disconnection to CCTV room
            await sio.emit("user_disconnected", {
                "userId": user_id,
                "role": role,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, room="admin-cctv")
            
        logger.info(f"[SOCKET] User disconnected: {user_id} (SID: {sid})")
    except Exception as e:
        logger.error(f"[SOCKET] Disconnect error: {str(e)}")

class SocketService:
    async def emit_to_user(self, user_id: str, event: str, data: Any) -> bool:
        try:
            await sio.emit(event, data, room=f"user-{user_id}")
            return True
        except Exception as e:
            logger.error(f"[SOCKET] Emit to user {user_id} failed: {str(e)}")
            return False

    async def broadcast_to_tracking(self, data: Any) -> bool:
        try:
            await sio.emit("live_location_update", data, room="live-tracking")
            # Also emit to CCTV room
            await sio.emit("live_location_update", data, room="admin-cctv")
            return True
        except Exception as e:
            logger.error(f"[SOCKET] Broadcast to tracking failed: {str(e)}")
            return False

    async def broadcast_activity(self, data: Any) -> bool:
        try:
            await sio.emit("activity_logged", data, room="admin-cctv")
            return True
        except Exception as e:
            logger.error(f"[SOCKET] Broadcast activity failed: {str(e)}")
            return False

    async def broadcast_to_role(self, role: str, event: str, data: Any) -> bool:
        try:
            room_name = f"role-{role.upper()}"
            await sio.emit(event, data, room=room_name)
            return True
        except Exception as e:
            logger.error(f"[SOCKET] Broadcast to role {role} failed: {str(e)}")
            return False

    async def broadcast_to_all(self, event: str, data: Any) -> bool:
        try:
            await sio.emit(event, data)
            return True
        except Exception as e:
            logger.error(f"[SOCKET] Global broadcast failed: {str(e)}")
            return False

socket_service = SocketService()
