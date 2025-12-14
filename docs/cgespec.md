# Roteiro para alinhar a geração do documento de especificação funcional à Computação Generativa

## 1. Objetivo
Tornar a produção do documento de especificação funcional (ex.: especificação de casos de uso, user stories, fluxos detalhados, regras de negócio e integrações) aderente ao modelo de Computação Generativa: execução multi-step controlada, schemas explícitos, guardrails, retries diferenciados, observabilidade e fallbacks determinísticos. Este roteiro descreve o que ajustar em prompts, YAML de agentes/tarefas e validadores para que a especificação seja precisa, rastreável e auditável.

## 2. Escopo e premissas
- Abrange agentes e pipelines que coletam insumos (requisitos aprovados, diagramas, petri nets, protótipos) e produzem o documento de especificação funcional consolidado.
- Nenhum agente gera a versão final em chamada única: seguir o pipeline canônico Router → EntityExtractor → Retriever → Composer → Verifier → Compliance → Formatter.
- Toda saída intermediária e final deve respeitar schemas definidos e passar por validações de formato, grounding e conformidade antes de avançar.

## 3. Papéis obrigatórios (foco em especificação)
- **RouterAgent**: classifica intenção (criar/atualizar/validar especificação) e seleciona pipeline adequado (ex.: geração inicial, sincronização com requisitos, validação de consistência com diagramas). 
- **EntityExtractorAgent**: extrai módulos, atores, cenários, eventos, pré/pós-condições, regras de transição, integrações, APIs, dados, restrições e lacunas.
- **RetrieverAgent**: faz RAG sobre requisitos aprovados, petri nets, diagramas de sequência/atividade, protótipos e histórico de versões da especificação; devolve `context_chunks` com fonte e localização.
- **ComposerAgent**: gera rascunho da especificação **somente** com base em `context_chunks` e entidades; monta seções como visão geral, arquitetura lógica, casos de uso, fluxos de eventos, regras de negócio, contratos de API, modelos de dados, requisitos de interface, estados e exceções.
- **VerifierAgent**: valida grounding de cada cenário/requisito de especificação, checando se os `context_ids` suportam fluxos, regras e contratos descritos; marca `issues` quando houver extrapolação ou inconsistência com requisitos ou diagramas.
- **ComplianceAgent**: verifica idioma/estilo, políticas de segurança (sem dados sensíveis não autorizados), aderência a restrições de integração e consistência de versões; exige que lacunas estejam declaradas.
- **FormatterAgent**: normaliza numeração, nomenclatura de atores/sistemas, modelos de tabelas e seções; aplica fallback determinístico para relatórios parciais com avisos claros.

## 4. Pipeline mínimo para a especificação funcional
1. **Classificação**: identificar se a tarefa é criação, atualização incremental ou validação da especificação contra requisitos/diagramas.
2. **Extração de entidades**: mapear atores, serviços, contratos de API, eventos, estados, regras, dependências, exceções, entradas/saídas e métricas de sucesso.
3. **Recuperação de contexto (RAG)**: coletar trechos relevantes de requisitos aprovados, petri nets, diagramas, protótipos e versões anteriores; manter `context_ids` rastreáveis.
4. **Composição do rascunho**: estruturar o documento em seções numeradas com listas de casos de uso, user stories, fluxos principais/alternativos, regras de transição, contratos de API (método, path, payload, status), modelos de dados, regras de validação e estados.
5. **Validação factual**: verificar cada item da especificação contra `context_chunks`; sinalizar `unsupported`, `ambiguous`, `inconsistent_with_requirements` (quando divergir do documento de requisitos) e sugerir reparo ou solicitação de evidência adicional.
6. **Validação de conformidade**: checar idioma pt-BR, ausência de 1ª pessoa, aderência a templates de formatação, políticas de segurança e consistência com versões de requisitos/diagramas referenciadas.
7. **Formatação final + fallback**: gerar saída final; se restarem `issues`, produzir versão parcial com avisos, lista de lacunas e perguntas objetivas.

## 5. Schemas recomendados
- **Intent**: `{ "intent": "create|update|validate", "scope": "functional_spec", "targets": ["casos_de_uso", "apis", "fluxos", "estados"], "reference_versions": {"requisitos": "vX", "diagramas": "vY"} }`
- **Entities**: `{ "actors": [...], "systems": [...], "apis": [{"name": string, "method": string, "path": string}], "events": [...], "states": [...], "rules": [...], "data_models": [...], "exceptions": [...], "gaps": [...], "questions": [...] }`
- **Context chunks**: lista `{ "id": string, "source": "requisitos|petrinet|diagrama|protótipo|histórico", "location": string, "quote": string, "relevance": number }`
- **Draft**: `{ "sections": [{ "id": string, "title": string, "content": string, "items": [{ "iid": string, "type": "caso_de_uso|api|fluxo|regra|estado", "text": string, "context_ids": [...], "status": "supported|unsupported|gap", "links_requisitos": [...], "links_diagramas": [...] }] }], "open_questions": [...], "gaps": [...] }`
- **Issues (Verifier)**: `{ "unsupported": [...], "ambiguous": [...], "inconsistent_with_requirements": [...], "format": [...], "actions": ["retry_with_context", "request_additional_source", "remove_unsourced"] }`
- **Compliance**: `{ "compliance_ok": bool, "violations": [...], "language": "pt-BR", "first_person": false, "security": {"pii_ok": bool} }`
- **Final output**: `{ "status": "complete|partial|failed", "document": "...texto final...", "gaps": [...], "trace_id": "..." }`

## 6. Instruções para prompts dos agentes
- **Schema-first**: cada prompt deve exigir o schema de saída acima e rejeitar strings livres.
- **Retries diferenciados**:
  - Tentativa 1: usar todo contexto disponível; marcar lacunas quando faltarem evidências.
  - Tentativa 2: restringir texto a trechos citados (`context_ids` obrigatórios); remover ou marcar como `gap` qualquer item sem suporte.
  - Tentativa 3: fallback determinístico explicando limitações, solicitando fontes específicas (ex.: diagrama ou requisito faltante) e entregando versão parcial.
- **ComposerAgent**: instruir a não inventar fluxos, endpoints ou regras; qualquer ausência vira `gap` com pergunta objetiva.
- **VerifierAgent**: verificar cada item da especificação contra `context_ids` e contra o documento de requisitos; sinalizar divergências como `inconsistent_with_requirements` e propor ação (retry ou remoção).
- **ComplianceAgent**: checar idioma pt-BR, ausência de 1ª pessoa, aderência a templates de seção, políticas de segurança (dados sensíveis) e consistência de versões referenciadas.
- **FormatterAgent**: aplicar template fixo de especificação (sumário, visão geral, arquitetura, casos de uso, APIs, modelos de dados, fluxos, exceções, anexos). Em fallback, incluir seção “Limitações e Próximos Passos” com lista de gaps.

## 7. Instruções para YAML de agentes e tarefas
- **agents.yaml**: acrescentar para cada agente de especificação os campos `inputs`, `outputs`, `tools` autorizadas (RAG, validadores de schema, verificadores de consistência com requisitos/diagramas), `retry_policies` (estratégias 1–3), `fallbacks` (templates determinísticos) e `validation` (formato + grounding + conformidade + consistência com requisitos/diagramas). Habilitar `observability` com `trace_id` e `step_id`.
- **tasks.yaml**: definir pipelines específicos para criação, atualização e validação da especificação, com ordenação canônica dos agentes. Em cada task, declarar `expected_outputs`, `success_criteria` (ex.: nenhum item sem `context_id`, nenhuma divergência com requisitos sem ser marcada, idioma pt-BR, ausência de 1ª pessoa), `failure_actions` (retry estratégico, fallback parcial) e metadados de rastreabilidade (versão do prompt/pipeline, fontes usadas, `trace_id`).

## 8. Observabilidade e testes
- **Tracing**: spans por step com tempo, tentativas, prompts, respostas truncadas, `issues` e decisões de retry/fallback; integrar com Langfuse ou equivalente.
- **Testes comportamentais**: incluir casos que validem:
  - Conformidade de schema em todas as etapas.
  - Presença de `context_id` para cada item da especificação; itens sem suporte movidos para `gaps`.
  - Alinhamento com o documento de requisitos (nenhum `inconsistent_with_requirements` sem ação tomada).
  - Ausência de primeira pessoa e idioma pt-BR.
  - Fallback parcial quando não houver contexto suficiente, com perguntas objetivas.
- **Datasets de regressão**: manter conjunto de entradas (requisitos, diagramas, petri nets) e saídas esperadas (estrutura da especificação) para detectar regressões em composição/verificação/compliance.

## 9. Fallbacks determinísticos recomendados
- Se após retries houver `unsupported` ou `inconsistent_with_requirements`, mover o item para `gaps` e registrar pergunta para o solicitante ou analista.
- Quando faltar contexto (diagramas ou requisitos), gerar especificação parcial com placeholders, avisos explícitos e lista de documentos necessários.
- Nunca inventar endpoints, fluxos ou regras; preferir `status=partial` com rastreabilidade de lacunas.

## 10. Checklist de adoção
1. Atualizar prompts de Router/EntityExtractor/Retriever/Composer/Verifier/Compliance/Formatter com schemas e políticas de retry/fallback acima.
2. Revisar `agents.yaml` e `tasks.yaml` com campos de schema, validações, metadados e pipelines canônicos de especificação.
3. Implementar validadores de formato, grounding e consistência com requisitos/diagramas antes de permitir avanço de etapa.
4. Ativar tracing por step e registrar `trace_id` na saída final do documento de especificação.
5. Criar testes automatizados para os critérios de sucesso e cenários de fallback descritos.
6. Versionar prompts e pipelines para regressão; manter dataset de inputs/outputs esperados.

---
Este roteiro integra a disciplina de Computação Generativa ao processo de especificação funcional, garantindo precisão, rastreabilidade e segurança nas entregas.
