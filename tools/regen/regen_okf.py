#!/usr/bin/env python3
"""Emite o bundle OKF (ws-server/knowledge/) do app-teste com PROVENIÊNCIA OKF v0.2
(Inserção E/F). Config via env (ver config.env)."""
import sys, os
from datetime import datetime
BACKEND = os.environ["LANGNET_BACKEND"]; APP = os.environ["APP_DIR"]; PID = os.environ["PROJECT_ID"]
sys.path.insert(0, BACKEND)
import agents.langnetagents as L

schema_sql = open(os.path.join(APP, "db/schema.sql")).read()
tasks_yaml = open(os.path.join(APP, "ws-server/tasks.yaml")).read()

# proveniência: modelo (env) + timestamp + aprovação da sessão de Modelo de Dados (best-effort)
gen_by = "langnet/" + (os.getenv("LMSTUDIO_MODEL_NAME") or os.getenv("APP_LLM_MODEL") or "qwen2.5-coder-32b-instruct")
gen_at = datetime.now().isoformat(timespec="seconds")
ver_by = None
try:
    from app.database import get_db_connection
    with get_db_connection() as c:
        cur = c.cursor(dictionary=True)
        cur.execute("SELECT status, approved_by FROM data_model_sessions "
                    "WHERE project_id=%s ORDER BY created_at DESC LIMIT 1", (PID,))
        r = cur.fetchone(); cur.close()
    if r:
        if str(r.get("status") or "").lower() in ("approved", "aprovado"):
            ver_by = "human:" + str(r.get("approved_by") or "operador")
    print(f"[regen_okf] proveniência: generated.by={gen_by} | verified.by={ver_by or '(nenhum — unverified)'}")
except Exception as e:
    print(f"[regen_okf] (sem lookup de proveniência: {e})")

files = L._emit_okf_bundle(schema_sql, tasks_yaml=tasks_yaml,
                           generated_by=gen_by, generated_at=gen_at,
                           verified_by=ver_by, source_ref=f"data-model://{PID}")
n = 0
for f in files:
    dst = os.path.join(APP, f["path"])
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w").write(f["content"]); n += 1
print(f"[regen_okf] {n} arquivos OKF escritos (com proveniência) em {APP}/ws-server/knowledge/")
