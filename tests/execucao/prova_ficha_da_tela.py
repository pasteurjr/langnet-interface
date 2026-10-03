"""Ficha da tela — ação aponta para caso de uso + passo, executor vem da Especificação.

Defeitos medidos no BioByte v5 (03/10/2026) que esta prova trava:
- 103 ações apontavam para nomes de tarefa inventados;
- mensagens de exceção viravam campo de exibição;
- a tela de Usuários mostrava a coluna SENHA HASH;
- o protótipo não dizia quem executa cada botão (o provedor fictício respondia "sucesso" a tudo).
"""
import sys, os, json, re, copy
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
import warnings; warnings.filterwarnings("ignore")
from agents.langnetexecucao import anotar_uc, extrair_execucao, blocos
from agents.langnetfichatela import (aplicar_ficha, conferir_tela, injetar_prototipo, agentes_do_sistema,
                                     remover_colunas_sensiveis, passos_para_prompt)
from agents.langnetui import diferencas_de_tela

falhas = []; casos = 0
def confere(nome, cond):
    global casos; casos += 1
    print(("OK   " if cond else "FALHA"), nome)
    if not cond: falhas.append(nome)

doc = open(os.path.join(os.path.dirname(__file__), "fixture_ucs_executado_por.md")).read()
uc11 = [u for u in extrair_execucao(doc) if u["uc"] == "UC-011"][0]
val = {f"{s['fluxo']} {s['id']}": "código gerado" for s in uc11["passos"]}; val["principal 4"] = "agente"
doc = anotar_uc(doc, "UC-011", lambda p, o: json.dumps(val))["doc"]
raw = [b for b in blocos(doc) if b["uc"] == "UC-011"][0]["corpo"]

confere("a lista de passos para o modelo traz o executor", "[principal 4] (agente)" in passos_para_prompt(raw))

tela = {
  "id": "multirresistencia", "name": "Multirresistência", "uc": [],
  "components": [
    {"type": "readonly", "field": "msg_classe", "label": "Não foi possível avaliar multirresistência: classe ausente em um ou mais antimicrobianos."},
    {"type": "readonly", "field": "multirresistente", "label": "Multirresistente", "bindTo": "decisoes.multirresistente"},
    {"type": "readonly", "field": "senha_hash", "label": "Senha hash", "bindTo": "usuarios.senha_hash"},
    {"type": "table", "field": "usuarios", "props": {"columns": ["nome", "senha_hash"]}},
  ],
  "actions": [
    {"id": "acao-1", "label": "Identificar multirresistência", "passo": "principal 4"},
    {"id": "acao-2", "label": "Ver antibiograma completo", "passo": "alternativo A3"},
    {"id": "acao-3", "label": "Exportar", "kind": "task", "target": "exportar_relatorio_inventado"},
    {"id": "acao-4", "label": "Voltar", "navegar_para": "casos"},
  ],
  "agentes": [{"passo": "principal 4", "forma": "decisao", "rotulo": "Decide multirresistência"}],
  "mockup_html": ('<html><body><main><table><tr><th>Nome</th><th>SENHA HASH</th></tr>'
                  '<tr><td>Ana</td><td>$2b$12$xyz</td></tr></table>'
                  '<div data-agente="principal 4">cartão</div>'
                  '<button data-acao="acao-1">Identificar</button><button data-acao="acao-2">Ver</button>'
                  '<button data-acao="acao-4">Voltar</button><button>Sem marca</button></main></body></html>'),
}
t = copy.deepcopy(tela)
rel = aplicar_ficha(t, raw, "UC-011")
A = {a["id"]: a for a in t["actions"]}
confere("executor copiado da Especificação (agente)", A["acao-1"]["executado_por"] == "agente" and A["acao-1"]["uc"] == "UC-011")
confere("executor copiado da Especificação (código gerado)", A["acao-2"]["executado_por"] == "código gerado")
confere("nome de tarefa inventado some e a ação fica sem executor", "target" not in A["acao-3"] and A["acao-3"]["executado_por"] is None)
confere("navegação é navegação", A["acao-4"]["executado_por"] == "navegação")
confere("o relatório nomeia a ação sem executor", rel["sem_executor"] == ["Exportar"])
confere("bloco de agente na posição do passo", [b["passo"] for b in t["agentes"]] == ["principal 4"] and t["agentes"][0]["forma"] == "decisao")
confere("mensagem de exceção deixa de ser campo", not any("classe ausente" in (c.get("label") or "") for c in t["components"]))
confere("…e entra como mensagem, com o passo", any(m["passo"] == "excecao E1" and "classe ausente" in m["texto"] for m in t["mensagens"]))
confere("campo sensível sai da tela", not any("senha" in (c.get("field") or "") for c in t["components"]))
confere("coluna sensível sai da tabela declarada", [c for c in t["components"] if c["type"] == "table"][0]["props"]["columns"] == ["nome"])
confere("coluna SENHA HASH sai do desenho", "SENHA HASH" not in t["mockup_html"] and "$2b$" not in t["mockup_html"] and "Ana" in t["mockup_html"])

probs = conferir_tela(t)
confere("conferência acusa a ação sem executor", any("Exportar" in p and "sem executor" in p for p in probs))
confere("conferência acusa botão sem marca no desenho", any("Exportar" in p and "data-acao" in p for p in probs))

t2 = copy.deepcopy(tela); t2["agentes"] = []
r2 = aplicar_ficha(t2, raw, "UC-011")
confere("passo agente sem bloco é criado e relatado", r2["agentes_sem_bloco"] == ["principal 4"] and len(t2["agentes"]) == 1)

# campo de verdade nunca sai por parecer mensagem (Nome/E-mail da tela de Usuários, 03/10)
t4 = copy.deepcopy(tela)
t4["components"] += [{"type": "text", "field": "classe", "label": "Classe"},
                     {"type": "readonly", "field": "avaliar", "label": "avaliar multirresistência"}]
aplicar_ficha(t4, raw, "UC-011")
confere("rótulo curto que aparece dentro de mensagem continua campo", {"classe", "avaliar"} <= {c.get("field") for c in t4["components"]})
val2 = dict(val); val2["alternativo A1"] = "agente"
doc2 = anotar_uc(open(os.path.join(os.path.dirname(__file__), "fixture_ucs_executado_por.md")).read(), "UC-011", lambda p, o: json.dumps(val2))["doc"]
raw2 = [b for b in blocos(doc2) if b["uc"] == "UC-011"][0]["corpo"]
t5 = copy.deepcopy(tela); aplicar_ficha(t5, raw2, "UC-011")
confere("passo agente do fluxo alternativo é variante, não segundo bloco", [b["passo"] for b in t5["agentes"]] == ["principal 4"] and t5["agentes"][0].get("variantes") == ["alternativo A1"])

ruim = {"id": "x", "mockup_html": "<table><tr><th>Nome</th></tr><tr><td>Exemplo A</td></tr></table>", "actions": [], "components": []}
confere("desenho genérico é reprovado", any("Exemplo A" in p for p in conferir_tela(ruim)))

# protótipo executável
html = injetar_prototipo(t["mockup_html"], t, agentes_do_sistema([t]))
m = re.search(r'<script type="application/json" id="ficha-da-tela">(.*?)</script>', html, re.S)
ficha = json.loads(m.group(1)) if m else {}
confere("a ficha vai para o protótipo", {a["id"]: a["executado_por"] for a in ficha.get("actions", [])} == {"acao-1": "agente", "acao-2": "código gerado", "acao-3": None, "acao-4": "navegação"})
confere("o script do protótipo vai junto, antes do </body>", "sem executor" in html and html.rstrip().endswith("</html>"))
confere("o assistente conhece os agentes do sistema", "Decide multirresistência" in html)

# a conversa de refino diz o que mudou — e diz quando nada mudou
d0 = diferencas_de_tela(t, copy.deepcopy(t))
t3 = copy.deepcopy(t); t3["actions"].append({"id": "acao-9", "label": "Refazer", "executado_por": "agente", "passo": "principal 4"})
confere("nada mudou → lista vazia", d0 == [])
confere("botão novo aparece nas mudanças", any("botão novo: Refazer" in x for x in diferencas_de_tela(t, t3)))

print(f"\n{casos} casos, {len(falhas)} falhas")
sys.exit(1 if falhas else 0)
