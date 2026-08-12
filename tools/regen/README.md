# Harness de regeneração + smoke-test (Fase 0 do plano v3)

Ferramental **versionado** (não mais no scratchpad volátil) para o ciclo
`editar gerador → regenerar → validar` do app-teste (padrão: ClinIA).

## Config
Edite `config.env` (paths, PROJECT_ID, portas, endpoint do LLM, banco do app).

## Uso
```bash
cd tools/regen
./regen.sh all        # limpa __pycache__ + regenera adapters (cauda) + telas do app-teste
./regen.sh screens    # só telas   |   ./regen.sh adapters  # só a cauda do adapters.py
./services.sh up      # sobe ws-server + frontend (aponta LLM alcançável)  |  down | status
./smoke.sh            # sobe serviços -> E2E pela UI -> verifica a cadeia no banco (sai 0 = verde)
```

## Arquivos
- `config.env` — configuração.
- `regen_screens.py` — regenera `frontend/src/screens/` (determinístico, sem LLM).
- `regen_adapters_tail.py` — regenera a cauda auto-gerada do `ws-server/adapters.py`.
- `regen.sh` — orquestra a regeneração (limpa pycache antes).
- `services.sh` — sobe/derruba ws-server e frontend de forma idempotente.
- `smoke_e2e.js` — E2E headless (Playwright): triagem→…→consulta; grava `e2e-carry.json`.
- `verify_chain.py` — confere no banco que a cadeia persistiu ligada (FKs corretas).
- `smoke.sh` — smoke completo (serviços + E2E + verificação).

## Notas
- Faz backup único de `screens/` (`.bak`) e `adapters.py` (`.bak`) na 1ª regeneração.
- O smoke sai 0 quando as etapas determinísticas críticas persistem a cadeia; as etapas
  agênticas podem variar por lentidão/flakiness do LLM local (retry embutido).
