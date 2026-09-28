"""Tarefa de julgamento NÃO ganha substituto mecânico.

O servidor de agentes prefere a função determinística ao agente. Quando a tarefa é de
julgamento, o tradutor emitia um corpo sem substância — abre conexão, atribui uma
constante e devolve {'status': 'sucesso'}. O agente nunca era chamado e a tarefa
relatava SUCESSO sem produzir nada. Medido no BioByte v5 em 28/09/2026:
recommend_bundle_with_justification devolveu "sucesso" e nenhum pacote;
draft_alert_text_for_care_team devolveu "sucesso" e nenhum texto.

A prova roda sobre o tasks.yaml REAL do v5 (fixtures_tasks_v5.yaml), que é o que
produziu o defeito.
"""
import sys, os, re
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
from agents.langnetagents import _generate_deterministic_adapters as emitir

TASKS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures_tasks_v5.yaml"), encoding="utf-8").read()
JULGAMENTO = ["recommend_bundle_with_justification", "draft_alert_text_for_care_team"]

saida = emitir(TASKS) or ""
falhas = []

for t in JULGAMENTO:
    if f"def {t}_deterministic(" in saida:
        corpo = saida.split(f"def {t}_deterministic(")[1].split("\ndef ")[0]
        if "cur.execute(" not in corpo:
            falhas.append(f"{t}: emitiu substituto que não consulta nada e devolve sucesso")

# nenhuma função emitida pode devolver sucesso sem ter consultado ou calculado
for m in re.finditer(r"def (\w+)_deterministic\(input_data\):(.*?)(?=\ndef |\Z)", saida, re.S):
    nome, corpo = m.group(1), m.group(2)
    if "'status': 'sucesso'" in corpo and "cur.execute(" not in corpo \
            and not re.search(r"_num\(|_safe_div\(", corpo):
        falhas.append(f"{nome}: devolve sucesso sem consulta nem conta")

emitidas = re.findall(r"def (\w+)_deterministic\(input_data\):", saida)
print(f"funções mecânicas emitidas: {len(emitidas)}")
print(f"casos: {2 + len(emitidas)} | falharam: {len(falhas)}")
for x in falhas: print("  X", x)
sys.exit(1 if falhas else 0)
