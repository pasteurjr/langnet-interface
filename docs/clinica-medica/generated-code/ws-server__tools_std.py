"""
tools_std.py — biblioteca de ferramentas LOCAIS REAIS do LangNet.

IMPLEMENTAÇÕES REAIS, sem mock: PDF (reportlab), CSV (csv), Embedding (endpoint
OpenAI-compat, ex.: LM Studio) e VectorSearch (cosseno sobre uma tabela configurada).
Quando algo não está configurado, a tool FALHA EXPLÍCITO — nunca devolve resultado falso.
Ferramentas externas (e-mail, redes sociais, calendário, CMS) NÃO ficam aqui: vêm por MCP.
"""
import os
import csv
import math
import logging
from typing import Any, Dict, List, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------- PDF (real, reportlab) ----------
class PdfGeneratorToolSchema(BaseModel):
    data: Dict[str, Any] = Field(..., description="Dados a renderizar no PDF")
    output_path: Optional[str] = Field(default="relatorio.pdf", description="Arquivo de saída")


class PdfGeneratorTool(BaseTool):
    name: str = "PdfGeneratorTool"
    description: str = "Gera um arquivo PDF REAL a partir de dados (título + pares/linhas)."
    args_schema: type[BaseModel] = PdfGeneratorToolSchema

    def _run(self, data: Dict[str, Any], output_path: str = "relatorio.pdf") -> Dict[str, Any]:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(output_path, pagesize=A4)
        w, h = A4
        y = h - 40
        d = data or {}
        title = str(d.get("titulo") or d.get("title") or "Relatório")
        c.setFont("Helvetica-Bold", 16); c.drawString(30, y, title[:90]); y -= 26
        c.setFont("Helvetica", 10)

        def line(txt: str):
            nonlocal y
            if y < 40:
                c.showPage(); c.setFont("Helvetica", 10); y = h - 40
            c.drawString(30, y, str(txt)[:115]); y -= 14

        def walk(obj, prefix=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        line(f"{prefix}{k}:"); walk(v, prefix + "  ")
                    else:
                        line(f"{prefix}{k}: {v}")
            elif isinstance(obj, list):
                for i, it in enumerate(obj):
                    if isinstance(it, (dict, list)):
                        line(f"{prefix}- item {i + 1}:"); walk(it, prefix + "  ")
                    else:
                        line(f"{prefix}- {it}")
            else:
                line(f"{prefix}{obj}")

        walk(d)
        c.save()
        return {"status": "ok", "path": os.path.abspath(output_path)}


# ---------- CSV (real) ----------
class CsvExporterToolSchema(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Linhas (lista de dicts) a exportar")
    output_path: Optional[str] = Field(default="export.csv", description="Arquivo de saída")


class CsvExporterTool(BaseTool):
    name: str = "CsvExporterTool"
    description: str = "Exporta dados para um arquivo CSV REAL."
    args_schema: type[BaseModel] = CsvExporterToolSchema

    def _run(self, data: List[Dict[str, Any]], output_path: str = "export.csv") -> Dict[str, Any]:
        rows = data if isinstance(data, list) else [data]
        cols: List[str] = []
        for r in rows:
            if isinstance(r, dict):
                for k in r:
                    if k not in cols:
                        cols.append(k)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            wtr = csv.DictWriter(f, fieldnames=cols or ["valor"])
            wtr.writeheader()
            for r in rows:
                wtr.writerow(r if isinstance(r, dict) else {"valor": r})
        return {"status": "ok", "path": os.path.abspath(output_path), "rows": len(rows)}


# ---------- Embedding (real, endpoint OpenAI-compat / LM Studio) ----------
def _embed(text: str) -> List[float]:
    import requests
    base = (os.getenv("EMBEDDINGS_API_BASE") or os.getenv("LMSTUDIO_API_BASE")
            or os.getenv("OPENAI_API_BASE") or "http://localhost:1234/v1").rstrip("/")
    model = os.getenv("EMBEDDINGS_MODEL", "text-embedding-nomic-embed-text-v1.5")
    key = os.getenv("EMBEDDINGS_API_KEY") or os.getenv("LMSTUDIO_API_KEY") or "not-needed"
    resp = requests.post(base + "/embeddings",
                         headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                         json={"model": model, "input": text}, timeout=60)
    resp.raise_for_status()
    return resp.json()["data"][0]["embedding"]


class EmbeddingToolSchema(BaseModel):
    text: str = Field(..., description="Texto para gerar embedding")


class EmbeddingTool(BaseTool):
    name: str = "EmbeddingTool"
    description: str = "Gera embeddings REAIS de um texto via endpoint de embeddings (ex.: LM Studio)."
    args_schema: type[BaseModel] = EmbeddingToolSchema

    def _run(self, text: str) -> List[float]:
        return _embed(str(text))


# ---------- VectorSearch (real, cosseno sobre tabela configurada) ----------
class VectorSearchToolSchema(BaseModel):
    query: str = Field(..., description="Texto de consulta (ou embedding)")
    top_k: int = Field(default=5, description="Número de resultados")


class VectorSearchTool(BaseTool):
    name: str = "VectorSearchTool"
    description: str = "Busca semântica REAL: embeda a consulta e ranqueia por cosseno os textos de uma tabela."
    args_schema: type[BaseModel] = VectorSearchToolSchema

    def _run(self, query: Any, top_k: int = 5) -> List[Dict[str, Any]]:
        table = os.getenv("VECTOR_TABLE")
        text_col = os.getenv("VECTOR_TEXT_COL", "texto")
        id_col = os.getenv("VECTOR_ID_COL", "id")
        if not table:
            raise RuntimeError(
                "VectorSearchTool: busca vetorial não configurada. Defina VECTOR_TABLE "
                "(+ VECTOR_TEXT_COL/VECTOR_ID_COL) para busca real. Sem mock.")
        qv = query if isinstance(query, list) else _embed(str(query))
        import mysql.connector
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'), port=int(os.getenv('DB_PORT', '3306')),
            user=os.getenv('DB_USER', 'root'), password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', ''))
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(f"SELECT `{id_col}`, `{text_col}` FROM `{table}` LIMIT 500")
            rows = cur.fetchall()
        finally:
            conn.close()

        def cos(a, b):
            s = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
            return s / (na * nb) if na and nb else 0.0

        scored = []
        for r in rows:
            rv = _embed(str(r.get(text_col) or ""))
            scored.append({"id": r.get(id_col), "similarity": round(cos(qv, rv), 4),
                           "texto": r.get(text_col)})
        scored.sort(key=lambda x: -x["similarity"])
        return scored[:top_k]


# ---------- Email (real, smtplib — falha explícito se SMTP não configurado) ----------
class EmailSenderToolSchema(BaseModel):
    to: str = Field(..., description="Destinatário")
    subject: str = Field(..., description="Assunto")
    body: str = Field(..., description="Corpo do e-mail")
    attachment_path: Optional[str] = Field(default=None, description="Caminho de anexo (opcional)")


class EmailSenderTool(BaseTool):
    name: str = "EmailSenderTool"
    description: str = "Envia e-mail REAL via SMTP. Requer SMTP configurado; sem config, falha explícito."
    args_schema: type[BaseModel] = EmailSenderToolSchema

    def _run(self, to: str, subject: str, body: str, attachment_path: Optional[str] = None) -> Dict[str, Any]:
        import smtplib
        from email.message import EmailMessage
        # Modo de SIMULAÇÃO opt-in (mesmo flag das externas) — resposta rotulada.
        if (os.getenv("SIMULATE_EXTERNAL", "") or "").strip().lower() in ("1", "true", "yes", "sim", "on"):
            return {"status": "simulado", "tool": "email_sender_tool",
                    "message": f"[SIMULAÇÃO] enviaria e-mail para {to} — nenhum envio real "
                               "(SIMULATE_EXTERNAL ligado). Configure SMTP no .env para valer.",
                    "to": to, "subject": subject}
        host = os.getenv("SMTP_HOST")
        if not host:
            raise RuntimeError(
                "EmailSenderTool: SMTP não configurado. Defina SMTP_HOST/SMTP_PORT/SMTP_USER/"
                "SMTP_PASSWORD (e SMTP_FROM) para envio real. Sem mock.")
        port = int(os.getenv("SMTP_PORT", "587"))
        user = os.getenv("SMTP_USER"); pwd = os.getenv("SMTP_PASSWORD")
        sender = os.getenv("SMTP_FROM", user or "no-reply@localhost")
        msg = EmailMessage()
        msg["From"] = sender; msg["To"] = to; msg["Subject"] = subject
        msg.set_content(body or "")
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as fh:
                msg.add_attachment(fh.read(), maintype="application", subtype="octet-stream",
                                   filename=os.path.basename(attachment_path))
        with smtplib.SMTP(host, port, timeout=30) as s:
            s.starttls()
            if user and pwd:
                s.login(user, pwd)
            s.send_message(msg)
        return {"status": "ok", "to": to}


# ---------- Fail-loud para integração externa NÃO configurada ----------
class _UnconfiguredToolSchema(BaseModel):
    class Config:
        extra = "allow"


def make_unconfigured_tool(tool_name: str) -> BaseTool:
    """Tool placeholder para integração externa NÃO configurada (ex.: instagram_graph_api_tool).
    Em vez de sumir em silêncio — o que faria o agente ACHAR que a ação foi feita — ela FALHA
    EXPLÍCITO ao ser chamada, instruindo a configurar via MCP ou credencial. Nunca finge sucesso."""
    class _Unconfigured(BaseTool):
        name: str = tool_name
        description: str = (f"Integração '{tool_name}' NÃO configurada. Atribua um servidor MCP "
                            "ou configure a credencial para habilitar esta ação externa.")
        args_schema: type[BaseModel] = _UnconfiguredToolSchema

        def _run(self, **kwargs) -> str:
            raise RuntimeError(
                f"Ferramenta '{tool_name}' não está configurada — NENHUMA ação externa foi "
                "executada. Configure via MCP (servidor + credencial) ou implemente a integração.")
    return _Unconfigured()


# Registro das tools locais reais (o ws-server mescla isto no TOOL_REGISTRY, sobrepondo
# qualquer versão mock que o LLM tenha gerado no tools.py).
STD_TOOLS = {
    "pdf_generator_tool": PdfGeneratorTool(),
    "csv_exporter_tool": CsvExporterTool(),
    "embedding_tool": EmbeddingTool(),
    "vector_search_tool": VectorSearchTool(),
    "email_sender_tool": EmailSenderTool(),
}
