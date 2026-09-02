import asyncio, json, time, websockets

CHAIN = json.load(open('/tmp/petri_chain.json'))
ORDER, INFO = CHAIN['order'], CHAIN['info']

# input inicial (token) que entra no fluxo — dados clínicos do paciente sentinela
SEED = {
    "email": "ana@hospital.br", "senha": "x", "codigo_mfa": "123456",
    "caso_id": "CAS-2023-001", "paciente_id": "P-001",
    "idade": 72, "apache_ii": 18, "dias_cateter": 12,
    "uti": True, "nutricao_parenteral": True, "neutropenia": False,
    "tipo_cateter": "Cateter Central", "microrganismo": "Staphylococcus aureus",
    "multirresistente": True,
}

def deep_merge(a, b):
    if not isinstance(b, dict): return a
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out

async def exec_task(name, input_data, timeout=140):
    async with websockets.connect("ws://localhost:5030", max_size=None, open_timeout=10) as ws:
        try: await asyncio.wait_for(ws.recv(), timeout=2)
        except Exception: pass
        await ws.send(json.dumps({"type":"execute_task","data":{"task_name":name,"input_data":input_data}}))
        t0=time.time()
        while time.time()-t0 < timeout:
            r=await asyncio.wait_for(ws.recv(), timeout=timeout)
            d=json.loads(r); typ=d.get("type")
            if typ=="task_completed": return d.get("data",{}).get("result",{})
            if typ=="error": return {"status":"erro","error":d.get("data",{}).get("error")}
        return {"status":"timeout"}

async def main():
    # só a cadeia clínica principal P1..P8 (+ admin do P1)
    main_chain = [p for p in ORDER if INFO[p]['task']]
    outputs = {}
    ok=0; total=0
    print(f"{'PLACE':5} {'TASK':34} {'RESULTADO'}")
    for pid in main_chain:
        i = INFO[pid]; task = i['task']
        # input_data = SEED + deepMerge dos outputs dos places anteriores (protocolo de entrada)
        inp = dict(SEED)
        for prev in i['prev']:
            if prev in outputs:
                inp = deep_merge(inp, outputs[prev])
        try:
            res = await exec_task(task, inp)
        except Exception as e:
            res = {"status":"erro","error":str(e)[:80]}
        total += 1
        status = res.get("status") if isinstance(res, dict) else None
        good = not (status in ("erro","timeout") or (isinstance(res,dict) and res.get("error")))
        if good: ok += 1
        outputs[pid] = res if isinstance(res, dict) else {}
        mark = "OK  " if good else "FALHOU"
        detail = json.dumps(res, ensure_ascii=False)[:95] if isinstance(res,dict) else str(res)[:95]
        print(f"{pid:5} {task:34} {mark} {detail}", flush=True)
    print(f"\nPLACAR (fluxo encadeado Petri): {ok}/{total} tarefas OK", flush=True)

asyncio.run(main())
