import asyncio, json, time, websockets, sys
async def run(name, inp, timeout=60):
    async with websockets.connect("ws://localhost:5030", max_size=None, open_timeout=10) as ws:
        try:
            await asyncio.wait_for(ws.recv(), timeout=2)
        except Exception:
            pass
        await ws.send(json.dumps({"type": "execute_task", "data": {"task_name": name, "input_data": inp}}))
        t0 = time.time()
        while time.time() - t0 < timeout:
            r = await asyncio.wait_for(ws.recv(), timeout=timeout)
            d = json.loads(r); typ = d.get("type")
            if typ == "task_completed":
                print("RESULT:", json.dumps(d.get("data", {}).get("result", {}), ensure_ascii=False)[:400]); return
            if typ == "error":
                print("ERROR:", json.dumps(d.get("data", {}), ensure_ascii=False)[:400]); return
        print("TIMEOUT")
name = sys.argv[1]; inp = json.loads(sys.argv[2])
asyncio.run(run(name, inp))
