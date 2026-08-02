"""
LangNet — Executor de Validação (Nível 1: Cobertura / Rastreabilidade).

Para cada caso de teste (efeito esperado do CEG), verifica se o APP GERADO tem um
artefato que entrega aquele efeito — cruzando com o ui_spec (telas + componentes +
ações) e as tasks geradas. Preenche "Resultado Obtido" e "Status" sem depender do
app rodando. Revela o que a geração cobriu ou deixou faltando.

Não é execução runtime (nível 2, contra o app vivo) — é rastreabilidade
spec → app gerado. Cada caso registra o MÉTODO usado e a evidência encontrada.

Status por caso:
  coberto      — há artefato claro que entrega o efeito (tela+ação, ou task)
  parcial      — a tela/fluxo existe, mas o elemento específico do efeito não foi
                 localizado (ex.: regra de negócio, validação) → exige checagem runtime
  nao_coberto  — nenhum artefato correspondente no app gerado
"""
from __future__ import annotations
import json
import re
from typing import List, Dict, Any, Optional

_STOP = {"o", "a", "os", "as", "de", "do", "da", "dos", "das", "e", "em", "para", "por",
         "com", "um", "uma", "no", "na", "que", "ao", "à", "sistema", "usuario", "usuário",
         "exibe", "mostra", "apresenta", "seu", "sua", "the", "of", "to"}

_UI_KW = ("exibe", "mostra", "apresenta", "alerta", "mensagem", "tela", "formul",
          "notific", "avisa", "solicita", "lista", "visualiza", "abre", "destaca")
_DATA_KW = ("salva", "grava", "cria", "gera", "registra", "atualiza", "exclui", "remove",
            "persiste", "processa", "calcula", "envia", "publica", "agenda", "sincroniza",
            "classifica", "coleta", "exporta", "valida")


def _tokens(s: str) -> set:
    return {w for w in re.findall(r"[a-zà-ú0-9]+", (s or "").lower()) if w not in _STOP and len(w) > 2}


def _overlap(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def classify_effect(desc: str) -> str:
    d = (desc or "").lower()
    ui = any(k in d for k in _UI_KW)
    data = any(k in d for k in _DATA_KW)
    if data and not ui:
        return "data"
    if ui and not data:
        return "ui"
    # efeito com verbo de dados no início (ex.: "salva persona e exibe sucesso") → dados
    for k in _DATA_KW:
        if d.strip().startswith(k):
            return "data"
    return "ui" if ui else ("data" if data else "ui")


def load_project_artifacts(project_id: str, get_db_connection) -> Dict[str, Any]:
    """Telas do ui_spec (nome+componentes+ações) e nomes de tasks do app gerado."""
    screens: List[dict] = []
    tasks: List[str] = []
    with get_db_connection() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT ui_spec_json FROM ui_spec_sessions WHERE project_id=%s "
                        "ORDER BY created_at DESC LIMIT 1", (project_id,))
            row = cur.fetchone()
            if row and row.get("ui_spec_json"):
                screens = json.loads(row["ui_spec_json"]).get("screens", [])
            cur.execute("SELECT tasks_yaml_content FROM tasks_yaml_sessions WHERE project_id=%s "
                        "ORDER BY created_at DESC LIMIT 1", (project_id,))
            row = cur.fetchone()
            if row and row.get("tasks_yaml_content"):
                tasks = re.findall(r"^([a-z][a-z0-9_]+):", row["tasks_yaml_content"], re.M)
        finally:
            cur.close()
    return {"screens": screens, "tasks": tasks}


def _screen_for_uc(uc_id: str, uc_name: str, screens: List[dict]) -> Optional[dict]:
    """Casa a tela do UC: por referência explícita ao UC, senão por similaridade de nome."""
    for s in screens:
        ucs = s.get("uc") or []
        if isinstance(ucs, str):
            ucs = [ucs]
        if uc_id in ucs:
            return s
    best, best_score = None, 0.25
    for s in screens:
        sc = _overlap(uc_name, s.get("name", ""))
        if sc > best_score:
            best, best_score = s, sc
    return best


def _screen_terms(screen: dict) -> str:
    if not screen:
        return ""
    parts = [screen.get("name", "")]
    for a in screen.get("actions", []):
        parts.append(a.get("label", ""))
        parts.append(a.get("target", ""))
    for c in screen.get("components", []):
        parts.append(c.get("label", "") or c.get("field", "") or c.get("type", ""))
    return " ".join(parts)


def verify_case(effect_desc: str, uc_id: str, uc_name: str, artifacts: dict) -> dict:
    kind = classify_effect(effect_desc)
    screen = _screen_for_uc(uc_id, uc_name, artifacts["screens"])
    screen_name = screen.get("name") if screen else None

    if kind == "data":
        # procura task/ação que entregue o efeito
        best_task, ts = None, 0.18
        for t in artifacts["tasks"]:
            sc = _overlap(effect_desc, t.replace("_", " "))
            if sc > ts:
                best_task, ts = t, sc
        act = None
        if screen:
            for a in screen.get("actions", []):
                if _overlap(effect_desc, a.get("label", "") + " " + (a.get("target") or "")) > 0.15:
                    act = a.get("label")
                    break
        if best_task:
            return {"metodo": "Dados", "status": "coberto",
                    "obtido": f"Task '{best_task}' entrega o efeito"
                              + (f"; tela '{screen_name}'" if screen_name else "")}
        if act:
            return {"metodo": "Dados", "status": "coberto",
                    "obtido": f"Ação '{act}' na tela '{screen_name}'"}
        if screen:
            return {"metodo": "Dados", "status": "parcial",
                    "obtido": f"Tela '{screen_name}' existe, mas sem task/ação específica p/ este efeito — verificar em runtime"}
        return {"metodo": "Dados", "status": "nao_coberto",
                "obtido": "Nenhuma task/tela correspondente no app gerado"}

    # kind == ui
    if screen:
        st = _overlap(effect_desc, _screen_terms(screen))
        if st > 0.12:
            return {"metodo": "UI", "status": "coberto",
                    "obtido": f"Tela '{screen_name}' com elemento correspondente"}
        return {"metodo": "UI", "status": "parcial",
                "obtido": f"Tela '{screen_name}' existe, mas o elemento do efeito (ex.: alerta/validação) não foi localizado no ui_spec — verificar em runtime"}
    return {"metodo": "UI", "status": "nao_coberto",
            "obtido": "Nenhuma tela correspondente no app gerado"}


def run_coverage(results: List[dict], artifacts: dict) -> dict:
    """Executa a verificação de cobertura sobre todos os casos. Retorna
    {"by_case": {case_id: {...}}, "summary": {coberto, parcial, nao_coberto, total}}."""
    by_case: Dict[str, dict] = {}
    tally = {"coberto": 0, "parcial": 0, "nao_coberto": 0}
    for r in results:
        if r.get("error"):
            continue
        for case in r.get("test_cases", []):
            eff = case.get("efeito_esperado", {}).get("desc", "")
            v = verify_case(eff, r["uc"], r.get("name", ""), artifacts)
            by_case[case["id"]] = v
            tally[v["status"]] = tally.get(v["status"], 0) + 1
    total = sum(tally.values())
    return {"by_case": by_case,
            "summary": {**tally, "total": total,
                        "pct_coberto": round(100 * tally["coberto"] / total) if total else 0}}
