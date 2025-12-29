"""
Review Agent Task Specification Prompt
Generates structured suggestions for improving agent/task specifications
"""

def get_review_agent_task_spec_prompt(agent_task_spec_document: str) -> str:
    """
    Generate review prompt for agent/task spec analysis

    Args:
        agent_task_spec_document: Current agent/task spec markdown content

    Returns:
        Formatted prompt for LLM review
    """
    return f"""Você é um especialista em análise de sistemas multi-agente e especificações CrewAI.

DOCUMENTO ATUAL:
{agent_task_spec_document}

TAREFA: Revise este documento de especificação de agentes e tarefas e identifique pontos que podem ser melhorados.

Analise os seguintes aspectos:
1. **Completude dos Agentes** - Agents faltando role/goal/backstory, tools mal especificadas, LLMs inadequados
2. **Clareza das Tarefas** - Descrições ambíguas, input/output schemas incompletos, expected_output vago
3. **Arquitetura Multi-Agente** - Redundância entre agentes, fluxo de tasks subotimizado, delegação mal definida
4. **Rastreabilidade** - Tasks sem mapeamento para UC/RF, requisitos não cobertos
5. **Boas Práticas** - Nomenclatura inconsistente, modularização inadequada, problemas de escalabilidade

FORMATO DE SAÍDA (Markdown):

## 🔍 Sugestões de Melhoria

### ✅ Pontos Positivos
- [Liste 2-3 pontos fortes - agentes bem definidos, tasks claras, boa rastreabilidade, etc.]

### ⚠️ Pontos a Melhorar

#### 1. [Categoria - ex: Completude dos Agentes]
- **Problema**: [Descrição específica - ex: "AG-01 não tem tools especificadas"]
- **Sugestão**: [Como melhorar - ex: "Adicionar tools: web_search, file_reader"]
- **Impacto**: [Alto/Médio/Baixo] - justifique
- **Localização**: [Ex: "Seção 2.1 - AG-01: Business Analyst"]

#### 2. [Categoria]
- **Problema**: [...]
- **Sugestão**: [...]
- **Impacto**: [...]
- **Localização**: [...]

[Continue com outros pontos - foque nos 5-8 mais importantes]

### 💡 Recomendações Gerais
- [Sugestão geral 1 - melhorias aplicáveis a múltiplos agentes/tasks]
- [Sugestão geral 2]
- [Sugestão geral 3]

### 📋 Próximos Passos Sugeridos
1. [Ação específica - ex: "Adicionar input_schema para T-001-01"]
2. [Ação específica]
3. [Ação específica]

IMPORTANTE:
- Seja específico e construtivo em suas sugestões
- Foque nos pontos mais críticos e de maior impacto
- Evite sugestões genéricas - seja concreto e acionável
- Se o documento está excelente, seja honesto e reconheça isso
- Mantenha um tom profissional e educado
- Considere boas práticas de CrewAI ao avaliar
"""
