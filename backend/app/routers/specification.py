"""
Specification Router
Handles functional specification generation, refinement, and versioning
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel, Field, validator
import uuid
from datetime import datetime
import asyncio
from app.database import (
    get_db_connection,
    get_db_cursor,
    save_specification_chat_message,
    get_specification_chat_messages,
    get_specification_chat_message,
    update_specification_chat_message,
    get_previous_refinements
)
from app.dependencies import get_current_user
from app.llm import get_llm_client

router = APIRouter(prefix="/specifications", tags=["specifications"])


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

def validate_specification_completeness(doc: str) -> dict:
    """
    Verifica se todas as 14 seções obrigatórias estão presentes no documento.

    Returns:
        dict com 'complete' (bool), 'missing_sections' (list), 'section_count' (int)
    """
    required_sections = [
        ("## 1.", "Introdução"),
        ("## 2.", "Visão Geral"),
        ("## 3.", "Requisitos Funcionais"),
        ("## 4.", "Requisitos Não-Funcionais"),
        ("## 5.", "Casos de Uso"),
        ("## 6.", "Modelo de Dados"),
        ("## 7.", "Interfaces"),
        ("## 8.", "Regras de Negócio"),
        ("## 9.", "Fluxos de Trabalho"),
        ("## 10.", "Análise de Arquitetura"),
        ("## 11.", "Controle de Qualidade"),
        ("## 12.", "Glossário"),
        ("## 13.", "Rastreabilidade"),
        ("## 14.", "Apêndices")
    ]

    doc_lower = doc.lower()
    missing = []
    found = []

    for section_marker, section_name in required_sections:
        # Check if section exists (case insensitive)
        if section_marker.lower() in doc_lower:
            found.append(section_name)
        else:
            missing.append(f"{section_marker} {section_name}")

    return {
        "complete": len(missing) == 0,
        "missing_sections": missing,
        "found_sections": found,
        "section_count": len(found),
        "total_expected": 14
    }


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
    wireframe_format: str = 'ascii'  # 'ascii' | 'plantuml'


class RefineSpecificationRequest(BaseModel):
    message: str
    action_type: str = Field(
        default="refine",
        description="Tipo de ação: 'refine' modifica documento, 'chat' apenas responde"
    )
    parent_message_id: Optional[str] = None

    @validator('action_type')
    def validate_action_type(cls, v):
        if v not in ['refine', 'chat']:
            raise ValueError("action_type deve ser 'refine' ou 'chat'")
        return v


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
    """Get single specification session with current version"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT * FROM execution_specification_sessions WHERE id = %s
            """, (session_id,))

            session = cursor.fetchone()

            if not session:
                cursor.close()
                raise HTTPException(status_code=404, detail="Specification not found")

            # Get latest version number
            cursor.execute("""
                SELECT MAX(version) as current_version
                FROM specification_version_history
                WHERE specification_session_id = %s
            """, (session_id,))
            version_result = cursor.fetchone()
            session['current_version'] = version_result['current_version'] if version_result and version_result['current_version'] else 1

            cursor.close()
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
        import sys
        print(f"\n{'='*80}")
        print(f"[SPEC GENERATION] 🚀 INICIANDO GERAÇÃO - Session: {session_id}")
        print(f"[SPEC GENERATION] Project: {request.project_id}")
        print(f"[SPEC GENERATION] Requirements: {request.requirements_session_id} v{request.requirements_version}")
        print(f"{'='*80}\n")
        sys.stdout.flush()

        # Save progress message to chat
        save_specification_chat_message(
            session_id=session_id,
            sender_type="system",
            message_text="🚀 GERANDO ESPECIFICAÇÃO INICIAL...\n\nAguarde, isso pode levar 1-3 minutos enquanto a IA analisa os requisitos e gera o documento completo.",
            message_type="progress",
            sender_name="Sistema"
        )
        print(f"[SPEC GENERATION] ✅ Mensagem de progresso salva no chat")
        sys.stdout.flush()

        # 1. Load requirements version
        print(f"[SPEC GENERATION] 📥 STEP 1: Carregando requisitos do banco...")
        sys.stdout.flush()
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
        print(f"[SPEC GENERATION] ✅ STEP 1 OK: Requirements loaded: {len(requirements_document)} chars")
        sys.stdout.flush()

        # 2. Load complementary documents (if any)
        print(f"[SPEC GENERATION] 📄 STEP 2: Verificando documentos complementares...")
        sys.stdout.flush()
        complementary_docs_content = ""
        if request.complementary_document_ids:
            # TODO: Implement loading of complementary documents
            print(f"[SPEC GENERATION] Loading {len(request.complementary_document_ids)} complementary docs...")

        # 3. Build generation prompt
        print(f"[SPEC GENERATION] 📝 STEP 3: Construindo prompt para LLM...")
        sys.stdout.flush()

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
            wireframe_format=request.wireframe_format,
            project_name=request.project_id  # TODO: Get actual project name
        )

        print(f"[SPEC GENERATION] ✅ STEP 3 OK: Prompt built: {len(prompt)} chars")
        sys.stdout.flush()

        # 4. Call LLM (aumentado para 24000 tokens para geração completa das 14 seções)
        print(f"\n[SPEC GENERATION] 🤖 STEP 4: CHAMANDO LLM AGORA... (max_tokens=24000)")
        print(f"[SPEC GENERATION] ⏳ Aguarde... isso pode levar 1-3 minutos...")
        import sys
        sys.stdout.flush()

        llm = get_llm_client()
        print(f"[SPEC GENERATION] 🔌 LLM client obtido, iniciando chamada...")
        sys.stdout.flush()

        specification_document = await llm.complete_async(
            prompt=prompt,
            max_tokens=65536  # DeepSeek-Reasoner suporta até 64K em thinking mode
        )

        print(f"[SPEC GENERATION] ✅ STEP 4 OK - LLM RETORNOU! Tamanho: {len(specification_document)} chars")
        sys.stdout.flush()

        # 4.1 Validate completeness
        print(f"[SPEC GENERATION] 🔍 STEP 5: Validando completude do documento...")
        sys.stdout.flush()

        validation = validate_specification_completeness(specification_document)
        print(f"[SPEC GENERATION] 📋 Validação: {validation['section_count']}/{validation['total_expected']} seções encontradas")
        if not validation['complete']:
            print(f"[SPEC GENERATION] ⚠️ Missing sections: {validation['missing_sections']}")

        # 5. Save results
        print(f"\n[SPEC GENERATION] 💾 STEP 6: Salvando no banco de dados...")
        sys.stdout.flush()

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

        print(f"\n{'='*80}")
        print(f"[SPEC GENERATION] ✅ STEP 6 OK: Documento salvo no banco!")
        print(f"[SPEC GENERATION] 🎉 GERAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"[SPEC GENERATION] Documento final: {len(specification_document)} chars, {validation['section_count']} seções")
        print(f"{'='*80}\n")
        sys.stdout.flush()

    except Exception as e:
        print(f"\n{'='*80}")
        print(f"[SPEC GENERATION] ❌ ERRO DURANTE GERAÇÃO: {e}")
        print(f"{'='*80}\n")
        sys.stdout.flush()

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
# REFINEMENT WORKFLOW (BACKGROUND)
# ============================================================

async def execute_specification_refinement(
    session_id: str,
    refinement_instructions: str,
    current_specification: str,
    requirements_session_id: str,
    agent_message_id: str
):
    """
    Execute specification refinement workflow in background
    Similar to chat.py:execute_refinement_workflow but for specifications
    """
    try:
        print(f"\n{'='*80}")
        print(f"[SPEC REFINEMENT] Starting refinement for session {session_id}")
        print(f"[SPEC REFINEMENT] Instructions length: {len(refinement_instructions)} chars")
        print(f"[SPEC REFINEMENT] Current specification length: {len(current_specification)} chars")
        print(f"{'='*80}\n")

        # 1. Update session status to 'processing'
        with get_db_connection() as db:
            cursor = db.cursor()
            cursor.execute("""
                UPDATE execution_specification_sessions
                SET status = 'generating'
                WHERE id = %s
            """, (session_id,))
            db.commit()
            cursor.close()
        print(f"[SPEC REFINEMENT] Session status updated to 'processing'")

        # 2. Load original requirements document for context
        original_requirements = ""
        if requirements_session_id:
            with get_db_connection() as db:
                cursor = db.cursor(dictionary=True)
                cursor.execute("""
                    SELECT requirements_document FROM execution_sessions
                    WHERE id = %s
                """, (requirements_session_id,))
                req_data = cursor.fetchone()
                cursor.close()
            if req_data:
                original_requirements = req_data.get('requirements_document', '')
                print(f"[SPEC REFINEMENT] ✅ Requirements loaded: {len(original_requirements)} chars")

        # 3. Get previous refinements history
        previous_refinements = get_previous_refinements(session_id, limit=10)
        refinement_history = ""
        if previous_refinements:
            refinement_history = "HISTÓRICO DE REFINAMENTOS ANTERIORES:\n"
            for idx, msg in enumerate(previous_refinements, 1):
                timestamp = msg.get('timestamp', '')
                message_text = msg.get('message_text', '')
                refinement_history += f"{idx}. [{timestamp}] Usuário solicitou: {message_text}\n"
            refinement_history += "\n"
            print(f"[SPEC REFINEMENT] 📚 Incluindo {len(previous_refinements)} refinamentos anteriores")
        else:
            print(f"[SPEC REFINEMENT] 📭 Nenhum refinamento anterior encontrado")

        # 4. Save progress message
        save_specification_chat_message(
            session_id=session_id,
            sender_type='system',
            message_text='✏️ GERANDO REFINAMENTO...\n\nProcessando com IA. Aguarde enquanto analiso suas instruções e atualizo o documento.',
            message_type='progress',
            sender_name='Sistema'
        )

        # 5. Build refinement prompt (ESPECÍFICO PARA ESPECIFICAÇÃO)
        refinement_prompt = f"""ESPECIFICAÇÃO FUNCIONAL ATUAL:
{current_specification}

DOCUMENTO DE REQUISITOS BASE (REFERÊNCIA):
{original_requirements[:15000] if original_requirements else "Não disponível"}

{refinement_history}NOVA SOLICITAÇÃO DO USUÁRIO:
{refinement_instructions}

TAREFA CRÍTICA:
1. Aplique as mudanças solicitadas à especificação funcional
2. Mantenha a estrutura IEEE 830 intacta (seções numeradas)
3. Mantenha rastreabilidade com requisitos originais (RF-XXX, UC-XXX, RN-XXX)
4. Retorne o documento COMPLETO refinado em markdown
5. NÃO adicione comentários, análises ou introduções
6. CONSIDERE o histórico de refinamentos anteriores para manter coerência
7. ⚠️ NÃO REPRODUZA o documento de requisitos na saída - ele é apenas contexto de referência

IMPORTANTE: Retorne SOMENTE o documento markdown refinado. Comece diretamente com o título "# Especificação Funcional". NÃO inclua o documento de requisitos base no final da resposta.
"""

        print(f"[SPEC REFINEMENT] Prompt built: {len(refinement_prompt)} chars")

        # 6. Save progress message - Processing
        save_specification_chat_message(
            session_id=session_id,
            sender_type='agent',
            message_text='🤔 Processando refinamento com IA. Isso pode levar alguns minutos...',
            message_type='progress',
            sender_name='Agente Especificação'
        )

        # 7. Call LLM
        print(f"[SPEC REFINEMENT] Calling LLM...")
        llm_client = get_llm_client()
        refined_specification = await llm_client.complete_async(
            prompt=refinement_prompt,
            temperature=0.7,
            max_tokens=65536  # DeepSeek-Reasoner suporta até 64K em thinking mode
        )

        print(f"[SPEC REFINEMENT] LLM completed. Refined document length: {len(refined_specification)} chars")

        if not refined_specification or len(refined_specification) < 100:
            print(f"[SPEC REFINEMENT] ⚠️ WARNING: LLM returned empty or too short document!")
            raise Exception("Refinement failed: LLM returned empty or invalid response")

        # 8. Save progress message - Analysis completed
        save_specification_chat_message(
            session_id=session_id,
            sender_type='agent',
            message_text='✅ Análise concluída. Aplicando refinamentos ao documento...',
            message_type='progress',
            sender_name='Agente Especificação'
        )

        # 9. Update session with refined specification
        with get_db_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                UPDATE execution_specification_sessions
                SET specification_document = %s,
                    status = 'completed',
                    updated_at = NOW()
                WHERE id = %s
            """, (refined_specification, session_id))

            # Get next version number
            cursor.execute("""
                SELECT MAX(version) as max_version
                FROM specification_version_history
                WHERE specification_session_id = %s
            """, (session_id,))
            result = cursor.fetchone()
            current_version = result['max_version'] if result and result['max_version'] else 0
            new_version = current_version + 1

            # Get user_id from session
            cursor.execute("SELECT user_id FROM execution_specification_sessions WHERE id = %s", (session_id,))
            user_result = cursor.fetchone()
            user_id = user_result['user_id'] if user_result else None

            # Extract first words from instructions for description
            description = refinement_instructions[:100] + ('...' if len(refinement_instructions) > 100 else '')

            # Save new version
            print(f"[SPEC REFINEMENT] Salvando versão {new_version}")
            cursor.execute("""
                INSERT INTO specification_version_history
                (specification_session_id, version, specification_document, created_by,
                 change_description, change_type, doc_size)
                VALUES (%s, %s, %s, %s, %s, 'ai_refinement', %s)
            """, (session_id, new_version, refined_specification, user_id, description, len(refined_specification)))

            db.commit()
            cursor.close()

        print(f"[SPEC REFINEMENT] ✅ Versão {new_version} salva com sucesso")

        # 10. Update agent message with completion
        update_specification_chat_message(
            message_id=agent_message_id,
            message_text=f"✅ Refinamento concluído! O documento foi atualizado com base em suas instruções.",
            metadata={'type': 'refinement_response', 'status': 'completed'}
        )

        # 11. Send completion notification with diff data
        save_specification_chat_message(
            session_id=session_id,
            sender_type='system',
            message_text='✅ Especificação refinada com sucesso. Veja as alterações destacadas.',
            message_type='info',
            sender_name='Sistema',
            metadata={
                'type': 'refinement_complete',
                'has_diff': True,
                'old_document': current_specification,
                'new_document': refined_specification
            }
        )

        print(f"[SPEC REFINEMENT] ✅ Workflow completed successfully")

    except Exception as e:
        print(f"[SPEC REFINEMENT] ❌ Error during refinement: {e}")
        import traceback
        traceback.print_exc()

        # Update session status to 'completed' (not failed, to allow retry)
        try:
            with get_db_connection() as db:
                cursor = db.cursor()
                cursor.execute("""
                    UPDATE execution_specification_sessions
                    SET status = 'completed'
                    WHERE id = %s
                """, (session_id,))
                db.commit()
                cursor.close()
        except:
            pass

        # Update agent message with error
        try:
            update_specification_chat_message(
                message_id=agent_message_id,
                message_text=f"❌ Erro ao processar refinamento: {str(e)}",
                metadata={'type': 'refinement_response', 'status': 'error', 'error': str(e)}
            )
        except:
            pass


async def execute_specification_chat(
    session_id: str,
    user_message_id: str,
    agent_message_id: str,
    chat_message: str,
    requirements_session_id: Optional[str]
):
    """
    Execute chat/analysis workflow - DOES NOT modify specification
    """
    try:
        print(f"\n{'='*80}")
        print(f"[SPEC CHAT] 💬 INICIANDO ANÁLISE - Session: {session_id}")
        print(f"{'='*80}\n")

        # 1. Load current specification
        with get_db_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                SELECT specification_document
                FROM execution_specification_sessions
                WHERE id = %s
            """, (session_id,))
            spec_data = cursor.fetchone()
            cursor.close()

        if not spec_data:
            raise Exception("Specification session not found")

        current_specification = spec_data['specification_document']
        print(f"[SPEC CHAT] ✅ Specification loaded: {len(current_specification)} chars")

        # 2. Load requirements for context (optional)
        original_requirements = ""
        if requirements_session_id:
            with get_db_connection() as db:
                cursor = db.cursor(dictionary=True)
                cursor.execute("""
                    SELECT requirements_document FROM execution_sessions
                    WHERE id = %s
                """, (requirements_session_id,))
                req_data = cursor.fetchone()
                cursor.close()
            if req_data:
                original_requirements = req_data.get('requirements_document', '')
                print(f"[SPEC CHAT] ✅ Requirements loaded: {len(original_requirements)} chars")

        # 3. Build chat/analysis prompt (NO refinement instructions)
        chat_prompt = f"""ESPECIFICAÇÃO FUNCIONAL (PARA ANÁLISE):
{current_specification}

DOCUMENTO DE REQUISITOS BASE (REFERÊNCIA):
{original_requirements[:15000] if original_requirements else "Não disponível"}

SOLICITAÇÃO DO USUÁRIO:
{chat_message}

TAREFA:
Analise a especificação funcional acima e responda à solicitação do usuário.

IMPORTANTE:
- NÃO modifique o documento
- NÃO retorne uma versão refinada da especificação
- Apenas ANALISE e RESPONDA à pergunta/solicitação
- Seja objetivo e direto
- Se identificar problemas, liste-os claramente
- Se for pergunta sobre completude, verifique se todas as 14 seções estão presentes

Responda de forma conversacional e útil.
"""

        print(f"[SPEC CHAT] Prompt built: {len(chat_prompt)} chars")

        # 4. Save progress message
        save_specification_chat_message(
            session_id=session_id,
            sender_type='system',
            message_text='🔍 ANALISANDO ESPECIFICAÇÃO...\n\nProcessando com IA. Aguarde...',
            message_type='progress',
            sender_name='Sistema'
        )

        # 5. Call LLM (NO document modification)
        print(f"[SPEC CHAT] Calling LLM for analysis...")
        llm_client = get_llm_client()
        analysis_response = await llm_client.complete_async(
            prompt=chat_prompt,
            temperature=0.7,
            max_tokens=4096  # Menor - apenas resposta, não documento completo
        )

        print(f"[SPEC CHAT] LLM completed. Response length: {len(analysis_response)} chars")

        # 6. Update agent message with analysis (NO database modification)
        update_specification_chat_message(
            message_id=agent_message_id,
            message_text=analysis_response,
            metadata={'type': 'chat_response', 'status': 'completed'}
        )

        print(f"\n{'='*80}")
        print(f"[SPEC CHAT] ✅ ANÁLISE CONCLUÍDA!")
        print(f"[SPEC CHAT] Response: {len(analysis_response)} chars")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"[SPEC CHAT] ❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

        # Update agent message with error
        update_specification_chat_message(
            message_id=agent_message_id,
            message_text=f"❌ Erro ao processar análise: {str(e)}",
            metadata={'type': 'chat_response', 'status': 'error', 'error': str(e)}
        )
    except:
        pass


async def execute_specification_review(
    session_id: str,
    user_id: str
):
    """
    Execute automatic review of specification without modifying it
    Returns structured suggestions for improvement
    """
    try:
        print(f"\n{'='*80}")
        print(f"[SPEC REVIEW] 🔍 Starting review for session {session_id}")
        print(f"{'='*80}\n")

        # 1. Get current specification
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT specification_document
                FROM execution_specification_sessions
                WHERE id = %s
            """, (session_id,))
            result = cursor.fetchone()

            if not result or not result['specification_document']:
                raise ValueError("No specification document found")

            current_spec = result['specification_document']

        print(f"[SPEC REVIEW] Current specification size: {len(current_spec)} chars")

        # 2. Generate review prompt
        from prompts.review_specification import get_review_specification_prompt
        review_prompt = get_review_specification_prompt(current_spec)
        print(f"[SPEC REVIEW] Review prompt generated: {len(review_prompt)} chars")

        # 3. Call LLM for review
        llm_client = get_llm_client()
        print(f"[SPEC REVIEW] Calling LLM for analysis...")

        suggestions = await llm_client.complete_async(
            prompt=review_prompt,
            temperature=0.7,
            max_tokens=4096
        )

        print(f"[SPEC REVIEW] ✅ Review completed. Suggestions length: {len(suggestions)} chars")

        # 4. Save review message to chat history
        review_msg_id = save_specification_chat_message(
            session_id=session_id,
            sender_type='agent',
            message_text=suggestions,
            message_type='chat',
            sender_name='Agente Especificação - Revisão'
        )

        print(f"[SPEC REVIEW] ✅ Review message saved with ID: {review_msg_id}")

        return {
            "review_message_id": review_msg_id,
            "suggestions": suggestions,
            "status": "success",
            "message": "Revisão concluída com sucesso"
        }

    except Exception as e:
        print(f"[SPEC REVIEW] ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


# ============================================================
# REFINEMENT ENDPOINT
# ============================================================

@router.post("/{session_id}/refine")
async def refine_specification(
    session_id: str,
    request: RefineSpecificationRequest
):
    """
    Process specification chat message
    Supports two modes:
    - action_type="refine": Modifies specification document
    - action_type="chat": Analyzes and responds without modification
    No authentication required - token may expire during long spec generation
    """
    try:
        # Get session data
        with get_db_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                SELECT specification_document, requirements_session_id, user_id
                FROM execution_specification_sessions
                WHERE id = %s
            """, (session_id,))
            session = cursor.fetchone()
            cursor.close()

        if not session:
            raise HTTPException(status_code=404, detail="Specification session not found")

        current_specification = session.get('specification_document', '')
        requirements_session_id = session.get('requirements_session_id')
        user_id = session.get('user_id')

        if not current_specification:
            raise HTTPException(status_code=400, detail="No specification document found in session")

        # Save user message with action_type metadata
        user_message_id = save_specification_chat_message(
            session_id=session_id,
            sender_type='user',
            message_text=request.message,
            message_type='chat',
            sender_name='Você',
            parent_message_id=request.parent_message_id,
            metadata={'action_type': request.action_type, 'type': f'{request.action_type}_request'}
        )

        # Create agent initial response based on action type
        if request.action_type == "chat":
            agent_response = "🔍 Entendi sua solicitação de análise. Vou verificar a especificação..."
            metadata_type = 'chat_response'
        else:  # refine
            agent_response = "✏️ Entendi sua solicitação de refinamento. Vou processar as mudanças..."
            metadata_type = 'refinement_response'

        agent_message_id = save_specification_chat_message(
            session_id=session_id,
            sender_type='agent',
            message_text=agent_response,
            message_type='chat',
            sender_name='Agente Especificação',
            parent_message_id=user_message_id,
            metadata={'type': metadata_type, 'status': 'processing'}
        )

        agent_message = get_specification_chat_message(agent_message_id)

        # Execute appropriate workflow in background based on action_type
        if request.action_type == "chat":
            # CHAT MODE: Analyze without modifying
            asyncio.create_task(execute_specification_chat(
                session_id=session_id,
                user_message_id=user_message_id,
                agent_message_id=agent_message_id,
                chat_message=request.message,
                requirements_session_id=requirements_session_id
            ))
            print(f"[API] 💬 Chat analysis task spawned for session {session_id}")
            response_message = "Análise em processamento..."
        else:  # refine
            # REFINE MODE: Modify document (existing behavior)
            asyncio.create_task(execute_specification_refinement(
                session_id=session_id,
                refinement_instructions=request.message,
                current_specification=current_specification,
                requirements_session_id=requirements_session_id,
                agent_message_id=agent_message_id
            ))
            print(f"[API] ✏️ Refinement task spawned for session {session_id}")
            response_message = "Refinamento em processamento..."

        return {
            "user_message_id": user_message_id,
            "agent_message": agent_message,
            "action_type": request.action_type,
            "status": "processing",
            "message": response_message
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")


# ============================================================
# REVIEW ENDPOINT
# ============================================================

@router.post("/{session_id}/review")
async def review_specification(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Automatic review of specification - generates improvement suggestions
    Does NOT modify the document
    """
    try:
        user_id = current_user['id']

        # Verify session exists and belongs to user
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT id
                FROM execution_specification_sessions
                WHERE id = %s AND user_id = %s
            """, (session_id, user_id))

            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Session not found")

        # Execute review
        print(f"[API] 🔍 Review task starting for session {session_id}")

        # Call review function
        result = await execute_specification_review(session_id, user_id)

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error in review endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# CHAT HISTORY ENDPOINT
# ============================================================

@router.get("/{session_id}/chat-history")
async def get_chat_history(session_id: str):
    """Get chat history for specification session"""
    try:
        # Verify session exists
        with get_db_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                SELECT id FROM execution_specification_sessions WHERE id = %s
            """, (session_id,))
            if not cursor.fetchone():
                cursor.close()
                raise HTTPException(status_code=404, detail="Specification session not found")
            cursor.close()

        # Get messages
        messages = get_specification_chat_messages(session_id=session_id, limit=100)
        return {"messages": messages, "total": len(messages)}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# STATUS ENDPOINT
# ============================================================

@router.get("/{session_id}/status")
async def get_specification_status(session_id: str):
    """Get specification session status and document"""
    try:
        with get_db_connection() as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    id,
                    session_name,
                    status,
                    specification_document,
                    requirements_session_id,
                    requirements_version,
                    started_at,
                    finished_at,
                    updated_at
                FROM execution_specification_sessions
                WHERE id = %s
            """, (session_id,))
            session = cursor.fetchone()

            if not session:
                cursor.close()
                raise HTTPException(status_code=404, detail="Specification session not found")

            # Get latest version number
            cursor.execute("""
                SELECT MAX(version) as current_version
                FROM specification_version_history
                WHERE specification_session_id = %s
            """, (session_id,))
            version_result = cursor.fetchone()
            current_version = version_result['current_version'] if version_result and version_result['current_version'] else 1

            cursor.close()

        return {
            "session_id": session['id'],
            "session_name": session['session_name'],
            "status": session['status'],
            "specification_document": session['specification_document'],
            "doc_size": len(session['specification_document'] or ''),
            "current_version": current_version,
            "requirements_session_id": session['requirements_session_id'],
            "requirements_version": session['requirements_version'],
            "started_at": session['started_at'].isoformat() if session['started_at'] else None,
            "finished_at": session['finished_at'].isoformat() if session['finished_at'] else None,
            "updated_at": session['updated_at'].isoformat() if session['updated_at'] else None
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting specification status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
