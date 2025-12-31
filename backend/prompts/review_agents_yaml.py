"""
Prompt para Revisar agents.yaml
"""

def get_review_agents_yaml_prompt(agents_yaml_content: str) -> str:
    """
    Gera o prompt para revisão de agents.yaml

    Args:
        agents_yaml_content: Conteúdo do agents.yaml a ser revisado

    Returns:
        Prompt formatado para o LLM
    """
    return f"""Você é especialista em análise de agents.yaml CrewAI.

YAML ATUAL:
{agents_yaml_content}

TAREFA: Revise este agents.yaml e identifique melhorias.

Analise:
1. **Completude**: Faltam campos? role/goal/backstory claros?
2. **Backstory**: Detalhado suficiente? Responsabilidades claras?
3. **Nomenclatura**: Snake_case? Terminam em _agent?
4. **Boas Práticas**: verbose/allow_delegation apropriados?
5. **Sintaxe YAML**: Identação, multiline (`>`), encoding

FORMATO DE SAÍDA (Markdown):

## 🔍 Sugestões de Melhoria - agents.yaml

### ✅ Pontos Positivos
- [2-3 pontos fortes]

### ⚠️ Pontos a Melhorar

#### 1. [Categoria]
- **Problema**: [Descrição específica]
- **Sugestão**: [Como melhorar]
- **Impacto**: [Alto/Médio/Baixo]
- **Localização**: [agent_name]

#### 2. [Categoria]
- **Problema**: [Descrição específica]
- **Sugestão**: [Como melhorar]
- **Impacto**: [Alto/Médio/Baixo]
- **Localização**: [agent_name]

### 💡 Recomendações Gerais
- [Sugestão 1]
- [Sugestão 2]

### 📋 Próximos Passos
1. [Ação específica]
2. [Ação específica]

IMPORTANTE: Seja específico, construtivo, acionável."""
