# E2E do app gerado (uso do solo) — achados de runtime

**Data:** 25/08/2026
**Contexto:** deploy + execução do app gerado (code_gen `8bacb9e3`), 110 arquivos, contra PostGIS `uso_solo_app`.

## O que FUNCIONOU
- App deploya e roda (ws-server em `ws://127.0.0.1:5021`).
- **PostGIS com dados reais**: lote + APP com geometrias SIRGAS 2000 sobrepostas; `ST_Intersects=True`, sobreposição **209.796 m²** (via `ST_Intersection`/`ST_Area`, no caminho determinístico do adapter). O núcleo geoespacial funciona.

## Achado principal: CrewAI 0.150 vs 1.15.17 (a questão do tool use do qwen3.8)
- **O qwen3.8-27b faz function-calling NATIVO perfeitamente** (provado na API: `tool_calls=[Function(name='ping_tool')]`, `finish=tool_calls`).
- **CrewAI 0.150** (a versão que o app usava): no loop do agente (`crew_agent_executor._invoke_loop`) chama `get_llm_response(...)` **sem `tools=`** — usa ReAct em TEXTO. Com o qwen3.8 isso retorna vazio na continuação (o CrewAI embute a `Observation` na mensagem do assistant, quebrando o turno do chat template).
- **CrewAI 1.15.17** (última): `_invoke_loop` checa `supports_function_calling()` e usa `_invoke_loop_native_tools()` que passa `tools=openai_tools`. **Provado**: CrewAI 1.15.17 + qwen3.8 + tool → `tool_calls=['ping_tool']` → executa → `RESULT: 'pong'`. ✅
- Conclusão: **a incompatibilidade era do CrewAI 0.150, NÃO do modelo.** Fix = pinar `crewai>=1.15`.

## Cascata de bugs de runtime do app gerado (corrigidos ao vivo no deploy)
1. **crewai>=0.30.0** frouxo → instalou a 0.150 (do sistema). Deve pinar **>=1.15**.
2. **ws-server chama `crew.kickoff` via `run_in_executor`** (thread) → crewai 1.x quebra (`RuntimeError: no running event loop`). Fix: **`await crew.kickoff_async()`** quando existir.
3. **`database_tool.py` passa `connection_timeout=10`** (opção do mysql-connector) ao `psycopg2.connect` → `invalid connection option`. Fix: **`connect_timeout`**.
4. **`database_tool.py` passa `autocommit=False`** ao `psycopg2.connect` (inválido; é atributo da conexão) → `invalid connection option "autocommit"`. Fix: **remover do connect**.
5. **Agente escreve SQL com placeholder `%s` sem passar params** → `column "s" does not exist`. Fragilidade de "LLM escreve SQL parametrizado".

## Ponto arquitetural (bug 5)
Cada task tem uma função **`_deterministic`** com o SQL correto e parametrizado (o `ST_Intersects` real). O caminho agêntico depende do LLM montar o SQL, e ele erra o binding. Robusto: o gerador **preferir o determinístico** para data-tasks (SQL/espacial), reservando o agêntico para tasks de decisão.

## Fixes a aplicar NO GERADOR (langnet)
- [ ] Pinar `crewai>=1.15` no `requirements.txt` emitido do ws-server.
- [ ] Emitir `kickoff_async` (fallback para `kickoff` em executor) no `websocket_server.py`.
- [ ] Emissor do `database_tool.py` dialeto-consciente (psycopg2: `connect_timeout`, sem `autocommit` no connect).
- [ ] Data-tasks (SQL/espacial) rodarem pelo caminho determinístico por padrão.

> Nota: o E2E provou o propósito geoespacial (PostGIS + ST_Intersects real com dado real) e destravou definitivamente a questão do CrewAI/tool use do qwen3.8.

## Decisão sobre o bug 5 (agent-SQL) — Opção B
Manter o caminho agêntico, mas **expor cada função `_deterministic` como uma TOOL de alto nível**
(ex.: `calcular_sobreposicao_app(lote_id)`) que por dentro roda o SQL determinístico correto.
O agente decide QUANDO chamar (function-calling nativo, destravado pela crewai 1.15), e o SQL
espacial fica na tool (não é o LLM que escreve `%s`). Alinha com a filosofia "Attested Computation":
agente orquestra/raciocina, camada determinística executa. A implementar no gerador.
