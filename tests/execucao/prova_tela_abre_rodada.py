"""A tela abre a rodada antes de pedir a tarefa ao servidor de agentes.

O servidor só aceita `execute_task` depois de `iniciar_execucao`. Sem isso, toda tela de
agente respondia "Execução não foi iniciada. Chame 'iniciar_execucao' primeiro." — um erro
técnico, sem saída para o operador. Medido no BioByte v5 em 28/09/2026: nenhuma das cinco
tarefas de IA rodava pela interface do hospital, embora rodassem pela Bancada.
"""
import sys, os, re
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
from agents.langnetagents import _template_ws_client as molde

js = molde(5002)
falhas = []
# só os ENVIOS de verdade contam — comentário citando o nome não é envio
envios = [l for l in js.splitlines() if "ws.send" in l and "//" not in l.split("ws.send")[0]]
ordem = [("iniciar_execucao" in l, "execute_task" in l) for l in envios]
if not any(a for a, _ in ordem):
    falhas.append("a tela nao abre a rodada")
if not any(b for _, b in ordem):
    falhas.append("a tela nao pede a tarefa")
i_ini = next((k for k, (a, _) in enumerate(ordem) if a), 99)
i_exe = next((k for k, (_, b) in enumerate(ordem) if b), -1)
if i_ini > i_exe:
    falhas.append("pede a tarefa ANTES de abrir a rodada")
if "5002" not in js:
    falhas.append("a porta do servidor nao entrou no molde")
if sum(1 for _, b in ordem if b) != 1:
    falhas.append("pede a tarefa mais de uma vez")
print(f"casos: 4 | passaram: {4-len(falhas)} | falharam: {len(falhas)}")
for m in falhas: print("  X", m)
sys.exit(1 if falhas else 0)
