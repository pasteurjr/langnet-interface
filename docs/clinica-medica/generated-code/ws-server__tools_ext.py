"""
tools_ext.py — INTEGRAÇÕES EXTERNAS do app gerado (LinkedIn, Instagram, Google Calendar, CMS).

Implementações REAIS que chamam as APIs oficiais. As credenciais vêm do AMBIENTE (.env,
seção "INTEGRAÇÕES EXTERNAS"). Enquanto não configuradas, cada tool FALHA EXPLÍCITO com uma
mensagem dizendo exatamente qual variável preencher — nunca devolve resultado falso.

Para habilitar no futuro: preencha as variáveis correspondentes no .env e reinicie o ws-server.
"""
import os
from typing import Any, Dict, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


def _require(*names: str):
    """Garante que as variáveis de ambiente existam; senão, falha explícito (fail-loud)."""
    missing = [n for n in names if not os.getenv(n)]
    if missing:
        raise RuntimeError(
            "Integração externa NÃO configurada: preencha " + ", ".join(missing) +
            " na seção 'INTEGRAÇÕES EXTERNAS' do .env e reinicie o ws-server. "
            "Nenhuma ação externa foi executada.")
    return [os.getenv(n) for n in names]


def _sim_on() -> bool:
    """Modo de SIMULAÇÃO (opt-in): permite testar o fluxo antes de ter as credenciais.
    Ligado por SIMULATE_EXTERNAL=true (global) ou SIMULATE_<TOOL>=true (por tool)."""
    return (os.getenv("SIMULATE_EXTERNAL", "") or "").strip().lower() in ("1", "true", "yes", "sim", "on")


def _simulado(tool: str, resumo: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Resposta CLARAMENTE ROTULADA como simulada (não é mock silencioso: o status é
    'simulado' e a mensagem avisa que nenhuma ação externa real ocorreu)."""
    out = {
        "status": "simulado",
        "tool": tool,
        "message": f"[SIMULAÇÃO] {resumo} — nenhuma ação externa REAL foi executada "
                   f"(SIMULATE_EXTERNAL ligado). Preencha as credenciais no .env para valer.",
        "id": "SIMULADO-" + tool.replace("_tool", "").replace("_api", "").upper(),
    }
    if extra:
        out.update(extra)
    return out


# ---------- LinkedIn: publicar post (API oficial) ----------
class LinkedInPublishSchema(BaseModel):
    text: str = Field(..., description="Texto do post a publicar no LinkedIn")


class LinkedInApiTool(BaseTool):
    name: str = "linkedin_api_tool"
    description: str = "Publica um post de texto no LinkedIn via API oficial (UGC Posts)."
    args_schema: type[BaseModel] = LinkedInPublishSchema

    def _run(self, text: str) -> Dict[str, Any]:
        if _sim_on():
            return _simulado("linkedin_api_tool", "publicaria este post no LinkedIn",
                             {"preview": (text or "")[:200]})
        import requests
        token, author = _require("LINKEDIN_ACCESS_TOKEN", "LINKEDIN_AUTHOR_URN")
        resp = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers={"Authorization": f"Bearer {token}",
                     "Content-Type": "application/json",
                     "X-Restli-Protocol-Version": "2.0.0"},
            json={"author": author, "lifecycleState": "PUBLISHED",
                  "specificContent": {"com.linkedin.ugc.ShareContent": {
                      "shareCommentary": {"text": text},
                      "shareMediaCategory": "NONE"}},
                  "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}},
            timeout=30)
        resp.raise_for_status()
        return {"status": "ok", "id": resp.headers.get("x-restli-id")}


# ---------- Instagram: publicar imagem (Graph API) ----------
class InstagramPublishSchema(BaseModel):
    image_url: str = Field(..., description="URL pública da imagem")
    caption: str = Field(default="", description="Legenda")


class InstagramGraphApiTool(BaseTool):
    name: str = "instagram_graph_api_tool"
    description: str = "Publica uma imagem no Instagram via Graph API (cria container + publica)."
    args_schema: type[BaseModel] = InstagramPublishSchema

    def _run(self, image_url: str, caption: str = "") -> Dict[str, Any]:
        if _sim_on():
            return _simulado("instagram_graph_api_tool", "publicaria esta imagem no Instagram",
                             {"image_url": image_url, "caption": (caption or "")[:200]})
        import requests
        token, ig_user = _require("INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_USER_ID")
        base = "https://graph.facebook.com/v19.0"
        c = requests.post(f"{base}/{ig_user}/media",
                          data={"image_url": image_url, "caption": caption, "access_token": token},
                          timeout=30)
        c.raise_for_status()
        creation_id = c.json().get("id")
        p = requests.post(f"{base}/{ig_user}/media_publish",
                          data={"creation_id": creation_id, "access_token": token}, timeout=30)
        p.raise_for_status()
        return {"status": "ok", "id": p.json().get("id")}


# ---------- Google Calendar: criar evento ----------
class GoogleCalendarEventSchema(BaseModel):
    summary: str = Field(..., description="Título do evento")
    start_iso: str = Field(..., description="Início em ISO 8601 (ex.: 2026-08-10T14:00:00-03:00)")
    end_iso: str = Field(..., description="Fim em ISO 8601")
    calendar_id: Optional[str] = Field(default=None, description="ID do calendário (default: GOOGLE_CALENDAR_ID ou 'primary')")


class GoogleCalendarApiTool(BaseTool):
    name: str = "google_calendar_api_tool"
    description: str = "Cria um evento no Google Calendar via API oficial (events.insert)."
    args_schema: type[BaseModel] = GoogleCalendarEventSchema

    def _run(self, summary: str, start_iso: str, end_iso: str,
             calendar_id: Optional[str] = None) -> Dict[str, Any]:
        if _sim_on():
            return _simulado("google_calendar_api_tool", f"criaria o evento '{summary}'",
                             {"summary": summary, "start": start_iso, "end": end_iso,
                              "htmlLink": "https://calendar.google.com/(evento-simulado)"})
        import requests
        (token,) = _require("GOOGLE_CALENDAR_ACCESS_TOKEN")
        cal = calendar_id or os.getenv("GOOGLE_CALENDAR_ID", "primary")
        resp = requests.post(
            f"https://www.googleapis.com/calendar/v3/calendars/{cal}/events",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"summary": summary, "start": {"dateTime": start_iso}, "end": {"dateTime": end_iso}},
            timeout=30)
        resp.raise_for_status()
        d = resp.json()
        return {"status": "ok", "id": d.get("id"), "htmlLink": d.get("htmlLink")}


# ---------- CMS genérico: publicar conteúdo ----------
class CmsPublishSchema(BaseModel):
    title: str = Field(..., description="Título")
    body: str = Field(..., description="Conteúdo (HTML ou markdown)")
    status: str = Field(default="draft", description="draft | published")


class CmsApiTool(BaseTool):
    name: str = "cms_api_tool"
    description: str = "Publica conteúdo no CMS do cliente via endpoint REST configurável."
    args_schema: type[BaseModel] = CmsPublishSchema

    def _run(self, title: str, body: str, status: str = "draft") -> Dict[str, Any]:
        if _sim_on():
            return _simulado("cms_api_tool", f"publicaria '{title}' no CMS",
                             {"title": title, "post_status": status})
        import requests
        url, key = _require("CMS_API_URL", "CMS_API_KEY")
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"title": title, "content": body, "status": status}, timeout=30)
        resp.raise_for_status()
        try:
            body_json = resp.json()
        except Exception:
            body_json = {}
        return {"status": "ok", "id": body_json.get("id"), "http_status": resp.status_code}


# Registro das integrações externas (mescladas no TOOL_REGISTRY pelo ws-server). Enquanto
# o .env não tiver as credenciais, cada _run() falha explícito na 1ª chamada (fail-loud).
EXT_TOOLS = {
    "linkedin_api_tool": LinkedInApiTool(),
    "instagram_graph_api_tool": InstagramGraphApiTool(),
    "google_calendar_api_tool": GoogleCalendarApiTool(),
    "cms_api_tool": CmsApiTool(),
}
