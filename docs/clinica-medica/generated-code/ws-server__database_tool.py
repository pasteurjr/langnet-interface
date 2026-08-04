"""Database Tool — CrewAI BaseTool que executa queries reais em MySQL.

Configuração via ambiente:
- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

O tool é seguro por padrão: SELECT retorna linhas como JSON, mutations retornam
row count + last_insert_id. Aceita params posicionais via placeholder %s.

Uso pelos agentes CrewAI:
    result = database_tool.run(query="SELECT * FROM leads WHERE score > 70")
    result = database_tool.run(
        query="INSERT INTO leads (nome, empresa, score) VALUES (%s, %s, %s)",
        params=["Fulano", "Beltrano SA", 85]
    )
"""
from __future__ import annotations

import json
import os
import logging
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

import mysql.connector

log = logging.getLogger(__name__)


class DatabaseToolSchema(BaseModel):
    query: str = Field(..., description="Query SQL. Use %s como placeholder pra parâmetros.")
    params: Optional[List[Any]] = Field(
        default=None,
        description="Lista de parâmetros posicionais pra bindings %s da query."
    )


class DatabaseTool(BaseTool):
    name: str = "database_tool"
    description: str = (
        "Executa queries SQL no banco de dados da aplicação (MySQL). "
        "Para SELECT retorna as linhas em JSON. Para INSERT/UPDATE/DELETE retorna "
        "affected_rows e last_insert_id. Sempre use placeholders %s pra parâmetros "
        "(evita SQL injection e formata datas/strings corretamente)."
    )
    args_schema: type[BaseModel] = DatabaseToolSchema

    def _connect(self):
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", ""),
            connection_timeout=10,
            autocommit=False,
        )

    def _run(self, query: str, params: Optional[List[Any]] = None) -> str:
        q = (query or "").strip()
        if not q:
            return json.dumps({"error": "query vazia"}, ensure_ascii=False)

        is_select = q.lstrip("(").lower().startswith(("select", "show", "describe", "explain"))
        conn = None
        try:
            conn = self._connect()
            cur = conn.cursor(dictionary=True)
            cur.execute(q, tuple(params) if params else None)

            if is_select:
                rows = cur.fetchall()
                # Serializa datas/UUIDs pra string
                out = json.dumps(
                    {"rows": rows, "row_count": len(rows)},
                    ensure_ascii=False, default=str,
                )
            else:
                conn.commit()
                out = json.dumps(
                    {
                        "affected_rows": cur.rowcount,
                        "last_insert_id": cur.lastrowid,
                    },
                    ensure_ascii=False,
                )
            cur.close()
            return out

        except mysql.connector.Error as e:
            if conn:
                try: conn.rollback()
                except Exception: pass
            log.exception("DatabaseTool error")
            return json.dumps(
                {"error": str(e), "errno": e.errno if hasattr(e, "errno") else None},
                ensure_ascii=False,
            )
        except Exception as e:
            log.exception("DatabaseTool unexpected error")
            return json.dumps({"error": str(e)}, ensure_ascii=False)
        finally:
            if conn:
                try: conn.close()
                except Exception: pass


# Instância pronta pra ser importada pelo TOOL_REGISTRY
database_tool = DatabaseTool()
