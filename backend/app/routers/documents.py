"""
Documents Router
Handles document upload, analysis, and requirements extraction
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
import os
import shutil
import uuid
from pathlib import Path
from datetime import datetime
import asyncio
from app.database import get_db_connection, save_chat_message
from app.dependencies import get_current_user
from app.parsers import DocumentParser
from app.llm import get_llm_client
from app.config import settings
from agents.langnetagents import execute_document_analysis_workflow
from api.langnetwebsocket import manager
from api.langnetapi import EXECUTIONS

router = APIRouter(prefix="/documents", tags=["documents"])


async def execute_analysis_in_background(
    session_id: str,
    execution_id: str,
    project_id: str,
    documents: list,
    instructions: str,
    use_web_research: bool
):
    """
    Execute LangNet analysis in background and save results
    """
    try:
        # Register execution in EXECUTIONS dict for WebSocket tracking
        EXECUTIONS[execution_id] = {
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "state": {
                "current_task": "document_analysis",
                "progress_percentage": 0,
                "completed_tasks": 0,
                "total_tasks": 4,
                "execution_log": []
            }
        }

        # Send progress updates via WebSocket
        await manager.send_message(
            execution_id,
            {"type": "task_started", "task": "document_analysis", "message": "Iniciando análise com IA..."}
        )

        # Extract content from ALL documents WITH CHUNKING
        from app.parsers import DocumentParser
        from pathlib import Path
        from utils.pdf_processor import process_pdf_for_agent, chunk_text

        all_documents_info = []
        all_documents_content = ""

        print(f"\n{'='*80}")
        print(f"[PHASE 1 - EXTRACTION DEBUG] Starting document extraction")
        print(f"[PHASE 1] Total documents to process: {len(documents)}")
        print(f"{'='*80}\n")

        for idx, (doc_id, doc_filename, doc_path) in enumerate(documents, 1):
            doc_type = Path(doc_path).suffix[1:]  # .pdf -> pdf

            print(f"\n{'='*80}")
            print(f"[PHASE 1] Document {idx}/{len(documents)}: {doc_filename}")
            print(f"[PHASE 1] File type: {doc_type}")
            print(f"[PHASE 1] File path: {doc_path}")
            print(f"[PHASE 1] File exists: {Path(doc_path).exists()}")
            if Path(doc_path).exists():
                print(f"[PHASE 1] File size: {Path(doc_path).stat().st_size} bytes")
            print(f"{'='*80}")

            # Use chunking for PDFs (optimal processing)
            if doc_type == "pdf":
                try:
                    print(f"[PHASE 1] Using process_pdf_for_agent with chunking...")
                    result = process_pdf_for_agent(
                        doc_path,
                        max_pages=50,
                        chunk_size=4000,      # ~2500 words per chunk
                        chunk_overlap=400,     # 10% overlap
                        max_chunks=None        # Process all
                    )
                    doc_text = "\n\n---CHUNK---\n\n".join(result['formatted_chunks'])
                    word_count = result['stats']['raw_text_words']

                    print(f"[PHASE 1] ✅ PDF extracted successfully")
                    print(f"[PHASE 1] Chunks: {len(result['formatted_chunks'])}")
                    print(f"[PHASE 1] Word count: {word_count}")
                    print(f"[PHASE 1] Text length: {len(doc_text)} chars")
                    print(f"[PHASE 1] First 200 chars: {doc_text[:200]}")

                except Exception as e:
                    print(f"[PHASE 1] ⚠️  Chunking failed for {doc_filename}, using simple parser: {e}")
                    parsed = DocumentParser.parse(doc_path)
                    if not parsed["success"]:
                        print(f"[PHASE 1] ❌ FAILED to parse {doc_filename}: {parsed.get('error', 'Unknown error')}")
                        continue
                    doc_text = parsed["text"]
                    word_count = len(doc_text.split())
                    print(f"[PHASE 1] ✅ Fallback parser worked: {word_count} words, {len(doc_text)} chars")
            else:
                # Simple parser for other formats (DOCX, TXT, MD)
                print(f"[PHASE 1] Using simple parser for {doc_type}...")
                parsed = DocumentParser.parse(doc_path)
                if not parsed["success"]:
                    print(f"[PHASE 1] ❌ FAILED to parse {doc_filename}: {parsed.get('error', 'Unknown error')}")
                    continue

                doc_text = parsed["text"]
                word_count = len(doc_text.split())

                # Apply chunking if text is long (>30k chars = ~20k words)
                if len(doc_text) > 30000:
                    print(f"[PHASE 1] Document is long ({len(doc_text)} chars), applying chunking...")
                    chunks = chunk_text(doc_text, max_chunk_size=4000, overlap=400)
                    doc_text = "\n\n---CHUNK---\n\n".join(
                        [f"[CHUNK {i+1}]\n{c}" for i, c in enumerate(chunks)]
                    )
                    print(f"[PHASE 1] ✅ Chunked into {len(chunks)} parts")

            all_documents_info.append({
                "id": doc_id,
                "filename": doc_filename,
                "type": doc_type,
                "word_count": word_count,
                "path": doc_path
            })

            # Concatenate all documents with separators
            content_before_add = len(all_documents_content)
            all_documents_content += f"\n\n{'='*80}\n"
            all_documents_content += f"DOCUMENT: {doc_filename} (type: {doc_type})\n"
            all_documents_content += f"{'='*80}\n\n"
            all_documents_content += doc_text
            content_after_add = len(all_documents_content)

            print(f"[PHASE 1] Added {content_after_add - content_before_add} chars to all_documents_content")
            print(f"[PHASE 1] Total accumulated: {content_after_add} chars")

        print(f"\n{'='*80}")
        print(f"[PHASE 1 - FINAL] Extraction complete")
        print(f"[PHASE 1 - FINAL] Processed documents: {len(all_documents_info)}")
        print(f"[PHASE 1 - FINAL] Total content length: {len(all_documents_content)} characters")
        print(f"[PHASE 1 - FINAL] Total words: {len(all_documents_content.split())}")
        print(f"[PHASE 1 - FINAL] Documents info:")
        for info in all_documents_info:
            print(f"[PHASE 1 - FINAL]   - {info['filename']}: {info['word_count']} words ({info['type']})")
        print(f"\n[PHASE 1 - FINAL] Preview of all_documents_content (first 500 chars):")
        print(f"{all_documents_content[:500]}")
        print(f"\n[PHASE 1 - FINAL] Preview of all_documents_content (last 500 chars):")
        print(f"{all_documents_content[-500:]}")
        print(f"{'='*80}\n")

        # Use first document ID for tracking (will be improved later)
        primary_doc_id = documents[0][0] if documents else None

        print(f"\n{'='*80}")
        print(f"[PHASE 1] BEFORE calling execute_document_analysis_workflow")
        print(f"[PHASE 1] Parameters being passed:")
        print(f"[PHASE 1]   - project_id: {project_id}")
        print(f"[PHASE 1]   - document_id: {primary_doc_id}")
        print(f"[PHASE 1]   - document_path: Multiple documents: {', '.join([d['filename'] for d in all_documents_info])}")
        print(f"[PHASE 1]   - additional_instructions length: {len(instructions)} chars")
        print(f"[PHASE 1]   - additional_instructions preview: {instructions[:200] if instructions else 'None'}")
        print(f"[PHASE 1]   - enable_web_research: {use_web_research}")
        print(f"[PHASE 1]   - document_content length: {len(all_documents_content)} chars")
        print(f"[PHASE 1]   - document_content preview (first 300 chars):")
        print(f"{all_documents_content[:300]}")
        print(f"[PHASE 1]   - document_type: multiple")
        print(f"[PHASE 1]   - project_name: Análise de Requisitos - Projeto {project_id}")
        print(f"[PHASE 1]   - project_description: {(instructions[:500] if instructions else 'Análise de documentos para geração de requisitos')[:100]}...")
        print(f"{'='*80}\n")

        # Execute LangNet workflow in thread pool (don't block async event loop)
        # This allows the workflow to run for 2-5 minutes without blocking
        result_state = await asyncio.to_thread(
            execute_document_analysis_workflow,
            project_id=project_id,
            document_id=primary_doc_id,
            document_path=f"Multiple documents: {', '.join([d['filename'] for d in all_documents_info])}",
            additional_instructions=instructions,
            enable_web_research=use_web_research,
            document_content=all_documents_content,  # Pass ALL documents content
            document_type="multiple",
            # Metadados do projeto para contexto dos agentes
            project_name=f"Análise de Requisitos - Projeto {project_id}",
            project_description=instructions[:500] if instructions else "Análise de documentos para geração de requisitos",
            project_domain="",  # Será identificado pelos agentes a partir dos documentos
            use_deepseek=True  # Enable DeepSeek (will use reasoner if configured)
        )

        # Extract requirements document
        print(f"\n{'='*80}")
        print(f"[DEBUG] documents.py - Extracting requirements_document_md from result_state")
        print(f"[DEBUG] result_state keys: {list(result_state.keys())}")
        requirements_doc = result_state.get('requirements_document_md', '')
        print(f"[DEBUG] requirements_doc length: {len(requirements_doc)}")
        if requirements_doc:
            print(f"[DEBUG] requirements_doc preview:\n{requirements_doc[:300]}")
        else:
            print(f"[DEBUG] ⚠️  WARNING: requirements_document_md is EMPTY in result_state!")
            print(f"[DEBUG] Available state keys: {list(result_state.keys())}")
        print(f"{'='*80}\n")

        # Save to database
        print(f"\n{'='*80}")
        print(f"[DEBUG] SALVANDO NO BANCO - session_id: {session_id}")
        print(f"[DEBUG] requirements_doc length: {len(requirements_doc)}")
        print(f"{'='*80}\n")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE execution_sessions
                SET requirements_document = %s, status = 'completed', finished_at = NOW()
                WHERE id = %s
            """, (requirements_doc, session_id))
            affected_rows = cursor.rowcount
            conn.commit()

            print(f"\n{'='*80}")
            print(f"[DEBUG] SAVE COMPLETO - affected_rows: {affected_rows}")
            print(f"{'='*80}\n")

            # Verificar se realmente salvou
            cursor.execute("""
                SELECT LENGTH(requirements_document) as doc_length
                FROM execution_sessions
                WHERE id = %s
            """, (session_id,))
            result = cursor.fetchone()
            doc_length_db = result[0] if result else 0

            print(f"\n{'='*80}")
            print(f"[DEBUG] VERIFICAÇÃO PÓS-SAVE:")
            print(f"[DEBUG] Tamanho no banco: {doc_length_db} bytes")
            print(f"[DEBUG] Tamanho enviado: {len(requirements_doc)} bytes")
            print(f"[DEBUG] Match: {doc_length_db == len(requirements_doc)}")
            print(f"{'='*80}\n")

            # ========== SAVE VERSION 1 ==========
            # Get user_id from session
            cursor.execute("SELECT user_id FROM execution_sessions WHERE id = %s", (session_id,))
            user_result = cursor.fetchone()
            user_id = user_result[0] if user_result else None

            # Insert version 1 in session_requirements_version
            print(f"[DEBUG] Salvando versão 1 na tabela session_requirements_version")
            cursor.execute("""
                INSERT INTO session_requirements_version
                (session_id, version, requirements_document, created_by, change_description, change_type, doc_size)
                VALUES (%s, 1, %s, %s, 'Análise inicial', 'analysis', %s)
            """, (session_id, requirements_doc, user_id, len(requirements_doc)))
            conn.commit()
            print(f"[DEBUG] ✅ Versão 1 salva com sucesso")
            # ====================================

            cursor.close()

        # Send completion message
        save_chat_message(
            session_id=session_id,
            sender_type='agent',
            message_text='✅ Análise concluída! Documento de requisitos gerado.',
            message_type='result',
            task_execution_id=None,
            sender_name='Agente Analista',
            metadata={'execution_id': execution_id, 'has_document': True}
        )

        # Send document as separate message
        save_chat_message(
            session_id=session_id,
            sender_type='agent',
            message_text=requirements_doc,
            message_type='document',
            task_execution_id=None,
            sender_name='Agente Analista',
            metadata={'execution_id': execution_id, 'document_type': 'requirements'}
        )

        # Update EXECUTIONS status to completed
        EXECUTIONS[execution_id]["status"] = "completed"
        EXECUTIONS[execution_id]["completed_at"] = datetime.now().isoformat()
        EXECUTIONS[execution_id]["state"] = result_state

        await manager.send_message(
            execution_id,
            {"type": "execution_completed", "message": "Análise concluída!", "session_id": session_id}
        )

    except Exception as e:
        print(f"❌ Error in background analysis: {e}")
        import traceback
        traceback.print_exc()

        # Update EXECUTIONS status to failed
        if execution_id in EXECUTIONS:
            EXECUTIONS[execution_id]["status"] = "failed"
            EXECUTIONS[execution_id]["error"] = str(e)
            EXECUTIONS[execution_id]["completed_at"] = datetime.now().isoformat()

        # Update status to failed
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE execution_sessions
                SET status = 'failed', finished_at = NOW()
                WHERE id = %s
            """, (session_id,))
            conn.commit()
            cursor.close()

        # Send error message
        save_chat_message(
            session_id=session_id,
            sender_type='system',
            message_text=f'❌ Erro na análise: {str(e)}',
            message_type='error',
            task_execution_id=None,
            metadata={'execution_id': execution_id, 'error': str(e)}
        )

        await manager.send_message(
            execution_id,
            {"type": "execution_failed", "error": str(e)}
        )


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

    # Validate that project exists
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM projects WHERE id = %s", (project_id,))
        project = cursor.fetchone()
        cursor.close()

        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"Project not found: {project_id}"
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

            # Generate UUID explicitly (don't rely on MySQL DEFAULT uuid())
            document_id = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO documents (
                    id, project_id, user_id, filename, original_filename,
                    file_type, file_size, file_path, storage_type,
                    metadata, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                document_id,
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
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    List documents with optional filtering

    Args:
        project_id: Filter by project (UUID string)
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


@router.get("/sessions")
async def list_execution_sessions(
    project_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List all execution sessions that have generated requirements documents

    Args:
        project_id: Filter by project ID (optional, but recommended)
        limit: Maximum number of sessions to return (default: 50)
        offset: Number of sessions to skip (default: 0)

    Returns:
        List of sessions with metadata
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        # Build query with optional project filter
        base_query = """
            SELECT
                id,
                session_name,
                status,
                started_at as created_at,
                finished_at,
                LENGTH(requirements_document) as doc_size
            FROM execution_sessions
            WHERE requirements_document IS NOT NULL
              AND requirements_document != ''
        """

        params = []

        # Add project filter if provided
        if project_id:
            base_query += " AND project_id = %s"
            params.append(project_id)

        base_query += " ORDER BY started_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(base_query, tuple(params))
        sessions = cursor.fetchall()

        # Get total count with same filter
        count_query = """
            SELECT COUNT(*) as total
            FROM execution_sessions
            WHERE requirements_document IS NOT NULL
              AND requirements_document != ''
        """

        count_params = []
        if project_id:
            count_query += " AND project_id = %s"
            count_params.append(project_id)

        cursor.execute(count_query, tuple(count_params))
        total_result = cursor.fetchone()
        total = total_result['total'] if total_result else 0

        cursor.close()

        return {
            "sessions": sessions,
            "total": total,
            "limit": limit,
            "offset": offset,
            "project_id": project_id
        }


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
    document_id: str,
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


class AnalyzeDocumentsRequest(BaseModel):
    document_ids: List[str]
    project_id: str
    instructions: Optional[str] = None
    use_web_research: bool = False


@router.post("/analyze-batch")
async def analyze_documents_batch(
    request: AnalyzeDocumentsRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze multiple documents at once and generate comprehensive requirements document
    This endpoint creates a chat session and uses WebSocket for real-time updates

    Args:
        request: Batch analysis request with document IDs, instructions, and options
        current_user: Authenticated user

    Returns:
        Execution session ID and initial status
    """
    # Create execution session
    session_id = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Verify project exists
        cursor.execute("SELECT id FROM projects WHERE id = %s", (request.project_id,))
        if not cursor.fetchone():
            cursor.close()
            raise HTTPException(status_code=404, detail=f"Project not found: {request.project_id}")

        # Verify all documents exist and belong to this project
        cursor.execute("""
            SELECT id, filename, file_path
            FROM documents
            WHERE id IN (%s) AND project_id = %s
        """ % (','.join(['%s'] * len(request.document_ids)), '%s'),
        tuple(request.document_ids) + (request.project_id,))

        documents = cursor.fetchall()

        if len(documents) != len(request.document_ids):
            cursor.close()
            raise HTTPException(
                status_code=404,
                detail=f"Some documents not found or don't belong to project {request.project_id}"
            )

        # Create execution session
        cursor.execute("""
            INSERT INTO execution_sessions (
                id, project_id, user_id, session_name,
                status, execution_metadata
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session_id,
            request.project_id,
            current_user["id"],
            f'Document Analysis - {len(documents)} files',
            'running',
            str({
                'execution_id': execution_id,
                'document_count': len(documents),
                'use_web_research': request.use_web_research,
                'instructions': request.instructions,
                'type': 'document_analysis'
            })
        ))
        conn.commit()

        # Save initial chat messages (without task_execution_id since it doesn't exist in task_executions)
        save_chat_message(
            session_id=session_id,
            sender_type='system',
            message_text=f'🚀 Iniciando análise de {len(documents)} documento(s)...',
            message_type='status',
            task_execution_id=None,
            metadata={
                'project_id': request.project_id,
                'document_count': len(documents),
                'execution_id': execution_id
            }
        )

        if request.instructions:
            save_chat_message(
                session_id=session_id,
                sender_type='user',
                message_text=request.instructions,
                message_type='chat',
                task_execution_id=None,
                sender_name='Você',
                metadata={'type': 'initial_instructions', 'execution_id': execution_id}
            )

        save_chat_message(
            session_id=session_id,
            sender_type='agent',
            message_text=f'📚 Processando documentos: {", ".join([d[1] for d in documents])}',
            message_type='progress',
            task_execution_id=None,
            sender_name='Agente Analista',
            metadata={'documents': [d[1] for d in documents], 'execution_id': execution_id}
        )

        cursor.close()

    # Start LangNet analysis in background
    asyncio.create_task(execute_analysis_in_background(
        session_id=session_id,
        execution_id=execution_id,
        project_id=request.project_id,
        documents=documents,
        instructions=request.instructions or '',
        use_web_research=request.use_web_research
    ))

    return {
        "session_id": session_id,
        "execution_id": execution_id,
        "status": "running",
        "message": "Analysis started. Connect to WebSocket for real-time updates.",
        "websocket_url": f"/ws/langnet/{execution_id}"
    }

# ============================================================================
# REQUIREMENTS DOCUMENT ENDPOINTS
# ============================================================================

class UpdateRequirementsRequest(BaseModel):
    """Request model for updating requirements document"""
    content: str


@router.get("/sessions/{session_id}/requirements")
async def get_requirements_document(
    session_id: str
):
    """
    Get requirements document for a session

    Args:
        session_id: Execution session ID

    Returns:
        Requirements document in markdown format
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT requirements_document, status, session_name
            FROM execution_sessions
            WHERE id = %s
        """, (session_id,))

        session = cursor.fetchone()
        cursor.close()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if not session['requirements_document']:
            raise HTTPException(
                status_code=404,
                detail="Requirements document not yet generated. Analysis may still be running."
            )

        return {
            "session_id": session_id,
            "session_name": session['session_name'],
            "status": session['status'],
            "content": session['requirements_document']
        }


@router.put("/sessions/{session_id}/requirements")
async def update_requirements_document(
    session_id: str,
    request: UpdateRequirementsRequest
):
    """
    Update requirements document (user edits)

    Args:
        session_id: Execution session ID
        request: Updated document content

    Returns:
        Success message
    """
    from datetime import datetime
    import re

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Verify session exists
        cursor.execute("SELECT id FROM execution_sessions WHERE id = %s", (session_id,))
        if not cursor.fetchone():
            cursor.close()
            raise HTTPException(status_code=404, detail="Session not found")

        # ========== UPDATE DATE IN MARKDOWN ==========
        # Auto-update date in the document to current date/time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")

        updated_content = request.content

        # Update "**Data:** YYYY-MM-DD HH:MM:SS" pattern
        updated_content = re.sub(
            r'\*\*Data:\*\*\s+\d{4}-\d{2}-\d{2}(\s+\d{2}:\d{2}:\d{2})?',
            f'**Data:** {current_datetime}',
            updated_content
        )

        # Update "**Data da análise:** YYYY-MM-DD" pattern
        updated_content = re.sub(
            r'\*\*Data da análise:\*\*\s+\d{4}-\d{2}-\d{2}',
            f'**Data da análise:** {current_date}',
            updated_content
        )

        # Update version history table dates (| 1.0 | YYYY-MM-DD ... |)
        updated_content = re.sub(
            r'\|\s*1\.0\s*\|\s*\d{4}-\d{2}-\d{2}(\s+\d{2}:\d{2}:\d{2})?\s*\|',
            f'| 1.0 | {current_datetime} |',
            updated_content
        )

        print(f"[UPDATE] 📅 Data atualizada para: {current_datetime}")
        # ============================================

        # Update document with auto-updated dates
        print(f"[UPDATE] 📝 Atualizando documento da sessão {session_id}")
        print(f"[UPDATE] 📏 Tamanho do conteúdo: {len(updated_content)} caracteres")
        cursor.execute("""
            UPDATE execution_sessions
            SET requirements_document = %s
            WHERE id = %s
        """, (updated_content, session_id))
        rows_affected = cursor.rowcount
        conn.commit()
        print(f"[UPDATE] ✅ UPDATE executado! Linhas afetadas: {rows_affected}")

        # Verificar se realmente salvou
        cursor.execute("SELECT LENGTH(requirements_document) FROM execution_sessions WHERE id = %s", (session_id,))
        saved_size = cursor.fetchone()[0]
        print(f"[UPDATE] 🔍 Tamanho salvo no banco: {saved_size} caracteres")

        # ========== SAVE NEW VERSION ==========
        # Get next version number
        cursor.execute("""
            SELECT MAX(version) as max_version
            FROM session_requirements_version
            WHERE session_id = %s
        """, (session_id,))
        result = cursor.fetchone()
        current_version = result[0] if result and result[0] else 0
        new_version = current_version + 1

        # Insert new version (manual edit) with updated content (includes new dates)
        cursor.execute("""
            INSERT INTO session_requirements_version
            (session_id, version, requirements_document, created_by, change_description, change_type, doc_size)
            VALUES (%s, %s, %s, NULL, 'Edição manual do documento', 'manual_edit', %s)
        """, (session_id, new_version, updated_content, len(updated_content)))
        conn.commit()
        print(f"[MANUAL EDIT] ✅ Versão {new_version} salva (tipo: manual_edit)")
        # ======================================

        cursor.close()

        # Save edit notification in chat
        save_chat_message(
            session_id=session_id,
            sender_type='user',
            message_text='📝 Documento de requisitos editado manualmente',
            message_type='info',
            task_execution_id=None,
            sender_name='Você',
            metadata={'action': 'document_edited'}
        )

    return {
        "success": True,
        "message": "Requirements document updated successfully"
    }

@router.get("/sessions/{session_id}/versions")
async def list_document_versions(session_id: str):
    """
    List all versions of a requirements document
    
    Args:
        session_id: Execution session ID
        
    Returns:
        List of versions with metadata
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        
        # Verify session exists
        cursor.execute("SELECT id FROM execution_sessions WHERE id = %s", (session_id,))
        if not cursor.fetchone():
            cursor.close()
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all versions
        cursor.execute("""
            SELECT 
                version,
                created_at,
                change_description,
                change_type,
                doc_size
            FROM session_requirements_version
            WHERE session_id = %s
            ORDER BY version DESC
        """, (session_id,))
        
        versions = cursor.fetchall()
        cursor.close()
        
    return {"versions": versions}


@router.get("/sessions/{session_id}/versions/{version}")
async def get_document_version(session_id: str, version: int):
    """
    Get a specific version of a requirements document
    
    Args:
        session_id: Execution session ID
        version: Version number
        
    Returns:
        Document content and metadata for the specified version
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get specific version
        cursor.execute("""
            SELECT 
                version,
                requirements_document,
                created_at,
                change_description,
                change_type,
                doc_size
            FROM session_requirements_version
            WHERE session_id = %s AND version = %s
        """, (session_id, version))
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Version {version} not found for session {session_id}"
            )
            
    return {
        "version": result['version'],
        "content": result['requirements_document'],
        "created_at": result['created_at'],
        "change_description": result['change_description'],
        "change_type": result['change_type'],
        "doc_size": result['doc_size']
    }
