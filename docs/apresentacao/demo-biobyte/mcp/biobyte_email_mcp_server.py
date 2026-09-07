#!/usr/bin/env python3
"""BioByte Sentinela — Servidor MCP de E-MAIL (canal de notificação).
Expõe a ferramenta `enviar_email(para, assunto, corpo)`, que envia a mensagem por SMTP de verdade
(SMTP_HOST/SMTP_PORT, padrão 127.0.0.1:1025 — a caixa postal local de demonstração; em produção,
o servidor do hospital, com SMTP_USER/SMTP_PASSWORD). Sem servidor SMTP alcançável, FALHA explícito:
nunca diz que enviou. Transporte SSE, porta 9121. Rodar:  python biobyte_email_mcp_server.py"""
import os, smtplib
from email.message import EmailMessage
from typing import TypedDict, Optional
from mcp.server.fastmcp import FastMCP

PORT = int(os.getenv("BIOBYTE_EMAIL_MCP_PORT", "9121"))
SMTP_HOST = os.getenv("SMTP_HOST", "127.0.0.1")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
REMETENTE = os.getenv("SMTP_FROM", "sentinela@hospital.br")
mcp = FastMCP("BioByte Sentinela - Notificações (E-mail)", host="127.0.0.1", port=PORT)


class ResultadoEnvio(TypedDict):
    enviado: bool
    para: str
    assunto: str
    servidor: str
    id_mensagem: Optional[str]


@mcp.tool()
def enviar_email(para: str, assunto: str, corpo: str) -> ResultadoEnvio:
    """Envia um e-mail de notificação (ex.: alerta de microrganismo multirresistente ao médico e ao
    enfermeiro). `para` aceita vários endereços separados por vírgula. Devolve se foi entregue ao
    servidor SMTP e o identificador da mensagem; se o servidor não responder, a chamada falha."""
    msg = EmailMessage()
    msg["From"] = REMETENTE
    msg["To"] = para
    msg["Subject"] = assunto
    msg.set_content(corpo)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=8) as s:
        if os.getenv("SMTP_USER"):
            s.starttls(); s.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD", ""))
        s.send_message(msg)
    return {"enviado": True, "para": para, "assunto": assunto,
            "servidor": f"{SMTP_HOST}:{SMTP_PORT}", "id_mensagem": msg["Message-ID"] or None}


if __name__ == "__main__":
    mcp.run(transport="sse")
