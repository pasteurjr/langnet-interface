"""
Cliente de teste para servidor debug
"""

import asyncio
import json
import websockets

async def test_debug_server():
    uri = "ws://localhost:5004"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Conectado ao servidor debug: {uri}")
            
            # Recebe mensagem de boas-vindas
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"📨 Boas-vindas: {welcome_data}")
            
            # Testa get_task_info
            await websocket.send(json.dumps({
                "type": "get_task_info",
                "data": {}
            }))
            
            info_response = await websocket.recv()
            info_data = json.loads(info_response)
            print(f"📋 Task info: {info_data}")
            
            # Testa execução de task
            await websocket.send(json.dumps({
                "type": "execute_task",
                "data": {
                    "task_name": "read_email",
                    "input_data": {"max_emails": 5}
                }
            }))
            
            # Recebe respostas da execução
            for i in range(3):  # Espera 3 mensagens (start, verbose, result)
                message = await websocket.recv()
                parsed = json.loads(message)
                print(f"📨 {parsed['type']}: {parsed['data']}")
            
            print("\n✅ Teste debug concluído com sucesso!")
                    
    except Exception as e:
        print(f"❌ Erro no teste debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_debug_server())