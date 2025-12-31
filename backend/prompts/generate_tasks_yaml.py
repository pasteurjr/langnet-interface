"""
Prompt para Gerar tasks.yaml a partir de Documento de Especificação de Agentes/Tarefas
"""

def get_tasks_yaml_prompt(agent_task_spec_document: str, custom_instructions: str = "") -> str:
    """
    Gera o prompt para criação de tasks.yaml

    Args:
        agent_task_spec_document: Documento MD com especificação de agentes/tarefas
        custom_instructions: Instruções adicionais do usuário

    Returns:
        Prompt formatado para o LLM
    """
    return f"""Você é especialista em CrewAI e YAML.

TAREFA: Transformar a ESPECIFICAÇÃO DE TAREFAS (Seção 3 do documento MD) em tasks.yaml válido.

DOCUMENTO MD (Seção 3 - Tarefas):
{agent_task_spec_document}

FORMATO tasks.yaml (seguir EXATAMENTE o padrão do framework):

```yaml
task_name:
  description: >
    Descrição detalhada da tarefa.
    Input data format: [descrição do input]

    Process steps:
      1. [Passo 1]
      2. [Passo 2]
      3. [Passo 3]

  expected_output: >
    Retornar um texto em formato JSON contendo as seguintes keys:
    - campo1: descrição do campo
    - campo2: descrição do campo
    - campo3: lista de items, onde cada item deve conter as keys:
      * subcampo1: descrição
      * subcampo2: descrição
```

REGRAS CRÍTICAS:
1. Nome da task: snake_case com verbo+objeto (ex: read_email, classify_message)
2. Description: "fazendo o parametro X = {{X}}" para parametrização
3. Process steps: numerados (1., 2., 3.)
4. Expected_output: TEXTUAL PURO, como linguagem natural
   - "Retornar um texto em formato JSON contendo as seguintes keys:"
   - "lista de X, onde cada X deve conter as keys:"
   - Usar `*` para subcampos
5. Usar `>` para multiline
6. Identação: 2 espaços
7. Placeholders: {{variavel}} (chaves duplas!)

⚠️ IMPORTANTE: Expected_output é DESCRIÇÃO TEXTUAL!
✅ CORRETO: "lista de emails, onde cada email deve conter as keys: * email_id: identificador único"
❌ ERRADO: "List[{{email_id, from}}]"
❌ ERRADO: JSON literal {{{{"emails": [...]}}}}

EXEMPLO REAL (EXATAMENTE como está em tasks.yaml):

```yaml
read_email:
  description: >
    Buscar emails não lidos usando email_fetch_tool e estruturar seu conteúdo básico.
    Input data format: None (busca diretamente usando email_fetch_tool)

    Process steps:
      1. Usar email_fetch_tool para buscar emails não lidos, fazendo o parametro max_emails = {{max_emails}}
      2. Para cada email obtido:
         - Extrair dados básicos (remetente, assunto, conteúdo)
         - Estruturar em formato padronizado
      3. Retornar dados em formato JSON conforme especificado no expected_output

  expected_output: >
    Retornar um texto em formato JSON contendo as seguintes keys:
    - timestamp: data e hora da execução
    - total_emails: quantidade de emails processados
    - emails: lista de emails, onde cada email deve conter as keys:
      * email_id: identificador único
      * from: email do remetente
      * subject: assunto do email
      * content: texto completo do email
      * date: data e hora do email
      * status: indicador se email foi lido com sucesso

classify_message:
  description: >
    Classificar cada email identificando sua categoria específica.
    Input data format:
      - JSON da task read_email_task contendo:
        * timestamp: data e hora da execução
        * total_emails: quantidade de emails processados
        * emails: lista onde cada email contém:
          - email_id: identificador único
          - from: email do remetente
          - subject: assunto do email
          - content: texto completo do email
          - date: data e hora do email
          - status: indicador se email foi lido com sucesso

    Process steps:
      1. Para cada email na lista:
         - Analisar conteúdo e classificar em categorias predefinidas
         - Se for pedido, identificar nome do produto e quantidade
         - Adicionar classificação ao registro do email

  expected_output: >
    Retornar um texto em formato JSON mantendo EXATAMENTE a mesma estrutura do input e adicionando para cada email na lista 'emails' as keys:
    - categoria: uma das categorias definidas nos steps
    - justificativa: texto explicando a classificação
    - nome_produto_pedido: se categoria for pedido, nome do produto identificado no conteúdo do email
    - quantidade_pedido: se categoria for pedido, quantidade do produto identificada no conteúdo do email

check_stock_availability:
  description: >
    Verificar disponibilidade em estoque dos produtos solicitados em pedidos.
    Input data format:
      - JSON da task classify_message contendo:
        * timestamp
        * total_emails
        * emails: lista onde cada email contém:
          - email_id, from, subject, content, date, status
          - categoria: classificação do email
          - justificativa: motivo da classificação
          - nome_produto_pedido: nome do produto identificado
          - quantidade_pedido: quantidade do produto identificada

    Process steps:
      1. Para cada email na lista:
         - Se categoria for "pedidos":
           * Enviar nome do produto para natural_language_query_stock_tool
           * Analisar produtos retornados
           * Selecionar produto mais similar ao solicitado
           * Adicionar produto escolhido e quantidade ao registro

  expected_output: >
    Retornar texto em formato JSON mantendo a estrutura do input (somente com os emails que sejam pedidos) e adicionando para cada email que tenha categoria igual a pedido:
    - produto_escolhido: nome do produto mais similar encontrado em estoque
    - quantidade_disponivel: quantidade em estoque do produto escolhido
```

{f'INSTRUÇÕES CUSTOMIZADAS:\\n{custom_instructions}' if custom_instructions else ''}

OUTPUT: Retorne APENAS o conteúdo do tasks.yaml (sem explicações, sem markdown).

Gere agora:"""
