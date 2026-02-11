PLANO: Geração Automática de Agentes e Tarefas a partir de Especificação Funcional

 Visão Geral

 Fase: 3 - Definição de Agentes e Tarefas
 Objetivo: Implementar geração automática via LLM de agentes e tarefas baseados na especificação funcional gerada na Fase 2

 Contexto Atual:
 - ✅ Fase 1 implementada: Upload e análise de documentos → Geração de requisitos
 - ✅ Fase 2 implementada: Geração de especificação funcional (14 seções) com chat refinement
 - 🎯 Fase 3 (próxima): Gerar agentes e tarefas automaticamente da especificação

 Estado Atual da Implementação

 Backend (Parcialmente Pronto)

 - ✅ Routers CRUD completos: agents.py, tasks.py
 - ✅ Database schemas: tabelas agents e tasks existem
 - ✅ YAML configs: langnet_agents.yaml com agent_specifier_agent e task_decomposer_agent
 - ✅ YAML tasks: langnet_tasks.yaml com suggest_agents e decompose_tasks tasks
 - ✅ Framework adapter: langnetagents.py com CrewAI + LLM providers
 - ❌ FALTA: Endpoint de geração automática usando LLM
 - ❌ FALTA: Lógica de parsing da resposta LLM → objetos Agent/Task

 Frontend (Parcialmente Pronto)

 - ✅ Páginas: AgentsPage.tsx, TasksPage.tsx (com dados mock)
 - ✅ Modais: AgentSpecifierModal.tsx, TaskSpecifierModal.tsx (simulados com setTimeout)
 - ✅ Componentes: AgentCard, TaskCard, forms
 - ❌ FALTA: Integração real com backend (substituir mocks)
 - ❌ FALTA: Botão "Gerar Agentes/Tarefas" na SpecificationPage
 - ❌ FALTA: Services para chamar endpoints de geração

 Arquitetura da Solução

 Fluxo de Dados

 Especificação Funcional (14 seções)
         ↓
 [SpecificationPage] → Botão "Gerar Agentes"
         ↓
 POST /api/agents/generate-from-specification
         ↓
 agent_specifier_agent (via langnet_tasks.yaml)
         ↓
 LLM analisa Seções 2, 3, 4, 5 da especificação
         ↓
 Retorna JSON com lista de agentes sugeridos
         ↓
 Backend parse → salva na tabela agents
         ↓
 Frontend exibe AgentSpecifierModal com sugestões
         ↓
 Usuário aprova/edita → salva agentes definitivos
         ↓
 [Click "Gerar Tarefas"]
         ↓
 POST /api/tasks/generate-from-specification
         ↓
 task_decomposer_agent (via langnet_tasks.yaml)
         ↓
 LLM analisa Seções 5, 8, 9 + agentes aprovados
         ↓
 Retorna JSON com tarefas + dependências
         ↓
 Backend parse → salva na tabela tasks
         ↓
 Frontend exibe TaskSpecifierModal com grafo de dependências

 Implementação Detalhada

 BACKEND - Parte 1: Endpoint de Geração de Agentes

 Arquivo: backend/app/routers/agent_generation.py (NOVO)

 Localização: /backend/app/routers/agent_generation.py

 Imports necessários:
 from fastapi import APIRouter, Depends, HTTPException
 from pydantic import BaseModel, Field
 from typing import List, Optional
 from app.auth import get_current_user
 from app.database import get_db_cursor
 from app.llm import get_llm_client
 import json
 import asyncio

 Request/Response Models:
 class AgentGenerationRequest(BaseModel):
     specification_session_id: str
     detail_level: str = Field(default="balanced", pattern="^(concise|balanced|detailed)$")
     max_agents: int = Field(default=10, ge=1, le=20)
     focus_areas: Optional[List[str]] = None  # e.g., ["data_processing", "api_integration"]

 class SuggestedAgent(BaseModel):
     name: str
     role: str
     goal: str
     backstory: str
     suggested_tools: List[str]
     delegation_targets: List[str]
     rationale: str

 class AgentGenerationResponse(BaseModel):
     session_id: str
     suggested_agents: List[SuggestedAgent]
     analysis_summary: str
     status: str
     message: str

 Endpoint:
 router = APIRouter(prefix="/agents", tags=["Agent Generation"])

 @router.post("/generate-from-specification")
 async def generate_agents_from_specification(
     request: AgentGenerationRequest,
     current_user: dict = Depends(get_current_user)
 ):
     """
     Generate agent suggestions from a functional specification using LLM
     """
     try:
         user_id = current_user['id']

         # 1. Get specification document
         with get_db_cursor() as cursor:
             cursor.execute("""
                 SELECT specification_document, requirements_session_id
                 FROM execution_specification_sessions
                 WHERE id = %s AND user_id = %s
             """, (request.specification_session_id, user_id))

             result = cursor.fetchone()
             if not result:
                 raise HTTPException(status_code=404, detail="Specification not found")

             spec_doc = result['specification_document']
             req_session_id = result['requirements_session_id']

         # 2. Get requirements for context
         requirements_json = None
         if req_session_id:
             with get_db_cursor() as cursor:
                 cursor.execute("""
                     SELECT requirements_json
                     FROM execution_requirements_sessions
                     WHERE id = %s
                 """, (req_session_id,))
                 req_result = cursor.fetchone()
                 if req_result:
                     requirements_json = req_result['requirements_json']

         # 3. Generate agent suggestions via LLM
         from prompts.agent_generation import get_agent_generation_prompt

         prompt = get_agent_generation_prompt(
             specification_document=spec_doc,
             requirements_json=requirements_json,
             detail_level=request.detail_level,
             max_agents=request.max_agents,
             focus_areas=request.focus_areas
         )

         print(f"[AGENT GEN] Calling LLM for agent suggestions...")
         llm_client = get_llm_client()

         llm_response = await llm_client.complete_async(
             prompt=prompt,
             temperature=0.7,
             max_tokens=8192
         )

         # 4. Parse LLM response
         suggested_agents = parse_agent_suggestions(llm_response)

         print(f"[AGENT GEN] Generated {len(suggested_agents)} agent suggestions")

         return AgentGenerationResponse(
             session_id=request.specification_session_id,
             suggested_agents=suggested_agents,
             analysis_summary=f"Analyzed specification and generated {len(suggested_agents)} specialized agents",
             status="success",
             message="Agent suggestions generated successfully"
         )

     except Exception as e:
         print(f"[AGENT GEN] Error: {str(e)}")
         import traceback
         traceback.print_exc()
         raise HTTPException(status_code=500, detail=str(e))


 def parse_agent_suggestions(llm_response: str) -> List[SuggestedAgent]:
     """
     Parse LLM response into structured agent suggestions
     Expected format: JSON array of agents
     """
     try:
         # Try to extract JSON from markdown code blocks
         if "```json" in llm_response:
             json_start = llm_response.find("```json") + 7
             json_end = llm_response.find("```", json_start)
             json_str = llm_response[json_start:json_end].strip()
         elif "```" in llm_response:
             json_start = llm_response.find("```") + 3
             json_end = llm_response.find("```", json_start)
             json_str = llm_response[json_start:json_end].strip()
         else:
             json_str = llm_response.strip()

         agents_data = json.loads(json_str)

         # Validate and convert to SuggestedAgent objects
         suggested_agents = []
         for agent_data in agents_data:
             suggested_agents.append(SuggestedAgent(
                 name=agent_data.get('name', ''),
                 role=agent_data.get('role', ''),
                 goal=agent_data.get('goal', ''),
                 backstory=agent_data.get('backstory', ''),
                 suggested_tools=agent_data.get('suggested_tools', []),
                 delegation_targets=agent_data.get('delegation_targets', []),
                 rationale=agent_data.get('rationale', '')
             ))

         return suggested_agents

     except Exception as e:
         print(f"[AGENT GEN] Parse error: {str(e)}")
         raise ValueError(f"Failed to parse agent suggestions: {str(e)}")

 Arquivo: backend/prompts/agent_generation.py (NOVO)

 Localização: /backend/prompts/agent_generation.py

 def get_agent_generation_prompt(
     specification_document: str,
     requirements_json: str = None,
     detail_level: str = "balanced",
     max_agents: int = 10,
     focus_areas: list = None
 ) -> str:
     """
     Generate prompt for agent suggestion from specification
     """

     focus_areas_text = ""
     if focus_areas:
         focus_areas_text = f"\nFOCUS AREAS: {', '.join(focus_areas)}"

     requirements_context = ""
     if requirements_json:
         requirements_context = f"""
 ORIGINAL REQUIREMENTS (for context):
 {requirements_json[:2000]}  # Limit to avoid token overflow
 """

     detail_instructions = {
         "concise": "Provide minimal but sufficient agent definitions (5-7 agents)",
         "balanced": "Provide well-balanced agent definitions covering all major areas (8-12 agents)",
         "detailed": "Provide comprehensive agent definitions with specialized roles (12-15 agents)"
     }

     return f"""Você é um especialista em design de sistemas multi-agente baseados em especificações funcionais.

 ESPECIFICAÇÃO FUNCIONAL COMPLETA:
 {specification_document}
 {requirements_context}

 TAREFA: Analisar a especificação funcional e projetar um conjunto otimizado de agentes especializados para implementar o sistema.

 ANÁLISE REQUERIDA:
 1. **Seção 2 - Visão Geral do Sistema**: Entender arquitetura e componentes principais
 2. **Seção 3 - Requisitos Funcionais**: Identificar funcionalidades que precisam de agentes
 3. **Seção 4 - Requisitos Não-Funcionais**: Considerar performance, segurança, escalabilidade
 4. **Seção 5 - Casos de Uso**: Mapear fluxos de trabalho para agentes
 5. **Seção 8 - Regras de Negócio**: Identificar lógica complexa que requer agentes especializados

 DIRETRIZES DE DESIGN:
 - {detail_instructions.get(detail_level, detail_instructions['balanced'])}
 - Máximo de {max_agents} agentes
 - Cada agente deve ter responsabilidade única e bem definida
 - Evitar sobreposição de responsabilidades
 - Considerar delegation entre agentes quando apropriado
 - Priorizar agentes que agregam mais valor ao sistema
 {focus_areas_text}

 PRINCÍPIOS:
 - **Coesão**: Cada agente deve ter uma função clara e específica
 - **Especialização**: Agentes devem ser experts em seu domínio
 - **Colaboração**: Identificar oportunidades de delegação entre agentes
 - **Completude**: Conjunto de agentes deve cobrir todos os requisitos funcionais

 FORMATO DE SAÍDA (JSON):
 ```json
 [
   {{
     "name": "data_processor_agent",
     "role": "Agente especializado em processamento e transformação de dados",
     "goal": "Processar, validar e transformar dados de entrada garantindo integridade e consistência",
     "backstory": "Especialista em ETL com 10+ anos de experiência em pipelines de dados complexos. Domina técnicas de validação, normalização e transformação de dados em diferentes 
 formatos.",
     "suggested_tools": ["data_validator", "schema_converter", "data_transformer"],
     "delegation_targets": ["database_agent", "api_integration_agent"],
     "rationale": "Necessário para implementar RF-003 (Processamento de Dados) e UC-002 (Importação de Dados)"
   }},
   {{
     "name": "api_integration_agent",
     "role": "Agente responsável por integração com APIs externas",
     "goal": "Gerenciar comunicação com serviços externos, tratando autenticação, retry e error handling",
     "backstory": "Arquiteto de integrações com expertise em REST, GraphQL e protocolos de comunicação. Conhece padrões de resiliência como circuit breaker e retry policies.",
     "suggested_tools": ["http_client", "auth_manager", "circuit_breaker"],
     "delegation_targets": ["error_handler_agent"],
     "rationale": "Essencial para RF-005 (Integração Externa) e RNF-002 (Disponibilidade)"
   }}
   // ... mais agentes
 ]

 IMPORTANTE:
 - Retorne APENAS o JSON, sem texto adicional
 - Certifique-se de que o JSON está bem formatado
 - Cada agente deve ter todos os campos preenchidos
 - Os nomes devem ser em snake_case
 - As ferramentas sugeridas devem ser genéricas e reutilizáveis
 - A rationale deve citar seções específicas da especificação (RF-XXX, UC-XXX, RNF-XXX)

 Gere agora os agentes otimizados para esta especificação."""

 ### BACKEND - Parte 2: Endpoint de Geração de Tarefas

 #### Arquivo: `backend/app/routers/task_generation.py` (NOVO)

 **Localização**: `/backend/app/routers/task_generation.py`

 **Request/Response Models**:
 ```python
 class TaskGenerationRequest(BaseModel):
     specification_session_id: str
     agent_ids: List[str]  # Agents generated/selected in previous step
     decomposition_strategy: str = Field(default="workflow", pattern="^(workflow|functional|hybrid)$")
     include_dependencies: bool = True

 class SuggestedTask(BaseModel):
     name: str
     description: str
     agent_id: str
     inputs: dict  # Input schema
     outputs: dict  # Output schema
     steps: List[str]
     dependencies: List[str]  # Task names this depends on
     parallel_execution: List[str]  # Tasks that can run in parallel
     expected_duration: str
     rationale: str

 class TaskGenerationResponse(BaseModel):
     session_id: str
     suggested_tasks: List[SuggestedTask]
     dependency_graph: dict
     critical_path: List[str]
     status: str
     message: str

 Endpoint:
 router = APIRouter(prefix="/tasks", tags=["Task Generation"])

 @router.post("/generate-from-specification")
 async def generate_tasks_from_specification(
     request: TaskGenerationRequest,
     current_user: dict = Depends(get_current_user)
 ):
     """
     Generate task decomposition from specification and agents
     """
     try:
         user_id = current_user['id']

         # 1. Get specification
         with get_db_cursor() as cursor:
             cursor.execute("""
                 SELECT specification_document
                 FROM execution_specification_sessions
                 WHERE id = %s AND user_id = %s
             """, (request.specification_session_id, user_id))

             result = cursor.fetchone()
             if not result:
                 raise HTTPException(status_code=404, detail="Specification not found")

             spec_doc = result['specification_document']

         # 2. Get selected agents
         agents_data = []
         with get_db_cursor() as cursor:
             placeholders = ','.join(['%s'] * len(request.agent_ids))
             cursor.execute(f"""
                 SELECT agent_id, name, role, goal
                 FROM agents
                 WHERE agent_id IN ({placeholders})
             """, request.agent_ids)

             agents_data = cursor.fetchall()

         if not agents_data:
             raise HTTPException(status_code=400, detail="No agents found with provided IDs")

         # 3. Generate task decomposition via LLM
         from prompts.task_generation import get_task_generation_prompt

         prompt = get_task_generation_prompt(
             specification_document=spec_doc,
             agents=agents_data,
             decomposition_strategy=request.decomposition_strategy
         )

         print(f"[TASK GEN] Calling LLM for task decomposition...")
         llm_client = get_llm_client()

         llm_response = await llm_client.complete_async(
             prompt=prompt,
             temperature=0.6,
             max_tokens=12288
         )

         # 4. Parse LLM response
         suggested_tasks = parse_task_suggestions(llm_response)

         # 5. Build dependency graph
         dependency_graph = build_dependency_graph(suggested_tasks)
         critical_path = calculate_critical_path(dependency_graph)

         print(f"[TASK GEN] Generated {len(suggested_tasks)} task suggestions")

         return TaskGenerationResponse(
             session_id=request.specification_session_id,
             suggested_tasks=suggested_tasks,
             dependency_graph=dependency_graph,
             critical_path=critical_path,
             status="success",
             message=f"Generated {len(suggested_tasks)} tasks with dependency analysis"
         )

     except Exception as e:
         print(f"[TASK GEN] Error: {str(e)}")
         import traceback
         traceback.print_exc()
         raise HTTPException(status_code=500, detail=str(e))


 def parse_task_suggestions(llm_response: str) -> List[SuggestedTask]:
     """Parse LLM response into structured task suggestions"""
     # Similar to parse_agent_suggestions
     # Extract JSON from markdown, validate, convert to SuggestedTask objects
     pass

 def build_dependency_graph(tasks: List[SuggestedTask]) -> dict:
     """Build directed graph of task dependencies"""
     graph = {"nodes": [], "edges": []}

     for task in tasks:
         graph["nodes"].append({
             "id": task.name,
             "label": task.description,
             "agent": task.agent_id
         })

         for dep in task.dependencies:
             graph["edges"].append({
                 "from": dep,
                 "to": task.name,
                 "type": "dependency"
             })

     return graph

 def calculate_critical_path(dependency_graph: dict) -> List[str]:
     """Calculate critical path through task dependency graph"""
     # Topological sort + longest path calculation
     # Returns ordered list of task names in critical path
     pass

 Arquivo: backend/prompts/task_generation.py (NOVO)

 Template similar ao agent_generation.py, mas focado em:
 - Extrair tarefas das Seções 5 (Use Cases), 8 (Business Rules), 9 (Workflows)
 - Mapear cada tarefa para um agente específico
 - Definir inputs/outputs claros
 - Identificar dependências entre tarefas
 - Sugerir execução paralela quando possível

 FRONTEND - Parte 1: Services

 Arquivo: src/services/agentGenerationService.ts (NOVO)

 const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

 const getAuthToken = (): string | null => {
   return localStorage.getItem('accessToken') || localStorage.getItem('token');
 };

 const getAuthHeaders = (): HeadersInit => {
   const token = getAuthToken();
   return {
     'Authorization': token ? `Bearer ${token}` : '',
     'Content-Type': 'application/json',
   };
 };

 export interface AgentGenerationRequest {
   specification_session_id: string;
   detail_level?: 'concise' | 'balanced' | 'detailed';
   max_agents?: number;
   focus_areas?: string[];
 }

 export interface SuggestedAgent {
   name: string;
   role: string;
   goal: string;
   backstory: string;
   suggested_tools: string[];
   delegation_targets: string[];
   rationale: string;
 }

 export interface AgentGenerationResponse {
   session_id: string;
   suggested_agents: SuggestedAgent[];
   analysis_summary: string;
   status: string;
   message: string;
 }

 export const generateAgentsFromSpecification = async (
   request: AgentGenerationRequest
 ): Promise<AgentGenerationResponse> => {
   console.log('🤖 Generating agents from specification:', request.specification_session_id);

   const response = await fetch(`${API_BASE_URL}/agents/generate-from-specification`, {
     method: 'POST',
     headers: getAuthHeaders(),
     body: JSON.stringify(request),
   });

   if (!response.ok) {
     const error = await response.json();
     console.error('❌ Failed to generate agents:', error);
     throw new Error(error.detail || 'Failed to generate agents');
   }

   const result = await response.json();
   console.log('✅ Agents generated:', result);
   return result;
 };

 export default {
   generateAgentsFromSpecification,
 };

 Arquivo: src/services/taskGenerationService.ts (NOVO)

 // Similar structure to agentGenerationService.ts
 // Implements generateTasksFromSpecification()

 FRONTEND - Parte 2: Integração com SpecificationPage

 Arquivo: src/pages/SpecificationPage.tsx (MODIFICAR)

 Adicionar estados:
 const [isGeneratingAgents, setIsGeneratingAgents] = useState(false);
 const [isGeneratingTasks, setIsGeneratingTasks] = useState(false);
 const [generatedAgents, setGeneratedAgents] = useState<SuggestedAgent[]>([]);
 const [generatedTasks, setGeneratedTasks] = useState<SuggestedTask[]>([]);

 Adicionar handlers:
 const handleGenerateAgents = async () => {
   if (!currentSessionId) return;

   setIsGeneratingAgents(true);
   try {
     const result = await generateAgentsFromSpecification({
       specification_session_id: currentSessionId,
       detail_level: 'balanced',
       max_agents: 10
     });

     setGeneratedAgents(result.suggested_agents);

     // Show in chat
     const agentMsg: ChatMessage = {
       id: uuidv4(),
       sender: 'agent',
       text: `✅ ${result.suggested_agents.length} agentes gerados:\n\n${result.analysis_summary}`,
       timestamp: new Date(),
       type: 'result'
     };
     setChatMessages(prev => [...prev, agentMsg]);

     // Open modal with suggestions
     setIsAgentSpecifierOpen(true);

   } catch (error) {
     console.error('Error generating agents:', error);
     alert('Erro ao gerar agentes. Tente novamente.');
   } finally {
     setIsGeneratingAgents(false);
   }
 };

 const handleGenerateTasks = async (selectedAgentIds: string[]) => {
   if (!currentSessionId) return;

   setIsGeneratingTasks(true);
   try {
     const result = await generateTasksFromSpecification({
       specification_session_id: currentSessionId,
       agent_ids: selectedAgentIds,
       decomposition_strategy: 'workflow',
       include_dependencies: true
     });

     setGeneratedTasks(result.suggested_tasks);

     // Show in chat
     const taskMsg: ChatMessage = {
       id: uuidv4(),
       sender: 'agent',
       text: `✅ ${result.suggested_tasks.length} tarefas geradas com grafo de dependências`,
       timestamp: new Date(),
       type: 'result'
     };
     setChatMessages(prev => [...prev, taskMsg]);

     // Open modal with task graph
     setIsTaskSpecifierOpen(true);

   } catch (error) {
     console.error('Error generating tasks:', error);
     alert('Erro ao gerar tarefas. Tente novamente.');
   } finally {
     setIsGeneratingTasks(false);
   }
 };

 Adicionar botões na interface:
 <div className="generation-actions">
   <button
     className="btn-generate-agents"
     onClick={handleGenerateAgents}
     disabled={isGeneratingAgents || !generatedDocument}
     title="Gerar agentes automaticamente da especificação"
   >
     {isGeneratingAgents ? '⏳ Gerando Agentes...' : '🤖 Gerar Agentes'}
   </button>

   <button
     className="btn-generate-tasks"
     onClick={() => handleGenerateTasks(selectedAgentIds)}
     disabled={isGeneratingTasks || generatedAgents.length === 0}
     title="Gerar tarefas baseadas nos agentes"
   >
     {isGeneratingTasks ? '⏳ Gerando Tarefas...' : '📋 Gerar Tarefas'}
   </button>
 </div>

 FRONTEND - Parte 3: Atualizar Modais

 Arquivo: src/components/agents/AgentSpecifierModal.tsx (MODIFICAR)

 Remover simulação setTimeout, adicionar:

 interface AgentSpecifierModalProps {
   isOpen: boolean;
   suggestedAgents: SuggestedAgent[];  // Real data from backend
   onClose: () => void;
   onSave: (agents: Agent[]) => void;
   isSaving: boolean;
 }

 const AgentSpecifierModal: React.FC<AgentSpecifierModalProps> = ({
   isOpen,
   suggestedAgents,
   onClose,
   onSave,
   isSaving
 }) => {
   const [editedAgents, setEditedAgents] = useState<Agent[]>([]);

   useEffect(() => {
     // Convert SuggestedAgent to Agent format
     const converted = suggestedAgents.map(sa => ({
       id: uuidv4(),
       name: sa.name,
       role: sa.role,
       goal: sa.goal,
       backstory: sa.backstory,
       tools: sa.suggested_tools,
       // ... other fields
     }));
     setEditedAgents(converted);
   }, [suggestedAgents]);

   const handleSave = () => {
     onSave(editedAgents);
   };

   return (
     <div className="modal-overlay">
       <div className="agent-specifier-modal">
         <h2>🤖 Agentes Sugeridos ({editedAgents.length})</h2>

         <div className="agents-list">
           {editedAgents.map((agent, index) => (
             <AgentSuggestionCard
               key={agent.id}
               agent={agent}
               onEdit={(updated) => {
                 const newAgents = [...editedAgents];
                 newAgents[index] = updated;
                 setEditedAgents(newAgents);
               }}
               onRemove={() => {
                 setEditedAgents(editedAgents.filter((_, i) => i !== index));
               }}
             />
           ))}
         </div>

         <div className="modal-footer">
           <button onClick={onClose} disabled={isSaving}>Cancelar</button>
           <button onClick={handleSave} disabled={isSaving}>
             {isSaving ? '⏳ Salvando...' : '✅ Salvar Agentes'}
           </button>
         </div>
       </div>
     </div>
   );
 };

 Arquivo: src/components/tasks/TaskSpecifierModal.tsx (MODIFICAR)

 Similar ao AgentSpecifierModal, mas com:
 - Display de grafo de dependências usando library de grafos (react-flow ou vis.js)
 - Lista de tarefas agrupadas por agente
 - Indicação de caminho crítico
 - Editor inline para ajustes

 Arquivos a Criar/Modificar

 Backend (Criar)

 1. backend/app/routers/agent_generation.py
 2. backend/app/routers/task_generation.py
 3. backend/prompts/agent_generation.py
 4. backend/prompts/task_generation.py

 Backend (Modificar)

 5. backend/app/main.py - Adicionar routers de geração

 Frontend (Criar)

 6. src/services/agentGenerationService.ts
 7. src/services/taskGenerationService.ts
 8. src/components/agents/AgentSuggestionCard.tsx
 9. src/components/tasks/TaskDependencyGraph.tsx

 Frontend (Modificar)

 10. src/pages/SpecificationPage.tsx - Adicionar botões e handlers
 11. src/pages/SpecificationPage.css - Estilos para botões
 12. src/components/agents/AgentSpecifierModal.tsx - Integração real
 13. src/components/tasks/TaskSpecifierModal.tsx - Integração real

 Fluxo UX Completo

 1. Usuário completa Fase 2 (especificação gerada)
 2. Clica "Gerar Agentes" → Backend analisa especificação via LLM
 3. Modal abre com 8-12 agentes sugeridos + rationale
 4. Usuário revisa, edita nomes/roles, remove redundantes, aprova
 5. Agentes salvos na tabela agents
 6. Clica "Gerar Tarefas" → Backend analisa especificação + agentes via LLM
 7. Modal abre com grafo de dependências visualizado
 8. Usuário ajusta sequência, atribui agentes, define parallelism
 9. Tarefas salvas na tabela tasks
 10. Próxima fase: Geração de YAML (Fase 4)

 Considerações Técnicas

 Parsing LLM Response

 - LLM pode retornar JSON malformado → implementar retry com correção
 - Usar json.loads() com try/except + fallback para regex extraction
 - Validar schema com Pydantic antes de salvar

 Performance

 - Geração de agentes: ~30-60 segundos (LLM call)
 - Geração de tarefas: ~60-120 segundos (análise mais complexa)
 - Frontend deve mostrar progress indicator, não timeout

 Validação

 - Agentes devem ter nomes únicos dentro do projeto
 - Tarefas devem referenciar agentes existentes
 - Grafo de dependências não deve ter ciclos (validação backend)

 Segurança

 - Verificar ownership da specification_session antes de gerar
 - Sanitizar inputs para evitar prompt injection
 - Rate limiting nos endpoints de geração (custo de LLM)

 Benefícios

 ✅ Automação: Gera agentes/tarefas automaticamente da especificação
 ✅ Inteligência: LLM analisa contexto e sugere arquitetura otimizada
 ✅ Flexibilidade: Usuário pode revisar e ajustar sugestões
 ✅ Rastreabilidade: Rationale conecta cada agente/tarefa aos requisitos
 ✅ Escalabilidade: Funciona para projetos de qualquer tamanho
 ✅ Consistência: Garante que agentes cobrem todos os requisitos funcionais
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌