"""
LangNet API Module
FastAPI endpoints and WebSocket for multi-agent system execution
"""

from .langnetapi import router as langnet_router

__all__ = ["langnet_router"]
