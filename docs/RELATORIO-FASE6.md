# Relatório — Fase 6 (concluída e validada): Gate de requisito + auto-crítica (Inserção C)

**Projeto:** LangNet · caso-teste ClinIA · **Data:** 2026-08-14 · **Executor:** Claude
**Commit selo:** `5b54ad5` · **Checkpoint de rollback (antes da fase):** `fcf4ad4`

> A Fase 6 ataca a **qualidade do requisito upstream**: um **gate** que checa os **8 elementos** de uma boa
> especificação por task, uma **auto-crítica** (à la RLAIF) e o **reforço dos prompts** de geração de spec.
> É a inserção de **maior ROI** segundo as referências (ROPE +20%; 38,3% das falhas do SWE-bench Verified
> eram requisitos sub-especificados). **Não altera telas.**

---

## 1. O que foi implementado

No gerador (`backend/agents/langnetagents.py`):
- **`_task_quality_report(tasks_yaml, schema_sql)`** — por task, a presença dos **8 elementos** (objetivo,
  contexto, inputs, output[=`output_schema`], constraints, evaluation, edge_cases, verification). O **gate**.
- Emite **`knowledge/quality_report.md`** (conceito OKF `type: Quality Report`) com a completude por task +
  as lacunas; e **loga um resumo** no code-gen (não-bloqueante).
- **`get_self_critique_prompt(artifact, checklist)`** — prompt reusável de **auto-crítica**: um agente
  critica o artefato contra o checklist dos 8 elementos (padrão *AI-feedback-contra-documento* da
  Constitutional AI).

Reforço de **prompt** (aditivo, no call site) em `app/routers/specification.py` e `agent_task_spec.py`:
exige as seções **constraints/edge_cases/evaluation/verification** + um passo de **gap-analysis** (listar
requisitos/ambiguidades/assunções faltantes) **antes** de gerar.

---

## 2. Provas de validação (saídas reais)

### 2.1 Unit do gate `_task_quality_report`
```
pre_atendimento_cardiologia -> objetivo ✓ contexto ✓ inputs ✓ output ✓ evaluation ✓ verification ✓
                               constraints ✗  edge_cases ✗
criar_encaminhamento        -> (idem)  constraints ✗  edge_cases ✗
```
✔ O gate identifica corretamente que as tasks da ClinIA (**geradas antes** do reforço) têm o essencial
mas **faltam constraints/edge_cases** — surfaçando a lacuna real.

### 2.2 Artefato `knowledge/quality_report.md` (o gate materializado)
```markdown
---
type: Quality Report
title: Qualidade de requisito das tasks (8 elementos)
generated: { by: langnet/qwen2.5-coder-32b-instruct, at: … }
---
# Completude por task (✓ presente · ✗ ausente)
| Task | objetivo | contexto | inputs | output | constraints | evaluation | edge_cases | verification |
| criar_encaminhamento | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ |
…
# Lacunas (o gate aponta o que falta)
- criar_encaminhamento: falta constraints, edge_cases
```

### 2.3 Reforço de prompt (nos 2 routers)
```
specification.py    → contém "QUALIDADE DE REQUISITO"  (True)
agent_task_spec.py  → contém "QUALIDADE DE REQUISITO"  (True)
```
✔ A geração de Especificação/Agent-Task Spec passa a exigir os 8 elementos + gap-analysis.

### 2.4 E2E (`./smoke.sh`) — regressão zero
```
[verify] atendimento=True | encaminhamento(medico+esp)=True | prontuario(liga pre_diag+enc)=True
[smoke] ✅ VERDE
```
✔ O gate é **não-bloqueante** (surfaça lacunas, não trava) — o fluxo clínico completo continua persistindo.

---

## 3. Telas
**A Fase 6 não altera nenhuma tela.** É qualidade de requisito (gate + auto-crítica + prompts). O smoke
seguiu **VERDE**.

---

## 4. Benefício, ressalva e trilha de commits
- **Benefício:** ataca o **maior ROI** apontado pelas referências — melhora a qualidade do requisito
  **upstream**, onde ela mais rende, com **gate** (surfaça lacunas) + **auto-crítica** (RLAIF) + prompts
  reforçados.
- **Ressalva honesta:** o reforço de prompt afeta a geração de spec de **todos os projetos** (rota
  compartilhada) — mudança **aditiva**; o **efeito pleno** (tasks já com constraints/edge_cases) aparece ao
  **gerar uma spec nova** pela pipeline. O gate/quality_report e a auto-crítica já são efetivos agora.
- **Rollback:** `fcf4ad4` (*ANTES da Fase 6*). **Selo:** `5b54ad5`.

## 5. Próximo passo (última fase)
**Fase 7 — log de suposições & limitações (Inserção D) + consolidação**: cada etapa registra
`assumptions_and_limitations`; consolidar a documentação. Será precedida pelo **CHECKPOINT — ANTES da
Fase 7**.
