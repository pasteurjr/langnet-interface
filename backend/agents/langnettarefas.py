"""Agentes & Tarefas pelo padrão — só o passo `agente` vira tarefa, no agente certo, com toda entrada.

Medido no BioByte v5 (03/10/2026), no documento de Agentes e Tarefas:
- o modelo escreveu as 5 tarefas agênticas certas (### T-AGN-001..005), com a classificação no
  agente clínico e a recomendação e o alerta no agente de tratamento;
- os laços de cobertura não as reconheceram (título ### em vez de ####) e anexaram 31 tarefas —
  uma por caso de uso, inclusive login, cadastro e backup — com agentes de nome inventado;
- a Geração de Código escolheu o agente pela ferramenta em comum e pôs as 5 no agente clínico;
- o UC-025, agêntico, ficou sem tarefa;
- a classificação NHSN declarava `criterios_candidatos` e `data_inicio_caso`, mas nada conferia
  de onde vinham — no aplicativo chegaram vazios e a decisão ficou "pendente".

Aqui a regra é do PROGRAMA, tirada da coluna "Executado por" da Especificação:
- uma tarefa por caso de uso agêntico (cobrindo os seus passos `agente`), e nenhuma para
  caso de uso convencional;
- o agente de cada tarefa é o que o documento declara, e todo agente declarado tem tarefa;
- cada entrada da tarefa declara a ORIGEM (tela, banco, tarefa anterior, contexto), e a origem
  tem de existir.
"""
from __future__ import annotations

import json
import re
from typing import Dict, List, Optional, Tuple

from agents.langnetexecucao import extrair_execucao

ORIGENS = ("tela", "banco", "tarefa", "contexto")
# chaves do formato de tarefa do CrewAI (o que vai no tasks.yaml); o resto vai ao tasks_meta.yaml
CHAVES_CREWAI = ("description", "expected_output", "agent", "context", "tools", "output_file",
                 "async_execution", "human_input", "markdown", "output_json", "output_pydantic")


# ── o que a Especificação manda virar tarefa ────────────────────────────────

def casos_agenticos(spec_doc: str) -> List[Dict]:
    """Casos de uso com passo `agente`: uc, nome, decisão e os passos do agente."""
    out = []
    for u in extrair_execucao(spec_doc or ""):
        ag = [s for s in u["passos"] if s["executado_por"] == "agente"]
        if not ag and u["natureza"] != "agêntica":
            continue
        out.append({"uc": u["uc"], "nome": u["nome"], "natureza": u["natureza"],
                    "passos": [{"passo": f"{s['fluxo']} {s['id']}", "acao": s["acao"] or s["condicao"],
                                "resposta": s["resposta"]} for s in ag]})
    return out


def bloco_para_o_prompt(spec_doc: str) -> str:
    cas = casos_agenticos(spec_doc)
    if not cas:
        return ""
    linhas = ["## 🔴 TAREFAS A CRIAR — EXATAMENTE ESTAS (lidas da coluna \"Executado por\")", "",
              f"A Especificação tem {len(cas)} caso(s) de uso com passo executado por agente. Crie UMA "
              "tarefa para CADA um, e NENHUMA outra: login, cadastro, relatório, auditoria, envio de "
              "e-mail, integração e tratamento de erro são executados por código (pronto ou código "
              "gerado), NUNCA por tarefa de agente. A tarefa cobre todos os passos `agente` do caso "
              "de uso (a decisão e os seus desfechos alternativos).", ""]
    for c in cas:
        linhas.append(f"- **{c['uc']} — {c['nome']}**")
        for p in c["passos"]:
            linhas.append(f"  - [{p['passo']}] {p['acao'][:200]} → {p['resposta'][:200]}")
    linhas += ["", "🔴 AGENTE DE CADA TAREFA: agrupe as tarefas por COMPETÊNCIA de julgamento "
               "(ex.: interpretar e classificar ≠ recomendar conduta e redigir comunicação). Cada "
               "tarefa declara em **Agent** um agente da tabela da Seção 1, e TODO agente da Seção 1 "
               "tem pelo menos uma tarefa — agente sem tarefa não deve existir.",
               "", "🔴 ORIGEM DE CADA ENTRADA: toda tarefa tem a linha `| **Origem das entradas** | ... |` "
               "com UMA origem por campo do Input Schema, no formato `campo: origem; campo: origem`. "
               "Origens válidas: `tela <campo>` (o usuário informa), `banco <tabela>.<coluna>` (o "
               "programa busca antes de chamar o agente — use tabelas e colunas do SCHEMA), "
               "`tarefa <nome_da_tarefa>` (saída de outra tarefa), `contexto` (o caso/atendimento aberto "
               "na tela). Se a tarefa precisa de critérios, regras ou parâmetros vigentes, eles vêm do "
               "`banco` — o agente não os inventa.", ""]
    return "\n".join(linhas)


# ── leitura do documento de Agentes e Tarefas ───────────────────────────────

def _tarefas(ats: str) -> List[Dict]:
    from prompts.generate_single_task_yaml import parse_task_blocks
    out = []
    for t in parse_task_blocks(ats or ""):
        t = dict(t)
        t["name"] = (t.get("name") or "").strip("` ")
        m = re.search(r'\|\s*\**Origem das entradas\**\s*\|\s*(.+?)\s*\|\s*$', t.get("raw", ""), re.M | re.I)
        t["origens"] = _ler_origens(m.group(1)) if m else {}
        t["entradas"] = chaves_de_primeiro_nivel(t.get("input_schema") or "")
        out.append(t)
    return out


def _roster(ats: str) -> Dict[str, str]:
    from prompts.generate_single_task_yaml import _parse_agent_overview
    return _parse_agent_overview(ats or "")


def chaves_de_primeiro_nivel(schema: str) -> List[str]:
    """Campos do primeiro nível de um Input Schema escrito como JSON ou como {a, b, c}."""
    s = (schema or "").replace("\\n", "\n")
    s = re.sub(r'```(?:json)?', '', s)
    i = s.find("{")
    # forma de lista ("- campo: Tipo (comentário)"), a do exemplo do próprio prompt
    lista = re.findall(r'(?m)^\s*[-•*]\s*`?([A-Za-z_]\w*)`?\s*\??\s*:', s)
    if lista and (i < 0 or s.find("-") < i):
        out = []
        for k in lista:
            if k not in out:
                out.append(k)
        return out
    if i < 0:
        return []
    prof, atual, chaves, buf = 0, [], [], ""
    for ch in s[i:]:
        if ch in "{[":
            prof += 1
            if prof == 1:
                continue
        elif ch in "}]":
            prof -= 1
            if prof == 0:
                break
        if prof == 1:
            buf += ch
    for parte in re.split(r',', re.sub(r'\{[^{}]*\}|\[[^\[\]]*\]', '', buf)):
        m = re.match(r'\s*"?([A-Za-z_][\w]*)"?\s*\??\s*(:|$)', parte)
        if m and m.group(1) not in chaves:
            chaves.append(m.group(1))
    return chaves


def _ler_origens(texto: str) -> Dict[str, str]:
    out = {}
    t = (texto or "").replace("\\n", "\n")
    for parte in re.split(r';|<br\s*/?>|\n', t):
        parte = re.sub(r'^\s*[-•*]\s*', '', parte.strip())
        m = re.match(r'\s*`?([A-Za-z_]\w*)`?\s*:\s*(.+)', parte)
        if m:
            out[m.group(1)] = m.group(2).strip().strip("`").strip()
    return out


def _tabelas_do_schema(schema_sql: str) -> Dict[str, List[str]]:
    try:
        from agents.langnetcoherence import schema_columns
        return {k.lower(): [c.lower() for c in v] for k, v in (schema_columns(schema_sql or "") or {}).items()}
    except Exception:
        return {}


# ── conferência (programa, não modelo) ──────────────────────────────────────

def conferir_ats(ats: str, spec_doc: str, schema_sql: str = "") -> Dict:
    cas = casos_agenticos(spec_doc)
    agenticos = {c["uc"] for c in cas}
    tarefas = _tarefas(ats)
    roster = _roster(ats)
    nomes_roster = set(roster.values())
    tabelas = _tabelas_do_schema(schema_sql)
    nomes_tarefas = {t["name"] for t in tarefas}
    problemas: List[str] = []

    por_uc: Dict[str, List[str]] = {}
    for t in tarefas:
        ucs = t.get("uc_related") or []
        for u in ucs:
            por_uc.setdefault(u, []).append(t["name"])
        if ucs and not (set(ucs) & agenticos):
            problemas.append(f"tarefa {t['name']} é de caso de uso convencional ({', '.join(ucs)}) — não deve existir")
        if not ucs:
            problemas.append(f"tarefa {t['name']} sem caso de uso relacionado")
    for c in cas:
        n = len(por_uc.get(c["uc"], []))
        if n == 0:
            problemas.append(f"{c['uc']} ({c['nome']}) é agêntico e não tem tarefa")
        elif n > 1:
            problemas.append(f"{c['uc']} tem {n} tarefas ({', '.join(por_uc[c['uc']])}) — deve ter uma")

    uso = {a: 0 for a in nomes_roster}
    for t in tarefas:
        a = t.get("agent_snake")
        bruto = t.get("agent") or ""
        declarado = bool(re.search(r'AG-\d+', bruto) and re.search(r'AG-\d+', bruto).group(0) in roster) or \
            any(n and n in bruto for n in nomes_roster)
        if not declarado:
            # o leitor aproxima o nome por semelhança; aqui isso é defeito, não conserto
            problemas.append(f"tarefa {t['name']}: agente \"{bruto}\" não é nenhum dos agentes declarados")
        elif a not in nomes_roster:
            problemas.append(f"tarefa {t['name']}: agente \"{t.get('agent')}\" não está na tabela de agentes")
        else:
            uso[a] += 1
    for a, n in uso.items():
        if n == 0 and tarefas:
            problemas.append(f"agente {a} não tem tarefa")

    for t in tarefas:
        if not (set(t.get("uc_related") or []) & agenticos):
            continue
        if (t.get("input_schema") or "").strip() and not t["entradas"]:
            problemas.append(f"tarefa {t['name']}: o Input Schema não pôde ser lido — nenhuma entrada conferida")
        for campo in t["entradas"]:
            o = t["origens"].get(campo)
            if not o:
                problemas.append(f"tarefa {t['name']}: entrada \"{campo}\" sem origem declarada")
                continue
            tipo = o.split()[0].lower() if o.split() else ""
            if tipo not in ORIGENS:
                problemas.append(f"tarefa {t['name']}: origem de \"{campo}\" inválida: {o}")
            elif tipo == "banco" and tabelas:
                ref = (o.split(None, 1) + [""])[1]
                m = re.match(r'([A-Za-z_]\w*)(?:\.([A-Za-z_]\w*))?', ref)
                tab = m.group(1).lower() if m else ""
                col = (m.group(2) or "").lower() if m else ""
                if tab not in tabelas:
                    problemas.append(f"tarefa {t['name']}: \"{campo}\" vem da tabela {tab}, que não existe no modelo de dados")
                elif col and col not in tabelas[tab]:
                    problemas.append(f"tarefa {t['name']}: \"{campo}\" vem de {tab}.{col}, coluna que não existe")
            elif tipo == "tarefa":
                ref = (o.split(None, 1) + [""])[1].strip("` ").split()[0] if len(o.split()) > 1 else ""
                if ref and ref not in nomes_tarefas and not any(ref == t2.get("id") for t2 in tarefas):
                    problemas.append(f"tarefa {t['name']}: \"{campo}\" vem da tarefa {ref}, que não existe")
    return {"tarefas": len(tarefas), "casos_agenticos": len(cas), "problemas": problemas,
            "aprovado": not problemas and bool(cas),
            "por_agente": uso, "por_uc": por_uc}


def remover_tarefas_convencionais(ats: str, spec_doc: str) -> Tuple[str, List[str]]:
    """Tira do documento os blocos de tarefa cujos casos de uso são todos convencionais."""
    agenticos = {c["uc"] for c in casos_agenticos(spec_doc)}
    tirados = []

    def troca(m):
        bloco = m.group(0)
        ucs = set()
        mu = re.search(r'\|\s*\**UC Relacionado\**\s*\|([^|]*)\|', bloco, re.I)
        if mu:
            ucs = set(re.findall(r'UC-\d+', mu.group(1)))
        if ucs and not (ucs & agenticos):
            nm = re.search(r'#{3,4}\s+(T-[\w-]+)', bloco)
            tirados.append(nm.group(1) if nm else "?")
            return ""
        return bloco
    novo = re.sub(r'(?ms)^#{3,4}\s+T-[\w-]+.*?(?=^#{1,4}\s|\Z)', troca, ats or "")
    return novo, tirados


# ── Geração de Código: agente pelo documento, YAML no formato do CrewAI ────

def agente_do_documento(tasks_yaml: str, ats: str, agents_yaml: str) -> Tuple[str, Dict[str, str]]:
    """Põe em cada tarefa do tasks.yaml o agente que o documento de Agentes e Tarefas declara.
    Antes era escolhido pela ferramenta em comum, e as 5 tarefas do BioByte caíram no mesmo agente."""
    import yaml
    try:
        tarefas = yaml.safe_load(tasks_yaml or "") or {}
        agentes = yaml.safe_load(agents_yaml or "") or {}
    except Exception:
        return tasks_yaml, {}
    if not isinstance(tarefas, dict) or not isinstance(agentes, dict):
        return tasks_yaml, {}
    declarado = {t["name"]: t.get("agent_snake") for t in _tarefas(ats)}
    feito = {}
    for nome, cfg in tarefas.items():
        a = declarado.get(nome)
        if isinstance(cfg, dict) and a and a in agentes and cfg.get("agent") != a:
            cfg["agent"] = a
            feito[nome] = a
    if not feito:
        return tasks_yaml, {}
    return yaml.dump(tarefas, sort_keys=False, allow_unicode=True), feito


def separar_yaml_crewai(tasks_yaml: str) -> Tuple[str, str]:
    """tasks.yaml só com as chaves do formato de tarefa do CrewAI; o resto (rastreabilidade,
    esquema de saída, natureza, verificação) vai para tasks_meta.yaml, que o servidor junta."""
    import yaml
    try:
        tarefas = yaml.safe_load(tasks_yaml or "") or {}
    except Exception:
        return tasks_yaml, ""
    if not isinstance(tarefas, dict):
        return tasks_yaml, ""
    canon, meta = {}, {}
    for nome, cfg in tarefas.items():
        if not isinstance(cfg, dict):
            canon[nome] = cfg
            continue
        canon[nome] = {k: v for k, v in cfg.items() if k in CHAVES_CREWAI}
        resto = {k: v for k, v in cfg.items() if k not in CHAVES_CREWAI}
        if resto:
            meta[nome] = resto
    return (yaml.dump(canon, sort_keys=False, allow_unicode=True),
            yaml.dump(meta, sort_keys=False, allow_unicode=True) if meta else "")
