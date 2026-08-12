# Item 4 — Fluxo clínico completo de ponta a ponta pela UI — Relatório

**Data:** 2026-08-11 · **Projeto:** ClinIA · **Executor:** Claude (features do gerador do LangNet) · **Commit-chave:** `10f8eb2`

> Costura final: um paciente percorrendo **Triagem → Pré-diagnóstico → Encaminhamento → Prontuário →
> Consulta**, tudo pela UI reorganizada, com o **atendimento corrente** propagando os IDs entre as
> etapas. Rodei de ponta a ponta e **verifiquei no banco** que toda a cadeia persistiu ligada.

---

## 1. Bug encontrado e corrigido no caminho (commit `10f8eb2`)

Na primeira corrida E2E, **pré-diagnóstico e prontuário não persistiam** (só atendimento + encaminhamento).
Causa: o ws-server às vezes devolve o resultado do agente **embrulhado** em `{ raw: "…json…" }` (ou
string com cerca markdown). O `SAVE_ENTITY` persistia sem os campos (`hipoteses`/`nivel_confianca`),
falhando por NOT NULL — e sem `pre_diagnostico_id` o prontuário também caía.
**Fix:** `parseAgentResult` no `_AGENT_BODY` desembrulha `{raw}`/string → objeto real antes de
persistir/exibir. Feature do gerador → vale para todo app gerado.

## 2. Corrida E2E — 5 etapas, um único atendimento

Rodei pela UI (`:3007`), um paciente cardíaco. O **atendimento corrente** (localStorage) acumulou os IDs
a cada etapa:

| Etapa | Tela | Persistiu | Write-back no carry |
|------|------|-----------|---------------------|
| 1 | Recepção & Triagem | paciente + atendimento | `paciente_id`, `atendimento_id` |
| 2 | Geração de Pré-diagnóstico | pre_diagnostico | `pre_diagnostico_id` |
| 3 | Seleção de Médico | encaminhamento | `encaminhamento_id` |
| 4 | Registro/Prontuário | prontuario | `prontuario_id` |
| 5 | Consulta Médica | diagnóstico final (agente) | — |

**Carry final** (todos os IDs da cadeia, herdados sem redigitar):
```json
{
  "paciente_id":       "1b8e3ecb-…",
  "atendimento_id":    "1beb7be0-…",
  "pre_diagnostico_id":"3cc4023d-…",
  "encaminhamento_id": "424e6af6-…",
  "prontuario_id":     "47128730-…"
}
```

No **Prontuário**, o banner "ATENDIMENTO CORRENTE" mostra a **cadeia inteira** e os campos *Pré-diagnóstico*
e *Encaminhamento* vêm **pré-preenchidos** (herdados) — o operador só preenche a queixa e o resumo:

![Registro/Prontuário — cadeia inteira herdada (banner) + Pré-diagnóstico/Encaminhamento pré-preenchidos + prontuário criado](IMG_PRONT)

## 3. Prova no banco `clinia_ops` — cadeia ligada de ponta a ponta

```
ATENDIMENTO:     Paciente E2E 525611 (Bradesco)
PRE_DIAGNOSTICO: nivel_confianca 0.9 · hipoteses {angina_de_peito, infarto_agudo_do_miocardio}
ENCAMINHAMENTO:  Cardiologia · Dr. Carlos Mendes
PRONTUARIO:      pre_diagnostico_id = 3cc4023d (pd_ok=1)  ·  encaminhamento_id = 424e6af6 (enc_ok=1)
                 triagem="Dor toracica opressiva…"  ·  resumo="Quadro sugestivo de SCA…"
```

O **prontuário referencia o pré-diagnóstico e o encaminhamento criados nas etapas anteriores** do mesmo
atendimento — a cadeia clínica fechou de ponta a ponta, tudo pela UI.

## 4. O que sustenta esse resultado (features feitas nos itens 1–4 + saneamento)

- **Tela híbrida** cadastro+agente + **encadeamento de persistência** (triagem abre o atendimento).
- **Atendimento corrente** (herança de FKs entre telas) + **write-back** do id de cada etapa.
- **Adapters respeitam o input propagado** (item 1) e **coerção de tipo** (item 2).
- **Saneamento** da task de pré-atendimento (pelo LangNet, UI) + **guard de coerência** tasks⟷schema.
- **Telas coletam as FKs obrigatórias** (item 3: seletor de médico etc.).
- **parseAgentResult** (este item): persistência robusta ao envelope do agente.

## 5. Conclusão

- **Fluxo clínico inteiro FUNCIONA de ponta a ponta pela UI** — triagem → pré-diagnóstico →
  encaminhamento → prontuário → consulta, um atendimento, cadeia persistida e ligada no banco.
- Tudo via **features do gerador do LangNet**, com a ClinIA como caso-teste (sem edição manual dos
  artefatos; o saneamento da task foi feito pelo próprio agente do LangNet via UI).
- **Ressalvas honestas:** o LLM local é lento/às vezes flaky (o driver usa espera/retry); a etapa de
  Consulta (agente) gera o diagnóstico final mas ainda não persiste um registro dedicado — candidato a
  um próximo refino se quiser fechar também a consulta no banco.
