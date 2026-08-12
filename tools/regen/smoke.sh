#!/usr/bin/env bash
# Smoke-test completo (Fase 0): garante serviços no ar -> roda E2E pela UI -> verifica a cadeia no banco.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/config.env"
export FRONTEND_PORT APP_DIR NODE_PLAYWRIGHT APP_DB_HOST APP_DB_PORT APP_DB_USER APP_DB_PASSWORD APP_DB_NAME

"$HERE/services.sh" up
# espera o frontend compilar / portas subirem
for i in $(seq 1 50); do
  ss -ltn 2>/dev/null | grep -q ":$WS_PORT " && ss -ltn 2>/dev/null | grep -q ":$FRONTEND_PORT " && break; sleep 3; done

echo "[smoke] rodando E2E pela UI..."
node "$HERE/smoke_e2e.js"; e2e=$?
echo "[smoke] verificando a cadeia no banco..."
"$PY" "$HERE/verify_chain.py"; ver=$?

if [ "$e2e" -eq 0 ] && [ "$ver" -eq 0 ]; then echo "[smoke] ✅ VERDE"; exit 0
else echo "[smoke] ❌ FALHOU (e2e=$e2e verify=$ver)"; exit 1; fi
