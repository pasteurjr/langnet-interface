"""
Projects router - CRUD endpoints for projects
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas import Project, ProjectCreate, ProjectUpdate
from app.database import execute_query, execute_insert, execute_update, execute_delete, get_db_cursor
from app.utils import generate_uuid, serialize_json, deserialize_json
from app.dependencies import get_pagination_params, validate_uuid

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate):
    """Create a new project"""
    project_id = generate_uuid()

    query = """
        INSERT INTO projects (
            id, user_id, name, description, domain, framework,
            default_llm, memory_system, start_from, template, status,
            project_data, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        )
    """

    params = (
        project_id,
        project.user_id,
        project.name,
        project.description,
        project.domain,
        project.framework,
        project.default_llm,
        project.memory_system,
        project.start_from,
        project.template,
        project.status,
        '{}'  # Empty JSON for project_data
    )

    try:
        execute_insert(query, params)
        return get_project(project_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating project: {str(e)}"
        )


@router.get("/{project_id}", response_model=Project)
def get_project(project_id: str):
    """Get a project by ID"""
    validate_uuid(project_id, "Project ID")

    query = "SELECT * FROM projects WHERE id = %s"
    project = execute_query(query, (project_id,), fetch_one=True)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )

    # Parse JSON fields
    project['project_data'] = deserialize_json(project.get('project_data'))
    project['petri_net'] = deserialize_json(project.get('petri_net'))
    project['config'] = deserialize_json(project.get('config'))

    return project


@router.get("/", response_model=List[Project])
def list_projects(
    user_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    framework: Optional[str] = None,
    pagination: dict = Depends(get_pagination_params)
):
    """List all projects with optional filters"""
    where_clauses = []
    params = []

    if user_id:
        validate_uuid(user_id, "User ID")
        where_clauses.append("user_id = %s")
        params.append(user_id)

    if status_filter:
        where_clauses.append("status = %s")
        params.append(status_filter)

    if framework:
        where_clauses.append("framework = %s")
        params.append(framework)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    query = f"""
        SELECT * FROM projects
        WHERE {where_sql}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """

    params.extend([pagination['limit'], pagination['skip']])

    projects = execute_query(query, tuple(params), fetch_all=True)

    # Parse JSON fields for each project
    for project in projects:
        project['project_data'] = deserialize_json(project.get('project_data'))
        project['petri_net'] = deserialize_json(project.get('petri_net'))
        project['config'] = deserialize_json(project.get('config'))

    return projects


@router.patch("/{project_id}", response_model=Project)
def update_project(project_id: str, project_update: ProjectUpdate):
    """Update a project"""
    validate_uuid(project_id, "Project ID")

    # Check if project exists
    get_project(project_id)

    update_fields = []
    params = []

    # Build dynamic UPDATE query based on provided fields
    if project_update.name is not None:
        update_fields.append("name = %s")
        params.append(project_update.name)

    if project_update.description is not None:
        update_fields.append("description = %s")
        params.append(project_update.description)

    if project_update.domain is not None:
        update_fields.append("domain = %s")
        params.append(project_update.domain)

    if project_update.framework is not None:
        update_fields.append("framework = %s")
        params.append(project_update.framework)

    if project_update.default_llm is not None:
        update_fields.append("default_llm = %s")
        params.append(project_update.default_llm)

    if project_update.memory_system is not None:
        update_fields.append("memory_system = %s")
        params.append(project_update.memory_system)

    if project_update.start_from is not None:
        update_fields.append("start_from = %s")
        params.append(project_update.start_from)

    if project_update.template is not None:
        update_fields.append("template = %s")
        params.append(project_update.template)

    if project_update.status is not None:
        update_fields.append("status = %s")
        params.append(project_update.status)

    if project_update.project_data is not None:
        update_fields.append("project_data = %s")
        params.append(serialize_json(project_update.project_data))

    if project_update.petri_net is not None:
        update_fields.append("petri_net = %s")
        params.append(serialize_json(project_update.petri_net))

    if project_update.config is not None:
        update_fields.append("config = %s")
        params.append(serialize_json(project_update.config))

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(project_id)

    query = f"""
        UPDATE projects
        SET {', '.join(update_fields)}
        WHERE id = %s
    """

    try:
        execute_update(query, tuple(params))
        return get_project(project_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating project: {str(e)}"
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str):
    """Delete a project and all associated data"""
    validate_uuid(project_id, "Project ID")

    # Check if project exists
    get_project(project_id)

    try:
        # Delete in order to respect foreign key constraints
        # Delete execution sessions first
        execute_delete("DELETE FROM execution_sessions WHERE project_id = %s", (project_id,))

        # Delete YAML files
        execute_delete("DELETE FROM yaml_files WHERE project_id = %s", (project_id,))

        # Delete documents
        execute_delete("DELETE FROM documents WHERE project_id = %s", (project_id,))

        # Delete tasks
        execute_delete("DELETE FROM tasks WHERE project_id = %s", (project_id,))

        # Delete agents
        execute_delete("DELETE FROM agents WHERE project_id = %s", (project_id,))

        # Finally delete the project
        rows_deleted = execute_delete("DELETE FROM projects WHERE id = %s", (project_id,))

        if rows_deleted == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting project: {str(e)}"
        )


@router.get("/{project_id}/stats")
def get_project_stats(project_id: str):
    """Get statistics for a project"""
    validate_uuid(project_id, "Project ID")

    # Check if project exists
    get_project(project_id)

    query = """
        SELECT
            (SELECT COUNT(*) FROM agents WHERE project_id = %s) as agents_count,
            (SELECT COUNT(*) FROM tasks WHERE project_id = %s) as tasks_count,
            (SELECT COUNT(*) FROM documents WHERE project_id = %s) as documents_count,
            (SELECT COUNT(*) FROM execution_sessions WHERE project_id = %s) as sessions_count,
            (SELECT COUNT(*) FROM yaml_files WHERE project_id = %s) as yaml_files_count
    """

    stats = execute_query(query, (project_id, project_id, project_id, project_id, project_id), fetch_one=True)

    return stats
