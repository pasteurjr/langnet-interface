"""
API Router: Agents YAML Generation
Gera agents.yaml a partir de documentos MD de especificação de agentes/tarefas
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from app.database import (
    create_agents_yaml_session, get_agents_yaml_session, update_agents_yaml_session,
    list_agents_yaml_sessions, create_agents_yaml_version, get_agents_yaml_versions,
    save_agents_yaml_chat_message, get_agents_yaml_chat_messages,
    get_agent_task_spec_session  # Para buscar documento MD base
)
from app.routers.auth import get_current_user
from app.llm import get_llm_response_async
from prompts.generate_agents_yaml import get_agents_yaml_prompt
from prompts.review_agents_yaml import get_review_agents_yaml_prompt

router = APIRouter(prefix="/agents-yaml", tags=["agents-yaml"])


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
async def generate_agents_yaml(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Gera agents.yaml a partir de documento MD de agentes/tarefas
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
        "session_name": f"agents_yaml_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "status": "generating",
        "execution_metadata": {}
    }

    create_agents_yaml_session(session_data)

    # Background task
    background_tasks.add_task(
        execute_agents_yaml_generation,
        session_id,
        spec_session["agent_task_spec_document"],
        request.custom_instructions,
        user_id
    )

    return {
        "session_id": session_id,
        "status": "generating",
        "message": "Geração de agents.yaml iniciada"
    }


async def execute_agents_yaml_generation(
    session_id: str,
    agent_task_spec_document: str,
    custom_instructions: Optional[str],
    user_id: str
):
    """
    Background task: Gera agents.yaml via LLM
    """
    try:
        print(f"\n{'='*80}")
        print(f"[AGENTS_YAML] Starting generation for session {session_id}")
        print(f"{'='*80}\n")

        # Construir prompt
        prompt = get_agents_yaml_prompt(agent_task_spec_document, custom_instructions or "")

        print(f"[AGENTS_YAML] Calling LLM...")
        start_time = datetime.now()

        # LLM call
        agents_yaml_content = await get_llm_response_async(
            prompt=prompt,
            system="Você é um especialista em CrewAI e geração de arquivos YAML.",
            temperature=0.3,
            max_tokens=16000
        )

        end_time = datetime.now()
        generation_time_ms = int((end_time - start_time).total_seconds() * 1000)

        print(f"[AGENTS_YAML] ✅ Generated {len(agents_yaml_content)} chars in {generation_time_ms}ms")

        # Contar agentes (linhas terminando em _agent:)
        import re
        agent_matches = re.findall(r'^\w+_agent:', agents_yaml_content, re.MULTILINE)
        total_agents = len(agent_matches)

        # Atualizar sessão
        update_agents_yaml_session(session_id, {
            "status": "completed",
            "agents_yaml_content": agents_yaml_content,
            "total_agents": total_agents,
            "generation_time_ms": generation_time_ms,
            "finished_at": datetime.now()
        })

        # Salvar versão 1
        create_agents_yaml_version({
            "session_id": session_id,
            "version": 1,
            "agents_yaml_content": agents_yaml_content,
            "created_by": user_id,
            "change_type": "initial_generation",
            "change_description": "Geração inicial do agents.yaml",
            "doc_size": len(agents_yaml_content)
        })

        print(f"[AGENTS_YAML] ✅ Session completed: {total_agents} agents")

    except Exception as e:
        print(f"[AGENTS_YAML] ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

        update_agents_yaml_session(session_id, {
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
    session = get_agents_yaml_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    return session


# ═══════════════════════════════════════════════════════════
# LIST SESSIONS
# ═══════════════════════════════════════════════════════════

@router.get("/")
async def list_sessions(project_id: str):
    """
    Lista todas as sessões de agents.yaml de um projeto
    """
    sessions = list_agents_yaml_sessions(project_id)
    return {
        "sessions": sessions,
        "total": len(sessions)
    }


# ═══════════════════════════════════════════════════════════
# REFINAMENTO
# ═══════════════════════════════════════════════════════════

@router.post("/{session_id}/refine")
async def refine_agents_yaml(
    session_id: str,
    request: RefineRequest,
    background_tasks: BackgroundTasks
):
    """
    Refina agents.yaml via chat (ASYNC)
    """
    session = get_agents_yaml_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    if not session.get("agents_yaml_content"):
        raise HTTPException(status_code=400, detail="Nenhum YAML para refinar")

    # Salvar mensagem do usuário
    save_agents_yaml_chat_message({
        "session_id": session_id,
        "sender_type": "user",
        "message_text": request.message,
        "message_type": "chat"
    })

    # Background task
    background_tasks.add_task(
        execute_agents_yaml_refinement,
        session_id,
        request.message
    )

    return {
        "status": "refining",
        "message": "Refinamento iniciado"
    }


async def execute_agents_yaml_refinement(session_id: str, user_message: str):
    """
    Background: Refina agents.yaml com contexto completo
    Baseado em execute_refinement() de agent_task_spec.py
    """
    try:
        import re
        import time

        # 1. ATUALIZAR STATUS PARA 'GENERATING'
        update_agents_yaml_session(session_id, {
            "status": "generating"
        })

        # 2. BUSCAR SESSÃO ATUAL
        session = get_agents_yaml_session(session_id)
        if not session:
            raise Exception(f"Sessão {session_id} não encontrada")

        current_yaml = session.get("agents_yaml_content", "")

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
        from app.database import get_previous_agents_yaml_refinements

        previous_refinements = get_previous_agents_yaml_refinements(session_id, limit=10)

        # Formatar histórico
        refinement_history = ""
        if previous_refinements:
            refinement_history = "\n## REFINAMENTOS ANTERIORES:\n"
            for idx, ref in enumerate(previous_refinements, 1):
                refinement_history += f"\n**Refinamento {idx}:**\n{ref['message_text']}\n"

        # 5. SALVAR MENSAGEM DE PROGRESSO
        save_agents_yaml_chat_message({
            "session_id": session_id,
            "sender_type": "system",
            "message_text": "🔄 Processando refinamento...",
            "message_type": "progress"
        })

        # 6. CONSTRUIR PROMPT DE REFINAMENTO
        refinement_prompt = f"""# REFINAMENTO DE AGENTS.YAML CREWAI

Você é um especialista em CrewAI e configuração de agentes.

## AGENTS.YAML ATUAL

{current_yaml}

## ESPECIFICAÇÃO DE AGENTES/TAREFAS (REFERÊNCIA - NÃO REPRODUZA)

⚠️ **IMPORTANTE**: Use apenas como CONTEXTO. NÃO reproduza este documento.

{agent_task_spec_document[:15000] if agent_task_spec_document else "Não disponível"}

{refinement_history}

## SOLICITAÇÃO DE REFINAMENTO

{user_message}

## INSTRUÇÕES CRÍTICAS

1. **Mantenha a estrutura**: Preserve EXATAMENTE a estrutura YAML existente
2. **Mantenha IDs de agentes**: NÃO altere nomes de agentes já definidos (ex: `research_agent:`)
3. **Aplique APENAS as mudanças solicitadas**: NÃO faça modificações não pedidas
4. **Seja CIRÚRGICO**: Modifique APENAS o que foi solicitado, mantendo todo o resto IDÊNTICO
5. **Formato YAML válido**: Use `>` para textos multiline, identação de 2 espaços
6. **NÃO EXPANDA**: NÃO adicione explicações extras ou agentes não solicitados
7. **TAMANHO**: O YAML refinado deve ter tamanho SIMILAR ao original (~{len(current_yaml)} caracteres)

⚠️ **CRÍTICO**:
- NÃO reproduza a especificação de agentes/tarefas
- NÃO adicione comentários YAML desnecessários
- NÃO expanda descrições desnecessariamente
- Seja CONCISO e OBJETIVO

## OUTPUT

Retorne APENAS o agents.yaml COMPLETO com as modificações aplicadas.
NÃO adicione preâmbulos, explicações ou conclusões.

Gere agora o agents.yaml refinado:
"""

        # 7. CHAMAR LLM ASSÍNCRONO
        start_time = time.time()

        print(f"[AGENTS_YAML_REFINE] 📝 Refinando YAML: {len(user_message)} chars de solicitação")

        refined_yaml = await get_llm_response_async(
            prompt=refinement_prompt,
            system="Você é um especialista em CrewAI e configuração de agentes.",
            temperature=0.3,
            max_tokens=16000
        )

        generation_time_ms = int((time.time() - start_time) * 1000)

        print(f"[AGENTS_YAML_REFINE] ✅ LLM retornou: {len(refined_yaml)} chars em {generation_time_ms/1000:.1f}s")

        # 8. CONTAR AGENTES
        total_agents = len(re.findall(r'^\w+_agent:', refined_yaml, re.MULTILINE))

        # 9. BUSCAR PRÓXIMA VERSÃO
        versions = get_agents_yaml_versions(session_id)
        current_version = max([v["version"] for v in versions]) if versions else 0
        new_version = current_version + 1

        # 10. ATUALIZAR SESSÃO
        update_agents_yaml_session(session_id, {
            "agents_yaml_content": refined_yaml,
            "total_agents": total_agents,
            "status": "completed",
            "finished_at": datetime.now(),
            "generation_time_ms": generation_time_ms
        })

        # 11. CRIAR NOVA VERSÃO
        create_agents_yaml_version({
            "session_id": session_id,
            "version": new_version,
            "agents_yaml_content": refined_yaml,
            "created_by": None,
            "change_type": "ai_refinement",
            "change_description": user_message[:500],
            "doc_size": len(refined_yaml)
        })

        print(f"[AGENTS_YAML_REFINE] 📦 Versão {new_version} criada: {total_agents} agentes")

        # 12. SALVAR MENSAGEM DE SUCESSO
        save_agents_yaml_chat_message({
            "session_id": session_id,
            "sender_type": "agent",
            "message_text": f"✅ YAML refinado com sucesso!\n\n📊 {total_agents} agentes.\n📌 Versão {new_version} criada.",
            "message_type": "result"
        })

    except Exception as e:
        # SALVAR ERRO
        print(f"[AGENTS_YAML_REFINE] ❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

        update_agents_yaml_session(session_id, {
            "status": "failed",
            "finished_at": datetime.now()
        })


# ═══════════════════════════════════════════════════════════
# REVISÃO (REVIEW)
# ═══════════════════════════════════════════════════════════

@router.post("/{session_id}/review")
async def review_agents_yaml(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Revisa agents.yaml e retorna sugestões (SÍNCRONO)
    """
    session = get_agents_yaml_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    if not session.get("agents_yaml_content"):
        raise HTTPException(status_code=400, detail="Nenhum YAML para revisar")

    try:
        print(f"[AGENTS_YAML_REVIEW] Session {session_id}")

        # Prompt de revisão
        prompt = get_review_agents_yaml_prompt(session["agents_yaml_content"])

        suggestions = await get_llm_response_async(
            prompt=prompt,
            system="Você é um especialista em análise de agents.yaml CrewAI.",
            temperature=0.7,
            max_tokens=4096
        )

        # Salvar mensagem de revisão
        review_msg_id = str(uuid.uuid4())
        save_agents_yaml_chat_message({
            "id": review_msg_id,
            "session_id": session_id,
            "sender_type": "agent",
            "message_text": suggestions,
            "message_type": "chat"
        })

        print(f"[AGENTS_YAML_REVIEW] ✅ Review completed")

        return {
            "review_message_id": review_msg_id,
            "suggestions": suggestions,
            "status": "success",
            "message": "Revisão concluída"
        }

    except Exception as e:
        print(f"[AGENTS_YAML_REVIEW] ❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# VERSÕES
# ═══════════════════════════════════════════════════════════

@router.get("/{session_id}/versions")
async def get_versions(session_id: str):
    """
    Lista todas as versões de agents.yaml
    """
    versions = get_agents_yaml_versions(session_id)
    return versions


# ═══════════════════════════════════════════════════════════
# CHAT HISTORY
# ═══════════════════════════════════════════════════════════

@router.get("/{session_id}/chat-history")
async def get_chat_history(session_id: str):
    """
    Retorna histórico de chat
    """
    messages = get_agents_yaml_chat_messages(session_id)
    return {
        "messages": messages,
        "total": len(messages)
    }
