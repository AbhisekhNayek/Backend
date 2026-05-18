from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import connect_db
from app.services.socket import socket_app

# Import all routers
from app.routers import (
    health,
    auth,
    users,
    doctors,
    chat,
    tracking,
    clinical,
    financial,
    verification,
    system,
    tasks,
    analytics,
    quick_fill,
    ai,
    womens_health,
    nurses,
    admin_dashboard,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await connect_db()
    yield
    # Shutdown logic (optional)

app = FastAPI(
    title="Docton Professional Python Backend",
    description="Drop-in Replacement FastAPI & Socket.IO server for the Flutter client app",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO app at /socket.io
app.mount("/socket.io", socket_app)

# Include API routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(doctors.router)
app.include_router(chat.router)
app.include_router(tracking.router)
app.include_router(clinical.router)
app.include_router(financial.router)
app.include_router(verification.router)
app.include_router(system.router)
app.include_router(tasks.router)
app.include_router(analytics.router)
app.include_router(quick_fill.router)
app.include_router(ai.router)
app.include_router(womens_health.router)
app.include_router(nurses.router)
app.include_router(admin_dashboard.router)

# 404 Fallback to mimic Express exactly
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Route not found"
        }
    )

@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Docton Backend is online",
        "framework": "FastAPI (Python)"
    }
