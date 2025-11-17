# Documento de Requisitos
## {project_name}

---

**Versão:** 1.0
**Data:** {generation_date}
**Status:** {document_status}

---

## 1. Informações do Projeto

### 1.1 Visão Geral
**Nome do Projeto:** {project_name}

**Descrição:**
{project_description}

**Objetivo:**
{project_objectives}

### 1.2 Contexto e Justificativa
{project_context}

### 1.3 Escopo
**Inclui:**
{scope_includes}

**Exclui:**
{scope_excludes}

---

## 2. Fontes de Informação

### 2.1 Documentos Analisados

| ID | Nome do Documento | Tipo | Data | Autor | Caminho/URL |
|----|-------------------|------|------|-------|-------------|
{documents_table}

### 2.2 Estatísticas de Análise

- **Total de documentos analisados:** {total_documents}
- **Total de páginas processadas:** {total_pages}
- **Total de palavras analisadas:** {total_words}
- **Data da análise:** {analysis_date}
- **Tempo de processamento:** {processing_time}

---

## 3. Requisitos Funcionais (FR)

### 3.1 Requisitos Funcionais por Categoria

{functional_requirements_by_category}

### 3.2 Lista Completa de Requisitos Funcionais

{functional_requirements_list}

**Exemplo de formato:**

**[FR-001]** Nome do Requisito
**Descrição:** Descrição detalhada do requisito funcional.
**Prioridade:** Alta | Média | Baixa
**Atores Envolvidos:** Lista de atores
**Fonte:** Seção X.Y do documento Z
**Dependências:** FR-002, FR-005
**Critérios de Aceitação:**
- Critério 1
- Critério 2

---

## 4. Requisitos Não-Funcionais (NFR)

### 4.1 Requisitos por Categoria

#### 4.1.1 Performance
{nfr_performance}

#### 4.1.2 Segurança
{nfr_security}

#### 4.1.3 Usabilidade
{nfr_usability}

#### 4.1.4 Confiabilidade
{nfr_reliability}

#### 4.1.5 Escalabilidade
{nfr_scalability}

#### 4.1.6 Manutenibilidade
{nfr_maintainability}

### 4.2 Lista Completa de Requisitos Não-Funcionais

{non_functional_requirements_list}

**Exemplo de formato:**

**[NFR-001]** Nome do Requisito
**Descrição:** Descrição detalhada do requisito não-funcional.
**Categoria:** Performance | Segurança | Usabilidade | Confiabilidade | Escalabilidade | Manutenibilidade
**Métrica Mensurável:** Definição clara de como medir (ex: tempo de resposta < 200ms)
**Prioridade:** Alta | Média | Baixa
**Critérios de Aceitação:**
- Critério mensurável 1
- Critério mensurável 2

---

## 5. Regras de Negócio (BR)

### 5.1 Regras de Negócio por Domínio

{business_rules_by_domain}

### 5.2 Lista Completa de Regras de Negócio

{business_rules_list}

**Exemplo de formato:**

**[BR-001]** Nome da Regra
**Descrição:** Descrição da regra de negócio.
**Condição:** Quando/Se [condição]
**Ação:** Então [ação resultante]
**Entidades Afetadas:** Lista de entidades
**Justificativa:** Razão de negócio para esta regra
**Exceções:** Casos excepcionais, se houver

---

## 6. Atores e Stakeholders

### 6.1 Atores do Sistema

{actors_list}

**Exemplo de formato:**

**[ACTOR-001]** Nome do Ator
**Tipo:** Usuário | Sistema | Serviço Externo
**Papel:** Descrição do papel
**Responsabilidades:**
- Responsabilidade 1
- Responsabilidade 2

**Pontos de Interação:**
- Interação com funcionalidade X
- Interação com funcionalidade Y

**Requisitos Relacionados:** FR-001, FR-003, NFR-002

---

## 7. Entidades e Relacionamentos

### 7.1 Modelo Conceitual de Dados

```mermaid
erDiagram
{entity_relationship_diagram}
```

### 7.2 Descrição das Entidades

{entities_description}

**Exemplo de formato:**

**[ENTITY-001]** Nome da Entidade
**Descrição:** Descrição da entidade no domínio.

**Atributos:**
| Atributo | Tipo | Obrigatório | Descrição | Restrições |
|----------|------|-------------|-----------|------------|
{entity_attributes_table}

**Relacionamentos:**
- Relacionamento com ENTITY-002 (1-N): Descrição
- Relacionamento com ENTITY-003 (N-N): Descrição

**Regras de Negócio Aplicáveis:** BR-001, BR-005

---

## 8. Fluxos de Trabalho Identificados

### 8.1 Visão Geral dos Fluxos

{workflows_overview}

### 8.2 Fluxos Detalhados

{workflows_detailed}

**Exemplo de formato:**

**[WORKFLOW-001]** Nome do Fluxo
**Descrição:** Descrição do fluxo de trabalho.
**Gatilho/Trigger:** O que inicia este fluxo
**Atores Envolvidos:** ACTOR-001, ACTOR-003

**Fluxo Principal:**

```mermaid
sequenceDiagram
{workflow_sequence_diagram}
```

**Passos:**
1. **Passo 1:** Descrição
   - Ator: ACTOR-001
   - Ação: Descrição da ação
   - Sistema: Resposta do sistema

2. **Passo 2:** Descrição (Ponto de Decisão)
   - Condição A → Ir para Passo 3
   - Condição B → Ir para Passo 5

**Fluxos Alternativos:**
- **Alt-1:** Descrição do fluxo alternativo
- **Alt-2:** Descrição de outro fluxo alternativo

**Fluxos de Exceção:**
- **Exc-1:** Tratamento de erro/exceção

**Estados Finais:**
- Sucesso: Descrição do estado final de sucesso
- Falha: Descrição dos estados finais de falha

**Requisitos Relacionados:** FR-010, FR-011, BR-003

---

## 9. Glossário de Termos do Domínio

### 9.1 Termos e Definições

{glossary_table}

**Formato:**

| Termo | Definição | Contexto de Uso | Sinônimos | Termos Relacionados |
|-------|-----------|-----------------|-----------|---------------------|
{glossary_entries}

### 9.2 Abreviações e Acrônimos

{abbreviations_table}

---

## 10. Verificações Complementares

### 10.1 Consistência entre Documentos

{consistency_analysis}

**Conflitos Identificados:**

{conflicts_table}

**Exemplo de formato:**

| ID | Conflito | Documentos Afetados | Severidade | Resolução Sugerida |
|----|----------|---------------------|------------|---------------------|
{conflicts_entries}

### 10.2 Ambiguidades Detectadas

{ambiguities_analysis}

**Lista de Ambiguidades:**

{ambiguities_list}

**Exemplo de formato:**

**[AMB-001]**
**Texto Ambíguo:** "{ambiguous_text}"
**Localização:** Documento X, Seção Y
**Razão:** Por que é ambíguo
**Pergunta de Clarificação:** Pergunta específica para o stakeholder
**Requisitos Afetados:** FR-005, NFR-002

### 10.3 Questões para Clarificação

{clarification_questions}

**Prioridade Alta:**
{high_priority_questions}

**Prioridade Média:**
{medium_priority_questions}

**Prioridade Baixa:**
{low_priority_questions}

**Formato de questão:**

**[Q-001]** [Prioridade: Alta]
**Questão:** Pergunta específica para o stakeholder
**Contexto:** Contexto da pergunta
**Requisitos Afetados:** FR-001, BR-003
**Impacto se não respondida:** Descrição do impacto

---

## 11. Análise de Completude

### 11.1 Avaliação de Suficiência

**Score de Completude Geral:** {completeness_score}/100

**Breakdown por Categoria:**
- Requisitos Funcionais: {fr_completeness}/100
- Requisitos Não-Funcionais: {nfr_completeness}/100
- Regras de Negócio: {br_completeness}/100
- Atores e Stakeholders: {actors_completeness}/100
- Entidades e Dados: {entities_completeness}/100
- Fluxos de Trabalho: {workflows_completeness}/100

### 11.2 Gaps Críticos Identificados

{critical_gaps}

**Exemplo de formato:**

**[GAP-001]** [Severidade: Crítica]
**Área:** Categoria funcional afetada
**Gap Identificado:** Descrição do que está faltando
**Justificativa:** Por que isso é crítico
**Impacto:** Impacto no projeto se não resolvido
**Requisitos Afetados:** Lista de requisitos impactados
**Informações Necessárias:** O que precisa ser fornecido

### 11.3 Informações Complementares Necessárias

{information_requests}

**Lista de Solicitações:**

{information_requests_list}

**Formato:**

**[INFO-REQ-001]** [Prioridade: Alta]
**Informação Solicitada:** Descrição específica
**Razão:** Por que é necessário
**Para completar:** Requisitos ou áreas que serão completadas
**Fonte Sugerida:** Quem pode fornecer (stakeholder, documento, sistema)

### 11.4 Cobertura de Requisitos Essenciais

{essential_coverage_analysis}

**Checklist por Tipo de Aplicação:** {application_type}

| Categoria Essencial | Status | Cobertura | Observações |
|---------------------|--------|-----------|-------------|
{essential_coverage_table}

---

## 12. Priorização e Dependências

### 12.1 Matriz de Priorização

```mermaid
quadrantChart
    title Matriz de Impacto vs Esforço
    x-axis Baixo Esforço --> Alto Esforço
    y-axis Baixo Impacto --> Alto Impacto
    quadrant-1 Fazer Primeiro
    quadrant-2 Planejar Cuidadosamente
    quadrant-3 Fazer Depois
    quadrant-4 Reavaliar Necessidade
{prioritization_chart_data}
```

### 12.2 Análise de Dependências

```mermaid
graph TD
{dependencies_graph}
```

### 12.3 Caminho Crítico

{critical_path_analysis}

**Requisitos no Caminho Crítico:**
{critical_requirements_list}

---

## 13. Pesquisa Complementar (Web Research)

### 13.1 Melhores Práticas da Indústria

{industry_best_practices}

### 13.2 Padrões e Standards Recomendados

{recommended_standards}

**Formato:**

**[STD-001]** Nome do Padrão
**Categoria:** Security | Performance | Accessibility | Compliance
**Descrição:** Descrição do padrão
**Aplicabilidade:** Como se aplica ao projeto
**Referência:** URL oficial
**Requisitos Relacionados:** NFR-001, NFR-003

### 13.3 Tecnologias Sugeridas

{suggested_technologies}

**Formato:**

**[TECH-001]** Nome da Tecnologia
**Caso de Uso:** Para que será usada
**Maturidade:** Madura | Emergente | Experimental
**Documentação:** URL
**Prós:** Lista de vantagens
**Contras:** Lista de desvantagens
**Requisitos Relacionados:** FR-010, NFR-005

### 13.4 Checklist de Compliance

{compliance_checklist}

**Formato:**

| Regulação | Requisito de Compliance | Status | Requisitos Relacionados | Ações Necessárias |
|-----------|------------------------|--------|------------------------|-------------------|
{compliance_entries}

### 13.5 Requisitos Potencialmente Faltantes (descobertos via pesquisa)

{missing_requirements_discovered}

---

## 14. Scores de Qualidade

### 14.1 Métricas de Qualidade Geral

| Métrica | Score | Status | Observações |
|---------|-------|--------|-------------|
| **Completude** | {completeness_score}/100 | {completeness_status} | {completeness_notes} |
| **Clareza** | {clarity_score}/100 | {clarity_status} | {clarity_notes} |
| **Consistência** | {consistency_score}/100 | {consistency_status} | {consistency_notes} |
| **Testabilidade** | {testability_score}/100 | {testability_status} | {testability_notes} |
| **Rastreabilidade** | {traceability_score}/100 | {traceability_status} | {traceability_notes} |

**Legenda de Status:**
- ✅ Excelente (90-100)
- ⚠️ Bom (70-89)
- ⚠️ Requer Atenção (50-69)
- ❌ Crítico (<50)

### 14.2 Issues Encontradas

{issues_summary}

**Issues por Severidade:**
- Críticas: {critical_issues_count}
- Altas: {high_issues_count}
- Médias: {medium_issues_count}
- Baixas: {low_issues_count}

### 14.3 Lista Detalhada de Issues

{issues_detailed_list}

**Formato:**

**[ISSUE-001]** [Severidade: {severity}]
**Tipo:** Ambiguidade | Conflito | Falta de Testabilidade | Falta de Rastreabilidade | Outro
**Descrição:** Descrição do problema
**Requisito Afetado:** FR-005
**Recomendação:** Sugestão específica de correção
**Exemplo:** Exemplo de como corrigir, se aplicável

---

## 15. Sugestões de Melhoria

### 15.1 Recomendações Gerais

{general_recommendations}

### 15.2 Melhorias por Categoria

**Requisitos Funcionais:**
{fr_improvements}

**Requisitos Não-Funcionais:**
{nfr_improvements}

**Regras de Negócio:**
{br_improvements}

**Documentação:**
{documentation_improvements}

---

## 16. Próximos Passos

### 16.1 Ações Imediatas Requeridas

{immediate_actions}

### 16.2 Validações Necessárias

{validations_needed}

### 16.3 Preparação para Especificação Funcional

{spec_preparation}

**Checklist para Fase 2.2 (Especificação Funcional):**
- [ ] Todos os gaps críticos foram resolvidos
- [ ] Questões de alta prioridade foram respondidas
- [ ] Conflitos foram resolvidos
- [ ] Score de completude ≥ 70%
- [ ] Score de clareza ≥ 70%
- [ ] Score de consistência ≥ 80%

---

## 17. Rastreabilidade

### 17.1 Matriz de Rastreabilidade

| Documento Fonte | Seção | Requisito(s) Extraído(s) | Tipo | Prioridade |
|-----------------|-------|--------------------------|------|------------|
{traceability_matrix}

### 17.2 Mapa de Cobertura

```mermaid
mindmap
  root((Requisitos))
{coverage_mindmap}
```

---

## 18. Metadados do Documento

**Gerado por:** LangNet Multi-Agent System
**Framework:** {framework_version}
**Agentes Envolvidos:**
- document_analyzer_agent
- requirements_engineer_agent
- web_researcher_agent
- quality_assurance_agent

**Workflow Executado:**
1. analyze_document
2. extract_requirements
3. research_additional_info
4. validate_requirements

**Tempo Total de Processamento:** {total_processing_time}

**Configurações de Geração:**
- LLM Provider: {llm_provider}
- Model: {llm_model}
- Web Research: {web_research_enabled}
- Additional Instructions: {has_additional_instructions}

---

## 19. Controle de Versões

| Versão | Data | Autor | Alterações | Status |
|--------|------|-------|------------|--------|
| 1.0 | {generation_date} | LangNet System | Versão inicial gerada automaticamente | {document_status} |
{version_history}

---

## 20. Aprovações

| Papel | Nome | Data | Assinatura | Status |
|-------|------|------|------------|--------|
| Product Owner | | | | Pendente |
| Tech Lead | | | | Pendente |
| QA Lead | | | | Pendente |
| Stakeholder | | | | Pendente |

---

**Fim do Documento de Requisitos**

*Este documento foi gerado automaticamente pelo LangNet Multi-Agent System baseado na análise de documentação fornecida e pesquisa complementar. Requer revisão e aprovação humana antes de prosseguir para a fase de Especificação Funcional.*
