# Plano de Correções (residuais) do Gerador — validado sobre a ClinIA

**Contexto:** a validação do ciclo completo (ClinIA) rodou 13/13 e corrigiu **6 bugs já commitados no
gerador** (extração de requisitos, refino por seção, Petri truncada, DeepSeek→local, KeyError de
formatação, fallback de código). Restam **falhas de qualidade do gerador de CÓDIGO** — a app compila e
roda, mas algumas telas não saem no formato certo. Este plano ataca essas.

**Como testamos (todas):** as sessões do pipeline da ClinIA já existem. Para cada fix:
1. Corrigir no gerador (`backend/agents/langnetagents.py`), com **commit+push "ANTES de…"**.
2. **Regenerar só o Código** da ClinIA (endpoint `/code-generation/{pid}/generate`, ~2-3 min).
3. Reconstruir a app em `/home/pasteurjr/clinia-app`, reiniciar ws-server (:5003) + frontend (:3002).
4. **Verificar a tela/comportamento específico** (critério de aceite abaixo) e capturar screenshot.
5. Regredir: confirmar que as telas que já funcionavam continuam boas.

---

## Falha 1 — Telas agênticas renderizam como "painel de KPIs" (não Entrada→Ação→Resultado)

- **Sintoma (ClinIA):** a **Triagem Agentiva** (UC-002) saiu como painel: cards readonly (Paciente,
  Queixa, Pressão, Frequência) + dropdown Especialidade + botão **"Atualizar"**.
- **Esperado:** **ENTRADA** editável (queixa, sinais vitais) → **AÇÃO** botão **"Classificar com IA"**
  (indicando o Agente Hub) → **RESULTADO DO AGENTE** (classificação verde/amarelo/vermelho +
  justificativa + área roteada) → botão **"Encaminhar ao Especialista"**.
- **Causa:** o refino que o 32B fez na Especificação (Entrada→Ação→Resultado) **não é lido** pelo
  gerador; `_agent_screen` (langnetagents.py:5695) monta um painel de cards a partir dos componentes
  readonly, sem o bloco entrada/ação/resultado.
- **O que corrigir:** `_agent_screen` + `_react_component_for_screen` — separar componentes editáveis
  (ENTRADA) de readonly (RESULTADO), renderizar o botão de ação com o rótulo do agente, e a seção de
  resultado do agente. Ler a intenção do UC (a área de destino como saída roteada).
- **Prioridade:** **P0** (é o coração do valor — "não é só CRUD"; é a tela que executa a triagem).
- **Aceite na ClinIA:** Triagem mostra campos editáveis + "Classificar com IA" + resultado + "Encaminhar".

## Falha 2 — Telas "Gestão de X" (CRUD) classificadas como agênticas

- **Sintoma (ClinIA):** **Gestão de Agentes** (UC-012) saiu com "Executar com IA" e **"Tarefa não
  definida para esta tela"** — deveria ser um CRUD com tabela + ações.
- **Esperado:** tabela (colunas reais) + busca + [+ Novo] + ações por linha (Ver/Editar/Excluir) + form.
- **Causa:** `_classify_screen` (langnetagents.py:5132) — a heurística `readonly and not editable` (ou
  `kind=dashboard`) classifica como `agent` telas que na verdade são cadastros; várias "Gestão de X"
  caíram nesse balde.
- **O que corrigir:** refinar `_classify_screen` — quando a tela tem **entidade** correspondente no
  schema e o UC é de gestão/cadastro (verbo gerir/gestão/cadastrar/CRUD), classificar como **crud**
  mesmo que os componentes tenham vindo readonly; só manter `agent` para os UCs realmente agênticos
  (triagem, pré-atendimento, pré-diagnóstico, encaminhamento, dashboard).
- **Prioridade:** **P0** (metade das telas de cadastro afetadas).
- **Aceite na ClinIA:** Gestão de Agentes/Especialidades/Médicos/Pacientes mostram tabela com dados.

## Falha 3 — Adapters CRUD `listar_*`/`excluir_*` não gerados (#9)

- **Sintoma (ClinIA):** ws-server responde "task 'listar_pacientes' não definida" — só existiam
  `cadastrar/atualizar/criar_encaminhamento/registrar_prontuario_deterministic`. (Contornado com um
  `__getattr__` genérico manual no artefato — patch de demo, não no gerador.)
- **Esperado:** o gerador emite `listar_<ent>_deterministic` e `excluir_<ent>_deterministic` para toda
  entidade do schema, dentro do próprio `adapters.py`.
- **Causa:** `_generate_crud_adapters` (langnetagents.py:3465, chamado em :4939) não completou o
  conjunto no caminho de **fallback** (bug #8) — provável que as entidades não tenham sido derivadas do
  schema, ou o dedup `_existing_fns` tenha barrado a geração.
- **O que corrigir:** garantir que `_generate_crud_adapters` derive as entidades do `schema_sql` e
  emita listar_/excluir_ para todas, independentemente do caminho (CrewAI normal ou fallback direto).
- **Prioridade:** **P0** (sem isso a app não lista nada sem o patch manual).
- **Aceite na ClinIA:** app lista pacientes/médicos/especialidades **sem** o patch `__getattr__`.

## Falha 4 — Cara B (Admin/Petri) fica "Carregando projeto…"

- **Sintoma (ClinIA):** a aba **Admin / Petri** não carrega — o viewer busca `project.json` via HTTP
  (proxy `:8001`) que a app gerada não sobe.
- **Esperado:** o canvas da Petri carrega (16 lugares/16 transições) a partir do `project.json` gerado.
- **Causa:** a app gerada não inclui um servidor estático para `project.json`/`petri_net.json`; o
  front assume um backend em `:8001`.
- **O que corrigir (opções):** (a) o gerador emitir um micro-servidor estático (ou servir via
  ws-server) para `project.json`; ou (b) embutir o `project.json` no build do front; ou (c) ajustar o
  proxy/caminho. Escolher a mais simples e coerente com o padrão visualtasksexec.
- **Prioridade:** **P1** (a Petri já foi gerada e provada no pipeline; é a visualização que falta).
- **Aceite na ClinIA:** aba Admin/Petri mostra o grafo com os lugares/transições/agentes.

## Falha 5 — Event loop bloqueado em geração pesada (#2)

- **Sintoma:** durante geração longa (Especificação/Petri), o backend :8000 fica sem resposta (timeout
  transitório); pode derrubar drivers.
- **Esperado:** o backend continua respondendo enquanto uma geração roda.
- **O que corrigir:** rodar as chamadas de LLM/CrewAI em thread pool (`run_in_executor`) nos endpoints
  síncronos pesados, para não bloquear o event loop do FastAPI.
- **Prioridade:** **P2** (robustez; mitigado nos drivers com retry).
- **Aceite:** durante uma geração, `GET /api/projects` responde < 1s.

## Falha 6 — LM Studio serve 4096 por auto-unload/JIT (#4, AMBIENTE)

- **Sintoma:** o modelo caía para contexto 4096 após ociosidade, travando etapas.
- **Status:** mitigado com **keep-alive** (ping a cada 55s) + ajuste do usuário (desativar auto-unload
  / fixar contexto). Não é bug do LangNet.
- **Prioridade:** **P2** (documentar como pré-requisito operacional; opcionalmente o LangNet pode ter
  um preflight de contexto que avisa cedo).

---

## Ordem sugerida de execução (tudo testado na ClinIA)

1. **P0 — Falha 3** (adapters CRUD): destrava a listagem "de verdade" (sem patch). Rápido.
2. **P0 — Falha 2** (classificação de telas): as Gestões viram CRUD com tabela.
3. **P0 — Falha 1** (telas agênticas Entrada→Ação→Resultado): a mais valiosa e a mais trabalhosa.
4. **P1 — Falha 4** (Cara B / Petri viewer).
5. **P2 — Falhas 5 e 6** (robustez/ambiente), se valer a pena.

**Marco de aceite final:** regenerar a ClinIA com o gerador corrigido e rodar a app mostrando: CRUDs
com tabela+dados, Triagem no formato Entrada→Ação→Resultado, e a Petri visualizável — **sem patches
manuais no artefato**.
