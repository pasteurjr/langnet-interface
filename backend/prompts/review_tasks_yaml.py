"""
Prompt para Revisar tasks.yaml
"""

def get_review_tasks_yaml_prompt(tasks_yaml_content: str) -> str:
    """
    Gera o prompt para revisão de tasks.yaml

    Args:
        tasks_yaml_content: Conteúdo do tasks.yaml a ser revisado

    Returns:
        Prompt formatado para o LLM
    """
    return f"""Você é especialista em análise de tasks.yaml CrewAI.

YAML ATUAL:
{tasks_yaml_content}

TAREFA: Revise este tasks.yaml e identifique melhorias.

Analise:
1. **Completude**: Faltam campos? description/expected_output claros?
2. **Description**: Process steps bem definidos? Input format claro?
3. **Expected Output**: Formato TEXTUAL correto? Sem JSON literal?
4. **Nomenclatura**: Snake_case? Verbo+objeto?
5. **Placeholders**: {{variavel}} correto?
6. **Dependências**: Inputs/outputs entre tasks coerentes?
7. **Sintaxe YAML**: Identação, multiline (`>`), encoding

FORMATO DE SAÍDA (Markdown):

## 🔍 Sugestões de Melhoria - tasks.yaml

### ✅ Pontos Positivos
- [2-3 pontos fortes]

### ⚠️ Pontos a Melhorar

#### 1. [Categoria]
- **Problema**: [Descrição específica]
- **Sugestão**: [Como melhorar]
- **Impacto**: [Alto/Médio/Baixo]
- **Localização**: [task_name]

#### 2. [Categoria]
- **Problema**: [Descrição específica]
- **Sugestão**: [Como melhorar]
- **Impacto**: [Alto/Médio/Baixo]
- **Localização**: [task_name]

### 💡 Recomendações Gerais
- [Sugestão 1]
- [Sugestão 2]

### 📋 Próximos Passos
1. [Ação específica]
2. [Ação específica]

IMPORTANTE:
- Seja específico, construtivo, acionável
- Verifique se expected_output está em formato TEXTUAL
- Valide coerência entre inputs/outputs das tasks"""
