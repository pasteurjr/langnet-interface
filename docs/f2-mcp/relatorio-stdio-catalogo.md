# MCP — Relatório: Suporte a stdio + Catálogo de Servidores Recomendados

**Data:** 24/07/2026 · **Commit:** `e97ba08`

---

## 1. Objetivo
Permitir **pré-cadastrar** servidores MCP úteis "na prateleira" (1 clique) e destravar o
transporte **stdio** (a maioria dos servidores MCP reais roda como comando local), que ficara
para depois na Fase 1.

## 2. O que foi implementado

### Backend
- **`_discover_tools` agora suporta `stdio`** — via `StdioServerParameters` + `stdio_client` do SDK
  `mcp`; o comando é parseado com `shlex` (ex.: `uvx mcp-server-fetch` → command `uvx`, args
  `['mcp-server-fetch']`); credenciais viram variáveis de ambiente do processo.
- **`GET /api/mcp/catalog`** — catálogo curado de 8 servidores recomendados, com nome, categoria,
  transporte, comando/URL, descrição e `needs_key`.

### Catálogo curado (relevante para a Quântica)
| Servidor | Categoria | Comando | Chave? |
|----------|-----------|---------|--------|
| Fetch (web) | Prospecção/Busca | `uvx mcp-server-fetch` | não |
| Brave Search | Prospecção/Busca | `npx -y @modelcontextprotocol/server-brave-search` | 🔑 BRAVE_API_KEY |
| Sequential Thinking | Raciocínio | `npx -y @modelcontextprotocol/server-sequential-thinking` | não |
| Memory (grafo) | Memória | `npx -y @modelcontextprotocol/server-memory` | não |
| Time | Utilidades | `uvx mcp-server-time` | não |
| Git | Dados/Dev | `uvx mcp-server-git` | não |
| GitHub | Dados/Dev | `npx -y @modelcontextprotocol/server-github` | 🔑 GITHUB_PERSONAL_ACCESS_TOKEN |
| Everything (teste) | Utilidades | `npx -y @modelcontextprotocol/server-everything` | não |

### Frontend
- Seção **⭐ Servidores recomendados** na tela MCP → Configuração Global, com **cadastro em 1 clique**.
- O form de registro manual ganhou a opção **stdio** + campo **Comando**.

## 3. Testes de validação (todos executados)

### T1 — Ambiente para servidores stdio
```
node v22.16.0 · npx 10.9.2 · uvx 0.7.20 · uv 0.7.20  (docker não instalado)
```
✅ Dá para rodar servidores stdio em Node (npx) e Python (uvx).

### T2 — Descoberta stdio direta (servidor REAL Fetch)
```
uvx mcp-server-fetch (1ª vez baixa o pacote)
STDIO OK — tools do fetch: [('fetch', 'Fetches a URL from the internet and optionally ext')]
```
✅ O cliente stdio conecta e descobre a ferramenta.

### T3 — Catálogo via API (`GET /api/mcp/catalog`)
Retornou os 8 servidores recomendados com transporte/comando/needs_key. ✅

### T4 — Registrar + testar via API (Fetch, stdio, do catálogo)
```
registrar (stdio, "uvx mcp-server-fetch") -> id=80dfc8c3-...
testar/ativar -> status: ativo | tools: ['fetch'] | Ativo — 1 ferramenta(s) descoberta(s).
```
✅ Servidor real **ativo** com a tool descoberta via stdio.

### T5 — Validação visual (UI real)
A tela mostra os 8 cards do catálogo com **+ cadastrar** (1 clique), 🔑 nos que precisam de chave,
o form manual com opção **stdio**, e o **Fetch (web)** já **ativo** (stdio, tool `fetch`).

## 4. Ressalvas honestas
- Servidores `stdio` rodam **como processo na máquina do backend** — ela precisa de `node`/`npx`
  (servidores TS) e `uvx`/`uv` (servidores Python), e alguns exigem **chave de API** (Brave, GitHub).
- O catálogo é uma **conveniência**: cada servidor só fica "ativo" após o **Testar** (handshake real).
  Alguns nomes de pacote do ecossistema podem mudar — o teste valida na hora.

## 5. Conclusão
O LangNet agora nasce com um **catálogo de integrações MCP na prateleira** (1 clique) e suporta os
transportes **sse, http e stdio** — cobrindo a grande maioria dos servidores MCP reais. Validado
ponta a ponta com o servidor **Fetch** de verdade.
