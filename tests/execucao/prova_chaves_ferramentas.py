"""As chaves dos mapas de ferramentas saem sem a crase do markdown.

O nome da tarefa vem do documento de Agentes e Tarefas escrito em markdown, onde
aparece como `nome_da_tarefa`. A crase viajava para dentro da chave e o servidor de
agentes, que procura pelo nome puro, nunca achava as ferramentas — o agente era
montado SEM ferramenta e respondia que não conseguiu obter o dado.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backend")
from agents.langnetagents import _inject_task_tools_into_adapters as f

saida = f("# adapters\n",
          {"`clinical_classifier_agent`": ["database_tool"], "outro_agente": ["json_parser_tool"]},
          {"`evaluate_multidrug_resistance`": ["database_tool"], "tarefa_limpa": ["json_parser_tool"]})

falhas = []
if "'`" in saida or "`'" in saida:
    falhas.append("sobrou crase numa chave")
for esperado in ["'clinical_classifier_agent'", "'outro_agente'",
                 "'evaluate_multidrug_resistance'", "'tarefa_limpa'"]:
    if esperado not in saida:
        falhas.append(f"faltou a chave {esperado}")

# e o mapa tem de continuar importável
ns = {}
exec(compile(saida, "adapters.py", "exec"), ns)
if ns["TASK_TOOLS"].get("evaluate_multidrug_resistance") != ["database_tool"]:
    falhas.append("a busca pelo nome puro da tarefa nao devolveu as ferramentas")
if ns["AGENT_TOOLS"].get("clinical_classifier_agent") != ["database_tool"]:
    falhas.append("a busca pelo nome puro do agente nao devolveu as ferramentas")

print(f"casos: 6 | passaram: {6 - len(falhas)} | falharam: {len(falhas)}")
for m in falhas: print("  X", m)
sys.exit(1 if falhas else 0)
