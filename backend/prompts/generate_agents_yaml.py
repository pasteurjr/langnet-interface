"""
Prompt para Gerar agents.yaml a partir de Documento de Especificação de Agentes/Tarefas
"""

def get_agents_yaml_prompt(agent_task_spec_document: str, custom_instructions: str = "") -> str:
    """
    Gera o prompt para criação de agents.yaml

    Args:
        agent_task_spec_document: Documento MD com especificação de agentes/tarefas
        custom_instructions: Instruções adicionais do usuário

    Returns:
        Prompt formatado para o LLM
    """
    return f"""Você é especialista em CrewAI e YAML.

TAREFA: Transformar a ESPECIFICAÇÃO DE AGENTES (Seção 2 do documento MD) em agents.yaml válido.

DOCUMENTO MD (Seção 2 - Agentes):
{agent_task_spec_document}

FORMATO agents.yaml:

```yaml
agent_name:
  role: >
    [Título do papel - 1 linha]
  goal: >
    [Objetivo mensurável - 1-2 linhas]
  backstory: >
    [Contexto detalhado - 100-300 palavras]

    Responsabilidades:
    1. [Resp 1]
    2. [Resp 2]
    3. [Resp 3]

    Expertise:
    - [Área 1]
    - [Área 2]

    Padrões:
    - [Framework 1]
    - [Framework 2]
  verbose: true
  allow_delegation: false
```

REGRAS:
1. Nome do agente: snake_case terminando em _agent (ex: email_reader_agent)
2. Extrair role, goal, backstory da tabela de agentes (Seção 2 do MD)
3. Backstory: expandir com responsabilidades (3-5 itens), expertise, padrões
4. verbose: sempre true
5. allow_delegation: false (ou true se mencionar delegação)
6. Usar `>` para multiline
7. Identação: 2 espaços

EXEMPLO:

```yaml
email_reader_agent:
  role: >
    Agente Buscador de Emails Não Lidos
  goal: >
    Buscar emails não lidos usando email_fetch_tool e estruturar seu conteúdo para análise
  backstory: >
    Você é um especialista em busca e leitura de emails com 10+ anos de experiência.

    Responsabilidades:
    1. Buscar todos os emails não lidos usando email_fetch_tool
    2. Estruturar os dados básicos (remetente, assunto, conteúdo)
    3. Preparar dados em formato padronizado

    Expertise:
    - Protocolos IMAP/POP3
    - Parsing de estruturas de email
    - Normalização de dados textuais

    Padrões:
    - RFC 5322 (Internet Message Format)
    - UTF-8 encoding
    - JSON Schema para output
  verbose: true
  allow_delegation: false

classifier_agent:
  role: >
    Agente Classificador de Emails
  goal: >
    Classificar emails em categorias específicas com base no conteúdo
  backstory: >
    Você é um especialista em análise e classificação de textos com 8+ anos de experiência.

    Responsabilidades:
    1. Analisar conteúdo de emails
    2. Identificar padrões e categorias
    3. Extrair informações específicas (produtos, quantidades)

    Expertise:
    - NLP e análise de sentimentos
    - Classificação de textos
    - Extração de entidades

    Padrões:
    - Taxonomias de classificação
    - Regras de negócio específicas
  verbose: true
  allow_delegation: false
```

{f'INSTRUÇÕES CUSTOMIZADAS:\\n{custom_instructions}' if custom_instructions else ''}

OUTPUT: Retorne APENAS o conteúdo do agents.yaml (sem explicações, sem markdown).

Gere agora:"""
