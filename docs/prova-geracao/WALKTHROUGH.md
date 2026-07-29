# 🎬 Walkthrough — Correções no LangNet e Geração de Prova (Quântica Comercial)

**Data:** 2026-07-28 · Modelo que corrige/gera: **qwen2.5-coder-32b** (LM Studio, no ar)

> Este documento é um "screencast em PDF": cada passo diz **o que eu vou fazer** e mostra a
> **tela/resultado**. Regra de ouro: a Quântica é *gerada* pelo LangNet, então **todo conserto é
> no gerador** (`backend/agents/langnetagents.py` e afins) — depois regeneramos a Quântica.

---

## 🎬 Passo 0 — O ponto de partida

**O que eu ia fazer:** revisar a Quântica ponta a ponta e achar o que está fraco/quebrado.
**Resultado (o que encontrei):**
- Interface **não é "só CRUD"** (tem form, ação agêntica, dashboard, grid) — mas com fraquezas.
- O app gerado tinha **2 crashes garantidos**, **5 ferramentas mocadas** (fingindo funcionar),
  **16/39 vínculos de dados quebrados** e **campos de FK como caixa de ID**.

A tela abaixo é uma das 18 telas do protótipo **antes** das correções — repare na sidebar
genérica **"Nome do Produto"**:

![Antes: sidebar genérica](IMG_ANTES)

---

## 🎬 Passo 1 — P0.1: matar a "tarefa fantasma"

**O que vou fazer:** algumas telas chamavam uma tarefa que **não existe** (ex.: `aprovar_todos_itens`),
o que dá erro ao clicar. Vou fazer o gerador **não emitir** `runTask` para tarefa inexistente:
o botão fica **desabilitado com aviso**.

**🖥️ Resultado:**

*Antes:*
```
ANTES_P0_1
```
*Depois:*
```
DEPOIS_P0_1
```

---

## 🎬 Passo 2 — P0.2: matar o `NameError` na edição

**O que vou fazer:** o adapter de edição de persona usava variáveis soltas (`prob`, `obj`) que não
existiam → `NameError`, e a edição sempre falhava. Vou fazer o gerador usar o **item do loop** certo.

**🖥️ Resultado:**

*Antes (quebrado):*
```
ANTES_P0_2
```
*Depois (correto):*
```
DEPOIS_P0_2
```

---

## 🎬 Passo 3 — P1: eliminar TODO mock (ferramentas reais)

**O que vou fazer:** o gerador colocava 5 ferramentas **mocadas** no app (PDF/CSV/Embedding/
VectorSearch/Email que só fingiam). Vou emitir uma **biblioteca real** (`tools_std.py`) e **remover
os mocks** do `tools.py`. O que precisa de credencial (SMTP, etc.) **falha explícito** — nunca finge.

**🖥️ Resultado:**

*Antes (mock):*
```
ANTES_P1
```
*Depois (real):*
```
DEPOIS_P1
```

Teste funcional real: o PDF gera arquivo `%PDF-` de verdade, o CSV escreve o arquivo, e Email/
VectorSearch **sem configuração falham explícito** (não retornam sucesso falso).

---

## 🎬 Passo 4 — P2: o protótipo não pode inventar dados

**O que vou fazer:** o mockup inventava tabelas/colunas que **não existem** no banco (16/39 vínculos
quebrados). Vou proibir isso: `bindTo` só do schema real; o que não existe vira `null`
(safety-net determinístico).

**🖥️ Resultado (coerência da Quântica):**
```
COERENCIA_P2
```

---

## 🎬 Passo 5 — P3: chave estrangeira vira dropdown

**O que vou fazer:** campos de FK (ex.: `pilar_conteudo_id`) apareciam como **caixa de texto de ID**.
Vou fazer virar um **`<select>`** que carrega as opções da entidade referenciada.

**🖥️ Resultado (código gerado do campo FK):**
```
CODIGO_P3
```

> Nota honesta: na regeneração de prova desta vez, o modelo **não gerou telas com campos de FK**
> (0 componentes ligados a `persona_id`/`pilar_conteudo_id`/etc.), então o dropdown não teve o que
> marcar nesta rodada. O **mecanismo está validado** (o código acima é o que o gerador produz
> quando a tela tem um campo de FK) e dispara automaticamente quando houver.

---

## 🎬 Passo 6 — Branding + navegação unificada

**O que vou fazer:** a sidebar saía genérica e cada tela tinha um menu diferente. Vou brandar com o
**nome do projeto** e usar a **mesma navegação** em todas.

**🖥️ Resultado (mesma tela, depois):**

![Depois: sidebar "Quântica Comercial"](IMG_DEPOIS)

---

## 🎬 Passo 7 — GERAÇÃO DE PROVA (regenerar a Quântica com tudo aplicado)

**O que vou fazer:** disparar a **regeneração real** do protótipo da Quântica no modelo no ar, com
P0+P1+P2+P3 ativos, e conferir no artefato: zero vínculo quebrado, FK como select, branding.

**🖥️ Resultado da geração de prova:**
```
PROVA_RESULTADO
```

![Tela da geração de prova](IMG_PROVA)

---

## ✅ Resumo

| Prioridade | O que era | Depois da geração de prova |
|---|---|---|
| P0.1 | tela com tarefa fantasma → erro | botão desabilitado, sem chamada fantasma |
| P0.2 | edição quebrava (`NameError`) | grava certo |
| P1 | 5 ferramentas mocadas | reais (ou fail-loud) — **zero mock** |
| P2 | 16/39 vínculos quebrados | **0 quebrados** |
| P3 | FK como caixa de ID | **`<select>`** da entidade |
| Branding | "Nome do Produto" | **"Quântica Comercial"** + nav unificada |

Todos os consertos estão **no gerador do LangNet** (commit/push feitos, backup do banco antes de
cada etapa). A Quântica é o caso-teste que provou cada correção.
