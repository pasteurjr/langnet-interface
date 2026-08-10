# Atendimento Corrente — propagação de contexto entre telas (sem redigitar) — Relatório

**Data:** 2026-08-10 · **Projeto:** ClinIA — Clínica Médica Inteligente · **Executor:** Claude (feature no gerador do LangNet)

> Você aprovou o "próximo passo natural": **propagar o mesmo atendimento** (paciente_id/atendimento_id)
> para as telas seguintes — Encaminhamento, Prontuário, Consulta — **via estado compartilhado**, para
> rodar o fluxo clínico **sem redigitar o atendimento corrente**. Feito e provado no app + no banco.

---

## 1. O que foi implementado (feature do gerador — commit `4b344bb`)

**Estado do "Atendimento Corrente" compartilhado entre telas** (`currentAttendance.js`, em
`localStorage`): `getCarry / setCarry / clearCarry`.

1. **A triagem grava** o `paciente_id` + `atendimento_id` no atendimento corrente (assim que os cria).
2. **As telas seguintes herdam** automaticamente:
   - **campos pré-preenchidos** (ex.: *Paciente ID* e *Atendimento ID* já vêm selecionados);
   - **banner "Atendimento corrente"** no topo, com os IDs e o link **"Encerrar / novo atendimento"**;
   - **injeção automática** do contexto na chamada da task (campo vazio do formulário **não apaga** o
     FK herdado).
3. **Write-back**: quando uma etapa **persiste** (`criar_`/`registrar_<entidade>`), o **id gerado** é
   gravado no atendimento corrente sob `<singular>_id` (ex.: `encaminhamento_id`) — para a **próxima**
   etapa herdar.
4. **Correção de casamento de task** (`_resolve_task_target`): agora pontua **substantivo**
   (encaminhamento/prontuário) acima de **verbo genérico** (cadastrar/criar). Antes,
   `cadastrar_encaminhamento` casava errado com `cadastrar_paciente`; agora casa `criar_encaminhamento`
   e `registrar_prontuario`. Sem casamento por substantivo → botão desabilitado (fail-loud), nunca a
   task errada.

## 2. Prova 1 — o Prontuário HERDA o atendimento da triagem (sem digitar)

Fiz uma triagem (paciente **Ana Prado**) e, **na mesma sessão**, abri **Registro/Prontuário**. A tela
já traz o **banner verde "ATENDIMENTO CORRENTE"** (`paciente_id: 0254cc6b… · atendimento_id: 02b14c65…`)
e os campos **Paciente ID = "Ana Prado 780429"** e **Atendimento ID = 02b14c65-…** **pré-preenchidos** —
o operador só preenche o médico e o texto clínico. **Nada do atendimento é redigitado.**

![Registro/Prontuário herdando o atendimento corrente da triagem — banner + campos pré-preenchidos](IMG_HERDA)

Confirmado também nos dados da própria página (lidos do app):
```
CARRY após triagem:              { paciente_id: 0254cc6b…, atendimento_id: 02b14c65… }
Campos pré-preenchidos no prontuário: { "paciente id": 0254cc6b…, "atendimento id": 02b14c65… }
Banner "Atendimento corrente" presente? true
```

## 3. Prova 2 — a propagação PERSISTE (encaminhamento ligado ao atendimento da triagem)

Criei um **encaminhamento** usando o **`atendimento_id` propagado** (o operador só escolhe
médico/especialidade). No banco `clinia_ops`, o encaminhamento ficou **ligado ao mesmo atendimento e
paciente da triagem**:

```json
{
  "enc_id":         "3740a0ca-94c7-11f1-8a81-cbea323b9023",
  "atendimento_id": "02b14c65-94c7-11f1-8a81-cbea323b9023",   // ← o MESMO da triagem
  "paciente_id":    "0254cc6b-94c7-11f1-8a81-cbea323b9023",
  "nome": "Ana Prado 780429"
}
→ encaminhamento.atendimento_id == atendimento propagado da triagem?  TRUE
```

O FK do atendimento **viajou** da triagem até o registro persistido — que era exatamente o que faltava.

## 4. O que ainda falta (achado honesto)

- **Adapters gerados pelo LLM para etapas específicas podem ter lógica própria frágil.** O
  `criar_encaminhamento_deterministic` (gerado pelo LLM) **ignora** o `atendimento_id` recebido e tenta
  **derivá-lo de um prontuário que ainda não existe** (lógica circular) — por isso a prova acima usei o
  adapter CRUD **genérico** (`criar_encaminhamentos`), que lê os campos corretamente. Sanear os adapters
  por-task gerados pelo LLM é um item de **qualidade de geração**, separado desta feature.
- **Fluxo clínico completo (5 etapas):** o Prontuário exige a cadeia inteira de IDs
  (`pre_diagnostico_id`, `encaminhamento_id`). O write-back já encadeia as etapas **determinísticas**;
  falta as etapas **agênticas** (ex.: geração de pré-diagnóstico) também **persistirem e devolverem seu
  id** para a cadeia fechar de ponta a ponta. Algumas telas ainda não coletam todos os campos que a
  tabela exige (ex.: a "Seleção de Médico" não tem um seletor de médico próprio).

## 5. Conclusão

- **Propagação do atendimento corrente entre telas: FEITA e comprovada** — as telas seguintes **herdam**
  `paciente_id`/`atendimento_id` (campos pré-preenchidos + banner), **sem redigitar**, e a propagação
  **persiste** (encaminhamento ligado ao atendimento da triagem).
- **Casamento de task corrigido** para o fluxo agêntico (encaminhamento/prontuário/consulta).
- Tudo via **feature do gerador do LangNet** (commit `4b344bb`), ClinIA como caso-teste — sem edição
  manual nos artefatos.
- **Próximo passo** (quando quiser): sanear os adapters por-task do LLM e fazer as etapas agênticas
  persistirem seus IDs, para o **fluxo clínico inteiro** (triagem → pré-diagnóstico → encaminhamento →
  prontuário → consulta) rodar de ponta a ponta pela UI.
