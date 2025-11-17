"""
Routers package - API endpoints
"""
from .auth import router as auth_router
from .users import router as users_router
from .projects import router as projects_router
from .agents import router as agents_router
from .tasks import router as tasks_router
from .documents import router as documents_router

__all__ = [
    "auth_router",
    "users_router",
    "projects_router",
    "agents_router",
    "tasks_router",
    "documents_router",
]
