"""
WebSocket API para execução individual de tasks do sistema Tropical
Baseado no tropicalagentssalesv2.py para suporte à Petri Net
"""

import asyncio
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import websockets
from websockets.server import WebSocketServerProtocol
import threading
import sys
import os

# Adiciona o diretório framework ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa as funções das tasks (usando versão simplificada para teste)
try:
    from simple_tropical_tasks import execute_individual_task, get_task_chain_info, individual_tasks
    print("✅ Módulo simple_tropical_tasks importado com sucesso (MODO MOCK)")
except ImportError as e:
    print(f"❌ Erro ao importar simple_tropical_tasks: {e}")
    sys.exit(1)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TropicalWebSocketAPI:
    def __init__(self, host: str = "localhost", port: int = 5002):
        self.host = host
        self.port = port
        self.active_connections: Dict[str, WebSocketServerProtocol] = {}
        self.execution_sessions: Dict[str, Dict] = {}
        
    def generate_session_id(self) -> str:
        """Gera ID único para sessão"""
        return f"tropical_session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    async def register_connection(self, websocket: WebSocketServerProtocol, session_id: str):
        """Registra nova conexão WebSocket"""
        self.active_connections[session_id] = websocket
        self.execution_sessions[session_id] = {
            "start_time": datetime.now(),
            "tasks_executed": [],
            "current_task": None,
            "status": "connected"
        }
        logger.info(f"Nova conexão registrada: {session_id}")
    
    async def unregister_connection(self, session_id: str):
        """Remove conexão WebSocket"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.execution_sessions:
            self.execution_sessions[session_id]["status"] = "disconnected"
            self.execution_sessions[session_id]["end_time"] = datetime.now()
        logger.info(f"Conexão removida: {session_id}")
    
    async def send_message(self, session_id: str, message_type: str, data: Any):
        """Envia mensagem via WebSocket"""
        if session_id not in self.active_connections:
            logger.warning(f"Tentativa de envio para sessão inexistente: {session_id}")
            return
        
        try:
            message = {
                "type": message_type,
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "data": data
            }
            
            websocket = self.active_connections[session_id]
            await websocket.send(json.dumps(message))
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para {session_id}: {e}")
            await self.unregister_connection(session_id)
    
    def create_verbose_callback(self, session_id: str) -> Callable[[str], None]:
        """Cria callback para verbose em tempo real"""
        def verbose_callback(message: str):
            # Cria task assíncrona se houver loop rodando
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.send_message(session_id, "verbose", {"message": message}))
            except RuntimeError:
                # Se não há loop rodando, ignora o verbose
                print(f"VERBOSE: {message}")
        return verbose_callback
    
    async def execute_task_async(self, session_id: str, task_name: str, input_data: Optional[Dict] = None):
        """Executa task individual de forma assíncrona"""
        try:
            # Atualiza status da sessão
            if session_id in self.execution_sessions:
                self.execution_sessions[session_id]["current_task"] = task_name
                self.execution_sessions[session_id]["status"] = "executing"
            
            # Envia notificação de início
            await self.send_message(session_id, "task_start", {
                "task_name": task_name,
                "input_data": input_data
            })
            
            # Cria callback para verbose
            verbose_callback = self.create_verbose_callback(session_id)
            
            # Executa a task em thread separada para não bloquear o WebSocket
            def run_task():
                try:
                    return execute_individual_task(task_name, input_data, verbose_callback)
                except Exception as e:
                    raise e
            
            # Executa em executor para não bloquear
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_task)
            
            # Registra execução na sessão
            if session_id in self.execution_sessions:
                self.execution_sessions[session_id]["tasks_executed"].append({
                    "task_name": task_name,
                    "timestamp": datetime.now().isoformat(),
                    "input_data": input_data,
                    "result": result,
                    "status": "success"
                })
                self.execution_sessions[session_id]["current_task"] = None
                self.execution_sessions[session_id]["status"] = "waiting"
            
            # Envia resultado
            await self.send_message(session_id, "task_result", {
                "task_name": task_name,
                "result": result,
                "status": "success"
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Erro na execução da task {task_name}: {str(e)}"
            logger.error(f"Erro em execute_task_async: {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Registra erro na sessão
            if session_id in self.execution_sessions:
                self.execution_sessions[session_id]["tasks_executed"].append({
                    "task_name": task_name,
                    "timestamp": datetime.now().isoformat(),
                    "input_data": input_data,
                    "error": error_msg,
                    "status": "error"
                })
                self.execution_sessions[session_id]["current_task"] = None
                self.execution_sessions[session_id]["status"] = "error"
            
            # Envia erro
            await self.send_message(session_id, "error", {
                "task_name": task_name,
                "error": error_msg,
                "traceback": traceback.format_exc()
            })
            
            raise Exception(error_msg)
    
    async def handle_message(self, session_id: str, message: Dict[str, Any]):
        """Processa mensagens recebidas via WebSocket"""
        try:
            message_type = message.get("type")
            data = message.get("data", {})
            
            if message_type == "execute_task":
                task_name = data.get("task_name")
                input_data = data.get("input_data")
                
                if not task_name:
                    await self.send_message(session_id, "error", {
                        "error": "task_name é obrigatório"
                    })
                    return
                
                if task_name not in individual_tasks:
                    await self.send_message(session_id, "error", {
                        "error": f"Task {task_name} não encontrada. Tasks disponíveis: {list(individual_tasks.keys())}"
                    })
                    return
                
                # Executa a task
                await self.execute_task_async(session_id, task_name, input_data)
                
            elif message_type == "get_task_info":
                # Retorna informações sobre as tasks
                task_info = get_task_chain_info()
                await self.send_message(session_id, "task_info", task_info)
                
            elif message_type == "get_session_status":
                # Retorna status da sessão
                session_info = self.execution_sessions.get(session_id, {})
                await self.send_message(session_id, "session_status", session_info)
                
            elif message_type == "ping":
                # Responde ping
                await self.send_message(session_id, "pong", {"timestamp": datetime.now().isoformat()})
                
            else:
                await self.send_message(session_id, "error", {
                    "error": f"Tipo de mensagem desconhecido: {message_type}"
                })
                
        except Exception as e:
            error_msg = f"Erro ao processar mensagem: {str(e)}"
            logger.error(error_msg)
            await self.send_message(session_id, "error", {
                "error": error_msg,
                "traceback": traceback.format_exc()
            })
    
    async def websocket_handler(self, websocket: WebSocketServerProtocol, path: str):
        """Handler principal do WebSocket"""
        session_id = self.generate_session_id()
        
        try:
            # Registra conexão
            await self.register_connection(websocket, session_id)
            
            # Envia mensagem de boas-vindas
            await self.send_message(session_id, "connected", {
                "session_id": session_id,
                "available_tasks": list(individual_tasks.keys()),
                "message": "Conexão estabelecida com sucesso"
            })
            
            # Loop principal de mensagens
            async for message in websocket:
                try:
                    parsed_message = json.loads(message)
                    await self.handle_message(session_id, parsed_message)
                except json.JSONDecodeError:
                    await self.send_message(session_id, "error", {
                        "error": "Mensagem deve ser um JSON válido"
                    })
                except Exception as e:
                    logger.error(f"Erro no loop de mensagens: {e}")
                    await self.send_message(session_id, "error", {
                        "error": str(e)
                    })
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Conexão WebSocket fechada: {session_id}")
        except Exception as e:
            logger.error(f"Erro no websocket_handler: {e}")
        finally:
            await self.unregister_connection(session_id)
    
    async def start_server(self):
        """Inicia o servidor WebSocket"""
        logger.info(f"Iniciando servidor WebSocket Tropical em {self.host}:{self.port}")
        
        try:
            server = await websockets.serve(
                self.websocket_handler,
                self.host,
                self.port,
                ping_interval=30,
                ping_timeout=10
            )
            
            logger.info(f"✅ Servidor WebSocket iniciado em ws://{self.host}:{self.port}")
            logger.info("Tasks disponíveis:")
            for task_name in individual_tasks.keys():
                logger.info(f"  - {task_name}")
            
            # Mantém o servidor rodando
            await server.wait_closed()
            
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor: {e}")
            raise

# Cliente de teste simples
class TropicalWebSocketClient:
    def __init__(self, uri: str = "ws://localhost:5002"):
        self.uri = uri
        
    async def test_connection(self):
        """Testa conexão e execução de task"""
        try:
            async with websockets.connect(self.uri) as websocket:
                print(f"✅ Conectado ao servidor: {self.uri}")
                
                # Recebe mensagem de boas-vindas
                welcome = await websocket.recv()
                print(f"📨 Mensagem de boas-vindas: {json.loads(welcome)}")
                
                # Solicita informações das tasks
                await websocket.send(json.dumps({
                    "type": "get_task_info",
                    "data": {}
                }))
                
                task_info = await websocket.recv()
                print(f"📋 Informações das tasks: {json.loads(task_info)}")
                
                # Testa execução de read_email
                print("\n🚀 Testando execução de read_email...")
                await websocket.send(json.dumps({
                    "type": "execute_task",
                    "data": {
                        "task_name": "read_email",
                        "input_data": {"max_emails": 3}
                    }
                }))
                
                # Recebe mensagens (verbose + resultado)
                message_count = 0
                while message_count < 10:  # Limite para evitar loop infinito
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                        parsed = json.loads(message)
                        
                        if parsed["type"] == "verbose":
                            print(f"💬 Verbose: {parsed['data']['message']}")
                        elif parsed["type"] == "task_result":
                            print(f"✅ Resultado: {parsed['data']}")
                            break
                        elif parsed["type"] == "error":
                            print(f"❌ Erro: {parsed['data']}")
                            break
                        else:
                            print(f"📨 Mensagem: {parsed}")
                        
                        message_count += 1
                        
                    except asyncio.TimeoutError:
                        print("⏱️ Timeout aguardando resposta")
                        break
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WebSocket API Tropical')
    parser.add_argument('--mode', choices=['server', 'test'], default='server',
                        help='Modo de execução: server ou test')
    parser.add_argument('--host', default='localhost', help='Host do servidor')
    parser.add_argument('--port', type=int, default=5002, help='Porta do servidor')
    
    args = parser.parse_args()
    
    if args.mode == 'server':
        # Inicia servidor WebSocket
        api = TropicalWebSocketAPI(host=args.host, port=args.port)
        asyncio.run(api.start_server())
        
    elif args.mode == 'test':
        # Executa teste de cliente
        client = TropicalWebSocketClient(f"ws://{args.host}:{args.port}")
        asyncio.run(client.test_connection())

if __name__ == "__main__":
    main()