# Item 3 — Telas agênticas coletam as FKs obrigatórias da entidade — Relatório

**Data:** 2026-08-11 · **Projeto:** ClinIA · **Executor:** Claude (feature no gerador do LangNet) · **Commits:** `cc31662`, `16947b1`

> Faltavam campos nas telas: a "Seleção de Médico" **cria um encaminhamento**, mas não tinha **seletor
> de médico** — e `encaminhamentos.medico_id` é NOT NULL, então o INSERT falhava por FK nula. O item 3
> faz a tela **coletar as FKs obrigatórias** da entidade que ela persiste. Provado E2E pela UI + banco.

---

## 1. O que foi implementado (commits `cc31662`/`16947b1`)

No `_agent_screen`: quando a task da tela **persiste uma entidade** (`criar_`/`registrar_<entidade>`), a
tela passa a **coletar as FKs NOT NULL** que essa entidade exige, como **dropdown da entidade
referenciada** — parseando `FOREIGN KEY` + `NOT NULL` do DDL. Regras:
- **Exclui** `paciente_id`/`atendimento_id` (vêm **herdados** do atendimento corrente — item anterior).
- **Remove o campo de texto redundante** do ui_spec com o mesmo nome-base (ex.: some o "Especialidade"
  solto quando entra o dropdown `especialidade_id`).

**Efeito na ClinIA:**
- **Seleção de Médico** (cria `encaminhamento`): ganhou **seletor de Médico** + **Especialidade**.
- **Registro/Prontuário** (cria `prontuario`): passou a coletar `pre_diagnostico_id` + `encaminhamento_id`
  (pré-preenchidos do carry via write-back).

## 2. Prova E2E pela UI — encaminhamento persiste com o médico escolhido

Com o **atendimento corrente** ativo (banner), na "Seleção de Médico" escolhi **Especialidade =
Cardiologia** e **Médico = Dr. Carlos Mendes** (dropdowns novos) e cliquei **Executar**:

![Seleção de Médico — dropdown de Médico + Especialidade, atendimento herdado, encaminhamento criado](IMG_SEL)

O resultado: **STATUS sucesso**, `ENCAMINHAMENTO_ID` gerado, `ATENDIMENTO_ID` = o herdado. E o banner
"ATENDIMENTO CORRENTE" passou a exibir também o **`encaminhamento_id`** (write-back para a próxima etapa).

## 3. Prova no banco `clinia_ops`

```json
{
  "enc_id":          "3cf0657d-95c0-11f1-8a81-cbea323b9023",
  "atendimento_id":  "a864b53e-95b1-11f1-8a81-cbea323b9023",   // ← herdado (atendimento corrente)
  "medico":          "Dr. Carlos Mendes",                       // ← escolhido no dropdown
  "especialidade":   "Cardiologia",                             // ← escolhida no dropdown
  "paciente":        "Bruno Neves 562165"
}
```

O encaminhamento persistiu **ligado ao atendimento corrente**, com o **médico e a especialidade
escolhidos na própria tela** — exatamente o campo que faltava. Sem o item 3, o INSERT falhava com
`medico_id cannot be null`.

## 4. Conclusão e próximo item

- **Item 3 FEITO e comprovado E2E**: telas agênticas que persistem uma entidade agora **coletam as FKs
  obrigatórias** (dropdowns), com os FKs do atendimento corrente **herdados** e os demais **escolhidos**.
- Com isso, **Seleção de Médico** e **Registro/Prontuário** têm todos os campos para persistir pela UI.
- **Próximo (item 4):** validação **E2E do fluxo clínico inteiro** pela UI — um paciente percorrendo
  triagem → pré-diagnóstico → encaminhamento → prontuário → consulta — com relatório final.
