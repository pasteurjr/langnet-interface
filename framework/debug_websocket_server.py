"""
Servidor WebSocket debug para identificar erros
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DebugWebSocketServer:
    def __init__(self):
        self.connections = {}
    
    async def handle_connection(self, websocket, path):
        session_id = f"debug_session_{datetime.now().strftime('%H%M%S')}"
        logger.info(f"Nova conexão: {session_id}")
        
        try:
            self.connections[session_id] = websocket
            
            # Envia mensagem de boas-vindas
            welcome_message = {
                "type": "connected",
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "data": {
                    "session_id": session_id,
                    "available_tasks": ["read_email", "classify_message", "check_stock_availability", "generate_response"],
                    "message": "Conexão debug estabelecida"
                }
            }
            
            await websocket.send(json.dumps(welcome_message))
            logger.info(f"Mensagem de boas-vindas enviada para {session_id}")
            
            # Loop de mensagens
            async for message in websocket:
                logger.info(f"Mensagem recebida de {session_id}: {message}")
                
                try:
                    parsed_message = json.loads(message)
                    message_type = parsed_message.get("type")
                    
                    if message_type == "get_task_info":
                        response = {
                            "type": "task_info",
                            "timestamp": datetime.now().isoformat(),
                            "session_id": session_id,
                            "data": {
                                "task_order": ["read_email", "classify_message", "check_stock_availability", "generate_response"],
                                "mock_mode": True,
                                "description": "Sistema debug WebSocket"
                            }
                        }
                        await websocket.send(json.dumps(response))
                        logger.info(f"Task info enviada para {session_id}")
                    
                    elif message_type == "execute_task":
                        task_name = parsed_message.get("data", {}).get("task_name")
                        input_data = parsed_message.get("data", {}).get("input_data")
                        
                        logger.info(f"Executando task {task_name} para {session_id}")
                        
                        # Simula execução
                        await websocket.send(json.dumps({
                            "type": "task_start",
                            "timestamp": datetime.now().isoformat(),
                            "session_id": session_id,
                            "data": {"task_name": task_name, "input_data": input_data}
                        }))
                        
                        # Simula verbose
                        await websocket.send(json.dumps({
                            "type": "verbose", 
                            "timestamp": datetime.now().isoformat(),
                            "session_id": session_id,
                            "data": {"message": f"[DEBUG] Executando {task_name}..."}
                        }))
                        
                        # Simula resultado
                        await websocket.send(json.dumps({
                            "type": "task_result",
                            "timestamp": datetime.now().isoformat(),
                            "session_id": session_id,
                            "data": {
                                "task_name": task_name,
                                "result": {
                                    "task_name": task_name,
                                    "result_type": "json",
                                    "result": {"debug": True, "task": task_name, "status": "mock_success"}
                                },
                                "status": "success"
                            }
                        }))
                        
                        logger.info(f"Task {task_name} concluída para {session_id}")
                    
                    elif message_type == "ping":
                        await websocket.send(json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat(),
                            "session_id": session_id,
                            "data": {"timestamp": datetime.now().isoformat()}
                        }))
                        logger.info(f"Pong enviado para {session_id}")
                    
                    else:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "timestamp": datetime.now().isoformat(),
                            "session_id": session_id,
                            "data": {"error": f"Tipo de mensagem desconhecido: {message_type}"}
                        }))
                        logger.warning(f"Tipo de mensagem desconhecido: {message_type}")
                
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON: {e}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "timestamp": datetime.now().isoformat(),
                        "session_id": session_id,
                        "data": {"error": "Mensagem deve ser um JSON válido"}
                    }))
                except Exception as e:
                    logger.error(f"Erro no processamento: {e}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "timestamp": datetime.now().isoformat(),
                        "session_id": session_id,
                        "data": {"error": str(e)}
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Conexão fechada: {session_id}")
        except Exception as e:
            logger.error(f"Erro na conexão {session_id}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if session_id in self.connections:
                del self.connections[session_id]
                logger.info(f"Conexão removida: {session_id}")

async def start_debug_server():
    server = DebugWebSocketServer()
    logger.info("Iniciando servidor WebSocket debug na porta 5004")
    
    async with websockets.serve(server.handle_connection, "localhost", 5004):
        logger.info("✅ Servidor debug iniciado em ws://localhost:5004")
        await asyncio.Future()  # Mantém rodando

if __name__ == "__main__":
    asyncio.run(start_debug_server())