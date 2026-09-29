"""A ferramenta com regra declarada na etapa Ferramentas é a que o agente recebe.

Medido no BioByte v5 em 29/09/2026: o modelo escreveu `TOOL_REGISTRY: Dict[str, BaseTool] = {`
(com anotação de tipo); o gerador procurava `TOOL_REGISTRY =`, não achava, e emitia a classe
JsonParserTool no FIM do arquivo — depois do laço que completa o registro. A ferramenta nunca
entrava no registro, e o agente recebia o substituto "Ferramenta 'json_parser_tool' não está
configurada". Esta prova executa o tools.py resultante.
"""
import sys, os, types
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
import warnings; warnings.filterwarnings("ignore")
import agents.langnetagents as M

falhas = []
def confere(nome, cond):
    print(("OK   " if cond else "FALHA"), nome)
    if not cond: falhas.append(nome)

tools_modelo = '''from typing import Dict
from crewai.tools import BaseTool

class DatabaseTool(BaseTool):
    name: str = "database_tool"
    description: str = "consulta"
    def _run(self, query=None):
        return "ok"

TOOL_REGISTRY: Dict[str, BaseTool] = {
    "database_tool": DatabaseTool(),
}
'''
doc = {"tools": [{"nome": "json_parser_tool", "origem": "deterministica", "descricao": "interpreta JSON",
                  "entrada": ["texto_json"], "saida": ["objeto"], "regra": "Verifique se o texto é JSON válido."}]}
# mesma ordem do gerador: completa o registro → emite as declaradas → tira citação órfã
saida = M._garantir_registro_de_ferramentas(tools_modelo, ["json_parser_tool"])
saida = M._emit_declared_tools(saida, doc)
saida = M._drop_undefined_registry_entries(saida)
confere("a classe vem antes do registro anotado", saida.index("class JsonParserTool") < saida.index("TOOL_REGISTRY: Dict"))
# executa, com o módulo de regras simulado
sys.modules["tools_rules"] = types.SimpleNamespace(json_parser_tool=lambda texto_json=None: {"objeto": {"a": 1}, "valido": True})
ns = {}
exec(saida, ns)
reg = ns["TOOL_REGISTRY"]
confere("json_parser_tool está no registro", "json_parser_tool" in reg)
confere("é a classe com a regra, não um substituto", type(reg.get("json_parser_tool")).__name__ == "JsonParserTool")
confere("a regra roda", reg["json_parser_tool"]._run(texto_json='{"a":1}')["valido"] is True)
confere("o que o modelo já tinha registrado continua", "database_tool" in reg)
print("\n%d falha(s)" % len(falhas)); sys.exit(1 if falhas else 0)
