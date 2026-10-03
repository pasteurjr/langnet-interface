"""Agentes & Tarefas pelo padrão — só caso de uso com passo `agente` vira tarefa, no agente declarado.

Fixtures: o documento de Agentes e Tarefas do BioByte v5 (como foi gerado) e os fluxos da
Especificação v3 (com a coluna "Executado por").
"""
import sys, os, json
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
import warnings; warnings.filterwarnings("ignore")
import yaml
from agents.langnettarefas import (casos_agenticos, conferir_ats, remover_tarefas_convencionais,
                                   agente_do_documento, separar_yaml_crewai, chaves_de_primeiro_nivel,
                                   bloco_para_o_prompt)
from prompts.generate_single_task_yaml import parse_task_blocks

falhas = []; casos = 0
def confere(nome, cond):
    global casos; casos += 1
    print(("OK   " if cond else "FALHA"), nome)
    if not cond: falhas.append(nome)

aqui = os.path.dirname(__file__)
spec = open(os.path.join(aqui, "fixture_spec_biobyte_v5_v3_fluxos.md")).read()
ats = open(os.path.join(aqui, "fixture_ats_biobyte_v5.md")).read()
schema = open(os.path.join(aqui, "fixture_schema_biobyte_v5.sql")).read()

cas = [c["uc"] for c in casos_agenticos(spec)]
confere("6 casos de uso agênticos, tirados da coluna", cas == ["UC-008", "UC-009", "UC-011", "UC-013", "UC-015", "UC-025"])
confere("o prompt recebe a lista fechada", all(u in bloco_para_o_prompt(spec) for u in cas) and "NENHUMA outra" in bloco_para_o_prompt(spec))

nomes = {t["name"] for t in parse_task_blocks(ats)}
confere("leitor reconhece tarefa com título ###", "classify_case_by_nhsn_criterion" in nomes)
confere("nome da tarefa sem crase", not any("`" in n for n in nomes))

r = conferir_ats(ats, spec, schema)
confere("documento v5 é REPROVADO", not r["aprovado"])
confere("acusa tarefa de caso convencional", any("autenticar_usuario_email_senha" in p and "convencional" in p for p in r["problemas"]))
confere("acusa agente inventado (UC-025 só tinha a tarefa do laço de cobertura)", any("sinalizar_hemocultura_suspeita_icsac" in p and "não é nenhum dos agentes" in p for p in r["problemas"]))
confere("acusa entrada sem origem (critérios NHSN)", any("criterios_candidatos" in p and "sem origem" in p for p in r["problemas"]))

limpo, tirados = remover_tarefas_convencionais(ats, spec)
confere("25 tarefas convencionais retiradas", len(tirados) == 25)
confere("as 5 tarefas agênticas certas ficam", {"classify_case_by_nhsn_criterion", "recommend_bundle_with_justification"} <= {t["name"] for t in parse_task_blocks(limpo)})

# documento corrigido à mão (o que a correção dirigida deve produzir) é APROVADO
import re
def com_origem(doc, nome, linha):
    return re.sub(rf"(\|\s*\*\*Nome\*\*\s*\|\s*`{nome}`\s*\|)", r"\1\n| **Origem das entradas** | " + linha + " |", doc)
d = limpo
# fica UMA tarefa por UC: as T-AGN (o laço de cobertura duplicou cada UC)
for tid in ("T-008-001", "T-009-001", "T-011-001", "T-013-001", "T-015-001"):
    d = re.sub(rf"(?ms)^#{{3,4}}\s+{tid}:.*?(?=^#{{1,4}}\s|\Z)", "", d)
orig = {t["name"]: t["entradas"] for t in __import__("agents.langnettarefas", fromlist=["_tarefas"])._tarefas(d)}
for nome, ents in orig.items():
    d = com_origem(d, nome, "; ".join(f"{e}: contexto" for e in ents))
d = d.replace("criterios_candidatos: contexto", "criterios_candidatos: banco criterios_nhsn")
r2 = conferir_ats(d, spec, schema)
outros = [p for p in r2["problemas"] if "UC-025" not in p and "sinalizar_hemocultura" not in p]
confere("depois da limpeza: uma tarefa por caso agêntico (fora o UC-025)", not any("deve ter uma" in p for p in r2["problemas"]))
confere("origem no banco é conferida contra o modelo de dados", not any("criterios_nhsn" in p for p in r2["problemas"]))
d_ruim = d.replace("criterios_candidatos: banco criterios_nhsn", "criterios_candidatos: banco tabela_que_nao_existe")
confere("origem em tabela inexistente é acusada", any("tabela_que_nao_existe" in p for p in conferir_ats(d_ruim, spec, schema)["problemas"]))
confere("sem o laço, UC-025 fica sem tarefa e é acusado", any(p.startswith("UC-025") and "não tem tarefa" in p for p in conferir_ats(re.sub(r"(?ms)^#{3,4}\s+T-025-001:.*?(?=^#{1,4}\s|\Z)", "", d), spec, schema)["problemas"]))
confere("os dois agentes têm tarefa", all(n > 0 for n in r2["por_agente"].values()))

# Geração de Código: o agente vem do documento
ty = yaml.dump({"recommend_bundle_with_justification": {"description": "x", "expected_output": "y", "agent": "clinical_classifier_agent"},
                "classify_case_by_nhsn_criterion": {"description": "x", "expected_output": "y"}})
ay = yaml.dump({"clinical_classifier_agent": {"role": "a"}, "treatment_recommender_agent": {"role": "b"}})
ty2, feito = agente_do_documento(ty, ats, ay)
t2 = yaml.safe_load(ty2)
confere("recomendação vai para o agente de tratamento (documento)", t2["recommend_bundle_with_justification"]["agent"] == "treatment_recommender_agent")
confere("classificação fica no agente clínico", t2["classify_case_by_nhsn_criterion"]["agent"] == "clinical_classifier_agent")

# YAML no formato do CrewAI
cheio = yaml.dump({"t": {"description": "d", "expected_output": "e", "agent": "a", "traceability": {"uc": ["UC-1"]},
                         "output_schema": {"type": "object"}, "execution": "agent"}})
canon, meta = separar_yaml_crewai(cheio)
confere("tasks.yaml só com chaves do CrewAI", set(yaml.safe_load(canon)["t"]) == {"description", "expected_output", "agent"})
confere("o resto vai para tasks_meta.yaml", set(yaml.safe_load(meta)["t"]) == {"traceability", "output_schema", "execution"})
import agents.langnetagents as M
src = M._template_websocket_server_py(5099)
confere("o servidor gerado junta tasks_meta.yaml", 'os.path.exists("tasks_meta.yaml")' in src and "TASKS_CONFIG[_tn].update(_meta)" in src)

confere("lê o 1º nível do Input Schema", chaves_de_primeiro_nivel('{"caso_id": "UUID", "x": {"y": 1}, "lista": [{"z": 2}]}') == ["caso_id", "x", "lista"])

print(f"\n{casos} casos, {len(falhas)} falhas")
sys.exit(1 if falhas else 0)
