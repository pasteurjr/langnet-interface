# ANÁLISE COMPLETA: Framework LangNet - Geração Automática de Sistemas Multi-Agente

**Data**: 2025-12-21
**Objetivo**: Entender COMPLETAMENTE a arquitetura do Framework LangNet para implementar geração automática de projetos no LangNet Interface

---

## 1. VISÃO GERAL DA ARQUITETURA COMPLETA

### 1.1 Dois Sistemas Separados

**SISTEMA 1: LangNet Interface** (este projeto - `/home/pasteurjr/progreact/langnet-interface`)
- **Função**: GERADOR de projetos completos
- **Stack**: React + TypeScript + FastAPI + MySQL
- **Responsabilidade**: Upload docs → Requisitos → Especificação → **GERA CÓDIGO COMPLETO**
- **Output**: Salva projeto em `projects.project_data` (JSON)

**SISTEMA 2: VisualTasksExec** (projeto separado - `/home/pasteurjr/progreact/valep12/visualtasksexec`)
- **Função**: EXECUTOR de projetos gerados
- **Stack**: React (interface de execução)
- **Interface**: `GenericFrameworkPageV2.jsx`
  - Lado esquerdo: Seleciona projeto (ex: "Gerenciador de Editais", "TropicalSales")
  - Centro: Visualiza Petri Net
  - Aba Operação: Executa passo a passo ou contínuo
- **Input**: Lê `projects.project_data` do banco MySQL (camerascasas.no-ip.info:3308)

### 1.2 Arquitetura de Geração e Execução

```
┌─────────────────────────────────────────────────────────────────┐
│           LANGNET INTERFACE (Gerador)                           │
│                                                                 │
│  Upload Docs → Requisitos → Especificação                      │
│                     ↓                                           │
│              [GERAÇÃO VIA LLM]                                  │
│                     ↓                                           │
│  ┌──────────────────────────────────────────┐                  │
│  │  agents.yaml (projeto específico)       │                  │
│  │  tasks.yaml (projeto específico)        │                  │
│  │  projectagents.py (State + TASK_REGISTRY)│                  │
│  │  project_adapter.py (WebSocket adapter) │                  │
│  │  Petri Net JSON (lugares + JavaScript)  │                  │
│  └──────────────────────────────────────────┘                  │
│                     ↓                                           │
│       SALVA em projects.project_data (MySQL)                   │
└─────────────────────────────────────────────────────────────────┘
                      ↓
                 [DATABASE]
          projects.project_data = JSON
                      ↓
┌─────────────────────────────────────────────────────────────────┐
│         VISUALTASKSEXEC (Executor)                              │
│                                                                 │
│  GenericFrameworkPageV2.jsx LÊ project_data                    │
│                     ↓                                           │
│  ┌───────────────────────────────────────────┐                 │
│  │  PETRI NET JSON (do banco)                │                 │
│  │  - lugares[] com JavaScript em .logica    │                 │
│  │  - transições[]                           │                 │
│  │  - arcos[]                                │                 │
│  │  - agentes[]                              │                 │
│  └───────────────────────────────────────────┘                 │
│                     ↓                                           │
│  JavaScript executa: new WebSocket("ws://localhost:6308")      │
│                     ↓                                           │
│  ┌───────────────────────────────────────────┐                 │
│  │  WEBSOCKET SERVER V7 (Python)             │                 │
│  │  - GenericWebSocketServer                 │                 │
│  │  - ProjectAdapter (gerado)                │                 │
│  └───────────────────────────────────────────┘                 │
│                     ↓                                           │
│  ┌───────────────────────────────────────────┐                 │
│  │  BACKEND (projectagents.py gerado)        │                 │
│  │  - ProjectState (TypedDict)               │                 │
│  │  - TASK_REGISTRY                          │                 │
│  │  - Input/Output Functions                 │                 │
│  └───────────────────────────────────────────┘                 │
│                     ↓                                           │
│  ┌───────────────────────────────────────────┐                 │
│  │  CREWAI + FRAMEWORK LANGNET               │                 │
│  │  - agents.yaml (gerado)                   │                 │
│  │  - tasks.yaml (gerado)                    │                 │
│  │  - Tools customizadas                     │                 │
│  └───────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. PETRI NET - ESTRUTURA E EXECUÇÃO

### 2.1 Arquivo: tropical_email_processing_petri_v3.json

**Estrutura:**
- **lugares (places)**: 5 places (P1 a P5), cada um representa uma task
- **transicoes**: 4 transitions (T1 a T4), controlam o fluxo entre places
- **arcos**: Conectam places → transitions → places (define o grafo)
- **agentes**: 4 agentes com coordenadas visuais para UI

### 2.2 Anatomia de um Place (P2 - read_email_task)

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

**Pontos-chave:**
- Campo `logica` contém **JavaScript executado pela UI** (navegador)
- Faz chamada **WebSocket** para `ws://localhost:6307`
- Envia mensagem: `{type: "execute_task", data: {task_name: "read_email", input_data: input}}`
- Aguarda resposta: `{type: "task_completed", data: {result: {...}}}`
- **Timeout** de 30 segundos
- Retorna `output` que é passado para o próximo place

### 2.3 Fluxo de Execução da Petri Net

```
P1 (Sistema Iniciado)
    ↓ [T1: Iniciar Processamento]
P2 (read_email_task) → WebSocket → Backend executa → retorna emails
    ↓ [T2: Classificar Emails]
P3 (classify_message_task) → WebSocket → Backend executa → retorna classificação
    ↓ [T3: Verificar Estoque]
P4 (check_stock_availability_task) → WebSocket → Backend executa → retorna estoque
    ↓ [T4: Gerar Respostas]
P5 (generate_response_task) → WebSocket → Backend executa → envia emails
```

**Disparo de Transições:**
- Quando um place tem `tokens >= 1`, a transição pode disparar
- Disparo consome token do place de entrada e produz token no place de saída
- Cada place executa sua `logica` JavaScript quando recebe token

---

## 3. YAML - DEFINIÇÕES DE AGENTES E TAREFAS

### 3.1 agents.yaml - Estrutura dos Agentes

**Exemplo: email_reader_agent**

```yaml
email_reader_agent:
  role: >
    Agente Buscador de Emails Não Lidos
  goal: >
    Buscar emails não lidos usando email_fetch_tool e estruturar seu conteúdo para análise
  backstory: >
    Você é um especialista em busca e leitura de emails responsável por:
    1. Buscar todos os emails não lidos usando email_fetch_tool
    2. Estruturar os dados básicos de cada email (remetente, assunto, conteúdo)
    3. Preparar estes dados em formato padronizado para análise posterior

    Você não faz nenhuma classificação ou análise do conteúdo,
    apenas garante que todos os emails não lidos sejam coletados
    e estruturados corretamente para o próximo agente.
  verbose: true
  allow_delegation: false
```

**Campos do Agent:**
- `role`: Papel do agente (1 linha descritiva)
- `goal`: Objetivo específico do agente
- `backstory`: Contexto detalhado, instruções, responsabilidades
- `verbose`: Se deve mostrar logs detalhados (true/false)
- `allow_delegation`: Se pode delegar tarefas para outros agentes (true/false)

**Agentes Definidos:**
1. `email_reader_agent` - Busca emails não lidos
2. `classifier_agent` - Classifica emails em categorias
3. `stock_checker_agent` - Verifica disponibilidade em estoque
4. `response_generator_agent` - Gera e envia respostas por email

### 3.2 tasks.yaml - Estrutura das Tarefas

**Exemplo: read_email task**

```yaml
read_email:
  description: >
    Buscar emails não lidos usando email_fetch_tool e estruturar seu conteúdo básico.
    Input data format: None (busca diretamente usando email_fetch_tool)

    Process steps:
      1. Usar email_fetch_tool para buscar emails não lidos, fazendo o parametro max_emails = {max_emails}
      2. Para cada email obtido:
         - Extrair dados básicos (remetente, assunto, conteúdo)
         - Estruturar em formato padronizado
      3. Retornar dados em formato JSON conforme especificado no expected_output

  expected_output: >
    Retornar um texto em formato JSON contendo as seguintes keys:
    - timestamp: data e hora da execução
    - total_emails: quantidade de emails processados
    - emails: lista de emails, onde cada email deve conter as keys:
      * email_id: identificador único
      * from: email do remetente
      * subject: assunto do email
      * content: texto completo do email
      * date: data e hora do email
      * status: indicador se email foi lido com sucesso
```

**Campos da Task:**
- `description`: Instruções detalhadas da task com **placeholders** (ex: `{max_emails}`)
- `expected_output`: Formato esperado da saída (JSON schema descritivo)

**Placeholders usados:**
- `{max_emails}` - Quantidade máxima de emails
- `{input_json}` - JSON de entrada das tasks anteriores

**Tasks Definidas:**
1. `read_email` - Busca emails (input: `{max_emails}`)
2. `classify_message` - Classifica emails (input: `{input_json}`)
3. `check_stock_availability` - Verifica estoque (input: `{input_json}`)
4. `generate_response` - Gera respostas (input: `{input_json}`)

---

## 4. STATE MANAGEMENT - TropicalSalesState (Similar ao LangGraph)

### 4.1 Definição do State (tropicalagentssalesv6.py:62-81)

```python
class TropicalSalesState(TypedDict, total=False):
    # Configuração inicial
    max_emails: int

    # Task outputs (JSONs das tasks)
    emails_json: str                    # read_email output
    classified_json: str                # classify_message output
    stock_checked_json: str             # check_stock_availability output
    response_report_md: str             # generate_response output

    # Dados estruturados (para facilitar parsing)
    emails_data: Dict[str, Any]         # Parsed emails_json
    classification_data: Dict[str, Any]  # Parsed classified_json
    stock_data: Dict[str, Any]          # Parsed stock_checked_json
    response_data: Dict[str, Any]       # Parsed response_report_md

    # Metadados de execução
    execution_log: List[Dict[str, Any]]
    current_task: Optional[str]
    timestamp: str
```

**Conceito-chave:**
- **State Acumulativo**: Cada task ADICIONA dados ao state, não substitui
- Similar ao **LangGraph**: State é um TypedDict que passa entre tasks
- **Persistência**: Outputs de tasks anteriores ficam disponíveis para tasks seguintes

### 4.2 Input/Output Functions - Transformação do State

**Padrão de Input Function:**

```python
def classify_message_input_func(state: TropicalSalesState) -> Dict[str, Any]:
    """V6: Extrai emails_json do context state acumulativo"""
    return {"input_json": state.get("emails_json", "{}")}
```

- **Responsabilidade**: Extrair APENAS os dados necessários do state
- **Entrada**: State completo
- **Saída**: Dicionário com dados para a task

**Padrão de Output Function:**

```python
def classify_message_output_func(state: TropicalSalesState, result: Any) -> TropicalSalesState:
    """V6: Atualiza context state com resultado do classify_message"""
    if isinstance(result, dict):
        classified_json = result.get("raw_output", json.dumps(result, ensure_ascii=False))
        classification_data = result
    else:
        classified_json = str(result)
        try:
            classification_data = json.loads(classified_json)
        except:
            classification_data = {"classifications": [], "error": "Failed to parse classifications"}

    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": "classify_message",
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "classifications_count": len(classification_data.get("emails", []))
    })

    return {
        **state,  # ⚠️ PRESERVA STATE ANTERIOR
        "classified_json": classified_json,  # Adiciona novo output
        "classification_data": classification_data,
        "execution_log": execution_log,
        "current_task": "classify_message",
        "timestamp": datetime.now().isoformat()
    }
```

- **Responsabilidade**: Atualizar state com resultado da task
- **Entrada**: State anterior + Resultado da task
- **Saída**: Novo state (merge do state anterior + novos dados)
- **Importante**: `{**state, ...}` **preserva todos os dados anteriores**

### 4.3 Fluxo de Dados Entre Tasks

```
TASK 1: read_email
├─ Input: {max_emails: 5}
├─ Output: {emails_json: "[...]", emails_data: {...}}
└─ State após: {max_emails, emails_json, emails_data, execution_log, ...}
    ↓
TASK 2: classify_message
├─ Input: {input_json: state.emails_json}  ← EXTRAI do state
├─ Output: {classified_json: "[...]", classification_data: {...}}
└─ State após: {max_emails, emails_json, classified_json, classification_data, ...}  ← ACUMULA
    ↓
TASK 3: check_stock_availability
├─ Input: {input_json: state.classified_json}  ← EXTRAI do state
├─ Output: {stock_checked_json: "[...]", stock_data: {...}}
└─ State após: {max_emails, emails_json, classified_json, stock_checked_json, ...}  ← ACUMULA
    ↓
TASK 4: generate_response
├─ Input: {input_json: state.stock_checked_json}  ← EXTRAI do state
├─ Output: {response_report_md: "...", response_data: {...}}
└─ State final: {todos os campos preenchidos}  ← STATE COMPLETO
```

**Benefícios:**
- ✅ Dados de tasks anteriores sempre disponíveis
- ✅ Rastreabilidade completa via `execution_log`
- ✅ Fácil debugging (inspecionar state em qualquer ponto)
- ✅ Reexecução de tasks individuais possível

---

## 5. TASK REGISTRY - MAPEAMENTO DE TASKS

### 5.1 Estrutura do TASK_REGISTRY (tropicalagentssalesv6.py:308-345)

```python
TASK_REGISTRY = {
    "read_email": {
        "input_func": read_email_input_func,
        "output_func": read_email_output_func,
        "requires": [],  # Primeira task - apenas configuração inicial
        "produces": ["emails_json", "emails_data"],
        "agent": email_reader_agent,
        "tools": [email_fetch_tool],
        "description": "Lê emails não lidos e estrutura dados"
    },
    "classify_message": {
        "input_func": classify_message_input_func,
        "output_func": classify_message_output_func,
        "requires": ["emails_json"],  # Precisa do resultado do read_email
        "produces": ["classified_json", "classification_data"],
        "agent": classifier_agent,
        "tools": [],
        "description": "Classifica emails em categorias"
    },
    # ... outras tasks
}
```

**Campos do Registry:**
- `input_func`: Função que extrai inputs do state
- `output_func`: Função que atualiza state com outputs
- `requires`: Lista de campos do state que a task precisa (dependências)
- `produces`: Lista de campos do state que a task gera
- `agent`: Instância do AgentClass (CrewAI)
- `tools`: Lista de tools disponíveis para o agent
- `description`: Descrição da task

**Validação de Dependências:**
- `requires` define DEPENDÊNCIAS entre tasks
- Permite validar se state tem os dados necessários antes de executar
- Facilita visualização do grafo de dependências

---

## 6. WEBSOCKET SERVER V7 - ARQUITETURA GENÉRICA

### 6.1 GenericWebSocketServer (websocket_generic_v7.py:23-242)

**Responsabilidades:**
- Comunicação WebSocket com HTML (recebe/envia mensagens)
- Processamento genérico de mensagens
- Captura de verbose estruturado
- **Delegação** de conversões para adapters

**Fluxo de Processamento:**

```python
async def process_message(self, data, websocket, client_id):
    message_type = data.get("type")  # "execute_task"
    payload = data.get("data", {})   # {task_name, input_data}

    if message_type == "execute_task":
        task_name = payload.get("task_name")
        input_data = payload.get("input_data")

        # 1. Validar se adapter suporta task
        if not self.adapter.supports_task(task_name):
            await self.send_error(websocket, f"Task nao suportada: {task_name}")
            return

        # 2. Executar task usando adapter
        result = await self.execute_task_with_adapter(task_name, input_data, websocket)

        # 3. Formatar resposta usando adapter
        final_response = self.adapter.format_task_response(task_name, result, duration)
        await websocket.send(json.dumps(final_response))
```

### 6.2 BaseAdapter Interface (base_adapter.py:19-129)

**Interface que todos os adapters devem implementar:**

```python
class BaseAdapter(ABC):
    @abstractmethod
    def get_project_name(self) -> str:
        """Retorna nome do projeto (ex: 'TropicalSales')"""
        pass

    @abstractmethod
    def supports_task(self, task_name: str) -> bool:
        """Verifica se task é suportada por este adapter"""
        pass

    @abstractmethod
    def convert_v1_to_backend_format(self, task_name: str, input_data: Any) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Converte dados V1 para formato do backend especifico
        Returns: Tuple[backend_input, context_state_list]"""
        pass

    @abstractmethod
    def convert_backend_result_to_v1(self, task_name: str, backend_result: Any, context_state_list: Dict[str, Any]) -> Dict[str, Any]:
        """Converte resultado do backend para formato V1"""
        pass

    @abstractmethod
    def generate_execution_script(self, task_name: str, backend_input: Dict[str, Any]) -> str:
        """Gera script Python temporario para execucao da task"""
        pass

    @abstractmethod
    def parse_verbose_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Faz parsing de linha de verbose"""
        pass

    @abstractmethod
    def format_task_response(self, task_name: str, result: Dict[str, Any], duration: float) -> Dict[str, Any]:
        """Formata resposta final da task"""
        pass
```

**Padrão de Adapter:**
- **Separation of Concerns**: WebSocket Server é genérico, conversões são no adapter
- **Reutilizável**: Mesmo server para TropicalSales, VALEP1, outros projetos
- **Extensível**: Criar novo adapter = implementar BaseAdapter

### 6.3 TropicalSalesAdapter - Conversões Específicas (tropical_sales_adapter.py)

**Exemplo: convert_v1_to_backend_format para classify_message**

```python
def _convert_task2_classify_message(self, input_data: Any) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """TASK 2: classify_message"""

    if isinstance(input_data, dict) and 'emails_json' in input_data:
        # Dados já estão no formato correto (sem wrapper 'result')
        emails_json = input_data.get('emails_json', '{}')

        # Criar Context State List
        context_state_list = {
            "states": [{
                **self.context_state_schema,
                "place_id": "P2_classify_message",
                "task_name": "classify_message",
                "max_emails": 5,
                "emails_json": emails_json,
                "emails_data": input_data.get('emails_data', {}),
                "execution_log": input_data.get('execution_log', []),
                "timestamp": datetime.now().isoformat()
            }],
            "merged_state": {
                **self.context_state_schema,
                "emails_json": emails_json,
                "timestamp": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat(),
        }

        # Backend input (formato esperado pela task)
        backend_input = {"input_json": emails_json}

        return backend_input, context_state_list
```

**Conversões realizadas:**
- **V1 format** (HTML/JavaScript) → **Context State** (TypedDict) → **Backend format** (input da task)
- Mantém rastreabilidade via `context_state_list`
- Adapter conhece o schema específico do TropicalSalesState

### 6.4 Execução de Task via Subprocess

**WebSocket Server executa task em subprocess separado:**

```python
async def execute_task_with_adapter(self, task_name, input_data, websocket):
    # 1. Adapter converte input
    backend_input, context_state_list = self.adapter.convert_v1_to_backend_format(task_name, input_data)

    # 2. Adapter gera script temporário
    temp_script = self.adapter.generate_execution_script(task_name, backend_input)

    with open('/tmp/temp_generic_task.py', 'w') as f:
        f.write(temp_script)

    # 3. Executar script em subprocess
    process = subprocess.Popen(
        ['python', '/tmp/temp_generic_task.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    # 4. Processar output linha por linha
    result = None
    while True:
        line = process.stdout.readline()
        if not line:
            break

        # Capturar resultado final
        if line.startswith("RESULTADO_FINAL_JSON:"):
            result_json = line.replace("RESULTADO_FINAL_JSON:", "").strip()
            result = json.loads(result_json)

        # Parsear verbose e enviar para interface
        elif self.adapter.should_parse_verbose_line(line):
            step_data = self.adapter.parse_verbose_line(line, task_name)
            if step_data:
                await websocket.send(json.dumps({
                    "type": "execution_step",
                    "data": step_data
                }))

    # 5. Converter resultado de volta para V1
    v1_result = self.adapter.convert_backend_result_to_v1(task_name, result, context_state_list)

    return v1_result
```

**Benefícios do Subprocess:**
- ✅ Isolamento de execução (crash não derruba WebSocket Server)
- ✅ Captura de stdout/stderr em tempo real
- ✅ Parsing de verbose linha por linha
- ✅ Envio de progress updates para interface via WebSocket

---

## 7. FRAMEWORK ADAPTER - INTEGRAÇÃO CREWAI + LANGGRAPH

### 7.1 FrameworkAdapterFactory (frameworkagentsadapterv4.py:1038-1090)

**Factory retorna adaptadores para diferentes frameworks:**

```python
class FrameworkAdapterFactory:
    @staticmethod
    def get_framework_adapters(version: str = "crewai", api_key: Optional[str] = None):
        if version == "crewai":
            return {
                "memory_system": LangChainFullTaskMemorySystem,
                "agent": HybridAgentAdapter,
                "task": LangGraphTaskAdapter,
                "team": LangGraphTeamAdapter,
                "tool": HybridToolAdapter,
                "strategy": AiTeamProcessingStrategy,
                "process": AiTeamProcess,
                "processtype": ProcessType,
                "basetool": AiTeamBaseTool,
                "pipeline": PipelineAdapter,
                "graph": Graph,
                "agentstate": AgentState,
                "memory_factory": AiTeamMemorySystemFactory,
            }
```

**Framework usado:**
- **CrewAI** para agentes e tasks
- **LangGraph** para state management e orchestration
- **Hybrid adapters** para compatibilidade entre frameworks

### 7.2 LangGraphTaskAdapter - Tasks como Nós do LangGraph

```python
class LangGraphTaskAdapter(HybridTaskAdapter):
    def __init__(
        self,
        description: str = None,
        expected_output: str = None,
        agent: Optional[HybridAgentAdapter] = None,
        tools: Optional[List[Tool]] = None,
        state_class: Type[Any] = None,
        input_func: Callable[[Any], Dict[str, Any]] = None,
        output_func: Callable[[Any, Any], Any] = None,
    ):
        self.input_func = input_func
        self.output_func = output_func
        self.state_class = state_class

    def as_langflow_node(self):
        def node_func(state: self.state_class) -> self.state_class:
            # 1. Input function extrai dados do state
            input_state = self.input_func(state)

            # 2. Executa a task (CrewAI)
            result = self.execute(input_state)

            # 3. Output function atualiza state com resultado
            output_state = self.output_func(state, result)

            return output_state

        return node_func
```

**Conceito:**
- Task do CrewAI vira **nó do LangGraph**
- Input/Output functions fazem **bridge** entre state e task
- State class é TypedDict (ex: TropicalSalesState)

### 7.3 Graph - StateGraph Wrapper

```python
class Graph(BaseTudo):
    """Adaptador para o StateGraph do LangGraph"""

    END = langgraph.graph.END
    START = langgraph.graph.START

    def __init__(self, state_class: Type[Any]):
        self.state_class = state_class
        self.graph = StateGraph(state_class)
        self.checkpointer = MemorySaver()

    def add_node(self, key: str, node: Union[HybridTaskAdapter, HybridTeamAdapter, Any]):
        if isinstance(node, (HybridTaskAdapter, HybridTeamAdapter)):
            real_name = node.get_node_name()
            node = node.as_langflow_node()
            self.graph.add_node(real_name, node)
            return real_name
        else:
            self.graph.add_node(key, node)
            return key

    def add_edge(self, start: str, end: Union[str, END]):
        self.graph.add_edge(start, end)
        return self

    def compile(self):
        return self.graph.compile()

    def execute(self, initial_state: Optional[AgentState] = None, **kwargs) -> AgentState:
        app = self.compile()
        return app.invoke(initial_state, **kwargs)
```

**Uso:**
```python
# Criar grafo
graph = Graph(state_class=TropicalSalesState)

# Adicionar tasks como nós
graph.add_node("read_email", task1_adapter)
graph.add_node("classify", task2_adapter)
graph.add_node("check_stock", task3_adapter)
graph.add_node("generate_response", task4_adapter)

# Definir fluxo
graph.set_entry_point("read_email")
graph.add_edge("read_email", "classify")
graph.add_edge("classify", "check_stock")
graph.add_edge("check_stock", "generate_response")
graph.add_edge("generate_response", graph.END)

# Executar
result = graph.execute(initial_state={"max_emails": 5})
```

---

## 8. PADRÕES CRÍTICOS PARA REPLICAR NO LANGNET

### 8.1 YAML Structure - Agents e Tasks

**✅ Implementar:**

```yaml
# agents.yaml
agent_name:
  role: "Descrição curta do papel"
  goal: "Objetivo específico do agente"
  backstory: |
    Contexto detalhado com:
    - Responsabilidades
    - Instruções específicas
    - Formato de saída esperado
  verbose: true
  allow_delegation: false

# tasks.yaml
task_name:
  description: |
    Descrição da task com placeholders {param1}, {param2}

    Process steps:
      1. Passo 1
      2. Passo 2
      3. Passo 3

  expected_output: |
    Formato detalhado da saída esperada (JSON schema descritivo)
    - campo1: descrição
    - campo2: descrição
```

### 8.2 State Management - TypedDict Acumulativo

**✅ Implementar:**

```python
from typing import TypedDict, List, Dict, Any, Optional

class ProjectState(TypedDict, total=False):
    # Input inicial
    project_name: str
    requirements_version: int

    # Outputs de cada task (acumulativo)
    task1_output: str
    task2_output: str
    task3_output: str

    # Dados estruturados
    task1_data: Dict[str, Any]
    task2_data: Dict[str, Any]

    # Metadata
    execution_log: List[Dict[str, Any]]
    current_task: Optional[str]
    timestamp: str

# Input function - extrai dados do state
def task2_input_func(state: ProjectState) -> Dict[str, Any]:
    return {
        "input_json": state.get("task1_output", "{}"),
        "project_name": state.get("project_name", "")
    }

# Output function - atualiza state preservando anterior
def task2_output_func(state: ProjectState, result: Any) -> ProjectState:
    return {
        **state,  # ⚠️ PRESERVA TUDO
        "task2_output": result.get("output", ""),
        "task2_data": result,
        "execution_log": state.get("execution_log", []) + [{
            "task": "task2",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }],
        "current_task": "task2",
        "timestamp": datetime.now().isoformat()
    }
```

### 8.3 TASK_REGISTRY - Mapeamento Completo

**✅ Implementar:**

```python
TASK_REGISTRY = {
    "task1": {
        "input_func": task1_input_func,
        "output_func": task1_output_func,
        "requires": [],  # Campos do state necessários
        "produces": ["task1_output", "task1_data"],  # Campos que gera
        "agent": agent1_instance,
        "tools": [tool1, tool2],
        "description": "Descrição da task1"
    },
    "task2": {
        "input_func": task2_input_func,
        "output_func": task2_output_func,
        "requires": ["task1_output"],  # Depende de task1
        "produces": ["task2_output", "task2_data"],
        "agent": agent2_instance,
        "tools": [tool3],
        "description": "Descrição da task2"
    }
}

# Executor genérico
def execute_task_with_context(task_name: str, context_state: ProjectState) -> ProjectState:
    task_config = TASK_REGISTRY[task_name]

    # 1. Extrair input do state
    task_input = task_config["input_func"](context_state)

    # 2. Criar task do CrewAI
    task_obj = CrewTask(
        description=tasks_yaml[task_name]['description'].format(**task_input),
        expected_output=tasks_yaml[task_name]['expected_output'],
        agent=task_config["agent"],
        tools=task_config["tools"]
    )

    # 3. Executar
    crew = Crew(agents=[task_config["agent"]], tasks=[task_obj])
    result = crew.kickoff(inputs=task_input)

    # 4. Atualizar state
    updated_state = task_config["output_func"](context_state, result)

    return updated_state
```

### 8.4 Adapter Pattern para WebSocket (Opcional - se usar WebSocket)

**✅ Se implementar WebSocket:**

```python
class LangNetAdapter(BaseAdapter):
    def __init__(self):
        self.project_name = "LangNet"
        self.supported_tasks = ["task1", "task2", "task3"]

    def supports_task(self, task_name: str) -> bool:
        return task_name in self.supported_tasks

    def convert_v1_to_backend_format(self, task_name: str, input_data: Any) -> Tuple[Dict, Dict]:
        # Conversão específica V1 → Context State → Backend
        context_state = self.get_initial_context_state()
        # ... preencher context_state com input_data
        backend_input = {...}  # Formato esperado pela task
        return backend_input, context_state

    def convert_backend_result_to_v1(self, task_name: str, backend_result: Any, context_state: Dict) -> Dict:
        # Conversão Backend → V1 para interface
        return {"result": backend_result}

    def generate_execution_script(self, task_name: str, backend_input: Dict) -> str:
        # Script Python temporário
        return f"""
import sys
sys.path.append('/path/to/langnet')
from backend.agents.langnet import execute_task_with_context

result = execute_task_with_context("{task_name}", {repr(backend_input)})
print("RESULTADO_FINAL_JSON:", json.dumps(result))
print("TASK_COMPLETED_SUCCESS")
"""
```

---

## 9. ESTRUTURA DE ARQUIVOS RECOMENDADA PARA LANGNET

```
backend/
├── agents/
│   ├── langnet_agents.py           # Definições de agents (carrega YAML)
│   ├── langnet_tasks.py            # TASK_REGISTRY + execute_task_with_context
│   └── langnet_state.py            # ProjectState TypedDict + input/output functions
├── config/
│   ├── agents.yaml                 # Agentes do projeto
│   └── tasks.yaml                  # Tasks do projeto
├── prompts/
│   ├── agent_generation.py         # Prompt para gerar agents.yaml
│   └── task_generation.py          # Prompt para gerar tasks.yaml
├── app/routers/
│   ├── agent_task_generation.py    # Endpoint unificado /generate-from-specification
│   └── execution.py                # Endpoints de execução de tasks
└── framework/
    ├── adapter.py                  # BaseAdapter se usar WebSocket
    └── websocket_server.py         # GenericWebSocketServer se usar WebSocket

frontend/
├── src/
│   ├── services/
│   │   ├── agentTaskService.ts     # Service para geração
│   │   └── executionService.ts     # Service para execução
│   ├── pages/
│   │   ├── AgentTaskPage.tsx       # Interface unificada
│   │   └── ExecutionPage.tsx       # Visualização de execução
│   └── components/
│       ├── agenttask/
│       │   ├── YAMLPreview.tsx
│       │   └── AgentTaskViewer.tsx
│       └── execution/
│           └── PetriNetVisualization.tsx
```

---

## 10. CHECKLIST DE IMPLEMENTAÇÃO

### 10.1 Backend

- [ ] Criar `ProjectState` TypedDict com campos acumulativos
- [ ] Criar input/output functions para cada task
- [ ] Criar `TASK_REGISTRY` mapeando tasks → agents/tools/functions
- [ ] Criar `agents.yaml` com 4-6 agentes
- [ ] Criar `tasks.yaml` com 4-6 tasks + placeholders
- [ ] Implementar `execute_task_with_context(task_name, context_state)`
- [ ] Criar prompt `agent_generation.py` (gera agents.yaml)
- [ ] Criar prompt `task_generation.py` (gera tasks.yaml)
- [ ] Criar endpoint `/api/agent-task/generate-from-specification`
- [ ] Criar endpoint `/api/execution/execute-task`
- [ ] Adicionar validação de dependências (requires/produces)
- [ ] Implementar logging de execution_log

### 10.2 Frontend

- [ ] Criar `AgentTaskPage.tsx` (interface unificada)
- [ ] Criar `agentTaskService.ts` (service de geração)
- [ ] Criar `YAMLPreview.tsx` (visualização de agents.yaml/tasks.yaml)
- [ ] Criar `AgentTaskViewer.tsx` (cards de agentes e tasks)
- [ ] Adicionar botão "Gerar Agentes & Tasks" na SpecificationPage
- [ ] Implementar chat refinement (adicionar/remover agents/tasks)
- [ ] Criar visualização de TASK_REGISTRY (grafo de dependências)
- [ ] Adicionar download de agents.yaml e tasks.yaml
- [ ] Criar `ExecutionPage.tsx` (execução de workflows)

### 10.3 Database

- [ ] Validar tabelas `agents` e `tasks` existem
- [ ] Criar tabela `execution_agent_task_sessions`
- [ ] Criar tabela `execution_agent_task_chat_messages`
- [ ] Adicionar índices para queries rápidas

---

## 11. DIFERENÇAS E ADAPTAÇÕES NECESSÁRIAS

### 11.1 TropicalSales → LangNet

| Aspecto | TropicalSales | LangNet (Adaptar) |
|---------|---------------|-------------------|
| **Domínio** | Processamento de emails | Geração de código multi-agente |
| **State** | `TropicalSalesState` (emails, classificação, estoque) | `ProjectState` (requisitos, especificação, código) |
| **Tasks** | 4 tasks lineares | 6-8 tasks com possível paralelismo |
| **Petri Net** | Fluxo linear P1→P2→P3→P4→P5 | Fluxo com branches/parallelism |
| **WebSocket** | Execução via WebSocket + subprocess | Execução via API REST (ou WebSocket se necessário) |
| **Tools** | email_fetch, email_send, stock_checker | code_generator, yaml_validator, file_writer |

### 11.2 Simplificações Possíveis

**Para MVP, considerar:**
1. **Não usar WebSocket inicialmente** - Executar tasks via API REST síncrona
2. **Não usar Petri Net visual** - Definir fluxo hardcoded no backend
3. **Focar em state management** - Implementar ProjectState + TASK_REGISTRY corretamente
4. **YAML generation via LLM** - Gerar agents.yaml e tasks.yaml com um único prompt

**Complexidade adicional (para futuro):**
1. WebSocket + subprocess para execução assíncrona
2. Petri Net visual editor
3. Adapter pattern para diferentes frameworks (CrewAI, AutoGen, LangChain)

---

## 12. SCHEMA DO BANCO DE DADOS

### 12.1 Tabela `projects` (MySQL - camerascasas.no-ip.info:3308)

```sql
CREATE TABLE projects (
  id CHAR(36) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,               -- Ex: "Gerenciador de Editais"
  description TEXT,
  domain VARCHAR(100),
  framework ENUM('crewai','langchain','autogen','custom'),
  default_llm VARCHAR(100),
  memory_system VARCHAR(100),
  start_from ENUM('blank','template'),
  template VARCHAR(100),
  status ENUM('draft','active','completed','archived','error'),
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  user_id CHAR(36) NOT NULL,
  project_data LONGTEXT NOT NULL           -- ⚠️ PETRI NET JSON COMPLETO
);
```

### 12.2 Conteúdo de `project_data` (JSON)

```json
{
  "nome": "Sistema de Processamento de Emails - Tropical Plásticos V2",
  "version": "2.1",
  "description": "...",
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
      "logica": "// P1 - Sistema Iniciado\nconst output = {...};\nreturn output;"
    },
    {
      "id": "P2",
      "nome": "read_email_task",
      "tokens": 0,
      "coordenadas": {"x": 350, "y": 200},
      "delay": 1000,
      "agentId": "email_reader_agent",
      "input_data": {"max_emails": 5, "timeout_seconds": 30},
      "output_data": {},
      "logica": "// P2 - Read Email (WebSocket)\nconst output = utils.clone(input);\ntry {\n  const ws = new WebSocket('ws://localhost:6308');\n  const result = await new Promise((resolve, reject) => {\n    ws.onopen = () => ws.send(JSON.stringify({\n      type: 'execute_task',\n      data: {task_name: 'read_email', input_data: input}\n    }));\n    ws.onmessage = (e) => {\n      const response = JSON.parse(e.data);\n      if (response.type === 'task_completed') {\n        ws.close();\n        resolve(response.data.result || response.data);\n      }\n    };\n  });\n  Object.assign(output, result);\n  output.status = 'completed';\n} catch (error) {\n  output.status = 'error';\n  output.error = error.message;\n}\nreturn output;"
    }
  ],
  "transicoes": [
    {"id": "T1", "nome": "Iniciar\\nProcessamento", "coordenadas": {"x": 225, "y": 200}}
  ],
  "arcos": [
    {"origem": "P1", "destino": "T1", "peso": 1},
    {"origem": "T1", "destino": "P2", "peso": 1}
  ],
  "agentes": [
    {"id": "email_reader_agent", "nome": "Email Reader Agent", "coordenadas": {"x": 290, "y": 0}}
  ]
}
```

**Campos Críticos:**
- **`lugares[].logica`**: **JAVASCRIPT** executado pelo navegador (GenericFrameworkPageV2.jsx)
- **`lugares[].input_data`**: Parâmetros de configuração (NÃO dados de runtime)
- **`lugares[].output_data`**: Sempre vazio (preenchido em runtime)
- **`lugares[].agentId`**: Referencia agente que executa essa task

---

## 13. O QUE PRECISA SER GERADO POR PROJETO

### 13.1 Exemplo: "Gerenciador de Editais"

A partir da **especificação funcional** do Gerenciador de Editais, o LangNet Interface deve gerar:

#### **1. agents.yaml** (específico do projeto)
```yaml
# /visualtasksexec/gerenciadoredital/agents.yaml
edital_scraper_agent:
  role: "Agente Web Scraper de Editais"
  goal: "Buscar e extrair editais de sites governamentais"
  backstory: |
    Especialista em web scraping com expertise em portais governamentais...
  verbose: true
  allow_delegation: false

edital_analyzer_agent:
  role: "Agente Analisador de Documentos"
  goal: "Analisar PDFs de editais e extrair informações estruturadas"
  backstory: |
    Analista de documentos com 10+ anos processando editais...
  verbose: true
  allow_delegation: false
```

#### **2. tasks.yaml** (específico do projeto)
```yaml
# /visualtasksexec/gerenciadoredital/tasks.yaml
scrape_editais:
  description: |
    Buscar editais em sites governamentais usando web scraping.
    Input: {urls: List[str], keywords: List[str]}
    Process:
      1. Acessar URLs fornecidas
      2. Buscar por keywords
      3. Extrair links de editais
  expected_output: |
    JSON contendo:
    - total_editais: int
    - editais: List[{url, titulo, data_publicacao, orgao}]

analyze_edital:
  description: |
    Analisar PDF do edital e extrair dados estruturados.
    Input: {input_json}  # De scrape_editais
  expected_output: |
    JSON com campos extraídos do edital...
```

#### **3. gerenciadoreditalagents.py** (código Python)
```python
# /visualtasksexec/gerenciadoredital/gerenciadoreditalagents.py
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
import json

class GerenciadorEditaisState(TypedDict, total=False):
    # Config inicial
    urls_busca: List[str]
    keywords: List[str]

    # Task outputs
    editais_scraped_json: str
    editais_analyzed_json: str
    notificacoes_enviadas_json: str

    # Dados estruturados
    editais_data: Dict[str, Any]
    analysis_data: Dict[str, Any]

    # Metadata
    execution_log: List[Dict[str, Any]]
    current_task: Optional[str]
    timestamp: str

def scrape_editais_input_func(state: GerenciadorEditaisState) -> Dict[str, Any]:
    return {
        "urls": state.get("urls_busca", []),
        "keywords": state.get("keywords", [])
    }

def scrape_editais_output_func(state: GerenciadorEditaisState, result: Any) -> GerenciadorEditaisState:
    editais_json = json.dumps(result, ensure_ascii=False)
    return {
        **state,
        "editais_scraped_json": editais_json,
        "editais_data": result,
        "execution_log": state.get("execution_log", []) + [{
            "task": "scrape_editais",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "editais_count": len(result.get("editais", []))
        }],
        "current_task": "scrape_editais",
        "timestamp": datetime.now().isoformat()
    }

# ... mais funções ...

TASK_REGISTRY = {
    "scrape_editais": {
        "input_func": scrape_editais_input_func,
        "output_func": scrape_editais_output_func,
        "requires": [],
        "produces": ["editais_scraped_json", "editais_data"],
        "agent": edital_scraper_agent,
        "tools": [web_scraper_tool],
        "description": "Busca editais em sites governamentais"
    },
    # ... mais tasks ...
}
```

#### **4. Petri Net JSON** (salvo em `projects.project_data`)
```json
{
  "nome": "Gerenciador de Editais V1",
  "version": "1.0",
  "lugares": [
    {
      "id": "P1",
      "nome": "scrape_editais_task",
      "agentId": "edital_scraper_agent",
      "input_data": {"urls": ["..."], "keywords": ["..."]},
      "logica": "const ws = new WebSocket('ws://localhost:6308');\n// ... código gerado ..."
    }
  ],
  "transicoes": [...],
  "arcos": [...],
  "agentes": [...]
}
```

#### **5. gerenciadoredital_adapter.py** (WebSocket adapter)
```python
# /visualtasksexec/gerenciadoredital/websocket_framework_v7/adapters/gerenciadoredital_adapter.py
class GerenciadorEditaisAdapter(BaseAdapter):
    def __init__(self):
        self.project_name = "GerenciadorEditais"
        self.supported_tasks = ["scrape_editais", "analyze_edital", "send_notifications"]

    def convert_v1_to_backend_format(self, task_name: str, input_data: Any):
        # Conversão específica do projeto
        pass
```

#### **6. start_websocket_gerenciadoredital.py** (WebSocket server)
```python
# /visualtasksexec/gerenciadoredital/start_websocket_gerenciadoredital.py
from websocket_framework_v7.websocket_generic_v7 import create_server
from adapters.gerenciadoredital_adapter import GerenciadorEditaisAdapter

adapter = GerenciadorEditaisAdapter()
start_server = create_server(adapter, host="localhost", port=6308)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

---

## 14. FRAMEWORK LANGNET (Biblioteca Compartilhada)

### 14.1 Localização: `/visualtasksexec/framework/`

**Arquivos principais:**
- **`frameworkagents.py`**: Classes base (Agent, Task, Team, Tool, Pipeline, Memory)
- **`frameworkagentsadapter.py`**: Adapters CrewAI (HybridAgentAdapter, LangGraphTaskAdapter)
- **`frameworkmemory.py`**: Sistema de memória LangChain
- **`websocket_generic_v7.py`**: WebSocket server genérico
- **`base_adapter.py`**: Interface BaseAdapter

### 14.2 Como Projetos Usam o Framework

```python
# Em gerenciadoreditalagents.py
from framework.frameworkagentsadapter import (
    HybridAgentAdapter,
    LangGraphTaskAdapter,
    FrameworkAdapterFactory
)

# Obter adapters do framework
adapters = FrameworkAdapterFactory.get_framework_adapters(version="crewai")

# Criar agente usando framework
edital_scraper_agent = adapters["agent"](
    role="Agente Web Scraper de Editais",
    goal="Buscar e extrair editais...",
    # ...
)
```

---

## 15. PRÓXIMOS PASSOS - IMPLEMENTAÇÃO NO LANGNET INTERFACE

### 15.1 O Que Precisa Ser Implementado

**Endpoint de Geração:** `/api/projects/generate-code-from-specification`

**Input:**
- `specification_session_id`: ID da especificação funcional
- `project_name`: Nome do projeto (ex: "Gerenciador de Editais")

**Output (salvo em `projects.project_data`):**
1. **agents.yaml** (texto YAML)
2. **tasks.yaml** (texto YAML)
3. **projectagents.py** (código Python completo)
4. **project_adapter.py** (código Python do adapter)
5. **Petri Net JSON** (com JavaScript em cada lugar.logica)
6. **start_websocket_project.py** (código Python do WebSocket server)

### 15.2 Prompt LLM de Geração

O LLM receberá:
- Especificação funcional completa
- Templates do TropicalSales como referência
- Instruções para gerar TODOS os arquivos

E retornará JSON com:
```json
{
  "agents_yaml": "...",
  "tasks_yaml": "...",
  "project_agents_py": "...",
  "project_adapter_py": "...",
  "petri_net_json": {...},
  "websocket_server_py": "..."
}
```

### 15.3 Fluxo Completo de Geração

```
1. Usuário completa especificação no LangNet Interface
2. Clica "Gerar Código do Projeto"
3. Backend chama LLM com:
   - Especificação completa
   - Templates TropicalSales
   - Instruções de geração
4. LLM retorna JSON com todos os arquivos
5. Backend salva em projects.project_data
6. Frontend mostra: "Projeto gerado! Abra no VisualTasksExec para executar"
7. Usuário abre VisualTasksExec
8. GenericFrameworkPageV2.jsx lê project_data do banco
9. Renderiza Petri Net
10. Usuário clica "Executar"
11. JavaScript executa WebSocket calls
12. Sistema multi-agente roda!
```

---

## 16. CONCLUSÃO

### 16.1 Arquitetura Entendida

**Framework LangNet:**
1. **Dois sistemas separados**: LangNet Interface (gerador) + VisualTasksExec (executor)
2. **Geração via LLM**: Código completo do projeto a partir da especificação
3. **Petri Nets com JavaScript**: Orquestração visual + execução via WebSocket
4. **State Management TypedDict**: Dados acumulativos entre tasks (similar LangGraph)
5. **CrewAI + Framework**: Engine de execução multi-agente
6. **Banco MySQL**: `projects.project_data` armazena Petri Net JSON completo

### 16.2 TropicalSales = Template de Referência

TropicalSales NÃO é parte do LangNet Interface - é um **exemplo de projeto gerado** que serve como **template** para gerar outros projetos.

### 16.3 Próximos Passos Imediatos

1. Criar endpoint `/api/projects/generate-code-from-specification`
2. Criar prompts de geração (usando TropicalSales como template)
3. Implementar parsing da resposta LLM → salvar em `projects.project_data`
4. Testar geração com "Gerenciador de Editais"
5. Validar execução no VisualTasksExec

---

**Relatório atualizado por:** Claude Sonnet 4.5
**Data:** 2025-12-21
**Versão:** 2.0 (COMPLETA)
