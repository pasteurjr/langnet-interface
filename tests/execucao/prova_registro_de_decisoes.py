"""As respostas dos agentes são gravadas na tabela que o documento de Agentes e Tarefas designa.

Medido no BioByte v5 em 29/09/2026: os agentes respondiam, a tela mostrava, e nada ia para o
banco — a premissa A-04 do documento ("toda decisão agêntica é persistida em decisao_sistema,
pelo código comum que chama a tarefa") não era lida por ninguém. Esta prova usa o documento,
o esquema e o tasks.yaml reais do projeto e grava num banco descartável.
"""
import sys, os, json
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
import warnings; warnings.filterwarnings("ignore")
import agents.langnetagents as M
aqui = os.path.dirname(os.path.abspath(__file__))
ats = open(aqui + "/fixture_ats_biobyte_v5.md", encoding="utf-8").read()
ddl = open(aqui + "/fixture_schema_biobyte_v5.sql", encoding="utf-8").read()
tasks = open(aqui + "/fixtures_tasks_v5.yaml", encoding="utf-8").read()

falhas = []
def confere(nome, cond):
    print(("OK   " if cond else "FALHA"), nome)
    if not cond: falhas.append(nome)

info = M._tabela_de_decisoes(ats, ddl)
confere("acha a tabela designada (decisao_sistema → decisoes_sistema)", info and info["tabela"] == "decisoes_sistema")
codigo = M._emitir_registro_de_decisoes(ats, ddl, tasks)
confere("emite o código de registro", "_registrar_decisao" in codigo)
confere("ninguém fica sem tipo válido", all(v in ("risco", "classificacao", "conduta") for v in json.loads(codigo.split("_REGISTRO_DECISOES = ")[1].split("\n\n\n")[0])["tipos"].values()))
confere("sem documento, não emite nada", M._emitir_registro_de_decisoes("", ddl, tasks) == "")

# grava de verdade num banco descartável
import pymysql
adm = pymysql.connect(host="127.0.0.1", port=3308, user="producao", password="112358123")
c = adm.cursor(); BANCO = "prova_registro_decisoes"
c.execute(f"DROP DATABASE IF EXISTS {BANCO}"); c.execute(f"CREATE DATABASE {BANCO}")
c.execute(f"USE {BANCO}")
c.execute("CREATE TABLE casos_clinicos (id CHAR(36) PRIMARY KEY)")
bloco = ddl[ddl.index("CREATE TABLE `decisoes_sistema`"):]
bloco = bloco[:bloco.index(";") + 1]
c.execute(bloco)
c.execute("INSERT INTO casos_clinicos VALUES ('caso-1')"); adm.commit()
os.environ.update(DB_HOST="127.0.0.1", DB_PORT="3308", DB_USER="producao", DB_PASSWORD="112358123", DB_NAME=BANCO)
ns = {}; exec(codigo, ns)
saida = {"multirresistente": True, "contagem_classes_resistentes": 4, "versao_prompt": "v1"}
r = ns["_registrar_decisao"]("evaluate_multidrug_resistance", {"upstream_outputs": {"x": {"caso_id": "caso-1"}}}, saida)
confere("grava quando o caso vem de uma saída anterior", r.get("registrado") is True)
c.execute("SELECT caso_id, tipo, origem_dado, valor FROM decisoes_sistema"); linha = c.fetchone()
confere("a linha aponta para o caso", linha and linha[0] == "caso-1")
confere("o valor é a resposta do agente", linha and json.loads(linha[3])["multirresistente"] is True)
confere("a origem cita a tarefa e o prompt", linha and linha[2].startswith("evaluate_multidrug_resistance · v1"))
r2 = ns["_registrar_decisao"]("evaluate_multidrug_resistance", {}, saida)
confere("sem o caso, NÃO grava e diz por quê", r2.get("registrado") is False and "caso_id" in r2.get("motivo", ""))
c.execute(f"DROP DATABASE {BANCO}"); adm.close()
print("\n%d falha(s)" % len(falhas)); sys.exit(1 if falhas else 0)
