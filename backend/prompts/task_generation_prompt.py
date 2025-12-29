"""
Task Generation Prompt
======================

Prompt template for automatic task generation from functional specifications
and generated agents.

INFERENCE CAPABILITIES:
- Automatically identifies process steps from workflow descriptions
- Infers input/output data structures from specification
- Suggests appropriate tools based on task actions
- Determines task dependencies from data flow (requires/produces)
- Assigns tasks to appropriate agents
"""

from typing import Optional, List


def get_task_generation_prompt(
    specification_document: str,
    agents_yaml: str,
    requirements_json: Optional[str] = None,
    detail_level: str = "balanced",
    custom_instructions: Optional[str] = None
) -> str:
    """
    Gera prompt para LLM criar tasks a partir de especificação e agentes.

    Args:
        specification_document: Documento completo de especificação funcional
        agents_yaml: YAML dos agentes já gerados
        requirements_json: JSON dos requisitos (contexto adicional)
        detail_level: Nível de detalhe (concise | balanced | detailed)
        custom_instructions: Instruções adicionais do usuário

    Returns:
        Prompt formatado para envio ao LLM
    """

    detail_instructions = {
        "concise": {
            "process_steps": "3-5 steps",
            "description_style": "Direto e objetivo, sem detalhes extras",
            "expected_output": "Formato mínimo necessário"
        },
        "balanced": {
            "process_steps": "5-8 steps",
            "description_style": "Equilibrado com contexto e instruções claras",
            "expected_output": "Formato detalhado com estrutura completa"
        },
        "detailed": {
            "process_steps": "8-12 steps",
            "description_style": "Muito detalhado com exemplos e edge cases",
            "expected_output": "Formato extremamente detalhado com exemplos"
        }
    }

    detail_config = detail_instructions.get(detail_level, detail_instructions["balanced"])

    prompt = f"""Você é um arquiteto especialista em design de workflows multi-agente com CrewAI.

Sua tarefa é analisar a ESPECIFICAÇÃO FUNCIONAL e os AGENTES GERADOS para **INFERIR AUTOMATICAMENTE** tasks apropriadas que implementam o sistema descrito.

═══════════════════════════════════════════════════════════
📋 SPECIFICATION DOCUMENT
═══════════════════════════════════════════════════════════

{specification_document}

═══════════════════════════════════════════════════════════
🤖 GENERATED AGENTS (YAML)
═══════════════════════════════════════════════════════════

{agents_yaml}

═══════════════════════════════════════════════════════════
📊 REQUIREMENTS (Contexto Adicional)
═══════════════════════════════════════════════════════════

{requirements_json or "N/A - Não fornecido"}

═══════════════════════════════════════════════════════════
🎯 SUAS INSTRUÇÕES DE INFERÊNCIA
═══════════════════════════════════════════════════════════

## 1. ANÁLISE DAS SEÇÕES RELEVANTES

Foque especialmente nestas seções da especificação:

**Seção 3 - Requisitos Funcionais:**
- Cada requisito funcional pode mapear para uma ou mais tasks
- Identifique verbos de ação: buscar, classificar, verificar, gerar, validar

**Seção 4 - Casos de Uso:**
- Fluxos principais e alternativos sugerem sequência de tasks
- Cada passo do fluxo pode ser uma task
- Condicionais e branches sugerem tasks de validação/decisão

**Seção 5 - Regras de Negócio:**
- Regras de validação sugerem tasks de verificação
- Cálculos e transformações sugerem tasks de processamento

**Seção 8 - Fluxos de Processo:**
- Cada caixa/etapa do fluxo é uma task candidata
- Setas/transições indicam dependencies (requires/produces)

## 2. HEURÍSTICAS DE IDENTIFICAÇÃO DE TASKS

### 2.1 Padrão: Verbo de Ação em Infinitivo

Procure por ações descritas na especificação:
- "**Buscar** emails não lidos" → read_email
- "**Classificar** mensagens" → classify_message
- "**Verificar** disponibilidade" → check_stock_availability
- "**Gerar** resposta" → generate_response
- "**Validar** entrada" → validate_input
- "**Processar** pagamento" → process_payment

**Nomenclatura:** Use snake_case com verbo + objeto
- ✅ read_email, classify_message, generate_report
- ❌ email_reader, message_classification, reporting

### 2.2 Padrão: Um Agente, Múltiplas Tasks

Um agente pode executar várias tasks relacionadas:
- **document_analyzer_agent** pode executar:
  - extract_entities
  - identify_relationships
  - validate_requirements

### 2.3 Granularidade de Tasks

**Princípio:** Cada task deve ser uma unidade de trabalho atômica e testável.

✅ **BOM:**
- read_email (APENAS ler)
- classify_message (APENAS classificar)
- check_stock (APENAS verificar estoque)

❌ **RUIM:**
- process_email_pipeline (lê + classifica + verifica + responde - muito acoplado)

## 3. INFERÊNCIA DE DESCRIPTION

A **description** é a instrução completa para o agente executar a task.

### 3.1 Estrutura Padrão da Description

```
[IMPORTANTE: Avisos críticos no topo - OPCIONAL]

[Descrição concisa da tarefa em 1-2 linhas]

[Input data format: Especificação dos dados de entrada]
Os dados estão disponíveis na variável {{placeholder}} contendo:
  * campo1: descrição e tipo
  * campo2: descrição e tipo
  * estrutura_aninhada:
    - subcampo1: descrição
    - subcampo2: descrição

Process steps:
  1. [Se usa {{input_json}}] OBRIGATÓRIO: Parse o JSON fornecido em {{input_json}}
  2. [Se usa tool] Usar nome_da_tool com parâmetro_x = {{placeholder_x}}
  3. Para cada item processado:
     - Ação específica
     - [Se condicional] Se condição X, então ação Y
     - Manter dados originais intactos
  4. [Validações/transformações específicas]
  5. [Sempre] Retornar dados em formato especificado no expected_output

[Instruções finais sobre preservação de dados, se aplicável]
```

### 3.2 Padrões Recorrentes (baseado em TropicalSales)

**Avisos Críticos no Topo:**
```
IMPORTANTE: Processar APENAS os dados REAIS fornecidos em {{input_json}}.
NUNCA criar dados fictícios.
```

**Parse Obrigatório:**
```
1. OBRIGATÓRIO: Parse o JSON fornecido em {{input_json}}
```

**Uso de Tools:**
```
2. Usar email_fetch_tool para buscar emails não lidos, fazendo o parametro max_emails = {{max_emails}}
```
```
3. Usar natural_language_query_stock_tool com nome_produto_pedido
4. Analisar produtos retornados no formato "PRODUTO: [nome], ESTOQUE: [quantidade]"
```

**Preservação de Dados:**
```
- Manter TODOS os dados originais intactos
```
```
- Para outros emails, manter TODOS os dados originais inalterados
```

**Condicionais:**
```
- Se categoria for "pedidos":
  * Usar tool_name com parâmetro
  * Adicionar campos novos
- Para outros casos, manter dados originais
```

**Formatação de Saída:**
```
3. Retornar dados em formato JSON conforme especificado no expected_output
```

### 3.3 Inferência de Input Data

**EXTRAIA** da especificação e de tasks anteriores:

1. **Se é a primeira task da pipeline:**
   - Input pode ser parâmetros de configuração: {{max_emails}}, {{project_id}}
   - Input pode ser "None" se busca dados externamente

2. **Se é task intermediária:**
   - Input é o output acumulado de tasks anteriores
   - Use placeholder {{input_json}} para JSON acumulado
   - Liste todos os campos esperados em "Os dados estão disponíveis na variável {{input_json}} contendo:"

3. **Estrutura de Campos:**
   - Descreva cada campo com tipo e significado
   - Para listas/arrays, descreva estrutura de cada item
   - Use indentação para estruturas aninhadas

**Exemplo:**
```
Os dados classificados estão disponíveis na variável {{input_json}} contendo:
  * timestamp: data e hora da execução (string ISO format)
  * total_emails: quantidade de emails processados (integer)
  * emails: lista de emails, onde cada email contém:
    - email_id: identificador único (string)
    - from: email do remetente (string)
    - subject: assunto do email (string)
    - content: texto completo do email (string)
    - categoria: classificação do email (string: "pedidos" | "duvidas" | ...)
    - nome_produto_pedido: nome do produto identificado, se pedido (string ou null)
```

### 3.4 Inferência de Process Steps

**EXTRAIA** dos casos de uso (seção 4) e fluxos (seção 8):

1. **Identifique cada ação sequencial:**
   - "Primeiro, o sistema busca..." → Step 1
   - "Em seguida, valida..." → Step 2
   - "Por fim, armazena..." → Step 3

2. **Identifique uso de tools:**
   - "Consulta na API externa" → Usar api_tool com parâmetros
   - "Lê arquivo" → Usar file_reader_tool com path
   - "Envia email" → Usar email_send_tool com to, subject, content

3. **Identifique condicionais:**
   - "Se quantidade > limite" → Se {{quantidade}} > {{limite}}:
   - "Para cada item" → Para cada item em {{lista}}:

4. **Detalhamento baseado em detail_level:**
   - {detail_level} → gere {detail_config['process_steps']}

**Exemplo (balanced):**
```
Process steps:
  1. OBRIGATÓRIO: Parse o JSON fornecido em {{input_json}}
  2. Para cada email REAL na lista:
     - Se categoria for "pedidos":
       * Usar natural_language_query_stock_tool com nome_produto_pedido
       * Analisar produtos retornados no formato "PRODUTO: [nome], ESTOQUE: [quantidade]"
       * Selecionar o produto mais similar ao solicitado
       * Adicionar produto_escolhido e quantidade_disponivel ao email
     - Para outros emails, manter TODOS os dados originais inalterados
  3. Retornar JSON completo com novos campos adicionados
```

## 4. INFERÊNCIA DE EXPECTED_OUTPUT

O **expected_output** especifica o formato EXATO do resultado da task.

### 4.1 Padrões de Formato

**JSON (mais comum):**
```
Retornar texto em formato JSON mantendo TODA a estrutura do input e adicionando:
- campo_novo1: descrição e tipo
- campo_novo2: descrição e tipo

Estrutura:
{{
  "campo_existente1": "...",
  "campo_novo1": "...",
  "campo_novo2": ...
}}

CRÍTICO: Manter todos os campos originais inalterados.
```

**Markdown:**
```
Retornar relatório em formato Markdown (sem a marcação ```markdown) contendo:

## Seção 1
- item1: descrição
- item2: descrição

## Seção 2
...
```

**String Simples:**
```
Retornar string contendo:
"RESULTADO: [valor], STATUS: [status]"
```

### 4.2 Padrão de Acumulação (TropicalSales)

**IMPORTANTE:** Cada task **PRESERVA** todos os dados anteriores e **ADICIONA** novos campos.

```
read_email output:
{{
  "timestamp": "...",
  "total_emails": 2,
  "emails": [...]
}}

↓

classify_message output:
{{
  "timestamp": "...",           ← PRESERVADO
  "total_emails": 2,             ← PRESERVADO
  "emails": [
    {{
      ... campos anteriores ...  ← PRESERVADO
      "categoria": "pedidos",    ← ADICIONADO
      "justificativa": "..."     ← ADICIONADO
    }}
  ]
}}
```

**Sempre incluir:**
```
IMPORTANTE: Manter todos os campos originais inalterados.
```
ou
```
CRÍTICO: Preservar TODA a estrutura de entrada.
```

## 5. INFERÊNCIA DE AGENT ASSIGNMENT

Cada task deve ser atribuída a exatamente UM agente.

### 5.1 Critérios de Atribuição

1. **Responsabilidade do Agente:**
   - Se agent role = "Buscador de Emails" → task = read_email
   - Se agent role = "Classificador" → task = classify_message

2. **Tools do Agente:**
   - Se task usa email_fetch_tool E agent tem essa tool → match
   - Se task usa database_query_tool E agent tem essa tool → match

3. **Goal do Agente:**
   - Se task goal alinha com agent goal → match

**REGRA:** O agent name deve existir no agents_yaml fornecido.

### 5.2 Exemplo de Atribuição

```yaml
# agents_yaml contém:
email_reader_agent:
  role: "Agente Buscador de Emails Não Lidos"
  ...

# Task deve ter:
agent: email_reader_agent  ✅
# NÃO:
agent: email_reader  ❌ (nome não existe)
agent: reader_agent  ❌ (nome não existe)
```

## 6. INFERÊNCIA DE TOOLS

As **tools** da task devem ser inferidas de:

### 6.1 Process Steps

Se a description menciona explicitamente uma tool:
```
2. Usar email_fetch_tool para buscar emails...
```
→ tools: ["email_fetch_tool"]

### 6.2 Agent Suggestions

Se o agente atribuído tem suggested_tools:
```yaml
# agent:
suggested_tools: ["email_fetch_tool", "json_parser_tool"]

# task pode usar subconjunto:
tools: ["email_fetch_tool"]
```

### 6.3 Palavras-Chave na Description

Mesmo mapeamento de palavras-chave do agent_generation_prompt:
- "pesquisar na web" → serper_search_tool, tavily_search_tool
- "consultar banco" → database_query_tool
- "enviar email" → email_send_tool

## 7. INFERÊNCIA DE REQUIRES/PRODUCES

**REQUIRES:** Lista de campos do state que a task necessita como input.

**PRODUCES:** Lista de campos que a task adiciona ao state.

### 7.1 Inferência de REQUIRES

**EXTRAIA** da section "Input data format" da description:

```
Os dados estão disponíveis em {{input_json}} contendo:
  * campo1: ...
  * campo2: ...
  * campo3: ...
```
→ requires: ["campo1", "campo2", "campo3"]

**Se input é None:**
→ requires: []

**Se usa parâmetros de configuração:**
```
Input: {{max_emails}}, {{project_id}}
```
→ requires: ["max_emails", "project_id"]

### 7.2 Inferência de PRODUCES

**EXTRAIA** do "expected_output":

```
Retornar JSON adicionando:
- novo_campo1: ...
- novo_campo2: ...
```
→ produces: ["novo_campo1", "novo_campo2"]

**IMPORTANTE:** NÃO inclua campos que já existem (preservados), apenas os NOVOS.

### 7.3 Exemplo Completo

```yaml
# Task: classify_message
requires: ["emails"]              # Precisa da lista de emails (de read_email)
produces: ["categoria", "justificativa"]  # Adiciona esses campos a cada email

# Task: check_stock_availability
requires: ["emails", "categoria", "nome_produto_pedido"]  # Precisa dos dados classificados
produces: ["produto_escolhido", "quantidade_disponivel"]  # Adiciona info de estoque
```

## 8. INFERÊNCIA DE DEPENDENCIES

**DEPENDENCIES:** Lista de tasks que devem executar ANTES desta task.

### 8.1 Critérios de Dependência

1. **Data Flow (PRINCIPAL):**
   - Se TaskB requires campo que TaskA produces → TaskB depends on TaskA

2. **Ordem Lógica (Especificação):**
   - "Primeiro busca, depois classifica" → classify depends on read

3. **Fluxos de Processo (Seção 8):**
   - Setas no diagrama indicam ordem

### 8.2 Exemplo de Dependências

```python
# Pipeline TropicalSales:
read_email:
  requires: []
  produces: ["emails"]
  dependencies: []  # Primeira task

classify_message:
  requires: ["emails"]
  produces: ["categoria"]
  dependencies: ["read_email"]  # Precisa de emails

check_stock_availability:
  requires: ["emails", "categoria"]
  produces: ["produto_escolhido"]
  dependencies: ["classify_message"]  # Precisa de categoria

generate_response:
  requires: ["emails", "categoria", "produto_escolhido"]
  produces: ["response_sent"]
  dependencies: ["check_stock_availability"]  # Precisa de produto
```

## 9. RATIONALE (Justificativa)

Para cada task, forneça uma breve justificativa (2-3 frases) explicando:
- Por que esta task é necessária
- Qual transformação de dados ela realiza
- Como ela contribui para o objetivo final

Exemplo:
"Esta task é necessária para validar os dados de entrada antes do processamento principal, garantindo integridade. Ela transforma dados brutos em estruturas validadas, aplicando regras de negócio definidas na seção 5. Contribui evitando erros downstream e garantindo qualidade dos dados."

═══════════════════════════════════════════════════════════
⚙️ CONFIGURAÇÃO
═══════════════════════════════════════════════════════════

- **Detail Level:** {detail_level}
- **Process Steps:** {detail_config['process_steps']}
- **Description Style:** {detail_config['description_style']}
- **Expected Output:** {detail_config['expected_output']}

═══════════════════════════════════════════════════════════
📝 INSTRUÇÕES ADICIONAIS DO USUÁRIO
═══════════════════════════════════════════════════════════

{custom_instructions or "Nenhuma instrução adicional fornecida."}

═══════════════════════════════════════════════════════════
📤 FORMATO DE OUTPUT
═══════════════════════════════════════════════════════════

Retorne um **JSON válido** contendo um array de tasks.

**IMPORTANTE:** Retorne APENAS o JSON, sem texto adicional antes ou depois.

Estrutura:

```json
[
  {{
    "name": "task_name_snake_case",
    "description": "IMPORTANTE: Avisos críticos...\\n\\nDescrição da tarefa...\\n\\nInput data format: {{input_json}} contendo:\\n  * campo1: ...\\n\\nProcess steps:\\n  1. Step\\n  2. Step\\n  ...",
    "expected_output": "Retornar JSON/Markdown contendo:\\n- campo1: ...\\n- campo2: ...\\n\\nCRÍTICO: Instruções finais",
    "agent": "agent_name_from_yaml",
    "tools": ["tool1", "tool2"],
    "requires": ["input_field1", "input_field2"],
    "produces": ["output_field1", "output_field2"],
    "dependencies": ["previous_task_name"],
    "rationale": "Justificativa de 2-3 frases."
  }},
  {{
    "name": "another_task",
    ...
  }}
]
```

**Regras do JSON:**
1. Use aspas duplas (") para strings
2. Use snake_case para nomes de tasks, agents e tools
3. Use \\n para quebras de linha na description e expected_output
4. Agent name deve existir no agents_yaml fornecido
5. Tools devem ser tools válidas do CrewAI
6. Requires/produces devem ser arrays de strings (nomes de campos)
7. Dependencies devem referenciar tasks existentes no mesmo array

═══════════════════════════════════════════════════════════
✅ EXEMPLO DE OUTPUT ESPERADO
═══════════════════════════════════════════════════════════

```json
[
  {{
    "name": "extract_functional_requirements",
    "description": "IMPORTANTE: Processar APENAS o documento real fornecido. NUNCA criar requisitos fictícios.\\n\\nExtrair requisitos funcionais do documento de especificação e estruturá-los em formato JSON padronizado.\\n\\nInput data format: {{specification_document}}\\nDocumento completo contendo todas as 14 seções da especificação funcional.\\n\\nProcess steps:\\n  1. OBRIGATÓRIO: Ler e parsear o documento fornecido em {{specification_document}}\\n  2. Identificar a seção 3 (Requisitos Funcionais)\\n  3. Para cada requisito listado:\\n     - Extrair ID do requisito (ex: RF-001)\\n     - Extrair descrição completa\\n     - Identificar prioridade (essencial, importante, desejável)\\n     - Identificar atores envolvidos\\n  4. Estruturar em formato JSON conforme expected_output\\n  5. Validar que todos os requisitos foram capturados",
    "expected_output": "Retornar texto em formato JSON contendo:\\n{{\\n  \\"total_requirements\\": número total de requisitos extraídos,\\n  \\"requirements\\": [\\n    {{\\n      \\"id\\": \\"RF-001\\",\\n      \\"description\\": \\"texto completo do requisito\\",\\n      \\"priority\\": \\"essencial | importante | desejável\\",\\n      \\"actors\\": [\\"ator1\\", \\"ator2\\"]\\n    }}\\n  ]\\n}}\\n\\nCRÍTICO: Manter fidelidade completa ao documento original.",
    "agent": "document_analyzer_agent",
    "tools": ["document_reader_tool", "json_parser_tool"],
    "requires": ["specification_document"],
    "produces": ["total_requirements", "requirements"],
    "dependencies": [],
    "rationale": "Esta task é fundamental para estruturar requisitos funcionais de forma programática. Ela transforma texto livre em dados estruturados, permitindo processamento automatizado downstream. Serve como base para tasks que dependem de requisitos bem definidos."
  }},
  {{
    "name": "research_applicable_standards",
    "description": "Pesquisar standards técnicos e de compliance aplicáveis ao domínio do sistema.\\n\\nInput data format: {{requirements}}\\nLista de requisitos funcionais extraídos, contendo:\\n  * requirements: array de objetos com id, description, priority\\n\\nProcess steps:\\n  1. OBRIGATÓRIO: Parse o JSON fornecido em {{requirements}}\\n  2. Para cada requisito, identificar domínios técnicos mencionados (ex: autenticação, pagamentos, dados pessoais)\\n  3. Para cada domínio identificado:\\n     - Usar serper_search_tool para buscar \\"[domínio] technical standards\\"\\n     - Usar tavily_search_tool para buscar \\"[domínio] compliance requirements\\"\\n  4. Filtrar resultados relevantes (ISO, IEEE, OWASP, GDPR, LGPD, PCI-DSS)\\n  5. Estruturar findings em formato JSON",
    "expected_output": "Retornar JSON contendo:\\n{{\\n  \\"domains_researched\\": [\\"autenticação\\", \\"pagamentos\\"],\\n  \\"standards\\": [\\n    {{\\n      \\"name\\": \\"ISO 27001\\",\\n      \\"domain\\": \\"segurança\\",\\n      \\"description\\": \\"...\\",\\n      \\"source_url\\": \\"https://...\\"\\n    }}\\n  ],\\n  \\"compliance\\": [...]\\n}}",
    "agent": "web_researcher_agent",
    "tools": ["serper_search_tool", "tavily_search_tool"],
    "requires": ["requirements"],
    "produces": ["domains_researched", "standards", "compliance"],
    "dependencies": ["extract_functional_requirements"],
    "rationale": "Necessária para enriquecer a especificação com conhecimento externo de standards e compliance. Garante que o sistema atenda requisitos regulatórios e siga best practices estabelecidas. Complementa requisitos funcionais com contexto da indústria."
  }}
]
```

═══════════════════════════════════════════════════════════
🚀 AGORA É SUA VEZ
═══════════════════════════════════════════════════════════

Analise a ESPECIFICAÇÃO FUNCIONAL e os AGENTES GERADOS para criar tasks que implementam o sistema.

**LEMBRE-SE:**
- INFIRA automaticamente description, process steps, input/output data, tools
- CADA task deve ter UM agente válido do agents_yaml
- DETERMINE dependencies corretas baseado em data flow (requires/produces)
- PRESERVE dados acumulados entre tasks (padrão TropicalSales)
- Retorne APENAS o JSON válido, sem texto adicional

Retorne o JSON agora:"""

    return prompt


def infer_task_dependencies(tasks: List[dict]) -> List[dict]:
    """
    Infere automaticamente dependencies entre tasks baseado em requires/produces.

    Args:
        tasks: Lista de tasks com requires e produces definidos

    Returns:
        Lista de tasks com dependencies atualizadas
    """
    for task in tasks:
        dependencies = set()
        task_requires = set(task.get("requires", []))

        # Para cada outra task, verifica se ela produz algo que esta task requer
        for other_task in tasks:
            if other_task["name"] == task["name"]:
                continue  # Não pode depender de si mesma

            other_produces = set(other_task.get("produces", []))
            if task_requires & other_produces:  # Interseção
                dependencies.add(other_task["name"])

        task["dependencies"] = sorted(list(dependencies))

    return tasks
