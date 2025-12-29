"""
Agent & Task Generation Router
===============================

Endpoints para geração automática de agentes e tarefas a partir de
especificações funcionais.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from datetime import datetime
import json
import yaml
import asyncio

from app.models.agent_task import (
    AgentTaskGenerationRequest,
    AgentTaskRefinementRequest,
    AgentData,
    TaskData,
    AgentTaskGenerationResponse,
    AgentTaskRefinementResponse,
    AgentTaskSessionSummary,
    AgentTaskSessionListResponse,
    DependencyGraph,
    GenerationStatus
)
from app.database import get_db_connection
from app.dependencies import get_current_user
from app.llm import get_llm_response_async

# Importar prompts
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from prompts.agent_generation_prompt import get_agent_generation_prompt
from prompts.task_generation_prompt import get_task_generation_prompt, infer_task_dependencies


router = APIRouter(prefix="/agent-task", tags=["agent-task"])


# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

async def fetch_specification_document(spec_session_id: str, version: int, connection) -> str:
    """Busca o documento de especificação do banco"""
    query = """
        SELECT sf.specification_document
        FROM execution_specification_sessions sf
        WHERE sf.id = %s
        LIMIT 1
    """
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, (spec_session_id,))
    result = cursor.fetchone()
    cursor.close()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specification session {spec_session_id} not found"
        )

    return result.get("specification_document", "")


async def fetch_requirements_context(spec_session_id: str, connection) -> str:
    """Busca os requisitos relacionados para contexto adicional"""
    # Buscar requirements_session_id associado à especificação
    query = """
        SELECT sg.requirements_session_id, rg.requirements_json
        FROM execution_specification_sessions sg
        LEFT JOIN requirements_generations rg ON rg.id = sg.requirements_session_id
        WHERE sg.id = %s
        LIMIT 1
    """
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, (spec_session_id,))
    result = cursor.fetchone()
    cursor.close()

    if result and result.get("requirements_json"):
        return result["requirements_json"]

    return None


def agents_to_yaml(agents: List[AgentData]) -> str:
    """Converte lista de AgentData para YAML"""
    agents_dict = {}

    for agent in agents:
        agents_dict[agent.name] = {
            "role": agent.role,
            "goal": agent.goal,
            "backstory": agent.backstory,
            "verbose": agent.verbose,
            "allow_delegation": agent.allow_delegation
        }

    return yaml.dump(agents_dict, default_flow_style=False, allow_unicode=True, sort_keys=False)


def tasks_to_yaml(tasks: List[TaskData]) -> str:
    """Converte lista de TaskData para YAML"""
    tasks_dict = {}

    for task in tasks:
        tasks_dict[task.name] = {
            "description": task.description,
            "expected_output": task.expected_output
        }

    return yaml.dump(tasks_dict, default_flow_style=False, allow_unicode=True, sort_keys=False)


def generate_dependency_graph(tasks: List[TaskData]) -> DependencyGraph:
    """Gera grafo de dependências entre tasks"""
    nodes = []
    edges = []

    for task in tasks:
        nodes.append({
            "id": task.name,
            "label": task.name.replace("_", " ").title(),
            "requires": task.requires,
            "produces": task.produces
        })

        for dep_task_name in task.dependencies:
            edges.append({
                "from": dep_task_name,
                "to": task.name
            })

    return DependencyGraph(nodes=nodes, edges=edges)


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/generate", response_model=AgentTaskGenerationResponse)
async def generate_agents_and_tasks(
    request: AgentTaskGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Gera agentes e tarefas automaticamente a partir de:
    1. Especificação funcional (specification_session_id) OU
    2. Documento de especificação de agentes/tarefas (agent_task_spec_session_id)

    **Processo:**
    1. Busca documento (especificação funcional OU documento de agentes/tarefas)
    2. Busca requisitos para contexto adicional (se aplicável)
    3. Chama LLM para gerar agentes (via agent_generation_prompt)
    4. Parseia resposta JSON dos agentes
    5. Converte agentes para YAML
    6. Chama LLM para gerar tasks (via task_generation_prompt)
    7. Parseia resposta JSON das tasks
    8. Infere dependencies automaticamente
    9. Converte tasks para YAML
    10. Cria sessão no banco
    11. Retorna resultado
    """
    try:
        with get_db_connection() as connection:
            # Determinar origem do documento
            spec_document = None
            requirements_json = None
            project_id = None
            source_session_id = None

            if request.agent_task_spec_session_id:
                # NOVO FLUXO: Buscar de agent_task_specification_sessions
                query = """
                    SELECT
                        agent_task_spec_document,
                        project_id,
                        specification_session_id
                    FROM agent_task_specification_sessions
                    WHERE id = %s
                    LIMIT 1
                """
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, (request.agent_task_spec_session_id,))
                result = cursor.fetchone()
                cursor.close()

                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Documento de especificação de agentes/tarefas {request.agent_task_spec_session_id} não encontrado"
                    )

                spec_document = result["agent_task_spec_document"]
                project_id = result["project_id"]
                source_session_id = request.agent_task_spec_session_id

                # Tentar buscar requisitos da especificação funcional original (se houver)
                if result.get("specification_session_id"):
                    requirements_json = await fetch_requirements_context(
                        result["specification_session_id"],
                        connection
                    )

            else:
                # FLUXO ORIGINAL: Buscar de specification_sessions
                # 1. Buscar especificação funcional
                spec_document = await fetch_specification_document(
                    request.specification_session_id,
                    request.specification_version,
                    connection
                )

                # 2. Buscar requisitos (contexto)
                requirements_json = await fetch_requirements_context(
                    request.specification_session_id,
                    connection
                )

                source_session_id = request.specification_session_id

            # 3. Gerar Agentes via LLM
            agent_prompt = get_agent_generation_prompt(
                specification_document=spec_document,
                requirements_json=requirements_json,
                detail_level=request.detail_level.value,
                max_agents=request.max_agents,
                custom_instructions=request.custom_instructions
            )

            # Chamar LLM de forma assíncrona
            agents_json_str = await get_llm_response_async(
                prompt=agent_prompt,
                temperature=0.3,  # Baixa temperatura para mais consistência
                max_tokens=16000
            )

            # 4. Parsear resposta JSON dos agentes
            try:
                # Limpar possíveis markdown code blocks
                agents_json_str = agents_json_str.strip()
                if agents_json_str.startswith("```json"):
                    agents_json_str = agents_json_str[7:]
                if agents_json_str.endswith("```"):
                    agents_json_str = agents_json_str[:-3]

                agents_data_list = json.loads(agents_json_str)
                agents = [AgentData(**agent_dict) for agent_dict in agents_data_list]
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao parsear JSON de agentes: {str(e)}\nResposta LLM: {agents_json_str[:500]}"
                )

            # 5. Converter agentes para YAML
            agents_yaml = agents_to_yaml(agents) if request.auto_generate_yaml else None

            # 6. Gerar Tasks via LLM
            task_prompt = get_task_generation_prompt(
                specification_document=spec_document,
                agents_yaml=agents_yaml or "",
                requirements_json=requirements_json,
                detail_level=request.detail_level.value,
                custom_instructions=request.custom_instructions
            )

            tasks_json_str = await get_llm_response_async(
                prompt=task_prompt,
                temperature=0.3,
                max_tokens=32000  # Tasks podem ser mais longas
            )

            # 7. Parsear resposta JSON das tasks
            try:
                # Limpar markdown
                tasks_json_str = tasks_json_str.strip()
                if tasks_json_str.startswith("```json"):
                    tasks_json_str = tasks_json_str[7:]
                if tasks_json_str.endswith("```"):
                    tasks_json_str = tasks_json_str[:-3]

                tasks_data_list = json.loads(tasks_json_str)
                tasks = [TaskData(**task_dict) for task_dict in tasks_data_list]
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao parsear JSON de tasks: {str(e)}\nResposta LLM: {tasks_json_str[:500]}"
                )

            # 8. Inferir dependencies automaticamente (caso LLM tenha errado)
            tasks_dict_list = [task.dict() for task in tasks]
            tasks_dict_list = infer_task_dependencies(tasks_dict_list)
            tasks = [TaskData(**task_dict) for task_dict in tasks_dict_list]

            # 9. Converter tasks para YAML
            tasks_yaml = tasks_to_yaml(tasks) if request.auto_generate_yaml else None

            # 10. Gerar dependency graph
            dependency_graph = generate_dependency_graph(tasks)

            # 11. Buscar project_id (se ainda não temos)
            if not project_id:
                # Buscar project_id da especificação funcional
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    "SELECT project_id FROM execution_specification_sessions WHERE id = %s",
                    (request.specification_session_id,)
                )
                spec_result = cursor.fetchone()
                project_id = spec_result["project_id"] if spec_result else None
                cursor.close()

                if not project_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Project ID not found for specification"
                    )

            # 12. Criar sessão no banco
            session_id = str(uuid.uuid4())
            session_name = f"Geração - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            insert_query = """
                INSERT INTO agent_task_sessions (
                    id, project_id, user_id, session_name,
                    specification_session_id, specification_version,
                    detail_level, frameworks, custom_instructions,
                    agents_count, tasks_count,
                    agents_yaml, tasks_yaml,
                    agents_json, tasks_json,
                    dependency_graph, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor = connection.cursor()
            cursor.execute(insert_query, (
                session_id,
                project_id,
                current_user["id"],
                session_name,
                # Se veio de agent_task_spec, usa agent_task_spec_session_id; senão usa specification_session_id
                request.agent_task_spec_session_id if request.agent_task_spec_session_id else request.specification_session_id,
                request.specification_version,
                request.detail_level.value,
                json.dumps(request.frameworks),
                request.custom_instructions,
                len(agents),
                len(tasks),
                agents_yaml,
                tasks_yaml,
                json.dumps([agent.dict() for agent in agents]),
                json.dumps([task.dict() for task in tasks]),
                json.dumps(dependency_graph.dict()),
                GenerationStatus.COMPLETED.value
            ))
            connection.commit()
            cursor.close()

            # 13. Retornar resultado
            return AgentTaskGenerationResponse(
                session_id=session_id,
                session_name=session_name,
                agents=agents,
                tasks=tasks,
                agents_yaml=agents_yaml,
                tasks_yaml=tasks_yaml,
                dependency_graph=dependency_graph,
                status=GenerationStatus.COMPLETED,
                message=f"{len(agents)} agentes e {len(tasks)} tarefas gerados com sucesso",
                created_at=datetime.now()
            )

    except HTTPException:
        raise
    except Exception as e:
        # Logar erro e retornar
        print(f"Erro ao gerar agentes e tarefas: {str(e)}")
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao gerar agentes e tarefas: {str(e)}"
        )


@router.get("/sessions", response_model=AgentTaskSessionListResponse)
async def list_agent_task_sessions(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Lista todas as sessões de geração de agentes/tarefas de um projeto"""
    with get_db_connection() as connection:
        query = """
            SELECT
                id, session_name, specification_session_id, specification_version,
                agents_count, tasks_count, status, created_at
            FROM agent_task_sessions
            WHERE project_id = %s AND user_id = %s
            ORDER BY created_at DESC
        """

        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (project_id, current_user["id"]))
        rows = cursor.fetchall()
        cursor.close()

        sessions = [AgentTaskSessionSummary(**row) for row in rows]

        return AgentTaskSessionListResponse(
            sessions=sessions,
            total=len(sessions)
        )


@router.get("/sessions/{session_id}", response_model=AgentTaskGenerationResponse)
async def get_agent_task_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Busca uma sessão específica de geração"""
    with get_db_connection() as connection:
        query = """
            SELECT
                id, session_name, specification_session_id, specification_version,
                agents_count, tasks_count, agents_yaml, tasks_yaml,
                agents_json, tasks_json, dependency_graph, status, created_at
            FROM agent_task_sessions
            WHERE id = %s AND user_id = %s
            LIMIT 1
        """

        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, (session_id, current_user["id"]))
        row = cursor.fetchone()
        cursor.close()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        # Parsear JSONs
        agents = [AgentData(**agent) for agent in json.loads(row["agents_json"])]
        tasks = [TaskData(**task) for task in json.loads(row["tasks_json"])]
        dependency_graph = DependencyGraph(**json.loads(row["dependency_graph"])) if row.get("dependency_graph") else None

        return AgentTaskGenerationResponse(
            session_id=row["id"],
            session_name=row["session_name"],
            agents=agents,
            tasks=tasks,
            agents_yaml=row["agents_yaml"],
            tasks_yaml=row["tasks_yaml"],
            dependency_graph=dependency_graph,
            status=GenerationStatus(row["status"]),
            message=f"{len(agents)} agentes e {len(tasks)} tarefas carregados",
            created_at=row["created_at"]
        )


@router.post("/refine", response_model=AgentTaskRefinementResponse)
async def refine_agents_and_tasks(
    request: AgentTaskRefinementRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Refina agentes e tarefas via chat conversacional.

    **Processo:**
    1. Busca sessão existente
    2. Monta prompt de refinamento com contexto completo
    3. Chama LLM para aplicar refinamento
    4. Atualiza sessão no banco
    5. Salva mensagem de chat
    """
    try:
        with get_db_connection() as connection:
            # 1. Buscar sessão existente
            query = """
                SELECT
                    id, session_name, agents_json, tasks_json,
                    agents_yaml, tasks_yaml, specification_session_id
                FROM agent_task_sessions
                WHERE id = %s AND user_id = %s
                LIMIT 1
            """

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (request.session_id, current_user["id"]))
            row = cursor.fetchone()
            cursor.close()

            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Session {request.session_id} not found"
                )

            # 2. Parsear dados atuais
            current_agents = json.loads(row["agents_json"])
            current_tasks = json.loads(row["tasks_json"])

            # 3. Montar prompt de refinamento
            refinement_prompt = f"""Você está refinando agentes e tarefas gerados anteriormente.

AGENTES ATUAIS (JSON):
{json.dumps(current_agents, indent=2, ensure_ascii=False)}

TAREFAS ATUAIS (JSON):
{json.dumps(current_tasks, indent=2, ensure_ascii=False)}

PEDIDO DO USUÁRIO:
{request.refinement_message}

INSTRUÇÕES:
1. Analise o pedido do usuário
2. Aplique as modificações solicitadas aos agentes e/ou tarefas
3. Mantenha a estrutura JSON válida
4. Se adicionar novos agentes/tasks, siga os mesmos padrões existentes
5. Se modificar tasks, atualize dependencies se necessário

RETORNE UM JSON com esta estrutura:
{{
  "agents": [...],  // Lista completa de agentes (com modificações)
  "tasks": [...],   // Lista completa de tasks (com modificações)
  "summary": "Resumo das mudanças aplicadas (2-3 frases)"
}}

Retorne APENAS o JSON, sem texto adicional:"""

            # 4. Chamar LLM
            refinement_json_str = await get_llm_response_async(
                prompt=refinement_prompt,
                temperature=0.4,
                max_tokens=32000
            )

            # 5. Parsear resposta
            try:
                refinement_json_str = refinement_json_str.strip()
                if refinement_json_str.startswith("```json"):
                    refinement_json_str = refinement_json_str[7:]
                if refinement_json_str.endswith("```"):
                    refinement_json_str = refinement_json_str[:-3]

                refinement_data = json.loads(refinement_json_str)

                refined_agents = [AgentData(**agent) for agent in refinement_data["agents"]]
                refined_tasks = [TaskData(**task) for task in refinement_data["tasks"]]
                summary = refinement_data.get("summary", "Refinamento aplicado com sucesso")

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao parsear refinamento: {str(e)}"
                )

            # 6. Atualizar YAMLs
            refined_agents_yaml = agents_to_yaml(refined_agents)
            refined_tasks_yaml = tasks_to_yaml(refined_tasks)

            # 7. Atualizar no banco
            update_query = """
                UPDATE agent_task_sessions
                SET
                    agents_json = %s,
                    tasks_json = %s,
                    agents_yaml = %s,
                    tasks_yaml = %s,
                    agents_count = %s,
                    tasks_count = %s,
                    updated_at = NOW()
                WHERE id = %s
            """

            cursor = connection.cursor()
            cursor.execute(update_query, (
                json.dumps([agent.dict() for agent in refined_agents]),
                json.dumps([task.dict() for task in refined_tasks]),
                refined_agents_yaml,
                refined_tasks_yaml,
                len(refined_agents),
                len(refined_tasks),
                request.session_id
            ))
            connection.commit()
            cursor.close()

            # 8. Salvar mensagem de chat
            chat_msg_id = str(uuid.uuid4())
            insert_msg_query = """
                INSERT INTO agent_task_chat_messages (id, session_id, sender, message, message_type)
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor = connection.cursor()
            # Mensagem do usuário
            cursor.execute(insert_msg_query, (
                str(uuid.uuid4()), request.session_id, 'user', request.refinement_message, 'status'
            ))
            # Mensagem da resposta
            cursor.execute(insert_msg_query, (
                str(uuid.uuid4()), request.session_id, 'assistant', summary, 'result'
            ))
            connection.commit()
            cursor.close()

            # 9. Retornar
            return AgentTaskRefinementResponse(
                session_id=request.session_id,
                refined_agents=refined_agents,
                refined_tasks=refined_tasks,
                agents_yaml=refined_agents_yaml,
                tasks_yaml=refined_tasks_yaml,
                refinement_summary=summary,
                status=GenerationStatus.COMPLETED,
                message="Refinamento aplicado com sucesso"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao refinar: {str(e)}")
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao refinar: {str(e)}"
        )
