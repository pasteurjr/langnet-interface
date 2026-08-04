# Correções encontradas na validação do ciclo completo (ClinIA)

> Este arquivo registra os **bugs do LangNet encontrados e corrigidos** durante a validação
> ponta a ponta (projeto de teste: Clínica Médica com triagem por agentes). Cada correção segue
> a regra: **commit+push de checkpoint ANTES** (com data/hora) → correção → commit da correção.
> Alimenta o relatório final.

---

## Bug #1 — Requisitos concluíam com documento VAZIO

**Etapa:** Requisitos (`generate_document`)
**Sintoma:** a geração rodava por ~18 min, o modelo local (qwen2.5-coder-32b) produzia um
documento de requisitos rico e específico da clínica (31 FRs, 17 NFRs, 9 BRs — visíveis no log),
mas o documento **salvo no banco tinha tamanho 0** e a etapa ficava presa em HTTP 404
("Requirements document not yet generated"), travando todo o pipeline logo na 1ª etapa.

**Causa raiz:** `generate_document_output_func` (backend/agents/langnetagents.py). O CrewAI devolve
o resultado embrulhado em `team_result` como uma **string JSON**. Ao serializar um markdown grande
como valor de string JSON, o modelo local não escapa perfeitamente (aspas e quebras de linha
literais, às vezes truncamento). O `json.loads` do JSON aninhado falhava e o regex de fallback
tentava `json.loads('"'+trecho+'"')`, que também falhava por causa de newline literal → resultado
**vazio**. O conteúdo existia, mas o parser não o recuperava.

**Correção:** novo `_extract_md_field_lenient()` — um extrator char-a-char que:
- localiza a chave `requirements_document_md` (aceita a chave escapada `\"...\"` do envelope);
- lê o valor tolerando **aspas não escapadas** no conteúdo (só encerra em `"` seguido de `,`/`}`),
  **newlines literais** e **truncamento** (lê até o fim se o JSON não fechar);
- desescapa `\n \t \r \" \\ \uXXXX`.
Fluxo novo: parse limpo → extrator leniente(team_result) → extrator leniente(output_json) →
dump do raw em `failed_generate_document_raw.txt` para diagnóstico se ainda vazio.
Testado em 4 casos (bem-formado / aspas não escapadas / newline literal+truncado / chave escapada).

**Commits:**
- `CHECKPOINT 2026-08-03 14:47 — ANTES de: corrigir extração de requirements_document_md`
- `FIX Requisitos: extrator leniente p/ requirements_document_md (team_result malformado)`

**Verificação (✅ CONFIRMADA):** re-execução do pipeline (projeto `a3ae2f89`, sessão de requisitos
`e160540b`) com o backend recarregado — `FINAL requirements_doc_md length: 67599` (antes: **0**),
driver: `REQUISITOS OK, 67775 chars`, artefato `01-requisitos.md` = 70 KB salvo, sem dump de falha.
A etapa que travava o pipeline inteiro na origem agora conclui e o chain seguiu automaticamente
para a Especificação.

---

## Achado #2 — Backend fica sem resposta durante geração pesada (event loop bloqueado)

**Etapa:** transição Especificação → Modelo de Dados
**Sintoma:** logo após a Especificação concluir (120 KB), o `POST /data-model/{pid}/generate` deu
**read timeout (60s)** e o driver abortou o chain. Segundos depois o backend voltou a responder
normalmente (200 em ~0,1s) — ou seja, **hang transitório**, não permanente.

**Causa provável:** as chamadas ao LLM local dentro das tasks assíncronas rodam de forma
**bloqueante** no event loop do FastAPI; enquanto uma geração longa está em curso, outras requisições
podem esperar além de 60s. Diferente do hang de pool já corrigido (aquele era esgotamento de conexão;
este é bloqueio de event loop).

**Ação (2 níveis):**
- **Imediata (resiliência do driver):** o driver de geração passará a **repetir POSTs com timeout maior
  e retry** em vez de abortar na 1ª leitura estourada — assim uma janela de backend ocupado não mata o
  ciclo. (Correção operacional, não altera o LangNet.)
- **Recomendação (LangNet, maior):** rodar as chamadas de LLM em thread pool (`run_in_executor`) para
  não bloquear o event loop — registrado como recomendação; mudança arquitetural com risco de
  regressão, a fazer com teste dedicado (não aplicada no meio desta validação para não desestabilizar).

---

## Bug #6 — 3 etapas forçavam DeepSeek cloud (viola a regra "nunca DeepSeek cloud") e travavam a Petri

**Etapa:** Rede de Petri (falha visível) + Requisitos + Geração de Código (mesma raiz).
**Sintoma:** a Petri falhava com `litellm.BadRequestError: DeepseekException - We were unable to start
processing your request within the 900-second timeout limit`. Ou seja, a geração da Petri estava indo
para o **DeepSeek cloud** (não o LM Studio local), e o DeepSeek não respondeu em 900s.
**Causa raiz:** três routers tinham **`use_deepseek=True` hardcoded**, e `get_llm(use_deepseek=True)`
**ignora `LLM_PROVIDER`** e força DeepSeek:
- `app/routers/petri_net.py:259` (Petri) → falhou visivelmente (DeepSeek timeout);
- `app/routers/code_generation.py:234` (Código) → usaria DeepSeek também;
- `app/routers/documents.py:200` (Requisitos) → também roteava para DeepSeek.
Isso **viola a restrição do projeto** ("nunca usar DeepSeek cloud") e explica o travamento da Petri.
(Os Requisitos "funcionaram" porque o DeepSeek estava disponível naquele momento — mas ainda assim
era o caminho errado.)
**Correção:** os três passaram a `use_deepseek=False`, respeitando `LLM_PROVIDER=lmstudio` (qwen local).
**Commits:** `CHECKPOINT ... ANTES de: Petri parar de usar DeepSeek cloud` + `FIX: pipeline respeita
LLM_PROVIDER (lmstudio) em Petri/Código/Requisitos — nunca DeepSeek cloud`.
**Verificação:** _(regenerar a Petri com lmstudio; agora o `_repair_json` do bug #5 lida com eventual
truncamento no modelo local)._

---

## Bug #7 — KeyError na formatação da descrição da task (Código)

**Etapa:** Geração de Código (`generate_python_code`).
**Sintoma:** `KeyError: '\n       "input_data"'`.
**Causa:** a descrição da task era formatada com `.format(**task_input)`, que interpreta as chaves
`{...}` dos exemplos JSON do prompt como campos de template.
**Correção:** `_safe_format_description` — substitui só placeholders válidos `{identificador}`,
deixando o JSON literal intacto. Commit: `FIX Código: KeyError na formatação...`. ✅ Verificado.

## Bug #8 — Geração de Código falhava (LLM vazio): prompt saturado + incompatibilidade CrewAI×modelo local

**Etapa:** Geração de Código. **Sintoma:** `ValueError: Invalid response from LLM call - None or empty`.
**Causa (duas camadas):**
1. **Prompt saturado (77 KB):** a Petri enriquecida (logica SQL por lugar, coordenadas, input/output_data
   dos 16 lugares) era serializada inteira no `petri_net_json`. Fix: **Petri compacta** (só estrutura) →
   prompt caiu para ~29 KB. Também `LMSTUDIO_MAX_TOKENS` 32000→16000 (32000 é otimista p/ contexto 40960).
2. **CrewAI × modelo local:** mesmo com o prompt cabendo, o **CrewAI+qwen retornava vazio** na resposta
   final do agente (que usa a tool `python_code_writer`) — enquanto **openai SDK, litellm e chamada direta
   geram o código corretamente** (provado 3×). O `crew` é um `LangGraphTeamAdapter` (método `executar()`,
   não `kickoff()`), e a exceção vinha de dentro do `executar()`.
**Correção:** **fallback direto ao LM Studio** em `execute_task_with_context` — envolve `_run_crew()`
(cobre `kickoff` E `executar`); se vier vazio e provider=lmstudio, chama `_direct_llm_complete()` com a
MESMA descrição e embrulha em `_DirectResult(.raw)` p/ o output_func processar.
**Commits:** `FIX Código: Petri compacta...` + `FIX Código: fallback direto ao LM Studio...`.
**Verificação (✅ CONFIRMADA):** log `[FALLBACK] chamada direta OK — 11477 chars`, HTTP 200, **13/13**.
A app ClinIA foi gerada completa: telas de negócio (TriagemAgentiva, PreAtendimentoEspecialista,
GeracaoPreDiagnostico, SelecaoDeMedico, GestaoDeEspecialidades/Medicos/Pacientes/Agentes…) + executor
de Petri (PetriNetSimulator, GuardEvaluator, PlaceProcessor).

---

## Bug #9 — Adapters CRUD `listar_*`/`excluir_*` não foram gerados (app não lista dados)

**Etapa:** Código (rodar a app). **Sintoma:** ao subir a app ClinIA, as telas CRUD chamam
`listar_<entidade>` (tabelas e dropdowns de FK), mas o ws-server responde *"task 'listar_pacientes'
não definida em tasks.yaml"*. O `adapters.py` gerado tinha só 4 funções determinísticas
(`cadastrar_paciente`, `atualizar_paciente`, `criar_encaminhamento`, `registrar_prontuario`) — **faltaram
os `listar_*` e `excluir_*`** de cada entidade. O `websocket_server.py` espera esses adapters
determinísticos (comentário no próprio código: "CRUD genérico listar_/atualizar_/excluir_<entidade>
que NÃO estão no tasks.yaml"), mas eles não foram emitidos.
**Causa provável:** o caminho de fallback direto (bug #8) devolveu o `adapters.py` do LLM, e a etapa
determinística `_generate_crud_adapters` (que gera listar_/excluir_ por entidade a partir do schema)
não completou o conjunto — só ficaram os adapters que o LLM escreveu.
**Mitigação (demo):** adicionei ao `adapters.py` da app um `__getattr__` que sintetiza
`listar_<ent>_deterministic`/`excluir_<ent>_deterministic` genéricos (SELECT */DELETE) — a app passou a
listar (ex.: `listar_pacientes` retorna os 3 pacientes). **É patch no artefato para a demo**, não no
gerador. **A fix correta no LangNet** é garantir que `_generate_crud_adapters` rode e complete listar_/
excluir_ para todas as entidades mesmo no caminho de fallback — registrado para corrigir depois.

---

## Achado #4 (AMBIENTE, não-LangNet) — LM Studio recarregou o modelo em 4096 (JIT), travando o Modelo de Dados

**Etapa:** Modelo de Dados (`POST /data-model/{pid}/generate`) e todas as seguintes.
**Sintoma:** `litellm.BadRequestError 400 - n_keep: 12866 >= n_ctx: 4096`.
**Investigação (empírica):** confirmado que **não é o LangNet nem o litellm**. Uma chamada pelo
**openai SDK direto** (o mesmo cliente que gerou Requisitos/Especificação com sucesso) ao
`qwen2.5-coder-32b-instruct` retorna AGORA `n_ctx: 4096`. O modelo do data model resolvido em runtime
é o correto (`openai/qwen2.5-coder-32b-instruct`, provider lmstudio, via load_dotenv OK) — não há troca
de modelo. Durante a Especificação o LM Studio servia **40960** (visto no erro daquela etapa); agora
serve **4096**.
**Causa:** comportamento de **JIT-load do LM Studio** — o modelo foi descarregado (idle TTL, ou outro
modelo carregado; a instância tem vários modelos, inclusive de vídeo `wan2.2`) e, ao ser requisitado
de novo, **recarregou no context length DEFAULT do modelo (4096)**, não nos 40960 setados manualmente.
**Ação (do usuário, na máquina 192.168.1.115):** recarregar `qwen2.5-coder-32b-instruct` com context
length 40960 (ou 32768), **desativar auto-unload/idle TTL** e mantê-lo pinado. Não corrigível daqui.
**Status:** ⏸️ pipeline pausado no Modelo de Dados aguardando o modelo voltar a 40960.

**Atualização (recorrência):** após o usuário recarregar a 40960, um teste passou (prompt ~7k tokens),
mas **em poucos minutos o contexto voltou a 4096** — confirmado que o modelo é **evictado por
ociosidade (auto-unload/idle TTL) e recarregado via JIT no default 4096** entre as etapas. Descartada
a hipótese de eviction por embeddings (o pipeline de data model **não** usa `memory=True`/embedder;
as referências a embeddings estão só no CÓDIGO GERADO, não no pipeline). Portanto **recarregar não
basta** — é preciso, no LM Studio: (1) **desativar Auto-Unload / Idle TTL** do modelo; (2) se o
**JIT loading** estiver ligado, setar o **context length do JIT = 40960** (senão o JIT recarrega em
4096); (3) manter o modelo **pinado/carregado** e evitar que outros modelos (ex.: vídeo `wan2.2`) o
expulsem por VRAM. É ajuste de ambiente (máquina do usuário), não do LangNet.
**Nota LangNet (menor, opcional):** `langnetdatamodel._get_llm` não seta `context_window` no CrewLLM;
setar ajudaria o litellm a contar tokens/truncar, mas NÃO resolve o n_ctx servido (que é do LM Studio).

---

## Bug #3 — Refino da Especificação estoura o contexto do modelo local (refino falha silencioso)

**Etapa:** Especificação → `POST /api/specifications/{sid}/refine`
**Sintoma:** ao enviar a rodada 1 de refino de interface (instruções de 3 KB), o refino foi aceito
(HTTP 200, assíncrono) mas **nunca gerou a v2**. No log:
`[SPEC REFINEMENT] Prompt built: 169660 chars` →
`openai.BadRequestError: 400 - n_keep: 41264 >= n_ctx: 40960 ("provide a shorter input")`.

**Causa raiz:** `execute_specification_refinement` (specification.py) monta o prompt com **a
especificação inteira (120 KB) + requisitos (até 45 KB) + histórico + instruções ≈ 41.264 tokens**,
acima do contexto de **40.960 tokens** do qwen local. Mesmo sem os requisitos, um doc de 120 KB
(~30 K tokens de entrada) mais a saída do doc inteiro (~30 K tokens) não cabe num contexto de 40 K —
**refino de documento inteiro numa tacada é fisicamente impossível no modelo local** para specs
grandes. (Limitação já conhecida, agora batida com doc maior.)

**Correção:** refino **por seção/UC (chunked)** dentro do endpoint. Quando a spec é grande, em vez de
uma chamada gigante: (1) divide o documento por seções `## N.` e a seção de Casos de Uso por blocos
`**UC-`; (2) refina **apenas as unidades relevantes à interface** (as que contêm "Wireframe" ou a
seção "Interfaces do Sistema"), passando o resto **inalterado**; (3) cada chamada leva só aquele
trecho + as instruções (cabe folgado no contexto); (4) se um trecho refinado vier suspeito
(curto/perdeu cabeçalho), mantém o original; (5) remonta o documento na ordem e salva como nova versão.

**Commits:**
- `CHECKPOINT 2026-08-03 21:40 — ANTES de: corrigir refino da Especificação p/ caber no contexto`
- `FIX Especificação: refino por seção/UC (chunked) p/ caber no contexto do modelo local`

**Verificação (✅ CONFIRMADA):** reenviada a rodada 1 de refino de interface com o backend recarregado.
Log: `Spec grande (120126 > 55000) → refino CHUNKED`, `33 unidades, 19 refináveis`, **sem
BadRequestError**. Resultado: **v2 criada** (725s, 19/19 unidades refinadas, 0 suspeitas). Wireframes
melhoraram: UC-013 (CRUD) ganhou tabela+busca+ações por linha+formulário; UC-002 (agêntica) ganhou
Entrada→Ação de IA→Resultado do agente+Encaminhar. Detalhes em `ANALISE-INTERFACE-SPEC.md`.

---
