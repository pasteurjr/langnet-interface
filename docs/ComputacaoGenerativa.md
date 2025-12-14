# Computação Generativa aplicada a Sistemas de Agentes

Este documento consolida duas partes:

1. O texto base com princípios e regras de Computação Generativa aplicado a sistemas de agentes LLM (reproduzido integralmente abaixo).
2. Instruções detalhadas para implementar esses princípios neste repositório, conectando-os aos artefatos já existentes (por exemplo, `docs/requisitosv0.2.txt`).

A intenção é oferecer um guia operacional para criar um runtime controlado, auditável e testável, alinhando agentes e pipelines às práticas de guardrails, observabilidade e versionamento de comportamento.

---

## Parte 1 — Texto base (reproduzido)

### 1. OBJETIVO DO DOCUMENTO

Este documento instrui a criação de um **Runtime de Computação Generativa** para sistemas de agentes baseados em LLMs.

O objetivo é **aumentar precisão, confiabilidade, rastreabilidade e controle**, substituindo abordagens baseadas em:
- prompts longos
- respostas diretas
- agentes autônomos não supervisionados

por uma **arquitetura programável**, modular e testável.

### 2. PRINCÍPIO FUNDAMENTAL (OBRIGATÓRIO)

#### Regra nº 1
**Nunca permitir que um LLM responda diretamente ao usuário em uma única chamada.**

Toda resposta deve ser resultado de:
- múltiplas etapas
- validações intermediárias
- guardrails
- retries
- fallback determinístico

LLMs devem ser tratados como **primitivas computacionais**, não como oráculos.

### 3. DEFINIÇÃO DE COMPUTAÇÃO GENERATIVA

Computação Generativa é uma abordagem onde:

- LLMs são funções controladas
- Prompts são instruções atômicas
- A lógica está no runtime, não no texto
- O comportamento é verificável
- O erro é detectável e corrigível
- O sistema é observável e reproduzível

### 4. ARQUITETURA GERAL DO SISTEMA

Implemente obrigatoriamente as seguintes camadas:

#### Camada 1 — Runtime de Orquestração
Responsável por:
- definir a sequência de etapas (steps)
- controlar fluxo (if/else)
- executar retries
- aplicar fallback
- registrar logs e metadados

#### Camada 2 — Agentes Especialistas
Cada agente executa **uma única função clara**.
Nenhum agente decide o fluxo geral.

#### Camada 3 — Guardrails / Guardiões
Modelos ou validadores que:
- verificam factualidade
- verificam aderência ao contexto
- verificam formato
- verificam conformidade e políticas

#### Camada 4 — Ferramentas Determinísticas
Sempre preferir:
- RAG
- banco de dados
- cálculos
- regras de negócio
em vez de “memória” do LLM.

#### Camada 5 — Observabilidade e Testes
- logs por etapa
- versionamento de comportamento
- testes comportamentais
- dataset de regressão

### 5. PAPÉIS DE AGENTES (OBRIGATÓRIOS)

Implemente pelo menos os seguintes agentes:

1. **RouterAgent**
   - Classifica a intenção da entrada
   - Decide qual pipeline executar

2. **EntityExtractorAgent**
   - Extrai entidades, parâmetros, variáveis

3. **RetrieverAgent**
   - Busca contexto via RAG, banco ou ferramentas

4. **ComposerAgent**
   - Gera rascunho da resposta SOMENTE com base no contexto

5. **VerifierAgent (Guardião)**
   - Verifica se cada afirmação é suportada pelo contexto

6. **ComplianceAgent (Guardião)**
   - Verifica políticas, regras, escopo, segurança

7. **FormatterAgent**
   - Normaliza estilo, idioma, estrutura
   - Remove primeira pessoa se exigido

Nenhum agente pode pular validações.

### 6. PIPELINE PADRÃO (MODELO CANÔNICO)

Toda resposta deve seguir esta sequência mínima:

1. Classificação de intenção
2. Extração de entidades
3. Recuperação de contexto
4. Composição do rascunho
5. Validação factual
6. Reparação (se necessário)
7. Validação de conformidade
8. Formatação final
9. Entrega ao usuário

### 7. DECOMPOSIÇÃO EM STEPS ATÔMICOS

Cada step deve:
- ter objetivo único
- ter entradas explícitas
- gerar saída estruturada (JSON)
- ser validado

Exemplo:
- ❌ "Responda tudo"
- ✅ "Classifique a intenção"
- ✅ "Extraia entidades"
- ✅ "Verifique se há extrapolação"

### 8. SCHEMA-FIRST (OBRIGATÓRIO)

Toda saída de agente deve seguir schema.

Exemplos de campos:
- intent
- entities
- context_chunks
- draft
- issues
- compliance_ok
- final_answer

Nenhuma string livre é aceita sem schema.

### 9. GUARDRAILS (VALIDAÇÃO EM CAMADAS)

Implemente validação em série:

1. Validação de formato (schema)
2. Validação de grounding (contexto)
3. Validação de escopo
4. Validação de conformidade

Se qualquer validação falhar:
- executar retry com instruções mais restritivas
- ou redirecionar para agente de reparo

### 10. RETRY CONTROLADO (NÃO INGÊNUO)

Retries devem mudar estratégia, por exemplo:
- tentativa 1: resposta normal
- tentativa 2: resposta somente com trechos do contexto
- tentativa 3: declarar explicitamente limitações

Nunca repetir exatamente o mesmo prompt.

### 11. FALLBACK DETERMINÍSTICO

Se todas as tentativas falharem:
- usar template determinístico
- ou retornar resposta parcial com aviso claro
- nunca inventar

### 12. OBSERVABILIDADE (OBRIGATÓRIA)

Registrar para cada step:
- id do step
- agente executado
- tempo de execução
- número de tentativas
- resultado (ok/falha)
- issues detectadas
- campos produzidos

O sistema deve gerar um `trace` completo.

### 13. TESTES COMPORTAMENTAIS

Implemente testes automáticos para verificar:

- saída segue schema
- não há primeira pessoa (se exigido)
- afirmações têm suporte no contexto
- lacunas são explicitamente declaradas
- estilo e idioma corretos

Exemplos de asserções:
- “Se não houver contexto suficiente, o sistema deve declarar limitação.”
- “Nenhuma resposta pode conter extrapolações.”

### 14. VERSIONAMENTO DE COMPORTAMENTO

Versionar:
- pipelines
- prompts atômicos
- regras de validação
- critérios de sucesso

Mudanças devem passar por regressão.

### 15. PRINCÍPIOS FINAIS (NÃO NEGOCIÁVEIS)

- O runtime manda, o LLM obedece
- Precisão vem de controle, não de criatividade
- LLMs erram; sistemas corrigem
- Engenharia > prompt engineering
- Todo comportamento deve ser auditável
- Nenhuma resposta sem validação

### 16. RESULTADO ESPERADO

Ao final da implementação, o sistema deve:

- produzir respostas reproduzíveis
- reduzir alucinação drasticamente
- falhar de forma segura
- explicar seus próprios limites
- operar como infraestrutura de software

---

## Parte 2 — Instruções para implementar neste repositório

Os itens abaixo detalham como aplicar o texto base nos artefatos e requisitos atuais, especialmente em `docs/requisitosv0.2.txt`. Cada ação prioriza execução programável, observável e testável.

### 2.1 Criar um runtime de orquestração multi-step com guardrails
- **Objetivo:** Transformar o pipeline canônico (Router → EntityExtractor → Retriever → Composer → Verifier → Compliance → Formatter) em um runtime explícito (por exemplo, módulo em `backend` ou `framework`) que nunca permita resposta direta em uma única chamada.
- **Passos sugeridos:**
  1. Modelar um `Orchestrator` que encadeie steps atômicos com schemas fixos de entrada/saída e suporte a condicionais simples (if/else) para reparo e fallback.
  2. Implementar controle de retries com estratégias diferenciadas por tentativa (normal → usar apenas trechos do contexto → declarar limitações), registrando número de tentativas e motivo de retry.
  3. Adicionar fallback determinístico para quando todas as tentativas falharem (templates claros, respostas parciais com aviso de limitação, jamais inventando conteúdo).
  4. Registrar por step: id, agente, tempo, tentativas, resultado, issues e campos produzidos. Integrar com Langfuse/tracing já previsto nos requisitos para manter auditabilidade.
  5. Documentar o fluxo no `README.md` e em `docs/requisitosv0.2.txt`, destacando que nenhum agente decide o fluxo geral e que o runtime é a autoridade.
- **Resultado esperado:** Pipeline reproduzível, com logs completos e comportamento versionado (incluindo prompts e regras), apto a regressão e análise de falhas.

### 2.2 Refatorar agentes e tarefas para abordagem schema-first e validação em série
- **Objetivo:** Eliminar saídas livres. Toda interação de agentes deve seguir schemas verificáveis, permitindo validações de formato, grounding e conformidade antes de avançar no pipeline.
- **Passos sugeridos:**
  1. Definir JSON Schemas (ou Zod/TypeBox) para agentes e tarefas, incluindo campos como `intent`, `entities`, `context_chunks`, `draft`, `issues`, `compliance_ok`, `final_answer`, além de inputs esperados, ferramentas autorizadas e critérios de aceitação.
  2. Atualizar `agents.yaml` e `tasks.yaml` para aderir aos schemas, evitando descrições livres. Incluir metadados de políticas de validação (ex.: obrigatoriedade de grounding, idioma, ausência de primeira pessoa quando aplicável).
  3. Implementar validadores que rejeitem saídas fora do schema e acionem retries ou agente de reparo. Cada validação deve ser encadeada: formato → grounding → escopo → conformidade.
  4. Garantir que cada agente execute somente uma função clara, sem decidir fluxo; o runtime controla a progressão.
- **Resultado esperado:** Dados estruturados, verificáveis e rastreáveis, com prevenção de extrapolações e aderência ao contexto antes de compor a resposta final.

### 2.3 Instrumentar observabilidade e testes comportamentais centrados no pipeline
- **Objetivo:** Tornar o sistema auditável e seguro por meio de tracing detalhado e testes automatizados que cobrem formato, grounding e conformidade.
- **Passos sugeridos:**
  1. Instrumentar cada step com spans de tracing (ex.: Langfuse) capturando prompts, respostas, retries, fallbacks e decisões de fluxo.
  2. Criar suíte de testes que simule intents e verifique: aderência ao schema, suporte factual ao contexto (RAG/dados), mensagens de limitação quando faltar grounding, conformidade de políticas e formatação final (idioma/estilo, ausência de primeira pessoa quando necessário).
  3. Manter datasets de regressão comportamental e versionar configurações de pipelines, prompts e critérios de sucesso para facilitar comparação entre versões.
  4. Documentar como executar os testes e interpretar traces, priorizando integração com requisitos já descritos em `docs/requisitosv0.2.txt`.
- **Resultado esperado:** Observabilidade granular e cobertura de testes que reduzam alucinações, garantam segurança de respostas e permitam evolução controlada do runtime.

### 2.4 Alinhamento com requisitos existentes
- Revisar `docs/requisitosv0.2.txt` para conectar cada item acima aos requisitos já capturados (RAG, integração, monitoramento, etc.).
- Garantir que os novos fluxos e guardrails sejam mencionados nos documentos de referência (ex.: `quick-reference.md`, `gap-analysis-report.md`) para manter consistência e facilitar onboarding.

### 2.5 Princípios de entrega
- Nenhuma resposta ao usuário deve bypassar validações ou pular etapas.
- Toda decisão de fluxo pertence ao runtime, não aos agentes.
- Priorizar ferramentas determinísticas (RAG, bancos, regras) sempre que possível.
- Registrar comportamentos e mudanças para auditoria e regressão.
- Em falhas, preferir respostas parciais ou templates determinísticos com avisos claros, nunca inventar.

