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

FORMATO DE SAÍDA:

Gere documento Markdown seguindo EXATAMENTE esta estrutura:

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

### Task 1: [task_name]

**ID:** T-001
**Agente:** [agent_name]
**Ordem:** 1 (primeira task)
**Tipo:** Inicial (sem dependências)

**Input Function:**
```python
def [task]_input_func(state: ProjectState) -> Dict[str, Any]:
    return {{"campo": state.get("campo", valor_padrao)}}
```

**Input Schema:**
- **campo** (tipo): Descrição do campo

**Process Steps:**
1. [Passo 1 detalhado]
2. [Passo 2 detalhado]
3. [Passo 3 detalhado]

**Output Function:**
```python
def [task]_output_func(state: ProjectState, result: Any) -> ProjectState:
    return {{
        **state,
        "[campo]_output": result.get("output"),
        "execution_log": state.get("execution_log", []) + [{{
            "task": "[task_name]",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }}],
        "timestamp": datetime.now().isoformat()
    }}
```

**Output Schema:**
```json
{{
  "campo1": "valor",
  "campo2": 123,
  "timestamp": "2026-01-08T10:00:00"
}}
```

**Tools Necessárias:**
- [tool_name]

**Campos do State Produzidos:**
- [campo1]
- [campo2]

**Campos do State Requeridos:**
- [campo_req1]

**Dependências:**
- Nenhuma (task inicial)

---

### Task 2: [task_name]

[Repetir estrutura para todas as tasks...]

---

## 4. Grafo de Dependências

```
T-001 ([task_name])
    ↓ produz: [campo1], [campo2]
T-002 ([task_name])
    ↓ produz: [campo3]
T-003 ([task_name])
    ↓ produz: [campo4]
```

**Dependências Explícitas:**
- T-002 requires: ["campo1"] (de T-001)
- T-003 requires: ["campo3"] (de T-002)

## 5. TASK_REGISTRY (Estrutura)

```python
TASK_REGISTRY = {{
    "[task1]": {{
        "input_func": [task1]_input_func,
        "output_func": [task1]_output_func,
        "requires": [],
        "produces": ["campo1", "campo2"],
        "agent": [agent1],
        "tools": [[tool1]],
        "description": "Descrição da task"
    }},
    "[task2]": {{
        "input_func": [task2]_input_func,
        "output_func": [task2]_output_func,
        "requires": ["campo1"],
        "produces": ["campo3"],
        "agent": [agent2],
        "tools": [],
        "description": "Descrição da task"
    }}
}}
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

REGRAS CRÍTICAS:

1. **State Acumulativo:** Cada output_func DEVE preservar state anterior com `{{**state, ...}}`
2. **Input Extração:** Input_func APENAS extrai campos do state, não transforma
3. **Dependências:** Campo em `requires` DEVE estar em `produces` de task anterior
4. **Tools:** Listar apenas tools CrewAI válidas mencionadas no tasks.yaml
5. **Tipos Python:** Especificar tipos corretos (str, int, List[Dict], Dict[str, Any])
6. **JSON Schemas:** Exemplos REALISTAS baseados no domínio do projeto
7. **Process Steps:** 3-7 passos descritivos e acionáveis
8. **Código Python:** Sintaxe VÁLIDA e executável nas functions
9. **Imports:** Assumir que datetime, json, Dict, Any, List já estão importados
10. **Nomenclatura:** snake_case para funções e campos

ANÁLISE REQUERIDA:

1. Analise o tasks.yaml para entender:
   - O que cada task faz (description)
   - Qual é o output esperado (expected_output)
   - Quais são os process steps

2. Infira as dependências:
   - Primeira task: requires = []
   - Tasks subsequentes: identifique quais campos do state ela precisa
   - Ex: Se task menciona "JSON da task anterior", adicione o campo ao requires

3. Defina campos produzidos:
   - Cada task produz pelo menos 1 campo principal (ex: emails_json)
   - Pode produzir campo parsed (ex: emails_data = parsed JSON)
   - Sempre adiciona entrada ao execution_log

4. Identifique tools:
   - Extraia do tasks.yaml (description ou process steps)
   - Ex: "usando email_fetch_tool" → tools: [email_fetch_tool]

5. Determine ordem de execução:
   - Construa grafo de dependências
   - Ordene topologicamente
   - Identifique possibilidades de paralelismo

FORMATO DAS FUNCTIONS:

**Input Function Pattern:**
```python
def [task]_input_func(state: ProjectState) -> Dict[str, Any]:
    \"\"\"Extrai [campos] do state\"\"\"
    return {{
        "campo1": state.get("campo1", default_value),
        "campo2": state.get("campo2", default_value)
    }}
```

**Output Function Pattern:**
```python
def [task]_output_func(state: ProjectState, result: Any) -> ProjectState:
    \"\"\"Atualiza state com resultado de [task]\"\"\"
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result, ensure_ascii=False))
        output_data = result
    else:
        output_json = str(result)
        try:
            output_data = json.loads(output_json)
        except:
            output_data = {{"error": "Failed to parse"}}

    execution_log = state.get("execution_log", [])
    execution_log.append({{
        "task": "[task_name]",
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    }})

    return {{
        **state,
        "[task]_json": output_json,
        "[task]_data": output_data,
        "execution_log": execution_log,
        "current_task": "[task_name]",
        "timestamp": datetime.now().isoformat()
    }}
```

IMPORTANTE:
- Analise o tasks.yaml cuidadosamente para inferir dependências corretas
- Use nomes de campos consistentes (ex: [task]_json, [task]_data)
- Mantenha o pattern de preservação de state: `{{**state, novos_campos}}`

{f'INSTRUÇÕES CUSTOMIZADAS:\\n{custom_instructions}' if custom_instructions else ''}

OUTPUT: Retorne APENAS o documento Markdown. Sem explicações externas.

Gere agora:
"""
