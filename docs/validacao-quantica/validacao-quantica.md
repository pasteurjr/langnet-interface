# Relatório de Validação de Rastreabilidade — Projeto Quântica Comercial

**Framework LangNet** · Validação ponta-a-ponta da cadeia de artefatos
**Data:** 20/07/2026
**Projeto:** Comercial Quântica (`b55ef718-0073-44d4-b279-11df89403e92`)
**Documento-fonte:** `20260615_031035_quantica-comercial-brief.md`

> Nota metodológica: a Quântica Comercial é a **instância de teste** do LangNet — não é o
> produto. Este relatório valida se os artefatos que o pipeline produziu para ela estão
> encadeados e coerentes, e serve de prova de campo para as correções de rastreabilidade
> implementadas nesta sessão.

---

## 1. Sumário executivo

O pipeline da Quântica tem **11 etapas** encadeadas, do documento inicial ao código Python.
A validação percorreu cada etapa lendo, no banco `langnet`, **qual sessão e qual versão** de
cada fonte originou cada artefato.

**Veredito:** a **espinha dorsal do pipeline (etapas 0–8) está coerente** — todos os artefatos,
do documento à `tasks.yaml`, apontam para a **mesma Especificação atual** (`fbc45992`, 06/jul) e
para a **mesma cadeia Agent-Task Spec** (`3c69a8a8`). As **3 etapas finais (Sequência de Tarefas,
Rede de Petri, Geração de Código)** apresentam incoerências de encadeamento, todas
**diagnosticadas com precisão** neste relatório (§4) — duas delas com **correção retroativa
bloqueada** por restrições de ambiente (§5), o que exige uma decisão do usuário.

Em paralelo, foram implementadas, testadas e versionadas **4 correções estruturais** no
código do LangNet (§6) que passam a **gravar a proveniência (sessão + versão de cada fonte)**
em toda geração futura — eliminando, dali em diante, a causa-raiz das incoerências encontradas.

---

## 2. A cadeia de rastreabilidade da Quântica

Cada linha mostra a **sessão mais recente e útil** de cada etapa e a **origem que ela declara**.

| # | Etapa | Sessão atual | Data | Origem declarada (sessão) | Versão gravada? | Coerência |
|---|-------|--------------|------|---------------------------|-----------------|-----------|
| 0 | Documento | `quantica-comercial-brief.md` | 15/jun | — (upload) | — | raiz |
| 1 | Requisitos | `9670f599` **v2** | 06/jul | documento | ✅ v2 | ✅ |
| 2 | Especificação | `fbc45992` | 06/jul | requisitos `9670f599` **v2** | ✅ v2 | ✅ |
| 3 | Modelo de Dados | `6f7183e6` | 06/jul | spec `fbc45992` | ⚠️ NULL (pré-fix) | ✅ |
| 4 | Casos de Teste | `bafc7b1d` (aprovado) | 18/jul | spec `fbc45992` | ✅ v1¹ | ✅ |
| 5 | Interface (ui_spec) | `2bfaaa3b` | 17/jul | spec `fbc45992` + data model `6f7183e6` | ⚠️ NULL (pré-fix) | ✅ |
| 6 | Agent-Task Spec | `3c69a8a8` | 13/jul | spec `fbc45992` **v1** | ✅ v1 | ✅ |
| 7 | agents.yaml | `74c29bb8` | 13/jul | agent_task_spec `3c69a8a8` **v1** | ✅ v1 | ✅ |
| 8 | tasks.yaml | `220d034e` | 16/jul | agent_task_spec `3c69a8a8` **v1** | ✅ v1 | ✅ |
| 9 | **Sequência de Tarefas** | `148e9abd` | **03/jul** | spec **`c16f3bc9`** (antiga) + ats **`767146de`** (antigo) + tasks **`1dba3682`** (antigo) | ⚠️ NULL | ⚠️ **DEFASADA** |
| 10 | **Rede de Petri** | `project_data` (vh v1/v2) | 19/jul | **nenhuma** (2 versões `manual_edit`) | ⚠️ NULL | ⚠️ **SEM PROVENIÊNCIA** |
| 11 | **Geração de Código** | `33b67c61` | 17/jul | agents `74c29bb8` ✅ + tasks `220d034e` ✅ + agent_task_spec `3c69a8a8` ✅ + **flow `NULL`** | ⚠️ NULL (pré-fix) | ⚠️ **NÃO USOU A SEQUÊNCIA** |

¹ A sessão de Casos de Teste `cd483e4c` (draft, 20/jul) foi gerada durante o **teste da correção
Etapa 1** desta sessão e **gravou corretamente** `specification_version = 1` — primeira prova de
campo do novo mecanismo de proveniência.

### 2.1 Representação da cadeia

```
[Documento] quantica-comercial-brief.md
     │
     ▼
[Requisitos] 9670f599 v2
     │
     ▼
[Especificação] fbc45992 ──────────────┬───────────────┬──────────────────┐
     │                                  │               │                  │
     ▼                                  ▼               ▼                  ▼
[Modelo de Dados] 6f7183e6      [Casos de Teste]  [Interface] 2bfaaa3b  [Agent-Task Spec] 3c69a8a8
     │                            bafc7b1d              │  (usa data model 6f7183e6)  │
     └────────────────────────────────────────────────►┘                             │
                                                                          ┌───────────┴───────────┐
                                                                          ▼                       ▼
                                                                   [agents.yaml] 74c29bb8   [tasks.yaml] 220d034e
                                                                          │                       │
                                                                          └───────────┬───────────┘
                                                                                      ▼
                                                                          [Geração de Código] 33b67c61
                                                                                      ▲
                          ⚠️ [Sequência de Tarefas] 148e9abd (defasada, cadeia antiga c16f3bc9)
                                     ── não conectada ao código (flow = NULL) ──┘

                          ⚠️ [Rede de Petri] project_data (edição manual, origem desconhecida)
```

---

## 3. O que está coerente (etapas 0–8)

- **Uma única Especificação corrente.** Modelo de Dados, Casos de Teste, Interface e Agent-Task
  Spec apontam todos para `fbc45992` — não há divergência de spec entre os consumidores diretos.
- **A Interface amarra as duas fontes certas:** spec `fbc45992` **e** modelo de dados `6f7183e6`
  (ambos correntes) — a tela de negócio foi desenhada sobre o schema atual.
- **Cadeia YAML consistente:** Agent-Task Spec `3c69a8a8` → `agents.yaml` `74c29bb8` e
  `tasks.yaml` `220d034e`, ambos declarando `agent_task_spec_version = 1`.
- **A Geração de Código usa o topo correto da cadeia:** `agents.yaml`, `tasks.yaml` e
  `agent_task_spec` correntes.

---

## 4. Incoerências encontradas

### 4.1 [ALTA] Sequência de Tarefas defasada
A última Sequência de Tarefas **completa** (`148e9abd`, **03/jul**) foi gerada de uma cadeia
**anterior**: spec `c16f3bc9` (a antiga, não a `fbc45992`), agent_task_spec `767146de` (antigo,
não `3c69a8a8`) e `tasks.yaml` `1dba3682` (antigo, não `220d034e`). Ela **antecede** o
Agent-Task Spec/agents/tasks atuais (13–16/jul) — logo, descreve um fluxo de execução de uma
versão anterior do sistema.

### 4.2 [ALTA] Código não incorporou a Sequência de Tarefas
A sessão de código corrente (`33b67c61`) tem `task_execution_flow_session_id = NULL` — foi gerada
**sem** a Sequência de Tarefas. O executor de Petri foi montado a partir de agents/tasks/petri,
mas o **fluxo de execução planejado** (ordem, paralelismo) não entrou como insumo.

### 4.3 [MÉDIA] Rede de Petri sem proveniência
A Petri vive em `projects.project_data` e tem 2 versões no histórico, ambas `manual_edit`
(19/jul), **sem vínculo** com agents.yaml/tasks.yaml/Sequência que a originaram. Não é possível,
retroativamente, saber de qual versão das fontes ela derivou.

### 4.4 [BAIXA] Versões NULL em artefatos anteriores ao fix
Modelo de Dados (`6f7183e6`), Interface (`2bfaaa3b`) e Código (`33b67c61`) têm as colunas de
versão da origem em NULL — foram gerados **antes** das correções desta sessão. O **vínculo de
sessão** existe e está correto; falta apenas o número da versão, que passa a ser gravado dali em diante.

---

## 5. Correção das incoerências — status e bloqueios

A instrução foi "se não estiverem coerentes, corrija". A correção natural é **regenerar** os
artefatos da cauda a partir da cadeia atual. Isso esbarra em dois obstáculos reais:

### 5.1 Regenerar a Sequência de Tarefas — BLOQUEADO pelo contexto do LLM
Tentativa realizada nesta sessão (sessão `d32dea7e`): **falhou** com
`Error 400 - Context size has been exceeded`. As três fontes somam **~33,6K tokens** de entrada
(Especificação 20,7K + Agent-Task Spec 9,6K + tasks.yaml 3,2K), acima da janela do
**qwen2.5-coder-32b** carregado no LM Studio (~32K). É exatamente o cenário anti-timeout já
registrado na memória do projeto.
**Opções (decisão do usuário):** (a) carregar o modelo no LM Studio com janela maior (≥48K);
(b) dividir a task de geração do fluxo em subtasks menores (padrão já usado no pipeline de
especificação); (c) usar LLM de nuvem — **descartado** por decisão prévia do usuário.

### 5.2 Regenerar a Rede de Petri — RISCO de perda de edições manuais
A Petri corrente tem **2 versões `manual_edit`** (trabalho manual do usuário). Uma nova geração
via LLM **sobrescreveria** `project_data`. Regenerar só para preencher colunas de proveniência é
um mau negócio. **Decisão do usuário:** manter a Petri atual (proveniência retroativa fica
indisponível, mas a próxima geração via UI já grava tudo — Etapa 3) **ou** aceitar regenerar e
perder as edições manuais.

### 5.3 O que já foi corrigido de forma definitiva
A causa-raiz — **o pipeline não gravava a versão das fontes** — foi corrigida no código do LangNet
(§6). Toda geração **futura** de qualquer etapa passa a gravar a proveniência completa; a sessão
de Casos de Teste `cd483e4c` (§2, nota 1) já comprova isso em campo.

---

## 6. Correções estruturais implementadas (código do LangNet)

Quatro etapas, cada uma com **backup do banco + commit + push + teste** antes de avançar:

| Etapa | Commit | Migration | O que passou a ser gravado | Teste |
|-------|--------|-----------|----------------------------|-------|
| 1 — Consumidores da Especificação | `8f1b143` | 023–025 | `specification_version` em Modelo de Dados, Casos de Teste e Interface (+ `data_model_version` na Interface) | Casos de Teste nova gravou `specification_version=1` |
| 2 — Sequência de Tarefas | `a08bc4c` | 026 | `specification_version`, `agent_task_spec_version`, `tasks_yaml_version` | Geração gravou `1/1/1` |
| 3 — Rede de Petri | `ea23ab4` | 027 | sessão+versão de agents.yaml, tasks.yaml e Sequência de Tarefas | Insert real gravou agents v1 + tasks v1 |
| 4 — Geração de Código | `78bd9d1` | 028 | versão das 4 fontes + versão da Petri usada + sessão/versão do ui_spec | Insert real: agents v1, tasks v1, spec v1, petri v2, ui_spec capturado |

Padrão comum: cada geração lê `MAX(version)` da `*_version_history` da fonte e carimba na
linha do artefato. Camada **aditiva e tolerante a falha** — versionamento nunca quebra a geração.

---

## 7. Recomendações

1. **Decidir sobre a Sequência de Tarefas (§5.1)** — sem isso, a cauda do pipeline permanece
   descolada da cadeia atual. Recomendação: aumentar a janela do LM Studio para ≥48K e regenerar;
   isso reconecta Sequência → Petri → Código com proveniência completa (validando as Etapas 2–4
   em geração real de ponta a ponta).
2. **Após a Sequência, regenerar o Código** passando `task_execution_flow_session_id` (corrige §4.2).
3. **Ao evoluir a Petri**, fazê-lo pela UI (Gerar Rede) para nascer com proveniência (Etapa 3),
   preservando a decisão do usuário sobre as edições manuais atuais (§5.2).
4. **Próxima feature de rastreabilidade:** exibir na UI o rótulo "gerado de: {fonte} v{n}" em cada
   etapa, consumindo as novas colunas — fecha o ciclo tornando a proveniência visível ao usuário.
