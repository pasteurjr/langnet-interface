"""Portões dos elos (F5): reprovam um caso montado com CADA defeito da revisão de 03/10/2026 e
aprovam o caso corrigido. Tudo determinístico — o 'modelo' aqui é uma resposta fixa."""
import sys, os, json, copy, re
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
import warnings; warnings.filterwarnings("ignore")
import yaml
from agents.langnetexecucao import anotar_uc, extrair_execucao, blocos
from agents.langnetfichatela import aplicar_ficha
from agents.langnetapptelas import emitir_aplicativo
from agents.langnetportoes import conferir_elos

falhas = []; casos = 0
def confere(nome, cond):
    global casos; casos += 1
    print(("OK   " if cond else "FALHA"), nome)
    if not cond: falhas.append(nome)

aqui = os.path.dirname(__file__)
schema = open(os.path.join(aqui, "fixture_schema_biobyte_v5.sql")).read()
spec0 = open(os.path.join(aqui, "fixture_ucs_executado_por.md")).read()
spec = spec0
for uc, agente in (("UC-001", None), ("UC-011", "principal 4")):
    u = [x for x in extrair_execucao(spec) if x["uc"] == uc][0]
    v = {f"{s['fluxo']} {s['id']}": ("pronto" if uc == "UC-001" else "código gerado") for s in u["passos"]}
    if agente: v[agente] = "agente"
    spec = anotar_uc(spec, uc, lambda p, o, v=v: json.dumps(v))["doc"]
raw = {b["uc"]: b["corpo"] for b in blocos(spec)}

def tela(sid, uc, acoes, agentes=()):
    botoes = "".join(f'<button data-acao="{a["id"]}">{a["label"]}</button>' for a in acoes)
    blocos_ag = "".join(f'<div data-agente="{p}"><span data-campo="multirresistente">Sim</span></div>' for p in agentes)
    s = {"id": sid, "name": sid, "uc": [uc], "components": [], "actions": acoes,
         "agentes": [{"passo": p, "forma": "decisao"} for p in agentes],
         "mockup_html": f'<html><body><main>{botoes}{blocos_ag}</main></body></html>'}
    aplicar_ficha(s, raw[uc], uc)
    msgs = "".join(f'<div data-mensagem="{m["passo"]}">{m["texto"]}</div>' for m in s["mensagens"])
    s["mockup_html"] = s["mockup_html"].replace("</main>", msgs + "</main>")
    return s
ui = {"screens": [tela("login", "UC-001", [{"id": "acao-1", "label": "Entrar", "passo": "principal 4"}]),
                  tela("multi", "UC-011", [{"id": "acao-1", "label": "Avaliar", "passo": "principal 4"}], ["principal 4"])]}
ats = """## 1. VISÃO GERAL DOS AGENTES
| ID | Nome | Módulo |
|---|---|---|
| AG-01 | clinical_classifier_agent | Clínico |

### T-AGN-001: Avaliar multirresistência
| Atributo | Especificação |
|---|---|
| **Nome** | `evaluate_multidrug_resistance` |
| **Agent** | AG-01 (Clinical Classifier Agent) |
| **Input Schema** | {"caso_id": "UUID", "antibiograma": []} |
| **Origem das entradas** | caso_id: contexto; antibiograma: banco antibiogramas |
| **UC Relacionado** | UC-011 |

## 4. MATRIZ
"""
ty = yaml.dump({"evaluate_multidrug_resistance": {"description": "d {caso_id}", "expected_output": "e", "agent": "clinical_classifier_agent"}})

def modelo(pedido):
    ids = re.findall(r"^- (acao-\d+):", pedido, re.M)
    tarefa = "lnx.agente('evaluate_multidrug_resistance', {}, null);" if "evaluate_multidrug_resistance" in pedido else ""
    js = "export default function montar(raiz, lnx) {\n" + "".join(f"  lnx.acao(raiz, '{i}', async () => {{ {tarefa} }});\n" for i in ids) + "}\n"
    return json.dumps({"controlador_js": js, "regras_py": ""})
arqs, rel = emitir_aplicativo(ui, spec, ats, schema, "Teste", chamar=modelo, paralelo=1)
import agents.langnetagents as M
arqs.append({"path": "ws-server/websocket_server.py", "content": M._template_websocket_server_py(5099)})
arqs.append({"path": "frontend/src/screens/wsClient.js", "content": M._template_ws_client(5099)})

r = conferir_elos(spec, ui, ats, ty, schema, arqs)
for p in r["portoes"]:
    if p["problemas"]: print("   ", p["nome"], p["problemas"][:3])
confere("caso corrigido: os 6 portões aprovam", r["aprovado"] and len(r["portoes"]) == 6)

def reprova(nome, portao, **troca):
    args = dict(spec_doc=spec, ui_spec=ui, ats_doc=ats, tasks_yaml=ty, schema_sql=schema, arquivos=arqs)
    args.update(troca)
    rr = conferir_elos(**args)
    alvo = [p for p in rr["portoes"] if p["nome"].startswith(portao)]
    confere(nome, alvo and not alvo[0]["aprovado"])

reprova("especificação sem a coluna Executado por", "Especificação: quem", spec_doc=spec0)
u2 = copy.deepcopy(ui); u2["screens"][1]["actions"][0]["target"] = "identificar_multirresistencia_antibiograma"
reprova("ação com nome de tarefa inventado (103 no v5)", "Especificação → Interface", ui_spec=u2)
u3 = copy.deepcopy(ui); u3["screens"][1]["actions"][0]["executado_por"] = None
reprova("ação sem executor", "Especificação → Interface", ui_spec=u3)
u4 = copy.deepcopy(ui); u4["screens"][0]["mockup_html"] = u4["screens"][0]["mockup_html"].replace("<main>", "<main><table><tr><th>SENHA HASH</th></tr></table>")
reprova("coluna SENHA HASH na tela", "Especificação → Interface", ui_spec=u4)
u5 = copy.deepcopy(ui); u5["screens"][1]["agentes"] = []
reprova("caso agêntico sem bloco de agente", "Especificação → Interface", ui_spec=u5)
u6 = copy.deepcopy(ui); u6["screens"] = u6["screens"][1:]
reprova("caso de uso sem tela", "Especificação → Interface", ui_spec=u6)
reprova("tarefa para caso convencional (25 no v5)", "Especificação → Agentes", ats_doc=ats.replace("| UC-011 |", "| UC-001 |"))
reprova("agente inventado", "Especificação → Agentes", ats_doc=ats.replace("AG-01 (Clinical Classifier Agent)", "agente_multirresistencia"))
reprova("entrada sem origem (critérios NHSN)", "Especificação → Agentes", ats_doc=ats.replace("; antibiograma: banco antibiogramas", ""))
reprova("tasks.yaml com chaves fora do CrewAI (traceability)", "Agentes & Tarefas → tasks.yaml",
        tasks_yaml=yaml.dump({"evaluate_multidrug_resistance": {"description": "d", "expected_output": "e", "traceability": {"uc": ["UC-011"]}}}))
reprova("tarefa do documento ausente do tasks.yaml", "Agentes & Tarefas → tasks.yaml", tasks_yaml=yaml.dump({"outra": {"description": "d", "expected_output": "e"}}))
a2 = [dict(a) for a in arqs]
for a in a2:
    if a["path"].endswith("screens/Multi.jsx"): a["content"] = a["content"].replace("Avaliar", "Outro desenho")
reprova("tela do aplicativo diferente do desenho aprovado", "Interface → Código", arquivos=a2)
a3 = [dict(a) for a in arqs]
for a in a3:
    if a["path"].endswith("controladores/Multi.js"): a["content"] = "export default function montar(raiz, lnx) {}"
reprova("ação não ligada no aplicativo (20 telas 'Ação não vinculada' no v5)", "Interface → Código", arquivos=a3)
reprova("console Admin/Petri no aplicativo", "Interface → Código", arquivos=arqs + [{"path": "frontend/src/petri-engine/PlaceProcessor.js", "content": ""}])
a4 = [dict(a) for a in arqs]
for a in a4:
    if a["path"].endswith("screens/Multi.jsx"): a["content"] = re.sub(r"Não foi possível avaliar[^\"<]*", "", a["content"])
reprova("mensagem de exceção do caso de uso ausente da tela", "Interface → Código", arquivos=a4)
a5 = [dict(a) for a in arqs]
for a in a5:
    if a["path"] == "ws-server/websocket_server.py": a["content"] = "async def _concluir_tarefa(): pass"
reprova("erro de tarefa respondido como sucesso (falha calada do v5)", "Erro nunca", arquivos=a5)

print(f"\n{casos} casos, {len(falhas)} falhas")
sys.exit(1 if falhas else 0)
