"""
ClinIA — Clínica Médica Inteligente — entrypoint
Sobe o servidor WebSocket na porta 5003 que recebe execute_task
e dispara a task CrewAI correspondente.
"""
import asyncio
import os
from dotenv import load_dotenv

from websocket_server import run_websocket_server

load_dotenv()

PROJECT_NAME = "ClinIA — Clínica Médica Inteligente"


def main():
    port = int(os.getenv("WEBSOCKET_PORT", "5003"))
    host = os.getenv("WEBSOCKET_HOST", "localhost")
    print(f"🚀 {PROJECT_NAME} — WebSocket server em ws://{host}:{port}")
    asyncio.run(run_websocket_server(host=host, port=port))


if __name__ == "__main__":
    main()
