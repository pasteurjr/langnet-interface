"""
LangNet FastAPI Application
"""
from fastapi import FastAPI, WebSocket, Query, status
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import test_connection
from app.routers import auth_router, users_router, projects_router, agents_router, tasks_router, documents_router
from app.routers.chat import router as chat_router
from app.routers.specification import router as specification_router
from app.routers.agent_task import router as agent_task_router
from app.routers.agent_task_spec import router as agent_task_spec_router
from app.routers.agents_yaml import router as agents_yaml_router
from app.routers.tasks_yaml import router as tasks_yaml_router
from api.langnetapi import router as langnet_router
from api.langnetwebsocket import websocket_endpoint
from app.utils import decode_access_token

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
    expose_headers=["*"],  # Expose all headers in responses
)

# Include routers with /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(agents_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")  # Chat with agents (memory-enabled)
app.include_router(specification_router, prefix="/api")  # Functional specification generation
app.include_router(agent_task_router, prefix="/api")  # Agent & Task generation from specifications
app.include_router(agent_task_spec_router, prefix="/api")  # Agent & Task specification document generation
app.include_router(agents_yaml_router, prefix="/api")  # agents.yaml generation from specification
app.include_router(tasks_yaml_router, prefix="/api")  # tasks.yaml generation from specification
app.include_router(langnet_router, prefix="/api")  # LangNet multi-agent system


# WebSocket endpoint for real-time execution streaming
@app.websocket("/ws/langnet/{execution_id}")
async def langnet_websocket(
    websocket: WebSocket,
    execution_id: str,
    token: str = Query(...)
):
    """
    WebSocket for streaming LangNet execution progress

    Requires authentication via token query parameter.
    Example: ws://localhost:8000/ws/langnet/{execution_id}?token=xxx
    """
    # Validate token before accepting WebSocket connection
    try:
        payload = decode_access_token(token)
        if not payload or not payload.get("user_id"):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired token")
            return
    except Exception as e:
        print(f"❌ WebSocket auth error: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
        return

    # Token is valid, proceed with WebSocket connection
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
