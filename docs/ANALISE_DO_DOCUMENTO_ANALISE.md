# Plano: Análise Completa - Input/Output de Tarefas e Geração de Petri Net

**Data:** 2026-01-08
**Contexto:** Implementação do fluxo de tarefas para gerar Petri Net que orquestra agentes multi-tarefa
**Arquivos Analisados:**
- `docs/ANALISE_TROPICALSALES_ARQUITETURA.md` (1348 linhas)
- `framework/tropicalagentssalesv6.py` (523 linhas)

---

## 🎯 Objetivo

Entender **precisamente** como os dados de **input e output** de cada tarefa são obtidos no sistema, e como implementar o **fluxo de tarefas** para gerar a **Petri Net** que orquestra todas as tarefas.

---

## 📋 1. COMO OS DADOS DE INPUT/OUTPUT SÃO OBTIDOS

### 1.1 Arquitetura de State Management (Estilo LangGraph)

O sistema usa um **State TypedDict ACUMULATIVO** que passa entre tasks:

```python
class TropicalSalesState(TypedDict, total=False):
    # Configuração inicial
    max_emails: int

    # Task outputs (JSONs acumulativos)
    emails_json: str                    # Output da read_email
    classified_json: str                # Output da classify_message
    stock_checked_json: str             # Output da check_stock_availability
    response_report_md: str             # Output da generate_response

    # Dados estruturados (parsed)
    emails_data: Dict[str, Any]
    classification_data: Dict[str, Any]
    stock_data: Dict[str, Any]
    response_data: Dict[str, Any]

    # Metadados de execução
    execution_log: List[Dict[str, Any]]
    current_task: Optional[str]
    timestamp: str
```

**Conceito-chave:** Cada task **adiciona** campos ao state, **sem remover** os anteriores.

---

### 1.2 Input Functions - Como Extrair Dados do State

Cada task tem uma **input_func** que **SELECIONA** apenas os dados necessários do state:

**Exemplo 1: Primeira Task (read_email)**
```python
def read_email_input_func(state: TropicalSalesState) -> Dict[str, Any]:
    """Extrai max_emails do state (configuração inicial)"""
    return {"max_emails": state.get("max_emails", 5)}
```
- **Input:** State completo
- **Output:** Apenas `{"max_emails": 5}` (dado necessário para task)
- **Propósito:** Task recebe APENAS o que precisa, não todo o state

**Exemplo 2: Task Subsequente (classify_message)**
```python
def classify_message_input_func(state: TropicalSalesState) -> Dict[str, Any]:
    """Extrai emails_json do state (resultado da task anterior)"""
    return {"input_json": state.get("emails_json", "{}")}
```
- **Input:** State acumulativo (contém max_emails + emails_json)
- **Output:** Apenas `{"input_json": "<json dos emails>"}`
- **Propósito:** Task recebe resultado da task anterior

**Exemplo 3: Task Final (check_stock_availability)**
```python
def check_stock_input_func(state: TropicalSalesState) -> Dict[str, Any]:
    """Extrai classified_json do state (resultado da classificação)"""
    return {"input_json": state.get("classified_json", "{}")}
```

**Padrão:**
- ✅ Input function é **SELETOR** - não transforma, apenas extrai
- ✅ State tem TODOS os resultados anteriores disponíveis
- ✅ Task recebe dicionário simples com dados específicos

---

### 1.3 Output Functions - Como Atualizar State com Resultados

Cada task tem uma **output_func** que **ATUALIZA** o state preservando dados anteriores:

**Exemplo: classify_message_output_func**
```python
def classify_message_output_func(state: TropicalSalesState, result: Any) -> TropicalSalesState:
    """Atualiza state com resultado da classificação"""

    # 1. Parse do resultado (vem do CrewAI)
    if isinstance(result, dict):
        classified_json = result.get("raw_output", json.dumps(result, ensure_ascii=False))
        classification_data = result
    else:
        classified_json = str(result)
        try:
            classification_data = json.loads(classified_json)
        except:
            classification_data = {"classifications": [], "error": "Failed to parse"}

    # 2. Atualizar log de execução (rastreabilidade)
    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "classify_message",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "classifications_count": len(classification_data.get("emails", []))
    })

    # 3. Retornar NOVO STATE com dados anteriores + novos
    return {
        **state,  # ⚠️ CRÍTICO: Preserva max_emails, emails_json, etc.
        "classified_json": classified_json,          # ✅ Adiciona output desta task
        "classification_data": classification_data,  # ✅ Adiciona dados parsed
        "execution_log": execution_log,              # ✅ Atualiza log
        "current_task": "classify_message",          # ✅ Marca task atual
        "timestamp": datetime.now().isoformat()      # ✅ Atualiza timestamp
    }
```

**Padrão:**
- ✅ `{**state, ...}` **preserva todo state anterior**
- ✅ Adiciona novos campos (resultado da task)
- ✅ Atualiza execution_log para rastreabilidade
- ✅ State cresce a cada task executada

---

### 1.4 Fluxo de Dados Entre Tasks (Exemplo Completo)

```
ESTADO INICIAL:
{
  "max_emails": 5,
  "execution_log": [],
  "timestamp": "2026-01-08T10:00:00"
}

↓ TASK 1: read_email
├─ Input (via input_func): {"max_emails": 5}
├─ Executa: CrewAI busca emails
├─ Output (via output_func): Atualiza state
└─ NOVO STATE:
{
  "max_emails": 5,                          ← Preservado
  "emails_json": "[{...}, {...}]",          ← Adicionado
  "emails_data": {...},                     ← Adicionado
  "execution_log": [{task: "read_email"}],  ← Atualizado
  "current_task": "read_email",             ← Adicionado
  "timestamp": "2026-01-08T10:01:00"        ← Atualizado
}

↓ TASK 2: classify_message
├─ Input (via input_func): {"input_json": state.emails_json}  ← EXTRAI do state
├─ Executa: CrewAI classifica emails
├─ Output (via output_func): Atualiza state
└─ NOVO STATE:
{
  "max_emails": 5,                          ← Preservado
  "emails_json": "[{...}, {...}]",          ← Preservado
  "emails_data": {...},                     ← Preservado
  "classified_json": "[{...}]",             ← Adicionado
  "classification_data": {...},             ← Adicionado
  "execution_log": [                        ← Atualizado (2 itens)
    {task: "read_email"},
    {task: "classify_message"}
  ],
  "current_task": "classify_message",       ← Atualizado
  "timestamp": "2026-01-08T10:02:00"        ← Atualizado
}

↓ TASK 3: check_stock_availability
├─ Input (via input_func): {"input_json": state.classified_json}  ← EXTRAI do state
├─ Executa: CrewAI verifica estoque
└─ ... (padrão continua)
```

**Benefícios:**
- ✅ Dados de tasks anteriores sempre disponíveis
- ✅ Rastreabilidade completa via execution_log
- ✅ Fácil debugging (inspecionar state em qualquer ponto)
- ✅ Reexecução de tasks individuais possível

---

## 📊 2. TASK_REGISTRY - Mapeamento Completo de Tasks

### 2.1 Estrutura do TASK_REGISTRY

Arquivo: `framework/tropicalagentssalesv6.py:308-345`

```python
TASK_REGISTRY = {
    "read_email": {
        "input_func": read_email_input_func,           # Função que extrai input
        "output_func": read_email_output_func,         # Função que atualiza state
        "requires": [],                                 # Dependências (campos do state)
        "produces": ["emails_json", "emails_data"],    # Output (campos gerados)
        "agent": email_reader_agent,                   # Agente CrewAI responsável
        "tools": [email_fetch_tool],                   # Tools disponíveis
        "description": "Lê emails não lidos"           # Descrição
    },
    "classify_message": {
        "input_func": classify_message_input_func,
        "output_func": classify_message_output_func,
        "requires": ["emails_json"],                   # ⚠️ Depende de read_email
        "produces": ["classified_json", "classification_data"],
        "agent": classifier_agent,
        "tools": [],
        "description": "Classifica emails em categorias"
    },
    "check_stock_availability": {
        "input_func": check_stock_input_func,
        "output_func": check_stock_output_func,
        "requires": ["classified_json"],               # ⚠️ Depende de classify_message
        "produces": ["stock_checked_json", "stock_data"],
        "agent": stock_checker_agent,
        "tools": [natural_language_query_stock_tool],
        "description": "Verifica disponibilidade em estoque"
    },
    "generate_response": {
        "input_func": generate_response_input_func,
        "output_func": generate_response_output_func,
        "requires": ["stock_checked_json"],            # ⚠️ Depende de check_stock
        "produces": ["response_report_md", "response_data"],
        "agent": response_generator_agent,
        "tools": [email_send_tool],
        "description": "Gera e envia respostas"
    }
}
```

### 2.2 Campo `requires` - Grafo de Dependências

O campo `requires` define **dependências entre tasks**:

```
read_email (requires: [])
    ↓ produz: emails_json
classify_message (requires: ["emails_json"])
    ↓ produz: classified_json
check_stock_availability (requires: ["classified_json"])
    ↓ produz: stock_checked_json
generate_response (requires: ["stock_checked_json"])
    ↓ produz: response_report_md
```

**Uso:**
- Validar se state tem dados necessários antes de executar task
- Gerar visualização do grafo de dependências
- Determinar ordem de execução (topological sort)
- Detectar dependências circulares

---

## 🌐 3. PETRI NET - COMO SE CONECTA AO BACKEND

### 3.1 Estrutura de um Place (Lugar) na Petri Net

Arquivo: `docs/ANALISE_TROPICALSALES_ARQUITETURA.md:100-119`

Cada **place** na Petri Net representa uma **task**:

```json
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
    "imap_server": "imap.gmail.com",
    "timeout_seconds": 30
  },

  "output_data": {},

  "logica": "// P2 - Read Email (WebSocket V7)\nconst output = utils.clone(input);\ntry {\n  const ws = new WebSocket(\"ws://localhost:6307\");\n  const result = await new Promise((resolve, reject) => {\n    const timeout = setTimeout(() => { ws.close(); reject(new Error(\"timeout\")); }, 30000);\n    ws.onopen = () => ws.send(JSON.dumps({\n      type: \"execute_task\", \n      data: {\n        task_name: \"read_email\", \n        input_data: input\n      }\n    }));\n    ws.onmessage = (e) => { \n      const response = JSON.parse(e.data);\n      if (response.type === \"task_completed\") {\n        clearTimeout(timeout); \n        ws.close(); \n        resolve(response.data?.result || response.data || {}); \n      }\n    };\n    ws.onerror = () => { clearTimeout(timeout); reject(new Error(\"WebSocket error\")); };\n  });\n  output.emails = result.emails || [];\n  output.total_emails = result.total_emails || 0;\n  output.status = \"completed\";\n} catch (error) {\n  output.emails = []; \n  output.status = \"error\"; \n  output.error = error.message;\n}\nreturn output;"
}
```

---

### 3.2 Campo `logica` - O JavaScript que Chama o WebSocket

**O campo que você procurava é:** `logica`

**O que contém:**
- Código **JavaScript** executado pelo **navegador** (frontend)
- Cria conexão **WebSocket** com backend Python
- Envia mensagem com nome da task e input_data
- Aguarda resposta do backend
- Retorna output que é passado para próximo place

**Anatomia do código JavaScript:**

```javascript
// 1. PREPARAÇÃO: Clonar input (dados do place anterior)
const output = utils.clone(input);

try {
  // 2. WEBSOCKET: Criar conexão
  const ws = new WebSocket("ws://localhost:6307");

  // 3. PROMISE: Aguardar resposta assíncrona
  const result = await new Promise((resolve, reject) => {

    // Timeout de 30 segundos
    const timeout = setTimeout(() => {
      ws.close();
      reject(new Error("timeout"));
    }, 30000);

    // Ao abrir conexão, enviar mensagem
    ws.onopen = () => ws.send(JSON.stringify({
      type: "execute_task",        // Tipo de mensagem
      data: {
        task_name: "read_email",   // Nome da task (do TASK_REGISTRY)
        input_data: input          // Dados de entrada (do place anterior)
      }
    }));

    // Ao receber mensagem, processar resposta
    ws.onmessage = (e) => {
      const response = JSON.parse(e.data);
      if (response.type === "task_completed") {
        clearTimeout(timeout);
        ws.close();
        resolve(response.data?.result || response.data || {});
      }
    };

    // Se der erro, rejeitar promise
    ws.onerror = () => {
      clearTimeout(timeout);
      reject(new Error("WebSocket error"));
    };
  });

  // 4. PROCESSAR RESULTADO: Extrair dados da resposta
  output.emails = result.emails || [];
  output.total_emails = result.total_emails || 0;
  output.status = "completed";

} catch (error) {
  // 5. ERRO: Tratar erro e retornar estado de erro
  output.emails = [];
  output.status = "error";
  output.error = error.message;
}

// 6. RETORNAR: Output é passado para próximo place
return output;
```

---

### 3.3 Campos input_data e output_data

**`input_data`:** Configuração **ESTÁTICA** do place
- Define parâmetros de configuração (ex: max_emails=5, timeout=30s)
- **NÃO** contém dados de runtime
- É usado para **gerar** o input inicial da task

**`output_data`:** Sempre **VAZIO** no JSON da Petri Net
- Preenchido em **runtime** quando place executa
- Não é salvo no banco (apenas em memória da execução)

**Fluxo:**
```
Place é disparado (recebe token)
    ↓
JavaScript em "logica" executa
    ↓
input_data + dados do token anterior → input do WebSocket
    ↓
WebSocket chama backend Python
    ↓
Backend executa task usando TASK_REGISTRY
    ↓
Backend retorna resultado via WebSocket
    ↓
JavaScript preenche output
    ↓
output é passado para próximo place (via token)
```

---

## 🔄 4. FLUXO COMPLETO DE EXECUÇÃO

### 4.1 Arquitetura em Camadas

```
┌─────────────────────────────────────────────────────────┐
│  FRONTEND (Browser - GenericFrameworkPageV2.jsx)       │
│  ┌───────────────────────────────────────────────────┐ │
│  │  PETRI NET (JSON)                                 │ │
│  │  - lugares[] com JavaScript em .logica            │ │
│  │  - transições[]                                   │ │
│  │  - arcos[]                                        │ │
│  └───────────────────────────────────────────────────┘ │
│                     ↓ (disparo de place)               │
│  ┌───────────────────────────────────────────────────┐ │
│  │  JAVASCRIPT (campo "logica")                      │ │
│  │  - new WebSocket("ws://localhost:6308")           │ │
│  │  - send({type:"execute_task", data:{...}})        │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                        ↓ (WebSocket)
┌─────────────────────────────────────────────────────────┐
│  WEBSOCKET SERVER (Python - GenericWebSocketServer)    │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Recebe: {type:"execute_task", data:{...}}        │ │
│  │  Chama: adapter.convert_v1_to_backend_format()    │ │
│  │  Gera: script Python temporário                   │ │
│  │  Executa: subprocess com script                   │ │
│  │  Retorna: {type:"task_completed", data:{...}}     │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                        ↓ (subprocess)
┌─────────────────────────────────────────────────────────┐
│  BACKEND (Python - tropicalagentssalesv6.py)           │
│  ┌───────────────────────────────────────────────────┐ │
│  │  TASK_REGISTRY                                    │ │
│  │  - input_func(state) → task_input                 │ │
│  │  - CrewAI executa task                            │ │
│  │  - output_func(state, result) → updated_state     │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

### 4.2 Sequência de Execução (Passo a Passo)

**1. Usuário clica "Executar" na interface**
- GenericFrameworkPageV2.jsx dispara primeira transição
- Transição consome token do P1 (Sistema Iniciado)
- Transição produz token no P2 (read_email_task)

**2. Place P2 recebe token e executa**
- JavaScript em `logica` executa no browser
- Cria WebSocket: `ws://localhost:6308`
- Envia: `{type: "execute_task", data: {task_name: "read_email", input_data: {...}}}`

**3. WebSocket Server (Python) recebe mensagem**
- `GenericWebSocketServer.process_message()` processa
- Valida se adapter suporta task: `adapter.supports_task("read_email")`
- Converte dados: `adapter.convert_v1_to_backend_format("read_email", input_data)`
- Gera script Python temporário: `adapter.generate_execution_script(...)`
- Salva em `/tmp/temp_generic_task.py`

**4. Backend executa task em subprocess**
```bash
python /tmp/temp_generic_task.py
```

Script temporário contém:
```python
from framework.tropicalagentssalesv6 import execute_task_with_context, TASK_REGISTRY

# State reconstruído pelo adapter
context_state = {
    "max_emails": 5,
    "execution_log": [],
    "timestamp": "..."
}

# Executar task
result = execute_task_with_context("read_email", context_state)

# Retornar resultado
print("RESULTADO_FINAL_JSON:", json.dumps(result))
print("TASK_COMPLETED_SUCCESS")
```

**5. execute_task_with_context() executa**
```python
def execute_task_with_context(task_name, context_state):
    task_config = TASK_REGISTRY[task_name]

    # 1. EXTRAIR INPUT
    task_input = task_config["input_func"](context_state)
    # → {"max_emails": 5}

    # 2. CRIAR TASK CrewAI
    task_obj = TaskClass(
        description=tasks_config["read_email"]['description'].format(**task_input),
        expected_output=tasks_config["read_email"]['expected_output'],
        agent=task_config["agent"],  # email_reader_agent
        tools=task_config["tools"]    # [email_fetch_tool]
    )

    # 3. EXECUTAR
    crew = TeamClass(agents=[...], tasks=[task_obj])
    result = crew.kickoff(inputs=task_input)

    # 4. ATUALIZAR STATE
    updated_state = task_config["output_func"](context_state, result)
    # → {...state, "emails_json": "[...]", "emails_data": {...}}

    return updated_state
```

**6. WebSocket Server captura resultado**
- Subprocess imprime: `RESULTADO_FINAL_JSON: {...}`
- Server parseia JSON do stdout
- Converte de volta para V1: `adapter.convert_backend_result_to_v1(...)`
- Envia resposta: `{type: "task_completed", data: {...}}`

**7. Frontend recebe resposta**
- JavaScript em `logica` resolve Promise
- Extrai dados do resultado
- Preenche `output` com emails, total_emails, status
- Retorna `output`

**8. Petri Net avança**
- Token com `output` é produzido no próximo place (P3 - classify_message_task)
- Processo se repete para P3, P4, P5...

---

## 📝 5. IMPLEMENTAÇÃO NO LANGNET - PASSOS NECESSÁRIOS

### 5.1 Backend Python

**Arquivo:** `backend/agents/project_agents.py` (gerado por projeto)

**Componentes:**
1. **State TypedDict** - Define campos acumulativos
2. **Input Functions** - Uma para cada task
3. **Output Functions** - Uma para cada task
4. **TASK_REGISTRY** - Mapeamento completo
5. **execute_task_with_context()** - Executor genérico

**Exemplo:**
```python
class ProjectState(TypedDict, total=False):
    # Config
    project_id: str

    # Task outputs
    task1_output: str
    task2_output: str

    # Metadata
    execution_log: List[Dict]
    current_task: str
    timestamp: str

def task1_input_func(state: ProjectState) -> Dict[str, Any]:
    return {"project_id": state.get("project_id")}

def task1_output_func(state: ProjectState, result: Any) -> ProjectState:
    return {
        **state,
        "task1_output": result.get("output"),
        "execution_log": state.get("execution_log", []) + [{"task": "task1", "status": "completed"}],
        "timestamp": datetime.now().isoformat()
    }

TASK_REGISTRY = {
    "task1": {
        "input_func": task1_input_func,
        "output_func": task1_output_func,
        "requires": [],
        "produces": ["task1_output"],
        "agent": agent1,
        "tools": [tool1],
        "description": "Primeira task"
    }
}
```

---

### 5.2 Petri Net JSON

**Arquivo:** Salvo em `projects.project_data` (MySQL)

**Estrutura:**
```json
{
  "nome": "Projeto X",
  "version": "1.0",
  "lugares": [
    {
      "id": "P1",
      "nome": "task1",
      "agentId": "agent1",
      "input_data": {"project_id": "123"},
      "output_data": {},
      "logica": "const output = utils.clone(input); try { const ws = new WebSocket('ws://localhost:6308'); const result = await new Promise((resolve, reject) => { ws.onopen = () => ws.send(JSON.stringify({type: 'execute_task', data: {task_name: 'task1', input_data: input}})); ws.onmessage = (e) => { const response = JSON.parse(e.data); if (response.type === 'task_completed') { ws.close(); resolve(response.data.result || response.data); }};}); Object.assign(output, result); output.status = 'completed'; } catch (error) { output.status = 'error'; output.error = error.message; } return output;"
    }
  ],
  "transicoes": [...],
  "arcos": [...],
  "agentes": [...]
}
```

---

### 5.3 WebSocket Adapter (Opcional)

**Arquivo:** `backend/adapters/project_adapter.py`

**Responsabilidades:**
- Converter dados V1 (frontend) → Backend format
- Converter resultado backend → V1 format
- Gerar script Python temporário
- Parsear verbose do CrewAI

**Interface:**
```python
class ProjectAdapter(BaseAdapter):
    def supports_task(self, task_name: str) -> bool:
        return task_name in ["task1", "task2", ...]

    def convert_v1_to_backend_format(self, task_name, input_data):
        # Converte input_data em context_state
        context_state = {...}
        backend_input = {...}
        return backend_input, context_state

    def convert_backend_result_to_v1(self, task_name, backend_result, context_state):
        # Converte state atualizado para formato V1
        return {"result": backend_result}

    def generate_execution_script(self, task_name, backend_input):
        # Gera script Python que executa execute_task_with_context
        return f"""
import sys
sys.path.append('/path/to/backend')
from agents.project_agents import execute_task_with_context

result = execute_task_with_context("{task_name}", {backend_input})
print("RESULTADO_FINAL_JSON:", json.dumps(result))
"""
```

---

## ✅ 6. RESPOSTA ÀS PERGUNTAS DO USUÁRIO

### 6.1 Como os dados de input e output de cada tarefa são obtidos?

**Input:**
- Cada task tem `input_func(state) -> dict`
- Função **EXTRAI** campos específicos do state acumulativo
- Exemplo: `{"input_json": state.get("task1_output")}`

**Output:**
- Cada task tem `output_func(state, result) -> state`
- Função **ATUALIZA** state preservando dados anteriores
- Padrão: `{**state, "task2_output": result}`

**Fluxo:**
```
State → input_func → task_input → CrewAI → result → output_func → updated_state
```

---

### 6.2 Como implementar o fluxo de tarefas para obter a Petri Net?

**Componentes necessários:**

1. **State TypedDict** - Define campos acumulativos
2. **Input/Output Functions** - Uma para cada task
3. **TASK_REGISTRY** - Mapeamento completo com `requires`/`produces`
4. **Grafo de dependências** - Baseado em `requires`
5. **Gerador de Petri Net** - Converte TASK_REGISTRY + grafo → JSON da Petri Net
6. **Gerador de JavaScript** - Cria campo `logica` para cada place

**Algoritmo:**
```python
def generate_petri_net(task_registry):
    lugares = []
    transicoes = []
    arcos = []

    for task_name, config in task_registry.items():
        # Criar place para task
        place = {
            "id": f"P_{task_name}",
            "nome": task_name,
            "agentId": config["agent"].name,
            "input_data": {...},  # Configuração estática
            "output_data": {},
            "logica": generate_websocket_javascript(task_name)  # ← Gerar JavaScript
        }
        lugares.append(place)

        # Criar transições baseadas em requires
        for required_field in config["requires"]:
            # Encontrar task que produz required_field
            source_task = find_task_that_produces(required_field)
            # Criar arco: source_task → transition → current_task
            create_edge(source_task, task_name)

    return {"lugares": lugares, "transicoes": transicoes, "arcos": arcos}
```

---

### 6.3 Qual campo chama o WebSocket?

**Campo:** `logica` (dentro de cada place)

**Tipo:** String contendo código JavaScript

**Conteúdo:**
- Cria `new WebSocket("ws://localhost:6308")`
- Envia `{type: "execute_task", data: {task_name: "...", input_data: {...}}}`
- Aguarda resposta `{type: "task_completed", data: {...}}`
- Retorna `output` para próximo place

**Geração:**
```python
def generate_websocket_javascript(task_name):
    return f"""
const output = utils.clone(input);
try {{
  const ws = new WebSocket('ws://localhost:6308');
  const result = await new Promise((resolve, reject) => {{
    ws.onopen = () => ws.send(JSON.stringify({{
      type: 'execute_task',
      data: {{task_name: '{task_name}', input_data: input}}
    }}));
    ws.onmessage = (e) => {{
      const response = JSON.parse(e.data);
      if (response.type === 'task_completed') {{
        ws.close();
        resolve(response.data.result || response.data);
      }}
    }};
  }});
  Object.assign(output, result);
  output.status = 'completed';
}} catch (error) {{
  output.status = 'error';
  output.error = error.message;
}}
return output;
"""
```

---

## 🎯 7. PRÓXIMOS PASSOS PARA IMPLEMENTAÇÃO

### 7.1 Prioridade Alta

1. ✅ Entender arquitetura (COMPLETO - este documento)
2. ⏭️ Criar gerador de State TypedDict a partir de tasks.yaml
3. ⏭️ Criar gerador de input/output functions
4. ⏭️ Criar gerador de TASK_REGISTRY
5. ⏭️ Criar gerador de Petri Net JSON (lugares, transições, arcos)
6. ⏭️ Criar gerador de JavaScript para campo `logica`

### 7.2 Prioridade Média

7. ⏭️ Implementar WebSocket Server genérico (pode reusar V7)
8. ⏭️ Implementar Adapter pattern por projeto
9. ⏭️ Integrar com frontend (GenericFrameworkPageV2.jsx)
10. ⏭️ Testes end-to-end

---

## 📚 Referências

- `docs/ANALISE_TROPICALSALES_ARQUITETURA.md` - Arquitetura completa
- `framework/tropicalagentssalesv6.py` - Implementação de referência
- TropicalSales - Projeto exemplo funcional
- LangGraph - Inspiração para state management

---

**Relatório criado por:** Claude Sonnet 4.5
**Data:** 2026-01-08
**Status:** Análise completa - Pronto para implementação
