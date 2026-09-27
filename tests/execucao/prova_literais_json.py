"""O tradutor de valores não transforma literal do JSON em variável do Python.

`false`, `true` e `null` são nomes VÁLIDOS em Python, então passavam pela checagem de
sintaxe e saíam como `_num(false)` — que estoura em execução com "name 'false' is not
defined" e derruba a tarefa. Medido no BioByte v5: a recomendação de pacote falhava e
travava a rede. A conta de verdade tem de continuar sendo conta.
"""
import sys, os, re
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
import agents.langnetagents as M

# _texpr vive dentro do emissor; a prova usa o emissor inteiro sobre linhas de valor
fonte = open(raiz + "/backend/agents/langnetagents.py", encoding="utf-8").read()
ini = fonte.index("    def _texpr(e):")
fim = fonte.index("\n    i = 0; n = len(raw)", ini)
corpo = "import re as _re\n" + "\n".join(l[4:] for l in fonte[ini:fim].splitlines())
ns = {}
exec(compile(corpo, "_texpr", "exec"), ns)
f = ns["_texpr"]

CASOS = [
    # (entrada, o que NÃO pode sair, o que tem de sair)
    ("false", None, "False"),
    ("true", None, "True"),
    ("false ou quando o antibiograma estiver pendente/com erro", "_num(", None),
    ("null (a ser preenchido por T-MDR-002)", None, "None"),
    ("area_construida / area_terreno", None, "_safe_div(area_construida, area_terreno)"),
    ("total * 0.5", None, "_num(total) * 0.5"),
    ("contagem_classes >= 3", "false", None),
]
falhas = []
for entrada, proibido, esperado in CASOS:
    saida = f(entrada)
    if proibido and proibido in saida:
        falhas.append(f"'{entrada[:40]}' -> saiu {saida[:60]} (nao podia conter {proibido})")
    if esperado and saida != esperado:
        falhas.append(f"'{entrada[:40]}' -> saiu {saida[:60]}, esperado {esperado}")
    # e o que sai tem de compilar
    try:
        compile(saida, "<saida>", "eval")
    except SyntaxError:
        falhas.append(f"'{entrada[:40]}' -> saida nao compila: {saida[:60]}")

print(f"casos: {len(CASOS)} | passaram: {len(CASOS) - len(falhas)} | falharam: {len(falhas)}")
for m in falhas: print("  X", m)
sys.exit(1 if falhas else 0)
