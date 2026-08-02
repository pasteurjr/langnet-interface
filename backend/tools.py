import json
import os
import csv
import io
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from crewai.tools import BaseTool


# ---------------------------------------------------------------------------
# DatabaseTool — executa queries SQL contra um banco PostgreSQL.
# Usado em todas as tasks que fazem INSERT / UPDATE / SELECT.
# Lê as credenciais de variáveis de ambiente (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD).
# ---------------------------------------------------------------------------
class DatabaseInput(BaseModel):
    """Schema de entrada para DatabaseTool."""
    query: str = Field(..., description="SQL query a ser executada. Placeholders no estilo %s.")
    params: List[Any] = Field(default_factory=list, description="Lista de parâmetros para substituir os placeholders %s na query.")


class DatabaseTool(BaseTool):
    name: str = "database_tool"
    description: str = (
        "Executa queries SQL contra o banco de dados PostgreSQL. "
        "Use para INSERT, UPDATE, SELECT, DELETE. Retorna registros como lista de dicts "
        "para SELECT ou um dict com 'affected_rows' para comandos DML."
    )
    args_schema: type[BaseModel] = DatabaseInput

    def _run(self, query: str, params: Optional[List[Any]] = None) -> Any:
        """Executa a query e retorna os resultados."""
        if params is None:
            params = []
        # Simulação — em produção substituir por psycopg2 / asyncpg
        # Aqui apenas registra e retorna um placeholder
        self._log(f"DB query: {query} | params={params}")
        # Simula retorno de SELECT com um registro vazio
        if query.strip().upper().startswith("SELECT"):
            return [{"id": str(uuid.uuid4()), "count": 0}]
        return {"affected_rows": 1, "status": "ok"}

    def _log(self, msg: str) -> None:
        import logging
        logging.getLogger("DatabaseTool").info(msg)


# ---------------------------------------------------------------------------
# EmbeddingTool — gera embeddings de texto para classificação de comentários.
# ---------------------------------------------------------------------------
class EmbeddingInput(BaseModel):
    text: str = Field(..., description="Texto do comentário para gerar embedding.")
    model: str = Field(default="text-embedding-ada-002", description="Modelo de embedding (ex: text-embedding-ada-002).")


class EmbeddingTool(BaseTool):
    name: str = "embedding_tool"
    description: str = (
        "Gera um vetor de embedding para um texto informado. "
        "Utilizado para classificar comentários por similaridade semântica."
    )
    args_schema: type[BaseModel] = EmbeddingInput

    def _run(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """Retorna um vetor de floats representando o embedding do texto."""
        self._log(f"Embedding text ({len(text)} chars) with model={model}")
        # Simulação — em produção integrar OpenAI / sentence-transformers
        import hashlib
        import struct
        # Gera 128 dimensões pseudo-aleatórias baseadas no hash do texto
        h = hashlib.sha256(text.encode()).digest()
        vec = []
        for i in range(128):
            val = struct.unpack('<f', h[(i * 4) % 32:(i * 4 + 4) % 32] if (i * 4) % 32 < 28 else b'\x00\x00\x00\x00')[0]
            vec.append(float(val % 1.0))
        return vec

    def _log(self, msg: str) -> None:
        import logging
        logging.getLogger("EmbeddingTool").info(msg)


# ---------------------------------------------------------------------------
# VectorSearchTool — busca similaridade entre embedding de comentário e categorias.
# ---------------------------------------------------------------------------
class VectorSearchInput(BaseModel):
    embedding: List[float] = Field(..., description="Vetor de embedding do comentário.")
    categories: List[str] = Field(..., description="Lista de categorias possíveis (ex: pergunta técnica, elogio, críica, spam, oportunidade comercial).")


class VectorSearchTool(BaseTool):
    name: str = "vector_search_tool"
    description: str = (
        "Classifica um embedding de comentário em uma das categorias fornecidas "
        "por similaridade de cosseno. Retorna a categoria mais similar."
    )
    args_schema: type[BaseModel] = VectorSearchInput

    def _run(self, embedding: List[float], categories: List[str]) -> str:
        """Retorna a categoria com maior similaridade ao embedding."""
        self._log(f"Classifying embedding (dim={len(embedding)}) into {categories}")
        # Simulação — retorna sempre a primeira categoria
        return categories[0] if categories else "desconhecido"

    def _log(self, msg: str) -> None:
        import logging
        logging.getLogger("VectorSearchTool").info(msg)


# ---------------------------------------------------------------------------
# PdfGeneratorTool — gera um arquivo PDF a partir de dados.
# ---------------------------------------------------------------------------
class PdfGeneratorInput(BaseModel):
    data: Dict[str, Any] = Field(..., description="Dados a serem incluídos no PDF.")
    output_path: str = Field(default="/tmp/export.pdf", description="Caminho para salvar o PDF.")


class PdfGeneratorTool(BaseTool):
    name: str = "pdf_generator_tool"
    description: str = (
        "Gera um arquivo PDF a partir de dados fornecidos. "
        "Usado para exportar relatórios e calendários editoriais em formato PDF."
    )
    args_schema: type[BaseModel] = PdfGeneratorInput

    def _run(self, data: Dict[str, Any], output_path: str = "/tmp/export.pdf") -> str:
        """Gera PDF e retorna o caminho do arquivo gerado."""
        self._log(f"Generating PDF at {output_path} with data keys={list(data.keys())}")
        # Em produção usar reportlab / fpdf2
        with open(output_path, 'w') as f:
            f.write(f"PDF Content: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return output_path

    def _log(self, msg: str) -> None:
        import logging
        logging.getLogger("PdfGeneratorTool").info(msg)


# ---------------------------------------------------------------------------
# CsvExporterTool — gera um arquivo CSV a partir de dados.
# ---------------------------------------------------------------------------
class CsvExporterInput(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Lista de registros a exportar.")
    output_path: str = Field(default="/tmp/export.csv", description="Caminho para salvar o CSV.")
    fieldnames: Optional[List[str]] = Field(default=None, description="Nomes das colunas. Se None, usa as chaves do primeiro registro.")


class CsvExporterTool(BaseTool):
    name: str = "csv_exporter_tool"
    description: str = (
        "Gera um arquivo CSV a partir de uma lista de dicionários. "
        "Usado para exportar relatórios e calendários editoriais em formato CSV."
    )
    args_schema: type[BaseModel] = CsvExporterInput

    def _run(self, data: List[Dict[str, Any]], output_path: str = "/tmp/export.csv", fieldnames: Optional[List[str]] = None) -> str:
        """Gera CSV e retorna o caminho do arquivo."""
        self._log(f"Generating CSV at {output_path} with {len(data)} rows")
        if not data:
            with open(output_path, 'w') as f:
                f.write("")
            return output_path
        fn = fieldnames or list(data[0].keys())
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fn)
            writer.writeheader()
            writer.writerows(data)
        return output_path

    def _log(self, msg: str) -> None:
        import logging
        logging.getLogger("CsvExporterTool").info(msg)


# ---------------------------------------------------------------------------
# EmailSenderTool — envia email com ou sem anexo.
# ---------------------------------------------------------------------------
class EmailSenderInput(BaseModel):
    to: str = Field(..., description="Endereço de email do destinatário.")
    subject: str = Field(..., description="Assunto do email.")
    body: str = Field(..., description="Corpo da mensagem.")
    attachments: Optional[List[str]] = Field(default=None, description="Lista de caminhos de arquivos para anexar.")


class EmailSenderTool(BaseTool):
    name: str = "email_sender_tool"
    description: str = (
        "Envia um email com assunto, corpo e anexos opcionais. "
        "Usado para enviar relatórios semanais para o CEO."
    )
    args_schema: type[BaseModel] = EmailSenderInput

    def _run(self, to: str, subject: str, body: str, attachments: Optional[List[str]] = None) -> str:
        """Envia o email e retorna status."""
        self._log(f"Sending email to {to}: subject='{subject}', attachments={attachments}")
        # Em produção usar smtplib / sendgrid / ses
        return f"Email enviado para {to} com sucesso."

    def _log(self, msg: str) -> None:
        import logging
        logging.getLogger("EmailSenderTool").info(msg)


# ---------------------------------------------------------------------------
# GoogleCalendarTool — sincroniza eventos com Google Calendar.
# ---------------------------------------------------------------------------
class GoogleCalendarInput(BaseModel):
    summary: str = Field(..., description="Título do evento.")
    start_datetime: str = Field(..., description="Data/hora de início no formato ISO 8601.")
    end_datetime: str = Field(..., description="Data/hora de fim no formato ISO 8601.")
    attendees: Optional[List[str]] = Field(default=None, description="Lista de emails dos participantes.")
    description: Optional[str] = Field(default=None, description="Descrição do evento.")


class GoogleCalendarTool(BaseTool):
    name: str = "google_calendar_tool"
    description: str = (
        "Cria um evento no Google Calendar. "
        "Usado para sincronizar reuniões agendadas com leads na agenda do CEO."
    )
    args_schema: type[BaseModel] = GoogleCalendarInput

    def _run(self, summary: str, start_datetime: str, end_datetime: str,
             attendees: Optional[List[str]] = None,
             description: Optional[str] = None) -> str:
        """Cria o evento e retorna o link."""
        self._log(f"Creating calendar event: '{summary}' at {start_datetime}")
        # Em produção usar google-api-python-client
        return f"Evento '{summary}' criado no Google Calendar."

    def _log(self, msg: str) -> None:
        import logging
        logging.getLogger("GoogleCalendarTool").info(msg)


# ---------------------------------------------------------------------------
# TOOL_REGISTRY — mapeia nomes snake_case para instâncias.
# O websocket_server consulta este dict para vincular tools às tasks.
# ---------------------------------------------------------------------------
TOOL_REGISTRY: Dict[str, BaseTool] = {
    "database_tool": DatabaseTool(),
    "embedding_tool": EmbeddingTool(),
    "vector_search_tool": VectorSearchTool(),
    "pdf_generator_tool": PdfGeneratorTool(),
    "csv_exporter_tool": CsvExporterTool(),
    "email_sender_tool": EmailSenderTool(),
    "google_calendar_tool": GoogleCalendarTool(),
}
