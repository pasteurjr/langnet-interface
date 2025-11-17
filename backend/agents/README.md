# LangNet Multi-Agent System

Sistema completo de análise de documentos e geração de código usando agentes inteligentes baseado no framework customizado (tropicalagentssalesv6.py pattern).

## 📁 Estrutura de Arquivos

```
backend/
├── agents/
│   ├── __init__.py                 # Exports
│   ├── langnetstate.py             # Context States (TypedDict)
│   ├── langnettools.py             # Custom Tools (LangChain)
│   └── langnetagents.py            # Implementação principal (~860 linhas)
├── api/
│   ├── __init__.py
│   ├── langnetapi.py               # REST API endpoints
│   └── langnetwebsocket.py         # WebSocket streaming
└── config/
    ├── langnet_agents.yaml         # 8 agentes configurados
    └── langnet_tasks.yaml          # 9 tarefas configuradas
```

## 🤖 Agentes Disponíveis

1. **document_analyst_agent** - Análise de documentos e extração de requisitos
2. **requirements_validator_agent** - Validação de requisitos (SMART principles)
3. **specification_generator_agent** - Geração de especificações funcionais
4. **agent_specifier_agent** - Sugestão automática de agentes
5. **task_decomposer_agent** - Decomposição de requisitos em tarefas
6. **petri_net_designer_agent** - Modelagem de workflows (Petri Nets)
7. **yaml_generator_agent** - Geração de arquivos YAML (CrewAI)
8. **code_generator_agent** - Geração de código Python
9. **web_researcher_agent** 🆕 - Pesquisa web para complementar requisitos

## 📋 Tarefas (Pipeline)

```
1. analyze_document          → Parse documento
2. extract_requirements      → Extrai requisitos (FR, NFR, BR) + instruções customizadas
3. research_additional_info  🆕 → Pesquisa web para complementar requisitos
4. validate_requirements     → Valida qualidade
5. generate_specification    → Gera especificação Markdown
6. suggest_agents            → Sugere agentes necessários
7. decompose_tasks           → Cria tarefas executáveis
8. design_petri_net          → Modela workflow
9. generate_yaml_files       → Gera agents.yaml + tasks.yaml
10. generate_python_code     → Gera código Python completo
```

## 🚀 Como Usar

### 1. Executar Pipeline Completo (Python)

```python
from agents.langnetagents import execute_full_pipeline

result = execute_full_pipeline(
    project_id="proj-123",
    document_id="doc-456",
    document_path="/uploads/requirements.pdf",
    framework_choice="crewai",
    additional_instructions="Focus on HIPAA compliance and HL7 FHIR standards",  # 🆕 NEW!
    verbose_callback=lambda msg: print(f"[VERBOSE] {msg}")
)

# Acessar resultados
print(f"Agents gerados: {len(result['agents_data'])}")
print(f"Tasks geradas: {len(result['tasks_data'])}")
print(f"YAML: {result['agents_yaml'][:200]}")
print(f"Código: {result['generated_code'][:200]}")
```

### 2. Executar Workflow Específico

```python
from agents.langnetagents import execute_document_analysis_workflow

# Apenas análise de documento
state = execute_document_analysis_workflow(
    document_id="doc-456",
    document_path="/uploads/requirements.pdf"
)

print(f"Requirements: {len(state['requirements_data']['functional_requirements'])}")
print(f"Specification: {state['specification_md'][:200]}")
```

### 3. Executar Task Individual

```python
from agents.langnetagents import execute_task_with_context, init_full_state

# Inicializar state
state = init_full_state(
    project_id="proj-123",
    document_id="doc-456",
    document_path="/uploads/doc.pdf"
)

# Executar task específica
state = execute_task_with_context("analyze_document", state)
state = execute_task_with_context("extract_requirements", state)

print(f"Content: {state['document_content'][:200]}")
print(f"Requirements: {state['requirements_json']}")
```

## 🌐 API REST

### POST /api/langnet/execute-full-pipeline

Executa pipeline completo em background.

**Request:**
```json
{
  "project_id": "proj-123",
  "document_id": "doc-456",
  "document_path": "/uploads/requirements.pdf",
  "framework_choice": "crewai"
}
```

**Response:**
```json
{
  "execution_id": "exec-789",
  "status": "running",
  "message": "Pipeline execution started",
  "started_at": "2025-11-10T20:00:00"
}
```

### GET /api/langnet/execution/{execution_id}/status

Verifica progresso da execução.

**Response:**
```json
{
  "execution_id": "exec-789",
  "status": "running",
  "current_task": "extract_requirements",
  "current_phase": "requirements_extraction",
  "progress_percentage": 45.5,
  "completed_tasks": 4,
  "total_tasks": 9,
  "errors": [],
  "execution_log": [...]
}
```

### GET /api/langnet/execution/{execution_id}/result

Obtem resultado final.

### POST /api/langnet/save-results/{execution_id}

Salva resultados no banco MySQL.

## 📡 WebSocket (Real-time)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/langnet/exec-789');

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);

  switch(msg.type) {
    case 'connected':
      console.log('Connected:', msg.execution_id);
      break;
    case 'task_started':
      console.log('Task started:', msg.task, msg.phase);
      break;
    case 'task_completed':
      console.log('Task completed:', msg.task);
      break;
    case 'progress':
      console.log('Progress:', msg.percentage + '%');
      break;
    case 'execution_completed':
      console.log('Done!', msg.result_summary);
      break;
  }
};
```

## 🔧 Tools Disponíveis

```python
from agents.langnettools import create_langnet_tools

tools = create_langnet_tools()

# Tools criadas:
# - document_reader: Lê PDF, DOCX, TXT, MD
# - yaml_writer: Escreve YAML formatado
# - markdown_writer: Escreve Markdown
# - python_code_writer: Escreve código Python
# - database_query: Query no MySQL
# - yaml_validator: Valida sintaxe YAML
# - serper_search: 🆕 Google Search via Serper API
# - serpapi_search: 🆕 Multi-engine search (Google/Bing/DuckDuckGo)
```

## 📊 Context State Pattern

O sistema usa **Context State List pattern** (baseado em tropicalagentssalesv6.py):

```python
from agents.langnetstate import LangNetFullState

# State acumula dados de todas as tasks
state: LangNetFullState = {
    "project_id": "...",
    "document_id": "...",
    "document_content": "...",        # Task 1 output
    "requirements_data": {...},        # Task 2 output
    "validation_data": {...},          # Task 3 output
    "specification_md": "...",         # Task 4 output
    "agents_data": [...],              # Task 5 output
    "tasks_data": [...],               # Task 6 output
    "petri_net_data": {...},           # Task 7 output
    "agents_yaml": "...",              # Task 8 output
    "generated_code": "...",           # Task 9 output
    "execution_log": [...],
    "current_task": "...",
    "progress_percentage": 75.0
}
```

## 🎯 Task Registry

```python
from agents.langnetagents import TASK_REGISTRY

# Cada task tem:
TASK_REGISTRY["extract_requirements"] = {
    "input_func": extract_requirements_input_func,   # Extrai input do state
    "output_func": extract_requirements_output_func, # Atualiza state
    "requires": ["document_content"],                 # Dependências
    "produces": ["requirements_json", "requirements_data"],
    "agent": AGENTS["document_analyst"],
    "tools": [],
    "phase": "requirements_extraction"
}
```

## 📚 Dependências

```
langchain-openai
crewai (via framework)
pydantic
fastapi
websockets
```

## 🔑 Variáveis de Ambiente

```bash
# .env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
ANTHROPIC_API_KEY=...
```

## 🧪 Testes

```bash
# Testar agentes
python backend/agents/langnetagents.py

# Output esperado:
# LangNet Agents System
# Loaded 8 agents
# Loaded 9 tasks
# Agents: ['document_analyst', 'requirements_validator', ...]
# Tasks: ['analyze_document', 'extract_requirements', ...]
```

## 📈 Próximos Passos

1. ✅ Core implementado (agents, tasks, API, WebSocket)
2. ⏳ Testes unitários
3. ⏳ Integração com interface React
4. ⏳ Persistência Redis para execuções
5. ⏳ Monitoring e métricas

## 🆘 Troubleshooting

### Erro: "Module 'frameworks' not found"

Adicione o path:
```python
import sys
from pathlib import Path
frameworks_path = Path(__file__).parent.parent.parent / "frameworks"
sys.path.insert(0, str(frameworks_path))
```

### Erro: "OpenAI API key not set"

Configure:
```bash
export OPENAI_API_KEY=sk-your-key
```

### Erro: "TASK_REGISTRY task not found"

Verifique nome da task em `TASK_REGISTRY.keys()`.

## 📞 Suporte

Sistema implementado seguindo padrão **tropicalagentssalesv6.py**:
- Context State List ✅
- Input/Output Functions ✅
- Task Registry ✅
- LangGraph Compatible ✅
- Framework Adapters (v4) ✅
