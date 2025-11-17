"""
Tasks router - CRUD endpoints for tasks
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas import Task, TaskCreate, TaskUpdate
from app.database import execute_query, execute_insert, execute_update, execute_delete
from app.utils import generate_uuid, serialize_list_field, parse_list_field, serialize_json, deserialize_json
from app.dependencies import get_pagination_params, validate_uuid

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    """Create a new task"""
    task_db_id = generate_uuid()

    query = """
        INSERT INTO tasks (
            id, project_id, task_id, name, description, agent_id,
            expected_output, tools, async_execution, context
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    params = (
        task_db_id, task.project_id, task.task_id, task.name, task.description, task.agent_id,
        task.expected_output, serialize_list_field(task.tools), task.async_execution,
        serialize_list_field(task.context)
    )

    execute_insert(query, params)
    return get_task(task_db_id)


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: str):
    """Get a task by ID"""
    validate_uuid(task_id, "Task ID")

    task = execute_query("SELECT * FROM tasks WHERE id = %s", (task_id,), fetch_one=True)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task['tools'] = parse_list_field(task.get('tools'))
    task['context'] = parse_list_field(task.get('context'))
    task['input_schema'] = deserialize_json(task.get('input_schema'))
    task['output_schema'] = deserialize_json(task.get('output_schema'))
    task['metadata'] = deserialize_json(task.get('metadata'))
    return task


@router.get("/", response_model=List[Task])
def list_tasks(
    project_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    pagination: dict = Depends(get_pagination_params)
):
    """List all tasks"""
    where_clauses = []
    params = []

    if project_id:
        validate_uuid(project_id, "Project ID")
        where_clauses.append("project_id = %s")
        params.append(project_id)

    if agent_id:
        validate_uuid(agent_id, "Agent ID")
        where_clauses.append("agent_id = %s")
        params.append(agent_id)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    query = f"SELECT * FROM tasks WHERE {where_sql} ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([pagination['limit'], pagination['skip']])

    tasks = execute_query(query, tuple(params), fetch_all=True)

    for task in tasks:
        task['tools'] = parse_list_field(task.get('tools'))
        task['context'] = parse_list_field(task.get('context'))
        task['input_schema'] = deserialize_json(task.get('input_schema'))
        task['output_schema'] = deserialize_json(task.get('output_schema'))
        task['metadata'] = deserialize_json(task.get('metadata'))

    return tasks


@router.patch("/{task_id}", response_model=Task)
def update_task(task_id: str, task_update: TaskUpdate):
    """Update a task"""
    validate_uuid(task_id, "Task ID")
    get_task(task_id)

    update_fields = []
    params = []

    for field, value in task_update.model_dump(exclude_unset=True).items():
        if field in ["tools", "context"]:
            update_fields.append(f"{field} = %s")
            params.append(serialize_list_field(value))
        elif field in ["input_schema", "output_schema", "metadata"]:
            update_fields.append(f"{field} = %s")
            params.append(serialize_json(value))
        else:
            update_fields.append(f"{field} = %s")
            params.append(value)

    if not update_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(task_id)

    query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s"
    execute_update(query, tuple(params))
    return get_task(task_id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str):
    """Delete a task"""
    validate_uuid(task_id, "Task ID")
    get_task(task_id)
    execute_delete("DELETE FROM tasks WHERE id = %s", (task_id,))
