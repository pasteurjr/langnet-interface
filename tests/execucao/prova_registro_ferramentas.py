"""Toda ferramenta declarada na etapa Ferramentas entra no registro.

O tools.py é escrito pelo modelo: numa rodada ele monta o registro e na seguinte
esquece. Sem registro, o servidor monta o agente SEM ferramenta e toda tarefa devolve
"não executado — falha de ferramenta". Medido no BioByte v5 em 28/09/2026: a MESMA
entrada gerou um pacote que passou em 6 de 9 casos da bateria e outro que passou em 2,
e a única diferença era o registro ausente.
"""
import sys, os, re
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
from agents.langnetagents import _garantir_registro_de_ferramentas as garantir

DECLARADAS = ["database_tool", "json_parser_tool", "vector_search_tool"]

SEM_REGISTRO = '''from database_tool import DatabaseTool, database_tool
from typing import Dict
TOOL_REGISTRY: Dict[str, object] = {}
try:
    from tools_std import _STD_TOOLS
    TOOL_REGISTRY.update(_STD_TOOLS)
except Exception:
    pass
'''
COM_REGISTRO = '''from database_tool import DatabaseTool, database_tool
from typing import Dict
TOOL_REGISTRY: Dict[str, object] = {
    'database_tool': database_tool,
    'json_parser_tool': None,
    'vector_search_tool': None,
}
'''

falhas = []

saida = garantir(SEM_REGISTRO, DECLARADAS)
if "Registro completado pelo LangNet" not in saida:
    falhas.append("não completou o registro quando faltava")
for n in DECLARADAS:
    if n not in saida:
        falhas.append(f"{n} ficou de fora do registro completado")
try:
    compile(saida, "tools.py", "exec")
except SyntaxError as e:
    falhas.append(f"o tools.py completado não compila: {e}")

# O CrewAI exige um OBJETO de ferramenta. Registrar a função crua derruba o agente com
# "Input should be a valid dictionary or instance of BaseTool" — foi o que aconteceu com
# json_parser_tool em 28/09/2026. O registro tem de RECUSAR função solta.
CENARIO = """
class _Falsa:
    name = "json_parser_tool"
    def _run(self, *a, **k):
        return {}

def json_parser_tool(texto):      # funcao solta: NAO serve
    return {}

TOOL_REGISTRY = {}
_instancia_certa = _Falsa()
""" + saida.split("# \u2500\u2500\u2500 Registro completado pelo LangNet \u2500\u2500\u2500")[-1]
ns = {}
try:
    exec(compile(CENARIO, "tools.py", "exec"), ns)
    reg = ns.get("TOOL_REGISTRY", {})
    escolhido = reg.get("json_parser_tool")
    if escolhido is not None and not (hasattr(escolhido, "_run") and hasattr(escolhido, "name")):
        falhas.append("registrou uma função solta em vez de um objeto de ferramenta")
except Exception as e:
    falhas.append(f"o registro completado estourou: {e}")

# quando o modelo ACERTOU, nada é mexido
saida2 = garantir(COM_REGISTRO, DECLARADAS)
if saida2 != COM_REGISTRO:
    falhas.append("mexeu num tools.py que já estava certo")

# o modelo às vezes nem CRIA o registro: o conserto tem de criá-lo, não estourar
SEM_NADA = "from database_tool import DatabaseTool, database_tool\n"
saida3 = garantir(SEM_NADA, DECLARADAS)
ns3 = {"DatabaseTool": object, "database_tool": None}
try:
    exec(compile(saida3.replace("from database_tool import DatabaseTool, database_tool", ""),
                 "tools.py", "exec"), ns3)
    if "TOOL_REGISTRY" not in ns3:
        falhas.append("não criou o registro quando o modelo nem o definiu")
except NameError as e:
    falhas.append(f"estourou quando o registro não existia: {e}")
except Exception:
    pass

# sem ferramentas declaradas, não inventa registro
if garantir(SEM_REGISTRO, []) != SEM_REGISTRO:
    falhas.append("acrescentou registro sem nada declarado")

print(f"casos: {5 + len(DECLARADAS)} | falharam: {len(falhas)}")
for m in falhas: print("  X", m)
sys.exit(1 if falhas else 0)
