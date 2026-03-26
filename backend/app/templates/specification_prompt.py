"""
Specification Generation Prompt Template
Generates comprehensive functional specification documents from requirements
"""


def build_specification_prompt(
    requirements_document: str,
    requirements_version: int,
    requirements_change_type: str,
    requirements_created_at: str,
    complementary_docs: str = "",
    detail_level: str = 'detailed',
    target_audience: str = 'mixed',
    include_data_model: bool = True,
    include_use_cases: bool = True,
    include_business_rules: bool = True,
    include_glossary: bool = True,
    custom_instructions: str = None,
    project_name: str = "Sistema",
    wireframe_format: str = 'ascii'  # 'ascii' | 'plantuml'
) -> str:
    """
    Build LLM prompt for functional specification generation

    Args:
        requirements_document: PRIMARY SOURCE - Requirements document content
        requirements_version: Version number of requirements used
        requirements_change_type: Type of change in requirements (analysis, refinement, etc)
        requirements_created_at: Creation date of requirements version
        complementary_docs: ADDITIONAL CONTEXT - Optional complementary documents
        detail_level: Level of detail (basic, detailed, comprehensive)
        target_audience: Target audience (technical, business, mixed)
        include_data_model: Whether to include data model section
        include_use_cases: Whether to include use cases section
        include_business_rules: Whether to include business rules section
        include_glossary: Whether to include glossary section
        custom_instructions: Optional custom instructions from user
        project_name: Name of the project

    Returns:
        Complete prompt for LLM specification generation
    """

    # Build sections to include
    sections_config = []
    if include_data_model:
        sections_config.append("- Modelo de Dados Conceitual")
    if include_use_cases:
        sections_config.append("- Casos de Uso Detalhados")
    if include_business_rules:
        sections_config.append("- Regras de Negócio")
    if include_glossary:
        sections_config.append("- Glossário de Termos")

    sections_list = "\n".join(sections_config) if sections_config else "- Todas as seções padrão"

    # Detail level instructions
    detail_instructions = {
        'basic': """
- Foco em visão geral de alto nível
- Descrições concisas e diretas
- Omitir detalhes técnicos profundos
- Priorizar clareza e simplicidade
""",
        'detailed': """
- Equilíbrio entre visão geral e detalhes
- Descrições completas mas objetivas
- Incluir detalhes técnicos relevantes
- Manter clareza e profundidade balanceadas
""",
        'comprehensive': """
- Máximo nível de detalhamento
- Descrições técnicas profundas
- Incluir todos os aspectos relevantes
- Documentação exaustiva de cada funcionalidade
"""
    }

    # Audience-specific tone
    audience_tone = {
        'technical': "Use terminologia técnica precisa e foque em detalhes de implementação.",
        'business': "Use linguagem de negócios clara, evite jargão técnico excessivo, foque em valor e benefícios.",
        'mixed': "Combine linguagem técnica e de negócios, explique termos quando necessário, atenda ambos públicos."
    }

    # Build complementary docs section
    complementary_section = ""
    if complementary_docs and complementary_docs.strip():
        complementary_section = f"""
## DOCUMENTOS COMPLEMENTARES (CONTEXTO ADICIONAL)

⚠️ IMPORTANTE: Os documentos abaixo são CONTEXTO ADICIONAL para enriquecer a especificação.
A FONTE PRIMÁRIA e OFICIAL é o Documento de Requisitos acima.

{complementary_docs}

---
"""

    # Build custom instructions section
    custom_section = ""
    if custom_instructions and custom_instructions.strip():
        custom_section = f"""
## INSTRUÇÕES CUSTOMIZADAS DO USUÁRIO

{custom_instructions}

---
"""

    # Build main prompt
    prompt = f"""
# GERAÇÃO DE ESPECIFICAÇÃO FUNCIONAL

Você é um Analista de Sistemas especializado em criar especificações funcionais completas e detalhadas.

## FONTE PRIMÁRIA: DOCUMENTO DE REQUISITOS (OFICIAL)

**Projeto:** {project_name}
**Versão dos Requisitos:** {requirements_version}
**Tipo de Documento:** {requirements_change_type}
**Data de Criação:** {requirements_created_at}

⚠️ CRÍTICO: Este é o documento OFICIAL de requisitos. Todas as funcionalidades e necessidades descritas aqui são PRIORITÁRIAS e devem ser fielmente refletidas na especificação.

---

{requirements_document}

---

{complementary_section}{custom_section}
## TAREFA: CRIAR ESPECIFICAÇÃO FUNCIONAL COMPLETA

### Configurações da Geração

**Nível de Detalhe:** {detail_level}
{detail_instructions.get(detail_level, detail_instructions['detailed'])}

**Público-alvo:** {target_audience}
{audience_tone.get(target_audience, audience_tone['mixed'])}

**Seções a Incluir:**
{sections_list}

### Estrutura Obrigatória do Documento

Você DEVE gerar um documento em Markdown seguindo EXATAMENTE esta estrutura:

```markdown
# Especificação Funcional - {project_name}

**Versão:** 1.0
**Data:** {requirements_created_at}
**Baseado em:** Requisitos v{requirements_version}

---

## 1. Introdução

### 1.1 Objetivo do Documento
Descrever o propósito desta especificação funcional.

### 1.2 Escopo do Sistema
Definir claramente o que está dentro e fora do escopo.

### 1.3 Definições, Acrônimos e Abreviações
Listar termos importantes para entendimento do documento.

### 1.4 Referências
- Documento de Requisitos v{requirements_version} ({requirements_created_at})
- [Listar outros documentos referenciados]

---

## 2. Visão Geral do Sistema

### 2.1 Perspectiva do Sistema
Posicionamento e contexto do sistema no ambiente.

### 2.2 Principais Funcionalidades
Lista resumida das funcionalidades-chave.

### 2.3 Usuários e Características
Perfis de usuários e suas necessidades.

### 2.4 Restrições Gerais
Limitações técnicas, de negócio ou regulatórias.

### 2.5 Premissas e Dependências
Suposições e dependências externas.

---

## 3. Requisitos Funcionais Detalhados

### 3.1 Consolidação de Requisitos
Para CADA requisito funcional identificado no documento de requisitos:

**RF-XXX: [Nome do Requisito]**
- **Descrição:** [Descrição completa]
- **Prioridade:** [Alta/Média/Baixa]
- **Origem:** [Rastreamento para documento de requisitos]
- **Critérios de Aceitação:**
  1. [Critério mensurável 1]
  2. [Critério mensurável 2]
- **Regras de Negócio Associadas:** [Se aplicável]
- **Dependências:** [Outros requisitos relacionados]

[Repetir para TODOS os requisitos funcionais]

---

## 4. Requisitos Não-Funcionais

### 4.1 Requisitos de Performance
- [Tempo de resposta esperado]
- [Capacidade de processamento]
- [Escalabilidade]

### 4.2 Requisitos de Segurança
- [Autenticação e autorização]
- [Criptografia]
- [Proteção de dados]

### 4.3 Requisitos de Usabilidade
- [Acessibilidade]
- [Interface do usuário]
- [Experiência do usuário]

### 4.4 Requisitos de Confiabilidade
- [Disponibilidade]
- [Recuperação de falhas]
- [Backup]

### 4.5 Requisitos de Manutenibilidade
- [Modularidade]
- [Documentação]
- [Testabilidade]

---

## 5. Casos de Uso
{f'''
### 🚨 REGRAS ABSOLUTAS — VIOLAÇÃO INVALIDA O DOCUMENTO:

**PROIBIÇÕES ABSOLUTAS — NUNCA ESCREVA:**
- "Por questões de espaço..."
- "seguem a mesma estrutura..."
- "serão resumidos abaixo..."
- "UC-XXX a UC-YYY seguem o padrão..."
- "ver UC-001 para referência..."
- Qualquer forma de abreviação, resumo ou referência cruzada entre UCs
- Colchetes com texto genérico como `[Nome do Ator]` ou `[ação do sistema]`

**OBRIGAÇÕES:**
1. CADA UC deve ser COMPLETAMENTE especificado — tabela de cabeçalho, fluxo principal completo, fluxos alternativos, exceções e wireframe
2. MÍNIMO 10 UCs totalmente detalhados, independente do tamanho do documento
3. USAR EXCLUSIVAMENTE nomes reais do documento de requisitos — atores, telas, campos, botões, mensagens
4. A coluna "Resposta do Sistema" DEVE descrever elementos concretos da UI (nome exato da tela, campos listados, texto das mensagens)
5. Sub-passos opcionais são numerados como 2.1, 2.2, etc.
6. Cada UC DEVE ter wireframe da(s) tela(s) principal(is)
7. O documento pode ser LONGO — isso é ESPERADO e OBRIGATÓRIO. Não comprima.

### 5.1 Atores do Sistema
[Listar TODOS os atores identificados no documento de requisitos com nome real e papel]

### 5.2 Especificação Detalhada de Casos de Uso

Para CADA caso de uso (MÍNIMO 10):

---

**UC-XXX: [título real do caso de uso]**

| Campo | Detalhe |
|-------|---------|
| **Ator Principal** | [nome real do perfil de usuário] |
| **Atores Secundários** | [outros envolvidos ou "Nenhum"] |
| **Objetivo** | [objetivo real baseado no requisito funcional] |
| **Pré-condições** | [condições reais necessárias] |
| **Pós-condições** | [estado real do sistema após execução bem-sucedida] |
| **RFs Relacionados** | RF-XXX, RF-YYY |
| **RNs Aplicáveis** | RN-XXX ou "Nenhum" |

#### Fluxo Principal

| # | Ação do Ator | Resposta do Sistema |
|---|--------------|---------------------|
| 1 | [ação concreta e real do ator — usar nome real do elemento UI clicado/preenchido] | [o sistema exibe/faz: descrever elementos UI visíveis — nome da tela, campos, botões, mensagens com texto exato] |
| 2 | [próxima ação — pode ser "O usuário pode opcionalmente:"] | [resposta do sistema ou deixar em branco se for cabeçalho de sub-ações] |
| 2.1 | [sub-ação opcional A — ex: "Clica em 'Cancelar'"] | [resposta específica — ex: "Sistema fecha o modal e retorna à tela anterior sem salvar dados"] |
| 2.2 | [sub-ação opcional B] | [resposta específica com elementos UI] |
| 3 | [próxima ação principal] | [resposta detalhada] |

#### Fluxos Alternativos

| ID | Condição | Ação do Ator | Resposta do Sistema |
|----|----------|--------------|---------------------|
| A1 | [condição real que desvia o fluxo] | [o que o ator faz nessa condição] | [como o sistema responde, mensagem exibida, próxima tela] |
| A2 | [outra condição alternativa] | [ação do ator] | [resposta do sistema] |

#### Fluxos de Exceção

| ID | Erro/Problema | Resposta do Sistema |
|----|--------------|---------------------|
| E1 | [erro real que pode ocorrer] | [mensagem exata exibida ao usuário + ação disponível ex: botão "Tentar novamente"] |
| E2 | [outro erro possível] | [tratamento e recuperação] |

#### Wireframe da Interface

''' + ('''
**Tela:** [nome real da tela]

```
┌─────────────────────────────────────────────┐
│  [Título real da tela]                      │
├─────────────────────────────────────────────┤
│                                             │
│  [Campo 1]: [____________________________] │
│  [Campo 2]: [____________________________] │
│                                             │
│  ┌──────────────────┐  ┌─────────────────┐ │
│  │  Botão Principal │  │    Cancelar     │ │
│  └──────────────────┘  └─────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```
''' if wireframe_format == 'ascii' else '''
**Tela:** [nome real da tela]

```plantuml
@startsalt
{+
  Titulo da Tela
  ==
  Nome Completo    | "                    "
  Email            | "                    "
  Senha            | "                    "
  ==
  [   Confirmar   ] | [  Cancelar  ]
}
@endsalt
```

**REGRAS OBRIGATÓRIAS para blocos plantuml Salt (violação causa crash no servidor):**
- NUNCA use strings vazias `""` ou com 1 único caractere `"x"`
- NUNCA use `()` radio buttons nem `[]` checkboxes dentro de Salt
- NUNCA use `^dropdown^` — use apenas labels de texto simples
- NUNCA coloque `|` ou `{` dentro de strings entre aspas
- Strings de input DEVEM ter mínimo 10 espaços: `"          "`
- Use `{+` para borda visível, `==` para separador horizontal
- Botões: `[  Label  ]` com pelo menos 2 espaços de cada lado
- Labels de campo: texto simples SEM aspas, seguido de `|` e o campo
''') + '''

[CONTINUAR COM TODOS OS CASOS DE USO — MÍNIMO 10 — CADA UM COMPLETAMENTE DETALHADO — SEM RESUMOS — SEM ABREVIAÇÕES]
''' if include_use_cases else ''}

---

## 6. Modelo de Dados Conceitual
{f'''
### 6.1 Entidades Principais
Listar e descrever cada entidade do sistema.

### 6.2 Relacionamentos
Descrever relacionamentos entre entidades.

### 6.3 Atributos Principais
Para cada entidade, listar atributos-chave e seus tipos.

### 6.4 Regras de Integridade
Constraints e validações importantes.
''' if include_data_model else ''}

---

## 7. Interfaces do Sistema

### 7.1 Interfaces de Usuário
Descrição das principais telas e fluxos de navegação.

### 7.2 Interfaces de Hardware
[Se aplicável] Integração com hardware específico.

### 7.3 Interfaces de Software
APIs e integrações com sistemas externos.

### 7.4 Interfaces de Comunicação
Protocolos e padrões de comunicação.

---

## 8. Regras de Negócio
{f'''
Para cada regra de negócio identificada:

**RN-XXX: [Nome da Regra]**
- **Descrição:** [Regra detalhada]
- **Condições:** [Quando se aplica]
- **Ações:** [O que deve acontecer]
- **Validações:** [Verificações necessárias]
- **Requisitos Relacionados:** [RF-XXX]

[Repetir para todas as regras de negócio]
''' if include_business_rules else ''}

---

## 9. Fluxos de Trabalho

### 9.1 Processos Principais
Descrição dos principais fluxos de trabalho do sistema.

### 9.2 Interações entre Componentes
Como diferentes partes do sistema se comunicam.

### 9.3 Sequências Críticas
Fluxos que requerem atenção especial.

---

## 10. Análise de Arquitetura Preliminar

### 10.1 Componentes e Serviços Necessários
Identificação de componentes principais do sistema.

### 10.2 Padrões de Interação
Como os componentes devem interagir entre si.

### 10.3 Integrações Externas
Sistemas externos e pontos de integração.

### 10.4 Considerações de Performance
Requisitos de performance e estratégias de otimização.

### 10.5 Considerações de Segurança
Aspectos de segurança da arquitetura.

### 10.6 Considerações de Escalabilidade
Como o sistema deve escalar.

### 10.7 Tecnologias Recomendadas
Frameworks, linguagens e ferramentas sugeridas.

---

## 11. Controle de Qualidade

### 11.1 Critérios de Aceitação Gerais
Critérios para considerar o sistema completo.

### 11.2 Estratégia de Testes
Abordagem de testes para validação.

### 11.3 Riscos Identificados
Riscos técnicos e de negócio.

### 11.4 Complexidades Previstas
Áreas que podem apresentar desafios.

---

## 12. Glossário
{f'''
Lista alfabética de termos técnicos e de domínio:

**[Termo]:** [Definição clara e concisa]

[Repetir para todos os termos importantes]
''' if include_glossary else ''}

---

## 13. Rastreabilidade

### 13.1 Matriz de Rastreabilidade
Tabela relacionando requisitos originais com elementos desta especificação:

| Requisito Original | Seção Especificação | RF | UC | RN |
|--------------------|---------------------|----|----|-----|
| [ID Requisito]     | [Seção X.Y]        | RF-XXX | UC-XXX | RN-XXX |

---

## 14. Apêndices

### 14.1 Histórico de Versões
| Versão | Data | Descrição | Autor |
|--------|------|-----------|-------|
| 1.0 | {requirements_created_at} | Versão inicial baseada em Requisitos v{requirements_version} | Sistema |

### 14.2 Aprovações
[Seção para registrar aprovações futuras]

---
```

## ⚠️ INSTRUÇÕES CRÍTICAS DE EXECUÇÃO - LEIA COM ATENÇÃO

### OBRIGATÓRIO: TODAS AS 14 SEÇÕES
O documento DEVE conter EXATAMENTE estas 14 seções numeradas:
1. Introdução (1.1-1.4)
2. Visão Geral do Sistema (2.1-2.5)
3. Requisitos Funcionais Detalhados
4. Requisitos Não-Funcionais (4.1-4.5)
5. Casos de Uso (MÍNIMO 10 UCs detalhados)
6. Modelo de Dados Conceitual
7. Interfaces do Sistema
8. Regras de Negócio (RN-XXX)
9. Fluxos de Trabalho
10. Análise de Arquitetura Preliminar
11. Controle de Qualidade
12. Glossário
13. Rastreabilidade (Matriz obrigatória)
14. Apêndices

**SE QUALQUER SEÇÃO ESTIVER FALTANDO, O DOCUMENTO SERÁ REJEITADO.**

### REGRAS DE EXECUÇÃO

1. **PRIORIDADE ABSOLUTA:** O Documento de Requisitos é a FONTE PRIMÁRIA. TODO requisito funcional mencionado lá DEVE estar refletido nesta especificação.

2. **RASTREABILIDADE:** Cada funcionalidade especificada DEVE ter rastreamento claro para o requisito original.

3. **RESOLUÇÃO DE CONFLITOS:** Se houver inconsistências entre documentos complementares e requisitos, os REQUISITOS têm precedência absoluta.

4. **COMPLETUDE TOTAL:**
   - TODOS os requisitos funcionais documentados
   - MÍNIMO 10 casos de uso COMPLETAMENTE detalhados — tabela, fluxo principal COMPLETO, alternativos, exceções e wireframe
   - TODAS as regras de negócio identificadas
   - Matriz de rastreabilidade COMPLETA

5. **CONSISTÊNCIA:** Verifique que não há contradições internas no documento.

6. **CRITÉRIOS MENSURÁVEIS:** Todos os critérios de aceitação devem ser testáveis e verificáveis.

7. **FORMATO:** Retorne SOMENTE o documento em Markdown. Não inclua comentários, análises ou introduções fora do documento.

8. **EXTENSÃO:** Gere o documento COMPLETO. NÃO truncar, NÃO resumir, NÃO pular seções. Documentos longos são ESPERADOS e CORRETOS.

9. **CASOS DE USO — REGRA DE OURO:** NUNCA escreva frases como "UC-003 a UC-010 seguem a mesma estrutura", "Por questões de espaço", "serão resumidos", "seguem o padrão do UC anterior". CADA UC deve ser 100% escrito do zero com todos os detalhes. Se o documento ficar com 20, 30 ou 50 páginas, isso é CORRETO.

## CHECKLIST FINAL - VERIFIQUE ANTES DE RETORNAR:
☐ Seção 1 (Introdução) presente?
☐ Seção 2 (Visão Geral) presente?
☐ Seção 3 (RFs) presente e TODOS os RFs documentados?
☐ Seção 4 (RNFs) presente?
☐ Seção 5 (Casos de Uso) presente com MÍNIMO 10 UCs COMPLETAMENTE DETALHADOS (sem resumos)?
☐ Seção 6 (Modelo de Dados) presente?
☐ Seção 7 (Interfaces) presente?
☐ Seção 8 (Regras de Negócio RN-XXX) presente?
☐ Seção 9 (Fluxos de Trabalho) presente?
☐ Seção 10 (Arquitetura) presente?
☐ Seção 11 (Qualidade) presente?
☐ Seção 12 (Glossário) presente?
☐ Seção 13 (Rastreabilidade) presente com MATRIZ?
☐ Seção 14 (Apêndices) presente?

## FORMATO DE SAÍDA

- Comece DIRETAMENTE com o cabeçalho: "# Especificação Funcional - {project_name}"
- NÃO inclua análises ou comentários antes/depois do documento
- Mantenha formatação markdown consistente
- Use numeração sequencial: ## 1., ## 2., ... ## 14.
- Inclua tabelas e listas quando apropriado

Gere agora a especificação funcional COMPLETA com TODAS as 14 seções:
"""

    return prompt
