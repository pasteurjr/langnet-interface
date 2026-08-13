#!/usr/bin/env python3
"""Fault-injection do contrato de saída (Fase 1): chama uma task agêntica cujo output_schema
exige um campo que o agente NÃO produz e confirma que o ws-server responde 'error' (fail-loud),
não 'task_completed'. Uso: fault_inject.py <task_name>."""
import asyncio, json, os, sys
import websockets

WS = f"ws://localhost:{os.environ.get('WS_PORT','5003')}"
TASK = sys.argv[1] if len(sys.argv) > 1 else "pre_atendimento_cardiologia"
INPUT = {"paciente_id": "n/a", "queixa_inicial": "Dor toracica opressiva, sudorese",
         "sinais_vitais": "PA 160/100, FC 120, SpO2 92"}

async def main():
    async with websockets.connect(WS, max_size=None) as ws:
        await ws.send(json.dumps({"type": "execute_task", "data": {"task_name": TASK, "input_data": INPUT}}))
        while True:
            m = json.loads(await asyncio.wait_for(ws.recv(), timeout=650))
            typ = m.get("type")
            if typ in ("task_completed", "task_result"):
                print("RESULTADO: task_completed (contrato NÃO barrou) — FALHA do teste"); return 1
            if typ in ("error", "task_error"):
                d = m.get("data") or {}
                print("RESULTADO: error (fail-loud OK) ::", str(d.get("error"))[:160], "| faltantes:", d.get("faltantes"))
                return 0

sys.exit(asyncio.run(main()))
