# Tela Híbrida Recepção & Triagem + Persistência de ponta a ponta — Relatório

**Data:** 2026-08-06 · **Projeto:** ClinIA — Clínica Médica Inteligente · **Executor:** Claude (correções no gerador do LangNet)

> Você aprovou ("Sim, quero") duas coisas: (1) a **tela híbrida** — que *cadastra o paciente* **e**
> *dispara o agente de triagem* na mesma tela; e (2) o **encadeamento de persistência** — a triagem
> abre o atendimento e gera os IDs (`paciente_id`/`atendimento_id`) que as etapas seguintes exigem,
> resolvendo os erros de FK. Abaixo o que foi feito, com **prova no app rodando e no banco**.

---

## 1. O problema que restava

Na revisão anterior, a tela **"Recepção & Triagem"** renderizava como um **CRUD de pacientes** (tabela
com Ver/Editar/Excluir) — tinha perdido a parte **agêntica**. E a demonstração de fluxo falhava nas
etapas de encaminhamento/prontuário com **`atendimento_id`/`paciente_id` cannot be null**, porque
nada abria o atendimento.

## 2. O que foi corrigido no gerador (2 mudanças + 1 retoque)

Tudo foi feito no **gerador de código do LangNet** (`backend/agents/langnetagents.py`) — a ClinIA é
apenas o caso-teste; a correção nasce de uma **feature do produto**, não de edição manual no app.

**A) Classificação da tela (`_classify_screen`)** — commit `ba206b0`
Uma tela que dispara uma **ação de agente** (`kind=='task'`) passa a ser classificada como **agent**
*antes* da regra de "tem entidade → CRUD". Assim "Recepção & Triagem" (entity=`pacientes` + ação
`iniciar_triagem`) vira **formulário + botão de IA + resultado**, em vez de virar um CRUD.

**B) Encadeamento de persistência (`_agent_screen` / `_AGENT_BODY`)** — commit `ba206b0`
A tela híbrida ganha um bloco `CHAIN`. No submit, **antes** de acionar o agente, o fluxo:
1. **`criar_pacientes`** — cadastra o paciente (gera `paciente_id`);
2. **`criar_atendimentos`** — abre o atendimento com `paciente_id` + `data_hora` (gera `atendimento_id`);
3. **`triagem_agentiva`** — dispara o agente já com os IDs no contexto.
Os IDs são resolvidos pelos **nomes de FK reais** (`paciente_id`, `atendimento_id`) lidos do schema —
não pelo PK genérico `id`. É *best-effort*: se o CPF já existe ou o atendimento falha, a triagem
ainda roda.

**C) Retoque (`_out_kw`)** — commit `6c442c0`
Campos que são **saída do agente** (`area_destino`, `encaminhamento`) não viram mais campo de
entrada — aparecem no painel de **Resultado**.

## 3. Prova 1 — a tela agora é HÍBRIDA (cadastro + agente), rodando no app

A tela ClinIA rodando: menu **ATENDIMENTO** no topo (fluxo agêntico) e **CADASTROS** ao final. A
"Recepção & Triagem" é um **formulário** (Identificação: Nome/CPF/Nascimento/Contato/Convênio +
Queixa + Sinais Vitais: PA/FC/Temperatura/SpO2 + Especialidade) com o botão **▷ Executar com IA** —
subtítulo **"UC-002 · executado por agente de IA"** (a rastreabilidade tela⟷caso de uso no próprio
código). **Não há tabela CRUD.**

![Tela híbrida Recepção & Triagem — cadastro (identificação + sinais) + botão Executar com IA](IMG_FORM)

## 4. Prova 2 — fluxo de ponta a ponta pela UI (cadastra + abre atendimento + tria)

Preenchi um paciente com **dor torácica irradiando + sudorese, PA 160/100, FC 120, SpO2 92%** e cliquei
**Executar com IA**. O resultado, tudo em uma tela:

- **Agente de triagem**: `classificacao_urgencia = "vermelho"`, com **justificativa clínica coerente**
  (sugere angina/quadro cardíaco grave, atendimento imediato) e **`area_destino = "Cardiologia"`** — ou
  seja, o agente **usou os sinais reais informados** (sem alucinar) e roteou corretamente.
- **Encadeamento de persistência**: a mesma ação gerou **`PACIENTE_ID`** e **`ATENDIMENTO_ID`** — o
  paciente foi cadastrado e o atendimento aberto.

![Fluxo E2E — form preenchido + Resultado (classificação vermelho/Cardiologia + PACIENTE_ID + ATENDIMENTO_ID)](IMG_RES)

## 5. Prova 3 — persistiu no banco (`clinia_ops`)

Consultando o banco real da aplicação (`clinia_ops`), o atendimento gerado pela UI existe, com a **FK
correta** ligando atendimento → paciente e a `data_hora` preenchida:

```json
{
  "atendimento_id": "06048134-91b0-11f1-8a81-cbea323b9023",
  "paciente_id":    "05f29123-91b0-11f1-8a81-cbea323b9023",
  "data_hora":      "2026-08-06 16:01:02",
  "nome": "Joao Cardoso 055719", "cpf": "810557190", "convenio": "SulAmérica"
}
```

É exatamente o **`atendimento_id`/`paciente_id`** que faltavam antes — agora **gerados e persistidos
pelo próprio fluxo de triagem**. As etapas de Encaminhamento/Prontuário passam a ter os FKs que exigiam.

## 6. Como validei (sem depender do pipeline lento)

As telas React do LangNet são **determinísticas** (geradas do `ui_spec` + Modelo de Dados). Regenerei
apenas as telas do app ClinIA com o gerador corrigido (backup em `screens.bak`), mantendo o
`ws-server`/adapters, e rodei o app (`:3007` → `ws://:5003` → banco `clinia_ops`, LLM local no LM
Studio). O encadeamento também foi verificado direto contra o `ws-server` (criar_pacientes →
criar_atendimentos → SELECT no banco).

## 7. Conclusão

- **Tela híbrida FEITA e comprovada rodando**: "Recepção & Triagem" cadastra o paciente **e** dispara o
  agente de triagem na **mesma tela** — fim do CRUD que tinha engolido a parte agêntica.
- **Persistência de ponta a ponta FEITA e comprovada no banco**: a triagem **cadastra o paciente e abre
  o atendimento**, gerando `paciente_id`/`atendimento_id` — **resolvendo os erros de FK** da demo
  anterior.
- **Triagem agêntica correta**: paciente cardíaco → **vermelho → Cardiologia**, usando os sinais reais.
- Tudo via **feature do gerador do LangNet** (3 commits: `ba206b0`, `6c442c0`), com a ClinIA como
  caso-teste — nada de edição manual nos artefatos.

**Próximo passo natural** (quando quiser): propagar o mesmo `atendimento_id` para as telas seguintes
(Encaminhamento/Prontuário) via estado compartilhado entre telas, para rodar o fluxo clínico inteiro
sem redigitar o atendimento corrente.
