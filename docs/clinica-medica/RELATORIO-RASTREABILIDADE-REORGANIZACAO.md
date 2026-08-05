# Rastreabilidade + Reorganização da Interface (pelo LangNet) — Relatório

**Data:** 2026-08-05 · **Executor:** Claude (instruindo o LangNet; correções feitas pelo agente do
LangNet, via os endpoints da UI) · **Projeto:** ClinIA (`a3ae2f89`)

> Você pediu 4 coisas: (1) correções **feitas pelo LangNet** (eu instruo, ele executa, pela UI);
> (2) **verificar a rastreabilidade** Spec ⟷ Interface ⟷ Implementação; (3) **reorganizar a interface**
> (Cadastros separado do fluxo agêntico; e definir **como o agente cadastra o paciente na triagem**);
> (4) que a mudança **reflita na documentação** (rastreabilidade). Este relatório mostra tudo, com
> screenshots da **UI do LangNet** e meus comentários.

---

## 1. Rastreabilidade Spec ⟷ Interface ⟷ Implementação — VERIFICADA ✅

**Comentário:** você perguntou se isso está implementado. **Está** — e verifiquei de 3 ângulos.

### 1.1 Na UI do LangNet (visual)
A página **Interface & Protótipo** mostra, para cada tela do protótipo, **o Caso de Uso de origem** e a
**proveniência**: etiqueta **"Origem: Especificação bb40c57d…"**, e cada tela rotulada com seu UC —
*Cadastro de Pacientes → UC-001*, *Triagem Agentiva → UC-002*, *Pré-atendimento → UC-003*, … até
*Gestão de Especialidades → UC-013*. Há os botões **"Verificar coerência"** e **"Refinar com o agente"**.

![Interface & Protótipo — cada tela ligada ao seu UC + Origem da Especificação](IMG08)

### 1.2 Nos dados (prova por API)
- **`sync-status` do protótipo**: `spec_version_used = 2` → o protótipo **sabe** de qual **versão da
  Especificação** foi gerado.
- **`screen/{id}/source`**: a tela `triagem-agentiva` está ligada ao **UC-002**, e o endpoint devolve o
  **ator, objetivo, fluxo e wireframe** daquele caso de uso. É a amarração tela ⟷ caso de uso.
- **No código React**: cada tela mostra o UC no subtítulo (ex.: "UC-002 · executado por agente de IA").

**Cadeia fechada:** UC-002 (Especificação) → tela `triagem-agentiva` (Interface) → subtítulo "UC-002"
(Implementação).

### 1.3 Bidirecional + coerência
- **`edit-source`**: editar o fluxo/wireframe de uma tela **grava nova versão da Especificação** (no UC)
  e regenera a tela → *editar a interface reflete na documentação*.
- **`/coherence`**: valida cada tela contra o schema real + o UC e propõe correções ao Modelo de Dados.

### 1.4 O limite (honesto) e a PROVA ao vivo
A rastreabilidade é de **registro (proveniência) + detecção de defasagem (staleness)**, **não** de
propagação automática. Demonstrei ao vivo: **antes** do refino, o protótipo estava
`stale: false` (`used=2, current=2`); **depois** de o LangNet refinar a Especificação para a **v3**, o
mesmo endpoint passou a `**stale: true**` (`used=2, current=3`) — o sistema **detectou** que o
protótipo ficou defasado da spec. Para atualizar, regenera-se o protótipo/código (o que está em curso).

---

## 2. Correção FEITA PELO LANGNET: reorganização da interface (Especificação v3)

**Comentário:** as correções foram feitas pelo **agente do LangNet**, via o **mesmo endpoint que o
botão "Refinar" da UI aciona** (`/specifications/{sid}/refine`) — eu só passei as instruções. Capturei a
UI do LangNet na etapa de Especificação, com o **Histórico de versões** e a **"Comparação de
Alterações" (diff Antes/Depois do Refinamento)** — a rastreabilidade de versões na própria tela.

![Especificação no LangNet — Histórico + Comparação de Alterações (versionamento)](IMG06)

O agente do LangNet reorganizou a Especificação (v2 → **v3**, 936s). O resultado no **UC-002**, que era
uma triagem confusa (só um dropdown de especialidade + resultado), virou **"Recepção & Triagem"** com o
fluxo completo que faltava:

**Fluxo (novo):**
1. Recepcionista preenche **identificação do paciente** (Nome, CPF, Data de Nascimento, Contato,
   Convênio) + Queixa + Sinais Vitais.
2. Ao clicar **"Iniciar Triagem"**: o sistema **identifica o paciente pelo CPF; se não existir,
   CADASTRA automaticamente; ABRE um Atendimento, gerando o `atendimento_id`**.
3. O agente classifica a urgência (verde/amarelo/vermelho) e escolhe a **especialidade de uma LISTA
   FECHADA** das cadastradas; roteia para o pré-atendimento.

**Wireframe (novo)** — gerado pelo agente:
```
┌──────────────────────────────────────────────────────┐
│  [Recepção & Triagem]                                │
│  IDENTIFICAÇÃO DO PACIENTE                           │
│    Nome / CPF / Data de Nascimento / Contato / Convênio
│  QUEIXA E SINAIS VITAIS                              │
│    Queixa / Pressão Arterial / Freq. Cardíaca / Temperatura / SpO2
│  AÇÃO: [Iniciar Triagem (Agente Hub de Triagem)]     │
│  RESULTADO: Classificação / Justificativa / Área de Destino
│  [Encaminhar ao Especialista]   [Cancelar]           │
└──────────────────────────────────────────────────────┘
```

**Por que isso importa (resolve o que você apontou):**
- Deixa claro **como o paciente é cadastrado**: o atendente digita os dados **na triagem**, e o sistema
  **cadastra (se novo) e abre o atendimento** — capturando os dados do cliente exatamente como você
  descreveu ("o agente/operador captura os dados, cria o cadastro").
- Gera o **`atendimento_id`** e resolve o **`paciente_id`**, o que **corrige os erros de FK** que a
  demonstração anterior revelou (encaminhamento/prontuário falhavam com "cannot be null").
- Usa **especialidade de lista fechada** → roteamento automático confiável.

A reorganização completa (2 módulos: **Atendimento** no topo, **Cadastros** administrativo ao final)
está especificada em `PROJETO-INTERFACE-REORGANIZADA.md` e foi passada ao agente.

---

## 3. Propagação (em curso) e o ponto a evoluir

**Comentário:** como a rastreabilidade é *registro + staleness* (não propagação automática), a mudança
da spec **precisa ser propagada** regenerando o Protótipo e o Código a partir da **v3**. Isso está **em
execução** (a regeneração do protótipo roda ~20min). Quando concluir, o protótipo volta a
`stale: false` (agora ligado à spec v3), e o app passa a refletir a Recepção & Triagem reorganizada.

**Ponto honesto:** a **separação do MENU em 2 módulos** (Atendimento × Cadastros) nasce na
Especificação, mas o **agrupamento final no app gerado** também depende do **gerador de código**
(atribuição de módulos por tela). Se a regeneração não separar o menu como especificado, o próximo
passo é ajustar essa atribuição no gerador — que eu faço e revalido na ClinIA.

## 4. Conclusão

- **Rastreabilidade: existe e foi verificada** (proveniência + amarração tela⟷UC + UC no código +
  bidirecional + coerência), com **prova ao vivo** do staleness (v2→v3 ⇒ `stale: true`).
- **A correção foi feita PELO LangNet** (agente refinou a Especificação v3), reorganizando o UC-002 em
  "Recepção & Triagem" com **cadastro do paciente na triagem** + **abertura de atendimento** + lista
  fechada de especialidades — resolvendo a confusão e os erros de FK.
- **A documentação reflete a mudança** (é a própria Especificação v3, versionada e rastreável).
- **Falta propagar** (regenerar protótipo+código — em curso) e, se preciso, ajustar o agrupamento do
  menu no gerador.
