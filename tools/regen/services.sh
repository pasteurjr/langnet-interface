#!/usr/bin/env bash
# Sobe/derruba os serviços do app-teste de forma idempotente (Fase 0). Uso:
#   ./services.sh up      # aponta LLM externo + sobe ws-server (:WS_PORT) e frontend (:FRONTEND_PORT)
#   ./services.sh down    # derruba ambos
#   ./services.sh status  # estado das portas
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/config.env"

pid_on() { ss -ltnp 2>/dev/null | grep ":$1 " | grep -oP 'pid=\K[0-9]+' | head -1; }
kill_port() { local p; p="$(pid_on "$1")"; [ -n "${p:-}" ] && kill "$p" 2>/dev/null && sleep 2 || true; }

point_llm() {  # garante que o ws-server usa o endpoint alcançável
  local env="$APP_DIR/ws-server/.env"
  [ -f "$env" ] && sed -i "s|^LMSTUDIO_API_BASE=.*|LMSTUDIO_API_BASE=$LLM_API_BASE|" "$env" || true
}

case "${1:-status}" in
  up)
    point_llm
    if [ -z "$(pid_on "$WS_PORT")" ]; then
      ( cd "$APP_DIR/ws-server"; set -a; . .env 2>/dev/null; set +a; setsid "$PY" main.py > "$APP_DIR/ws-server.harness.log" 2>&1 & )
      echo "[services] ws-server subindo (:$WS_PORT)"
    else echo "[services] ws-server já no ar (:$WS_PORT)"; fi
    if [ -z "$(pid_on "$FRONTEND_PORT")" ]; then
      ( cd "$APP_DIR/frontend"; setsid env PORT="$FRONTEND_PORT" BROWSER=none REACT_APP_WS_URL="ws://localhost:$WS_PORT" \
          node node_modules/.bin/react-scripts start > "$APP_DIR/frontend.harness.log" 2>&1 & )
      echo "[services] frontend subindo (:$FRONTEND_PORT) — compila em ~40-90s"
    else echo "[services] frontend já no ar (:$FRONTEND_PORT)"; fi
    ;;
  down) kill_port "$WS_PORT"; kill_port "$FRONTEND_PORT"; echo "[services] derrubados" ;;
  status)
    for p in "$WS_PORT" "$FRONTEND_PORT"; do
      ss -ltn 2>/dev/null | grep -q ":$p " && echo "  :$p UP" || echo "  :$p DOWN"; done ;;
  *) echo "uso: $0 [up|down|status]"; exit 2 ;;
esac
