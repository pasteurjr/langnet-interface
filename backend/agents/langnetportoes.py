"""Portões dos ELOS entre etapas (F5 do plano v1.1) — o programa confere, não o modelo.

A revisão de 03/10/2026 mostrou que cada etapa produzia bem o seu artefato, mas a etapa seguinte
não consumia o que a anterior entregou — e eu media cada etapa isolada. Estes portões medem o ELO:

  1. Especificação: todo passo diz quem o executa (pronto · código gerado · agente)
  2. Especificação → Interface: todo caso de uso tem tela; toda ação tem executor; caso agêntico
     tem bloco de agente; nada sensível; nenhum botão solto; desenho sem script quebrado
  3. Especificação → Agentes & Tarefas: uma tarefa por caso agêntico, nenhuma convencional; agente
     declarado e usado; toda entrada com origem que existe
  4. Agentes & Tarefas → tasks.yaml: toda tarefa do documento está no YAML, no formato do CrewAI
  5. Interface → Código: toda tela do aplicativo é o desenho aprovado; todo controlador aprovado;
     toda mensagem de exceção do caso de uso está na tela; a ação de agente chama a tarefa certa
  6. Erro nunca é sucesso: o servidor de agentes e a biblioteca das telas tratam erro como erro

Cada portão devolve {nome, aprovado, problemas}; `conferir_elos` devolve todos e o total.
"""
from __future__ import annotations

import json
import re
from typing import Dict, List, Optional


def _portao(nome: str, problemas: List[str]) -> Dict:
    return {"nome": nome, "aprovado": not problemas, "problemas": problemas}


def p1_especificacao(spec_doc: str) -> Dict:
    from agents.langnetexecucao import conferir_execucao
    c = conferir_execucao(spec_doc or "")
    return _portao("Especificação: quem executa cada passo", c["problemas"] if c["casos_de_uso"] else ["especificação sem casos de uso"])


def p2_interface(spec_doc: str, ui_spec: Dict) -> Dict:
    from agents.langnetexecucao import extrair_execucao
    from agents.langnetfichatela import conferir_tela
    ucs = extrair_execucao(spec_doc or "")
    telas = (ui_spec or {}).get("screens") or []
    com_tela = {u for s in telas for u in (s.get("uc") or [])}
    p = [f"{u['uc']} sem tela" for u in ucs if u["uc"] not in com_tela]
    for s in telas:
        if not isinstance(s.get("ficha"), dict):
            p.append(f"{s.get('id')}: tela sem ficha (gerada antes do padrão)")
        p += conferir_tela(s)
        if any(a.get("target") for a in s.get("actions") or []):
            p.append(f"{s.get('id')}: ação com nome de tarefa inventado")
    for u in ucs:
        if any(st["executado_por"] == "agente" for st in u["passos"]):
            if not any(s.get("agentes") for s in telas if u["uc"] in (s.get("uc") or [])):
                p.append(f"{u['uc']}: caso agêntico sem bloco de agente na tela")
    return _portao("Especificação → Interface", p)


def p3_tarefas(spec_doc: str, ats_doc: str, schema_sql: str) -> Dict:
    from agents.langnettarefas import conferir_ats
    c = conferir_ats(ats_doc or "", spec_doc or "", schema_sql or "")
    return _portao("Especificação → Agentes & Tarefas", c["problemas"])


def p4_yaml(ats_doc: str, tasks_yaml: str) -> Dict:
    import yaml
    from agents.langnettarefas import _tarefas, CHAVES_CREWAI
    p = []
    try:
        ty = yaml.safe_load(re.sub(r"^```(?:ya?ml)?|```$", "", (tasks_yaml or "").strip(), flags=re.M)) or {}
    except Exception as e:
        return _portao("Agentes & Tarefas → tasks.yaml", [f"tasks.yaml não é YAML válido: {e}"])
    nomes = [t["name"] for t in _tarefas(ats_doc or "")]
    for n in nomes:
        if n not in ty:
            p.append(f"tarefa {n} do documento não está no tasks.yaml")
    for n, cfg in ty.items():
        if n not in nomes:
            p.append(f"tasks.yaml tem a tarefa {n}, que o documento de Agentes e Tarefas não declara")
        if isinstance(cfg, dict):
            fora = [k for k in cfg if k not in CHAVES_CREWAI]
            if fora:
                p.append(f"tarefa {n}: chaves fora do formato do CrewAI: {', '.join(fora)}")
            if not cfg.get("description") or not cfg.get("expected_output"):
                p.append(f"tarefa {n}: sem description ou expected_output")
    return _portao("Agentes & Tarefas → tasks.yaml", p)


def p5_codigo(spec_doc: str, ui_spec: Dict, arquivos: List[Dict], ats_doc: str, schema_sql: str) -> Dict:
    from agents.langnetapptelas import corpo_da_tela, conferir_controlador, _pascal
    from agents.langnettarefas import _tarefas
    from agents.langnetappapi import meta_do_modelo
    por_caminho = {a["path"]: a.get("content") or "" for a in arquivos or []}
    tabelas = meta_do_modelo(schema_sql or "")["tabelas"]
    tarefa_do_uc = {}
    for t in _tarefas(ats_doc or ""):
        for u in t.get("uc_related") or []:
            tarefa_do_uc.setdefault(u, t["name"])
    telas = [s for s in (ui_spec or {}).get("screens") or [] if (s.get("mockup_html") or "").strip()]
    ids = [s.get("id") for s in telas]
    p = []
    if any(c.startswith("frontend/src/petri-engine/") or c.endswith("MainExecutor.jsx") for c in por_caminho):
        p.append("o aplicativo leva o console Admin/Petri")
    regras = por_caminho.get("backend/regras.py", "")
    usados = set()
    for s in telas:
        comp = _pascal(s.get("id") or s.get("name"))
        while comp in usados:
            comp += "2"
        usados.add(comp)
        jsx = por_caminho.get(f"frontend/src/screens/{comp}.jsx")
        js = por_caminho.get(f"frontend/src/controladores/{comp}.js")
        if jsx is None or js is None:
            p.append(f"{s.get('id')}: a tela não está no aplicativo"); continue
        desenho = json.dumps(corpo_da_tela(s.get("mockup_html")), ensure_ascii=False)
        if desenho not in jsx:
            p.append(f"{s.get('id')}: a tela do aplicativo não é o desenho aprovado")
        tarefa = next((tarefa_do_uc[u] for u in s.get("uc") or [] if u in tarefa_do_uc), None)
        p += conferir_controlador(js, regras, s, tarefa, tabelas, ids)
        texto = jsx + js
        for m in s.get("mensagens") or []:
            if m["texto"][:60] not in texto and json.dumps(m["texto"][:60], ensure_ascii=False)[1:-1] not in texto:
                p.append(f"{s.get('id')}: a mensagem do caso de uso \"{m['texto'][:70]}\" não está na tela")
    return _portao("Interface → Código", p)


def p6_erro_nao_e_sucesso(arquivos: List[Dict]) -> Dict:
    por_caminho = {a["path"]: a.get("content") or "" for a in arquivos or []}
    p = []
    srv = por_caminho.get("ws-server/websocket_server.py", "")
    if srv and "_erro_de_banco_em_palavras" not in srv:
        p.append("o servidor de agentes não traduz o erro nem o separa do sucesso")
    cli = por_caminho.get("frontend/src/screens/wsClient.js", "")
    if cli and "success === false" not in cli:
        p.append("o cliente das telas aceita resposta com erro como sucesso")
    lnx = por_caminho.get("frontend/src/lnx.js", "")
    if lnx and "throw new Error" not in lnx:
        p.append("a biblioteca das telas não trata erro da API como erro")
    api = por_caminho.get("backend/main.py", "")
    if api and "HTTPException(422" not in api:
        p.append("a API não devolve o erro do banco como erro")
    return _portao("Erro nunca é sucesso", p)


def conferir_elos(spec_doc: str, ui_spec: Optional[Dict] = None, ats_doc: str = "", tasks_yaml: str = "",
                  schema_sql: str = "", arquivos: Optional[List[Dict]] = None) -> Dict:
    portoes = [p1_especificacao(spec_doc)]
    if ui_spec is not None:
        portoes.append(p2_interface(spec_doc, ui_spec))
    if ats_doc:
        portoes.append(p3_tarefas(spec_doc, ats_doc, schema_sql))
    if ats_doc and tasks_yaml:
        portoes.append(p4_yaml(ats_doc, tasks_yaml))
    if arquivos and ui_spec is not None:
        portoes.append(p5_codigo(spec_doc, ui_spec, arquivos, ats_doc, schema_sql))
        portoes.append(p6_erro_nao_e_sucesso(arquivos))
    return {"aprovado": all(p["aprovado"] for p in portoes), "portoes": portoes,
            "problemas": sum(len(p["problemas"]) for p in portoes)}
