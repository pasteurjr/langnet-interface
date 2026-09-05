"""Router da etapa PROTÓTIPO (Fase 3 do plano).

Gera, monta e serve o protótipo React da Especificação de Interface aprovada, para que ele seja
usado DENTRO da própria etapa — em vez de imagem estática que só se olha.

O protótipo é o aplicativo com a fonte de dados trocada: as telas são emitidas pelo mesmo
emissor do gerador de código, e só o módulo de acesso a dados difere (semente fictícia aqui,
servidor de agentes no aplicativo).
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel, Field
import json

from app.database import get_db_connection
from app.dependencies import get_current_user

from agents.langnetprototype import (
    gerar_prototipo, montar_prototipo, RAIZ_PROTOTIPOS,
)

router = APIRouter(prefix="/api/prototype", tags=["prototype"])


class GerarRequest(BaseModel):
    ui_spec_session_id: Optional[str] = Field(
        None, description="Sessão da Especificação de Interface; ausente = a mais recente")
    linhas_por_tabela: int = Field(6, ge=1, le=50,
                                   description="Quantas linhas fictícias por tabela na semente")


def _fontes(project_id: str, ui_session_id: Optional[str]):
    """Devolve (ui_spec, schema_sql, tasks_yaml, ui_session_id, versao, nome_projeto)."""
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        if ui_session_id:
            cur.execute("SELECT id, version, ui_spec_json, data_model_session_id "
                        "FROM ui_spec_sessions WHERE id=%s", (ui_session_id,))
        else:
            cur.execute("SELECT id, version, ui_spec_json, data_model_session_id "
                        "FROM ui_spec_sessions WHERE project_id=%s "
                        "ORDER BY version DESC, created_at DESC LIMIT 1", (project_id,))
        ui = cur.fetchone()
        if not ui:
            cur.close()
            raise HTTPException(404, "Nenhuma Especificação de Interface para este projeto")

        # DDL aprovado do Modelo de Dados — origem da semente de dados fictícios.
        schema = ""
        cur.execute("SELECT schema_sql FROM data_model_sessions WHERE project_id=%s "
                    "AND schema_sql IS NOT NULL AND CHAR_LENGTH(schema_sql)>0 "
                    "ORDER BY version DESC, created_at DESC LIMIT 1", (project_id,))
        dm = cur.fetchone()
        if dm:
            schema = dm.get("schema_sql") or ""

        # tasks.yaml — dá o contrato de saída de cada tarefa, para o provedor fictício
        # responder com as MESMAS chaves que o aplicativo responderia.
        tasks = ""
        # tasks_yaml_sessions não tem coluna de versão — a mais recente é pela data.
        cur.execute("SELECT tasks_yaml_content AS tasks_yaml FROM tasks_yaml_sessions "
                    "WHERE project_id=%s ORDER BY created_at DESC LIMIT 1", (project_id,))
        ty = cur.fetchone()
        if ty:
            tasks = ty.get("tasks_yaml") or ""

        cur.execute("SELECT name FROM projects WHERE id=%s", (project_id,))
        pr = cur.fetchone()
        cur.close()

    ui_spec = ui.get("ui_spec_json") or "{}"
    if isinstance(ui_spec, str):
        ui_spec = json.loads(ui_spec)
    return (ui_spec, schema, tasks, ui["id"], int(ui.get("version") or 1),
            (pr or {}).get("name") or "Protótipo")


@router.post("/{project_id}/generate")
def gerar(project_id: str, req: GerarRequest, user=Depends(get_current_user)):
    ui_spec, schema, tasks, sid, versao, nome = _fontes(project_id, req.ui_spec_session_id)
    if not schema:
        raise HTTPException(400, "Modelo de Dados sem DDL aprovado — a semente de dados "
                                 "fictícios sai dele; aprove o Modelo de Dados antes")
    arquivos = gerar_prototipo(ui_spec, schema, tasks, nome)
    destino = RAIZ_PROTOTIPOS / sid / f"v{versao}"
    resultado = montar_prototipo(arquivos, destino, nome)
    if not resultado.get("ok"):
        raise HTTPException(500, resultado.get("erro") or "falha ao montar o protótipo")
    resultado.update({"ui_spec_session_id": sid, "version": versao,
                      "url": f"/prototipo/{sid}/v{versao}/index.html"})
    return resultado


@router.get("/project/{project_id}/latest")
def ultimo(project_id: str, user=Depends(get_current_user)):
    """Protótipo já montado da versão mais recente, se existir."""
    _, _, _, sid, versao, _ = _fontes(project_id, None)
    destino = RAIZ_PROTOTIPOS / sid / f"v{versao}"
    if not (destino / "index.html").exists():
        raise HTTPException(404, "Protótipo ainda não montado para esta versão")
    return {"ui_spec_session_id": sid, "version": versao,
            "url": f"/prototipo/{sid}/v{versao}/index.html",
            "bytes": (destino / "bundle.js").stat().st_size}
