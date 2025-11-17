"""
Documents Router
Handles document upload, analysis, and requirements extraction
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
import os
import shutil
from pathlib import Path
from datetime import datetime
from app.database import get_db_connection
from app.dependencies import get_current_user
from app.parsers import DocumentParser
from app.llm import get_llm_client
from app.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and parse a document

    Args:
        file: Document file (PDF, DOCX, TXT, MD)
        project_id: Associated project ID
        current_user: Authenticated user

    Returns:
        Created document with parsed content
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext.replace(".", "") not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {settings.allowed_extensions}"
        )

    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    max_size = settings.max_file_size_mb * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_file_size_mb}MB"
        )

    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(exist_ok=True)

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = upload_dir / safe_filename

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Parse document
    try:
        parsed = DocumentParser.parse(str(file_path))

        if not parsed["success"]:
            raise HTTPException(status_code=400, detail=f"Failed to parse document: {parsed['error']}")

        # Save to database
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO documents (
                    project_id, user_id, filename, original_filename,
                    file_type, file_size, file_path, storage_type,
                    metadata, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                project_id,
                current_user["id"],
                safe_filename,
                file.filename,
                parsed["format"],
                file_size,
                str(file_path),
                "local",
                str(parsed["metadata"]),
                "uploaded"
            ))

            document_id = cursor.lastrowid
            conn.commit()

            # Fetch created document
            cursor.execute("""
                SELECT d.*, u.name as creator_name, p.name as project_name
                FROM documents d
                JOIN users u ON d.user_id = u.id
                JOIN projects p ON d.project_id = p.id
                WHERE d.id = %s
            """, (document_id,))

            doc = cursor.fetchone()
            cursor.close()

        return {
            "id": doc[0],
            "project_id": doc[1],
            "user_id": doc[2],
            "name": doc[3],  # filename
            "original_filename": doc[4],
            "type": doc[5],  # file_type
            "file_size": doc[6],
            "file_path": doc[7],
            "storage_type": doc[8],
            "uploaded_at": doc[9],
            "status": doc[10],
            "analysis_result": doc[11],  # analysis_results
            "extracted_entities": doc[12],
            "requirements": doc[13],
            "metadata": doc[14],
            "creator_name": doc[15],
            "project_name": doc[16]
        }

    except HTTPException:
        raise
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.get("/")
async def list_documents(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    List documents with optional filtering

    Args:
        project_id: Filter by project
        status: Filter by status (uploaded, analyzing, analyzed, error)
        current_user: Authenticated user

    Returns:
        List of documents
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        query = """
            SELECT d.*, u.name as creator_name, p.name as project_name
            FROM documents d
            JOIN users u ON d.user_id = u.id
            JOIN projects p ON d.project_id = p.id
            WHERE 1=1
        """
        params = []

        if project_id:
            query += " AND d.project_id = %s"
            params.append(project_id)

        if status:
            query += " AND d.status = %s"
            params.append(status)

        query += " ORDER BY d.uploaded_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()

    documents = []
    for row in rows:
        documents.append({
            "id": row[0],
            "project_id": row[1],
            "user_id": row[2],
            "name": row[3],  # filename
            "original_filename": row[4],
            "type": row[5],  # file_type
            "file_size": row[6],
            "file_path": row[7],
            "storage_type": row[8],
            "uploaded_at": row[9],
            "status": row[10],
            "analysis_result": row[11],  # analysis_results
            "extracted_entities": row[12],
            "requirements": row[13],
            "metadata": row[14],
            "creator_name": row[15],
            "project_name": row[16]
        })

    return documents


@router.get("/{document_id}")
async def get_document(
    document_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Get single document by ID

    Args:
        document_id: Document ID
        current_user: Authenticated user

    Returns:
        Document details
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT d.*, u.name as creator_name, p.name as project_name
            FROM documents d
            JOIN users u ON d.user_id = u.id
            JOIN projects p ON d.project_id = p.id
            WHERE d.id = %s
        """, (document_id,))

        doc = cursor.fetchone()
        cursor.close()

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": doc[0],
        "project_id": doc[1],
        "user_id": doc[2],
        "name": doc[3],  # filename
        "original_filename": doc[4],
        "type": doc[5],  # file_type
        "file_size": doc[6],
        "file_path": doc[7],
        "storage_type": doc[8],
        "uploaded_at": doc[9],
        "status": doc[10],
        "analysis_result": doc[11],  # analysis_results
        "extracted_entities": doc[12],
        "requirements": doc[13],
        "metadata": doc[14],
        "creator_name": doc[15],
        "project_name": doc[16]
    }


@router.post("/{document_id}/analyze")
async def analyze_document(
    document_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze document and extract requirements using LLM

    Args:
        document_id: Document ID
        current_user: Authenticated user

    Returns:
        Analysis results with extracted requirements
    """
    # Get document and analyze
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM documents WHERE id = %s", (document_id,))
        doc = cursor.fetchone()

        if not doc:
            cursor.close()
            raise HTTPException(status_code=404, detail="Document not found")

        # Update status to analyzing
        cursor.execute(
            "UPDATE documents SET status = %s WHERE id = %s",
            ("analyzing", document_id)
        )
        conn.commit()

        try:
            # Get LLM client
            llm = get_llm_client()

            # Extract requirements using LLM
            system_prompt = """You are a requirements analyst. Analyze the provided document and extract:
1. Functional Requirements (FR): What the system must do
2. Non-Functional Requirements (NFR): Quality attributes, constraints
3. Business Rules (BR): Constraints and policies
4. Actors: Who interacts with the system
5. Use Cases: Key scenarios and workflows

Respond with a JSON object containing these categorized requirements."""

            user_prompt = f"""Analyze this document and extract requirements:

Document: {doc[2]}
Content:
{doc[5]}

Extract all requirements, actors, and use cases. Be thorough and specific."""

            # Get structured analysis
            analysis = llm.extract_json(user_prompt, system_prompt)

            # Save analysis results
            cursor.execute("""
                UPDATE documents
                SET status = %s, analysis_result = %s
                WHERE id = %s
            """, ("analyzed", str(analysis), document_id))
            conn.commit()

            # Extract requirements and save to requirements table
            requirements_data = []

            # Functional requirements
            for fr in analysis.get("functional_requirements", []):
                requirements_data.append((
                    doc[1],  # project_id
                    document_id,
                    fr.get("id", ""),
                    fr.get("description", ""),
                    "functional",
                    fr.get("priority", "medium"),
                    current_user["id"]
                ))

            # Non-functional requirements
            for nfr in analysis.get("non_functional_requirements", []):
                requirements_data.append((
                    doc[1],
                    document_id,
                    nfr.get("id", ""),
                    nfr.get("description", ""),
                    "non_functional",
                    nfr.get("priority", "medium"),
                    current_user["id"]
                ))

            # Business rules
            for br in analysis.get("business_rules", []):
                requirements_data.append((
                    doc[1],
                    document_id,
                    br.get("id", ""),
                    br.get("description", ""),
                    "business_rule",
                    br.get("priority", "medium"),
                    current_user["id"]
                ))

            # Insert requirements
            if requirements_data:
                cursor.executemany("""
                    INSERT INTO requirements (
                        project_id, document_id, requirement_id,
                        description, type, priority, created_by
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, requirements_data)
                conn.commit()

            cursor.close()

            return {
                "document_id": document_id,
                "status": "analyzed",
                "analysis": analysis,
                "requirements_extracted": len(requirements_data)
            }

        except Exception as e:
            # Update status to error
            cursor.execute(
                "UPDATE documents SET status = %s WHERE id = %s",
                ("error", document_id)
            )
            conn.commit()
            cursor.close()

            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/{document_id}/requirements")
async def get_document_requirements(
    document_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Get requirements extracted from document

    Args:
        document_id: Document ID
        current_user: Authenticated user

    Returns:
        List of requirements
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.*, u.name as creator_name
            FROM requirements r
            JOIN users u ON r.created_by = u.id
            WHERE r.document_id = %s
            ORDER BY r.type, r.requirement_id
        """, (document_id,))

        rows = cursor.fetchall()
        cursor.close()

    requirements = []
    for row in rows:
        requirements.append({
            "id": row[0],
            "project_id": row[1],
            "document_id": row[2],
            "requirement_id": row[3],
            "description": row[4],
            "type": row[5],
            "priority": row[6],
            "status": row[7],
            "created_by": row[8],
            "created_at": row[9],
            "updated_at": row[10],
            "creator_name": row[11]
        })

    return requirements


@router.patch("/{document_id}")
async def update_document(
    document_id: int,
    name: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Update document metadata

    Args:
        document_id: Document ID
        name: New filename (optional)
        status: New status (optional)
        current_user: Authenticated user

    Returns:
        Updated document
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        updates = []
        params = []

        if name:
            updates.append("filename = %s")
            params.append(name)

        if status:
            updates.append("status = %s")
            params.append(status)

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        params.append(document_id)

        cursor.execute(
            f"UPDATE documents SET {', '.join(updates)} WHERE id = %s",
            params
        )
        conn.commit()

        # Fetch updated document
        cursor.execute("""
            SELECT d.*, u.name as creator_name, p.name as project_name
            FROM documents d
            JOIN users u ON d.user_id = u.id
            JOIN projects p ON d.project_id = p.id
            WHERE d.id = %s
        """, (document_id,))

        doc = cursor.fetchone()
        cursor.close()

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": doc[0],
        "project_id": doc[1],
        "user_id": doc[2],
        "name": doc[3],  # filename
        "original_filename": doc[4],
        "type": doc[5],  # file_type
        "file_size": doc[6],
        "file_path": doc[7],
        "storage_type": doc[8],
        "uploaded_at": doc[9],
        "status": doc[10],
        "analysis_result": doc[11],  # analysis_results
        "extracted_entities": doc[12],
        "requirements": doc[13],
        "metadata": doc[14],
        "creator_name": doc[15],
        "project_name": doc[16]
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete document and associated file

    Args:
        document_id: Document ID
        current_user: Authenticated user

    Returns:
        Success message
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get document
        cursor.execute("SELECT file_path FROM documents WHERE id = %s", (document_id,))
        doc = cursor.fetchone()

        if not doc:
            cursor.close()
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete file
        file_path = Path(doc[0])
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Warning: Failed to delete file {file_path}: {e}")

        # Delete from database
        cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
        conn.commit()
        cursor.close()

    return {"message": "Document deleted successfully"}
