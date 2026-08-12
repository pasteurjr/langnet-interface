#!/usr/bin/env python3
"""Regenera a CAUDA auto-gerada do adapters.py do ws-server do app-teste: helpers
(_LIST_HELPER: _as_list/_hoje/_cv) + adapters determinísticos por-task + CRUD por entidade.
Preserva a 'cabeça' (parte do LLM + TASK_TOOLS). Config via env (ver config.env)."""
import sys, os, re, ast

BACKEND = os.environ["LANGNET_BACKEND"]
APP = os.environ["APP_DIR"]
sys.path.insert(0, BACKEND)
import agents.langnetagents as L

WS = os.path.join(APP, "ws-server")
APP_ADAPTERS = os.path.join(WS, "adapters.py")
tasks_yaml = open(os.path.join(WS, "tasks.yaml")).read()
schema_sql = open(os.path.join(APP, "db/schema.sql")).read()

orig = open(APP_ADAPTERS).read()
MARK = "# ─── helper de normalização de campos de lista (auto-gerado pelo LangNet) ───"
idx = orig.find(MARK)
if idx < 0:
    raise SystemExit("[regen_adapters_tail] marcador _LIST_HELPER não encontrado — abortando (adapters.py inesperado)")

head = orig[:idx].rstrip() + "\n"
existing_fns = set(re.findall(r"def\s+(\w+)\s*\(", head))
model = L._schema_model(schema_sql)
entities = list(model.keys())
det = L._generate_deterministic_adapters(tasks_yaml)
det_names = set(re.findall(r"def\s+(\w+)\s*\(", det))
crud = L._generate_crud_adapters(entities, schema_sql, existing_fns | det_names)

new = head + L._LIST_HELPER + det + ("\n" + crud if crud else "") + "\n"
ast.parse(new)  # valida sintaxe antes de escrever
# backup único
bak = APP_ADAPTERS + ".bak"
if not os.path.exists(bak):
    open(bak, "w").write(orig)
open(APP_ADAPTERS, "w").write(new)
print(f"[regen_adapters_tail] adapters.py regenerado e válido ({len(entities)} entidades)")
