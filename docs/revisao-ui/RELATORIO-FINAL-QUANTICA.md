# Relatório Final — Revisão do Pipeline LangNet + Conformidade da App Quântica Comercial

**Data:** 2026-07-31 · **Revisor:** Claude, agindo no lugar do usuário (UI real, pedindo revisão ao agente do LangNet)
**Projeto:** Quântica Comercial (`b55ef718…`) · **Modelo revisor:** qwen2.5-coder-32b (LM Studio, no ar)

> Este relatório tem 3 partes: **(A)** revisão das 10 etapas do pipeline pela UI; **(B)** análise de
> **conformidade** da aplicação Quântica **gerada** (o que foi construído × o que foi especificado),
> com telas reais da app rodando; **(C)** plano de ajustes priorizado.

> **Nota técnica:** corrigi um erro meu anterior — a spec de 73KB são **~20K tokens** (não 73K); o
> qwen-32b local **dá conta** dos documentos (o pipeline gera em chunks). Não é preciso trocar de modelo.

---

# PARTE A — Revisão das 10 etapas (pela UI)

| # | Etapa | Revisão do agente | Veredito |
|---|---|---|---|
| 1 | Documentos (upload) | n/a | — |
| 2 | **Requisitos** | ✅ "Refine with Agent" | 🟢 Documento bom (v1.1, 39KB, 12 seções, LGPD-aware) |
| 3 | **Especificação** | ✅ Analisar | 🟢 Revisão do agente muito boa (lacunas, UCs faltantes, coerência) |
| 4 | **Modelo de Dados** | ✅ Revisar | 🟢 Revisão sólida (NOT NULL/UNIQUE, normalizar JSON, índices) |
| 5 | **Protótipo** | ✅ Coerência | 🟢 0/24 vínculos quebrados (prova P2), branded; 3 kind-mismatch |
| 6 | **Agentes/Agent-Task** | ✅ Revisar (mas…) | 🔴 Não auto-carrega — exige "Selecionar Especificação" |
| 7 | **Casos de Teste** | ✅ Revisar | 🟡 Só 1 de ~20 UCs (bug de geração) |
| 8 | **Sequência de Tarefas** | ✅ Revisar (mas…) | 🔴 Não auto-carrega — exige 3 docs |
| 9 | **Rede de Petri** | ❌ Não tem | 🔴 Canvas vazio; agente não revisa esta etapa |
| 10 | **Código** | ✅ Chat refino | ⚠️ Mostrou 0 sessões (provável artefato do meu automatismo; API tem 44) |

**Achado transversal:** a **segunda metade do pipeline** (Agentes, Sequência de Tarefas, Petri, Código)
**não auto-carrega** a última versão — quebra o fluxo de revisão. As 4 primeiras auto-carregam.
O agente do LangNet **revisa bem** onde há chat/Revisar.

Detalhes por etapa (Especificação, Modelo de Dados, Casos de Teste) e telas em
`docs/revisao-ui/RELATORIO-REVISAO-UI.pdf`.

---

# PARTE B — Conformidade da aplicação Quântica GERADA

> App rodando de verdade em `:3001` (`quantica-app-coerente`, gerada 2026-07-23 — **anterior aos meus
> fixes P0-P3**). ws-server (:5002) fora → operações de dados mostram "WebSocket error" (esperado).

## B.1 — Conformidade ESTRUTURAL: ✅ CONFORME

A app implementa telas para **todos os grupos de UC** da spec, organizadas em módulos que espelham
o domínio especificado, com branding **"Quântica Comercial"**:

| Módulo (sidebar) | UCs/entidades cobertos | Conforme? |
|---|---|---|
| **CADASTROS** (20) | Personas, Leads, Empresas, Canais, Contatos, Pilares, Palavras-chave, Objeções, Gatilhos, Problemas, Métricas… | ✅ = entidades do Modelo de Dados |
| **CONTEÚDO** | UC-002 Calendário, UC-003 Editar, UC-004 Aprovar, UC-005 Temas, UC-006 Gerar Conteúdo, UC-007 Verificar Fatos, Revisão | ✅ = UCs da spec |
| **PUBLICAÇÃO** | Agendamento, Publicação Automática | ✅ |
| **ENGAJAMENTO** | UC-011 Métricas, Classificação de Comentários, Respostas | ✅ |
| **RELATÓRIOS** | Relatórios Semanais, Exportação | ✅ (UC-035 que o agente apontou como faltante NA SPEC existe como tela!) |
| **INTEGRAÇÕES** | Leads Warm Inbound, Sincronização Google Calendar | ✅ |
| **Admin / Petri** | Executor de Petri (Cara B) | ✅ |

**Cada tela declara seu UC** (ex.: "UC-006 · executado por agente de IA"). **Não é "só CRUD"**:
há telas de cadastro (CRUD), telas agênticas (Executar com IA) e integrações.

## B.2 — Conformidade dos AGENTES: ✅ CONFORME

As telas agênticas disparam o **agente correto** do pipeline:
- UC-006 "Geração de Conteúdo" → agente `gerar_conteudo_redator` ✓
- UC-011 "Coleta de Métricas" → agente `coletar_metricas_engajamento` ✓

## B.3 — DIVERGÊNCIAS (não-conforme) 🔴

1. 🔴 **Dashboard virou botão.** UC-011 (Métricas) foi **prototipado como painel de KPIs**
   (cards Impressões/Alcance/Curtidas…), mas a app **construiu apenas um botão "▷ Executar com IA"**.
   O gerador de tela agêntica não reproduz o layout de dashboard do protótipo. **Não conforme com o
   protótipo/spec.**
2. 🟡 **FK como ID cru.** `EMPRESA_ID` (Leads) é coluna de ID; Persona/Pilar (Geração de Conteúdo)
   são caixas de texto — não dropdowns. (Meu fix **P3** torna FK em `<select>`, mas esta app é anterior.)
3. ⚠️ **Runtime depende do ws-server.** Sem :5002 a app não lê/grava (WebSocket error). Esta app é
   **anterior aos fixes P0-P3**, então o ws-server dela ainda teria os 2 crashes + tools mock.

## B.4 — Veredito de conformidade
**Conforme na estrutura e no roteamento de agentes** (as telas certas, para os UCs certos, disparando
os agentes certos). **Não conforme em riqueza de algumas telas** (dashboards viraram botão) e em
**detalhes de UX** (FK como ID) — mas **estes três pontos já estão endereçados** pelos meus fixes
P2/P3 (0 vínculos quebrados, FK→select) e pela biblioteca de tools reais (P1). Falta **regenerar a
app** com o gerador atual para materializar tudo.

---

# PARTE C — Plano de Ajustes (priorizado)

## P0 — Já feito (no gerador), falta regenerar a app
- ✅ 2 crashes (task fantasma, NameError de edição) — corrigidos.
- ✅ Zero mock (biblioteca `tools_std.py` real + fail-loud) — corrigido.
- ✅ P2 coerência (0 vínculos quebrados) + P3 (FK→select) + branding — corrigidos.
- ⏳ **AÇÃO:** regenerar a app Quântica com o gerador atual e subir ws-server para validar em runtime.

## P1 — Bugs de geração encontrados nesta revisão
1. 🔴 **Casos de Teste cobre só 1 de ~20 UCs** → o gerador deve iterar **todos** os UCs.
2. 🔴 **Dashboard vira botão** → o gerador de tela agêntica deve, para `kind=dashboard`, renderizar
   os **cards de KPI** (readonly do ui_spec) + botão de atualizar — não só "Executar com IA".

## P2 — Padrão quebrado nas etapas finais (auto-load)
3. 🔴 **Agentes/Agent-Task, Sequência de Tarefas, Petri, Código** devem **auto-carregar a última
   versão** (como Especificação/Modelo de Dados/Protótipo). Hoje exigem reselecionar origem/regenerar.
   *(Bate com o plano "padronizar todas as etapas no padrão da Especificação".)*
4. 🟡 **Rede de Petri** não tem revisão de agente — avaliar adicionar (feature nova) ou documentar
   que é regeneração-only.

## P3 — Conteúdo (aplicar sugestões do próprio agente)
5. 🟡 **Especificação:** virar UCs os faltantes que o agente apontou (LGPD/UC-036, coerência UC-003/005/007).
6. 🟢 **Modelo de Dados:** aplicar as sugestões (NOT NULL/UNIQUE em `pilares_conteudo.nome`,
   normalizar JSON `slots`/`slides`, índice em `posts.tipo_conteudo`, renomear `slides`→`estrutura_slides`).
7. 🟡 **Protótipo:** corrigir os 3 kind-mismatch (UC-003 edit, UC-016 list, UC-017 dashboard).

## Ordem recomendada
1. **Regenerar a app** com o gerador atual (materializa P0-P3) + subir ws-server → provar runtime.
2. **P1** (Casos de Teste todos os UCs; dashboard com KPIs).
3. **P2** (auto-load das etapas finais).
4. **P3** (aplicar sugestões de conteúdo por etapa).
