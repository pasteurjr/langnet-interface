#!/usr/bin/env python3
"""Portão de rastreabilidade (CLI). Uso: python3 tools/langnet_trace_gate.py <project_id>

Puxa os artefatos MAIS RECENTES do projeto (spec -> requisitos de origem via
proveniência; ATS/tasks.yaml/data-model por recência) e roda o guardrail
determinístico langnettraceability.audit. Sai com código != 0 se o portão reprova
(algum FR/NFR/BR sem cobertura), para poder ser usado como gate de CI/pipeline.

Não hardcoda credenciais: usa app.database.get_db_connection (env DB_*).
"""
import sys
import os

_BACKEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
sys.path.insert(0, os.path.abspath(_BACKEND))

from app.database import get_db_connection  # noqa: E402
from agents.langnettraceability import audit, format_report  # noqa: E402


def _fetch(project_id: str):
    art = {"requirements_md": "", "spec_md": "", "ats_md": "",
           "tasks_yaml": "", "schema_sql": "", "entities_json": ""}
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        # 1) spec mais recente (traz a proveniência dos requisitos)
        cur.execute("""SELECT specification_document, requirements_session_id, requirements_version
                       FROM execution_specification_sessions
                       WHERE project_id=%s AND status='completed'
                       ORDER BY created_at DESC LIMIT 1""", (project_id,))
        s = cur.fetchone()
        if s:
            art["spec_md"] = s["specification_document"] or ""
            if s.get("requirements_session_id"):
                cur.execute("""SELECT requirements_document FROM session_requirements_version
                               WHERE session_id=%s AND version=%s LIMIT 1""",
                            (s["requirements_session_id"], s.get("requirements_version") or 1))
                r = cur.fetchone()
                if r:
                    art["requirements_md"] = r["requirements_document"] or ""
        # fallback requisitos: última versão de qualquer sessão do projeto
        if not art["requirements_md"]:
            cur.execute("""SELECT srv.requirements_document
                           FROM session_requirements_version srv
                           JOIN execution_sessions es ON es.id=srv.session_id
                           WHERE es.project_id=%s ORDER BY srv.version DESC LIMIT 1""", (project_id,))
            r = cur.fetchone()
            if r:
                art["requirements_md"] = r["requirements_document"] or ""
        # 2) ATS mais recente
        cur.execute("""SELECT agent_task_spec_document FROM agent_task_specification_sessions
                       WHERE project_id=%s AND status='completed' ORDER BY created_at DESC LIMIT 1""", (project_id,))
        a = cur.fetchone()
        if a:
            art["ats_md"] = a["agent_task_spec_document"] or ""
        # 3) tasks.yaml mais recente
        cur.execute("""SELECT tasks_yaml_content FROM tasks_yaml_sessions
                       WHERE project_id=%s AND status='completed' ORDER BY created_at DESC LIMIT 1""", (project_id,))
        t = cur.fetchone()
        if t:
            art["tasks_yaml"] = t["tasks_yaml_content"] or ""
        # 4) modelo de dados mais recente
        cur.execute("""SELECT schema_sql, entities_json FROM data_model_sessions
                       WHERE project_id=%s ORDER BY updated_at DESC LIMIT 1""", (project_id,))
        d = cur.fetchone()
        if d:
            art["schema_sql"] = d.get("schema_sql") or ""
            art["entities_json"] = d.get("entities_json") or ""
        cur.close()
    return art


def main():
    if len(sys.argv) < 2:
        print("uso: python3 tools/langnet_trace_gate.py <project_id>")
        sys.exit(2)
    art = _fetch(sys.argv[1])
    res = audit(**art)
    print(format_report(res))
    sys.exit(0 if res["gate_pass"] else 1)


if __name__ == "__main__":
    main()
