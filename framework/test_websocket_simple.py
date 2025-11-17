"""
Teste simples da WebSocket API Tropical
"""

import asyncio
import json
import websockets

async def test_websocket():
    uri = "ws://localhost:5003"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Conectado a {uri}")
            
            # Recebe mensagem de boas-vindas
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"📨 Boas-vindas: {welcome_data['type']}")
            print(f"📋 Tasks disponíveis: {welcome_data['data']['available_tasks']}")
            
            # Testa get_task_info
            await websocket.send(json.dumps({
                "type": "get_task_info",
                "data": {}
            }))
            
            info_response = await websocket.recv()
            info_data = json.loads(info_response)
            print(f"📋 Info das tasks: {info_data['data']['task_order']}")
            
            # Testa execução de read_email
            print("\n🚀 Testando execução de read_email...")
            await websocket.send(json.dumps({
                "type": "execute_task",
                "data": {
                    "task_name": "read_email",
                    "input_data": {"max_emails": 5}
                }
            }))
            
            # Aguarda respostas
            message_count = 0
            while message_count < 20:  # Limite para evitar loop infinito
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    parsed = json.loads(message)
                    
                    if parsed["type"] == "verbose":
                        print(f"💬 Verbose: {parsed['data']['message']}")
                    elif parsed["type"] == "task_start":
                        print(f"🏁 Iniciando: {parsed['data']['task_name']}")
                    elif parsed["type"] == "task_result":
                        print(f"✅ Resultado: {parsed['data']['result']['task_name']} - {parsed['data']['result']['result_type']}")
                        if parsed['data']['result']['result_type'] == 'json':
                            result_data = parsed['data']['result']['result']
                            if 'emails' in result_data:
                                print(f"   📧 {len(result_data['emails'])} emails processados")
                        break
                    elif parsed["type"] == "error":
                        print(f"❌ Erro: {parsed['data']['error']}")
                        break
                    else:
                        print(f"📨 {parsed['type']}: {parsed['data']}")
                    
                    message_count += 1
                    
                except asyncio.TimeoutError:
                    print("⏱️ Timeout aguardando resposta")
                    break
                except Exception as e:
                    print(f"❌ Erro ao processar mensagem: {e}")
                    break
            
            # Teste classificação em sequência
            print("\n🔗 Testando classify_message...")
            await websocket.send(json.dumps({
                "type": "execute_task", 
                "data": {
                    "task_name": "classify_message",
                    "input_data": {
                        "timestamp": "2025-07-30T18:55:00",
                        "total_emails": 2,
                        "emails": [
                            {
                                "email_id": "001",
                                "from": "cliente@empresa.com",
                                "subject": "Pedido urgente",
                                "content": "Preciso de 100 bombonas 20l",
                                "date": "2025-07-30T18:55:00",
                                "status": "success"
                            }
                        ]
                    }
                }
            }))
            
            # Aguarda resultado da classificação
            classify_result = None
            for _ in range(10):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    parsed = json.loads(message)
                    
                    if parsed["type"] == "task_result":
                        classify_result = parsed['data']['result']['result']
                        print(f"✅ Classificação concluída: {len(classify_result['emails'])} emails classificados")
                        break
                    elif parsed["type"] == "verbose":
                        print(f"💬 {parsed['data']['message']}")
                    elif parsed["type"] == "error":
                        print(f"❌ Erro: {parsed['data']['error']}")
                        break
                        
                except asyncio.TimeoutError:
                    print("⏱️ Timeout na classificação")
                    break
            
            print("\n✅ Teste WebSocket concluído com sucesso!")
                    
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket())