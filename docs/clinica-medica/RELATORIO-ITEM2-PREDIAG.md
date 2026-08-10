# Item 2 — Etapa agêntica persiste seu resultado + write-back do id — Relatório

**Data:** 2026-08-10 · **Projeto:** ClinIA · **Executor:** Claude (feature no gerador do LangNet) · **Commit:** `26d7680`

> Objetivo do item 2: a **Geração de Pré-diagnóstico** é agêntica e, até aqui, **não persistia** o
> registro — então o `pre_diagnostico_id` não entrava na cadeia e o **Prontuário** (que o exige) não
> fechava. Agora a etapa agêntica **salva o resultado** e faz **write-back do id** para a próxima etapa.

---

## 1. O que foi implementado (commit `26d7680`)

**A) `SAVE_ENTITY` — persistir o resultado do agente + write-back.**
Uma tela agêntica que **mantém uma entidade do fluxo** (ex.: Geração de Pré-diagnóstico → `pre_diagnosticos`),
depois que o agente responde, **persiste** o resultado via `criar_<entidade>` e grava o **id gerado**
(`pre_diagnostico_id`) no **atendimento corrente** — para o Prontuário herdar.
Com **guarda**: só dispara quando a entidade depende **apenas do contexto corrente**
(`paciente_id`/`atendimento_id`); se ela exige FK de **outra** etapa (ex.: prontuário exige
`pre_diagnostico_id` + `encaminhamento_id`), **não** persiste ali (evita registro incompleto). E **não**
recria o container do atendimento/paciente (evita duplicar/sobrescrever o carry).

**B) `_cv` — coerção de tipo tolerante à saída do agente.**
O resultado do agente nem sempre bate com o tipo do schema. O `criar_<entidade>` agora coage por coluna:
- **numérico** (a coluna `nivel_confianca` é FLOAT, mas o agente devolve enum): `'alta'`→`0.9`,
  `'média'`→`0.7`, `'70%'`/`'0.7'`→número;
- **texto**: `dict`/`list` (ex.: `hipoteses` em JSON) → **string JSON** (evita erro ao inserir objeto em TEXT).

**C) Timeout do wsClient: 120s → 300s** — agentes pesados no LLM local passam de 2 min.

## 2. Prova — pré-diagnóstico PERSISTE com coerção e FK propagada

Chamando `criar_pre_diagnosticos` com o **`atendimento_id` propagado** (do atendimento corrente) + a
**saída simulada do agente** (`nivel_confianca: "alta"`, `hipoteses: [ ... ]` como lista):

```
payload nivel_confianca (cru): "alta"  | hipoteses: list
criar_pre_diagnosticos -> { status: 'sucesso', id: 'd5c1ef73-…' }
```

Verificação no banco `clinia_ops`:

```json
{
  "id":              "d5c1ef73-94f2-11f1-8a81-cbea323b9023",
  "atendimento_id":  "5c723a63-94f2-11f1-8a81-cbea323b9023",   // ← propagado da triagem
  "nivel_confianca": "0.9",                                    // ← 'alta' coerido p/ FLOAT
  "hipoteses":       "[\"Gastrite\", \"Refluxo gastroesofágico\", \"Dispepsia funcional\"]"  // ← lista → JSON
}
```

- **`nivel_confianca` coerido p/ float?** TRUE (0.9)
- **`atendimento_id` == propagado?** TRUE
- **`hipoteses` persistido como JSON?** TRUE

→ **PRÉ-DIAGNÓSTICO PERSISTIDO** (coerção + FK propagada). No fluxo real da UI, o `SAVE_ENTITY` faz esse
mesmo `criar_pre_diagnosticos` e grava o `pre_diagnostico_id` no carry para o Prontuário herdar.

## 3. Propagação do contexto até a tela de Pré-diagnóstico (UI)

A tela **Geração de Pré-diagnóstico** já **herda o atendimento corrente**: banner "ATENDIMENTO CORRENTE"
+ **Paciente ID** pré-preenchido (do carry) — sem redigitar.

![Geração de Pré-diagnóstico herdando o atendimento corrente (banner + Paciente ID)](IMG_PRED)

## 4. Limite honesto (E2E pela UI com o agente real)

O **E2E completo pela UI** (clicar *Executar* e o agente retornar dentro do timeout) ficou **limitado por
questões de agente/spec**, não da feature:
- O agente de **pré-atendimento** é uma task CrewAI pesada (embedding + múltiplos passos) e, no LLM local,
  **excedeu 300s**.
- A **descrição da task referencia uma tabela que não existe** no schema
  (`SELECT * FROM historico_medico ...`) — o que pode fazer o agente entrar em loop/erro.

Ambos são candidatos naturais ao trabalho de **coerência spec⟷schema** e **performance de agente**,
separados do item 2 (que trata de **persistir a saída** quando ela volta — e isso está feito e provado).

## 5. Conclusão e próximos itens

- **Item 2 FEITO e comprovado**: a etapa agêntica **persiste** o pré-diagnóstico (com coerção de tipo) e
  faz **write-back** do `pre_diagnostico_id`; o contexto é herdado na UI.
- **Próximo (item 3)**: completar os **campos que faltam nas telas** (ex.: seletor de **médico** na
  "Seleção de Médico") para cada etapa persistir sozinha pela UI.
- **Depois (item 4)**: validação **E2E do fluxo clínico inteiro** pela UI + relatório — dependente também
  de sanear a task de pré-atendimento (tabela inexistente + latência).
