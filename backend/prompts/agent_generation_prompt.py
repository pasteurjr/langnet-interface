"""
Agent Generation Prompt
=======================

Prompt template for automatic agent generation from functional specifications.

INFERENCE CAPABILITIES:
- Automatically identifies roles from specification text patterns
- Infers backstories based on described responsibilities
- Suggests appropriate CrewAI tools based on keywords and actions
- Determines delegation targets from interaction flows
"""

from typing import Optional, List


# Mapeamento de palavras-chave → tools sugeridas
KEYWORD_TO_TOOLS_MAP = {
    # Busca e Pesquisa
    "pesquisar": ["serper_search_tool", "tavily_search_tool"],
    "buscar na web": ["serper_search_tool", "tavily_search_tool"],
    "buscar informações": ["serper_search_tool", "tavily_search_tool"],
    "consultar internet": ["serper_search_tool", "web_scraper_tool"],
    "pesquisa online": ["tavily_search_tool", "serper_search_tool"],

    # Documentos
    "ler documento": ["document_reader_tool", "pdf_reader_tool"],
    "processar pdf": ["pdf_reader_tool"],
    "analisar documento": ["document_reader_tool"],
    "extrair de documento": ["document_reader_tool", "json_parser_tool"],
    "parsear json": ["json_parser_tool"],
    "ler arquivo": ["document_reader_tool", "file_reader_tool"],

    # Banco de Dados
    "consultar banco": ["database_query_tool"],
    "verificar estoque": ["database_query_tool"],
    "buscar no banco": ["database_query_tool"],
    "query database": ["database_query_tool"],
    "validar dados": ["database_query_tool", "json_parser_tool"],

    # Geração e Escrita
    "gerar código": ["code_generator_tool"],
    "criar arquivo": ["file_writer_tool", "yaml_writer_tool"],
    "escrever yaml": ["yaml_writer_tool"],
    "gerar relatório": ["file_writer_tool"],
    "criar documento": ["file_writer_tool"],

    # Comunicação
    "enviar email": ["email_send_tool"],
    "notificar": ["slack_notification_tool", "email_send_tool"],
    "alertar": ["slack_notification_tool"],
    "enviar mensagem": ["email_send_tool", "slack_notification_tool"],

    # Código
    "analisar código": ["code_docs_search_tool"],
    "documentar código": ["code_docs_search_tool", "file_writer_tool"],
    "revisar código": ["code_docs_search_tool"],
}


def get_agent_generation_prompt(
    specification_document: str,
    requirements_json: Optional[str] = None,
    detail_level: str = "balanced",
    max_agents: int = 10,
    custom_instructions: Optional[str] = None
) -> str:
    """
    Gera prompt para LLM criar agentes a partir de especificação funcional.

    Args:
        specification_document: Documento completo de especificação funcional
        requirements_json: JSON dos requisitos (contexto adicional)
        detail_level: Nível de detalhe (concise | balanced | detailed)
        max_agents: Número máximo de agentes a gerar
        custom_instructions: Instruções adicionais do usuário

    Returns:
        Prompt formatado para envio ao LLM
    """

    detail_instructions = {
        "concise": {
            "backstory_lines": "3-5 linhas",
            "responsibilities": "2-4 responsabilidades",
            "tone": "Direto e objetivo"
        },
        "balanced": {
            "backstory_lines": "5-8 linhas",
            "responsibilities": "4-6 responsabilidades",
            "tone": "Equilibrado entre contexto e objetividade"
        },
        "detailed": {
            "backstory_lines": "8-12 linhas",
            "responsibilities": "6-10 responsabilidades",
            "tone": "Detalhado com exemplos e contexto rico"
        }
    }

    detail_config = detail_instructions.get(detail_level, detail_instructions["balanced"])

    # Lista de tools disponíveis (baseado em CrewAI)
    available_tools = [
        "serper_search_tool",
        "tavily_search_tool",
        "serpapi_search_tool",
        "web_scraper_tool",
        "document_reader_tool",
        "pdf_reader_tool",
        "json_parser_tool",
        "file_reader_tool",
        "file_writer_tool",
        "yaml_writer_tool",
        "code_generator_tool",
        "code_docs_search_tool",
        "database_query_tool",
        "email_send_tool",
        "slack_notification_tool",
    ]

    prompt = f"""Você é um arquiteto especialista em design de sistemas multi-agente com CrewAI.

Sua tarefa é analisar a ESPECIFICAÇÃO FUNCIONAL fornecida e **INFERIR AUTOMATICAMENTE** agentes apropriados para implementar o sistema descrito.

═══════════════════════════════════════════════════════════
📋 SPECIFICATION DOCUMENT
═══════════════════════════════════════════════════════════

{specification_document}

═══════════════════════════════════════════════════════════
📊 REQUIREMENTS (Contexto Adicional)
═══════════════════════════════════════════════════════════

{requirements_json or "N/A - Não fornecido"}

═══════════════════════════════════════════════════════════
🎯 SUAS INSTRUÇÕES DE INFERÊNCIA
═══════════════════════════════════════════════════════════

## 1. ANÁLISE DAS SEÇÕES RELEVANTES

Foque especialmente nestas seções da especificação:

**Seção 2 - Escopo do Sistema:**
- Identifique objetivos principais e funcionalidades macro
- Cada objetivo/funcionalidade macro pode sugerir um agente de domínio

**Seção 3 - Requisitos Funcionais:**
- Cada requisito funcional detalhado pode sugerir um agente especializado
- Agrupe requisitos relacionados sob um mesmo agente

**Seção 4 - Casos de Uso:**
- Cada caso de uso complexo pode requerer um agente dedicado
- Identifique interações entre casos de uso para delegation

**Seção 5 - Regras de Negócio:**
- Regras de validação e lógica de negócio sugerem agentes validadores
- Regras complexas podem requerer agentes especializados

**Seção 8 - Fluxos de Processo:**
- Cada fluxo de processo pode mapear para uma sequência de agentes
- Identifique handoffs entre etapas do processo

## 2. HEURÍSTICAS DE IDENTIFICAÇÃO DE AGENTES

### 2.1 Padrão: Substantivo + Verbo Recorrente

Procure por padrões como:
- "Sistema deve **enviar** notificações" → **notification_sender_agent**
- "**Validar** dados de entrada" → **data_validator_agent**
- "**Processar** pagamentos" → **payment_processor_agent**
- "**Gerar** relatórios" → **report_generator_agent**

### 2.2 Padrão: Atores e Personas

Identifique menções a:
- "Cliente", "Usuário", "Administrador" → **customer_interface_agent**, **admin_manager_agent**
- "Sistema externo", "API", "Serviço" → **external_integration_agent**, **api_connector_agent**

### 2.3 Padrão: Domínios Funcionais

Agrupe por domínio:
- **Autenticação/Autorização** → **authentication_agent**, **authorization_agent**
- **Relatórios/Analytics** → **report_generator_agent**, **analytics_agent**
- **Processamento de Dados** → **data_processor_agent**, **data_transformer_agent**
- **Comunicação** → **email_sender_agent**, **notification_manager_agent**

### 2.4 Princípio da Responsabilidade Única

**IMPORTANTE:** Cada agente deve ter UMA responsabilidade bem definida.

Exemplos do TropicalSales:
- ✅ **email_reader_agent** - APENAS lê emails
- ✅ **classifier_agent** - APENAS classifica
- ✅ **stock_checker_agent** - APENAS verifica estoque
- ✅ **response_generator_agent** - APENAS gera e envia respostas

❌ **EVITE:** **email_processor_agent** que lê, classifica, verifica estoque E responde (responsabilidades demais)

## 3. INFERÊNCIA DE ROLES

**ROLE** deve ser uma descrição curta (1-2 linhas) do papel do agente.

**Estrutura:** [Função] + [Domínio/Objeto]

Exemplos:
- "Agente Buscador de Emails Não Lidos"
- "Classificador de Mensagens de Clientes"
- "Especialista em Verificação de Produtos em Estoque"
- "Gerador e Enviador de Respostas Automáticas"

**EXTRAIA** do texto da especificação:
- Verbos de ação: buscar, classificar, verificar, gerar, processar, validar
- Objetos de domínio: emails, mensagens, produtos, pedidos, usuários, relatórios

## 4. INFERÊNCIA DE GOALS

**GOAL** deve ser um objetivo específico e mensurável.

**Estrutura:** [Verbo de ação] + [objeto] + [contexto/restrição]

Exemplos:
- "Buscar emails não lidos usando ferramentas de integração e estruturar seu conteúdo para análise"
- "Classificar precisamente o conteúdo de emails em categorias predefinidas, identificando o assunto principal"
- "Analisar emails categorizados como pedidos, consultar estoque e identificar o produto mais similar disponível"

**EXTRAIA** dos requisitos funcionais e casos de uso:
- O que o agente deve fazer (verbo)
- Sobre o que (objeto)
- Com qual critério de sucesso (mensurável)

## 5. INFERÊNCIA DE BACKSTORIES

**BACKSTORY** deve contextualizar o agente e listar responsabilidades numeradas.

**Estrutura:**
```
Você é um [especialista em X] responsável por:
1. [Responsabilidade específica 1]
2. [Responsabilidade específica 2]
3. [Responsabilidade específica 3]
...

[Contexto adicional ou exemplo, se aplicável]
```

**Tom:** Use "Você é..." para criar senso de identidade.

**Detalhe:** Baseado em detail_level = {detail_level}
- Backstories devem ter: {detail_config['backstory_lines']}
- Listar: {detail_config['responsibilities']}
- Tom: {detail_config['tone']}

**EXTRAIA** das seções 3, 4, 5:
- Passos descritos nos casos de uso → responsabilidades numeradas
- Regras de negócio → restrições e validações no backstory
- Fluxos de processo → sequência de ações no backstory

## 6. INFERÊNCIA DE TOOLS

**IMPORTANTE:** Sugira APENAS tools que REALMENTE são necessárias baseado nas ações descritas.

### 6.1 Mapeamento Automático: Palavras-Chave → Tools

Analise a especificação procurando por estas palavras-chave:

| Palavras-Chave | Tools Sugeridas |
|----------------|-----------------|
| "pesquisar", "buscar na web", "consultar internet" | serper_search_tool, tavily_search_tool |
| "ler documento", "processar PDF", "analisar arquivo" | document_reader_tool, pdf_reader_tool |
| "parsear JSON", "estruturar dados" | json_parser_tool |
| "consultar banco", "verificar estoque", "buscar no banco" | database_query_tool |
| "gerar código", "criar script" | code_generator_tool |
| "criar arquivo", "escrever YAML", "gerar relatório" | file_writer_tool, yaml_writer_tool |
| "enviar email", "notificar por email" | email_send_tool |
| "notificar", "alertar", "enviar mensagem" | slack_notification_tool |
| "analisar código", "documentar código" | code_docs_search_tool |

### 6.2 Inferência por Domínio Funcional

Se a especificação menciona:

**Busca de Informações:**
- → serper_search_tool, tavily_search_tool, web_scraper_tool

**Processamento de Documentos:**
- → document_reader_tool, pdf_reader_tool, json_parser_tool

**Persistência de Dados:**
- → database_query_tool, file_writer_tool, yaml_writer_tool

**Geração de Conteúdo:**
- → code_generator_tool, file_writer_tool

**Comunicação Externa:**
- → email_send_tool, slack_notification_tool

### 6.3 Tools Disponíveis (CrewAI)

Você DEVE sugerir tools desta lista:
{chr(10).join(f"  - {tool}" for tool in available_tools)}

**NÃO invente tools que não existem nesta lista.**

Se precisar de uma tool customizada, use nome genérico como:
- custom_domain_query_tool (substitua "domain" pelo domínio, ex: custom_stock_query_tool)

## 7. INFERÊNCIA DE DELEGATION TARGETS

**DELEGATION_TARGETS:** Outros agentes com quem este agente pode interagir.

**Identifique** nas seções 4 (Casos de Uso) e 8 (Fluxos de Processo):
- Handoffs entre etapas: "Após validação, o sistema **envia** para processamento"
  → validator_agent delegation_targets: [processor_agent]
- Interações explícitas: "Agente A consulta Agente B para obter informação"
  → agentA delegation_targets: [agentB]

**PADRÃO TropicalSales:**
- allow_delegation: false (geralmente)
- Delegation é feita via orquestração de tasks, não delegation do CrewAI

**Recomendação:** Use delegation_targets apenas se houver interação explícita.
Para fluxos sequenciais, deixe vazio [] e confie na orquestração de tasks.

## 8. RATIONALE (Justificativa)

Para cada agente, forneça uma breve justificativa (2-3 frases) explicando:
- Por que este agente é necessário
- Qual problema ele resolve
- Como ele se encaixa no sistema geral

Exemplo:
"Este agente é necessário para isolar a responsabilidade de busca de emails, garantindo que a coleta de dados seja independente da classificação. Ele resolve o problema de acoplamento entre leitura e processamento, permitindo reutilização e testabilidade. Encaixa-se como primeiro passo do pipeline de processamento de emails."

═══════════════════════════════════════════════════════════
⚙️ CONFIGURAÇÃO
═══════════════════════════════════════════════════════════

- **Max Agents:** {max_agents} agentes (recomendado: 4-8 para sistemas moderados)
- **Detail Level:** {detail_level}
- **Verbose:** true (sempre)
- **Allow Delegation:** false (padrão; mude para true apenas se necessário)

═══════════════════════════════════════════════════════════
📝 INSTRUÇÕES ADICIONAIS DO USUÁRIO
═══════════════════════════════════════════════════════════

{custom_instructions or "Nenhuma instrução adicional fornecida."}

═══════════════════════════════════════════════════════════
📤 FORMATO DE OUTPUT
═══════════════════════════════════════════════════════════

Retorne um **JSON válido** contendo um array de agentes.

**IMPORTANTE:** Retorne APENAS o JSON, sem texto adicional antes ou depois.

Estrutura:

```json
[
  {{
    "name": "agent_name_snake_case",
    "role": "Descrição curta do papel (1-2 linhas)",
    "goal": "Objetivo específico e mensurável do agente",
    "backstory": "Você é um especialista...\\n1. Responsabilidade\\n2. Responsabilidade\\n3. ...",
    "verbose": true,
    "allow_delegation": false,
    "suggested_tools": ["tool1", "tool2"],
    "delegation_targets": ["other_agent_name"],
    "rationale": "Justificativa de 2-3 frases explicando por que este agente é necessário."
  }},
  {{
    "name": "another_agent",
    ...
  }}
]
```

**Regras do JSON:**
1. Use aspas duplas (") para strings
2. Use snake_case para nomes de agentes e tools
3. Use \\n para quebras de linha no backstory
4. suggested_tools deve conter apenas tools da lista disponível
5. delegation_targets pode ser array vazio [] se não houver delegation
6. Backstory deve seguir o padrão: "Você é... responsável por:\\n1. ...\\n2. ..."

═══════════════════════════════════════════════════════════
✅ EXEMPLO DE OUTPUT ESPERADO
═══════════════════════════════════════════════════════════

```json
[
  {{
    "name": "document_analyzer_agent",
    "role": "Analisador Especializado de Documentos Funcionais",
    "goal": "Extrair entidades, relacionamentos e regras de negócio de documentos de requisitos para estruturação de sistema",
    "backstory": "Você é um especialista em análise de documentos técnicos responsável por:\\n1. Ler e interpretar documentos de requisitos funcionais\\n2. Identificar entidades de domínio e seus atributos\\n3. Extrair regras de negócio e validações\\n4. Estruturar informações em formato JSON padronizado\\n5. Garantir que nenhuma informação crítica seja perdida no processo",
    "verbose": true,
    "allow_delegation": false,
    "suggested_tools": ["document_reader_tool", "pdf_reader_tool", "json_parser_tool"],
    "delegation_targets": [],
    "rationale": "Este agente é essencial para isolar a complexidade de análise documental, garantindo extração consistente de informações. Ele resolve o problema de interpretação manual de requisitos, automatizando a estruturação de dados. Serve como base para agentes downstream que dependem de entidades bem definidas."
  }},
  {{
    "name": "web_researcher_agent",
    "role": "Pesquisador de Padrões e Compliance na Web",
    "goal": "Buscar standards técnicos, requisitos de compliance e best practices aplicáveis ao domínio do sistema",
    "backstory": "Você é um pesquisador especializado em standards e compliance que:\\n1. Identifica domínios técnicos relevantes do sistema\\n2. Busca standards aplicáveis (ISO, IEEE, OWASP, etc.)\\n3. Pesquisa requisitos de compliance (GDPR, LGPD, PCI-DSS)\\n4. Coleta best practices da indústria\\n5. Estrutura findings em formato JSON com referências",
    "verbose": true,
    "allow_delegation": false,
    "suggested_tools": ["serper_search_tool", "tavily_search_tool", "web_scraper_tool"],
    "delegation_targets": [],
    "rationale": "Necessário para enriquecer a especificação com conhecimento externo de standards e compliance. Resolve o problema de especificações que ignoram requisitos regulatórios e best practices estabelecidas. Complementa a análise documental com contexto da indústria."
  }}
]
```

═══════════════════════════════════════════════════════════
🚀 AGORA É SUA VEZ
═══════════════════════════════════════════════════════════

Analise a ESPECIFICAÇÃO FUNCIONAL fornecida e gere {max_agents} agentes seguindo todas as heurísticas e padrões descritos acima.

**LEMBRE-SE:**
- INFIRA automaticamente roles, goals, backstories e tools
- Use APENAS tools da lista disponível
- Siga o princípio da responsabilidade única
- Retorne APENAS o JSON válido, sem texto adicional

Retorne o JSON agora:"""

    return prompt


def get_tools_by_keywords(text: str) -> List[str]:
    """
    Identifica tools sugeridas baseado em palavras-chave no texto.

    Args:
        text: Texto da especificação

    Returns:
        Lista de tools sugeridas
    """
    text_lower = text.lower()
    suggested_tools = set()

    for keyword, tools in KEYWORD_TO_TOOLS_MAP.items():
        if keyword in text_lower:
            suggested_tools.update(tools)

    return sorted(list(suggested_tools))
