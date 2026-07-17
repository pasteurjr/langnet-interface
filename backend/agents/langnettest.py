"""
LangNet — Geração de Casos de Teste por Grafo de Causa-Efeito (CEG) + validação.

Pipeline:
  1. Parseia cada caso de uso da spec (fluxo principal + alternativos + exceção).
  2. LLM extrai o grafo causa-efeito (causas = ações do ator, efeitos = respostas).
  3. Motor determinístico (ceg_engine) gera a tabela de decisão minimizada e os
     casos de teste (método do artigo do Pasteur Ottoni).
  4. (execução — fase seguinte) roda cada caso contra a app e compara esperado×obtido.
"""
from __future__ import annotations
import json
import os
import re
from typing import Any, Dict, List, Optional

from prompts.generate_ceg import build_ceg_prompt
from agents.ceg_engine import generate_test_cases

_llm_cache: Dict[str, Any] = {}


def _get_llm():
    key = "cegtest"
    if key in _llm_cache:
        return _llm_cache[key]
    from crewai import LLM as CrewLLM
    provider = (os.getenv("LLM_PROVIDER") or "deepseek").lower()
    if provider == "lmstudio":
        lm = os.getenv("LMSTUDIO_MODEL_NAME", "openai/deepseek-r1-distill-qwen-32b")
        if lm and not lm.startswith("openai/") and "/" not in lm:
            lm = f"openai/{lm}"
        _llm_cache[key] = CrewLLM(model=lm, api_key=os.getenv("LMSTUDIO_API_KEY", "lm-studio"),
                                  base_url=os.getenv("LMSTUDIO_API_BASE", "http://192.168.1.115:1234/v1"),
                                  temperature=0.1, max_tokens=int(os.getenv("LMSTUDIO_MAX_TOKENS", "16000")))
        return _llm_cache[key]
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY não configurada.")
    model = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-v4-flash")
    if not model.startswith("deepseek/"):
        model = f"deepseek/{model}"
    _llm_cache[key] = CrewLLM(model=model, api_key=api_key,
                              base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
                              temperature=0.1, max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "32768")),
                              extra_body={"reasoning": {"enabled": False}})
    return _llm_cache[key]


def _call_llm(prompt: str) -> str:
    llm = _get_llm()
    try:
        return llm.call([{"role": "user", "content": prompt}])
    except Exception:
        return llm.call(prompt)


def _extract_json(text: str) -> Optional[str]:
    if not text:
        return None
    t = re.sub(r'^```(?:json)?\s*\n', '', text.strip())
    t = re.sub(r'\n```\s*$', '', t)
    start = t.find("{")
    if start < 0:
        return None
    depth = 0; in_str = False; esc = False
    for i in range(start, len(t)):
        ch = t[i]
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': in_str = False
        else:
            if ch == '"': in_str = True
            elif ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return t[start:i + 1]
    return None


# ─────────────────────────────────────────────────────────────
# Parsing dos casos de uso (fluxos completos)
# ─────────────────────────────────────────────────────────────
def parse_use_cases(spec_document: str) -> List[dict]:
    """Extrai UCs com fluxo principal, alternativos e exceção (texto bruto por seção)."""
    ucs = []
    pattern = re.compile(r'\*\*(UC-\d+):\s*(.+?)\*\*(.*?)(?=\*\*UC-\d+:|\Z)', re.S)
    for m in pattern.finditer(spec_document):
        uc_id, name, body = m.group(1).strip(), m.group(2).strip(), m.group(3)
        uc = {"id": uc_id, "name": name}
        for fm in re.finditer(r'\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|', body):
            k = fm.group(1).strip().lower()
            if "ator principal" in k: uc["actor"] = fm.group(2).strip()
            elif "objetivo" in k: uc["objetivo"] = fm.group(2).strip()
        def section(title):
            sm = re.search(rf'{title}(.*?)(?=####|\*\*UC-|\Z)', body, re.S)
            return sm.group(1).strip() if sm else ""
        uc["fluxo_principal"] = section(r'Fluxo Principal')
        uc["fluxos_alt"] = section(r'Fluxos Alternativos') or "(nenhum)"
        uc["fluxos_exc"] = section(r'Fluxos de Exceção') or "(nenhum)"
        ucs.append(uc)
    return ucs


def ceg_for_uc(uc: dict) -> Optional[dict]:
    """LLM → grafo causa-efeito válido (com 1 retry)."""
    prompt = build_ceg_prompt(uc)
    for attempt in range(2):
        raw = _call_llm(prompt if attempt == 0 else prompt + "\n\n⚠️ Retorne SOMENTE o JSON válido do grafo.")
        js = _extract_json(raw or "")
        if not js:
            continue
        try:
            ceg = json.loads(js)
        except Exception:
            continue
        if ceg.get("causes") and ceg.get("effects") and ceg.get("rules"):
            ceg.setdefault("uc", uc["id"])
            ceg.setdefault("constraints", [])
            return ceg
    return None


def generate_ceg_test_cases(spec_document: str, only: Optional[List[str]] = None) -> dict:
    """Gera CEG + tabela de decisão + casos de teste para todos os UCs (ou só `only`)."""
    ucs = parse_use_cases(spec_document)
    if only:
        ucs = [u for u in ucs if u["id"] in only]
    results = []
    log = []
    for uc in ucs:
        ceg = ceg_for_uc(uc)
        if not ceg:
            log.append(f"{uc['id']}: CEG falhou")
            results.append({"uc": uc["id"], "name": uc["name"], "error": "CEG não gerado"})
            continue
        tc = generate_test_cases(ceg)
        results.append({"uc": uc["id"], "name": uc["name"], "actor": uc.get("actor"),
                        "objetivo": uc.get("objetivo"), "ceg": ceg, **tc})
        log.append(f"{uc['id']}: {tc['n_causes']} causas, {tc['n_effects']} efeitos, {tc['n_cases']} casos")
        print(f"[CEG] {log[-1]}")
    return {"results": results, "log": "\n".join(log),
            "total_cases": sum(r.get("n_cases", 0) for r in results)}
