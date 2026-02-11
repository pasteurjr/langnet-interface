# Plano: Implementação Completa do Pipeline de Geração Multi-Agente com Petri Net

**Data:** 2026-01-08
**Contexto:** Implementar geração automática completa de projetos multi-agente executáveis
**Baseado em:** Análise dos arquivos TropicalSales e arquitetura LangNet existente

---

## 🎯 Objetivos

Implementar 5 componentes principais para geração automática de sistemas multi-agente:

1. ✅ **Documento de Sequência de Tarefas Detalhado** - Especificar fluxo de execução com inputs/outputs
2. ✅ **Revisão e Enriquecimento dos YAMLs** - Adicionar input_data, output_data, tools, requires, produces
3. ✅ **Geração de Petri Net Completa** - JSON com lugares, transições, arcos e campo `logica` (JavaScript)
4. ✅ **Geração de Código Python do Framework** - State TypedDict, TASK_REGISTRY, input/output functions
5. ✅ **Geração de Servidor WebSocket** - Adapter e servidor genérico por projeto

---

## 📊 Estado Atual (O Que Já Existe)

### ✅ Implementado e Funcionando

**Pipeline de Geração de YAMLs:**
- `/backend/app/routers/agent_task_spec.py` - Gera documento MD intermediário
- `/backend/app/routers/agents_yaml.py` - Gera agents.yaml
- `/backend/app/routers/tasks_yaml.py` - Gera tasks.yaml
- Prompts LLM estruturados em `/backend/prompts/`
- Sistema de refinamento via chat
- Versionamento e histórico

**Banco de Dados:**
- Tabelas: `agent_task_specification_sessions`, `agents_yaml_sessions`, `tasks_yaml_sessions`
- Campos LONGTEXT para armazenar documentos
- Histórico de versões e chat

**WebSocket:**
- `/backend/api/langnetwebsocket.py` - Streaming de progresso implementado
- ConnectionManager para broadcast

**Agentes Configurados:**
- `langnet_agents.yaml` com 9 agentes incluindo `petri_net_designer_agent`
- `langnet_tasks.yaml` com tasks do pipeline

### ❌ Faltando (O Que Será Implementado)

1. Documento de fluxo de execução detalhado
2. Campos adicionais nos YAMLs (input_data, output_data, requires, produces, tools)
3. Geração de Petri Net JSON completo com JavaScript no campo `logica`
4. Geração de código Python (State TypedDict, TASK_REGISTRY, execute_task_with_context)
5. Geração de adapter WebSocket e servidor por projeto

---

## 🏗️ FASE 1: Documento de Sequência de Tarefas Detalhado

**IMPORTANTE:** Esta fase segue **exatamente o mesmo padrão** das páginas existentes:
- SpecificationPage.tsx (Especificação Funcional)
- AgentsYamlPage.tsx (Agents YAML)
- TasksYamlPage.tsx (Tasks YAML)

### 1.1 Objetivo

Criar um **módulo completo** (frontend + backend + banco) para gerar e gerenciar o documento `task_execution_flow.md` que especifique:
- State TypedDict completo (campos de config, outputs, metadados)
- Input/Output functions para cada task (código Python)
- Ordem de execução e dependências explícitas (grafo)
- Tools necessárias por task
- TASK_REGISTRY structure

### 1.2 Formato do Documento

**Nome:** `task_execution_flow.md`

**Estrutura:**

```markdown
# Fluxo de Execução de Tarefas - [Nome do Projeto]

## 1. Visão Geral

- **Total de Tasks:** X
- **Total de Agentes:** Y
- **Tipo de Fluxo:** Linear / Pipeline / Paralelo / Misto
- **Modelo de State:** Acumulativo (LangGraph-style)

## 2. Definição do State (TypedDict)

### 2.1 Campos de Configuração Inicial
| Campo | Tipo | Descrição | Valor Padrão |
|-------|------|-----------|--------------|
| max_emails | int | Quantidade máxima de emails | 5 |

### 2.2 Campos de Output das Tasks
| Campo | Tipo | Produzido Por | Consumido Por |
|-------|------|---------------|---------------|
| emails_json | str | read_email | classify_message |
| classified_json | str | classify_message | check_stock |

### 2.3 Campos de Metadados
| Campo | Tipo | Descrição |
|-------|------|-----------|
| execution_log | List[Dict] | Log de execução |
| current_task | str | Task em execução |
| timestamp | str | Timestamp ISO |

## 3. Sequência de Execução

### Task 1: read_email

**ID:** T-001
**Agente:** email_reader_agent
**Ordem:** 1 (primeira task)
**Tipo:** Inicial (sem dependências)

**Input Function:**
```python
def read_email_input_func(state: ProjectState) -> Dict[str, Any]:
    return {"max_emails": state.get("max_emails", 5)}
```

**Input Schema:**
- **max_emails** (int): Quantidade máxima de emails a buscar

**Process Steps:**
1. Conectar ao servidor IMAP usando email_fetch_tool
2. Buscar emails não lidos (limite: max_emails)
3. Extrair: email_id, from, subject, content, date
4. Estruturar em JSON

**Output Function:**
```python
def read_email_output_func(state: ProjectState, result: Any) -> ProjectState:
    return {
        **state,
        "emails_json": result.get("raw_output"),
        "emails_data": json.loads(result.get("raw_output")),
        "execution_log": state.get("execution_log", []) + [...],
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "timestamp": "2026-01-08T10:00:00",
  "total_emails": 3,
  "emails": [
    {
      "email_id": "msg_001",
      "from": "customer@example.com",
      "subject": "Pedido de orçamento",
      "content": "...",
      "date": "2026-01-08T09:30:00",
      "status": "unread"
    }
  ]
}
```

**Tools Necessárias:**
- email_fetch_tool (CrewAI)

**Campos do State Produzidos:**
- emails_json (str)
- emails_data (Dict)

**Campos do State Requeridos:**
- max_emails (int)

**Dependências:**
- Nenhuma (task inicial)

---

### Task 2: classify_message

**ID:** T-002
**Agente:** classifier_agent
**Ordem:** 2
**Tipo:** Sequencial (depende de T-001)

**Input Function:**
```python
def classify_message_input_func(state: ProjectState) -> Dict[str, Any]:
    return {"input_json": state.get("emails_json", "{}")}
```

**Input Schema:**
- **input_json** (str): JSON da task anterior (emails_json)

**Process Steps:**
1. Parsear input_json
2. Para cada email, classificar em categoria (pedido, dúvida, reclamação)
3. Identificar produtos mencionados
4. Extrair intenção do cliente
5. Estruturar classificação

**Output Function:**
```python
def classify_message_output_func(state: ProjectState, result: Any) -> ProjectState:
    return {
        **state,
        "classified_json": result.get("raw_output"),
        "classification_data": json.loads(result.get("raw_output")),
        "execution_log": state.get("execution_log", []) + [...],
        "timestamp": datetime.now().isoformat()
    }
```

**Output Schema:**
```json
{
  "timestamp": "2026-01-08T10:01:00",
  "emails": [
    {
      "email_id": "msg_001",
      "category": "pedido",
      "products": ["produto_A", "produto_B"],
      "intent": "cotação",
      "priority": "alta"
    }
  ]
}
```

**Tools Necessárias:**
- Nenhuma (usa LLM do agente)

**Campos do State Produzidos:**
- classified_json (str)
- classification_data (Dict)

**Campos do State Requeridos:**
- emails_json (str)

**Dependências:**
- read_email (T-001)

---

### [Repetir para todas as tasks...]

## 4. Grafo de Dependências

```
T-001 (read_email)
    ↓ produz: emails_json
T-002 (classify_message)
    ↓ produz: classified_json
T-003 (check_stock)
    ↓ produz: stock_checked_json
T-004 (generate_response)
    ↓ produz: response_report_md
```

**Dependências Explícitas:**
- T-002 requires: ["emails_json"] (de T-001)
- T-003 requires: ["classified_json"] (de T-002)
- T-004 requires: ["stock_checked_json"] (de T-003)

## 5. TASK_REGISTRY (Estrutura)

```python
TASK_REGISTRY = {
    "read_email": {
        "input_func": read_email_input_func,
        "output_func": read_email_output_func,
        "requires": [],
        "produces": ["emails_json", "emails_data"],
        "agent": email_reader_agent,
        "tools": [email_fetch_tool],
        "description": "Busca emails não lidos"
    },
    "classify_message": {
        "input_func": classify_message_input_func,
        "output_func": classify_message_output_func,
        "requires": ["emails_json"],
        "produces": ["classified_json", "classification_data"],
        "agent": classifier_agent,
        "tools": [],
        "description": "Classifica emails"
    }
}
```

## 6. Validações

### 6.1 Completude
- [ ] Todas as tasks têm input/output definidos
- [ ] Todas as dependências são satisfeitas
- [ ] Não há ciclos no grafo

### 6.2 Consistência
- [ ] Campos produzidos são consumidos
- [ ] Tipos de dados são compatíveis
- [ ] Tools estão disponíveis

## 7. Métricas

- **Tempo estimado de execução:** Xm
- **Complexidade do grafo:** Linear/Árvore/DAG
- **Paralelismo possível:** Sim/Não (quais tasks)
```

### 1.3 Arquitetura Completa (Padrão SpecificationPage)

Esta implementação replica **exatamente** o padrão usado em SpecificationPage, AgentsYamlPage e TasksYamlPage.

#### 1.3.1 FRONTEND - Interface Usuário

**Página Principal:** `/src/pages/SequenciaTarefasPage.tsx`
- **Copiar de:** `/src/pages/SpecificationPage.tsx` (840 linhas)
- **Layout:** 3 colunas (sidebar 280px, chat central, actions panel 320px)
- **Estrutura:**
  ```
  LEFT SIDEBAR:
  - YAMLs Base (agents.yaml + tasks.yaml selecionados)
  - Botão "Histórico" (carrega modal de histórico)
  - Configuração (custom instructions)
  - Botão "🚀 Gerar Sequência"
  - Botão "🔍 Revisar Sequência"

  MIDDLE - CHAT:
  - Indicador de geração ("🚀 GERANDO SEQUÊNCIA...")
  - Progress bar
  - Chat Interface (refinamento/análise)

  RIGHT PANEL:
  - Document Actions Card
  - Botões: Ver Diferenças, Editar, Visualizar, Exportar PDF
  ```

**Estilos:** `/src/pages/SequenciaTarefasPage.css`
- **Copiar de:** `/src/pages/SpecificationPage.css` (1322 linhas)
- **Classes principais:** `.sequencia-tarefas-page-chat`, `.page-header`, `.spec-chat-container`

**Componentes Reutilizados:**
- `ChatInterface.tsx` - Interface de chat
- `DocumentActionsCard.tsx` - Card de ações do documento
- `MarkdownViewerModal.tsx` - Visualizar documento
- `MarkdownEditorModal.tsx` - Editar documento
- `DiffViewerModal.tsx` - Ver diferenças entre versões
- `ProgressBar.tsx` - Barra de progresso

**Serviço:** `/src/services/taskExecutionFlowService.ts`
- **Baseado em:** `specificationService.ts` (262 linhas)
- **Funções:**
  ```typescript
  generateTaskExecutionFlow(data: GenerateFlowRequest): Promise<SessionResponse>
  getTaskExecutionFlowSession(sessionId: string): Promise<FlowSession>
  listTaskExecutionFlowSessions(projectId: string): Promise<FlowSession[]>
  refineTaskExecutionFlow(sessionId: string, message: string, actionType: string): Promise
  reviewTaskExecutionFlow(sessionId: string): Promise<ReviewResponse>
  listTaskExecutionFlowVersions(sessionId: string): Promise<FlowVersion[]>
  getTaskExecutionFlowChatHistory(sessionId: string): Promise<ChatMessage[]>
  updateTaskExecutionFlow(sessionId: string, content: string): Promise
  ```

#### 1.3.2 BANCO DE DADOS - 3 Tabelas

**Migração:** `/backend/database/migrations/015_create_task_execution_flow_tables.sql`

**Tabela 1: task_execution_flow_sessions**
```sql
CREATE TABLE `task_execution_flow_sessions` (
  -- Identificação
  `id` CHAR(36) PRIMARY KEY,
  `project_id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,

  -- Contexto/Origem
  `agent_task_spec_session_id` CHAR(36) NOT NULL,
  `agents_yaml_session_id` CHAR(36) NOT NULL,
  `tasks_yaml_session_id` CHAR(36) NOT NULL,
  `session_name` VARCHAR(255),

  -- Timing
  `started_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `finished_at` TIMESTAMP NULL,

  -- Status e Conteúdo
  `status` ENUM('generating','completed','failed','cancelled') DEFAULT 'generating',
  `flow_document` LONGTEXT,
  `generation_log` LONGTEXT,
  `execution_metadata` LONGTEXT,

  -- Metadados Técnicos
  `generation_time_ms` BIGINT UNSIGNED,
  `ai_model_used` VARCHAR(100),
  `total_tasks` INT UNSIGNED DEFAULT 0,
  `has_parallelism` BOOLEAN DEFAULT FALSE,

  -- Auditoria
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  -- Indexes
  KEY `idx_project_id` (`project_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_agent_task_spec` (`agent_task_spec_session_id`),
  KEY `idx_agents_yaml` (`agents_yaml_session_id`),
  KEY `idx_tasks_yaml` (`tasks_yaml_session_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),

  -- Foreign Keys
  CONSTRAINT `fk_tef_project` FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_tef_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_tef_spec` FOREIGN KEY (`agent_task_spec_session_id`) REFERENCES `agent_task_specification_sessions`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_tef_agents_yaml` FOREIGN KEY (`agents_yaml_session_id`) REFERENCES `agents_yaml_sessions`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_tef_tasks_yaml` FOREIGN KEY (`tasks_yaml_session_id`) REFERENCES `tasks_yaml_sessions`(`id`) ON DELETE CASCADE
);
```

**Tabela 2: task_execution_flow_version_history**
```sql
CREATE TABLE `task_execution_flow_version_history` (
  `session_id` CHAR(36) NOT NULL,
  `version` INT(10) UNSIGNED NOT NULL,
  `flow_document` LONGTEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `created_by` CHAR(36),
  `change_type` ENUM('initial_generation','ai_refinement','manual_edit') DEFAULT 'manual_edit',
  `change_description` VARCHAR(500),
  `doc_size` INT(10) UNSIGNED,

  PRIMARY KEY (`session_id`, `version`),
  KEY `idx_change_type` (`change_type`),
  KEY `idx_created_at` (`created_at`),

  CONSTRAINT `fk_tefv_session` FOREIGN KEY (`session_id`) REFERENCES `task_execution_flow_sessions`(`id`) ON DELETE CASCADE
);
```

**Tabela 3: task_execution_flow_chat_messages**
```sql
CREATE TABLE `task_execution_flow_chat_messages` (
  `id` CHAR(36) PRIMARY KEY,
  `session_id` CHAR(36) NOT NULL,
  `sender_type` ENUM('user','agent','system') NOT NULL,
  `sender_name` VARCHAR(100),
  `message_text` LONGTEXT NOT NULL,
  `message_type` ENUM('chat','status','progress','result','error') DEFAULT 'chat',
  `timestamp` TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
  `metadata` LONGTEXT,

  KEY `idx_session_id` (`session_id`),
  KEY `idx_timestamp` (`timestamp`),

  CONSTRAINT `fk_tefcm_session` FOREIGN KEY (`session_id`) REFERENCES `task_execution_flow_sessions`(`id`) ON DELETE CASCADE
);
```

#### 1.3.3 BACKEND - CRUD Completo

**Funções em** `/backend/app/database.py`:

```python
# SESSION CRUD
def create_task_execution_flow_session(session_data: dict) -> str
def get_task_execution_flow_session(session_id: str) -> dict | None
def update_task_execution_flow_session(session_id: str, updates: dict)
def list_task_execution_flow_sessions(project_id: str, limit: int = 50) -> list

# VERSION HISTORY
def create_task_execution_flow_version(version_data: dict) -> None
def get_task_execution_flow_versions(session_id: str) -> list

# CHAT MESSAGES
def save_task_execution_flow_chat_message(message_data: dict) -> str
def get_task_execution_flow_chat_messages(session_id: str, limit: int = 50) -> list
def get_previous_task_execution_flow_refinements(session_id: str, limit: int = 10) -> list
```

#### 1.3.4 ENDPOINTS Backend

**Router:** `/backend/app/routers/task_execution_flow.py`

**Endpoints Implementados:**

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| POST | `/task-execution-flow/` | Criar sessão + geração inicial | Sim |
| GET | `/task-execution-flow/` | Listar sessões por projeto | Não |
| GET | `/task-execution-flow/{session_id}` | Obter sessão específica | Não |
| POST | `/task-execution-flow/{session_id}/refine` | Refinamento via chat (async) | Não |
| POST | `/task-execution-flow/{session_id}/review` | Revisão do documento | Não |
| GET | `/task-execution-flow/{session_id}/versions` | Listar versões | Não |
| GET | `/task-execution-flow/{session_id}/chat-history` | Histórico de chat | Não |

**Request Models:**
```python
class GenerateFlowRequest(BaseModel):
    agent_task_spec_session_id: str
    agents_yaml_session_id: str
    tasks_yaml_session_id: str
    custom_instructions: Optional[str] = None

class RefineRequest(BaseModel):
    message: str
    action_type: str = "refine"  # refine | chat
```

#### 1.3.5 PROMPTS

**Arquivo:** `/backend/prompts/generate_task_execution_flow.py`

Prompt já implementado (ver seção 1.2 para estrutura do documento)

**Arquivo:** `/backend/prompts/review_task_execution_flow.py`

```python
def get_review_task_execution_flow_prompt(flow_document: str) -> str:
    """Prompt para revisar documento de fluxo e sugerir melhorias"""
    return f"""Analise o documento de fluxo de execução:

{flow_document}

Verifique:
1. Completude do State TypedDict
2. Consistência das dependências (requires/produces)
3. Clareza das input/output functions
4. Ausência de ciclos no grafo
5. Corretude dos tipos Python

Retorne sugestões de melhoria."""
```

#### 1.3.6 NAVEGAÇÃO - Menu Lateral

**Arquivo:** `/src/contexts/NavigationContext.tsx`

Adicionar item de menu:
```typescript
{
  id: "sequencia-tarefas",
  label: "Sequência de Tarefas",
  icon: "🔄",
  path: "/sequencia-tarefas",
  requiresProject: true
}
```

**Routes em** `/src/App.tsx`:
```typescript
<Route path="/project/:projectId/sequencia-tarefas" element={<SequenciaTarefasPage />} />
<Route path="/sequencia-tarefas" element={<SequenciaTarefasPage />} />
```

#### 1.3.7 FLUXO COMPLETO

```
1. User acessa "Sequência de Tarefas" no menu
2. User seleciona:
   - Especificação de Agentes/Tarefas (base)
   - agents.yaml (versão)
   - tasks.yaml (versão)
3. User adiciona instruções customizadas (opcional)
4. User clica "🚀 Gerar Sequência"
   → POST /task-execution-flow/
   → Background task: execute_flow_generation()
   → Status: "generating"
5. Frontend faz polling:
   → GET /task-execution-flow/{session_id} (5s)
   → GET /task-execution-flow/{session_id}/chat-history (2s)
6. LLM gera documento task_execution_flow.md
7. Status: "completed"
   → Cria versão 1
   → Exibe documento no painel direito
8. User pode:
   - Refinar via chat (POST /refine)
   - Revisar (POST /review)
   - Editar manualmente
   - Ver versões anteriores
   - Exportar PDF
```

### 1.4 Checklist de Implementação da Fase 1

#### Backend

- [ ] **Migração SQL**
  - [ ] Criar `/backend/database/migrations/015_create_task_execution_flow_tables.sql`
  - [ ] Incluir 3 tabelas: sessions, version_history, chat_messages
  - [ ] Aplicar migração no banco: `mysql langnet < 015...sql`

- [ ] **Funções CRUD (`database.py`)**
  - [ ] `create_task_execution_flow_session()`
  - [ ] `get_task_execution_flow_session()`
  - [ ] `update_task_execution_flow_session()`
  - [ ] `list_task_execution_flow_sessions()`
  - [ ] `create_task_execution_flow_version()`
  - [ ] `get_task_execution_flow_versions()`
  - [ ] `save_task_execution_flow_chat_message()`
  - [ ] `get_task_execution_flow_chat_messages()`
  - [ ] `get_previous_task_execution_flow_refinements()`

- [ ] **Prompts**
  - [ ] `/backend/prompts/generate_task_execution_flow.py` (já existe)
  - [ ] `/backend/prompts/review_task_execution_flow.py`

- [ ] **Router (`task_execution_flow.py`)**
  - [ ] POST `/` - Criar sessão
  - [ ] GET `/` - Listar sessões
  - [ ] GET `/{session_id}` - Obter sessão
  - [ ] POST `/{session_id}/refine` - Refinamento
  - [ ] POST `/{session_id}/review` - Revisão
  - [ ] GET `/{session_id}/versions` - Versões
  - [ ] GET `/{session_id}/chat-history` - Chat
  - [ ] `execute_flow_generation()` - Background task
  - [ ] `execute_flow_refinement()` - Background refinement

- [ ] **Registro no** `main.py`
  - [ ] Import do router
  - [ ] `app.include_router(task_execution_flow_router, prefix="/api")`

#### Frontend

- [ ] **Página Principal**
  - [ ] Copiar `SpecificationPage.tsx` → `SequenciaTarefasPage.tsx`
  - [ ] Copiar `SpecificationPage.css` → `SequenciaTarefasPage.css`
  - [ ] Adaptar texto e labels
  - [ ] Adaptar lógica de seleção (YAMLs base em vez de requisitos)
  - [ ] Adaptar chamadas de serviço

- [ ] **Serviço**
  - [ ] Criar `/src/services/taskExecutionFlowService.ts`
  - [ ] Implementar todas as funções (8 funções principais)

- [ ] **Navegação**
  - [ ] Adicionar item "Sequência de Tarefas" em `NavigationContext.tsx`
  - [ ] Adicionar routes em `App.tsx`

- [ ] **Testes**
  - [ ] Testar geração inicial
  - [ ] Testar refinamento via chat
  - [ ] Testar revisão
  - [ ] Testar versionamento
  - [ ] Testar edição manual
  - [ ] Testar export PDF

---

## 🏗️ FASE 2: Revisão e Enriquecimento dos YAMLs

### 2.1 Objetivo

Adicionar campos **ausentes** aos YAMLs de tasks para suportar geração de código:
- `input_data` - Configuração estática (parâmetros)
- `output_data` - Schema esperado
- `requires` - Dependências (campos do state)
- `produces` - Outputs (campos adicionados ao state)
- `tools` - Tools CrewAI necessárias

### 2.2 Formato Atualizado do tasks.yaml

**ANTES (formato atual):**
```yaml
read_email:
  description: >
    Buscar emails não lidos...
  expected_output: >
    JSON contendo emails...
```

**DEPOIS (formato enriquecido):**
```yaml
read_email:
  description: >
    Buscar emails não lidos usando email_fetch_tool.
    Input data format: {max_emails: int}

    Process steps:
      1. Conectar ao IMAP
      2. Buscar emails não lidos
      3. Estruturar em JSON

  expected_output: >
    Retornar um texto em formato JSON contendo:
    - timestamp: data e hora da execução
    - total_emails: quantidade de emails
    - emails: lista de emails com keys email_id, from, subject, content, date

  # NOVOS CAMPOS:
  input_data:
    max_emails: 5
    timeout_seconds: 30

  output_data: {}  # Preenchido em runtime

  requires: []  # Primeira task - sem dependências

  produces:
    - emails_json
    - emails_data

  tools:
    - email_fetch_tool

  agent: email_reader_agent  # Opcional: pode inferir da spec
```

### 2.3 Implementação

**Modificar:** `/backend/prompts/generate_tasks_yaml.py`

Adicionar ao prompt:

```python
FORMATO COMPLETO tasks.yaml:

```yaml
task_name:
  description: >
    [Descrição com input format e process steps]

  expected_output: >
    [Formato textual do output esperado]

  input_data:
    [campo]: [valor_padrão]  # Configuração estática

  output_data: {{}}  # Sempre vazio (runtime only)

  requires:
    - [campo_state_1]  # Campos do state necessários
    - [campo_state_2]

  produces:
    - [campo_output_1]  # Campos adicionados ao state
    - [campo_output_2]

  tools:
    - [tool_name]  # Tools CrewAI necessárias

  agent: [agent_name]  # Agente responsável (opcional)
```

REGRAS:

1. **input_data:** Configuração ESTÁTICA
   - Parâmetros que NÃO mudam entre execuções
   - Ex: max_emails, timeout, thresholds
   - Valores padrão razoáveis

2. **output_data:** SEMPRE {{}}
   - Preenchido apenas em runtime
   - Não persiste no YAML

3. **requires:** Campos do STATE necessários
   - Listar campos que a task CONSOME
   - Primeira task: `requires: []`
   - Tasks subsequentes: campos produzidos por tasks anteriores
   - Ex: `requires: ["emails_json"]`

4. **produces:** Campos do STATE gerados
   - Listar campos que a task ADICIONA ao state
   - Mínimo 1 campo (o output principal)
   - Ex: `produces: ["classified_json", "classification_data"]`

5. **tools:** Tools CrewAI
   - Usar nomes válidos: email_fetch_tool, email_send_tool, etc
   - Vazio `[]` se task usa apenas LLM do agente

6. **agent:** Nome do agente (opcional)
   - Pode ser inferido da especificação
   - Útil para validação
```

**Modificar:** `/backend/app/routers/tasks_yaml.py`

Atualizar geração para incluir novos campos:

```python
async def execute_tasks_yaml_generation(
    session_id: str,
    agent_task_spec_document: str,
    custom_instructions: str,
    user_id: str
):
    # ... código existente ...

    # Prompt ATUALIZADO com novos campos
    prompt = get_tasks_yaml_prompt(
        agent_task_spec_document,
        custom_instructions,
        include_metadata=True  # ← NOVO: incluir requires/produces/tools
    )

    # ... resto do código ...
```

**Nova Validação:**

```python
def validate_tasks_yaml_enriched(tasks_yaml_content: str) -> Dict[str, Any]:
    """
    Valida YAML enriquecido com novos campos

    Verifica:
    1. Todos os campos obrigatórios presentes
    2. requires aponta para campos válidos (produzidos por tasks anteriores)
    3. produces não tem duplicatas entre tasks
    4. tools são válidas (da lista CrewAI)
    5. Dependências não formam ciclos
    """
    tasks = yaml.safe_load(tasks_yaml_content)

    # Construir grafo de dependências
    dependency_graph = {}
    all_produces = set()

    for task_name, task_def in tasks.items():
        requires = task_def.get('requires', [])
        produces = task_def.get('produces', [])

        # Validar produces
        for field in produces:
            if field in all_produces:
                raise ValueError(f"Campo '{field}' produzido por múltiplas tasks")
            all_produces.add(field)

        dependency_graph[task_name] = requires

    # Validar que requires existem
    for task_name, requires in dependency_graph.items():
        for req in requires:
            if req not in all_produces:
                raise ValueError(f"Task '{task_name}' requer '{req}' mas nenhuma task o produz")

    # Validar ciclos (topological sort)
    try:
        execution_order = topological_sort(dependency_graph)
    except Exception as e:
        raise ValueError(f"Dependências circulares detectadas: {e}")

    return {
        "valid": True,
        "total_tasks": len(tasks),
        "dependency_graph": dependency_graph,
        "execution_order": execution_order,
        "all_produces": list(all_produces)
    }
```

---

## 🏗️ FASE 3: Geração de Petri Net com Campo `logica`

### 3.1 Objetivo

Gerar **JSON completo da Petri Net** com:
- Lugares (places) - Um para cada task
- Transições (transitions) - Conectam lugares
- Arcos (arcs) - Define o grafo
- Agentes (agents) - Referências aos agentes
- **Campo `logica`** - JavaScript com chamada WebSocket

### 3.2 Estrutura do JSON

```json
{
  "nome": "Sistema de Processamento - Projeto X",
  "version": "1.0",
  "description": "Petri Net gerada automaticamente",

  "lugares": [
    {
      "id": "P1",
      "nome": "Sistema\\nIniciado",
      "tokens": 1,
      "coordenadas": {"x": 100, "y": 200},
      "delay": 0,
      "subnet": {},
      "agentId": null,
      "input_data": {"system_start": true},
      "output_data": {},
      "logica": "const output = {...input, status: 'started'}; return output;"
    },
    {
      "id": "P2",
      "nome": "read_email_task",
      "tokens": 0,
      "coordenadas": {"x": 350, "y": 200},
      "delay": 1000,
      "subnet": {},
      "agentId": "email_reader_agent",
      "input_data": {
        "max_emails": 5,
        "timeout_seconds": 30
      },
      "output_data": {},
      "logica": "const output = utils.clone(input); try { const ws = new WebSocket('ws://localhost:6308'); const result = await new Promise((resolve, reject) => { const timeout = setTimeout(() => { ws.close(); reject(new Error('timeout')); }, 30000); ws.onopen = () => ws.send(JSON.stringify({type: 'execute_task', data: {task_name: 'read_email', input_data: input}})); ws.onmessage = (e) => { const response = JSON.parse(e.data); if (response.type === 'task_completed') { clearTimeout(timeout); ws.close(); resolve(response.data.result || response.data); }}; ws.onerror = () => { clearTimeout(timeout); reject(new Error('WebSocket error')); };}); Object.assign(output, result); output.status = 'completed'; } catch (error) { output.status = 'error'; output.error = error.message; } return output;"
    }
  ],

  "transicoes": [
    {
      "id": "T1",
      "nome": "Iniciar\\nProcessamento",
      "coordenadas": {"x": 225, "y": 200}
    },
    {
      "id": "T2",
      "nome": "Processar\\nEmails",
      "coordenadas": {"x": 475, "y": 200}
    }
  ],

  "arcos": [
    {"origem": "P1", "destino": "T1", "peso": 1},
    {"origem": "T1", "destino": "P2", "peso": 1},
    {"origem": "P2", "destino": "T2", "peso": 1}
  ],

  "agentes": [
    {
      "id": "email_reader_agent",
      "nome": "Email Reader Agent",
      "coordenadas": {"x": 290, "y": 50}
    }
  ]
}
```

### 3.3 Geração do Campo `logica` (JavaScript)

**Template do JavaScript:**

```javascript
const output = utils.clone(input);

try {
  const ws = new WebSocket('ws://localhost:6308');

  const result = await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      ws.close();
      reject(new Error('timeout'));
    }, 30000);

    ws.onopen = () => ws.send(JSON.stringify({
      type: 'execute_task',
      data: {
        task_name: '[TASK_NAME]',
        input_data: input
      }
    }));

    ws.onmessage = (e) => {
      const response = JSON.parse(e.data);
      if (response.type === 'task_completed') {
        clearTimeout(timeout);
        ws.close();
        resolve(response.data.result || response.data);
      }
    };

    ws.onerror = () => {
      clearTimeout(timeout);
      reject(new Error('WebSocket error'));
    };
  });

  Object.assign(output, result);
  output.status = 'completed';

} catch (error) {
  output.status = 'error';
  output.error = error.message;
}

return output;
```

### 3.4 Implementação

**Arquivo Novo:** `/backend/prompts/generate_petri_net.py`

```python
def get_petri_net_generation_prompt(
    task_execution_flow: str,
    tasks_yaml: str,
    agents_yaml: str,
    custom_instructions: str = ""
) -> str:
    """
    Gera prompt para criar Petri Net JSON completo
    """
    return f"""
Você é especialista em Petri Nets e geração de código JavaScript.

TAREFA: Gerar JSON COMPLETO da Petri Net com campo `logica`.

INPUTS:

1. FLUXO DE EXECUÇÃO:
{task_execution_flow[:20000]}

2. TASKS YAML:
{tasks_yaml[:10000]}

3. AGENTS YAML:
{agents_yaml[:5000]}

ESTRUTURA DA SAÍDA:

Gere JSON válido com esta estrutura EXATA:

{{
  "nome": "[Nome do Projeto]",
  "version": "1.0",
  "description": "[Descrição baseada no fluxo]",

  "lugares": [
    {{
      "id": "P1",
      "nome": "Sistema\\nIniciado",
      "tokens": 1,
      "coordenadas": {{"x": 100, "y": 200}},
      "delay": 0,
      "subnet": {{}},
      "agentId": null,
      "input_data": {{"system_start": true}},
      "output_data": {{}},
      "logica": "const output = {{...input, status: 'started'}}; return output;"
    }},
    {{
      "id": "P2",
      "nome": "[task_name]",
      "tokens": 0,
      "coordenadas": {{"x": 350, "y": 200}},
      "delay": 1000,
      "subnet": {{}},
      "agentId": "[agent_id]",
      "input_data": {{...}},  # DO YAML
      "output_data": {{}},
      "logica": "[JAVASCRIPT WEBSOCKET - ver template]"
    }}
  ],

  "transicoes": [...],
  "arcos": [...],
  "agentes": [...]
}}

REGRAS PARA `logica`:

Para P1 (inicial): JavaScript simples que retorna input + status

Para tasks (P2+): JavaScript com WebSocket seguindo EXATAMENTE:

```javascript
const output = utils.clone(input);
try {{
  const ws = new WebSocket('ws://localhost:6308');
  const result = await new Promise((resolve, reject) => {{
    const timeout = setTimeout(() => {{ ws.close(); reject(new Error('timeout')); }}, 30000);
    ws.onopen = () => ws.send(JSON.stringify({{type: 'execute_task', data: {{task_name: '[TASK_NAME]', input_data: input}}}}));
    ws.onmessage = (e) => {{ const response = JSON.parse(e.data); if (response.type === 'task_completed') {{ clearTimeout(timeout); ws.close(); resolve(response.data.result || response.data); }} }};
    ws.onerror = () => {{ clearTimeout(timeout); reject(new Error('WebSocket error')); }};
  }});
  Object.assign(output, result);
  output.status = 'completed';
}} catch (error) {{
  output.status = 'error';
  output.error = error.message;
}}
return output;
```

COORDENADAS:

- Distribuir lugares horizontalmente (x: 100, 350, 600, 850...)
- Y fixo em 200 para linearidade
- Agentes em y: 50 (acima dos lugares)
- Transições entre lugares (x médio)

ARCOS:

- Lugar → Transição → Lugar
- Peso sempre 1
- Conectar sequencialmente baseado em dependências

OUTPUT: Retorne APENAS o JSON. Sem markdown, sem explicações.

{custom_instructions}
"""
```

**Arquivo Novo:** `/backend/app/routers/petri_net.py`

```python
from fastapi import APIRouter, BackgroundTasks, Depends
from typing import Optional
import uuid

router = APIRouter(prefix="/petri-net", tags=["Petri Net"])

@router.post("/")
async def generate_petri_net(
    request: GeneratePetriNetRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Gera Petri Net JSON completo

    Input:
        - task_execution_flow_session_id
        - tasks_yaml_session_id
        - agents_yaml_session_id
        - custom_instructions

    Output:
        - petri_net.json salvo em petri_net_sessions
    """
    session_id = str(uuid.uuid4())

    # Buscar documentos
    flow = get_task_execution_flow_session(request.flow_session_id)
    tasks_yaml = get_tasks_yaml_session(request.tasks_yaml_session_id)
    agents_yaml = get_agents_yaml_session(request.agents_yaml_session_id)

    # Criar sessão
    create_petri_net_session({
        "id": session_id,
        "project_id": flow["project_id"],
        "user_id": current_user['id'],
        "status": "generating"
    })

    # Background task
    background_tasks.add_task(
        execute_petri_net_generation,
        session_id,
        flow["flow_document"],
        tasks_yaml["tasks_yaml_content"],
        agents_yaml["agents_yaml_content"],
        request.custom_instructions
    )

    return {"session_id": session_id, "status": "generating"}

async def execute_petri_net_generation(
    session_id: str,
    flow_document: str,
    tasks_yaml: str,
    agents_yaml: str,
    custom_instructions: str
):
    try:
        # 1. Construir prompt
        prompt = get_petri_net_generation_prompt(
            flow_document,
            tasks_yaml,
            agents_yaml,
            custom_instructions
        )

        # 2. Chamar LLM
        petri_net_json = await get_llm_response_async(
            prompt=prompt,
            system="Você é especialista em Petri Nets e JavaScript.",
            temperature=0.3,
            max_tokens=32000
        )

        # 3. Validar JSON
        petri_net_data = json.loads(petri_net_json)

        # 4. Validar estrutura
        validate_petri_net_structure(petri_net_data)

        # 5. Salvar
        update_petri_net_session(session_id, {
            "petri_net_json": petri_net_json,
            "total_places": len(petri_net_data.get("lugares", [])),
            "total_transitions": len(petri_net_data.get("transicoes", [])),
            "status": "completed"
        })

    except Exception as e:
        update_petri_net_session(session_id, {
            "status": "failed",
            "error_message": str(e)
        })
```

**Nova Tabela:** `petri_net_sessions`

```sql
CREATE TABLE `petri_net_sessions` (
  `id` CHAR(36) PRIMARY KEY,
  `project_id` CHAR(36) NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `task_execution_flow_session_id` CHAR(36),
  `tasks_yaml_session_id` CHAR(36),
  `agents_yaml_session_id` CHAR(36),
  `petri_net_json` LONGTEXT,
  `total_places` INT UNSIGNED DEFAULT 0,
  `total_transitions` INT UNSIGNED DEFAULT 0,
  `status` ENUM('generating','completed','failed') DEFAULT 'generating',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

---

## 🏗️ FASE 4: Geração de Código Python do Framework

### 4.1 Objetivo

Gerar arquivo **Python completo** (`projectagents.py`) com:
1. **State TypedDict** - Baseado no fluxo de execução
2. **Input Functions** - Uma para cada task
3. **Output Functions** - Uma para cada task
4. **TASK_REGISTRY** - Mapeamento completo
5. **execute_task_with_context()** - Executor genérico

### 4.2 Estrutura do Código Gerado

```python
# projectagents.py
# Gerado automaticamente pelo LangNet Interface
# Data: 2026-01-08

from __future__ import annotations
import os
import json
import yaml
from pathlib import Path
from typing import TypedDict, Optional, Any, Dict, List
from datetime import datetime
from crewai import Agent as AgentClass, Task as TaskClass, Crew as TeamClass

# ==================================================================
# 1. STATE DEFINITION
# ==================================================================

class ProjectState(TypedDict, total=False):
    """State acumulativo para o projeto (estilo LangGraph)"""

    # Configuração inicial
    max_emails: int

    # Task outputs (JSONs das tasks)
    emails_json: str
    classified_json: str
    stock_checked_json: str
    response_report_md: str

    # Dados estruturados (parsed)
    emails_data: Dict[str, Any]
    classification_data: Dict[str, Any]
    stock_data: Dict[str, Any]
    response_data: Dict[str, Any]

    # Metadados de execução
    execution_log: List[Dict[str, Any]]
    current_task: Optional[str]
    timestamp: str

# ==================================================================
# 2. LOAD YAMLS
# ==================================================================

BASE_DIR = Path(__file__).resolve().parent
agents_config = yaml.safe_load((BASE_DIR / "agents.yaml").read_text())
tasks_config = yaml.safe_load((BASE_DIR / "tasks.yaml").read_text())

# ==================================================================
# 3. TOOLS
# ==================================================================

from framework.tools import ToolClass

email_fetch_tool = ToolClass(
    name="Email Fetch Tool",
    description="Connects to IMAP and fetches unread emails.",
    tool_type="emailfetchtool",
    tool_config={
        "server": os.getenv("SMTP_HOST"),
        "email": os.getenv("EMAIL_USERNAME"),
        "password": os.getenv("EMAIL_PASSWORD")
    }
).create()[0]

# ==================================================================
# 4. AGENTS
# ==================================================================

def get_llm_instance():
    return os.getenv("DEFAULT_LLM", "gpt-4o-mini")

email_reader_agent = AgentClass(
    config=agents_config['email_reader_agent'],
    llm=get_llm_instance(),
    verbose=True,
    allow_delegation=False
)

classifier_agent = AgentClass(
    config=agents_config['classifier_agent'],
    llm=get_llm_instance(),
    verbose=True,
    allow_delegation=False
)

# ... outros agentes ...

# ==================================================================
# 5. INPUT/OUTPUT FUNCTIONS
# ==================================================================

def read_email_input_func(state: ProjectState) -> Dict[str, Any]:
    """Extrai max_emails do state"""
    return {"max_emails": state.get("max_emails", 5)}

def read_email_output_func(state: ProjectState, result: Any) -> ProjectState:
    """Atualiza state com resultado do read_email"""
    if isinstance(result, dict):
        emails_json = result.get("raw_output", json.dumps(result, ensure_ascii=False))
        emails_data = result
    else:
        emails_json = str(result)
        try:
            emails_data = json.loads(emails_json)
        except:
            emails_data = {"emails": [], "error": "Failed to parse"}

    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "read_email",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "emails_count": len(emails_data.get("emails", []))
    })

    return {
        **state,
        "emails_json": emails_json,
        "emails_data": emails_data,
        "execution_log": execution_log,
        "current_task": "read_email",
        "timestamp": datetime.now().isoformat()
    }

# ... outras funções ...

# ==================================================================
# 6. TASK_REGISTRY
# ==================================================================

TASK_REGISTRY = {
    "read_email": {
        "input_func": read_email_input_func,
        "output_func": read_email_output_func,
        "requires": [],
        "produces": ["emails_json", "emails_data"],
        "agent": email_reader_agent,
        "tools": [email_fetch_tool],
        "description": "Lê emails não lidos e estrutura dados"
    },
    "classify_message": {
        "input_func": classify_message_input_func,
        "output_func": classify_message_output_func,
        "requires": ["emails_json"],
        "produces": ["classified_json", "classification_data"],
        "agent": classifier_agent,
        "tools": [],
        "description": "Classifica emails em categorias"
    }
}

# ==================================================================
# 7. EXECUTOR
# ==================================================================

def execute_task_with_context(
    task_name: str,
    context_state: ProjectState,
    verbose: Optional[callable] = None
) -> ProjectState:
    """Executa uma task usando context state"""

    if task_name not in TASK_REGISTRY:
        raise ValueError(f"Task '{task_name}' não encontrada")

    task_config = TASK_REGISTRY[task_name]

    # 1. Extrair input
    task_input = task_config["input_func"](context_state)

    # 2. Criar task
    task_obj = TaskClass(
        description=tasks_config[task_name]['description'].format(**task_input),
        expected_output=tasks_config[task_name]['expected_output'],
        agent=task_config["agent"],
        tools=task_config["tools"]
    )

    # 3. Executar
    crew = TeamClass(
        agents=[task_config["agent"]],
        tasks=[task_obj],
        verbose=False
    )

    result = crew.kickoff(inputs=task_input)

    # 4. Atualizar state
    updated_state = task_config["output_func"](context_state, result)

    return updated_state
```

### 4.3 Implementação

**Arquivo Novo:** `/backend/prompts/generate_python_code.py`

```python
def get_python_code_generation_prompt(
    task_execution_flow: str,
    agents_yaml: str,
    tasks_yaml: str,
    custom_instructions: str = ""
) -> str:
    """Gera prompt para código Python completo"""

    return f"""
Você é especialista em Python, CrewAI e geração de código.

TAREFA: Gerar código Python COMPLETO de agentes multi-tarefa.

INPUTS:

1. FLUXO DE EXECUÇÃO:
{task_execution_flow[:25000]}

2. AGENTS YAML:
{agents_yaml[:8000]}

3. TASKS YAML:
{tasks_yaml[:12000]}

ARQUIVO DE SAÍDA: projectagents.py

ESTRUTURA:

# projectagents.py
# Gerado automaticamente

from __future__ import annotations
import os, json, yaml
from pathlib import Path
from typing import TypedDict, Optional, Any, Dict, List
from datetime import datetime
from crewai import Agent as AgentClass, Task as TaskClass, Crew as TeamClass

# 1. STATE DEFINITION
class ProjectState(TypedDict, total=False):
    [campos baseados na Seção 2 do fluxo]

# 2. LOAD YAMLS
BASE_DIR = Path(__file__).resolve().parent
agents_config = yaml.safe_load((BASE_DIR / "agents.yaml").read_text())
tasks_config = yaml.safe_load((BASE_DIR / "tasks.yaml").read_text())

# 3. TOOLS
[Criar tools baseadas no campo 'tools' do tasks.yaml]

# 4. AGENTS
[Criar agentes baseados no agents.yaml]

# 5. INPUT/OUTPUT FUNCTIONS
[Para CADA task na Seção 3 do fluxo, criar funções]

# 6. TASK_REGISTRY
TASK_REGISTRY = {{
    [Mapear todas as tasks]
}}

# 7. EXECUTOR
def execute_task_with_context(task_name, context_state, verbose=None):
    [Implementação genérica]

REGRAS CRÍTICAS:

1. **State TypedDict:** Extrair TODOS os campos da Seção 2.1, 2.2, 2.3 do fluxo
2. **Input Functions:** Copiar código Python da Seção 3 (Input Function de cada task)
3. **Output Functions:** Copiar código Python da Seção 3 (Output Function de cada task)
4. **Tools:** Inferir do campo 'tools' do tasks.yaml, criar instâncias ToolClass
5. **Agentes:** Criar instância AgentClass para cada agente do agents.yaml
6. **TASK_REGISTRY:** Mapear TODAS as tasks com todos os campos
7. **Type Hints:** Usar anotações completas (TypedDict, Optional, List, Dict)
8. **PEP 8:** Código limpo, docstrings, comentários

OUTPUT: Retorne APENAS o código Python. Sem markdown, sem explicações.

{custom_instructions}
"""
```

**Arquivo Novo:** `/backend/app/routers/python_code.py`

Similar ao petri_net.py, cria sessão e gera código via LLM.

**Nova Tabela:** `python_code_sessions`

---

## 🏗️ FASE 5: Geração de Servidor WebSocket

### 5.1 Objetivo

Gerar 2 arquivos:
1. **project_adapter.py** - Adapter específico do projeto
2. **start_websocket_project.py** - Script de inicialização

### 5.2 Estrutura dos Arquivos

**project_adapter.py:**

```python
# project_adapter.py
# Gerado automaticamente

from typing import Any, Dict, Tuple, Optional
from datetime import datetime
import json

from framework.websocket.base_adapter import BaseAdapter

class ProjectAdapter(BaseAdapter):
    def __init__(self):
        self.project_name = "ProjectX"
        self.supported_tasks = ["read_email", "classify_message", ...]

        self.context_state_schema = {
            "max_emails": 5,
            "emails_json": "",
            "execution_log": [],
            "timestamp": ""
        }

    def get_project_name(self) -> str:
        return self.project_name

    def supports_task(self, task_name: str) -> bool:
        return task_name in self.supported_tasks

    def convert_v1_to_backend_format(
        self,
        task_name: str,
        input_data: Any
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Converte dados V1 (frontend) para formato backend"""

        # Métodos específicos por task
        if task_name == "read_email":
            return self._convert_task1_read_email(input_data)
        elif task_name == "classify_message":
            return self._convert_task2_classify_message(input_data)
        # ...

    def _convert_task1_read_email(self, input_data):
        """Conversão específica para read_email"""
        context_state = {
            **self.context_state_schema,
            "max_emails": input_data.get("max_emails", 5),
            "timestamp": datetime.now().isoformat()
        }

        backend_input = {"max_emails": context_state["max_emails"]}

        return backend_input, {"states": [context_state], "merged_state": context_state}

    def convert_backend_result_to_v1(
        self,
        task_name: str,
        backend_result: Any,
        context_state_list: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Converte resultado backend para V1"""
        return {"result": backend_result, "status": "completed"}

    def generate_execution_script(
        self,
        task_name: str,
        backend_input: Dict[str, Any]
    ) -> str:
        """Gera script Python temporário"""
        return f"""
import sys
sys.path.append('/path/to/project')
from projectagents import execute_task_with_context
import json

result = execute_task_with_context("{task_name}", {backend_input})
print("RESULTADO_FINAL_JSON:", json.dumps(result))
print("TASK_COMPLETED_SUCCESS")
"""
```

**start_websocket_project.py:**

```python
# start_websocket_project.py
# Gerado automaticamente

import asyncio
from framework.websocket.websocket_generic_v7 import create_server
from project_adapter import ProjectAdapter

if __name__ == "__main__":
    adapter = ProjectAdapter()

    print(f"🚀 Iniciando WebSocket Server para {adapter.get_project_name()}")
    print(f"📡 Porta: 6308")
    print(f"📋 Tasks suportadas: {adapter.supported_tasks}")

    start_server = create_server(
        adapter,
        host="localhost",
        port=6308
    )

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
```

### 5.3 Implementação

**Arquivo Novo:** `/backend/prompts/generate_websocket_adapter.py`

Prompt para gerar adapter com métodos específicos por task.

**Arquivo Novo:** `/backend/app/routers/websocket_code.py`

Router para gerar os 2 arquivos WebSocket.

---

## 📁 Estrutura Final de Arquivos Gerados

Ao final do pipeline, o sistema gera:

```
projeto_x/
├── agents.yaml                      # YAML de agentes (CrewAI)
├── tasks.yaml                       # YAML de tasks (CrewAI)
├── task_execution_flow.md           # Documento de fluxo detalhado
├── petri_net.json                   # Petri Net completa
├── projectagents.py                 # Código Python do framework
├── project_adapter.py               # Adapter WebSocket
└── start_websocket_project.py       # Script de inicialização
```

Armazenamento no banco:
- `projects.project_data` → JSON com todos os arquivos

---

## 🔄 Pipeline Completo de Geração

```
1. User: Upload Document
   ↓
2. Document Analysis → requirements.md
   ↓
3. Specification Generation → specification.md
   ↓
4. Agent Task Spec → agent_task_spec.md (5 seções)
   ↓
5. [FASE 2] Agents YAML → agents.yaml (com metadata)
   ↓
6. [FASE 2] Tasks YAML → tasks.yaml (com requires/produces/tools)
   ↓
7. [FASE 1] Task Execution Flow → task_execution_flow.md (NOVO)
   ↓
8. [FASE 3] Petri Net → petri_net.json (com campo logica)
   ↓
9. [FASE 4] Python Code → projectagents.py
   ↓
10. [FASE 5] WebSocket → project_adapter.py + start_websocket_project.py
   ↓
11. Save to DB (projects.project_data = JSON de todos os arquivos)
```

---

## 📊 Tabelas de Banco de Dados Necessárias

```sql
-- Já existem:
-- agent_task_specification_sessions
-- agents_yaml_sessions
-- tasks_yaml_sessions

-- NOVAS (criar):

CREATE TABLE `task_execution_flow_sessions` (
  `id` CHAR(36) PRIMARY KEY,
  `project_id` CHAR(36),
  `user_id` CHAR(36),
  `agent_task_spec_session_id` CHAR(36),
  `agents_yaml_session_id` CHAR(36),
  `tasks_yaml_session_id` CHAR(36),
  `flow_document` LONGTEXT,
  `total_tasks` INT UNSIGNED DEFAULT 0,
  `has_parallelism` BOOLEAN DEFAULT FALSE,
  `status` ENUM('generating','completed','failed'),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE `petri_net_sessions` (
  `id` CHAR(36) PRIMARY KEY,
  `project_id` CHAR(36),
  `user_id` CHAR(36),
  `task_execution_flow_session_id` CHAR(36),
  `petri_net_json` LONGTEXT,
  `total_places` INT UNSIGNED DEFAULT 0,
  `total_transitions` INT UNSIGNED DEFAULT 0,
  `status` ENUM('generating','completed','failed'),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE `python_code_sessions` (
  `id` CHAR(36) PRIMARY KEY,
  `project_id` CHAR(36),
  `user_id` CHAR(36),
  `task_execution_flow_session_id` CHAR(36),
  `python_code` LONGTEXT,
  `code_size` INT UNSIGNED DEFAULT 0,
  `status` ENUM('generating','completed','failed'),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE `websocket_code_sessions` (
  `id` CHAR(36) PRIMARY KEY,
  `project_id` CHAR(36),
  `user_id` CHAR(36),
  `task_execution_flow_session_id` CHAR(36),
  `adapter_code` LONGTEXT,
  `server_code` LONGTEXT,
  `status` ENUM('generating','completed','failed'),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

---

## ✅ Checklist de Implementação

### Fase 1: Documento de Fluxo (Task Execution Flow)
- [ ] Criar `/backend/prompts/generate_task_execution_flow.py`
- [ ] Criar `/backend/app/routers/task_execution_flow.py`
- [ ] Criar tabela `task_execution_flow_sessions`
- [ ] Implementar função `execute_flow_generation()`
- [ ] Adicionar validação de dependências
- [ ] Testar geração com TropicalSales

### Fase 2: Enriquecimento de YAMLs
- [ ] Modificar `/backend/prompts/generate_tasks_yaml.py` (adicionar campos)
- [ ] Atualizar validação em `tasks_yaml.py`
- [ ] Implementar `validate_tasks_yaml_enriched()`
- [ ] Implementar `topological_sort()` para dependências
- [ ] Testar geração com novos campos

### Fase 3: Petri Net com `logica`
- [ ] Criar `/backend/prompts/generate_petri_net.py`
- [ ] Criar `/backend/app/routers/petri_net.py`
- [ ] Criar tabela `petri_net_sessions`
- [ ] Implementar template JavaScript do campo `logica`
- [ ] Implementar `validate_petri_net_structure()`
- [ ] Testar geração de Petri Net completa

### Fase 4: Código Python
- [ ] Criar `/backend/prompts/generate_python_code.py`
- [ ] Criar `/backend/app/routers/python_code.py`
- [ ] Criar tabela `python_code_sessions`
- [ ] Implementar geração de State TypedDict
- [ ] Implementar geração de input/output functions
- [ ] Implementar geração de TASK_REGISTRY
- [ ] Testar execução do código gerado

### Fase 5: WebSocket
- [ ] Criar `/backend/prompts/generate_websocket_adapter.py`
- [ ] Criar `/backend/app/routers/websocket_code.py`
- [ ] Criar tabela `websocket_code_sessions`
- [ ] Implementar geração de adapter
- [ ] Implementar geração de server script
- [ ] Testar WebSocket connection

### Integração Final
- [ ] Atualizar `projects.project_data` schema
- [ ] Criar endpoint consolidado `/api/projects/generate-complete`
- [ ] Implementar pipeline sequencial completo
- [ ] Adicionar WebSocket streaming de progresso
- [ ] Criar interface frontend (opcional)
- [ ] Testes end-to-end com projeto real

---

## 📝 Arquivos a Criar/Modificar

### Novos Arquivos (Backend)

**Prompts:**
- `/backend/prompts/generate_task_execution_flow.py`
- `/backend/prompts/generate_petri_net.py`
- `/backend/prompts/generate_python_code.py`
- `/backend/prompts/generate_websocket_adapter.py`

**Routers:**
- `/backend/app/routers/task_execution_flow.py`
- `/backend/app/routers/petri_net.py`
- `/backend/app/routers/python_code.py`
- `/backend/app/routers/websocket_code.py`

**Models:**
- `/backend/app/models/task_execution_flow.py`
- `/backend/app/models/petri_net.py`
- `/backend/app/models/python_code.py`
- `/backend/app/models/websocket_code.py`

**Database:**
- `/backend/database/migrations/015_create_task_execution_flow_tables.sql`
- `/backend/database/migrations/016_create_petri_net_tables.sql`
- `/backend/database/migrations/017_create_python_code_tables.sql`
- `/backend/database/migrations/018_create_websocket_code_tables.sql`

### Arquivos a Modificar

**Backend:**
- `/backend/prompts/generate_tasks_yaml.py` - Adicionar campos requires/produces/tools
- `/backend/app/routers/tasks_yaml.py` - Atualizar validação
- `/backend/app/database.py` - Adicionar funções CRUD para novas tabelas
- `/backend/main.py` - Registrar novos routers

**Frontend (Opcional):**
- Criar páginas para visualização de cada etapa

---

## 🎯 Resultado Final

Ao completar todas as 5 fases, o sistema será capaz de:

1. ✅ **Gerar documento de fluxo detalhado** com todas as especificações de input/output
2. ✅ **YAMLs enriquecidos** com metadados completos (requires, produces, tools)
3. ✅ **Petri Net executável** com JavaScript que chama WebSocket
4. ✅ **Código Python completo** pronto para execução (State, TASK_REGISTRY, functions)
5. ✅ **Servidor WebSocket** funcional e específico por projeto

**Pipeline Completo:**
- Input: Documento de requisitos
- Output: Sistema multi-agente EXECUTÁVEL e IMPLANTÁVEL

**Tecnologias:**
- CrewAI para agentes
- LangGraph-style state management
- Petri Net para orquestração
- WebSocket para execução distribuída
- MySQL para persistência

---

**Plano criado por:** Claude Sonnet 4.5
**Data:** 2026-01-08
**Status:** Pronto para implementação
