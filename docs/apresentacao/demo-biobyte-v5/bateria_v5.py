#!/usr/bin/env python3
"""Bateria do BioByte v5 contra o sistema IMPLANTADO.

Cada caso tem um JUÍZO DE VERDADE, escrito contra o gabarito plantado no banco — não
contagem de palavras em comum. O que não tem como ser julgado é reportado como tal,
nunca como aprovação.

  HC-2026-1187 — Staphylococcus aureus, 6 antimicrobianos, 4 classes resistentes  -> É multirresistente
  HC-2026-1204 — Escherichia coli,      4 antimicrobianos, 1 classe  resistente   -> NÃO é
"""
import asyncio, json, os, re, sys, time
from pathlib import Path
import pymysql

PORTA = sys.argv[1] if len(sys.argv) > 1 else "5026"
MDR, NAO_MDR = "HC-2026-1187", "HC-2026-1204"


async def pedir(tarefa, entrada, limite=240):
    import websockets
    async with websockets.connect(f"ws://127.0.0.1:{PORTA}", max_size=None, open_timeout=15) as ws:
        await ws.send(json.dumps({"type": "iniciar_execucao", "data": {}}))
        await asyncio.sleep(1.0)
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


def cava(d, *chaves):
    """Procura a chave em qualquer nível da resposta (o agente às vezes aninha)."""
    if isinstance(d, dict):
        for k, v in d.items():
            if k in chaves:
                return v
            r = cava(v, *chaves)
            if r is not None:
                return r
    elif isinstance(d, list):
        for x in d:
            r = cava(x, *chaves)
            if r is not None:
                return r
    return None


# ---- os juízos: (nome do caso, tarefa, entrada, função que julga a resposta) ----
def j_contagem_mdr(r):
    n = cava(r, "contagem_classes_resistentes")
    cls = cava(r, "classes_resistentes") or []
    if n is None:
        return False, f"não devolveu a contagem (chaves: {list(r)[:5]})"
    ok = int(float(n)) == 4 and len(cls) == 4
    return ok, f"contagem={n}, classes={cls} (gabarito: 4)"

def j_contagem_nao_mdr(r):
    n = cava(r, "contagem_classes_resistentes")
    if n is None:
        return False, "não devolveu a contagem"
    return int(float(n)) == 1, f"contagem={n} (gabarito: 1)"

def j_veredito_mdr(r):
    v = cava(r, "multirresistente")
    if v is None:
        return False, "veredito vazio — a regra das três classes não foi aplicada"
    return v is True, f"multirresistente={v} (gabarito: verdadeiro)"

def j_veredito_nao_mdr(r):
    v = cava(r, "multirresistente")
    if v is None:
        return False, "veredito vazio — a regra das três classes não foi aplicada"
    return v is False, f"multirresistente={v} (gabarito: falso)"

def j_traducao_completa(r):
    ab = cava(r, "antibiograma") or []
    micro = cava(r, "microrganismo")
    if not ab:
        return False, "não devolveu antibiograma"
    com_classe = [x for x in ab if isinstance(x, dict) and x.get("classe")]
    ok = len(ab) == 6 and len(com_classe) == 6 and micro == "Staphylococcus aureus"
    return ok, f"{len(ab)} antimicrobianos, {len(com_classe)} com classe, microrganismo={micro} (gabarito: 6/6/Staphylococcus aureus)"

def j_traducao_amostra_inexistente(r):
    apro = cava(r, "aproveitavel")
    just = str(cava(r, "justificativa") or "")
    if apro is True:
        return False, "declarou aproveitável um resultado que não existe — inventou"
    return (apro is False and len(just) > 30), f"aproveitavel={apro}, justificou em {len(just)} caracteres"

def j_classificacao_valida(r):
    c = cava(r, "classificacao")
    if c is None:
        return False, "não devolveu classificação"
    return c in ("confirmada", "descartada", "pendente"), f"classificacao={c} (aceitos: confirmada/descartada/pendente)"

def j_bundle_existe(r, bundles):
    b = cava(r, "bundle_recomendado_nome", "bundle_recomendado", "bundle",
             "nome_bundle", "bundle_id")
    just = str(cava(r, "justificativa") or "")
    if not b:
        return False, "não recomendou bundle"
    achou = any(str(b).lower() in nb.lower() or nb.lower() in str(b).lower() for nb in bundles)
    return (achou and len(just) > 20), f"bundle={str(b)[:60]}, existe no cadastro={achou}, justificativa={len(just)} car"

def j_alerta_redigido(r):
    t = cava(r, "mensagem_alerta", "texto_alerta", "mensagem", "texto")
    if not t or len(str(t)) < 40:
        return False, f"texto do alerta ausente ou curto demais ({len(str(t or ''))} caracteres)"
    tx = str(t).lower()
    cita = any(p in tx for p in ("aureus", "multirresist", "classe", "resistent"))
    return cita, f"{len(str(t))} caracteres; cita o achado clínico={cita}"


async def main():
    c = pymysql.connect(host='127.0.0.1', port=3308, user='producao', password='112358123',
                        database='biobyte_v5_app', charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)
    cur = c.cursor(); cur.execute("SELECT nome FROM bundles")
    bundles = [r["nome"] for r in cur.fetchall()]

    CASOS = [
        ("UC-011 · conta as classes resistentes (caso multirresistente)",
         "evaluate_multidrug_resistance", {"identificador_amostra": MDR}, j_contagem_mdr),
        ("UC-011 · conta as classes resistentes (caso NÃO multirresistente)",
         "evaluate_multidrug_resistance", {"identificador_amostra": NAO_MDR}, j_contagem_nao_mdr),
        ("UC-011 · aplica a regra das três classes (deve dizer SIM)",
         "evaluate_multidrug_resistance", {"identificador_amostra": MDR}, j_veredito_mdr),
        ("UC-011 · aplica a regra das três classes (deve dizer NÃO)",
         "evaluate_multidrug_resistance", {"identificador_amostra": NAO_MDR}, j_veredito_nao_mdr),
        ("UC-008 · traduz o resultado do laboratório inteiro",
         "translate_lab_result_to_hospital_vocabulary", {"identificador_amostra": MDR}, j_traducao_completa),
        ("UC-008 · recusa amostra inexistente sem inventar",
         "translate_lab_result_to_hospital_vocabulary", {"identificador_amostra": "HC-NAO-EXISTE"},
         j_traducao_amostra_inexistente),
        ("UC-009 · classifica pelo critério da norma",
         "classify_case_by_nhsn_criterion",
         {"identificador_amostra": MDR, "data_inicio_caso": "2026-09-21"}, j_classificacao_valida),
        ("UC-015 · recomenda bundle que existe no cadastro",
         "recommend_bundle_with_justification",
         {"identificador_amostra": MDR, "classificacao": "confirmada", "multirresistente": True},
         lambda r: j_bundle_existe(r, bundles)),
        ("UC-013 · redige o texto do alerta citando o achado",
         "draft_alert_text_for_care_team",
         {"identificador_amostra": MDR, "multirresistente": True,
          "classes_resistentes": ["Betalactâmico", "Cefalosporina", "Fluoroquinolona", "Aminoglicosídeo"]},
         j_alerta_redigido),
    ]

    linhas, ok, falhou = [], 0, 0
    for nome, tarefa, entrada, juiz in CASOS:
        try:
            r = await pedir(tarefa, entrada)
        except Exception as e:
            r = {"status": "erro", "error": f"{type(e).__name__}: {e}"}
        try:
            passou, razao = juiz(r)
        except Exception as e:
            passou, razao = False, f"juiz falhou: {e}"
        ok += 1 if passou else 0
        falhou += 0 if passou else 1
        print(f"{'APROVADO ' if passou else 'REPROVADO'} | {nome}", flush=True)
        print(f"            {razao}", flush=True)
        linhas.append({"caso": nome, "tarefa": tarefa, "aprovado": bool(passou),
                       "razao": razao, "resposta": r})

    print()
    print(f"=== BATERIA: {ok} aprovados / {falhou} reprovados, em {len(CASOS)} casos ===")
    json.dump({"aprovados": ok, "reprovados": falhou, "casos": linhas},
              open(os.environ["CLAUDE_JOB_DIR"] + "/tmp/bateria_v5_resultado.json", "w"),
              ensure_ascii=False, indent=2)

asyncio.run(main())
