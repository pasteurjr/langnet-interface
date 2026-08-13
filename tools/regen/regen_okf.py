#!/usr/bin/env python3
"""Emite o bundle OKF de conhecimento (ws-server/knowledge/) do app-teste a partir do schema real
(Inserção E / Fase 2). Config via env (ver config.env)."""
import sys, os
BACKEND = os.environ["LANGNET_BACKEND"]; APP = os.environ["APP_DIR"]
sys.path.insert(0, BACKEND)
import agents.langnetagents as L
schema_sql = open(os.path.join(APP, "db/schema.sql")).read()
files = L._emit_okf_bundle(schema_sql)
n = 0
for f in files:
    dst = os.path.join(APP, f["path"])  # path já vem como ws-server/knowledge/...
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w").write(f["content"]); n += 1
print(f"[regen_okf] {n} arquivos OKF escritos em {APP}/ws-server/knowledge/")
