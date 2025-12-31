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

Analise com ATENÇÃO ESPECIAL ao expected_output:

1. **Completude**:
   - Faltam campos obrigatórios (description, expected_output)?
   - Description tem "Input data format" e "Process steps"?
   - Expected_output está presente e completo?

2. **Description**:
   - Process steps numerados (1., 2., 3.)?
   - Input format explicitamente descrito?
   - Placeholders {{variavel}} com chaves duplas?

3. **Expected Output - VALIDAÇÃO CRÍTICA**:
   ✅ Verificar SE JÁ está correto (formato textual descritivo):
      - Usa linguagem natural: "Retornar um texto em formato JSON contendo..."
      - Descreve campos: "- campo: descrição do campo"
      - Descreve listas: "lista de X, onde cada X deve conter as keys: * subcampo"

   ❌ APENAS sugerir correção SE:
      - Usar formato tipado: List[...], Dict[str, Any]
      - Usar JSON literal com chaves fixas
      - Usar schema tipo objeto com properties

   🚨 SE JÁ ESTÁ EM FORMATO TEXTUAL: Marcar como ✅ correto, NÃO sugerir mudança!

4. **Nomenclatura**:
   - Snake_case?
   - Nome com verbo+objeto (ex: read_email, classify_message)?

5. **Placeholders**:
   - Usando {{variavel}} (chaves duplas)?
   - Placeholders referenciados na description?

6. **Dependências**:
   - Inputs/outputs entre tasks coerentes?
   - Tasks referenciam outputs de tasks anteriores corretamente?

7. **Sintaxe YAML**:
   - Identação correta (2 espaços)?
   - Multiline com `>`?
   - Encoding UTF-8 válido?

## VALIDAÇÃO CRÍTICA DE EXPECTED_OUTPUT

⚠️ PADRÃO CREWAI OFICIAL: Expected_output é DESCRIÇÃO TEXTUAL em linguagem natural!

✅ FORMATO CORRETO (NÃO sugerir mudança):
```yaml
expected_output: >
  Retornar um texto em formato JSON contendo as seguintes keys:
  - timestamp: data e hora da execução
  - emails: lista de emails, onde cada email deve conter as keys:
    * email_id: identificador único
    * from: email do remetente
    * subject: assunto do email
```

❌ FORMATOS INCORRETOS (NUNCA sugerir):
```yaml
# ERRADO 1: Formato tipado (Python/TypeScript-like)
expected_output: "List[Email]" ou "Dict[str, Any]"

# ERRADO 2: JSON literal direto
expected_output: (incluir JSON literal com estrutura fixa)

# ERRADO 3: Schema JSON estruturado
expected_output: (usar notação de schema type/properties)
```

Exemplos concretos do formato ERRADO:
- "List[Email]" com tipos Python/TypeScript
- Estruturas JSON fixas ao invés de descrições textuais
- Notação de schema com type/properties ao invés de linguagem natural

🚨 SE O YAML JÁ USA FORMATO TEXTUAL DESCRITIVO: NÃO sugerir "correção" para formato estruturado!

## IMPORTANTE: PADRÃO CREWAI vs. OUTROS FRAMEWORKS

O CrewAI **recomenda oficialmente** expected_output como DESCRIÇÃO TEXTUAL, não como schema estruturado.

- Outros frameworks (AutoGen, LangChain) podem usar schemas JSON
- CrewAI usa descrição natural para flexibilidade do LLM
- NÃO confundir com TypeScript/Python type hints

REFERÊNCIA: https://docs.crewai.com/core-concepts/Tasks/#task-output

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
- Verifique se expected_output está em formato TEXTUAL (linguagem natural)
- NÃO sugerir mudança de formato textual para List[...] ou JSON literal
- Valide coerência entre inputs/outputs das tasks
- Cite linha/task específica ao sugerir melhorias"""
