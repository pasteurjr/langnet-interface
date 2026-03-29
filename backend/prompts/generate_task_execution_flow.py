"""
Prompt para Gerar Documento de Fluxo de Execução de Tarefas
Gera task_execution_flow.md a partir de specification + agent_task_spec + tasks.yaml
"""

def get_task_execution_flow_prompt(
    specification_document: str,
    agent_task_spec_document: str,
    tasks_yaml: str,
    additional_docs_text: str = "",
    custom_instructions: str = ""
) -> str:
    """
    Gera prompt para criar documento detalhado de fluxo de execução

    Args:
        specification_document: Documento de especificação funcional (contexto de negócio)
        agent_task_spec_document: Documento MD de especificação de agentes/tarefas
        tasks_yaml: YAML de tasks gerado (sequência de execução)
        additional_docs_text: Documentos externos opcionais
        custom_instructions: Instruções adicionais do usuário

    Returns:
        Prompt formatado para o LLM
    """
    return f"""Você é especialista em design de workflows e state management (LangGraph).

TAREFA: Gerar documento MARKDOWN detalhado do fluxo de execução de tarefas.

INPUTS DISPONÍVEIS:

1. ESPECIFICAÇÃO FUNCIONAL (Contexto de Negócio):
{specification_document[:100000]}

2. ESPECIFICAÇÃO DE AGENTES E TAREFAS (Relacionamento):
{agent_task_spec_document[:80000]}

3. TASKS.YAML (Sequência de Execução):
{tasks_yaml}

{additional_docs_text if additional_docs_text else ""}

═══════════════════════════════════════════════════════════════
REGRAS CRÍTICAS — LEIA ANTES DE GERAR QUALQUER COISA
═══════════════════════════════════════════════════════════════

REGRA 1 — IDs SEQUENCIAIS ÚNICOS:
- Use APENAS IDs sequenciais: T-001, T-002, T-003, ...
- NUNCA use IDs por categoria (T-ANA-001, T-GER-001, etc.)
- O mesmo ID T-001 deve aparecer na Seção 3, no Grafo (Seção 4) e no TASK_REGISTRY (Seção 5)
- Um ID não pode ser reutilizado em nenhuma hipótese

REGRA 2 — CADA TASK APARECE EXATAMENTE UMA VEZ NO GRAFO:
- Em LangGraph, um node só pode existir em um único lugar do grafo
- Se uma task é usada em múltiplos fluxos, ela deve aparecer como node único
  com conditional edges ou como tasks SEPARADAS com nomes distintos
- NUNCA escreva "T-005 [reutilizado]" — duplique a task com nome diferente
  (ex: classify_inconsistency_severity_proposal) se precisar do mesmo comportamento em outro fluxo
- O grafo deve ser um DAG válido onde cada node aparece uma única vez

REGRA 3 — STATE COMPLETO (incluindo campos de entrada externa):
- A seção 2.1 deve listar TODOS os campos que o state inicial precisa ter
- Isso inclui campos que NÃO vêm de tasks anteriores, mas de:
  * Input do usuário (ex: edital_file, user_question, edit_requests)
  * Configuração externa (ex: portal_config, classification_rules, template_type)
  * Dados fornecidos em runtime (ex: proposal_file, bid_events, admin_context)
- Se uma task requires um campo que nenhuma outra task produz, esse campo DEVE
  estar na seção 2.1 como campo de configuração/entrada inicial
- NUNCA deixe um campo em "requires" que não está nem na seção 2.1 nem no "produces" de outra task

REGRA 4 — GERAR CÓDIGO LANGGRAPH REAL (Seção 5):
- Após o TASK_REGISTRY, gere o código Python completo de construção do grafo:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any, List, Optional

# Definição do State
class ProjectState(TypedDict):
    # Campos de configuração inicial
    campo1: str
    campo2: Dict[str, Any]
    # Campos de output das tasks
    task1_json: str
    task1_data: Dict[str, Any]
    # Metadados
    execution_log: List[Dict[str, Any]]
    current_task: str
    timestamp: str

# Instanciação dos agentes
agent1 = create_agent("agent1_name")
agent2 = create_agent("agent2_name")

# Construção do grafo
def build_workflow() -> StateGraph:
    workflow = StateGraph(ProjectState)

    # Adicionar nodes
    workflow.add_node("task1_name", lambda state: run_task("task1_name", state))
    workflow.add_node("task2_name", lambda state: run_task("task2_name", state))

    # Definir entry point
    workflow.set_entry_point("task1_name")

    # Adicionar edges lineares
    workflow.add_edge("task1_name", "task2_name")

    # Edges condicionais (quando há ramificações)
    def route_after_task3(state: ProjectState) -> str:
        if state.get("condicao"):
            return "task4a_name"
        return "task4b_name"

    workflow.add_conditional_edges(
        "task3_name",
        route_after_task3,
        {{"task4a_name": "task4a_name", "task4b_name": "task4b_name"}}
    )

    # Tasks paralelas que convergem
    workflow.add_edge("task4a_name", END)
    workflow.add_edge("task4b_name", END)

    return workflow.compile()

# Compilar
graph = build_workflow()
```

REGRA 5 — TASK_REGISTRY com strings para agentes (não objetos):
- Use strings para identificar agentes: `"agent": "agent_name"`
- NUNCA use referências a objetos Python não definidos: `"agent": AG-01` ← PROIBIDO
- Exemplo correto:
```python
TASK_REGISTRY = {{
    "task_name": {{
        "input_func": task_name_input_func,
        "output_func": task_name_output_func,
        "requires": ["campo_anterior"],
        "produces": ["campo_produzido_json", "campo_produzido_data"],
        "agent": "nome_do_agente_string",
        "tools": ["tool1", "tool2"],
        "description": "O que esta task faz"
    }}
}}
```

═══════════════════════════════════════════════════════════════
FORMATO DE SAÍDA — ESTRUTURA DO DOCUMENTO
═══════════════════════════════════════════════════════════════

# Fluxo de Execução de Tarefas - [Nome do Projeto]

## 1. Visão Geral

- **Total de Tasks:** X
- **Total de Agentes:** Y
- **Tipo de Fluxo:** Linear / Pipeline / Paralelo / Misto
- **Modelo de State:** Acumulativo (LangGraph-style)

## 2. Definição do State (TypedDict)

### 2.1 Campos de Configuração e Entrada Inicial
Inclui TODOS os campos que o state inicial precisa — configurações, inputs do usuário e dados externos.

| Campo | Tipo | Descrição | Obrigatório | Valor Padrão |
|-------|------|-----------|-------------|--------------|
| campo_config | Dict[str, Any] | Configuração do sistema | Sim | {{}} |
| arquivo_input | str | Arquivo fornecido pelo usuário | Sim | "" |
| campo_opcional | str | Campo opcional | Não | "" |

### 2.2 Campos de Output das Tasks
Apenas campos PRODUZIDOS por tasks durante a execução.

| Campo | Tipo | Produzido Por (ID) | Consumido Por (IDs) |
|-------|------|-------------------|---------------------|
| task1_json | str | T-001 | T-002, T-003 |
| task1_data | Dict[str, Any] | T-001 | T-002, T-003 |

### 2.3 Campos de Metadados
| Campo | Tipo | Descrição |
|-------|------|-----------|
| execution_log | List[Dict] | Log de execução |
| current_task | str | Task em execução |
| timestamp | str | Timestamp ISO |

## 3. Sequência de Execução

### Task 1: [task_name]

**ID:** T-001
**Agente:** [nome_do_agente] (string, não objeto)
**Ordem:** 1 (primeira task)
**Tipo:** Inicial / Processamento / Final

**Input Function:**
```python
def task_name_input_func(state: ProjectState) -> Dict[str, Any]:
    \"\"\"Extrai campos necessários do state\"\"\"
    return {{
        "campo1": state.get("campo1", ""),
        "campo2": state.get("campo2", {{}})
    }}
```

**Input Schema:**
- **campo1** (str): Descrição — vem de: [seção 2.1 config / T-00X output]
- **campo2** (Dict): Descrição — vem de: [seção 2.1 config / T-00X output]

**Process Steps:**
1. [Passo 1 detalhado]
2. [Passo 2 detalhado]
3. [Passo 3 detalhado]

**Output Function:**
```python
def task_name_output_func(state: ProjectState, result: Any) -> ProjectState:
    \"\"\"Atualiza state com resultado de task_name\"\"\"
    if isinstance(result, dict):
        output_json = json.dumps(result, ensure_ascii=False)
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {{"error": "Failed to parse output"}}

    execution_log = state.get("execution_log", [])
    execution_log.append({{
        "task": "task_name",
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    }})

    return {{
        **state,
        "task_name_json": output_json,
        "task_name_data": output_data,
        "execution_log": execution_log,
        "current_task": "task_name",
        "timestamp": datetime.now().isoformat()
    }}
```

**Output Schema:**
```json
{{
  "campo_resultado1": "valor_exemplo_real",
  "campo_resultado2": 123
}}
```

**Tools Necessárias:**
- [tool_name]

**Campos do State Produzidos:**
- task_name_json (str)
- task_name_data (Dict)

**Campos do State Requeridos:**
- campo1 → origem: [config inicial seção 2.1 / T-00X]
- campo2 → origem: [config inicial seção 2.1 / T-00X]

**Dependências:**
- Nenhuma (task inicial) / T-00X (task_name_anterior)

---

[Repetir estrutura Task N para TODAS as tasks]

---

## 4. Grafo de Dependências

```
[Fluxo Principal]
T-001 (task_name_1)
    ↓ produz: task1_data
T-002 (task_name_2)
    ↓ produz: task2_data
T-003 (task_name_3)
    ↓ produz: task3_data

[Fluxo Paralelo A — independente]
T-010 (task_name_10)
    ↓ produz: task10_data
T-011 (task_name_11)
    ↓ produz: task11_data
```

ATENÇÃO: Cada task (T-00X) aparece exatamente uma vez neste grafo.
Se o mesmo comportamento é necessário em dois fluxos, as tasks têm nomes distintos.

**Dependências Explícitas:**
- T-002 requires: ["task1_data"] — produzido por T-001
- T-003 requires: ["task2_data"] — produzido por T-002

## 5. Código Python de Implementação

### 5.1 TASK_REGISTRY

```python
TASK_REGISTRY = {{
    "task_name_1": {{
        "input_func": task_name_1_input_func,
        "output_func": task_name_1_output_func,
        "requires": [],
        "produces": ["task_name_1_json", "task_name_1_data"],
        "agent": "nome_agente_string",
        "tools": ["tool1", "tool2"],
        "description": "Descrição objetiva da task"
    }},
    "task_name_2": {{
        "input_func": task_name_2_input_func,
        "output_func": task_name_2_output_func,
        "requires": ["task_name_1_data"],
        "produces": ["task_name_2_json", "task_name_2_data"],
        "agent": "outro_agente_string",
        "tools": [],
        "description": "Descrição objetiva da task"
    }}
}}
```

### 5.2 Grafo LangGraph (StateGraph)

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any, List, Optional
import json
from datetime import datetime

# State TypedDict
class ProjectState(TypedDict):
    # === CAMPOS DE CONFIGURAÇÃO INICIAL (seção 2.1) ===
    campo_config: Dict[str, Any]
    arquivo_input: str
    # === CAMPOS DE OUTPUT DAS TASKS (seção 2.2) ===
    task_name_1_json: str
    task_name_1_data: Dict[str, Any]
    task_name_2_json: str
    task_name_2_data: Dict[str, Any]
    # === METADADOS ===
    execution_log: List[Dict[str, Any]]
    current_task: str
    timestamp: str

# Função auxiliar de execução de task via TASK_REGISTRY
def run_task(task_name: str, state: ProjectState) -> ProjectState:
    config = TASK_REGISTRY[task_name]
    task_input = config["input_func"](state)
    # Aqui o agente executa com CrewAI
    result = config["agent_instance"].execute(task_input)
    return config["output_func"](state, result)

# Construção do grafo
def build_workflow() -> StateGraph:
    workflow = StateGraph(ProjectState)

    # Adicionar nodes (um por task)
    workflow.add_node("task_name_1", lambda s: run_task("task_name_1", s))
    workflow.add_node("task_name_2", lambda s: run_task("task_name_2", s))
    # ... todos os nodes

    # Entry point
    workflow.set_entry_point("task_name_1")

    # Edges lineares
    workflow.add_edge("task_name_1", "task_name_2")
    # ... demais edges

    # Edges condicionais (se houver ramificações)
    # def route_after_task_X(state: ProjectState) -> str:
    #     if state.get("condicao"):
    #         return "task_branch_a"
    #     return "task_branch_b"
    # workflow.add_conditional_edges("task_name_X", route_after_task_X, {{...}})

    # Finalização
    workflow.add_edge("task_name_last", END)

    return workflow.compile()

# Compilar
graph = build_workflow()
```

## 6. Validações

### 6.1 Completude
- [ ] Todas as tasks têm input/output definidos
- [ ] Todas as dependências são satisfeitas (sem campos "mágicos")
- [ ] Não há ciclos no grafo
- [ ] Cada task aparece exatamente uma vez no grafo

### 6.2 Consistência do State
- [ ] Todo campo em "requires" está em seção 2.1 OU em "produces" de task anterior
- [ ] Nenhum campo de entrada externa está ausente da seção 2.1
- [ ] Tipos de dados são compatíveis entre tasks

### 6.3 Implementação
- [ ] TASK_REGISTRY usa strings para agentes (não objetos AG-XX)
- [ ] IDs sequenciais (T-001, T-002...) usados consistentemente em todas as seções
- [ ] Código StateGraph tem add_node para cada task da seção 3
- [ ] Código StateGraph tem add_edge/add_conditional_edges para todas as dependências

## 7. Métricas

- **Tempo estimado de execução:** [Xm por fluxo]
- **Complexidade do grafo:** DAG / Linear / Árvore
- **Paralelismo possível:** [Sim/Não — quais fluxos podem rodar em paralelo]

═══════════════════════════════════════════════════════════════
REGRAS ADICIONAIS DE QUALIDADE
═══════════════════════════════════════════════════════════════

1. **State Acumulativo:** output_func SEMPRE usa `{{**state, novos_campos}}`
2. **Input apenas extrai:** input_func NUNCA transforma dados, só lê do state
3. **Tools válidas:** Apenas tools mencionadas no tasks.yaml ou agent_task_spec
4. **JSON Schemas realistas:** Exemplos baseados no domínio real do projeto
5. **Process Steps:** 3-7 passos descritivos e acionáveis
6. **Código Python válido:** Sintaxe correta, executável, sem objetos indefinidos
7. **Imports assumidos:** datetime, json, Dict, Any, List, Optional já importados
8. **snake_case:** Para todas as funções, campos e variáveis

ANÁLISE REQUERIDA ANTES DE GERAR:

1. Liste todas as tasks do tasks.yaml → esses são seus nodes
2. Para cada task, identifique: o que ela consome e o que produz
3. Mapeie cada campo consumido: vem de task anterior ou é entrada inicial?
4. Construa o grafo: ordene topologicamente, identifique paralelismos
5. Preencha seção 2.1 com TODOS os campos de entrada que não vêm de tasks
6. Gere o código StateGraph com todos os nodes e edges corretos

{f'INSTRUÇÕES CUSTOMIZADAS:\\n{custom_instructions}' if custom_instructions else ''}

OUTPUT: Retorne APENAS o documento Markdown. Sem explicações externas.

Gere agora:
"""
