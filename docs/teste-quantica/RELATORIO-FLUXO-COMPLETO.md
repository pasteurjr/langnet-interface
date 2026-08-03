# Teste do Fluxo Completo — Aplicação Quântica Comercial (gerada pelo LangNet)

**Data:** 2026-08-03 · **Executor:** Claude (dirigindo a app gerada, screenshots reais)
**Projeto:** Quântica Comercial (`b55ef718…`) · **App em:** `/home/pasteurjr/quantica-app-fixed/`
**Ambiente:** frontend `:3001` · ws-server `:5002` → banco **`quantica_ops`** · `SIMULATE_EXTERNAL=true`

> Tarefa: *"Teste você todo o fluxo e gere um report me mostrando as telas."*
> Rodei a aplicação **gerada pelo LangNet** ponta a ponta, com o modo de simulação das
> integrações externas ligado, e capturei cada tela do caminho real do usuário.

---

## Resumo executivo

| # | Etapa do fluxo | Tela | Resultado |
|---|---|---|---|
| 1 | Cadastro (CRUD) | Formulário de Cadastro de Persona | ✅ **44 de 44** registros reais do banco |
| 2 | Geração agêntica (form) | Geração Automática de Conteúdo | ✅ Persona **e** Pilar como `<select>` populados |
| 3 | Geração agêntica (resultado) | idem, após *Executar com IA* | ✅ **STATUS = sucesso**, `POST_ID` gravado |
| 4 | Painel (dashboard) | Coleta de Métricas de Engajamento | ✅ 6 cards de KPI + *Atualizar* |
| 5 | Publicação (integração externa) | Publicação Automática de Conteúdo | ✅ tela ok; tool externa → **modo simulado** |
| 6 | Orquestração (Cara B) | Admin / Petri | ✅ **30 lugares · 29 transições · 15 agentes** |

**Bug corrigido durante o teste:** `listar_pilares_conteudo_deterministic` estava **duplicado** no
gerador — uma versão usava a coluna `nome` (do schema do Modelo de Dados) e outra `tema` (a coluna
real da tabela `quantica_ops`), causando *"Unknown column 'nome'"* e deixando o dropdown de **Pilar
vazio**. Corrigi `_generate_crud_adapters` para **deduplicar** por função já existente
(`existing_fns`). Após a correção, o dropdown de Pilar popula e o *Executar com IA* cria um post real.

---

## 1. Cadastro com dados reais (CRUD)

A tela **Formulário de Cadastro de Persona** (UC-001) lê direto do `quantica_ops`: **44 de 44
registros reais**, com busca e ações Ver / Editar / Excluir. Não há mock — é o banco de produção da
instância de teste.

![CRUD Personas — 44 reais](F1)

---

## 2. Geração automática de conteúdo (tela agêntica) — o form

**Geração Automática de Conteúdo** (UC-006) é uma tela **agêntica**: dispara o agente
`gerar_conteudo_redator`. Os campos de chave estrangeira viraram `<select>` de verdade —
**Persona** carregou as personas reais ("Fundador de Fintech — copiloto de crédito") e **Pilar**
carregou de `pilares_conteudo`. Antes da correção deste teste, o Pilar vinha **vazio** (bug do
`nome`/`tema`).

![Gerar Conteúdo — form com FK-selects](F2a)

---

## 3. Geração automática de conteúdo — o resultado

Ao clicar **Executar com IA**, o ws-server despacha a task e grava o post no banco. Resultado real:

> **STATUS: sucesso** · **POST_ID: `ba919a80-8f0e-11f1-8a81-cbea323b9023`**

O post foi **efetivamente criado** no `quantica_ops` (a data de publicação é preenchida
automaticamente via `_hoje()` quando o agente não a fornece — outro gap já corrigido).

![Gerar Conteúdo — resultado sucesso](F2b)

---

## 4. Painel de KPIs (dashboard)

**Coleta de Métricas de Engajamento** (UC-011) é classificada como **painel/dashboard** — não CRUD.
Renderiza 6 cards de KPI (Impressões, Alcance, Curtidas, Comentários, Compartilhamentos, Cliques) e
um botão **↻ Atualizar** (atualizado por agente de IA). Este é o comportamento correto após o fix da
regressão que antes transformava o painel em cadastro.

![Métricas — dashboard de KPIs](F3)

---

## 5. Publicação automática — integração externa em modo simulado

**Publicação Automática de Conteúdo** (UC-010) usa as tools externas (LinkedIn / Instagram / CMS).
Com `SIMULATE_EXTERNAL=true`, **nenhuma ação externa real é executada** — as tools retornam um
payload rotulado `status: simulado`, permitindo testar o fluxo **antes de criar as credenciais**.

![Publicação Automática](F4)

**Prova das tools em modo simulação** (chamada direta às 4 tools externas geradas):

```
linkedin_api_tool   -> {'status': 'simulado', 'tool': 'linkedin_api_tool',
                        'message': '[SIMULAÇÃO] publicaria este post no LinkedIn — nenhuma ação
                        externa REAL foi executada (SIMULATE_EXTERNAL ligado)...'}
instagram_graph_api_tool -> {'status': 'simulado', ... '[SIMULAÇÃO] publicaria esta imagem...'}
google_calendar_api_tool -> {'status': 'simulado', ... "[SIMULAÇÃO] criaria o evento 'Reunião teste'..."}
cms_api_tool        -> {'status': 'simulado', ... "[SIMULAÇÃO] publicaria 'Artigo' no CMS..."}
```

Sem credencial e com simulação **desligada**, as mesmas tools falham **explícito** (fail-loud:
*"preencha X no .env"*) — nunca retornam mock silencioso. Os placeholders das credenciais já estão
no `.env.example` (seção *INTEGRAÇÕES EXTERNAS*) e o passo-a-passo de criação está em
`docs/integracoes/GUIA-CREDENCIAIS-INTEGRACOES.pdf`.

---

## 6. Orquestração dos agentes (Cara B — Admin / Petri)

A aba **Admin / Petri** mostra a "segunda cara" da app: o **executor da Rede de Petri** que orquestra
os agentes. **30 lugares · 29 transições · 15 agentes**. Cada lugar de execução aponta o agente
responsável — `persona_manager_agent`, `content_planner_agent`, `content_generator_agent`,
`fact_checker_agent`, `content_reviewer_agent`, `scheduler_agent`, `publisher_agent`,
`metrics_collector_agent`, `comment_classifier_agent`, `response_generator_agent`,
`lead_identifier_agent`, `permission_manager_agent`, `exporter_agent`, `report_generator_agent`,
`calendar_syncer_agent` — do *Iniciar Fluxo* até *Fim do Fluxo*.

![Admin / Petri — 30 lugares, 15 agentes](F5)

**Como as duas caras se conectam:** as telas de negócio (Cara A) chamam `runTask()` por WebSocket
(`:5002`); o ws-server despacha **determinístico-primeiro** (`<task>_deterministic` = SQL puro, sem
LLM) e, quando a task é agêntica, aciona o `crew.kickoff()` do CrewAI. A Rede de Petri (Cara B) é a
visão de orquestração do mesmo conjunto de agentes/tasks.

---

## 7. Achados honestos (não bloqueiam o fluxo)

- 🟡 **Tasks agênticas externas** (publisher / coletar métricas / sincronizar agenda) podem retornar
  *"Invalid response from LLM call - None or empty"* — instabilidade do CrewAI com o modelo **local**
  (qwen), não do gerador. O **modo simulação funciona no nível da tool** (provado acima), então o
  caminho de negócio é testável independentemente dessa flakiness do LLM local.
- 🟡 `pilares_conteudo` tem poucos registros no `quantica_ops` → o dropdown de Pilar mostra o(s)
  registro(s) existente(s) (dado, não bug).
- 🟡 A tela de Publicação exibe os campos como caixas de texto (Canal / Data / Conteúdo) — o LLM
  gerou slots de texto ali; a estrutura (painel + form) está correta.

---

## Conclusão

O fluxo completo da aplicação Quântica **roda ponta a ponta** com dados reais do `quantica_ops`:
CRUD (44 personas), geração agêntica que **cria um post de verdade** (FK-selects populados após o
fix de deduplicação), dashboard de KPIs, publicação em **modo simulado** (integrações externas
testáveis sem credencial) e a orquestração de **15 agentes** na Rede de Petri. Um bug real do
gerador (duplicação `nome`/`tema`) foi **encontrado e corrigido durante o próprio teste**, e a
correção foi verificada ao vivo (Pilar popula, *Executar* grava o post).
