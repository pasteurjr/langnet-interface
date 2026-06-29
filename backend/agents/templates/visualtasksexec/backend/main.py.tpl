"""
{{PROJECT_NAME}} — Backend FastAPI standalone

Serve a estrutura do projeto (Petri Net + agentes + tasks) pro frontend.
Sem banco — lê do project.json embarcado.
"""
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

PROJECT_FILE = Path(__file__).parent / "project.json"

app = FastAPI(
    title="{{PROJECT_NAME}} — Projects API",
    version="1.0.0",
)

# CORS aberto pra dev (frontend roda em outra porta)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_project() -> dict:
    if not PROJECT_FILE.exists():
        raise HTTPException(500, f"project.json não encontrado em {PROJECT_FILE}")
    with PROJECT_FILE.open() as f:
        return json.load(f)


@app.get("/")
def root():
    return {"service": "{{PROJECT_NAME}} backend", "status": "running"}


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "{{PROJECT_NAME}}"}


@app.get("/api/projects")
def list_projects():
    """Lista os projetos disponíveis. Como esse backend é mono-projeto,
    retorna sempre 1 elemento."""
    p = _load_project()
    return {
        "success": True,
        "projects": [
            {
                "id": p["id"],
                "name": p["name"],
                "description": p.get("description", ""),
                "stats": {
                    "places": len((p.get("petriNet") or {}).get("lugares", [])),
                    "transitions": len((p.get("petriNet") or {}).get("transicoes", [])),
                    "agents": len(p.get("agents", [])),
                    "tasks": len(p.get("tasks", [])),
                },
            }
        ],
    }


@app.get("/api/projects/{project_id}")
def get_project(project_id: str):
    p = _load_project()
    if p["id"] != project_id:
        raise HTTPException(404, f"projeto '{project_id}' não encontrado")
    return {"success": True, "project": p}


if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "{{BACKEND_PORT}}")))
