# Análise de Padrões: Tools, Agents e Tasks

**Data:** 2025-12-23
**Objetivo:** Documentar padrões identificados em TropicalSales para aplicar na geração automática de Agentes e Tarefas do LangNet

---

## 1. TOOLS IDENTIFICADAS NO TROPICALSALES

### 1.1 email_fetch_tool
- **Arquivo:** tropicalsales/tasks.yaml:7
- **Task:** read_email
- **Agente:** email_reader_agent
- **Função:** Buscar emails não lidos
- **Parâmetros:** max_emails
- **Uso:** `email_fetch_tool para buscar emails não lidos, fazendo o parametro max_emails = {max_emails}`

### 1.2 natural_language_query_stock_tool
- **Arquivo:** tropicalsales/tasks.yaml:88
- **Task:** check_stock_availability
- **Agente:** stock_checker_agent
- **Função:** Consultar estoque usando linguagem natural
- **Retorna:** Formato "PRODUTO: [nome], ESTOQUE: [quantidade]"
- **Uso:** `Usar natural_language_query_stock_tool com nome_produto_pedido`

### 1.3 email_send_tool
- **Arquivo:** tropicalsales/tasks.yaml:146-150
- **Task:** generate_response
- **Agente:** response_generator_agent
- **Função:** Enviar emails de resposta
- **Parâmetros:** to_email, subject, content
- **Uso:** `OBRIGATÓRIO: Enviar email usando email_send_tool executando a ferramenta com esses parâmetros exatos`

---

## 2. TOOLS IDENTIFICADAS NO LANGNET

### 2.1 Search Tools (Atual)
- **Arquivo:** langnet_tasks.yaml:1228-1231
- **Task:** research_web_standards_compliance
- **Agente:** specification_web_researcher_agent
- **Tools:**
  - tavily_search_tool (AI-powered search)
  - serpapi_search_tool (Google SERP API)
  - serper_search_tool (Google Search API alternative)

### 2.2 Tools Necessárias (Inferidas do domínio)

**Análise de Documentos:**
- `document_reader_tool` - Ler documentos de requisitos
- `pdf_reader_tool` - Processar PDFs
- `json_parser_tool` - Parse de JSON estruturado

**Busca e Pesquisa:**
- `tavily_search_tool` ✓ (já existente)
- `serper_search_tool` ✓ (já existente)
- `web_scraper_tool` - Extrair dados de páginas web

**Geração de Código:**
- `code_docs_search_tool` - Buscar documentação de código
- `file_writer_tool` - Escrever arquivos YAML/Python
- `code_generator_tool` - Gerar código

**Persistência:**
- `database_query_tool` - Consultar banco de dados
- `yaml_writer_tool` - Escrever YAMLs formatados

**Comunicação (Opcional):**
- `slack_notification_tool` - Notificações Slack
- `email_send_tool` - Enviar emails (se necessário)

---

## 3. PADRÕES ESTRUTURAIS

### 3.1 Estrutura agents.yaml

```yaml
agent_name:
  role: >
    Descrição curta do papel (1-2 linhas)
    Foco no WHAT (o que o agente faz)

  goal: >
    Objetivo específico e mensurável
    Foco no WHY (por que existe)

  backstory: |
    Contexto detalhado com:
    1. Responsabilidades numeradas e específicas
    2. Instruções claras sobre comportamento
    3. Exemplos quando aplicável (opcional)
    4. Restrições ou limitações importantes

    Tom: Profissional, descritivo, "Você é..."

  verbose: true
  allow_delegation: false  # Geralmente false no TropicalSales
```

**Exemplo do TropicalSales:**
```yaml
stock_checker_agent:
  role: >
    Especialista em Verificação de Produtos em Estoque
  goal: >
    Analisar emails que sejam pedidos, consultar estoque dos produtos mencionados
    e identificar o produto mais similar disponível
  backstory: >
    Você é um especialista em análise de pedidos e consulta de estoque que:
    1. Identifica precisamente pedidos de produtos
    2. Extrai o nome do produto mencionado
    3. Consulta estoque usando natural_language_query_stock_tool
    4. Analisa as opções retornadas e identifica o produto mais similar ao solicitado
    5. Mantém registro estruturado das consultas e resultados
  verbose: true
  allow_delegation: false
```

### 3.2 Estrutura tasks.yaml

```yaml
task_name:
  description: >
    [Opcional] IMPORTANTE: Instruções críticas no topo

    Descrição concisa da tarefa (1-2 linhas)

    [Sempre presente] Input data format: Especificação dos dados de entrada
    Os dados estão disponíveis na variável {placeholder} contendo:
      * campo1: descrição do tipo e significado
      * campo2: descrição do tipo e significado
      * campo3: estrutura aninhada
        - subcampo1: descrição
        - subcampo2: descrição

    Process steps:
      1. [Frequente] OBRIGATÓRIO: Parse o JSON fornecido em {input_json}
      2. [Se usa tool] Usar nome_da_tool com parâmetros específicos
      3. Para cada item processado:
         - Ação específica
         - [Se condicional] Condição e ação
         - Manter dados originais intactos
      4. [Sempre] Retornar dados em formato especificado no expected_output

  expected_output: >
    Formato exato do resultado esperado

    Retornar JSON/Markdown/Texto contendo:
    - campo1: descrição e tipo
    - campo2: descrição e tipo
    - estrutura_aninhada:
      * subcampo1: descrição
      * subcampo2: descrição

    [Frequente] CRÍTICO: Manter todos os campos originais inalterados
    [Frequente] IMPORTANTE: Preservar estrutura de entrada + adicionar novos campos
```

**Exemplo do TropicalSales:**
```yaml
check_stock_availability:
  description: >
    IMPORTANTE: Processar APENAS os emails REAIS fornecidos em {input_json}.
    NUNCA criar dados fictícios.

    Verificar disponibilidade em estoque dos produtos solicitados em pedidos.

    Os dados classificados estão disponíveis na variável {input_json} contendo:
      * timestamp: data e hora da execução
      * total_emails: quantidade de emails processados
      * emails: lista onde cada email contém:
        - email_id: identificador único
        - from: email do remetente
        - categoria: classificação do email
        - nome_produto_pedido: nome do produto identificado (se pedido)
        - quantidade_pedido: quantidade do produto identificada (se pedido)

    Process steps:
      1. OBRIGATÓRIO: Parse o JSON fornecido em {input_json}
      2. Para cada email REAL na lista:
         - Se categoria for "pedidos":
           * Usar natural_language_query_stock_tool com nome_produto_pedido
           * Analisar produtos retornados no formato "PRODUTO: [nome], ESTOQUE: [quantidade]"
           * Selecionar o produto mais similar ao solicitado
           * Adicionar produto_escolhido e quantidade_disponivel ao email
         - Para outros emails, manter TODOS os dados originais inalterados

  expected_output: >
    Retornar texto em formato JSON mantendo TODA a estrutura do input e adicionando
    para cada email que tenha categoria igual a "pedidos":
    - produto_escolhido: nome do produto mais similar encontrado em estoque
    - quantidade_disponivel: quantidade em estoque do produto escolhido

    IMPORTANTE: Manter todos os emails (não apenas pedidos) para compatibilidade
    com próximas tasks.
```

---

## 4. PADRÕES DE USO DE TOOLS

### 4.1 Referência Explícita nas Instruções

**TropicalSales Pattern:**
```yaml
description: >
  Process steps:
    1. Usar email_fetch_tool para buscar emails, fazendo o parametro max_emails = {max_emails}
    2. Para cada email obtido...
```

**LangNet Pattern (atual):**
```yaml
# Tools definidas separadamente, não mencionadas na description
tools:
  - tavily_search_tool
  - serpapi_search_tool
  - serper_search_tool
```

**🎯 Recomendação:** Combinar ambos os padrões
- Definir tools explicitamente na seção `tools:`
- Mencionar tools nas instruções da description para clareza

### 4.2 Especificação de Parâmetros

**Sempre incluir:**
- Nome exato da tool
- Parâmetros esperados com placeholders: `{max_emails}`, `{nome_produto_pedido}`
- Formato de retorno esperado: "PRODUTO: [nome], ESTOQUE: [quantidade]"

**Exemplo:**
```yaml
- Usar natural_language_query_stock_tool com nome_produto_pedido
- Analisar produtos retornados no formato "PRODUTO: [nome], ESTOQUE: [quantidade]"
- Selecionar o produto mais similar ao solicitado
```

### 4.3 Instruções de Execução

**Pattern TropicalSales:**
```yaml
- OBRIGATÓRIO: Enviar email usando email_send_tool executando a ferramenta com esses parâmetros exatos:
  * to_email: email do cliente [from do email original]
  * subject: "Resposta ao email: [subject do email original]"
  * content: texto gerado do template bem formatado
- IMPORTANTE: Executar efetivamente a ferramenta email_send_tool para cada email de pedido, não apenas simular
```

**🎯 Características:**
- Uso de marcadores: OBRIGATÓRIO, IMPORTANTE, CRÍTICO
- Parâmetros listados com bullet points
- Instruções explícitas sobre execução real (não simulação)

---

## 5. PADRÕES DE STATE MANAGEMENT

### 5.1 Input/Output Accumulation Pattern

**Conceito:** Cada task recebe JSON acumulado, adiciona campos, preserva tudo.

**Exemplo do fluxo TropicalSales:**

```
read_email output:
{
  "timestamp": "...",
  "total_emails": 2,
  "emails": [
    {"email_id": "1", "from": "...", "subject": "...", "content": "..."}
  ]
}

↓ (passa para classify_message)

classify_message output:
{
  "timestamp": "...",           ← PRESERVADO
  "total_emails": 2,             ← PRESERVADO
  "emails": [
    {
      "email_id": "1",           ← PRESERVADO
      "from": "...",             ← PRESERVADO
      "subject": "...",          ← PRESERVADO
      "content": "...",          ← PRESERVADO
      "categoria": "pedidos",    ← ADICIONADO
      "justificativa": "..."     ← ADICIONADO
    }
  ]
}

↓ (passa para check_stock_availability)

check_stock_availability output:
{
  // ... todos os campos anteriores preservados ...
  "emails": [
    {
      // ... todos os campos anteriores ...
      "produto_escolhido": "...",      ← ADICIONADO
      "quantidade_disponivel": 10      ← ADICIONADO
    }
  ]
}
```

### 5.2 Instruções Recorrentes

**Preservação de Dados:**
```
- Manter TODOS os dados originais intactos
- CRÍTICO: Manter todos os campos originais inalterados
- Preservar estrutura de entrada
- Adicionar novos campos sem remover existentes
```

**Parse Obrigatório:**
```
1. OBRIGATÓRIO: Parse o JSON fornecido em {input_json}
2. Para cada item REAL na lista...
```

**Validação de Dados:**
```
IMPORTANTE: Processar APENAS os dados REAIS fornecidos. NUNCA criar dados fictícios.
```

---

## 6. MAPEAMENTO: ESPECIFICAÇÃO → AGENTS/TASKS

### 6.1 Análise de Seções da Especificação

**Seções relevantes para geração (conforme PLANO):**

| Seção | Conteúdo | Extração de Agents | Extração de Tasks |
|-------|----------|-------------------|-------------------|
| 2. Escopo | Objetivos, funcionalidades | Agentes de domínio | Tasks principais |
| 3. Requisitos Funcionais | Funcionalidades detalhadas | Agentes especializados | Tasks específicas |
| 4. Casos de Uso | Fluxos de interação | Agentes por caso de uso | Sequências de tasks |
| 5. Regras de Negócio | Lógica e validações | Agentes de validação | Tasks de verificação |
| 8. Fluxos de Processo | Workflows detalhados | Agentes por processo | Dependências de tasks |

### 6.2 Heurísticas de Identificação

**Para Agents:**
1. **Substantivos + Verbos Recorrentes:** "Sistema deve enviar", "Validador de dados"
   - → Agent: email_sender_agent, data_validator_agent

2. **Atores/Personas:** "Cliente", "Administrador", "Sistema externo"
   - → Agent: customer_interface_agent, admin_manager_agent

3. **Domínios Funcionais:** "Autenticação", "Relatórios", "Processamento"
   - → Agent: authentication_agent, report_generator_agent

4. **Responsabilidades Isoladas:** Cada agent faz UMA coisa bem feita
   - TropicalSales: Ler emails ≠ Classificar ≠ Verificar estoque ≠ Responder

**Para Tasks:**
1. **Verbos de Ação:** "Buscar", "Classificar", "Verificar", "Gerar", "Enviar"
   - → Tasks: read_email, classify_message, check_stock, generate_response

2. **Fluxos Sequenciais:** Ordem de execução definida
   - → Dependency chain via TASK_REGISTRY (requires/produces)

3. **Entradas/Saídas Explícitas:** O que recebe e o que produz
   - → Input/Output functions no TASK_REGISTRY

### 6.3 Regras de Atribuição de Tools

**Por Domínio Funcional:**

| Domínio | Tools Típicas |
|---------|---------------|
| Busca de dados | serper_search_tool, tavily_search_tool, web_scraper_tool |
| Leitura de documentos | document_reader_tool, pdf_reader_tool, json_parser_tool |
| Escrita de dados | file_writer_tool, database_query_tool, yaml_writer_tool |
| Comunicação | email_send_tool, slack_notification_tool |
| Análise de código | code_docs_search_tool, code_generator_tool |
| Consultas customizadas | natural_language_query_X_tool (específica do domínio) |

**Por Palavras-Chave na Especificação:**

| Palavra-Chave | Tool Sugerida |
|---------------|---------------|
| "pesquisar na web", "buscar informações" | serper_search_tool, tavily_search_tool |
| "ler documento", "processar PDF" | document_reader_tool, pdf_reader_tool |
| "gerar código", "criar arquivo" | code_generator_tool, file_writer_tool |
| "consultar banco", "verificar estoque" | database_query_tool, custom_query_tool |
| "enviar email", "notificar" | email_send_tool, slack_notification_tool |
| "parsear JSON", "estruturar dados" | json_parser_tool |

---

## 7. TEMPLATES DE GERAÇÃO

### 7.1 Template para Agent Generation Prompt

```python
def get_agent_generation_prompt(
    specification_document: str,
    requirements_json: str = None,
    detail_level: str = "balanced",
    max_agents: int = 10
) -> str:
    return f"""
Você é um especialista em design de sistemas multi-agente.

SPECIFICATION DOCUMENT:
{specification_document}

REQUIREMENTS (contexto adicional):
{requirements_json or "N/A"}

INSTRUCTIONS:
Analise as seções 2, 3, 4, 5, 8 da especificação e gere {max_agents} agentes.

Para cada agente, identifique:
1. ROLE: Papel específico (1-2 linhas)
2. GOAL: Objetivo mensurável
3. BACKSTORY: Contexto detalhado com responsabilidades numeradas
4. TOOLS: Lista de CrewAI tools necessárias (ex: serper_search_tool, document_reader_tool)
5. DELEGATION_TARGETS: Outros agentes com quem pode interagir
6. RATIONALE: Por que este agente é necessário

DETAIL LEVEL: {detail_level}
- concise: Backstories curtas (3-5 linhas)
- balanced: Backstories médias (5-8 linhas) [DEFAULT]
- detailed: Backstories detalhadas (8-12 linhas)

OUTPUT FORMAT (JSON):
[
  {{
    "name": "agent_name_snake_case",
    "role": "Descrição curta do papel",
    "goal": "Objetivo específico e mensurável",
    "backstory": "Você é um especialista...\\n1. Responsabilidade\\n2. Responsabilidade",
    "verbose": true,
    "allow_delegation": false,
    "suggested_tools": ["tool1", "tool2"],
    "delegation_targets": ["other_agent_name"],
    "rationale": "Explicação de por que este agente é necessário"
  }}
]

IMPORTANT:
- Use snake_case para agent names
- Tools devem ser CrewAI tools existentes
- Backstory deve usar "Você é..." e listar responsabilidades numeradas
- Evite agentes genéricos; seja específico para o domínio
"""
```

### 7.2 Template para Task Generation Prompt

```python
def get_task_generation_prompt(
    specification_document: str,
    agents_yaml: str,
    requirements_json: str = None,
    detail_level: str = "balanced"
) -> str:
    return f"""
Você é um especialista em design de workflows multi-agente.

SPECIFICATION DOCUMENT:
{specification_document}

GENERATED AGENTS:
{agents_yaml}

REQUIREMENTS (contexto adicional):
{requirements_json or "N/A"}

INSTRUCTIONS:
Analise a especificação e os agentes gerados para criar tasks.

Para cada task, defina:
1. DESCRIPTION: Instruções detalhadas com:
   - [Opcional] IMPORTANTE: Avisos críticos no topo
   - Descrição concisa da tarefa
   - Input data format: {placeholder} com estrutura completa
   - Process steps: Lista numerada com menções explícitas a tools
2. EXPECTED_OUTPUT: Formato exato do resultado
3. AGENT: Nome do agente responsável (deve existir em agents_yaml)
4. TOOLS: Lista de tools necessárias (mencionadas nos steps)
5. REQUIRES: Lista de fields de state necessários como input
6. PRODUCES: Lista de fields que esta task adiciona ao state
7. DEPENDENCIES: Lista de tasks que devem executar antes
8. RATIONALE: Por que esta task é necessária

DETAIL LEVEL: {detail_level}
- concise: Process steps breves (3-5 steps)
- balanced: Process steps médios (5-8 steps) [DEFAULT]
- detailed: Process steps detalhados (8-12 steps)

PATTERNS A SEGUIR:
1. Use placeholders: {{input_json}}, {{field_name}}
2. Sempre incluir "OBRIGATÓRIO: Parse o JSON fornecido" se usa {input_json}
3. Mencionar tools explicitamente: "Usar tool_name com parâmetro_x"
4. Especificar formato de retorno das tools
5. Incluir instruções de preservação: "Manter TODOS os dados originais intactos"

OUTPUT FORMAT (JSON):
[
  {{
    "name": "task_name_snake_case",
    "description": "Texto formatado conforme pattern...",
    "expected_output": "Formato exato do resultado...",
    "agent": "agent_name",
    "tools": ["tool1", "tool2"],
    "requires": ["field1", "field2"],
    "produces": ["new_field1", "new_field2"],
    "dependencies": ["previous_task_name"],
    "rationale": "Explicação"
  }}
]

IMPORTANT:
- Task names devem ser verbos de ação em snake_case
- Cada task deve ter um agent existente atribuído
- Definir dependências corretamente para ordem de execução
- Tools mencionadas na description devem estar na lista tools
"""
```

---

## 8. PRÓXIMOS PASSOS (IMPLEMENTAÇÃO)

### 8.1 Backend - Endpoints

**Arquivo:** `backend/app/routers/agent_task.py`

```python
@router.post("/agent-task/generate")
async def generate_agents_and_tasks(
    request: AgentTaskGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Gera agents.yaml e tasks.yaml a partir de especificação funcional.

    Steps:
    1. Buscar documento de especificação (session_id + version)
    2. Buscar requisitos relacionados para contexto adicional
    3. Gerar agentes via LLM usando agent_generation_prompt
    4. Parsear resposta JSON dos agentes
    5. Gerar agents.yaml
    6. Gerar tasks via LLM usando task_generation_prompt + agents.yaml
    7. Parsear resposta JSON das tasks
    8. Gerar tasks.yaml
    9. Criar agent_task_session no banco
    10. Salvar YAMLs no banco
    11. Retornar session_id + agents + tasks + YAMLs
    """
```

### 8.2 Backend - Prompts

**Arquivos:**
- `backend/prompts/agent_generation_prompt.py`
- `backend/prompts/task_generation_prompt.py`

Implementar templates da seção 7.1 e 7.2.

### 8.3 Backend - Models

**Arquivo:** `backend/app/models/agent_task.py`

```python
class AgentTaskGenerationRequest(BaseModel):
    specification_session_id: str
    specification_version: int = 1
    detail_level: str = "balanced"  # concise | balanced | detailed
    frameworks: List[str] = ["CrewAI"]
    custom_instructions: Optional[str] = None
    auto_generate_yaml: bool = True

class AgentData(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    verbose: bool = True
    allow_delegation: bool = False
    suggested_tools: List[str]
    delegation_targets: List[str]
    rationale: str

class TaskData(BaseModel):
    name: str
    description: str
    expected_output: str
    agent: str
    tools: List[str]
    requires: List[str]
    produces: List[str]
    dependencies: List[str]
    rationale: str

class AgentTaskGenerationResponse(BaseModel):
    session_id: str
    agents: List[AgentData]
    tasks: List[TaskData]
    agents_yaml: str
    tasks_yaml: str
    dependency_graph: Optional[dict]
    status: str
    message: str
```

### 8.4 Backend - Database Migration

**SQL para agent_task_sessions:**

```sql
CREATE TABLE agent_task_sessions (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    session_name VARCHAR(255) NOT NULL,
    specification_session_id VARCHAR(36) NOT NULL,
    specification_version INT NOT NULL,
    detail_level ENUM('concise', 'balanced', 'detailed') DEFAULT 'balanced',
    frameworks JSON NOT NULL,  -- ["CrewAI", "AutoGen"]
    custom_instructions TEXT,
    agents_count INT DEFAULT 0,
    tasks_count INT DEFAULT 0,
    agents_yaml LONGTEXT,
    tasks_yaml LONGTEXT,
    agents_json JSON,
    tasks_json JSON,
    dependency_graph JSON,
    status ENUM('generating', 'completed', 'failed') DEFAULT 'generating',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_project_user (project_id, user_id),
    INDEX idx_spec_session (specification_session_id)
);

CREATE TABLE agent_task_chat_messages (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    sender ENUM('user', 'system', 'assistant') NOT NULL,
    message TEXT NOT NULL,
    message_type ENUM('status', 'progress', 'result', 'error') DEFAULT 'status',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES agent_task_sessions(id) ON DELETE CASCADE,
    INDEX idx_session_created (session_id, created_at)
);
```

### 8.5 Frontend - Integração

**Arquivo:** `src/pages/AgentTaskPage.tsx`

Substituir TODOs (linhas 74, 107) por chamadas reais a `agentTaskService.generateAgentsAndTasks()`.

### 8.6 Frontend - History Modal

**Arquivo:** `src/components/agentTask/AgentTaskHistoryModal.tsx` (criar)

Similar a `SpecificationHistoryModal`, mas para carregar sessões de agent_task_sessions.

---

## 9. CHECKLIST DE IMPLEMENTAÇÃO

- [ ] **Backend - Prompts**
  - [ ] Criar `backend/prompts/agent_generation_prompt.py`
  - [ ] Criar `backend/prompts/task_generation_prompt.py`
  - [ ] Adicionar mapeamento de tools por domínio
  - [ ] Testar prompts com LLM (OpenAI/Anthropic)

- [ ] **Backend - Models**
  - [ ] Criar `backend/app/models/agent_task.py`
  - [ ] Definir Request/Response models
  - [ ] Adicionar validações Pydantic

- [ ] **Backend - Database**
  - [ ] Criar migration SQL
  - [ ] Executar migration em dev
  - [ ] Testar criação de registros

- [ ] **Backend - Endpoints**
  - [ ] Criar `backend/app/routers/agent_task.py`
  - [ ] Implementar `/agent-task/generate`
  - [ ] Implementar `/agent-task/sessions` (listar)
  - [ ] Implementar `/agent-task/sessions/{id}` (buscar)
  - [ ] Implementar `/agent-task/refine` (refinamento via chat)
  - [ ] Adicionar routes em `main.py`

- [ ] **Backend - Lógica de Geração**
  - [ ] Implementar chamada ao LLM para agentes
  - [ ] Parsear resposta JSON dos agentes
  - [ ] Converter JSON → YAML (agents.yaml)
  - [ ] Implementar chamada ao LLM para tasks
  - [ ] Parsear resposta JSON das tasks
  - [ ] Converter JSON → YAML (tasks.yaml)
  - [ ] Gerar dependency graph
  - [ ] Salvar no banco

- [ ] **Frontend - História Modal**
  - [ ] Criar `AgentTaskHistoryModal.tsx`
  - [ ] Listar sessões antigas
  - [ ] Carregar YAMLs selecionados
  - [ ] Mostrar preview de agents/tasks

- [ ] **Frontend - Integração**
  - [ ] Substituir TODO em startGeneration()
  - [ ] Substituir TODO em handleChatSend()
  - [ ] Implementar download de YAMLs
  - [ ] Implementar visualização de grafo de dependências

- [ ] **Testes**
  - [ ] Testar geração com especificação real
  - [ ] Validar estrutura YAML gerada
  - [ ] Testar refinamento via chat
  - [ ] Testar carregamento de histórico

---

## 10. REFERÊNCIAS

- **TropicalSales:** `/home/pasteurjr/progreact/valep12/visualtasksexec/tropicalsales/`
  - `agents.yaml` - Definições de 4 agentes
  - `tasks.yaml` - Definições de 4 tasks com tools

- **LangNet Atual:** `/home/pasteurjr/progreact/langnet-interface/backend/config/`
  - `langnet_agents.yaml` - Agentes atuais
  - `langnet_tasks.yaml` - Tasks atuais (1780 linhas)

- **Documentação de Planejamento:**
  - `PLANO: Geração Automática de Agentes e Tasks.md` (821 linhas)
  - `ANALISE_TROPICALSALES_ARQUITETURA.md` (1348 linhas)
  - `PLANO_INTERFACE_AGENTES_TAREFAS.md`

- **Código Frontend:**
  - `src/pages/AgentTaskPage.tsx` (390 linhas)
  - `src/services/agentTaskService.ts`
  - `src/contexts/NavigationContext.tsx`

---

**FIM DA ANÁLISE**
