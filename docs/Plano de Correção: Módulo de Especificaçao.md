Plano de Correção: Módulo de Especificação Funcional

 RESUMO

 Implementar o módulo de Especificação Funcional seguindo o padrão de DocumentsPage, mas com:
 1. Seleção de documento de requisitos (sessão + versão) como fonte
 2. Documentos complementares opcionais
 3. Prompts específicos para especificação (já implementado em specification_prompt.py)
 4. Chat de refinamento idêntico ao de requisitos

 ---
 ARQUIVOS A MODIFICAR/CRIAR

 | Arquivo                                  | Ação                                                    | Linhas      |
 |------------------------------------------|---------------------------------------------------------|-------------|
 | backend/app/routers/specification.py     | MODIFICAR - Implementar /refine, /chat-history, /status | ~200 linhas |
 | src/services/specificationChatService.ts | CRIAR                                                   | ~100 linhas |
 | src/pages/SpecificationPage.tsx          | REESCREVER completo                                     | ~600 linhas |
 | src/pages/SpecificationPage.css          | MODIFICAR - Adicionar estilos chat                      | ~100 linhas |

 ---
 FASE 1: Backend - specification.py

 1.1 Adicionar endpoint /refine (linha 460)

 Seguir exatamente o padrão de chat.py:execute_refinement_workflow (linhas 231-538):

 async def execute_specification_refinement(
     session_id: str,
     refinement_instructions: str,
     current_specification: str,
     requirements_session_id: str,
     agent_message_id: str
 ):
     """
     Execute specification refinement workflow in background
     Baseado em chat.py:execute_refinement_workflow
     """
     try:
         # 1. Update session status to 'processing'
         with get_db_connection() as db:
             cursor = db.cursor()
             cursor.execute("""
                 UPDATE execution_specification_sessions
                 SET status = 'processing'
                 WHERE id = %s
             """, (session_id,))
             db.commit()
             cursor.close()

         # 2. Load original requirements document for context
         with get_db_connection() as db:
             cursor = db.cursor(dictionary=True)
             cursor.execute("""
                 SELECT requirements_document FROM execution_sessions
                 WHERE id = %s
             """, (requirements_session_id,))
             req_data = cursor.fetchone()
             cursor.close()

         original_requirements = req_data['requirements_document'] if req_data else ""

         # 3. Get previous refinements history
         previous_refinements = get_previous_refinements(session_id, limit=10)
         refinement_history = ""
         if previous_refinements:
             refinement_history = "HISTÓRICO DE REFINAMENTOS ANTERIORES:\n"
             for idx, msg in enumerate(previous_refinements, 1):
                 refinement_history += f"{idx}. {msg.get('message_text', '')}\n"

         # 4. Build refinement prompt (ESPECÍFICO PARA ESPECIFICAÇÃO)
         refinement_prompt = f"""ESPECIFICAÇÃO FUNCIONAL ATUAL:
 {current_specification}

 DOCUMENTO DE REQUISITOS BASE (REFERÊNCIA):
 {original_requirements[:10000]}

 {refinement_history}

 SOLICITAÇÃO DO USUÁRIO:
 {refinement_instructions}

 TAREFA:
 1. Aplique as mudanças solicitadas à especificação
 2. Mantenha a estrutura IEEE 830 intacta
 3. Mantenha rastreabilidade com requisitos originais
 4. Retorne o documento COMPLETO refinado
 5. NÃO adicione comentários ou análises

 IMPORTANTE: Retorne SOMENTE o documento markdown refinado.
 """

         # 5. Call LLM
         llm_client = get_llm_client()
         refined_specification = llm_client.complete(
             prompt=refinement_prompt,
             temperature=0.7,
             max_tokens=16000
         )

         # 6. Update session with refined specification
         with get_db_connection() as db:
             cursor = db.cursor(dictionary=True)
             cursor.execute("""
                 UPDATE execution_specification_sessions
                 SET specification_document = %s,
                     status = 'completed',
                     updated_at = NOW()
                 WHERE id = %s
             """, (refined_specification, session_id))

             # Get next version
             cursor.execute("""
                 SELECT MAX(version) as max_version
                 FROM specification_version_history
                 WHERE specification_session_id = %s
             """, (session_id,))
             result = cursor.fetchone()
             new_version = (result['max_version'] or 0) + 1

             # Get user_id
             cursor.execute("SELECT user_id FROM execution_specification_sessions WHERE id = %s", (session_id,))
             user_result = cursor.fetchone()
             user_id = user_result['user_id'] if user_result else None

             # Save new version
             cursor.execute("""
                 INSERT INTO specification_version_history
                 (specification_session_id, version, specification_document, created_by,
                  change_description, change_type, doc_size)
                 VALUES (%s, %s, %s, %s, %s, 'ai_refinement', %s)
             """, (session_id, new_version, refined_specification, user_id,
                   refinement_instructions[:100], len(refined_specification)))

             db.commit()
             cursor.close()

         # 7. Update agent message
         update_chat_message(
             message_id=agent_message_id,
             message_text="✅ Refinamento concluído!",
             metadata={'type': 'refinement_response', 'status': 'completed'}
         )

         # 8. Send completion notification with diff
         save_chat_message(
             session_id=session_id,
             sender_type='system',
             message_text='✅ Especificação refinada com sucesso.',
             message_type='info',
             sender_name='Sistema',
             metadata={
                 'type': 'refinement_complete',
                 'has_diff': True,
                 'old_document': current_specification,
                 'new_document': refined_specification
             }
         )

     except Exception as e:
         # Handle error - update status and message
         ...

 1.2 Atualizar endpoint /refine

 @router.post("/{session_id}/refine")
 async def refine_specification(
     session_id: str,
     request: RefineSpecificationRequest,
     current_user: dict = Depends(get_current_user)
 ):
     """Refine specification via chat"""
     try:
         # Get session data
         with get_db_connection() as db:
             cursor = db.cursor(dictionary=True)
             cursor.execute("""
                 SELECT specification_document, requirements_session_id
                 FROM execution_specification_sessions
                 WHERE id = %s
             """, (session_id,))
             session = cursor.fetchone()
             cursor.close()

         if not session:
             raise HTTPException(status_code=404, detail="Session not found")

         current_specification = session.get('specification_document', '')
         requirements_session_id = session.get('requirements_session_id')

         if not current_specification:
             raise HTTPException(status_code=400, detail="No specification document found")

         # Save user message
         user_message_id = save_chat_message(
             session_id=session_id,
             sender_type='user',
             message_text=request.message,
             message_type='chat',
             sender_name='Você',
             parent_message_id=request.parent_message_id,
             metadata={'type': 'refinement_request'}
         )

         # Save agent initial response
         agent_message_id = save_chat_message(
             session_id=session_id,
             sender_type='agent',
             message_text="Processando refinamento...",
             message_type='chat',
             sender_name='Agente Especificação',
             parent_message_id=user_message_id,
             metadata={'type': 'refinement_response', 'status': 'processing'}
         )

         agent_message = get_chat_message(agent_message_id)

         # Execute refinement in background
         asyncio.create_task(execute_specification_refinement(
             session_id=session_id,
             refinement_instructions=request.message,
             current_specification=current_specification,
             requirements_session_id=requirements_session_id,
             agent_message_id=agent_message_id
         ))

         return {
             "user_message_id": user_message_id,
             "agent_message": agent_message,
             "status": "processing"
         }
     except HTTPException:
         raise
     except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

 1.3 Adicionar endpoint /chat-history

 @router.get("/{session_id}/chat-history")
 async def get_chat_history(session_id: str):
     """Get chat history for specification session"""
     try:
         messages = get_chat_messages(session_id=session_id, limit=100, offset=0)
         return {"messages": messages, "total": len(messages)}
     except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

 1.4 Adicionar endpoint /status

 @router.get("/{session_id}/status")
 async def get_specification_status(session_id: str):
     """Get specification session status"""
     try:
         with get_db_connection() as db:
             cursor = db.cursor(dictionary=True)
             cursor.execute("""
                 SELECT id, session_name, status, specification_document,
                        requirements_session_id, requirements_version,
                        started_at, finished_at
                 FROM execution_specification_sessions
                 WHERE id = %s
             """, (session_id,))
             session = cursor.fetchone()
             cursor.close()

         if not session:
             raise HTTPException(status_code=404, detail="Session not found")

         return {
             "session_id": session['id'],
             "session_name": session['session_name'],
             "status": session['status'],
             "specification_document": session['specification_document'],
             "doc_size": len(session['specification_document'] or ''),
             "requirements_session_id": session['requirements_session_id'],
             "requirements_version": session['requirements_version']
         }
     except HTTPException:
         raise
     except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

 ---
 FASE 2: Frontend - specificationChatService.ts

 Criar arquivo src/services/specificationChatService.ts:

 const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

 const getAuthHeaders = (): HeadersInit => {
   const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
   return {
     'Authorization': token ? `Bearer ${token}` : '',
     'Content-Type': 'application/json',
   };
 };

 export interface RefineSpecificationRequest {
   message: string;
   parent_message_id?: string;
 }

 export const refineSpecification = async (
   sessionId: string,
   request: RefineSpecificationRequest
 ) => {
   const response = await fetch(`${API_BASE_URL}/specifications/${sessionId}/refine`, {
     method: 'POST',
     headers: getAuthHeaders(),
     body: JSON.stringify(request),
   });

   if (!response.ok) {
     const error = await response.json();
     throw new Error(error.detail || 'Failed to refine specification');
   }

   return response.json();
 };

 export const getChatHistory = async (sessionId: string) => {
   const response = await fetch(`${API_BASE_URL}/specifications/${sessionId}/chat-history`, {
     method: 'GET',
     headers: getAuthHeaders(),
   });

   if (!response.ok) {
     const error = await response.json();
     throw new Error(error.detail || 'Failed to get chat history');
   }

   return response.json();
 };

 export const getSessionStatus = async (sessionId: string) => {
   const response = await fetch(`${API_BASE_URL}/specifications/${sessionId}/status`, {
     method: 'GET',
     headers: getAuthHeaders(),
   });

   if (!response.ok) {
     const error = await response.json();
     throw new Error(error.detail || 'Failed to get session status');
   }

   return response.json();
 };

 ---
 FASE 3: Frontend - SpecificationPage.tsx

 Reescrever completamente seguindo padrão de DocumentsPage.tsx (linhas 1-955).

 Estados necessários:

 // Sessions
 const [specifications, setSpecifications] = useState<SpecificationSession[]>([]);
 const [selectedSpec, setSelectedSpec] = useState<SpecificationSession | null>(null);
 const [loadingList, setLoadingList] = useState(true);
 const [loadingSpec, setLoadingSpec] = useState(false);

 // Versions
 const [versions, setVersions] = useState<SpecificationVersion[]>([]);
 const [selectedVersion, setSelectedVersion] = useState<number>(0);

 // Document
 const [documentContent, setDocumentContent] = useState<string>('');
 const [documentFilename, setDocumentFilename] = useState<string>('especificacao.md');

 // Chat (igual DocumentsPage)
 const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
 const [isChatProcessing, setIsChatProcessing] = useState(false);

 // Diff
 const [showDiff, setShowDiff] = useState(false);
 const [oldDocument, setOldDocument] = useState<string>('');

 // Modals
 const [showGenerationModal, setShowGenerationModal] = useState(false);
 const [isEditorOpen, setIsEditorOpen] = useState(false);
 const [isViewerOpen, setIsViewerOpen] = useState(false);
 const [isDiffModalOpen, setIsDiffModalOpen] = useState(false);

 // Polling
 const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

 Layout (3 colunas como DocumentsPage):

 ┌─────────────────────────────────────────────────────────────────┐
 │  Header: Especificação Funcional  [Nova] [Atualizar]            │
 ├──────────────────┬──────────────────────────┬───────────────────┤
 │  SIDEBAR         │  CHAT AREA               │  DOCUMENT PANEL   │
 │                  │                          │                   │
 │  📋 Sessões      │  ChatInterface           │  DocumentActions  │
 │  - Sessão 1 ✓    │  (igual DocumentsPage)   │  - Visualizar     │
 │  - Sessão 2      │                          │  - Editar         │
 │  - Sessão 3      │                          │  - Download       │
 │                  │                          │  - Ver Diff       │
 │  ───────────     │                          │                   │
 │  📜 Versões      │                          │                   │
 │  - v3 (atual)    │                          │                   │
 │  - v2            │                          │                   │
 │  - v1            │                          │                   │
 └──────────────────┴──────────────────────────┴───────────────────┘

 Componentes a reutilizar de DocumentsPage:

 1. ChatInterface - Reutilizar diretamente
 2. DocumentActionsCard - Reutilizar diretamente
 3. MarkdownEditorModal - Reutilizar diretamente
 4. MarkdownViewerModal - Reutilizar diretamente
 5. DiffViewerModal - Reutilizar diretamente

 Funções principais:

 1. loadSpecifications() - Carregar lista de sessões
 2. handleSelectSpecification(spec) - Selecionar sessão
 3. loadVersions(sessionId) - Carregar versões
 4. handleVersionChange(version) - Trocar versão
 5. handleSendChatMessage(message) - Enviar refinamento
 6. loadChatHistory(sessionId) - Carregar chat
 7. startPolling(sessionId) / stopPolling() - Polling de status
 8. handleGenerationSuccess(sessionId) - Callback do modal
 9. handleSaveEdit(newContent) - Salvar edição manual

 ---
 ORDEM DE EXECUÇÃO

 1. Backend: Modificar specification.py
   - Implementar execute_specification_refinement() (~100 linhas)
   - Atualizar endpoint /refine (~50 linhas)
   - Adicionar /chat-history (~15 linhas)
   - Adicionar /status (~30 linhas)
 2. Frontend: Criar specificationChatService.ts (~60 linhas)
 3. Frontend: Reescrever SpecificationPage.tsx (~600 linhas)
   - Importar componentes existentes
   - Implementar 3 colunas
   - Integrar ChatInterface
   - Integrar modais
 4. CSS: Atualizar SpecificationPage.css
   - Adicionar classes para layout 3 colunas
   - Estilo do chat area
 5. Testar fluxo completo:
   - Nova especificação via modal
   - Polling durante geração
   - Chat de refinamento
   - Histórico de versões
   - Diff viewer
