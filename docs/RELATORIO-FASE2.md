# Relatório — Fase 2 (concluída e validada): Bundle OKF de contexto (Inserção E)

**Projeto:** LangNet · caso-teste ClinIA · **Data:** 2026-08-13 · **Executor:** Claude
**Commit selo:** `f5d3933` · **Checkpoint de rollback (antes da fase):** `0fcf526`

> A Fase 2 emite o **domínio como conhecimento OKF** (Markdown + frontmatter YAML, FKs como wikilinks) e
> faz os **agentes do runtime consumirem esse conhecimento como contexto aterrado**. Ataca a **alucinação
> na raiz** (o agente inventar entidades / consultar tabelas inexistentes). **Não altera telas** — a
> mudança é no ws-server + em novos arquivos `ws-server/knowledge/`.

---

## 1. O que foi implementado

No gerador (`backend/agents/langnetagents.py`):
- **`_emit_okf_bundle(schema_sql, …)`**: emite `ws-server/knowledge/` em **OKF v0.2** — `index.md`
  (`okf_version`) + `tables/<t>.md` (frontmatter `type: DB Table`/`description`/`status` + **Schema** com
  colunas/tipos + **FKs como wikilinks** para o grafo) + `log.md` (reservado, **sem** frontmatter, conforme
  a spec OKF). Derivado do Modelo de Dados **real**. Emitido no build junto do `db/schema.sql`.
- **`_okf_context(task_name, input_data, description)`** (helper nos adapters): seleciona os conceitos OKF
  relevantes (tabelas citadas na descrição/inputs + vizinhos por FK) e devolve o markdown de contexto.
- **Bloco no template do ws-server** (`_execute_task`): injeta *"CONTEXTO DO DOMÍNIO (tabelas/relações
  REAIS; use SOMENTE estas, NÃO invente outras)"* no prompt do agente, logo após os DADOS DE ENTRADA.

Harness: `regen_okf.py` emite o bundle; `regen.sh` ganhou os alvos `okf` e no `all`.

---

## 2. Provas de validação (saídas reais)

### 2.1 Bundle emitido + conformance OKF
```
[regen_okf] 11 arquivos OKF escritos (index.md + log.md + 9 tabelas)
conformance: toda tabela .md tem 'type'  → OK
log.md sem frontmatter  → CORRETO (arquivo reservado do OKF v0.2)
historico_medico no bundle?  → NÃO (zero tabela fantasma)
```

### 2.2 Conceito OKF de uma tabela (schema real + FK wikilink) — `tables/pre_diagnosticos.md`
```markdown
---
type: DB Table
title: pre_diagnosticos
description: Tabela pre_diagnosticos do domínio (schema real; use SOMENTE tabelas deste bundle).
resource: db://pre_diagnosticos
status: stable
---
# Schema
| Coluna | Tipo | Referência |
|---|---|---|
| atendimento_id | CHAR | [atendimentos](/tables/atendimentos.md) |
| hipoteses | TEXT |  |
| nivel_confianca | FLOAT |  |
| exames_sugeridos | TEXT |  |
# Joins
- atendimento_id → [atendimentos](/tables/atendimentos.md)
```

### 2.3 Contexto injetado no agente — `_okf_context(pre_atendimento_cardiologia, …)`
```
tabelas no contexto: ['atendimentos', 'pacientes']   (tabelas REAIS, citadas na task)
contém FK wikilinks (/tables/..md)?  True
menciona historico_medico?          False
tamanho: 917 chars
```
✔ O agente recebe o **mapa real do domínio** (tabelas que existem, com joins) — e **nenhuma** tabela
inexistente.

### 2.4 E2E (`./smoke.sh`) — regressão zero, agente rodando COM o contexto OKF
```
[verify] atendimento=True | encaminhamento(medico+esp)=True | prontuario(liga pre_diag+enc)=True
[smoke] ✅ VERDE
```
✔ O ws-server injeta o contexto (`websocket_server.py` contém o bloco de injeção) e o fluxo clínico
completo continua persistindo a cadeia ligada.

---

## 3. Telas
**A Fase 2 não altera nenhuma tela.** O entregável é conhecimento (arquivos `knowledge/*.md`) + a injeção
de contexto no ws-server. O smoke desta fase seguiu **VERDE**, exercitando as mesmas telas da Fase 0.

---

## 4. Benefício e trilha de commits
- **Benefício:** dá aos agentes o **contexto aterrado** do domínio real — ataca a **alucinação na raiz**
  (inventar entidade / consultar tabela inexistente). É o *"conectar a IA ao contexto interno"* que a DORA
  aponta como alavanca de valor, e a implementação de referência do Google (*Enrichment Agent*).
- **Rollback:** `0fcf526` (*ANTES da Fase 2*). **Selo:** `f5d3933` (*Fase 2 concluída e validada*).

## 5. Próximo passo
**Fase 3 — hierarquia de instruções (Inserção G)**: como a Fase 2 injeta contexto recuperado, a Fase 3
impõe a **cadeia de comando** (regras/spec > task > input_data > **contexto = DADO, não COMANDO**), fechando
o flanco de *prompt-injection* que a injeção de contexto abre. Será precedida pelo commit **CHECKPOINT —
ANTES da Fase 3**.
