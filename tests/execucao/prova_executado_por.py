"""Coluna "Executado por" — o programa lê, escreve e confere; o modelo só diz o executor.

Padrão de interação com agentes v1.0 (03/10/2026): cada passo dos fluxos principal, alternativos
e de exceção declara quem produz a resposta do sistema — pronto · código gerado · agente.
Fixture: UC-001 (convencional) e UC-011 (agêntico) da especificação v2 do BioByte v5.
"""
import sys, os, json
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
import warnings; warnings.filterwarnings("ignore")
from agents.langnetexecucao import (extrair_execucao, conferir_execucao, anotar_uc, blocos,
                                    extrair_mensagens, normalizar_executor)

falhas = []; casos = 0
def confere(nome, cond):
    global casos; casos += 1
    print(("OK   " if cond else "FALHA"), nome)
    if not cond: falhas.append(nome)

doc = open(os.path.join(os.path.dirname(__file__), "fixture_ucs_executado_por.md")).read()
ucs = {u["uc"]: u for u in extrair_execucao(doc)}
confere("lê os dois casos de uso com a natureza", ucs["UC-001"]["natureza"] == "convencional" and ucs["UC-011"]["natureza"] == "agêntica")
confere("lê os três fluxos do UC-011", {s["fluxo"] for s in ucs["UC-011"]["passos"]} == {"principal", "alternativo", "excecao"})
confere("documento antigo, sem a coluna, é reprovado", not conferir_execucao(doc)["aprovado"])

# mensagens de exceção são mensagens, não nomes de campo
e1 = [s for s in ucs["UC-011"]["passos"] if s["id"] == "E1"][0]
confere("mensagem de exceção reconhecida como mensagem", e1["mensagens"] == ["Não foi possível avaliar multirresistência: classe ausente em um ou mais antimicrobianos."])
confere("nome de campo citado NÃO é mensagem", "Multirresistência" not in e1["mensagens"])
confere("toda exceção do UC-011 tem a sua mensagem", all(s["mensagens"] for s in ucs["UC-011"]["passos"] if s["fluxo"] == "excecao"))

confere("normaliza 'Código-Gerado'", normalizar_executor("`Código-Gerado`") == "código gerado")
confere("recusa valor fora da lista", normalizar_executor("IA") is None)

def modelo(valores):
    def responder(pedido, observacao):
        return json.dumps(valores)
    return responder

def chaves(uc, padrao, **troca):
    v = {f"{s['fluxo']} {s['id']}": padrao for s in ucs[uc]["passos"]}
    v.update(troca); return v

# anotação correta
r = anotar_uc(doc, "UC-011", modelo(chaves("UC-011", "código gerado", **{"principal 4": "agente"})))
confere("anotação aceita no agêntico com um passo agente", r["mudou"] and not r["problemas"])
b0 = [b for b in blocos(doc) if b["uc"] == "UC-011"][0]; b1 = [b for b in blocos(r["doc"]) if b["uc"] == "UC-011"][0]
confere("nada fora do caso de uso muda", r["doc"][:b1["inicio_corpo"]] == doc[:b0["inicio_corpo"]] and r["doc"][b1["fim_corpo"]:] == doc[b0["fim_corpo"]:])
antes = [(s["acao"], s["resposta"]) for s in ucs["UC-011"]["passos"]]
depois = [(s["acao"], s["resposta"]) for s in extrair_execucao(r["doc"])[1]["passos"]]
confere("nenhuma célula dos fluxos muda", antes == depois)
confere("a coluna é lida de volta", extrair_execucao(r["doc"])[1]["passos"][3]["executado_por"] == "agente")
r2 = anotar_uc(r["doc"], "UC-011", modelo(chaves("UC-011", "pronto", **{"principal 2": "agente"})))
confere("reanotar atualiza a coluna sem duplicar", r2["doc"].count("Executado por") == r["doc"].count("Executado por") and not r2["problemas"])

# recusas do programa
confere("convencional com agente é recusado", "convencional" in " ".join(anotar_uc(doc, "UC-001", modelo(chaves("UC-001", "agente")))["problemas"]))
confere("agêntico sem agente é recusado", "sem nenhum passo" in " ".join(anotar_uc(doc, "UC-011", modelo(chaves("UC-011", "pronto")))["problemas"]))
falta = chaves("UC-001", "pronto"); falta.pop("principal 1")
confere("passo faltando é recusado", any("faltou" in p for p in anotar_uc(doc, "UC-001", modelo(falta))["problemas"]))
confere("resposta sem JSON é recusada e nada muda", anotar_uc(doc, "UC-001", lambda p, o: "não sei")["mudou"] is False)

# segunda tentativa leva o motivo da recusa
vistos = []
def aprende(pedido, observacao):
    vistos.append(observacao)
    return json.dumps(chaves("UC-001", "agente") if not observacao else chaves("UC-001", "pronto"))
r3 = anotar_uc(doc, "UC-001", aprende)
confere("a 2ª tentativa recebe o motivo e passa", r3["mudou"] and "convencional" in vistos[1])

# o documento inteiro anotado é aprovado
d = anotar_uc(r["doc"], "UC-001", modelo(chaves("UC-001", "pronto")))["doc"]
c = conferir_execucao(d)
confere("documento anotado é aprovado pela conferência", c["aprovado"] and c["por_valor"]["agente"] == 1)

# o prompt de geração pede a coluna nas três tabelas
from app.templates import specification_prompt as P
fonte = open(P.__file__).read()
confere("prompt pede a coluna nas três tabelas", fonte.count("| Executado por |") == 3 and "EXECUTADO POR" in fonte)

print(f"\n{casos} casos, {len(falhas)} falhas")
sys.exit(1 if falhas else 0)
