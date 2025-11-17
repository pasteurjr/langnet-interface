"""
LangNet FastAPI Application
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import test_connection
from app.routers import auth_router, users_router, projects_router, agents_router, tasks_router, documents_router
from app.routers.chat import router as chat_router
from api.langnetapi import router as langnet_router
from api.langnetwebsocket import websocket_endpoint

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(agents_router)
app.include_router(tasks_router)
app.include_router(documents_router)
app.include_router(chat_router)  # Chat with agents (memory-enabled)
app.include_router(langnet_router)  # LangNet multi-agent system


# WebSocket endpoint for real-time execution streaming
@app.websocket("/ws/langnet/{execution_id}")
async def langnet_websocket(websocket: WebSocket, execution_id: str):
    """WebSocket for streaming LangNet execution progress"""
    await websocket_endpoint(websocket, execution_id)


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 60)
    print(f"🚀 Starting {settings.api_title} v{settings.api_version}")
    print("=" * 60)

    # Test database connection
    if test_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")

    print("=" * 60)
    print(f"📡 API running on http://{settings.api_host}:{settings.api_port}")
    print(f"📖 Docs available at http://{settings.api_host}:{settings.api_port}/docs")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("\n" + "=" * 60)
    print("🛑 Shutting down LangNet API")
    print("=" * 60)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "LangNet API",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.api_version
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
