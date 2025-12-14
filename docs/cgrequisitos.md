# Roteiro para alinhar a geração do documento de requisitos à Computação Generativa

## 1. Objetivo
Garantir que a geração do documento de requisitos (ex.: `docs/requisitosv0.2.txt` e sucessores) siga o modelo de Computação Generativa: múltiplos steps controlados, saídas com schema, guardrails, retries diferenciados, observabilidade e fallback determinístico. Este roteiro instrui o que adaptar em prompts, YAML de tarefas e agentes dedicados a produzir o documento de requisitos.

## 2. Escopo e premissas
- Abrange os agentes e pipelines responsáveis por coletar documentos de entrada, analisar requisitos e gerar o documento final.
- Nenhum agente deve produzir a versão final em uma única chamada: sempre seguir o pipeline canônico Router → EntityExtractor → Retriever → Composer → Verifier → Compliance → Formatter.
- Todas as saídas intermediárias e finais devem obedecer a schemas explícitos (JSON/struct) e ser validadas antes de avançar.

## 3. Papéis obrigatórios (ajuste específico para requisitos)
- **RouterAgent**: classifica a intenção (gerar/atualizar documento de requisitos, validar consistência, completar lacunas) e seleciona o pipeline adequado.
- **EntityExtractorAgent**: extrai entidades e variáveis relevantes (atores, módulos, requisitos funcionais/não funcionais, restrições, fontes de evidência, lacunas).
- **RetrieverAgent**: realiza RAG sobre documentos de entrada (PDFs, notas, e-mails) e sobre versões anteriores do documento de requisitos. Retorna `context_chunks` rastreáveis com metadados (fonte, página, trecho).
- **ComposerAgent**: gera um rascunho do documento de requisitos **somente** com base em `context_chunks` e nas entidades extraídas; sem extrapolações. Deve preencher campos obrigatórios (seções, requisitos, critérios de aceitação, rastreabilidade para fontes).
- **VerifierAgent**: valida grounding e factualidade de cada requisito com base nos `context_chunks`; marca `issues` quando um requisito não tem suporte explícito ou contém extrapolação.
- **ComplianceAgent**: verifica aderência a políticas (sem PII sensível não autorizado), escopo, estilo e idioma definidos; garante que lacunas sejam declaradas.
- **FormatterAgent**: normaliza idioma, formatação e estrutura (sem 1ª pessoa, seguir template do documento de requisitos); aplica fallback determinístico quando houver `issues` não resolvidos.

## 4. Pipeline mínimo para o documento de requisitos
1. **Classificação**: determinar se a tarefa é criar, atualizar ou validar o documento.
2. **Extração de entidades**: identificar atores, sistemas, regras, fluxos, requisitos F/NF, dependências, métricas e lacunas.
3. **Recuperação de contexto (RAG)**: coletar trechos relevantes dos documentos e versões anteriores; incluir IDs/links para rastreabilidade.
4. **Composição do rascunho**: montar seções estruturadas (Introdução, Escopo, Requisitos Funcionais, Requisitos Não Funcionais, Regras de Negócio, Fluxos, Critérios de Aceitação, Riscos, Lacunas). Cada requisito deve referenciar `context_ids`.
5. **Validação factual**: marcar `issues` por requisito (sem suporte, extrapolação, ambiguidade). Incluir tentativa de reparo pedindo fontes adicionais ou removendo itens não suportados.
6. **Validação de conformidade**: checar idioma, formato, ausência de 1ª pessoa, políticas de segurança, consistência de IDs.
7. **Formatação final** com fallback determinístico: se ainda houver `issues`, gerar saída parcial com avisos explícitos e lista de lacunas.

## 5. Schemas recomendados
- **Intent**: `{ "intent": "create|update|validate", "scope": "requirements_doc", "requested_sections": [...] }`
- **Entities**: `{ "actors": [...], "systems": [...], "business_rules": [...], "workflows": [...], "requirements": [...], "non_functional": [...], "gaps": [...], "questions": [...] }`
- **Context chunks**: lista de objetos `{ "id": string, "source": string, "page": number?, "quote": string, "relevance": number }`
- **Draft**: `{ "sections": [{ "id": string, "title": string, "content": string, "requirements": [{ "rid": string, "type": "F|NF", "text": string, "acceptance_criteria": [...], "context_ids": [...], "status": "supported|unsupported|gap" }] }], "open_questions": [...], "gaps": [...] }`
- **Issues (Verifier)**: `{ "unsupported": [...], "ambiguous": [...], "contradictory": [...], "format": [...], "actions": ["retry_with_context", "remove_unsourced"] }`
- **Compliance**: `{ "compliance_ok": bool, "violations": [...], "language": "pt-BR", "first_person": false }`
- **Final output**: `{ "status": "complete|partial|failed", "document": "...texto final...", "gaps": [...], "trace_id": "..." }`

## 6. Instruções para prompts dos agentes
- **Todos os prompts** devem exigir saída no schema correspondente e rejeitar strings livres.
- **Retries diferenciados**:
  - Tentativa 1: uso completo de contexto; se faltarem evidências, marcar lacunas.
  - Tentativa 2: resposta estritamente ancorada nos trechos; remover itens sem `context_ids` válidos.
  - Tentativa 3: fallback determinístico declarando limitações e solicitando fontes específicas.
- **ComposerAgent**: instruir a nunca inventar requisitos; se não houver suporte, mover o item para `gaps` com perguntas objetivas.
- **VerifierAgent**: prompt deve listar cada requisito com seus `context_ids` e checar existência dos trechos. Em caso negativo, sinalizar em `unsupported` e sugerir ação (remover ou pedir fonte).
- **ComplianceAgent**: incluir checagem de idioma pt-BR, proibir 1ª pessoa, e confirmar que toda afirmação tem pelo menos um `context_id`.
- **FormatterAgent**: aplicar template fixo do documento (títulos, numeração, glossário). Em fallback, incluir seção “Limitações e Próximos Passos”.

## 7. Instruções para os YAML de tarefas dos agentes
- **agents.yaml**: para cada agente acima, adicionar campos:
  - `inputs` (schema esperado), `outputs` (schema), `tools` permitidas (RAG, DB, verificadores), `retry_policies` (estratégias diferenciadas), `fallbacks` (templates determinísticos), `validation` (formato + grounding + conformidade).
  - `observability`: habilitar logs/trace por step, IDs correlacionados (ex.: `trace_id`, `step_id`).
- **tasks.yaml** (ou equivalente):
  - Incluir pipelines explícitos para geração/atualização/validação do documento de requisitos, referenciando os agentes em ordem canônica.
  - Em cada task, definir `inputs`, `expected_outputs`, `success_criteria` (ex.: nenhum requisito sem `context_id`, sem 1ª pessoa, idioma pt-BR), `failure_actions` (retry com estratégia 2/3, fallback parcial).
  - Adicionar metadados de rastreabilidade (versão do prompt, data, fonte do contexto) e ligação ao `trace_id`.

## 8. Observabilidade e testes específicos
- **Tracing**: criar spans por step com tempo, tentativas, prompts, respostas truncadas, `issues` e decisões de retry/fallback. Integrar com Langfuse ou ferramenta similar.
- **Testes comportamentais**: casos automatizados que checam:
  - Saída segue schema em todas as etapas.
  - Nenhum requisito é mantido sem `context_id` válido; lacunas são explicitadas.
  - Ausência de primeira pessoa; idioma pt-BR.
  - Fallback gera saída parcial com lista de lacunas quando não há suporte.
  - Rastreabilidade: cada requisito aponta para pelo menos um `context_chunk` com fonte.
- **Datasets de regressão**: manter conjunto de inputs (documentos) e expected outputs (estrutura do documento de requisitos) para detectar regressões nas etapas de composição/verificação/compliance.

## 9. Fallbacks determinísticos recomendados
- Se o Verifier mantiver `unsupported` após retries, mover o requisito para `gaps` e incluir pergunta clara para o solicitante.
- Se não houver contexto suficiente, gerar documento parcial com seções vazias, mantendo placeholders e avisos explícitos.
- Nunca “inventar” requisitos; sempre preferir sair com `status=partial` + lista de lacunas.

## 10. Checklist para adoção
1. Atualizar prompts dos agentes com schemas e políticas de retry/fallback acima.
2. Revisar `agents.yaml` e `tasks.yaml` adicionando campos de schema, validações, metadados e pipelines canônicos.
3. Implementar verificadores de formato/grounding/compliance antes de avançar cada step.
4. Ativar tracing por step e armazenar `trace_id` na saída final.
5. Criar testes automatizados para os critérios de sucesso descritos.
6. Registrar versões dos prompts e pipelines para regressão futura.

---
Este roteiro é parte integrante do esforço de Computação Generativa para reduzir alucinação, garantir rastreabilidade e produzir documentos de requisitos auditáveis.
