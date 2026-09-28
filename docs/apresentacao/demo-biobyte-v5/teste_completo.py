#!/usr/bin/env python3
"""TESTE COMPLETO do BioByte Sentinela v5 — aplicação implantada.

Duas baterias, todo caso com veredito conferido contra o banco ou contra gabarito:

  A) CADASTRO (CRUD)  — para cada entidade: listar, criar, ler, alterar, excluir.
     O veredito não é "a chamada respondeu"; é a linha existir/sumir no banco.
  B) AGENTES          — as 5 tarefas de IA contra dois casos clínicos plantados.

Gera o registro em docs/apresentacao/demo-biobyte-v5/registro_de_testes.md
"""
import asyncio, json, os, sys, time, uuid, datetime
import pymysql, websockets

PORTA = sys.argv[1] if len(sys.argv) > 1 else "5033"
BANCO = dict(host='127.0.0.1', port=3308, user='producao', password='112358123',
             database='biobyte_v5_app', charset='utf8mb4',
             cursorclass=pymysql.cursors.DictCursor, autocommit=True)
MDR, NAO_MDR = "HC-2026-1187", "HC-2026-1204"
REG = []   # (bateria, caso, esperado, obtido, passou)


def conta(tabela, onde="", args=()):
    c = pymysql.connect(**BANCO); cur = c.cursor()
    cur.execute(f"SELECT COUNT(*) n FROM `{tabela}` " + (f"WHERE {onde}" if onde else ""), args)
    n = cur.fetchone()['n']; c.close(); return n


async def pedir(tarefa, entrada, limite=180):
    async with websockets.connect(f"ws://127.0.0.1:{PORTA}", max_size=None, open_timeout=15) as ws:
        await ws.send(json.dumps({"type": "iniciar_execucao", "data": {}}))
        await asyncio.sleep(0.8)
        await ws.send(json.dumps({"type": "execute_task",
                                  "data": {"task_name": tarefa, "input_data": entrada}}))
        t0 = time.time()
        while time.time() - t0 < limite:
            try:
                m = json.loads(await asyncio.wait_for(ws.recv(), timeout=limite))
            except asyncio.TimeoutError:
                return {"status": "sem resposta"}
            if m.get("type") in ("task_completed", "task_result"):
                return (m.get("data") or {}).get("result") or m.get("data") or {}
            if m.get("type") in ("task_error", "error"):
                return {"status": "erro", "error": (m.get("data") or {}).get("error")}
    return {"status": "tempo esgotado"}


def anota(bateria, caso, esperado, obtido, passou):
    REG.append((bateria, caso, esperado, obtido, bool(passou)))
    print(f"{'PASSOU  ' if passou else 'FALHOU  '} | {caso}")
    print(f"            esperado: {esperado}")
    print(f"            obtido:   {obtido}", flush=True)


# ---------------- A) CADASTRO ----------------
ENTIDADES = [
    ("pacientes", {"nome": "Teste CRUD", "data_nascimento": "1975-03-22", "sexo": "F",
                   "numero_prontuario": "PR-TESTE-%s" % uuid.uuid4().hex[:6]},
     "nome", "Teste CRUD ALTERADO"),
    ("antimicrobianos", {"nome": "Teste-AM-%s" % uuid.uuid4().hex[:5], "classe": "Classe de Teste"},
     "classe", "Classe ALTERADA"),
    ("bundles", {"nome": "Bundle de Teste %s" % uuid.uuid4().hex[:5],
                 "indicacao": "somente teste", "reducao_media_risco": 10,
                 "intervalo_confianca": "5-15%", "ativo": 1},
     "indicacao", "indicacao ALTERADA"),
]


async def bateria_cadastro():
    print("\n" + "=" * 72); print("BATERIA A — CADASTRO (listar, criar, ler, alterar, excluir)"); print("=" * 72)
    for ent, dados, campo, novo_valor in ENTIDADES:
        # LISTAR
        r = await pedir(f"listar_{ent}", {})
        linhas = (r or {}).get("rows") or (r or {}).get("items") or []
        no_banco = conta(ent)
        anota("cadastro", f"{ent} · listar", f"a tela recebe as {no_banco} linhas do banco",
              f"recebeu {len(linhas)}", len(linhas) == no_banco)

        # CRIAR
        antes = conta(ent)
        r = await pedir(f"criar_{ent}", dados)
        depois = conta(ent)
        novo_id = (r or {}).get("id") or (r or {}).get("pk")
        anota("cadastro", f"{ent} · criar", f"o banco passa de {antes} para {antes+1} linhas",
              f"ficou com {depois} (resposta: {str(r)[:70]})", depois == antes + 1)
        if depois != antes + 1:
            continue

        # LER
        r = await pedir(f"obter_{ent}", {"id": novo_id})
        achou = any(str(v) == str(list(dados.values())[0]) for v in (r or {}).values()
                    if not isinstance(v, (dict, list)))
        anota("cadastro", f"{ent} · ler", "devolve o registro recém-criado",
              f"devolveu {str(r)[:90]}", achou)

        # ALTERAR
        r = await pedir(f"atualizar_{ent}", {"id": novo_id, campo: novo_valor})
        c = pymysql.connect(**BANCO); cur = c.cursor()
        cur.execute(f"SELECT `{campo}` v FROM `{ent}` WHERE id=%s", (novo_id,))
        row = cur.fetchone(); c.close()
        atual = (row or {}).get("v")
        anota("cadastro", f"{ent} · alterar", f"o campo {campo} vira '{novo_valor}' NO BANCO",
              f"no banco está '{atual}'", str(atual) == novo_valor)

        # EXCLUIR
        antes = conta(ent)
        r = await pedir(f"excluir_{ent}", {"id": novo_id})
        depois = conta(ent)
        anota("cadastro", f"{ent} · excluir", f"o banco volta de {antes} para {antes-1} linhas",
              f"ficou com {depois}", depois == antes - 1)


# ---------------- B) AGENTES ----------------
def cava(d, *chaves):
    if isinstance(d, dict):
        for k, v in d.items():
            if k in chaves and v is not None: return v
            r = cava(v, *chaves)
            if r is not None: return r
    elif isinstance(d, list):
        for x in d:
            r = cava(x, *chaves)
            if r is not None: return r
    return None


async def bateria_agentes():
    print("\n" + "=" * 72); print("BATERIA B — AGENTES (contra gabarito plantado no banco)"); print("=" * 72)
    r = await pedir("evaluate_multidrug_resistance", {"identificador_amostra": MDR})
    n = cava(r, "contagem_classes_resistentes")
    anota("agentes", "multirresistência · conta as classes (caso 4 classes)",
          "contagem = 4", f"contagem = {n}", n is not None and int(float(n)) == 4)
    v = cava(r, "multirresistente")
    anota("agentes", "multirresistência · aplica a regra das três classes",
          "multirresistente = verdadeiro", f"multirresistente = {v}", v is True)

    r = await pedir("evaluate_multidrug_resistance", {"identificador_amostra": NAO_MDR})
    n = cava(r, "contagem_classes_resistentes")
    anota("agentes", "multirresistência · conta as classes (caso 1 classe)",
          "contagem = 1", f"contagem = {n}", n is not None and int(float(n)) == 1)

    r = await pedir("translate_lab_result_to_hospital_vocabulary", {"identificador_amostra": MDR})
    ab = cava(r, "antibiograma") or []
    com_classe = [x for x in ab if isinstance(x, dict) and x.get("classe")]
    anota("agentes", "tradução · traz o antibiograma completo do banco",
          "6 antimicrobianos, todos com classe", f"{len(ab)} antimicrobianos, {len(com_classe)} com classe",
          len(ab) == 6 and len(com_classe) == 6)

    r = await pedir("translate_lab_result_to_hospital_vocabulary", {"identificador_amostra": "HC-NAO-EXISTE"})
    apro = cava(r, "aproveitavel"); just = str(cava(r, "justificativa") or "")
    anota("agentes", "tradução · recusa amostra inexistente sem inventar",
          "aproveitável = falso, com justificativa", f"aproveitável = {apro}, justificativa de {len(just)} caracteres",
          apro is False and len(just) > 30)

    r = await pedir("classify_case_by_nhsn_criterion", {"identificador_amostra": MDR, "data_inicio_caso": "2026-09-21"})
    cl = cava(r, "classificacao")
    anota("agentes", "classificação · responde pelo critério da norma",
          "confirmada, descartada ou pendente", f"{cl}", cl in ("confirmada", "descartada", "pendente"))

    r = await pedir("recommend_bundle_with_justification",
                    {"identificador_amostra": MDR, "classificacao": "confirmada", "multirresistente": True})
    bn = cava(r, "bundle_recomendado_nome", "bundle_recomendado", "bundle")
    just = str(cava(r, "justificativa") or "")
    c = pymysql.connect(**BANCO); cur = c.cursor(); cur.execute("SELECT nome FROM bundles"); nomes=[x['nome'] for x in cur.fetchall()]; c.close()
    existe = bool(bn) and any(str(bn).lower() in x.lower() or x.lower() in str(bn).lower() for x in nomes)
    anota("agentes", "recomendação · escolhe pacote que existe no cadastro",
          "um pacote do cadastro, com justificativa", f"{str(bn)[:50]} (justificativa: {len(just)} car)",
          existe and len(just) > 20)

    r = await pedir("draft_alert_text_for_care_team",
                    {"identificador_amostra": MDR, "multirresistente": True,
                     "classes_resistentes": ["Betalactâmico", "Cefalosporina", "Fluoroquinolona", "Aminoglicosídeo"]})
    tx = str(cava(r, "texto_alerta", "mensagem_alerta", "mensagem", "texto") or "")
    cita = any(p in tx.lower() for p in ("aureus", "multirresist", "classe", "resistent"))
    anota("agentes", "alerta · redige o texto citando o achado clínico",
          "texto clínico citando o achado", f"{len(tx)} caracteres, cita o achado = {cita}",
          len(tx) > 40 and cita)


async def main():
    await bateria_cadastro()
    await bateria_agentes()
    ok = sum(1 for x in REG if x[4]); tot = len(REG)
    print("\n" + "=" * 72)
    print(f"RESULTADO: {ok} de {tot} casos passaram")
    print("=" * 72)
    # registro
    linhas = [f"# Registro de Testes — BioByte Sentinela v5", "",
              f"Executado em {datetime.datetime.now():%d/%m/%Y %H:%M} contra a aplicação implantada "
              f"(servidor de agentes na porta {PORTA}, banco `biobyte_v5_app`).", "",
              f"**{ok} de {tot} casos passaram.**", "",
              "Cada caso tem um veredito conferido: no cadastro, contra a linha no banco; "
              "nos agentes, contra o gabarito plantado (uma amostra com 4 classes resistentes e "
              "outra com 1).", ""]
    for bat, rot in (("cadastro", "Cadastro — listar, criar, ler, alterar, excluir"),
                     ("agentes", "Agentes — as cinco tarefas de inteligência artificial")):
        linhas += [f"## {rot}", "", "| | Caso | Esperado | Obtido |", "|---|---|---|---|"]
        for b, caso, esp, obt, passou in REG:
            if b != bat: continue
            linhas.append(f"| {'✅' if passou else '❌'} | {caso} | {esp} | {obt} |")
        linhas.append("")
    destino = "/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v5/registro_de_testes.md"
    open(destino, "w", encoding="utf-8").write("\n".join(linhas))
    print("registro em:", destino)

asyncio.run(main())
