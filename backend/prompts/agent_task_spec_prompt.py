"""
Prompt para Geração de Especificação de Agentes e Tarefas
==========================================================
Gera documento Markdown estruturado com tabelas de agentes e tarefas
"""

from typing import List, Optional


def build_agent_task_spec_prompt(
    specification_document: str,
    detail_level: str = "balanced",
    max_agents: int = 10,
    frameworks: List[str] = ["CrewAI"],
    custom_instructions: Optional[str] = None
) -> str:
    """
    Constrói prompt para gerar especificação de agentes e tarefas

    Output esperado: Documento Markdown com 5 seções:
    1. VISÃO GERAL DOS AGENTES (tabela resumo)
    2. ESPECIFICAÇÃO DETALHADA DOS AGENTES (tabelas individuais)
    3. ESPECIFICAÇÃO DETALHADA DAS TAREFAS (tabelas individuais)
    4. MATRIZ DE RASTREABILIDADE
    5. GRAFO DE DEPENDÊNCIAS (resumo visual)
    """

    frameworks_str = ', '.join(frameworks)

    prompt = f"""
# GERAÇÃO DE ESPECIFICAÇÃO DE AGENTES E TAREFAS

Você é um arquiteto de sistemas multi-agente especializado em {frameworks_str}.

## TAREFA

A partir da **ESPECIFICAÇÃO FUNCIONAL** fornecida, gere um documento estruturado
especificando TODOS os agentes e tarefas necessários para implementar o sistema.

## ESPECIFICAÇÃO FUNCIONAL (FONTE PRIMÁRIA)

{specification_document}

## FRAMEWORKS SUPORTADOS

{frameworks_str}

## NÍVEL DE DETALHAMENTO

{detail_level.upper()}

## INSTRUÇÕES CRÍTICAS

1. **Número de Agentes:** Gerar entre 8 e {max_agents} agentes especializados
2. **Princípio SRP:** Cada agente tem UMA responsabilidade única
3. **LLM Assignment:** Especificar LLM apropriado para cada agente:
   - **Claude 3.5 Sonnet**: Tarefas complexas (análise profunda, raciocínio, validação de lógica)
   - **GPT-4o**: Tarefas balanceadas (processamento de texto, extração estruturada)
   - **GPT-4o-mini**: Tarefas simples (busca, formatação, extração básica)

4. **Memória:** Especificar se memória deve estar habilitada/desabilitada por agente
5. **Delegação:** Especificar para quais outros agentes pode delegar (usar IDs AG-XX)
6. **Módulos Funcionais:** Agrupar agentes por módulo (ex: Cadastro, Monitoramento, Classificação, Análise, etc)
7. **Rastreabilidade:** TODA task deve mapear para UC e RF da especificação funcional

## FORMATO DE OUTPUT (MARKDOWN)

### 1. VISÃO GERAL DOS AGENTES

| ID    | Nome                 | Módulo             | LLM            | Memória |
|-------|----------------------|--------------------|----------------|---------|
| AG-01 | portfolio_manager    | Cadastro           | Claude 3.5     | Sim     |
| AG-02 | edital_hunter        | Monitoramento      | GPT-4o-mini    | Não     |
| AG-03 | document_parser      | Análise            | GPT-4o         | Não     |
| ...   | ...                  | ...                | ...            | ...     |

### 2. ESPECIFICAÇÃO DETALHADA DOS AGENTES

Para cada agente, criar tabela individual:

#### AG-01: Portfolio Manager Agent

| Atributo          | Especificação |
|-------------------|---------------|
| **Nome**          | portfolio_manager_agent |
| **Role**          | Gerente de Portfólio de Produtos |
| **Goal**          | Manter cadastro completo e otimizado de produtos para maximizar aderência em editais públicos |
| **Backstory**     | Você é um especialista em catálogos de produtos com 15+ anos de experiência em licitações públicas. Você é responsável por:\\n1. Garantir completude e precisão de informações técnicas de produtos\\n2. Maximizar aderência de produtos a editais\\n3. Manter base de dados atualizada e otimizada |
| **LLM**           | Claude 3.5 Sonnet |
| **Tools**         | pdf_reader, docx_reader, embedding_tool, database_tool |
| **Delegação**     | Pode delegar para AG-03 (Document Parser Agent) quando precisar extrair dados de documentos complexos |
| **Memória**       | Habilitada (necessária para manter contexto de produtos) |
| **Verbose**       | true |
| **Módulo**        | Cadastro do Portfólio |
| **Rationale**     | Este agente é essencial porque centraliza a gestão de produtos, garantindo que informações técnicas estejam completas e padronizadas para análise posterior de editais. |

**Tarefas Associadas:** T-CAD-001, T-CAD-002, T-CAD-003, T-CAD-004

---

*(Repetir para todos os agentes AG-02, AG-03, ...)*

### 3. ESPECIFICAÇÃO DETALHADA DAS TAREFAS

Para cada task, criar tabela individual:

#### T-CAD-001: Upload e Processamento de Manuais

| Atributo           | Especificação |
|--------------------|---------------|
| **ID**             | T-CAD-001 |
| **Nome**           | upload_process_manuals |
| **Descrição**      | Processar upload de manuais técnicos, instruções de uso e especificações de produtos. Extrair texto, identificar estrutura documental e armazenar documento indexado para consulta futura. |
| **Agent**          | AG-01 (Portfolio Manager Agent) |
| **Tools**          | pdf_reader, docx_reader, database_tool |
| **Input Schema**   | \\n- manual_file: File (PDF/DOCX)\\n- product_class: String (classe do produto) |
| **Output Schema**  | \\n- document_id: UUID (ID do documento armazenado)\\n- extracted_text: Text (texto extraído)\\n- structure_metadata: JSON (metadados de estrutura) |
| **Dependencies**   | None (primeira task do módulo) |
| **Módulo**         | Cadastro do Portfólio |
| **UC Relacionado** | UC-CAD-001 (Cadastrar Produto Manualmente) |
| **RF Relacionado** | RF-001 (Upload de documentos), RF-002 (Extração de texto) |
| **Rationale**      | Esta task é fundamental porque permite que o sistema ingira informações técnicas de produtos a partir de documentos oficiais, garantindo precisão e rastreabilidade. |

---

*(Repetir para todas as tasks T-CAD-002, T-CAD-003, T-MON-001, etc)*

### 4. MATRIZ DE RASTREABILIDADE

| Task ID   | Task Nome                 | UC          | RF          | Módulo       |
|-----------|---------------------------|-------------|-------------|--------------|
| T-CAD-001 | upload_process_manuals    | UC-CAD-001  | RF-001, RF-002 | Cadastro  |
| T-CAD-002 | extract_specifications_ai | UC-CAD-001  | RF-002, RF-003 | Cadastro  |
| T-CAD-003 | validate_completeness     | UC-CAD-001  | RF-004      | Cadastro  |
| T-MON-001 | fetch_new_editais         | UC-MON-001  | RF-010, RF-011 | Monitoramento |
| ...       | ...                       | ...         | ...         | ...          |

### 5. GRAFO DE DEPENDÊNCIAS (RESUMO VISUAL)

```
MÓDULO: Cadastro do Portfólio
├─ T-CAD-001 (Upload Manuais)
│  ↓
├─ T-CAD-002 (Extrair Especificações com IA)
│  ↓
└─ T-CAD-003 (Validar Completude)

MÓDULO: Monitoramento de Editais
├─ T-MON-001 (Buscar Novos Editais)
│  ↓
├─ T-MON-002 (Parsear Documento de Edital)
│  ↓
└─ T-MON-003 (Extrair Itens e Especificações)
    ↓
    T-CLA-001 (Classificar Item vs Produto)
```

## DIRETRIZES ADICIONAIS

1. **Nomenclatura:**
   - Agentes: snake_case terminando em `_agent` (ex: portfolio_manager_agent)
   - Tasks: snake_case com verbo + objeto (ex: upload_process_manuals, classify_item_product)
   - IDs: AG-XX para agentes, T-[MÓDULO]-XXX para tasks (ex: AG-01, T-CAD-001, T-MON-001)

2. **Tools (Ferramentas CrewAI Reais):**
   - Documentos: pdf_reader, docx_reader, txt_reader
   - Web: serper_search_tool, tavily_search_tool, scrape_website_tool
   - Banco: database_tool, sql_query_tool
   - Embeddings: embedding_tool, vector_search_tool
   - APIs: api_call_tool, json_parser_tool

3. **Dependencies:**
   - Especificar dependencies CLARAS entre tasks
   - Tasks sem dependencies podem executar em paralelo
   - Use nomes exatos de tasks (ex: dependencies: ["upload_process_manuals"])

4. **Rastreabilidade:**
   - Use IDs EXATOS da especificação funcional (UC-XXX, RF-XXX, RN-XXX)
   - Se um UC não tem ID, crie um consistente (ex: UC-CAD-001, UC-MON-001)

5. **Módulos Funcionais:**
   - Identifique 4-8 módulos principais baseados nos casos de uso
   - Exemplos: Cadastro, Monitoramento, Classificação, Score, Proposta, Notificação

{f'## INSTRUÇÕES CUSTOMIZADAS\\n\\n{custom_instructions}' if custom_instructions else ''}

## OUTPUT FINAL

Retorne o documento COMPLETO em Markdown seguindo exatamente a estrutura das 5 seções acima.

⚠️ **CRÍTICO:**
- TODAS as 5 seções devem estar presentes
- TODAS as tabelas devem estar completas e formatadas corretamente
- IDs devem seguir os padrões (AG-XX, T-XXX-XXX)
- Rastreabilidade deve usar IDs reais da especificação funcional

Gere agora a especificação completa:
"""

    return prompt
