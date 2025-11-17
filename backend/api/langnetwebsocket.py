"""
LangNet WebSocket Handler
Real-time streaming of execution progress
"""
from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import asyncio
from datetime import datetime

from app.dependencies import get_current_user


# Active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, execution_id: str, websocket: WebSocket):
        await websocket.accept()
        if execution_id not in self.active_connections:
            self.active_connections[execution_id] = set()
        self.active_connections[execution_id].add(websocket)

    def disconnect(self, execution_id: str, websocket: WebSocket):
        if execution_id in self.active_connections:
            self.active_connections[execution_id].discard(websocket)
            if not self.active_connections[execution_id]:
                del self.active_connections[execution_id]

    async def send_message(self, execution_id: str, message: dict):
        if execution_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[execution_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.add(connection)

            # Clean up dead connections
            for connection in dead_connections:
                self.active_connections[execution_id].discard(connection)

    async def broadcast(self, execution_id: str, message: dict):
        await self.send_message(execution_id, message)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, execution_id: str):
    """
    WebSocket endpoint for streaming execution progress

    Messages sent:
    - {"type": "connected", "execution_id": "..."}
    - {"type": "task_started", "task": "...", "phase": "..."}
    - {"type": "task_progress", "task": "...", "progress": 45.5}
    - {"type": "task_completed", "task": "...", "output": "..."}
    - {"type": "task_failed", "task": "...", "error": "..."}
    - {"type": "execution_completed", "result": {...}}
    - {"type": "execution_failed", "error": "..."}
    """
    await manager.connect(execution_id, websocket)

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "execution_id": execution_id,
            "timestamp": datetime.now().isoformat()
        })

        # Import here to avoid circular dependency
        from api.langnetapi import EXECUTIONS

        # Stream execution updates
        last_log_count = 0
        while True:
            if execution_id not in EXECUTIONS:
                await websocket.send_json({
                    "type": "error",
                    "message": "Execution not found"
                })
                break

            execution = EXECUTIONS[execution_id]
            state = execution.get("state", {})

            # Send execution log updates
            execution_log = state.get("execution_log", [])
            if len(execution_log) > last_log_count:
                new_logs = execution_log[last_log_count:]
                for log in new_logs:
                    if log["status"] == "started":
                        await websocket.send_json({
                            "type": "task_started",
                            "task": log["task"],
                            "phase": log.get("phase"),
                            "timestamp": log["timestamp"]
                        })
                    elif log["status"] == "completed":
                        await websocket.send_json({
                            "type": "task_completed",
                            "task": log["task"],
                            "output_preview": log.get("output_preview", ""),
                            "timestamp": log["timestamp"]
                        })
                    elif log["status"] == "failed":
                        await websocket.send_json({
                            "type": "task_failed",
                            "task": log["task"],
                            "timestamp": log["timestamp"]
                        })

                last_log_count = len(execution_log)

            # Send progress update
            if state.get("progress_percentage") is not None:
                await websocket.send_json({
                    "type": "progress",
                    "percentage": state["progress_percentage"],
                    "completed_tasks": state.get("completed_tasks", 0),
                    "total_tasks": state.get("total_tasks", 9),
                    "current_task": state.get("current_task"),
                    "current_phase": state.get("current_phase")
                })

            # Check if execution finished
            if execution["status"] in ["completed", "failed"]:
                if execution["status"] == "completed":
                    await websocket.send_json({
                        "type": "execution_completed",
                        "execution_id": execution_id,
                        "result_summary": {
                            "agents_generated": len(state.get("agents_data", [])),
                            "tasks_generated": len(state.get("tasks_data", [])),
                            "has_yaml": bool(state.get("agents_yaml")),
                            "has_code": bool(state.get("generated_code"))
                        },
                        "timestamp": execution.get("completed_at")
                    })
                else:
                    await websocket.send_json({
                        "type": "execution_failed",
                        "execution_id": execution_id,
                        "error": execution.get("error", "Unknown error"),
                        "timestamp": execution.get("completed_at")
                    })
                break

            # Wait before next update
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        manager.disconnect(execution_id, websocket)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        manager.disconnect(execution_id, websocket)
