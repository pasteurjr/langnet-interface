"""O leitor do documento de Agentes e Tarefas devolve o nome da tarefa SEM a crase.

O documento é markdown e escreve o nome em `crase`. A crase viajava para dentro da
chave e tudo que procura pelo nome puro errava: a etapa Ferramentas exibia
"tarefa:`nome`" e o servidor de agentes montava o agente SEM ferramenta — o agente
então respondia, honestamente, que não conseguira obter o dado.
"""
import sys, os
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
from agents.langnetagents import _parse_tools_from_spec as ler

ATS = """
## 3. ESPECIFICAÇÃO DETALHADA DAS TAREFAS

### T-001

| Campo | Valor |
|---|---|
| **Nome** | `evaluate_multidrug_resistance` |
| **Tools** | json_parser_tool, database_tool |

### T-002

| Campo | Valor |
|---|---|
| **Nome** | classify_case_by_nhsn_criterion |
| **Tools** | database_tool (consulta, histórico), vector_search_tool |

## 4. FIM
"""

saida = ler(ATS)
texto = repr(saida)
falhas = []
if "`" in texto:
    falhas.append("sobrou crase na saída do leitor")
# procura o mapa de tarefas, seja qual for o nome da chave
achou = {}
def varrer(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str) and "multidrug" in k: achou[k] = v
            varrer(v)
varrer(saida)
if "evaluate_multidrug_resistance" not in achou:
    falhas.append(f"nome puro não encontrado; chaves vistas: {list(achou)}")
else:
    if sorted(achou["evaluate_multidrug_resistance"]) != ["database_tool", "json_parser_tool"]:
        falhas.append(f"ferramentas erradas: {achou['evaluate_multidrug_resistance']}")

print(f"casos: 3 | passaram: {3 - len(falhas)} | falharam: {len(falhas)}")
for m in falhas: print("  X", m)
sys.exit(1 if falhas else 0)
