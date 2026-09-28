"""O caso de uso e o requisito de cada tarefa vêm do documento para o tasks.yaml.

Quando o formato voltou ao padrão do CrewAI (24/09/2026), a injeção do bloco de
rastreabilidade saiu do prompt e nada a repôs. Medido no BioByte v5 em 28/09/2026:
a matriz do pacote saía vazia (99 requisitos, zero ligações) e o casamento tela↔tarefa
— que usa o caso de uso como ponte entre o português da tela e o inglês da tarefa —
nunca disparava, deixando quatro das cinco telas de agente sem botão de executar.
"""
import sys, os, re
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
from agents.langnetagents import _injetar_rastreabilidade_do_documento as injetar

ATS = """
### T-AGN-003: Evaluate Multidrug Resistance

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `evaluate_multidrug_resistance` |
| **Agent** | AG-01 |
| **UC Relacionado** | UC-011 |
| **RF Relacionado** | FR-031, FR-032, FR-033 |

### T-AGN-004: Draft Alert

| Atributo | Especificação |
|----------|---------------|
| **Nome** | `draft_alert_text_for_care_team` |
| **UC Relacionado** | UC-013 |
| **RF Relacionado** | FR-040 |
"""
YAML = """evaluate_multidrug_resistance:
  description: >
    Avaliar multirresistência.
  expected_output: >
    JSON

draft_alert_text_for_care_team:
  description: >
    Redigir alerta.
  expected_output: >
    JSON
"""

saida = injetar(YAML, ATS)
falhas = []
import yaml as _y
d = _y.safe_load(saida)
for t, uc, frs in [("evaluate_multidrug_resistance", "UC-011", ["FR-031","FR-032","FR-033"]),
                   ("draft_alert_text_for_care_team", "UC-013", ["FR-040"])]:
    tr = (d.get(t) or {}).get("traceability")
    if not tr:
        falhas.append(f"{t}: sem bloco de rastreabilidade"); continue
    if uc not in [str(x) for x in (tr.get("uc") or [])]:
        falhas.append(f"{t}: caso de uso {uc} nao veio (veio {tr.get('uc')})")
    if sorted(str(x) for x in (tr.get("fr") or [])) != sorted(frs):
        falhas.append(f"{t}: requisitos errados (veio {tr.get('fr')})")
# descrição e formato de saída continuam intactos
if "Avaliar multirresistência" not in saida or "expected_output" not in saida:
    falhas.append("mexeu na descricao ou no formato de saida")
# sem documento, não inventa
if injetar(YAML, "") != YAML:
    falhas.append("inventou rastreabilidade sem documento")

print(f"casos: 6 | passaram: {6-len(falhas)} | falharam: {len(falhas)}")
for m in falhas: print("  X", m)
sys.exit(1 if falhas else 0)
