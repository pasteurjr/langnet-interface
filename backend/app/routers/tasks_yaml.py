"""
API Router: Tasks YAML Generation
Gera tasks.yaml a partir de documentos MD de especificação de agentes/tarefas
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from app.database import (
    create_tasks_yaml_session, get_tasks_yaml_session, update_tasks_yaml_session,
    list_tasks_yaml_sessions, create_tasks_yaml_version, get_tasks_yaml_versions,
    save_tasks_yaml_chat_message, get_tasks_yaml_chat_messages,
    get_agent_task_spec_session  # Para buscar documento MD base
)
from app.routers.auth import get_current_user
from app.llm import get_llm_response_async
from prompts.generate_tasks_yaml import get_tasks_yaml_prompt
from prompts.review_tasks_yaml import get_review_tasks_yaml_prompt

router = APIRouter(prefix="/tasks-yaml", tags=["tasks-yaml"])


# ═══════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════

class GenerateRequest(BaseModel):
    agent_task_spec_session_id: str
    agent_task_spec_version: int = 1
    custom_instructions: Optional[str] = None


class RefineRequest(BaseModel):
    message: str
    action_type: str = "refine"


# ═══════════════════════════════════════════════════════════
# GERAÇÃO INICIAL
# ═══════════════════════════════════════════════════════════

@router.post("/")
async def generate_tasks_yaml(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Gera tasks.yaml a partir de documento MD de agentes/tarefas
    """
    user_id = current_user['id']
    session_id = str(uuid.uuid4())

    # Buscar documento MD base
    spec_session = get_agent_task_spec_session(request.agent_task_spec_session_id)
    if not spec_session:
        raise HTTPException(status_code=404, detail="Especificação de agentes/tarefas não encontrada")

    if not spec_session.get("agent_task_spec_document"):
        raise HTTPException(status_code=400, detail="Documento de especificação vazio")

    # Criar sessão
    session_data = {
        "id": session_id,
        "project_id": spec_session["project_id"],
        "user_id": user_id,
        "agent_task_spec_session_id": request.agent_task_spec_session_id,
        "agent_task_spec_version": request.agent_task_spec_version,
        "session_name": f"tasks_yaml_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "status": "generating",
        "execution_metadata": {}
    }

    create_tasks_yaml_session(session_data)

    # Busca schema_sql do Data Model mais recente do projeto — permite ao LLM
    # gerar Process steps SQL corretos respeitando o schema real das tabelas.
    _schema_sql = ""
    try:
        from app.database import get_db_connection as _gdb
        with _gdb() as _c:
            _cur = _c.cursor(dictionary=True)
            _cur.execute("""
                SELECT schema_sql FROM data_model_sessions
                WHERE project_id=%s AND schema_sql IS NOT NULL
                  AND CHAR_LENGTH(schema_sql) > 0
                ORDER BY created_at DESC LIMIT 1
            """, (spec_session["project_id"],))
            _r = _cur.fetchone()
            if _r:
                _schema_sql = _r["schema_sql"]
            _cur.close()
    except Exception as _e:
        print(f"[TASKS_YAML] warning: falha ao carregar schema: {_e}")

    # Background task
    background_tasks.add_task(
        execute_tasks_yaml_generation,
        session_id,
        spec_session["agent_task_spec_document"],
        request.custom_instructions,
        user_id,
        _schema_sql,
    )

    return {
        "session_id": session_id,
        "status": "generating",
        "message": "Geração de tasks.yaml iniciada"
    }


async def execute_tasks_yaml_generation(
    session_id: str,
    agent_task_spec_document: str,
    custom_instructions: Optional[str],
    user_id: str,
    data_model_schema_sql: str = "",
):
    """
    Background task: Gera tasks.yaml via LLM
    """
    try:
        print(f"\n{'='*80}")
        print(f"[TASKS_YAML] Starting generation for session {session_id}")
        print(f"[TASKS_YAML] schema_sql: {len(data_model_schema_sql)} chars")
        print(f"{'='*80}\n")

        # Construir prompt
        prompt = get_tasks_yaml_prompt(
            agent_task_spec_document,
            custom_instructions or "",
            data_model_schema_sql=data_model_schema_sql,
        )

        print(f"[TASKS_YAML] Calling LLM...")
        start_time = datetime.now()

        # LLM call
        tasks_yaml_content = await get_llm_response_async(
            prompt=prompt,
            system="Você é um especialista em CrewAI e geração de arquivos YAML.",
            temperature=0.3,
            max_tokens=16000
        )

        end_time = datetime.now()
        generation_time_ms = int((end_time - start_time).total_seconds() * 1000)

        print(f"[TASKS_YAML] ✅ Generated {len(tasks_yaml_content)} chars in {generation_time_ms}ms")

        # Contar tasks (linhas terminando com :)
        import re
        task_matches = re.findall(r'^[a-z_]+:', tasks_yaml_content, re.MULTILINE)
        # Filtrar para contar apenas tasks (não 'description' ou 'expected_output')
        total_tasks = len([t for t in task_matches if not t.startswith(('description:', 'expected_output:'))])

        # Atualizar sessão
        update_tasks_yaml_session(session_id, {
            "status": "completed",
            "tasks_yaml_content": tasks_yaml_content,
            "total_tasks": total_tasks,
            "generation_time_ms": generation_time_ms,
            "finished_at": datetime.now()
        })

        # Salvar versão 1
        create_tasks_yaml_version({
            "session_id": session_id,
            "version": 1,
            "tasks_yaml_content": tasks_yaml_content,
            "created_by": user_id,
            "change_type": "initial_generation",
            "change_description": "Geração inicial do tasks.yaml",
            "doc_size": len(tasks_yaml_content)
        })

        print(f"[TASKS_YAML] ✅ Session completed: {total_tasks} tasks")

    except Exception as e:
        print(f"[TASKS_YAML] ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

        update_tasks_yaml_session(session_id, {
            "status": "failed",
            "generation_log": str(e)
        })


# ═══════════════════════════════════════════════════════════
# GET SESSION
# ═══════════════════════════════════════════════════════════

@router.get("/{session_id}")
async def get_session(session_id: str):
    """
    Retorna dados da sessão (usado para polling)
    """
    session = get_tasks_yaml_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    return session


# ═══════════════════════════════════════════════════════════
# LIST SESSIONS
# ═══════════════════════════════════════════════════════════

@router.get("/")
async def list_sessions(project_id: str):
    """
    Lista todas as sessões de tasks.yaml de um projeto
    """
    sessions = list_tasks_yaml_sessions(project_id)
    return {
        "sessions": sessions,
        "total": len(sessions)
    }


# ═══════════════════════════════════════════════════════════
# REFINAMENTO
# ═══════════════════════════════════════════════════════════

@router.post("/{session_id}/refine")
async def refine_tasks_yaml(
    session_id: str,
    request: RefineRequest,
    background_tasks: BackgroundTasks
):
    """
    Refina tasks.yaml via chat (ASYNC)
    """
    session = get_tasks_yaml_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    if not session.get("tasks_yaml_content"):
        raise HTTPException(status_code=400, detail="Nenhum YAML para refinar")

    # Salvar mensagem do usuário
    save_tasks_yaml_chat_message({
        "session_id": session_id,
        "sender_type": "user",
        "message_text": request.message,
        "message_type": "chat"
    })

    # Background task
    background_tasks.add_task(
        execute_tasks_yaml_refinement,
        session_id,
        request.message
    )

    return {
        "status": "refining",
        "message": "Refinamento iniciado"
    }


async def execute_tasks_yaml_refinement(session_id: str, user_message: str):
    """
    Background: Refina tasks.yaml com contexto completo
    Baseado em execute_refinement() de agent_task_spec.py
    """
    try:
        import re
        import time

        # 1. ATUALIZAR STATUS PARA 'GENERATING'
        update_tasks_yaml_session(session_id, {
            "status": "generating"
        })

        # 2. BUSCAR SESSÃO ATUAL
        session = get_tasks_yaml_session(session_id)
        if not session:
            raise Exception(f"Sessão {session_id} não encontrada")

        current_yaml = session.get("tasks_yaml_content", "")

        # 3. BUSCAR DOCUMENTO MD BASE (ESPECIFICAÇÃO DE AGENTES/TAREFAS)
        agent_task_spec_document = ""
        if session.get("agent_task_spec_session_id"):
            from app.database import get_db_connection
            with get_db_connection() as db:
                cursor = db.cursor(dictionary=True)
                cursor.execute("""
                    SELECT agent_task_spec_document
                    FROM agent_task_specification_sessions
                    WHERE id = %s
                    LIMIT 1
                """, (session["agent_task_spec_session_id"],))
                spec_result = cursor.fetchone()
                cursor.close()

                if spec_result:
                    agent_task_spec_document = spec_result.get("agent_task_spec_document", "")

        # 4. BUSCAR REFINAMENTOS ANTERIORES (HISTÓRICO)
        from app.database import get_previous_tasks_yaml_refinements

        previous_refinements = get_previous_tasks_yaml_refinements(session_id, limit=10)

        # Formatar histórico
        refinement_history = ""
        if previous_refinements:
            refinement_history = "\n## REFINAMENTOS ANTERIORES:\n"
            for idx, ref in enumerate(previous_refinements, 1):
                refinement_history += f"\n**Refinamento {idx}:**\n{ref['message_text']}\n"

        # 5. SALVAR MENSAGEM DE PROGRESSO
        save_tasks_yaml_chat_message({
            "session_id": session_id,
            "sender_type": "system",
            "message_text": "🔄 Processando refinamento...",
            "message_type": "progress"
        })

        # 6. CONSTRUIR PROMPT DE REFINAMENTO
        refinement_prompt = f"""# REFINAMENTO DE TASKS.YAML CREWAI

Você é um especialista em CrewAI e configuração de tarefas.

## TASKS.YAML ATUAL

{current_yaml}

## ESPECIFICAÇÃO DE AGENTES/TAREFAS (REFERÊNCIA - NÃO REPRODUZA)

⚠️ **IMPORTANTE**: Use apenas como CONTEXTO. NÃO reproduza este documento.

{agent_task_spec_document[:15000] if agent_task_spec_document else "Não disponível"}

{refinement_history}

## SOLICITAÇÃO DE REFINAMENTO

{user_message}

## INSTRUÇÕES CRÍTICAS

1. **Mantenha a estrutura**: Preserve EXATAMENTE a estrutura YAML existente
2. **Mantenha IDs de tasks**: NÃO altere nomes de tarefas já definidas
3. **Aplique APENAS as mudanças solicitadas**: NÃO faça modificações não pedidas
4. **Seja CIRÚRGICO**: Modifique APENAS o que foi solicitado, mantendo todo o resto IDÊNTICO
5. **Formato YAML válido**: Use `>` para textos multiline, identação de 2 espaços
6. **Expected_output**: SEMPRE textual (não JSON literal)
7. **NÃO EXPANDA**: NÃO adicione explicações extras ou tarefas não solicitadas
8. **TAMANHO**: O YAML refinado deve ter tamanho SIMILAR ao original (~{len(current_yaml)} caracteres)

⚠️ **CRÍTICO**:
- NÃO reproduza a especificação de agentes/tarefas
- NÃO adicione comentários YAML desnecessários
- NÃO expanda descrições desnecessariamente
- Seja CONCISO e OBJETIVO

## OUTPUT

Retorne APENAS o tasks.yaml COMPLETO com as modificações aplicadas.
NÃO adicione preâmbulos, explicações ou conclusões.

Gere agora o tasks.yaml refinado:
"""

        # 7. CHAMAR LLM ASSÍNCRONO
        start_time = time.time()

        print(f"[TASKS_YAML_REFINE] 📝 Refinando YAML: {len(user_message)} chars de solicitação")

        refined_yaml = await get_llm_response_async(
            prompt=refinement_prompt,
            system="Você é um especialista em CrewAI e configuração de tarefas.",
            temperature=0.3,
            max_tokens=16000
        )

        generation_time_ms = int((time.time() - start_time) * 1000)

        print(f"[TASKS_YAML_REFINE] ✅ LLM retornou: {len(refined_yaml)} chars em {generation_time_ms/1000:.1f}s")

        # 8. CONTAR TASKS
        task_matches = re.findall(r'^[a-z_]+:', refined_yaml, re.MULTILINE)
        total_tasks = len([t for t in task_matches if not t.startswith(('description:', 'expected_output:'))])

        # 9. BUSCAR PRÓXIMA VERSÃO
        versions = get_tasks_yaml_versions(session_id)
        current_version = max([v["version"] for v in versions]) if versions else 0
        new_version = current_version + 1

        # 10. ATUALIZAR SESSÃO
        update_tasks_yaml_session(session_id, {
            "tasks_yaml_content": refined_yaml,
            "total_tasks": total_tasks,
            "status": "completed",
            "finished_at": datetime.now(),
            "generation_time_ms": generation_time_ms
        })

        # 11. CRIAR NOVA VERSÃO
        create_tasks_yaml_version({
            "session_id": session_id,
            "version": new_version,
            "tasks_yaml_content": refined_yaml,
            "created_by": None,
            "change_type": "ai_refinement",
            "change_description": user_message[:500],
            "doc_size": len(refined_yaml)
        })

        print(f"[TASKS_YAML_REFINE] 📦 Versão {new_version} criada: {total_tasks} tarefas")

        # 12. SALVAR MENSAGEM DE SUCESSO
        save_tasks_yaml_chat_message({
            "session_id": session_id,
            "sender_type": "agent",
            "message_text": f"✅ YAML refinado com sucesso!\n\n📊 {total_tasks} tarefas.\n📌 Versão {new_version} criada.",
            "message_type": "result"
        })

    except Exception as e:
        # SALVAR ERRO
        print(f"[TASKS_YAML_REFINE] ❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

        update_tasks_yaml_session(session_id, {
            "status": "failed",
            "finished_at": datetime.now()
        })


# ═══════════════════════════════════════════════════════════
# REVISÃO (REVIEW)
# ═══════════════════════════════════════════════════════════

@router.post("/{session_id}/review")
async def review_tasks_yaml(
    session_id: str
):
    """
    Revisa tasks.yaml e retorna sugestões (SÍNCRONO - sem autenticação para evitar expiração)
    """
    session = get_tasks_yaml_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    if not session.get("tasks_yaml_content"):
        raise HTTPException(status_code=400, detail="Nenhum YAML para revisar")

    try:
        print(f"[TASKS_YAML_REVIEW] Session {session_id}")

        # Prompt de revisão
        prompt = get_review_tasks_yaml_prompt(session["tasks_yaml_content"])

        suggestions = await get_llm_response_async(
            prompt=prompt,
            system="Você é um especialista em análise de tasks.yaml CrewAI.",
            temperature=0.7,
            max_tokens=4096
        )

        # Salvar mensagem de revisão
        review_msg_id = str(uuid.uuid4())
        save_tasks_yaml_chat_message({
            "id": review_msg_id,
            "session_id": session_id,
            "sender_type": "agent",
            "message_text": suggestions,
            "message_type": "chat"
        })

        print(f"[TASKS_YAML_REVIEW] ✅ Review completed")

        return {
            "review_message_id": review_msg_id,
            "suggestions": suggestions,
            "status": "success",
            "message": "Revisão concluída"
        }

    except Exception as e:
        print(f"[TASKS_YAML_REVIEW] ❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# VERSÕES
# ═══════════════════════════════════════════════════════════

@router.get("/{session_id}/versions")
async def get_versions(session_id: str):
    """
    Lista todas as versões de tasks.yaml
    """
    versions = get_tasks_yaml_versions(session_id)
    return {
        "versions": versions,
        "total": len(versions)
    }


# ═══════════════════════════════════════════════════════════
# CHAT HISTORY
# ═══════════════════════════════════════════════════════════

@router.get("/{session_id}/chat-history")
async def get_chat_history(session_id: str):
    """
    Retorna histórico de chat
    """
    messages = get_tasks_yaml_chat_messages(session_id)
    return {
        "messages": messages,
        "total": len(messages)
    }
