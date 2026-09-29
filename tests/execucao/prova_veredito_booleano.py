"""O veredito verdadeiro/falso do agente não pode ser apagado pelo contrato de saída.

Medido no BioByte v5 em 29/09/2026: a tarefa de multirresistência contava 4 classes e
respondia `multirresistente: true`, mas o programa gerado "coagia" a resposta contra o
esquema — que declarava o campo como INTEIRO (a coluna é TINYINT) — e `int(float("True"))`
falha e vira None. O veredito certo era apagado, a recomendação e o alerta recusavam, e o
único teste reprovado da bateria era exatamente esse.

Três coisas precisam valer:
  1. campo que o documento declara "booleano" sai no esquema como boolean, mesmo que a
     coluna do banco seja TINYINT;
  2. a conversão para inteiro aceita verdadeiro/falso (True → 1);
  3. valor que não se consegue converter NÃO some: fica como veio (falha não passa calada).
"""
import sys, os
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
import agents.langnetagents as M

falhas = []
def confere(nome, cond):
    print(("OK   " if cond else "FALHA"), nome)
    if not cond:
        falhas.append(nome)

# 1. o esquema
cfg = {"expected_output": "Retornar um texto em formato JSON contendo as seguintes keys: "
       "- multirresistente: booleano indicando se o germe é multirresistente "
       "- contagem_classes_resistentes: número inteiro de classes resistentes "
       "- justificativa: texto explicando a decisão"}
modelo = {"resultados_hemocultura": {"cols": [("multirresistente", "TINYINT"), ("id", "CHAR")],
                                     "ddl": "CREATE TABLE `resultados_hemocultura` (`multirresistente` TINYINT(1))"}}
sch = M._derive_output_schema("evaluate_multidrug_resistance", cfg, modelo)
confere("esquema: multirresistente é boolean", sch["properties"]["multirresistente"]["type"] == "boolean")
confere("esquema: contagem continua numérica", sch["properties"]["contagem_classes_resistentes"]["type"] in ("integer", "number"))

# 2 e 3. o código emitido no adapters.py
ns = {}
exec(M._ADAPTERS_COERCAO_SRC if hasattr(M, "_ADAPTERS_COERCAO_SRC") else "", ns)
fonte = open(raiz + "/backend/agents/langnetagents.py", encoding="utf-8").read()
def extrai(fn):
    i = fonte.index('    "def %s(' % fn)
    linhas = []
    for l in fonte[i:].split("\n"):
        if not l.strip().startswith('"'):
            break
        linhas.append(eval(l.strip()))
    return "".join(linhas)
exec(extrai("_cv") + "\n" + extrai("_coerce_to_schema"), ns)
cv, co = ns["_cv"], ns["_coerce_to_schema"]

confere("_cv(True, TINYINT) = 1", cv(True, "TINYINT") == 1)
confere("_cv('false', INT) = 0", cv("false", "INT") == 0)
confere("_cv('sim', TINYINT) = 1", cv("sim", "TINYINT") == 1)
confere("_cv('70%', INT) continua 70", cv("70%", "INT") == 70)

obj, _ = co({"multirresistente": True, "contagem_classes_resistentes": 4}, sch)
confere("coerção mantém multirresistente = True", obj["multirresistente"] is True)
obj, _ = co('{"multirresistente": "true", "contagem_classes_resistentes": "4"}', sch)
confere("coerção de 'true' vira True", obj["multirresistente"] is True)
confere("coerção de '4' vira 4", obj["contagem_classes_resistentes"] == 4)
obj, _ = co({"contagem_classes_resistentes": "quatro ou cinco"}, sch)
confere("valor não conversível não some", obj["contagem_classes_resistentes"] == "quatro ou cinco")

print("\n%d falha(s)" % len(falhas))
sys.exit(1 if falhas else 0)
