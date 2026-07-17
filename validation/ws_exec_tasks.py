#!/usr/bin/env python3
"""Executa cada task REAL do tasks.yaml via WebSocket, registrando resultado."""
import asyncio, json, time, websockets
REAL = json.load(open("/tmp/uso-solo-pipeline/real-tasks.json"))
WS = "ws://localhost:5003"; TIMEOUT = 75
INPUTS = {
    "cadastrar_persona_alvo": {"nome": f"WS Real {int(time.time())}", "descricao": "x",
        "canais": ["linkedin"], "problemas": ["p1"], "gatilhos_de_compra": ["g1"],
        "objecoes": ["o1"], "palavras_chave": ["k1"]},
    "gerar_calendario_mensal": {"mes_ano": "Outubro/2023"},
    "gerar_relatorios_semanais": {"data": "2024-10-07"},
    "gerar_conteudo_redator": {"tipo_conteudo": "Post Curto", "persona": "X", "pilar": "Y"},
    "verificar_fatos_revisor": {"afirmacao": "O céu é azul"},
    "publicar_conteudo_plataformas": {"post_id": "demo", "canal": "linkedin"},
    "coletar_metricas_engajamento": {"periodo_inicio": "2024-10-01", "periodo_fim": "2024-10-31"},
    "classificar_comentarios_leads": {"comentario": "Quero saber o preço"},
    "gerar_respostas_automaticas_comentarios": {"comentario": "Gostei"},
    "identificar_leads_warm_inbound": {"mes_ano": "Outubro/2023"},
    "exportar_calendario_relatorios": {"mes_ano": "Outubro/2023", "formato": "PDF"},
    "sincronizar_agenda_google_calendar": {},
}
async def run(task, inp):
    t0=time.time()
    try:
        async with websockets.connect(WS, open_timeout=10) as ws:
            try: await asyncio.wait_for(ws.recv(), timeout=3)
            except asyncio.TimeoutError: pass
            await ws.send(json.dumps({"type":"execute_task","data":{"task_name":task,"input_data":inp}}))
            while True:
                m=json.loads(await asyncio.wait_for(ws.recv(), timeout=TIMEOUT))
                if m.get("type") in ("task_completed","task_result"):
                    return {"outcome":"completed","secs":round(time.time()-t0,1),"result":m.get("data",{}).get("result",m.get("data"))}
                if m.get("type")=="error":
                    return {"outcome":"error","secs":round(time.time()-t0,1),"error":str(m.get("data",{}).get("error"))[:200]}
    except asyncio.TimeoutError: return {"outcome":"timeout","secs":TIMEOUT}
    except Exception as e: return {"outcome":"exception","secs":round(time.time()-t0,1),"error":str(e)[:160]}
async def main():
    out={}
    for t in REAL:
        r=await run(t, INPUTS.get(t,{})); out[t]=r
        print(f"{t:42s} {r['outcome']:10s} {r.get('secs')}s")
    json.dump(out, open("/tmp/uso-solo-pipeline/ws-exec-results.json","w"), ensure_ascii=False, indent=2)
    print("OK")
asyncio.run(main())
