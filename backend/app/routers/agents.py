"""
Agents router - CRUD endpoints for agents
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas import Agent, AgentCreate, AgentUpdate
from app.database import execute_query, execute_insert, execute_update, execute_delete
from app.utils import generate_uuid, serialize_list_field, parse_list_field, serialize_json, deserialize_json
from app.dependencies import get_pagination_params, validate_uuid

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
def create_agent(agent: AgentCreate):
    """Create a new agent"""
    agent_id = generate_uuid()

    query = """
        INSERT INTO agents (
            id, project_id, agent_id, name, role, goal, backstory,
            tools, verbose, allow_delegation, max_iter, max_rpm, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    params = (
        agent_id, agent.project_id, agent.agent_id, agent.name, agent.role,
        agent.goal, agent.backstory, serialize_list_field(agent.tools),
        agent.verbose, agent.allow_delegation, agent.max_iter, agent.max_rpm, agent.status
    )

    try:
        execute_insert(query, params)
        return get_agent(agent_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{agent_id}", response_model=Agent)
def get_agent(agent_id: str):
    """Get an agent by ID"""
    validate_uuid(agent_id, "Agent ID")

    query = "SELECT * FROM agents WHERE id = %s"
    agent = execute_query(query, (agent_id,), fetch_one=True)

    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    agent['tools'] = parse_list_field(agent.get('tools'))
    agent['metadata'] = deserialize_json(agent.get('metadata'))
    return agent


@router.get("/", response_model=List[Agent])
def list_agents(
    project_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    pagination: dict = Depends(get_pagination_params)
):
    """List all agents"""
    where_clauses = []
    params = []

    if project_id:
        validate_uuid(project_id, "Project ID")
        where_clauses.append("project_id = %s")
        params.append(project_id)

    if status_filter:
        where_clauses.append("status = %s")
        params.append(status_filter)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    query = f"SELECT * FROM agents WHERE {where_sql} ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([pagination['limit'], pagination['skip']])

    agents = execute_query(query, tuple(params), fetch_all=True)

    for agent in agents:
        agent['tools'] = parse_list_field(agent.get('tools'))
        agent['metadata'] = deserialize_json(agent.get('metadata'))

    return agents


@router.patch("/{agent_id}", response_model=Agent)
def update_agent(agent_id: str, agent_update: AgentUpdate):
    """Update an agent"""
    validate_uuid(agent_id, "Agent ID")
    get_agent(agent_id)

    update_fields = []
    params = []

    for field, value in agent_update.model_dump(exclude_unset=True).items():
        if field == "tools":
            update_fields.append("tools = %s")
            params.append(serialize_list_field(value))
        elif field == "metadata":
            update_fields.append("metadata = %s")
            params.append(serialize_json(value))
        else:
            update_fields.append(f"{field} = %s")
            params.append(value)

    if not update_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(agent_id)

    query = f"UPDATE agents SET {', '.join(update_fields)} WHERE id = %s"

    execute_update(query, tuple(params))
    return get_agent(agent_id)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: str):
    """Delete an agent"""
    validate_uuid(agent_id, "Agent ID")
    get_agent(agent_id)

    execute_delete("DELETE FROM agents WHERE id = %s", (agent_id,))
