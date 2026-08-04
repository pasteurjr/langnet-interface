"""
WebSocket server compatível com o padrão visualtasksexec.
Recebe {"type":"execute_task", "data":{"task_name", "input_data"}}
e emite task_start / verbose / task_completed / error.
"""
import asyncio
import json
import os
import traceback
from datetime import datetime
from typing import Any, Dict

import websockets
import yaml
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

load_dotenv()

import tools as tools_module
import adapters as adapters_module


# ─── LLM: 3 providers configuráveis via LLM_PROVIDER ─────────────────────────
# - deepseek (default): API cloud, custa tokens. V4 Flash/Pro.
# - lmstudio: LM Studio local, R1 distill Qwen 32B. Zero custo/token.
# - openai: fallback.
#
# Estratégia: 2 LLMs pré-construídos, um "fast" e um "reasoning".
# - FLASH_LLM: pura geração de texto/JSON. Rápido. Agentes SEM tools.
# - PRO_LLM: raciocina antes de decidir chamar tool. Agentes COM tools.
# _build_agent escolhe automaticamente com base em `AGENT_TOOLS[agent_id]`.
def _current_provider() -> str:
    return (os.getenv("LLM_PROVIDER") or "deepseek").lower()


def _build_llm_flash() -> LLM:
    prov = _current_provider()
    if prov == "lmstudio":
        # LM Studio API OpenAI-compatible. Sem custo por token.
        # Modelo FAST (mesmo do reasoning aqui — LM Studio típico só tem R1 carregado).
        _m = os.getenv("LMSTUDIO_MODEL_NAME", "openai/deepseek-r1-distill-qwen-32b")
        if _m and not _m.startswith("openai/") and "/" not in _m:
            _m = f"openai/{_m}"
        return LLM(
            model=_m,
            api_key=os.getenv("LMSTUDIO_API_KEY", "lm-studio"),
            base_url=os.getenv("LMSTUDIO_API_BASE", "http://192.168.1.115:1234/v1"),
            temperature=0.7,
            max_tokens=int(os.getenv("LMSTUDIO_MAX_TOKENS", "16000")),
        )
    if prov == "deepseek" and os.getenv("DEEPSEEK_API_KEY"):
        return LLM(
            model=os.getenv("DEEPSEEK_MODEL_NAME", "deepseek/deepseek-v4-flash"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"),
            temperature=0.7,
            max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "32768")),
            extra_body={"reasoning": {"enabled": False}},
        )
    return LLM(model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
               api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7)


def _build_llm_pro() -> LLM:
    prov = _current_provider()
    if prov == "lmstudio":
        # R1 já raciocina por padrão — sem flag necessário. Mesmo modelo do flash aqui.
        _m = os.getenv("LMSTUDIO_MODEL_NAME_PRO", os.getenv("LMSTUDIO_MODEL_NAME", "openai/deepseek-r1-distill-qwen-32b"))
        if _m and not _m.startswith("openai/") and "/" not in _m:
            _m = f"openai/{_m}"
        return LLM(
            model=_m,
            api_key=os.getenv("LMSTUDIO_API_KEY", "lm-studio"),
            base_url=os.getenv("LMSTUDIO_API_BASE", "http://192.168.1.115:1234/v1"),
            temperature=0.3,
            max_tokens=int(os.getenv("LMSTUDIO_MAX_TOKENS_PRO", "24000")),
        )
    if prov == "deepseek" and os.getenv("DEEPSEEK_API_KEY"):
        return LLM(
            model=os.getenv("DEEPSEEK_MODEL_NAME_PRO", "deepseek/deepseek-v4-pro"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"),
            temperature=0.3,
            max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS_PRO", "32768")),
            extra_body={"reasoning": {"enabled": True}},
        )
    return LLM(model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
               api_key=os.getenv("OPENAI_API_KEY"), temperature=0.3)


FLASH_LLM = _build_llm_flash()
PRO_LLM = _build_llm_pro()
# Compat: código legado que ainda referencia SHARED_LLM funciona.
SHARED_LLM = FLASH_LLM


def _load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


AGENTS_CONFIG = _load_yaml("agents.yaml")
TASKS_CONFIG = _load_yaml("tasks.yaml")


TOOL_REGISTRY = getattr(tools_module, "TOOL_REGISTRY", {})
# F2 Fase 3: mescla as tools MCP (mcp_tools.py) no registry — agentes com tools MCP
# atribuídas as resolvem por nome, igual às tools embutidas.
try:
    import mcp_tools as _mcp_mod
    TOOL_REGISTRY.update(getattr(_mcp_mod, "MCP_TOOLS", {}))
    if getattr(_mcp_mod, "MCP_TOOLS", None):
        print(f"[ws] {len(_mcp_mod.MCP_TOOLS)} tool(s) MCP carregada(s)")
except Exception as _mcp_e:
    pass
TASK_TOOLS = getattr(adapters_module, "TASK_TOOLS", {})
AGENT_TOOLS = getattr(adapters_module, "AGENT_TOOLS", {})


def _resolve_tools(names):
    """Converte lista de nomes em instâncias de tool via TOOL_REGISTRY.

    Tool referenciada mas AUSENTE do registry NÃO é descartada em silêncio (isso faria o
    agente achar que a ação externa foi feita). Vira uma tool 'não configurada' que FALHA
    EXPLÍCITO ao ser chamada — instruindo a configurar via MCP. Nunca finge sucesso."""
    out = []
    for name in names or []:
        inst = TOOL_REGISTRY.get(name)
        if inst is None:
            try:
                from tools_std import make_unconfigured_tool
                inst = make_unconfigured_tool(name)
                print(f"[ws] tool '{name}' NÃO configurada → fail-loud (atribua um servidor MCP)")
            except Exception:
                continue
        out.append(inst)
    return out


def _agent_for_task(task_id: str) -> str:
    """Resolve o agente da task — preferindo task.agent, com fallback
    para o primeiro agente em AGENT_TOOLS que mencione essa task."""
    cfg = TASKS_CONFIG.get(task_id, {}) or {}
    agent_id = cfg.get("agent") or cfg.get("agent_id")
    if agent_id:
        return agent_id
    # Fallback: primeiro agente da lista (degradação graceful)
    if AGENTS_CONFIG:
        return next(iter(AGENTS_CONFIG.keys()))
    return ""


def _build_agent(agent_id: str) -> Agent:
    cfg = AGENTS_CONFIG.get(agent_id, {})
    tool_names = AGENT_TOOLS.get(agent_id, [])
    tools = _resolve_tools(tool_names)
    # Se o agente tem TOOLS reais, usa PRO_LLM (com reasoning) — necessário
    # pra CrewAI conseguir fazer tool call. Sem tools, usa FLASH_LLM (mais barato/rápido).
    chosen_llm = PRO_LLM if tools else FLASH_LLM
    return Agent(
        role=cfg.get("role", agent_id),
        goal=cfg.get("goal", ""),
        backstory=cfg.get("backstory", ""),
        verbose=cfg.get("verbose", True),
        allow_delegation=cfg.get("allow_delegation", False),
        tools=tools,
        llm=chosen_llm,
    )


def _build_task(task_id: str, agent: Agent, description: str) -> Task:
    cfg = TASKS_CONFIG.get(task_id, {})
    tool_names = TASK_TOOLS.get(task_id, [])
    return Task(
        description=description or cfg.get("description", ""),
        expected_output=cfg.get("expected_output", ""),
        agent=agent,
        tools=_resolve_tools(tool_names),
    )


async def _send(ws, msg_type: str, data: Any) -> None:
    # default=str serializa datetime/date/Decimal/UUID vindos do banco (SELECT *).
    await ws.send(json.dumps({
        "type": msg_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
    }, default=str, ensure_ascii=False))


async def _execute_task(ws, task_name: str, input_data: Dict[str, Any]) -> None:
    await _send(ws, "task_start", {"task_name": task_name, "input_data": input_data})

    # Deterministic-first: se adapters.py define <task>_deterministic, roda direto
    # em Python (sem CrewAI/LLM). Vale inclusive para tasks CRUD auto-geradas
    # (listar_/atualizar_/excluir_<entidade>) que NÃO estão no tasks.yaml — por
    # isso este check vem ANTES da validação em TASKS_CONFIG.
    det_fn = getattr(adapters_module, f"{task_name}_deterministic", None)
    if callable(det_fn):
        try:
            payload = input_data if isinstance(input_data, dict) else {}
            loop = asyncio.get_running_loop()
            det_result = await loop.run_in_executor(None, det_fn, payload)
            await _send(ws, "task_completed", {"task_name": task_name, "result": det_result})
        except Exception as _exc:
            await _send(ws, "error", {"task_name": task_name, "error": str(_exc), "traceback": traceback.format_exc()})
        return

    task_cfg = TASKS_CONFIG.get(task_name)
    if not task_cfg:
        await _send(ws, "error", {"task_name": task_name, "error": f"task '{task_name}' não definida em tasks.yaml"})
        return

    agent_id = task_cfg.get("agent") or task_cfg.get("agent_id")
    if not agent_id:
        await _send(ws, "error", {"task_name": task_name, "error": "task sem agente vinculado"})
        return

    try:
        agent = _build_agent(agent_id)

        # Aplica input_func (extrai dados de input_data → kwargs)
        input_fn = getattr(adapters_module, f"{task_name}_input_func", None)
        prepared = input_fn(input_data) if callable(input_fn) else input_data

        # Formata a descrição da task com inputs — usa format_map com dict que
        # devolve string vazia p/ chaves ausentes, evitando fallback silencioso
        # que deixa {placeholders} literais no prompt do agente.
        description = task_cfg.get("description", "")
        if prepared:
            class _SafeDict(dict):
                def __missing__(self, key):
                    return ""  # placeholder ausente vira vazio (não quebra)
            # Achata prepared em strings pra evitar KeyError em __missing__
            try:
                description = description.format_map(_SafeDict(prepared))
            except Exception:
                pass  # último recurso: mantém description literal

        task = _build_task(task_name, agent, description)
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, crew.kickoff)

        raw = getattr(result, "raw", None) or str(result)

        output_fn = getattr(adapters_module, f"{task_name}_output_func", None)
        if callable(output_fn):
            try:
                parsed = output_fn(input_data, raw)
            except Exception:
                parsed = {"raw": raw}
        else:
            parsed = {"raw": raw}

        await _send(ws, "task_completed", {"task_name": task_name, "result": parsed})
    except Exception as exc:
        await _send(ws, "error", {"task_name": task_name, "error": str(exc), "traceback": traceback.format_exc()})


async def _handle_client(ws):
    await _send(ws, "connected", {"available_tasks": list(TASKS_CONFIG.keys())})
    async for message in ws:
        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            await _send(ws, "error", {"error": "invalid JSON"})
            continue

        msg_type = payload.get("type")
        data = payload.get("data") or {}

        if msg_type == "execute_task":
            await _execute_task(ws, data.get("task_name"), data.get("input_data") or {})
        elif msg_type == "ping":
            await _send(ws, "pong", {"timestamp": datetime.utcnow().isoformat()})
        elif msg_type == "get_task_info":
            await _send(ws, "task_info", {"tasks": list(TASKS_CONFIG.keys())})
        else:
            await _send(ws, "error", {"error": f"unknown message type: {msg_type}"})


async def run_websocket_server(host: str = "localhost", port: int = 5003):
    async with websockets.serve(_handle_client, host, port, ping_interval=30, ping_timeout=10):
        print(f"🌐 WebSocket aceitando conexões em ws://{host}:{port}")
        await asyncio.Future()  # run forever
