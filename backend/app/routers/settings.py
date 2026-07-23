"""
Router: /api/settings — Configurações do Sistema (F1 / UC-P01)

Persiste config editável pela UI (banco de dados, provedor LLM, integrações) na
tabela system_settings, com precedência: valor salvo no banco > variável de ambiente
> default. SEGREDOS (senha de banco, API keys) NUNCA são retornados em claro:
- GET devolve string vazia para o segredo + flag `<key>_is_set` indicando se há valor.
- PUT só grava um segredo quando um novo valor não-vazio é enviado (senão mantém o atual).

Testes de conexão reais:
- POST /test-db  → tenta conectar no MySQL com as credenciais informadas.
- POST /test-llm → consulta o endpoint OpenAI-compatible (LM Studio/DeepSeek/OpenAI).
"""
import os
import json
import urllib.request
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.database import get_db_connection
from app.routers.auth import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])


# ── Esquema das configurações: section → campos (env var, é segredo?, default) ──
_SCHEMA: Dict[str, list] = {
    "database": [
        {"key": "db_host", "env": "DB_HOST", "secret": False, "default": "localhost"},
        {"key": "db_port", "env": "DB_PORT", "secret": False, "default": "3306"},
        {"key": "db_user", "env": "DB_USER", "secret": False, "default": ""},
        {"key": "db_password", "env": "DB_PASSWORD", "secret": True, "default": ""},
        {"key": "db_name", "env": "DB_NAME", "secret": False, "default": ""},
    ],
    "llm": [
        {"key": "llm_provider", "env": "LLM_PROVIDER", "secret": False, "default": "lmstudio"},
        {"key": "lmstudio_api_base", "env": "LMSTUDIO_API_BASE", "secret": False, "default": "http://localhost:1234/v1"},
        {"key": "lmstudio_model_name", "env": "LMSTUDIO_MODEL_NAME", "secret": False, "default": "qwen2.5-coder-32b-instruct"},
        {"key": "openai_api_key", "env": "OPENAI_API_KEY", "secret": True, "default": ""},
        {"key": "openai_model_name", "env": "OPENAI_MODEL_NAME", "secret": False, "default": "gpt-4o-mini"},
        {"key": "deepseek_api_key", "env": "DEEPSEEK_API_KEY", "secret": True, "default": ""},
        {"key": "deepseek_api_base", "env": "DEEPSEEK_API_BASE", "secret": False, "default": "https://api.deepseek.com/v1"},
        {"key": "deepseek_model_name", "env": "DEEPSEEK_MODEL_NAME", "secret": False, "default": "deepseek/deepseek-chat"},
    ],
}

_FIELD = {f["key"]: {**f, "section": sec} for sec, fields in _SCHEMA.items() for f in fields}


# ── Helpers de persistência ──
def _load_saved() -> Dict[str, str]:
    """Retorna {setting_key: setting_value} de tudo salvo no banco."""
    out: Dict[str, str] = {}
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT setting_key, setting_value FROM system_settings")
            for r in cur.fetchall():
                out[r["setting_key"]] = r["setting_value"]
            cur.close()
    except Exception as exc:  # noqa: BLE001
        print(f"[SETTINGS] falha ao ler system_settings: {exc}")
    return out


def _effective(key: str, saved: Optional[Dict[str, str]] = None) -> str:
    """Valor efetivo: banco (system_settings) > config atual (env/.env/defaults) > default.

    A config atual vem de `app.config.settings` (pydantic BaseSettings, que já mescla
    .env + os.environ + defaults) — mais fiel que os.getenv sozinho, pois o backend
    guarda parte da config (ex.: credenciais de banco) apenas nos defaults do config.py.
    """
    saved = saved if saved is not None else _load_saved()
    f = _FIELD[key]
    if key in saved and saved[key] is not None:
        return saved[key]
    try:
        from app.config import settings as _cfg
        val = getattr(_cfg, key, None)
        if val is not None and str(val) != "":
            return str(val)
    except Exception:  # noqa: BLE001
        pass
    return os.getenv(f["env"], f["default"])


def apply_settings_to_env() -> int:
    """Carrega os valores salvos no banco para os.environ, para consumidores que
    leem via os.getenv por chamada (ex.: o builder de LLM) pegarem ao vivo.
    Chamado no startup e após cada PUT. Retorna quantas chaves aplicou."""
    saved = _load_saved()
    n = 0
    for key, val in saved.items():
        f = _FIELD.get(key)
        if f and val is not None and val != "":
            os.environ[f["env"]] = val
            n += 1
    return n


# ── GET /settings ──
@router.get("")
def get_settings(current_user: dict = Depends(get_current_user)):
    """Config efetiva por seção. Segredos vêm vazios + flag <key>_is_set."""
    saved = _load_saved()
    result: Dict[str, Dict[str, Any]] = {}
    for section, fields in _SCHEMA.items():
        result[section] = {}
        for f in fields:
            key = f["key"]
            val = _effective(key, saved)
            if f["secret"]:
                # nunca expõe o segredo; só informa se há valor configurado
                result[section][key] = ""
                result[section][f"{key}_is_set"] = bool(val)
            else:
                result[section][key] = val
    return result


# ── PUT /settings ──
class UpdateSettingsRequest(BaseModel):
    # dict aninhado { section: { key: value } }
    settings: Dict[str, Dict[str, Any]]


@router.put("")
def update_settings(req: UpdateSettingsRequest, current_user: dict = Depends(get_current_user)):
    """Grava as configurações. Segredos só são gravados quando vem um valor não-vazio
    (campo vazio = manter o atual). Aplica em os.environ ao final."""
    written = 0
    with get_db_connection() as conn:
        cur = conn.cursor()
        for section, kv in (req.settings or {}).items():
            if section not in _SCHEMA:
                continue
            for key, value in (kv or {}).items():
                if key not in _FIELD or key.endswith("_is_set"):
                    continue
                f = _FIELD[key]
                if f["secret"] and (value is None or str(value) == ""):
                    continue  # não sobrescreve segredo com vazio
                cur.execute(
                    "INSERT INTO system_settings (section, setting_key, setting_value, is_secret, updated_by) "
                    "VALUES (%s, %s, %s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE setting_value=VALUES(setting_value), updated_by=VALUES(updated_by)",
                    (f["section"], key, str(value), 1 if f["secret"] else 0, current_user.get("id")),
                )
                written += 1
        conn.commit()
        cur.close()
    applied = apply_settings_to_env()
    return {"status": "ok", "written": written, "applied_to_env": applied}


# ── POST /settings/test-db ──
class TestDbRequest(BaseModel):
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None  # se vazio, usa o já salvo/efetivo
    db_name: Optional[str] = None


@router.post("/test-db")
def test_db(req: TestDbRequest, current_user: dict = Depends(get_current_user)):
    """Tenta conectar no MySQL com as credenciais informadas (senha vazia = usa a atual)."""
    import mysql.connector
    saved = _load_saved()
    host = req.db_host or _effective("db_host", saved)
    port = int(req.db_port or _effective("db_port", saved) or 3306)
    user = req.db_user or _effective("db_user", saved)
    password = req.db_password if (req.db_password not in (None, "")) else _effective("db_password", saved)
    name = req.db_name or _effective("db_name", saved)
    try:
        conn = mysql.connector.connect(host=host, port=port, user=user, password=password,
                                       database=name, connection_timeout=6)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=%s", (name,))
        ntables = cur.fetchone()[0]
        cur.close(); conn.close()
        return {"ok": True, "message": f"Conectado a {name}@{host}:{port} — {ntables} tabelas."}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


# ── POST /settings/test-llm ──
class TestLlmRequest(BaseModel):
    provider: Optional[str] = None
    api_base: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None


@router.post("/test-llm")
def test_llm(req: TestLlmRequest, current_user: dict = Depends(get_current_user)):
    """Consulta {api_base}/models do endpoint OpenAI-compatible e verifica o modelo."""
    saved = _load_saved()
    provider = (req.provider or _effective("llm_provider", saved) or "lmstudio").lower()
    if provider == "lmstudio":
        api_base = req.api_base or _effective("lmstudio_api_base", saved)
        model = req.model or _effective("lmstudio_model_name", saved)
        api_key = "lm-studio"
    elif provider == "deepseek":
        api_base = req.api_base or _effective("deepseek_api_base", saved)
        model = req.model or _effective("deepseek_model_name", saved)
        api_key = req.api_key or _effective("deepseek_api_key", saved)
    else:  # openai
        api_base = req.api_base or "https://api.openai.com/v1"
        model = req.model or _effective("openai_model_name", saved)
        api_key = req.api_key or _effective("openai_api_key", saved)
    url = api_base.rstrip("/") + "/models"
    try:
        r = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key or 'x'}"})
        with urllib.request.urlopen(r, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        models = [m.get("id") for m in data.get("data", []) if m.get("id")]
        found = model in models
        return {"ok": True, "provider": provider, "endpoint": url,
                "model_found": found, "model": model,
                "models_sample": models[:10],
                "message": (f"Modelo '{model}' disponível." if found
                            else f"Endpoint OK, mas o modelo '{model}' não está na lista.")}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "provider": provider, "endpoint": url, "error": str(exc)}
