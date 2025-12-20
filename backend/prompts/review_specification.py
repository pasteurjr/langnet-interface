"""
Review Specification Prompt
Generates structured suggestions for improving functional specifications
"""

def get_review_specification_prompt(specification_document: str) -> str:
    """
    Generate review prompt for specification analysis

    Args:
        specification_document: Current specification markdown content

    Returns:
        Formatted prompt for LLM review
    """
    return f"""Você é um especialista em análise de especificações técnicas e funcionais de software.

DOCUMENTO ATUAL:
{specification_document}

TAREFA: Revise este documento de especificação funcional e identifique pontos que podem ser melhorados.

Analise os seguintes aspectos:
1. **Completude** - Requisitos faltantes ou incompletos
2. **Clareza** - Ambiguidades, falta de detalhes técnicos ou explicações insuficientes
3. **Consistência** - Contradições, inconsistências entre seções ou requisitos conflitantes
4. **Viabilidade** - Requisitos irrealistas, problemáticos ou difíceis de implementar
5. **Boas Práticas** - Melhorias arquiteturais, técnicas ou de design

FORMATO DE SAÍDA (Markdown):

## 🔍 Sugestões de Melhoria

### ✅ Pontos Positivos
- [Liste 2-3 pontos fortes do documento atual - aspectos bem detalhados, requisitos claros, etc.]

### ⚠️ Pontos a Melhorar

#### 1. [Categoria - ex: Completude, Clareza, etc.]
- **Problema**: [Descrição específica do problema identificado]
- **Sugestão**: [Como melhorar - seja específico e construtivo]
- **Impacto**: [Alto/Médio/Baixo] - justifique brevemente
- **Localização**: [Seção ou requisito específico afetado]

#### 2. [Categoria]
- **Problema**: [...]
- **Sugestão**: [...]
- **Impacto**: [...]
- **Localização**: [...]

[Continue com outros pontos - foque nos 5-8 mais importantes]

### 💡 Recomendações Gerais
- [Sugestão geral 1 - melhorias aplicáveis a múltiplas seções]
- [Sugestão geral 2]
- [Sugestão geral 3]

### 📋 Próximos Passos Sugeridos
1. [Ação específica recomendada]
2. [Ação específica recomendada]
3. [Ação específica recomendada]

IMPORTANTE:
- Seja específico e construtivo em suas sugestões
- Foque nos pontos mais críticos e de maior impacto
- Evite sugestões genéricas - seja concreto e acionável
- Se o documento está excelente, seja honesto e reconheça isso
- Mantenha um tom profissional e educado
"""
