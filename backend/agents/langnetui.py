"""
LangNet UI Spec — etapa de Especificação & Protótipo de Interface.

Consome a Especificação Funcional (UCs + wireframes) + schema_sql do Data Model
e produz, por tela:
  - estrutura JSON (rota, entidade, componentes ligados ao schema, ações)
  - mockup HTML/CSS standalone
  - PNG do mockup (render headless via Playwright) para revisão visual

Espelha o padrão de agents/langnetdatamodel.py (LLM CrewAI, provider-agnóstico).
Geração chunked: 1 tela por chamada LLM.
"""
from __future__ import annotations

import base64
import json
import os
from typing import Any, Dict, List, Optional

from prompts.generate_ui_spec import (
    parse_uc_blocks, parse_schema_tables, select_relevant_tables,
    build_sub_schema, is_agentic_screen, build_single_screen_prompt,
    extract_json_object, validate_screen,
)

_llm_cache: Dict[str, Any] = {}


# ────────────────────────────────────────────────────────────────────────
# LLM (mesmo padrão do langnetdatamodel)
# ────────────────────────────────────────────────────────────────────────
def _get_llm():
    key = "uispec"
    if key in _llm_cache:
        return _llm_cache[key]

    from crewai import LLM as CrewLLM
    provider = (os.getenv("LLM_PROVIDER") or "deepseek").lower()

    if provider == "lmstudio":
        lm_model = os.getenv("LMSTUDIO_MODEL_NAME", "openai/deepseek-r1-distill-qwen-32b")
        if lm_model and not lm_model.startswith("openai/") and "/" not in lm_model:
            lm_model = f"openai/{lm_model}"
        _llm_cache[key] = CrewLLM(
            model=lm_model,
            api_key=os.getenv("LMSTUDIO_API_KEY", "lm-studio"),
            base_url=os.getenv("LMSTUDIO_API_BASE", "http://192.168.1.115:1234/v1"),
            temperature=0.3,
            max_tokens=int(os.getenv("LMSTUDIO_MAX_TOKENS", "16000")),
        )
        return _llm_cache[key]

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY não configurada.")
    model = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-v4-flash")
    if not model.startswith("deepseek/"):
        model = f"deepseek/{model}"
    _llm_cache[key] = CrewLLM(
        model=model,
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
        temperature=0.3,
        max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "32768")),
        extra_body={"reasoning": {"enabled": False}},
    )
    return _llm_cache[key]


def _call_llm(prompt: str) -> str:
    llm = _get_llm()
    try:
        return llm.call([{"role": "user", "content": prompt}])
    except Exception:
        return llm.call(prompt)


# ────────────────────────────────────────────────────────────────────────
# Render HTML → PNG (Playwright headless, sync API)
# ────────────────────────────────────────────────────────────────────────
def render_html_to_png_b64(html: str, width: int = 960) -> Optional[str]:
    """Renderiza um HTML standalone em PNG e devolve como data URI base64.
    Retorna None se o Playwright não estiver disponível ou falhar."""
    if not html:
        return None
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        print(f"[UI_SPEC] Playwright indisponível: {e}")
        return None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox"])
            page = browser.new_page(viewport={"width": width, "height": 800})
            page.set_content(html, wait_until="networkidle")
            # Tailwind CDN (JIT) processa as classes via JS após o load — dá um
            # tempo pra pintar antes de tirar o screenshot.
            page.wait_for_timeout(1200)
            png = page.screenshot(full_page=True)
            browser.close()
        return "data:image/png;base64," + base64.b64encode(png).decode("ascii")
    except Exception as e:
        print(f"[UI_SPEC] render falhou: {e}")
        return None


# ────────────────────────────────────────────────────────────────────────
# Geração de UMA tela (com retry)
# ────────────────────────────────────────────────────────────────────────
def _generate_one_screen(uc: Dict[str, str], sub_schema: str) -> Optional[Dict[str, Any]]:
    prompt = build_single_screen_prompt(uc, sub_schema)
    raw = _call_llm(prompt)
    obj_txt = extract_json_object(raw or "")
    screen = None
    if obj_txt:
        try:
            screen = json.loads(obj_txt)
        except Exception:
            screen = None

    if screen:
        ok, _ = validate_screen(screen)
        if ok:
            return screen

    # Retry com instrução explícita
    retry_prompt = prompt + (
        "\n\n⚠️ RETRY: sua resposta anterior não era um JSON válido com "
        "mockup_html contendo HTML+CSS. Retorne SOMENTE o objeto JSON, começando "
        "com { e terminando com }."
    )
    raw2 = _call_llm(retry_prompt)
    obj2 = extract_json_object(raw2 or "")
    if obj2:
        try:
            screen2 = json.loads(obj2)
            ok2, _ = validate_screen(screen2)
            if ok2:
                return screen2
        except Exception:
            pass
    return None


# ────────────────────────────────────────────────────────────────────────
# Workflow completo
# ────────────────────────────────────────────────────────────────────────
def execute_ui_spec_workflow(
    specification_document: str,
    schema_sql: str = "",
    render_png: bool = True,
) -> Dict[str, Any]:
    """Gera a UI Spec inteira (todas as telas) a partir da spec + schema.

    Retorna:
      {
        "ui_spec": {screens, navigation, action_map},
        "mockups": {screen_id: png_data_uri},
        "screens_count": N,
        "generation_log": "..."
      }
    """
    ucs = parse_uc_blocks(specification_document)
    tables = parse_schema_tables(schema_sql) if schema_sql else {}

    log_lines: List[str] = [f"UCs: {len(ucs)}, tabelas: {len(tables)}"]
    screens: List[Dict[str, Any]] = []
    mockups: Dict[str, str] = {}
    action_map: Dict[str, Dict[str, str]] = {}

    for idx, uc in enumerate(ucs, 1):
        picked = select_relevant_tables(uc, tables)
        sub_schema = build_sub_schema(picked, tables)
        screen = _generate_one_screen(uc, sub_schema)
        if not screen:
            log_lines.append(f"[{idx}/{len(ucs)}] {uc.get('id')} FALHOU")
            print(f"[UI_SPEC] [{idx}/{len(ucs)}] {uc.get('id')} falhou")
            continue

        # Separa o HTML pesado do PNG
        html = screen.get("mockup_html", "")
        if render_png and html:
            png = render_html_to_png_b64(html)
            if png:
                mockups[screen["id"]] = png

        # action_map: agrega ações task/crud
        for act in (screen.get("actions") or []):
            tgt = act.get("target")
            kind = act.get("kind")
            if tgt and kind in ("task", "crud"):
                action_map[tgt] = {"kind": kind, "screen": screen["id"]}

        screens.append(screen)
        log_lines.append(
            f"[{idx}/{len(ucs)}] {uc.get('id')} → {screen.get('id')} "
            f"({len(screen.get('components', []))} comps, png={'sim' if screen['id'] in mockups else 'nao'})"
        )
        print(f"[UI_SPEC] {log_lines[-1]}")

    navigation = _build_navigation(screens)
    ui_spec = {
        "screens": screens,
        "navigation": navigation,
        "action_map": action_map,
    }
    return {
        "ui_spec": ui_spec,
        "mockups": mockups,
        "screens_count": len(screens),
        "generation_log": "\n".join(log_lines),
    }


def _build_navigation(screens: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Agrupa telas numa navegação lateral. Uma entrada por rota-base."""
    nav: List[Dict[str, str]] = []
    seen = set()
    for s in screens:
        route = s.get("route") or f"/{s.get('id')}"
        base = "/" + route.strip("/").split("/")[0]
        if base in seen:
            continue
        seen.add(base)
        nav.append({"label": s.get("name", base), "route": base})
    return nav


_REFINE_SCREEN_PROMPT = """Você é designer de produto e engenheiro front-end sênior.
Abaixo está a especificação JSON de UMA tela (com seu mockup HTML/Tailwind) e uma
INSTRUÇÃO de mudança do usuário. Aplique SÓ a mudança pedida e devolva a tela
INTEIRA atualizada, no MESMO formato JSON (com mockup_html completo).

REGRAS:
- Mantenha o design system Tailwind já usado (sidebar slate-900, cards rounded-2xl,
  inputs com focus ring indigo, chips coloridos, fonte Inter, Tailwind via CDN).
- Preserve tudo que a instrução NÃO pediu pra mudar (id, route, demais campos).
- Se a instrução adiciona um campo, inclua-o em `components` (com type/label/bindTo)
  E também no mockup_html.
- Retorne SOMENTE o objeto JSON da tela, começando com {{ e terminando com }}.

## TELA ATUAL (JSON)
{screen_json}

## INSTRUÇÃO DO USUÁRIO
{instruction}

Retorne a tela atualizada (apenas o JSON):"""


def refine_one_screen(screen: Dict[str, Any], instruction: str, render_png: bool = True) -> Dict[str, Any]:
    """Refina UMA tela conforme a instrução. Regenera estrutura + mockup_html e
    re-renderiza o PNG. Retorna {'screen': novo_screen, 'png': data_uri|None}."""
    prompt = _REFINE_SCREEN_PROMPT.format(
        screen_json=json.dumps(screen, ensure_ascii=False),
        instruction=instruction,
    )
    raw = _call_llm(prompt)
    obj = extract_json_object(raw or "")
    new_screen = None
    if obj:
        try:
            cand = json.loads(obj)
            ok, _ = validate_screen(cand)
            if ok:
                new_screen = cand
        except Exception:
            new_screen = None

    if new_screen is None:
        # retry curto
        raw2 = _call_llm(prompt + "\n\n⚠️ Retorne SOMENTE o JSON válido da tela.")
        obj2 = extract_json_object(raw2 or "")
        if obj2:
            try:
                cand2 = json.loads(obj2)
                ok2, _ = validate_screen(cand2)
                if ok2:
                    new_screen = cand2
            except Exception:
                pass
    if new_screen is None:
        raise RuntimeError("refino da tela não retornou JSON válido")

    # preserva id/route se o LLM os removeu
    new_screen.setdefault("id", screen.get("id"))
    new_screen.setdefault("route", screen.get("route"))

    png = None
    if render_png and new_screen.get("mockup_html"):
        png = render_html_to_png_b64(new_screen["mockup_html"])
    return {"screen": new_screen, "png": png}


def refine_ui_spec(current_ui_spec_json: str, instruction: str, schema_sql: str = "",
                   screen_id: Optional[str] = None) -> Dict[str, Any]:
    """Refina a UI spec. Se screen_id é dado, refina SÓ aquela tela (robusto e
    barato); senão tenta inferir a tela alvo pela instrução; se não achar, aplica
    à primeira tela. Re-renderiza o PNG da tela alterada.

    Retorna {'ui_spec': ..., 'mockup_update': {screen_id: png}}.
    """
    ui_spec = json.loads(current_ui_spec_json) if current_ui_spec_json else {}
    screens = ui_spec.get("screens", [])
    if not screens:
        raise RuntimeError("ui_spec sem telas")

    # Seleciona a tela alvo
    target_idx = None
    if screen_id:
        for i, s in enumerate(screens):
            if s.get("id") == screen_id:
                target_idx = i
                break
    if target_idx is None:
        # tenta casar por nome/id mencionado na instrução
        instr_low = instruction.lower()
        for i, s in enumerate(screens):
            name = (s.get("name", "") + " " + s.get("id", "")).lower()
            toks = [t for t in name.replace("-", " ").split() if len(t) > 3]
            if any(t in instr_low for t in toks):
                target_idx = i
                break
    if target_idx is None:
        target_idx = 0

    result = refine_one_screen(screens[target_idx], instruction)
    new_screen = result["screen"]
    screens[target_idx] = new_screen
    ui_spec["screens"] = screens

    mockup_update = {}
    if result.get("png"):
        mockup_update[new_screen.get("id")] = result["png"]

    return {"ui_spec": ui_spec, "mockup_update": mockup_update, "refined_screen": new_screen.get("id")}
