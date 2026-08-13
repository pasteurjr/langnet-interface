#!/usr/bin/env bash
# Entry-point do harness de regeneração (Fase 0). Uso:
#   ./regen.sh all        # limpa pycache + regenera adapters (cauda) + telas
#   ./regen.sh screens    # só as telas
#   ./regen.sh adapters   # só a cauda do adapters.py
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/config.env"
# credenciais do banco do LangNet (para os scripts que leem ui_spec/data_model/tasks)
if [ -f "$LANGNET_BACKEND/.env" ]; then set -a; . "$LANGNET_BACKEND/.env"; set +a; fi
export LANGNET_BACKEND APP_DIR PROJECT_ID WS_PORT

clean_pycache() { find "$LANGNET_BACKEND" -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true; }

cmd="${1:-all}"
case "$cmd" in
  screens)  clean_pycache; "$PY" "$HERE/regen_screens.py" ;;
  adapters) clean_pycache; "$PY" "$HERE/regen_adapters_tail.py" ;;
  wsserver) clean_pycache; "$PY" "$HERE/regen_wsserver.py" ;;
  okf)      clean_pycache; "$PY" "$HERE/regen_okf.py" ;;
  all)      clean_pycache; "$PY" "$HERE/regen_adapters_tail.py"; "$PY" "$HERE/regen_wsserver.py"; "$PY" "$HERE/regen_okf.py"; "$PY" "$HERE/regen_screens.py" ;;
  *) echo "uso: $0 [all|screens|adapters|wsserver|okf]"; exit 2 ;;
esac
echo "[regen] OK ($cmd)"
