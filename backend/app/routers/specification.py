"""
Specification Router
Handles functional specification generation, refinement, and versioning
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime
import asyncio
from app.database import get_db_connection, save_chat_message, get_previous_refinements
from app.dependencies import get_current_user
from app.llm import get_llm_client

router = APIRouter(prefix="/specifications", tags=["specifications"])


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class GenerateSpecificationRequest(BaseModel):
    project_id: str
    requirements_session_id: str
    requirements_version: int
    complementary_document_ids: List[str] = []
    session_name: Optional[str] = None
    detail_level: str = 'detailed'  # basic | detailed | comprehensive
    target_audience: str = 'mixed'  # technical | business | mixed
    include_data_model: bool = True
    include_use_cases: bool = True
    include_business_rules: bool = True
    include_glossary: bool = True
    custom_instructions: Optional[str] = None


class RefineSpecificationRequest(BaseModel):
    message: str
    parent_message_id: Optional[str] = None


class UpdateSpecificationRequest(BaseModel):
    content: str


# ============================================================
# CRUD ENDPOINTS
# ============================================================

@router.post("/")
async def create_specification_session(
    request: GenerateSpecificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new specification generation session
    Returns session_id immediately, generation happens in background
    """
    try:
        session_id = str(uuid.uuid4())

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Verify requirements session exists
            cursor.execute("""
                SELECT id FROM execution_sessions
                WHERE id = %s AND project_id = %s
            """, (request.requirements_session_id, request.project_id))

            if not cursor.fetchone():
                cursor.close()
                raise HTTPException(
                    status_code=404,
                    detail="Requirements session not found"
                )

            # Verify requirements version exists
            cursor.execute("""
                SELECT version FROM session_requirements_version
                WHERE session_id = %s AND version = %s
            """, (request.requirements_session_id, request.requirements_version))

            if not cursor.fetchone():
                cursor.close()
                raise HTTPException(
                    status_code=404,
                    detail=f"Requirements version {request.requirements_version} not found"
                )

            # Create specification session
            session_name = request.session_name or f"Especificação {datetime.now().strftime('%d/%m/%Y %H:%M')}"

            cursor.execute("""
                INSERT INTO execution_specification_sessions (
                    id, project_id, user_id, requirements_session_id, requirements_version,
                    session_name, status, ai_model_used, execution_metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, 'generating', %s, %s)
            """, (
                session_id,
                request.project_id,
                current_user['id'],
                request.requirements_session_id,
                request.requirements_version,
                session_name,
                'gpt-4-turbo',  # Model used
                str({
                    'detail_level': request.detail_level,
                    'target_audience': request.target_audience,
                    'includes': {
                        'data_model': request.include_data_model,
                        'use_cases': request.include_use_cases,
                        'business_rules': request.include_business_rules,
                        'glossary': request.include_glossary
                    },
                    'complementary_docs': request.complementary_document_ids
                })
            ))

            conn.commit()
            cursor.close()

        # Execute generation in background
        asyncio.create_task(execute_specification_generation(
            session_id=session_id,
            request=request,
            user_id=current_user['id']
        ))

        return {
            "session_id": session_id,
            "status": "generating",
            "message": "Specification generation started in background"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating specification session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_specifications(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List specification sessions with filters"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM execution_specification_sessions WHERE 1=1"
            params = []

            if project_id:
                query += " AND project_id = %s"
                params.append(project_id)

            if status:
                query += " AND status = %s"
                params.append(status)

            query += " ORDER BY started_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query, tuple(params))
            sessions = cursor.fetchall()
            cursor.close()

            return {"sessions": sessions, "total": len(sessions)}

    except Exception as e:
        print(f"❌ Error listing specifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
async def get_specification(session_id: str):
    """Get single specification session"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT * FROM execution_specification_sessions WHERE id = %s
            """, (session_id,))

            session = cursor.fetchone()
            cursor.close()

            if not session:
                raise HTTPException(status_code=404, detail="Specification not found")

            return session

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting specification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{session_id}")
async def update_specification(
    session_id: str,
    request: UpdateSpecificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update specification (manual edit)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            # Update main document
            cursor.execute("""
                UPDATE execution_specification_sessions
                SET specification_document = %s, updated_at = NOW()
                WHERE id = %s
            """, (request.content, session_id))

            # Get next version number
            cursor.execute("""
                SELECT MAX(version) as max_version
                FROM specification_version_history
                WHERE specification_session_id = %s
            """, (session_id,))

            result = cursor.fetchone()
            current_version = result['max_version'] if result and result['max_version'] else 0
            new_version = current_version + 1

            # Save new version
            cursor.execute("""
                INSERT INTO specification_version_history
                (specification_session_id, version, specification_document, created_by,
                 change_description, change_type, doc_size)
                VALUES (%s, %s, %s, %s, 'Edição manual do documento', 'manual_edit', %s)
            """, (
                session_id,
                new_version,
                request.content,
                current_user['id'],
                len(request.content)
            ))

            conn.commit()
            cursor.close()

            return {"message": "Specification updated", "version": new_version}

    except Exception as e:
        print(f"❌ Error updating specification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# VERSIONING ENDPOINTS
# ============================================================

@router.get("/{session_id}/versions")
async def list_versions(session_id: str):
    """List all versions of a specification"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            # Verify session exists
            cursor.execute("""
                SELECT id FROM execution_specification_sessions WHERE id = %s
            """, (session_id,))

            if not cursor.fetchone():
                cursor.close()
                raise HTTPException(status_code=404, detail="Specification not found")

            # Get versions
            cursor.execute("""
                SELECT version, created_at, change_description, change_type, doc_size
                FROM specification_version_history
                WHERE specification_session_id = %s
                ORDER BY version DESC
            """, (session_id,))

            versions = cursor.fetchall()
            cursor.close()

            return {"versions": versions}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error listing versions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/versions/{version}")
async def get_version(session_id: str, version: int):
    """Get specific version of a specification"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT * FROM specification_version_history
                WHERE specification_session_id = %s AND version = %s
            """, (session_id, version))

            version_data = cursor.fetchone()
            cursor.close()

            if not version_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Version {version} not found"
                )

            return version_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting version: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# GENERATION WORKFLOW (BACKGROUND)
# ============================================================

async def execute_specification_generation(
    session_id: str,
    request: GenerateSpecificationRequest,
    user_id: str
):
    """
    Execute specification generation workflow in background
    """
    try:
        print(f"\n{'='*80}")
        print(f"[SPEC GENERATION] Starting generation for session {session_id}")
        print(f"[SPEC GENERATION] Project: {request.project_id}")
        print(f"[SPEC GENERATION] Requirements: {request.requirements_session_id} v{request.requirements_version}")
        print(f"{'='*80}\n")

        # 1. Load requirements version
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT requirements_document, change_type, created_at
                FROM session_requirements_version
                WHERE session_id = %s AND version = %s
            """, (request.requirements_session_id, request.requirements_version))

            requirements_data = cursor.fetchone()
            cursor.close()

        if not requirements_data:
            raise Exception("Requirements version not found")

        requirements_document = requirements_data['requirements_document']
        print(f"[SPEC GENERATION] ✅ Requirements loaded: {len(requirements_document)} chars")

        # 2. Load complementary documents (if any)
        complementary_docs_content = ""
        if request.complementary_document_ids:
            # TODO: Implement loading of complementary documents
            print(f"[SPEC GENERATION] Loading {len(request.complementary_document_ids)} complementary docs...")

        # 3. Build generation prompt
        from app.templates.specification_prompt import build_specification_prompt

        prompt = build_specification_prompt(
            requirements_document=requirements_document,
            requirements_version=request.requirements_version,
            requirements_change_type=requirements_data['change_type'],
            requirements_created_at=requirements_data['created_at'].strftime('%d/%m/%Y'),
            complementary_docs=complementary_docs_content,
            detail_level=request.detail_level,
            target_audience=request.target_audience,
            include_data_model=request.include_data_model,
            include_use_cases=request.include_use_cases,
            include_business_rules=request.include_business_rules,
            include_glossary=request.include_glossary,
            custom_instructions=request.custom_instructions,
            project_name=request.project_id  # TODO: Get actual project name
        )

        print(f"[SPEC GENERATION] ✅ Prompt built: {len(prompt)} chars")

        # 4. Call LLM
        print(f"[SPEC GENERATION] Calling LLM...")
        llm = get_llm_client()
        result = await llm.generate(prompt, max_tokens=16000)
        specification_document = result['text']

        print(f"[SPEC GENERATION] ✅ LLM response: {len(specification_document)} chars")

        # 5. Save results
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Update session
            cursor.execute("""
                UPDATE execution_specification_sessions
                SET specification_document = %s,
                    status = 'completed',
                    finished_at = NOW(),
                    total_sections = %s
                WHERE id = %s
            """, (
                specification_document,
                specification_document.count('##'),  # Count sections
                session_id
            ))

            # Save version 1
            cursor.execute("""
                INSERT INTO specification_version_history
                (specification_session_id, version, specification_document, created_by,
                 change_type, change_description, doc_size)
                VALUES (%s, 1, %s, %s, 'initial_generation', 'Geração inicial da especificação', %s)
            """, (
                session_id,
                specification_document,
                user_id,
                len(specification_document)
            ))

            conn.commit()
            cursor.close()

        print(f"[SPEC GENERATION] ✅ Generation completed successfully")

    except Exception as e:
        print(f"[SPEC GENERATION] ❌ Error: {e}")

        # Update session status to failed
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE execution_specification_sessions
                    SET status = 'failed', generation_log = %s
                    WHERE id = %s
                """, (str(e), session_id))
                conn.commit()
                cursor.close()
        except:
            pass


# ============================================================
# REFINEMENT ENDPOINT
# ============================================================

@router.post("/{session_id}/refine")
async def refine_specification(
    session_id: str,
    request: RefineSpecificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Refine specification via chat with agent
    Similar to requirements refinement workflow
    """
    # TODO: Implement refinement workflow
    # This will be similar to chat.py:execute_refinement_workflow
    raise HTTPException(status_code=501, detail="Refinement not yet implemented")
