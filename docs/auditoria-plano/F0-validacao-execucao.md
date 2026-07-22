# F0 — Validação de Execução do App Gerado (Quântica Comercial)

**Data:** 22/07/2026 · **Sessão de código:** `af4708e5` (55 arquivos)
**LLM:** qwen2.5-coder-32b-instruct (LM Studio local, 192.168.1.115) · **Banco do app:** `quantica_ops`

## Veredito

✅ **O aplicativo gerado RODA de verdade, ponta a ponta.** Os dois caminhos de execução
funcionam e o frontend compila. A geração do LangNet produz um sistema **executável**, não apenas
arquivos plausíveis.

## Ambiente montado

| Item | Ação |
|------|------|
| Extração | 55 arquivos da sessão `af4708e5` gravados em `~/quantica-app-gerada/` |
| Banco do app | `quantica_ops` (banco **separado** do `langnet` — sem risco ao LangNet); 20 tabelas já existentes |
| `.env` do ws-server | `LLM_PROVIDER=lmstudio`, modelo `qwen2.5-coder-32b-instruct`, `DB_NAME=quantica_ops` |
| Dependências | crewai, websockets, mysql-connector, litellm, pyyaml, dotenv — todas presentes |

## Testes executados e resultados

| # | Teste | Resultado | Evidência |
|---|-------|-----------|-----------|
| T-F0.1 | Subir `ws-server` (main.py) na porta 5002 | ✅ **PASSOU** | Porta 5002 ativa; handshake `connected` lista 18 tasks |
| T-F0.2 | Task **determinística** `cadastrar_persona_alvo` → INSERT real | ✅ **PASSOU** | `task_completed {status:sucesso, persona_id:UUID}`; no banco: persona + 2 canais + 2 problemas + gatilhos/objeções/palavras corretos |
| T-F0.3 | Task **CrewAI** `verificar_fatos_revisor` → `crew.kickoff()` no LLM local | ✅ **PASSOU** | ~30s; `task_completed` com `{"status":"falha"}` (o verificador julgou "300% em 2 dias" como não-comprovável — avaliação correta). Zero exceptions no log. |
| T-F0.4 | `npm install` + `npm run build` do frontend | ✅ **PASSOU** | 1302 pacotes; "The build folder is ready to be deployed"; bundle 228 KB; só warnings `no-unused-vars` |

**Conclusão dos testes:** a cadeia **tela → `runTask` → WebSocket :5002 → ws-server → (SQL determinístico
OU CrewAI+LLM) → resultado** está **funcional**. O banco recebe escritas reais; o LLM local executa
tarefas cognitivas; o frontend compila para produção.

## Achados / problemas (com severidade)

| Sev. | Achado | Detalhe | Onde corrigir |
|------|--------|---------|---------------|
| 🟠 Média | **`.env.example` vaza a senha real do banco** | Vem com `DB_PASSWORD=112358123` (produção) e default `LLM_PROVIDER=deepseek` (nuvem, que o usuário rejeita) | Gerador: usar placeholders (`DB_PASSWORD=`) e default local/seguro |
| 🟠 Média | **Nome do modelo LM Studio errado no template** | `.env.example` traz `LMSTUDIO_MODEL_NAME=openai/deepseek-r1-distill-qwen-32b`, não o modelo carregado | Gerador: parametrizar pelo modelo real do projeto |
| 🟡 Baixa | **Adapter determinístico não trata input string** | Se `canais` chega como `"a, b"` (string), o INSERT itera **caractere a caractere**. No fluxo real a tela usa `splitList` (envia lista) e funciona; falta defesa | `ws-server/adapters.py` (gerador): normalizar string→lista no `_deterministic` |
| 🟡 Baixa | **Algumas telas não disparam task** | Ex.: `GerenciarPermissoesUsuarios.jsx` importa `runTask`/`onPrimary` mas não os usa (form estático) | Gerador `_generate_business_screens`: garantir binding ação→task em todos os tipos |
| 🟡 Baixa | **Saída de task cognitiva é enxuta** | `verificar_fatos_revisor` devolveu só `{"status":"falha"}`; poderia trazer justificativa/campos | Prompt da task / `output_func` no gerador |
| 🟢 Info | **Schema real não está em `data_model_sessions.schema_sql`** | A coluna trazia stub "teste"; as tabelas vêm de `entities_json`. O `quantica_ops` já tinha o schema completo de uma execução anterior | Verificar por que `schema_sql` ficou stub nessa sessão |

## Correções recomendadas no GERADOR (não no artefato)

1. **Segurança do `.env`** (🟠): emitir placeholders para segredos e default de LLM local; nunca embutir
   a senha real do banco. *Teste:* grep no `.env.example` gerado não encontra senha real.
2. **Parametrizar o modelo LM Studio** (🟠) pelo modelo configurado no projeto. *Teste:* `.env.example`
   traz o modelo correto.
3. **Robustez do adapter determinístico** (🟡): normalizar campos de lista (`splitList` no servidor).
   *Teste:* `cadastrar_persona_alvo` com `canais` string cria 1 canal "a, b" (ou 2), nunca N caracteres.
4. **Binding ação→task em todas as telas** (🟡). *Teste:* nenhuma tela gerada tem `runTask` importado e
   não usado.

## Conclusão

O **F0 confirma a hipótese central da auditoria**: o pipeline do LangNet gera um app **que executa** —
telas React reais, persistência SQL real e agentes CrewAI reais rodando no LLM local. Os problemas
encontrados são **de polimento do gerador** (segurança do `.env`, defesa de input, binding de telas),
não falhas estruturais. O caminho está aberto para as próximas fases (F1 — Configurações reais, etc.).

**Como reproduzir:** `cd ~/quantica-app-gerada/ws-server && python3 main.py` (porta 5002) e disparar
`execute_task` via WebSocket; frontend em `~/quantica-app-gerada/frontend` com `npm start` (porta 3001).
