"""
Agent Task Specification Router
================================
Endpoints para geração e refinamento de especificação de agentes/tarefas
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
import asyncio
import uuid
from datetime import datetime
import json
import time

from app.models.agent_task_spec import (
    GenerateAgentTaskSpecRequest,
    RefineAgentTaskSpecRequest,
    AgentTaskSpecResponse,
    AgentTaskSpecVersionResponse,
    ChatMessageResponse,
    AgentTaskSpecListResponse,
    AgentTaskSpecStatus,
    ApprovalStatus
)
from app.database import (
    create_agent_task_spec_session,
    get_agent_task_spec_session,
    update_agent_task_spec_session,
    list_agent_task_spec_sessions,
    create_agent_task_spec_version,
    get_agent_task_spec_versions,
    save_agent_task_spec_chat_message,
    get_agent_task_spec_chat_messages,
    get_db_connection,
    get_db_cursor
)
from app.llm import get_llm_response_async
from app.dependencies import get_current_user
from prompts.agent_task_spec_prompt import build_agent_task_spec_prompt


router = APIRouter(
    prefix="/agent-task-spec",
    tags=["Agent Task Specification"]
)


# ═══════════════════════════════════════════════════════════
# GERAÇÃO
# ═══════════════════════════════════════════════════════════

@router.post("/", response_model=AgentTaskSpecResponse)
async def generate_agent_task_spec(
    request: GenerateAgentTaskSpecRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Gera documento de especificação de agentes e tarefas a partir de especificação funcional

    Retorna session_id imediatamente e executa geração em background
    """

    # 1. Validar que specification_session_id existe e buscar project_id
    with get_db_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT project_id, specification_document
            FROM execution_specification_sessions
            WHERE id = %s
            LIMIT 1
        """, (request.specification_session_id,))
        spec_session = cursor.fetchone()
        cursor.close()

    if not spec_session:
        raise HTTPException(status_code=404, detail="Especificação funcional não encontrada")

    # 2. Criar sessão de geração
    session_id = str(uuid.uuid4())
    session_name = f"Espec Agentes - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    session_data = {
        "id": session_id,
        "project_id": spec_session["project_id"],
        "user_id": current_user["id"],
        "specification_session_id": request.specification_session_id,
        "specification_version": request.specification_version,
        "session_name": session_name,
        "status": AgentTaskSpecStatus.GENERATING.value,
        "execution_metadata": {
            "detail_level": request.detail_level.value,
            "frameworks": request.frameworks,
            "max_agents": request.max_agents,
            "custom_instructions": request.custom_instructions
        }
    }

    create_agent_task_spec_session(session_data)

    # 3. Lançar background task para geração
    background_tasks.add_task(
        execute_agent_task_spec_generation,
        session_id=session_id,
        request=request,
        user_id=current_user["id"]
    )

    # 4. Retornar session_id imediatamente
    return AgentTaskSpecResponse(
        session_id=session_id,
        session_name=session_name,
        status=AgentTaskSpecStatus.GENERATING,
        approval_status=ApprovalStatus.PENDING,
        message="Geração iniciada. Acompanhe o progresso via chat.",
        created_at=datetime.now()
    )


async def execute_agent_task_spec_generation(
    session_id: str,
    request: GenerateAgentTaskSpecRequest,
    user_id: str
):
    """
    Executa geração de especificação de agentes/tarefas em background
    """

    try:
        # 1. Buscar especificação funcional
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT specification_document
                FROM execution_specification_sessions
                WHERE id = %s
                LIMIT 1
            """, (request.specification_session_id,))
            spec_session = cursor.fetchone()
            cursor.close()

        if not spec_session or not spec_session.get("specification_document"):
            raise ValueError("Especificação funcional não encontrada ou não possui documento gerado")

        spec_document = spec_session["specification_document"]

        # 2. Construir prompt
        prompt = build_agent_task_spec_prompt(
            specification_document=spec_document,
            detail_level=request.detail_level.value,
            max_agents=request.max_agents,
            frameworks=request.frameworks,
            custom_instructions=request.custom_instructions
        )

        # 3. Salvar mensagem de início
        save_agent_task_spec_chat_message({
            "session_id": session_id,
            "sender_type": "system",
            "message_text": "🚀 Gerando especificação de agentes e tarefas...",
            "message_type": "status"
        })

        # 4. Chamar LLM (async)
        start_time = datetime.now()

        print(f"[AGENT_TASK_SPEC] 📝 Tamanho do prompt: {len(prompt)} caracteres")
        print(f"[AGENT_TASK_SPEC] 📝 Tamanho da spec funcional: {len(spec_document)} caracteres")
        print(f"[AGENT_TASK_SPEC] 🤖 Chamando LLM com max_tokens=65536...")

        agent_task_spec_document = await get_llm_response_async(
            prompt=prompt,
            system="Você é um arquiteto de sistemas multi-agente especializado em CrewAI.",
            temperature=0.7,
            max_tokens=65536  # DeepSeek-Reasoner suporta até 64K em thinking mode
        )

        end_time = datetime.now()
        generation_time_ms = int((end_time - start_time).total_seconds() * 1000)

        print(f"[AGENT_TASK_SPEC] ✅ LLM retornou! Tamanho: {len(agent_task_spec_document)} caracteres")
        print(f"[AGENT_TASK_SPEC] ⏱️ Tempo: {generation_time_ms / 1000:.1f}s")

        # 5. Parsear contadores (contar ## em Markdown)
        total_agents = agent_task_spec_document.count("#### AG-")  # Contadores de seções de agentes
        total_tasks = agent_task_spec_document.count("#### T-")    # Contadores de seções de tasks

        # 6. Atualizar sessão
        update_agent_task_spec_session(session_id, {
            "status": AgentTaskSpecStatus.COMPLETED.value,
            "agent_task_spec_document": agent_task_spec_document,
            "total_agents": total_agents,
            "total_tasks": total_tasks,
            "generation_time_ms": generation_time_ms,
            "ai_model_used": "deepseek-reasoner",
            "finished_at": datetime.now()
        })

        # 7. Criar versão 1
        create_agent_task_spec_version({
            "session_id": session_id,
            "version": 1,
            "agent_task_spec_document": agent_task_spec_document,
            "created_by": user_id,
            "change_type": "initial_generation",
            "doc_size": len(agent_task_spec_document.encode('utf-8'))
        })

        # 8. Salvar mensagem de sucesso
        save_agent_task_spec_chat_message({
            "session_id": session_id,
            "sender_type": "system",
            "message_text": f"✅ Especificação gerada com sucesso!\n\n📊 {total_agents} agentes e {total_tasks} tarefas especificados.\n⏱️ Tempo: {generation_time_ms / 1000:.1f}s",
            "message_type": "result"
        })

    except Exception as e:
        # Salvar erro
        update_agent_task_spec_session(session_id, {
            "status": AgentTaskSpecStatus.FAILED.value,
            "finished_at": datetime.now()
        })

        save_agent_task_spec_chat_message({
            "session_id": session_id,
            "sender_type": "system",
            "message_text": f"❌ Erro na geração: {str(e)}",
            "message_type": "error"
        })


# ═══════════════════════════════════════════════════════════
# CONSULTA
# ═══════════════════════════════════════════════════════════

@router.get("/sessions", response_model=AgentTaskSpecListResponse)
async def list_agent_task_spec_sessions_endpoint(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Lista todas as sessões de especificação de agentes/tarefas de um projeto"""

    sessions = list_agent_task_spec_sessions(project_id)

    return AgentTaskSpecListResponse(
        sessions=[
            AgentTaskSpecResponse(
                session_id=session["id"],
                session_name=session["session_name"],
                agent_task_spec_document=session.get("agent_task_spec_document"),
                total_agents=session.get("total_agents", 0),
                total_tasks=session.get("total_tasks", 0),
                status=AgentTaskSpecStatus(session["status"]),
                approval_status=ApprovalStatus(session.get("approval_status", "pending")),
                message=f"{session.get('total_agents', 0)} agentes, {session.get('total_tasks', 0)} tarefas",
                created_at=session["created_at"]
            ) for session in sessions
        ],
        total=len(sessions)
    )


@router.get("/{session_id}", response_model=AgentTaskSpecResponse)
async def get_agent_task_spec_session_endpoint(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtém sessão específica de especificação"""

    session = get_agent_task_spec_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    return AgentTaskSpecResponse(
        session_id=session["id"],
        session_name=session["session_name"],
        agent_task_spec_document=session.get("agent_task_spec_document"),
        total_agents=session.get("total_agents", 0),
        total_tasks=session.get("total_tasks", 0),
        status=AgentTaskSpecStatus(session["status"]),
        approval_status=ApprovalStatus(session.get("approval_status", "pending")),
        message=f"{session.get('total_agents', 0)} agentes, {session.get('total_tasks', 0)} tarefas",
        created_at=session["created_at"]
    )


@router.get("/{session_id}/versions", response_model=List[AgentTaskSpecVersionResponse])
async def get_version_history(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtém histórico de versões"""

    versions = get_agent_task_spec_versions(session_id)

    return [
        AgentTaskSpecVersionResponse(
            session_id=version["session_id"],
            version=version["version"],
            agent_task_spec_document=version["agent_task_spec_document"],
            created_at=version["created_at"],
            change_type=version["change_type"],
            change_description=version.get("change_description")
        ) for version in versions
    ]


@router.get("/{session_id}/chat-history", response_model=List[ChatMessageResponse])
async def get_chat_history(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtém histórico de chat"""

    messages = get_agent_task_spec_chat_messages(session_id, limit=100)

    return [
        ChatMessageResponse(
            id=msg["id"],
            session_id=msg["session_id"],
            sender_type=msg["sender_type"],
            message_text=msg["message_text"],
            message_type=msg["message_type"],
            timestamp=msg["timestamp"]
        ) for msg in messages
    ]


# ═══════════════════════════════════════════════════════════
# REFINAMENTO
# ═══════════════════════════════════════════════════════════

@router.post("/{session_id}/refine", response_model=AgentTaskSpecResponse)
async def refine_agent_task_spec(
    session_id: str,
    request: RefineAgentTaskSpecRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Refina documento de especificação via chat

    action_type='refine': Modifica documento e cria nova versão
    action_type='chat': Apenas responde sem modificar
    """

    session = get_agent_task_spec_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    # Salvar mensagem do usuário
    save_agent_task_spec_chat_message({
        "session_id": session_id,
        "sender_type": "user",
        "message_text": request.message,
        "message_type": "chat"
    })

    if request.action_type == "refine":
        # Atualizar status para reviewing
        update_agent_task_spec_session(session_id, {
            "status": AgentTaskSpecStatus.REVIEWING.value
        })

        background_tasks.add_task(
            execute_refinement,
            session_id=session_id,
            message=request.message,
            user_id=current_user["id"]
        )
    else:
        # Chat mode: apenas responder sem modificar
        background_tasks.add_task(
            execute_chat,
            session_id=session_id,
            message=request.message
        )

    return AgentTaskSpecResponse(
        session_id=session["id"],
        session_name=session["session_name"],
        agent_task_spec_document=session.get("agent_task_spec_document"),
        total_agents=session.get("total_agents", 0),
        total_tasks=session.get("total_tasks", 0),
        status=AgentTaskSpecStatus(session["status"]),
        approval_status=ApprovalStatus(session.get("approval_status", "pending")),
        message="Processando refinamento...",
        created_at=session["created_at"]
    )


async def execute_refinement(session_id: str, message: str, user_id: str):
    """
    Executa refinamento do documento de especificação de agentes/tarefas
    Baseado em execute_specification_refinement() de specification.py
    """
    try:
        # 1. ATUALIZAR STATUS PARA 'GENERATING'
        update_agent_task_spec_session(session_id, {
            "status": AgentTaskSpecStatus.GENERATING.value
        })

        # 2. BUSCAR SESSÃO ATUAL
        session = get_agent_task_spec_session(session_id)
        if not session:
            raise Exception(f"Sessão {session_id} não encontrada")

        current_document = session.get("agent_task_spec_document", "")

        # 3. BUSCAR ESPECIFICAÇÃO FUNCIONAL (CONTEXTO)
        specification_document = ""
        if session.get("specification_session_id"):
            from app.database import get_db_connection
            with get_db_connection() as db:
                cursor = db.cursor(dictionary=True)
                cursor.execute("""
                    SELECT specification_document
                    FROM execution_specification_sessions
                    WHERE id = %s
                    LIMIT 1
                """, (session["specification_session_id"],))
                spec_result = cursor.fetchone()
                cursor.close()

                if spec_result:
                    specification_document = spec_result.get("specification_document", "")

        # 4. BUSCAR REFINAMENTOS ANTERIORES (HISTÓRICO)
        from app.database import get_previous_agent_task_spec_refinements

        previous_refinements = get_previous_agent_task_spec_refinements(session_id, limit=10)

        # Formatar histórico
        refinement_history = ""
        if previous_refinements:
            refinement_history = "\n## REFINAMENTOS ANTERIORES:\n"
            for idx, ref in enumerate(previous_refinements, 1):
                refinement_history += f"\n**Refinamento {idx}:**\n{ref['message_text']}\n"

        # 5. SALVAR MENSAGEM DE PROGRESSO
        save_agent_task_spec_chat_message({
            "session_id": session_id,
            "sender_type": "system",
            "message_text": "🔄 Processando refinamento...",
            "message_type": "progress"
        })

        # 6. CONSTRUIR PROMPT DE REFINAMENTO
        refinement_prompt = f"""# REFINAMENTO DE ESPECIFICAÇÃO DE AGENTES E TAREFAS

Você é um arquiteto de sistemas multi-agente especializado em CrewAI.

## DOCUMENTO ATUAL DE ESPECIFICAÇÃO

{current_document}

## ESPECIFICAÇÃO FUNCIONAL (REFERÊNCIA - NÃO REPRODUZA)

⚠️ **IMPORTANTE**: Use apenas como CONTEXTO. NÃO reproduza este documento.

{specification_document[:15000] if specification_document else "Não disponível"}

{refinement_history}

## SOLICITAÇÃO DE REFINAMENTO

{message}

## INSTRUÇÕES CRÍTICAS

1. **Mantenha a estrutura**: Preserve todas as 5 seções (Visão Geral, Agentes, Tarefas, Rastreabilidade, Grafo)
2. **Mantenha IDs existentes**: Não altere IDs de agentes (AG-XX) ou tasks (T-XXX-XXX) já definidos
3. **Aplique APENAS as mudanças solicitadas**: Não faça modificações não pedidas
4. **Rastreabilidade**: Se adicionar tasks, mapeie para UC e RF da especificação funcional
5. **Formato Markdown**: Mantenha tabelas bem formatadas
6. **Dependencies**: Se adicionar/modificar tasks, atualize dependencies

⚠️ **NÃO REPRODUZA a especificação funcional**. Apenas modifique o documento de agentes/tarefas.

## OUTPUT

Retorne o documento COMPLETO de especificação de agentes/tarefas com as modificações aplicadas.

Gere agora o documento refinado:
"""

        # 7. CHAMAR LLM ASSÍNCRONO
        start_time = time.time()

        print(f"[REFINEMENT] 📝 Refinando documento: {len(message)} chars de solicitação")

        refined_document = await get_llm_response_async(
            prompt=refinement_prompt,
            system="Você é um arquiteto de sistemas multi-agente especializado em CrewAI.",
            temperature=0.7,
            max_tokens=65536  # DeepSeek Reasoner suporta 64K
        )

        generation_time_ms = int((time.time() - start_time) * 1000)

        print(f"[REFINEMENT] ✅ LLM retornou: {len(refined_document)} chars em {generation_time_ms/1000:.1f}s")

        # 8. PARSEAR CONTADORES
        total_agents = refined_document.count("### AG-")
        total_tasks = refined_document.count("### T-")

        # 9. BUSCAR PRÓXIMA VERSÃO
        versions = get_agent_task_spec_versions(session_id)
        current_version = max([v["version"] for v in versions]) if versions else 0
        new_version = current_version + 1

        # 10. ATUALIZAR SESSÃO
        update_agent_task_spec_session(session_id, {
            "agent_task_spec_document": refined_document,
            "total_agents": total_agents,
            "total_tasks": total_tasks,
            "status": AgentTaskSpecStatus.COMPLETED.value,
            "finished_at": datetime.now(),
            "generation_time_ms": generation_time_ms
        })

        # 11. CRIAR NOVA VERSÃO
        create_agent_task_spec_version({
            "session_id": session_id,
            "version": new_version,
            "agent_task_spec_document": refined_document,
            "created_by": user_id,
            "change_type": "ai_refinement",
            "change_description": message[:500],  # Primeiros 500 chars
            "doc_size": len(refined_document.encode('utf-8'))
        })

        print(f"[REFINEMENT] 📦 Versão {new_version} criada: {total_agents} agentes, {total_tasks} tarefas")

        # 12. SALVAR MENSAGEM DE SUCESSO
        save_agent_task_spec_chat_message({
            "session_id": session_id,
            "sender_type": "agent",
            "message_text": f"✅ Documento refinado com sucesso!\n\n📊 {total_agents} agentes e {total_tasks} tarefas.\n📌 Versão {new_version} criada.",
            "message_type": "result"
        })

    except Exception as e:
        # SALVAR ERRO
        print(f"[REFINEMENT] ❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

        update_agent_task_spec_session(session_id, {
            "status": AgentTaskSpecStatus.FAILED.value,
            "finished_at": datetime.now()
        })

        save_agent_task_spec_chat_message({
            "session_id": session_id,
            "sender_type": "system",
            "message_text": f"❌ Erro ao refinar: {str(e)}",
            "message_type": "error"
        })


async def execute_chat(session_id: str, message: str):
    """Executa chat sem modificar documento"""

    try:
        # 1. Buscar documento atual
        session = get_agent_task_spec_session(session_id)
        current_document = session["agent_task_spec_document"]

        # 2. Construir prompt de chat
        chat_prompt = f"""
# ANÁLISE DE ESPECIFICAÇÃO DE AGENTES E TAREFAS

## DOCUMENTO ATUAL

{current_document}

## PERGUNTA DO USUÁRIO

{message}

## TAREFA

Analise a pergunta e responda de forma clara e objetiva, baseando-se no documento acima.

**NÃO modifique o documento** - apenas forneça informações e análises.

Responda:
"""

        # 3. Chamar LLM
        response = await get_llm_response_async(
            prompt=chat_prompt,
            system="Você é um assistente especializado em análise de especificações de agentes e tarefas.",
            temperature=0.7,
            max_tokens=4096
        )

        # 4. Salvar resposta
        save_agent_task_spec_chat_message({
            "session_id": session_id,
            "sender_type": "assistant",
            "message_text": response,
            "message_type": "chat"
        })

    except Exception as e:
        save_agent_task_spec_chat_message({
            "session_id": session_id,
            "sender_type": "assistant",
            "message_text": f"❌ Erro: {str(e)}",
            "message_type": "error"
        })
