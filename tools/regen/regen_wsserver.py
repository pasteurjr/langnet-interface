#!/usr/bin/env python3
"""Regenera o ws-server do app-teste para refletir mudanças no gerador que afetam runtime:
(1) injeta `output_schema` por task no tasks.yaml (contrato de saída — Inserção A);
(2) regenera websocket_server.py a partir do template (inclui a validação do contrato).
Config via env (ver config.env). Faz backup único (.bak) na 1ª vez."""
import sys, os, ast

BACKEND = os.environ["LANGNET_BACKEND"]
APP = os.environ["APP_DIR"]
WS_PORT = int(os.environ.get("WS_PORT", "5003"))
sys.path.insert(0, BACKEND)
import agents.langnetagents as L

WS = os.path.join(APP, "ws-server")

# (1) tasks.yaml: injeta output_schema
schema_sql = open(os.path.join(APP, "db/schema.sql")).read()
ty = open(os.path.join(WS, "tasks.yaml")).read()
ty2 = L._annotate_tasks_output_schema(ty, schema_sql)
ty2 = L._annotate_tasks_verification(ty2, schema_sql)
if ty2 != ty:
    bak = os.path.join(WS, "tasks.yaml.bak")
    if not os.path.exists(bak):
        open(bak, "w").write(ty)
    open(os.path.join(WS, "tasks.yaml"), "w").write(ty2)
    print("[regen_wsserver] tasks.yaml: output_schema injetado")
else:
    print("[regen_wsserver] tasks.yaml: sem mudança (output_schema já presente ou não derivável)")

# (2) websocket_server.py: regenera do template
new_ws = L._template_websocket_server_py(WS_PORT)
ast.parse(new_ws)  # valida sintaxe
wsp = os.path.join(WS, "websocket_server.py")
bak = wsp + ".bak"
if not os.path.exists(bak) and os.path.exists(wsp):
    open(bak, "w").write(open(wsp).read())
open(wsp, "w").write(new_ws)
has_contract = "_coerce_to_schema" in new_ws and "output_schema" in new_ws
print(f"[regen_wsserver] websocket_server.py regenerado e válido (contrato de saída presente? {has_contract})")
