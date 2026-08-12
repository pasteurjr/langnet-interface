#!/usr/bin/env python3
"""Regenera as telas de negócio (Cara A) do app-teste a partir do gerador do LangNet.
Determinístico (sem LLM): lê ui_spec + Modelo de Dados + tasks.yaml do banco do LangNet
e reescreve frontend/src/screens/. Config via variáveis de ambiente (ver config.env)."""
import sys, os, json, shutil

BACKEND = os.environ["LANGNET_BACKEND"]
APP = os.environ["APP_DIR"]
PID = os.environ["PROJECT_ID"]
WS_PORT = int(os.environ.get("WS_PORT", "5003"))
sys.path.insert(0, BACKEND)

from app.database import get_db_connection
import agents.langnetagents as L

with get_db_connection() as c:
    cur = c.cursor(dictionary=True)
    cur.execute("SELECT name FROM projects WHERE id=%s", (PID,))
    project_name = (cur.fetchone() or {}).get("name") or "App"
    cur.execute("SELECT ui_spec_json FROM ui_spec_sessions WHERE project_id=%s AND ui_spec_json IS NOT NULL ORDER BY created_at DESC LIMIT 1", (PID,))
    ui_spec = json.loads(cur.fetchone()["ui_spec_json"])
    cur.execute("SELECT schema_sql, entities_json, target_dbms FROM data_model_sessions WHERE project_id=%s AND status IN ('completed','approved','draft') ORDER BY created_at DESC LIMIT 1", (PID,))
    dm = cur.fetchone()
    cur.execute("SELECT tasks_yaml_content FROM tasks_yaml_sessions WHERE project_id=%s AND tasks_yaml_content IS NOT NULL ORDER BY created_at DESC LIMIT 1", (PID,))
    trow = cur.fetchone(); cur.close()

schema_sql = (dm.get("schema_sql") if dm else "") or ""
if len(schema_sql) < 50 and dm and dm.get("entities_json"):
    from agents.langnetdatamodel import generate_ddl
    schema_sql = generate_ddl(json.loads(dm["entities_json"]), dbms=(dm.get("target_dbms") or "mysql"))

tasks_yaml = ((trow or {}).get("tasks_yaml_content") or "").strip()
if tasks_yaml.startswith("```"):
    tasks_yaml = "\n".join(l for l in tasks_yaml.splitlines() if not l.strip().startswith("```"))

files = L._generate_business_screens(ui_spec, WS_PORT, project_name, tasks_yaml, schema_sql=schema_sql, task_modules={})
scr = os.path.join(APP, "frontend/src/screens")
bak = scr + ".bak"
if not os.path.exists(bak) and os.path.isdir(scr):
    shutil.copytree(scr, bak)
for f in files:
    dst = os.path.join(APP, f["path"])
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w").write(f["content"])
print(f"[regen_screens] {len(files)} arquivos escritos (project={project_name!r}, schema={len(schema_sql)} chars)")
