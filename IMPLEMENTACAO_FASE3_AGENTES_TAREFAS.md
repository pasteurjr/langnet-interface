# Implementação Fase 3: Geração Automática de Agentes e Tarefas

## Resumo Executivo

**Objetivo**: Implementar geração automática via LLM de agentes e tarefas a partir da especificação funcional gerada na Fase 2.

**Status Atual**:
- ✅ Fase 1: Documentos → Requisitos (implementado)
- ✅ Fase 2: Requisitos → Especificação Funcional (implementado)
- 🎯 Fase 3: Especificação → Agentes + Tarefas (próxima)

**Infraestrutura Existente**:
- ✅ CRUD de agents e tasks (backend)
- ✅ Tabelas de banco de dados
- ✅ YAML configs com `agent_specifier_agent` e `task_decomposer_agent`
- ✅ Páginas frontend (AgentsPage, TasksPage) com dados mock
- ✅ Modais (AgentSpecifierModal, TaskSpecifierModal) simulados

**O que Falta**:
- ❌ Endpoints backend para geração via LLM
- ❌ Integração real frontend ↔ backend
- ❌ Prompt templates para análise de especificação

---

## Arquitetura da Solução

### Fluxo Completo
```
SpecificationPage (Fase 2 completa)
    ↓
[Botão "Gerar Agentes"]
    ↓
POST /api/agents/generate-from-specification
    ↓
LLM analisa Seções 2, 3, 4, 5 da especificação
    ↓
Retorna JSON com 8-12 agentes sugeridos
    ↓
AgentSpecifierModal mostra sugestões
    ↓
Usuário revisa/edita/aprova
    ↓
Salva na tabela agents
    ↓
[Botão "Gerar Tarefas"]
    ↓
POST /api/tasks/generate-from-specification
    ↓
LLM analisa Seções 5, 8, 9 + agentes aprovados
    ↓
Retorna JSON com tarefas + dependências
    ↓
TaskSpecifierModal mostra grafo de dependências
    ↓
Usuário revisa/edita/aprova
    ↓
Salva na tabela tasks
```

---

## Implementação: Backend (5 arquivos)

### 1. Prompt Template - Agentes
**Arquivo**: `backend/prompts/agent_generation.py` (NOVO)

**Função**: Gerar prompt que analisa especificação e sugere agentes

**Entrada**:
- `specification_document`: Markdown completo da especificação (14 seções)
- `requirements_json`: Requisitos originais para contexto
- `detail_level`: "concise" (5-7 agentes), "balanced" (8-12), "detailed" (12-15)
- `max_agents`: Limite máximo
- `focus_areas`: Lista opcional de áreas prioritárias

**Saída**: Prompt formatado que instrui LLM a:
1. Analisar Seções 2 (Visão Geral), 3 (RFs), 4 (RNFs), 5 (Casos de Uso), 8 (Regras de Negócio)
2. Identificar responsabilidades distintas
3. Retornar JSON array com agentes:
   - `name`: Identificador único (snake_case)
   - `role`: Descrição da função (1-2 frases)
   - `goal`: Objetivo estratégico
   - `backstory`: Contexto de expertise
   - `suggested_tools`: Ferramentas necessárias
   - `delegation_targets`: Agentes para os quais pode delegar
   - `rationale`: Justificativa citando requisitos (RF-XXX, UC-XXX)

**Exemplo de Output Esperado do LLM**:
```json
[
  {
    "name": "data_processor_agent",
    "role": "Agente especializado em processamento e transformação de dados",
    "goal": "Processar, validar e transformar dados garantindo integridade",
    "backstory": "Especialista em ETL com 10+ anos de experiência...",
    "suggested_tools": ["data_validator", "schema_converter"],
    "delegation_targets": ["database_agent"],
    "rationale": "Necessário para RF-003 (Processamento) e UC-002 (Importação)"
  }
]
```

---

### 2. Router - Geração de Agentes
**Arquivo**: `backend/app/routers/agent_generation.py` (NOVO)

**Endpoint**: `POST /api/agents/generate-from-specification`

**Request Body**:
```python
{
  "specification_session_id": "uuid",
  "detail_level": "balanced",  # concise | balanced | detailed
  "max_agents": 10,
  "focus_areas": ["data_processing", "api_integration"]  # opcional
}
```

**Lógica**:
1. Verifica autenticação e ownership da specification_session
2. Busca specification_document do banco
3. Busca requirements_json (se disponível) para contexto
4. Gera prompt usando `get_agent_generation_prompt()`
5. Chama LLM via `llm_client.complete_async()` (temperatura 0.7, max_tokens 8192)
6. Parseia resposta JSON do LLM
7. Valida com Pydantic
8. Retorna lista de `SuggestedAgent`

**Response**:
```python
{
  "session_id": "uuid",
  "suggested_agents": [...],  # Array de SuggestedAgent
  "analysis_summary": "Analyzed specification and generated 10 agents",
  "status": "success",
  "message": "Agent suggestions generated successfully"
}
```

**Função de Parsing**: `parse_agent_suggestions(llm_response: str)`
- Extrai JSON de markdown code blocks (```json ... ```)
- Trata JSON malformado com try/except
- Converte para lista de objetos `SuggestedAgent` (Pydantic)
- Lança `ValueError` se parsing falhar

---

### 3. Prompt Template - Tarefas
**Arquivo**: `backend/prompts/task_generation.py` (NOVO)

**Função**: Gerar prompt que decompõe especificação em tarefas

**Entrada**:
- `specification_document`: Markdown completo
- `agents`: Lista de agentes já criados/aprovados
- `decomposition_strategy`: "workflow" (baseado em fluxos), "functional" (por funcionalidade), "hybrid"

**Saída**: Prompt que instrui LLM a:
1. Analisar Seções 5 (Casos de Uso), 8 (Regras de Negócio), 9 (Fluxos de Trabalho)
2. Mapear cada tarefa para um agente específico
3. Identificar dependências entre tarefas
4. Retornar JSON array com tarefas:
   - `name`: Identificador único
   - `description`: O que a tarefa faz
   - `agent_id`: Agente responsável
   - `inputs`: Schema de entrada (dict)
   - `outputs`: Schema de saída (dict)
   - `steps`: Lista de passos de execução
   - `dependencies`: Lista de task_names que devem executar antes
   - `parallel_execution`: Lista de tasks que podem rodar em paralelo
   - `expected_duration`: Estimativa ("5min", "30min", "2h")
   - `rationale`: Justificativa citando casos de uso

**Exemplo de Output Esperado**:
```json
[
  {
    "name": "validate_input_data",
    "description": "Validar dados de entrada conforme schema",
    "agent_id": "data_processor_agent",
    "inputs": {"data": "object", "schema": "object"},
    "outputs": {"validated_data": "object", "errors": "array"},
    "steps": ["Load schema", "Apply validators", "Return results"],
    "dependencies": [],
    "parallel_execution": ["log_validation_attempt"],
    "expected_duration": "5min",
    "rationale": "Necessário para UC-002 (Importação de Dados)"
  }
]
```

---

### 4. Router - Geração de Tarefas
**Arquivo**: `backend/app/routers/task_generation.py` (NOVO)

**Endpoint**: `POST /api/tasks/generate-from-specification`

**Request Body**:
```python
{
  "specification_session_id": "uuid",
  "agent_ids": ["agent-uuid-1", "agent-uuid-2"],  # Agentes aprovados
  "decomposition_strategy": "workflow",  # workflow | functional | hybrid
  "include_dependencies": true
}
```

**Lógica**:
1. Verifica autenticação
2. Busca specification_document
3. Busca agentes selecionados da tabela `agents`
4. Gera prompt usando `get_task_generation_prompt()`
5. Chama LLM (temperatura 0.6, max_tokens 12288)
6. Parseia resposta JSON
7. Constrói grafo de dependências: `build_dependency_graph()`
8. Calcula caminho crítico: `calculate_critical_path()`
9. Retorna tarefas + grafo + caminho crítico

**Response**:
```python
{
  "session_id": "uuid",
  "suggested_tasks": [...],
  "dependency_graph": {
    "nodes": [{"id": "task1", "label": "...", "agent": "..."}],
    "edges": [{"from": "task1", "to": "task2", "type": "dependency"}]
  },
  "critical_path": ["task1", "task3", "task5"],
  "status": "success",
  "message": "Generated 15 tasks with dependency analysis"
}
```

**Funções Auxiliares**:
- `parse_task_suggestions()`: Similar a `parse_agent_suggestions`
- `build_dependency_graph()`: Cria estrutura de grafo direcionado
- `calculate_critical_path()`: Topological sort + longest path (algoritmo de caminho crítico)

---

### 5. Atualizar Main FastAPI
**Arquivo**: `backend/app/main.py` (MODIFICAR)

**Mudança**: Adicionar novos routers

```python
from app.routers import agent_generation, task_generation

# Adicionar após routers existentes
app.include_router(agent_generation.router, prefix="/api")
app.include_router(task_generation.router, prefix="/api")
```

---

## Implementação: Frontend (5 arquivos)

### 6. Service - Geração de Agentes
**Arquivo**: `src/services/agentGenerationService.ts` (NOVO)

**Função**: `generateAgentsFromSpecification(request)`

**Request**:
```typescript
{
  specification_session_id: string;
  detail_level?: 'concise' | 'balanced' | 'detailed';
  max_agents?: number;
  focus_areas?: string[];
}
```

**Implementação**:
```typescript
- Busca token de autenticação do localStorage
- POST para /api/agents/generate-from-specification
- Headers: Authorization Bearer + Content-Type JSON
- Retorna AgentGenerationResponse ou lança Error
```

**Response Type**:
```typescript
{
  session_id: string;
  suggested_agents: SuggestedAgent[];
  analysis_summary: string;
  status: string;
  message: string;
}
```

---

### 7. Service - Geração de Tarefas
**Arquivo**: `src/services/taskGenerationService.ts` (NOVO)

**Função**: `generateTasksFromSpecification(request)`

**Request**:
```typescript
{
  specification_session_id: string;
  agent_ids: string[];
  decomposition_strategy?: 'workflow' | 'functional' | 'hybrid';
  include_dependencies?: boolean;
}
```

**Implementação**: Similar ao agentGenerationService

---

### 8. Integração na SpecificationPage
**Arquivo**: `src/pages/SpecificationPage.tsx` (MODIFICAR)

**Novos Estados**:
```typescript
const [isGeneratingAgents, setIsGeneratingAgents] = useState(false);
const [isGeneratingTasks, setIsGeneratingTasks] = useState(false);
const [generatedAgents, setGeneratedAgents] = useState<SuggestedAgent[]>([]);
const [generatedTasks, setGeneratedTasks] = useState<SuggestedTask[]>([]);
```

**Novo Handler - Gerar Agentes**:
```typescript
const handleGenerateAgents = async () => {
  if (!currentSessionId) return;

  setIsGeneratingAgents(true);
  try {
    // Chama service
    const result = await generateAgentsFromSpecification({
      specification_session_id: currentSessionId,
      detail_level: 'balanced',
      max_agents: 10
    });

    // Armazena agentes
    setGeneratedAgents(result.suggested_agents);

    // Adiciona mensagem ao chat
    const agentMsg: ChatMessage = {
      id: uuidv4(),
      sender: 'agent',
      text: `✅ ${result.suggested_agents.length} agentes gerados`,
      timestamp: new Date(),
      type: 'result'
    };
    setChatMessages(prev => [...prev, agentMsg]);

    // Abre modal com sugestões
    setIsAgentSpecifierOpen(true);

  } catch (error) {
    console.error('Error generating agents:', error);
    alert('Erro ao gerar agentes. Tente novamente.');
  } finally {
    setIsGeneratingAgents(false);
  }
};
```

**Novo Handler - Gerar Tarefas**:
```typescript
const handleGenerateTasks = async (selectedAgentIds: string[]) => {
  // Similar ao handleGenerateAgents
  // Chama generateTasksFromSpecification()
  // Abre TaskSpecifierModal com grafo de dependências
};
```

**Novos Botões na Interface**:
```tsx
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
```

---

### 9. Estilos para Botões
**Arquivo**: `src/pages/SpecificationPage.css` (MODIFICAR)

**Adicionar**:
```css
.generation-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.btn-generate-agents,
.btn-generate-tasks {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-generate-agents:hover:not(:disabled),
.btn-generate-tasks:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-generate-agents:disabled,
.btn-generate-tasks:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
```

---

### 10. Atualizar AgentSpecifierModal (Opcional)
**Arquivo**: `src/components/agents/AgentSpecifierModal.tsx` (MODIFICAR)

**Mudança**: Substituir simulação `setTimeout` por dados reais

**Antes (Simulação)**:
```typescript
useEffect(() => {
  setTimeout(() => {
    setGeneratedAgents([/* mock data */]);
    setIsGenerating(false);
  }, 3000);
}, []);
```

**Depois (Dados Reais)**:
```typescript
interface AgentSpecifierModalProps {
  isOpen: boolean;
  suggestedAgents: SuggestedAgent[];  // Vem do backend
  onClose: () => void;
  onSave: (agents: Agent[]) => void;
  isSaving: boolean;
}

// Converte SuggestedAgent para Agent format
useEffect(() => {
  const converted = suggestedAgents.map(sa => ({
    id: uuidv4(),
    name: sa.name,
    role: sa.role,
    goal: sa.goal,
    backstory: sa.backstory,
    tools: sa.suggested_tools,
    // ... outros campos
  }));
  setEditedAgents(converted);
}, [suggestedAgents]);
```

---

## Arquivos a Criar/Modificar - Checklist

### Backend (Criar 4, Modificar 1)
- [ ] `backend/prompts/agent_generation.py` - CRIAR
- [ ] `backend/app/routers/agent_generation.py` - CRIAR
- [ ] `backend/prompts/task_generation.py` - CRIAR
- [ ] `backend/app/routers/task_generation.py` - CRIAR
- [ ] `backend/app/main.py` - MODIFICAR (adicionar 2 linhas)

### Frontend (Criar 2, Modificar 3)
- [ ] `src/services/agentGenerationService.ts` - CRIAR
- [ ] `src/services/taskGenerationService.ts` - CRIAR
- [ ] `src/pages/SpecificationPage.tsx` - MODIFICAR (adicionar estados, handlers, botões)
- [ ] `src/pages/SpecificationPage.css` - MODIFICAR (adicionar estilos dos botões)
- [ ] `src/components/agents/AgentSpecifierModal.tsx` - MODIFICAR (opcional: substituir mock)

**Total**: 10 arquivos (6 novos, 4 modificações)

---

## Considerações Técnicas

### Performance
- **Geração de Agentes**: ~30-60 segundos (chamada LLM)
- **Geração de Tarefas**: ~60-120 segundos (análise mais complexa)
- Frontend deve mostrar indicador de progresso, não timeout

### Parsing LLM Response
- LLM pode retornar JSON malformado
- Implementar retry automático se parsing falhar
- Usar `json.loads()` com try/except
- Fallback para regex extraction se necessário
- Validar schema com Pydantic antes de retornar

### Validação
- **Agentes**: Nomes únicos dentro do projeto
- **Tarefas**: Referências a agent_ids existentes
- **Grafo**: Não deve ter ciclos (validação backend)

### Segurança
- Verificar ownership da specification_session antes de gerar
- Sanitizar inputs para evitar prompt injection
- Rate limiting nos endpoints de geração (custo de LLM)

### Error Handling
- LLM falha → retornar erro 500 com mensagem clara
- JSON malformado → retry com prompt de correção
- Specification não encontrada → 404
- Sem permissão → 403

---

## Fluxo UX Completo

1. **Usuário está na SpecificationPage** (Fase 2 completa - especificação gerada)
2. **Clica "🤖 Gerar Agentes"**
   - Loading: "⏳ Gerando Agentes..."
   - Backend analisa especificação via LLM (30-60s)
   - Modal abre com 8-12 agentes sugeridos + rationale de cada um
3. **Usuário revisa agentes no modal**
   - Pode editar nome, role, goal, backstory
   - Pode remover agentes redundantes
   - Pode adicionar novos manualmente (opcional)
4. **Clica "✅ Salvar Agentes"**
   - Agentes são salvos na tabela `agents`
   - Modal fecha
5. **Clica "📋 Gerar Tarefas"** (agora habilitado)
   - Loading: "⏳ Gerando Tarefas..."
   - Backend analisa especificação + agentes aprovados (60-120s)
   - Modal abre com grafo de dependências visualizado
6. **Usuário revisa tarefas no modal**
   - Vê grafo de dependências (nodes + edges)
   - Vê caminho crítico destacado
   - Pode ajustar sequência, atribuir agentes
7. **Clica "✅ Salvar Tarefas"**
   - Tarefas são salvas na tabela `tasks`
   - Modal fecha
8. **Próxima fase**: Geração de YAML (Fase 4)

---

## Benefícios da Implementação

✅ **Automação**: Gera agentes/tarefas automaticamente da especificação
✅ **Inteligência**: LLM analisa contexto e sugere arquitetura otimizada
✅ **Flexibilidade**: Usuário pode revisar e ajustar sugestões antes de salvar
✅ **Rastreabilidade**: Rationale conecta cada agente/tarefa aos requisitos originais
✅ **Escalabilidade**: Funciona para projetos de qualquer tamanho
✅ **Consistência**: Garante que agentes cobrem todos os requisitos funcionais
✅ **Visualização**: Grafo de dependências ajuda a entender fluxo de tarefas
✅ **Otimização**: Caminho crítico identifica gargalos potenciais

---

## Estratégia de Implementação Recomendada

### Opção 1: Tudo de uma vez (2-3 horas)
- Implementar todos os 10 arquivos
- Testar end-to-end após conclusão
- **Risco**: Se algo falhar, debug mais difícil

### Opção 2: Backend primeiro (1-1.5 horas)
- Implementar 5 arquivos backend
- Testar via Postman/curl
- Depois implementar 5 arquivos frontend
- **Vantagem**: Validar lógica de geração antes de UI

### Opção 3: Agentes completo, depois Tarefas (incremental)
- **Iteração 1** (1-1.5 horas):
  - Prompt + router de agentes (backend)
  - Service + integração SpecificationPage (frontend)
  - Testar geração de agentes end-to-end
- **Iteração 2** (1-1.5 horas):
  - Prompt + router de tarefas (backend)
  - Service + integração SpecificationPage (frontend)
  - Testar geração de tarefas end-to-end
- **Vantagem**: Menor risco, validação incremental

---

## Próximos Passos

**Aguardando sua aprovação para começar a implementação.**

Escolha uma das opções:
1. **Implementar tudo agora** (Opção 1)
2. **Backend primeiro** (Opção 2)
3. **Incremental - Agentes primeiro** (Opção 3)

Ou sugira outra abordagem se preferir!
