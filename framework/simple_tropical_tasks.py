"""
Versão simplificada do sistema de tasks tropicais para teste da WebSocket API
Sem dependências complexas do framework
"""

import json
from typing import Any, Dict, List, Union, Optional, Callable
from datetime import datetime

# Mock das classes necessárias para teste
class MockAgent:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

class MockTask:
    def __init__(self, name: str, description: str, agent: MockAgent):
        self.name = name
        self.description = description
        self.agent = agent
    
    def execute(self, input_data: Dict = None) -> Dict:
        """Mock da execução da task"""
        timestamp = datetime.now().isoformat()
        
        if self.name == "read_email":
            return {
                "timestamp": timestamp,
                "total_emails": 2,
                "emails": [
                    {
                        "email_id": "001",
                        "from": "cliente1@empresa.com",
                        "subject": "Pedido de produtos",
                        "content": "Preciso de 50 bombonas 20l para minha empresa",
                        "date": timestamp,
                        "status": "success"
                    },
                    {
                        "email_id": "002", 
                        "from": "cliente2@loja.com",
                        "subject": "Consulta preços",
                        "content": "Qual o preço de potes redondos?",
                        "date": timestamp,
                        "status": "success"
                    }
                ]
            }
        
        elif self.name == "classify_message":
            if not input_data or "emails" not in input_data:
                raise ValueError("classify_message requer emails de input")
            
            result = input_data.copy()
            for email in result["emails"]:
                if "bombona" in email["content"].lower():
                    email["categoria"] = "pedidos"
                    email["justificativa"] = "Email menciona produto com quantidade"
                    email["nome_produto_pedido"] = "bombona 20l"
                    email["quantidade_pedido"] = 50
                else:
                    email["categoria"] = "consultas_precos"
                    email["justificativa"] = "Email pergunta sobre preços"
                    email["nome_produto_pedido"] = "pote redondo"
                    email["quantidade_pedido"] = 0
            
            return result
        
        elif self.name == "check_stock_availability":
            if not input_data or "emails" not in input_data:
                raise ValueError("check_stock_availability requer emails classificados")
            
            # Filtra apenas emails de pedidos
            pedidos = [email for email in input_data["emails"] if email.get("categoria") == "pedidos"]
            
            result = {
                "timestamp": timestamp,
                "total_emails": len(pedidos),
                "emails": []
            }
            
            for email in pedidos:
                email_result = email.copy()
                if "bombona" in email.get("nome_produto_pedido", "").lower():
                    email_result["produto_escolhido"] = "Bombona Plastica 20L"
                    email_result["quantidade_disponivel"] = 75
                else:
                    email_result["produto_escolhido"] = "Produto Generico"
                    email_result["quantidade_disponivel"] = 10
                
                result["emails"].append(email_result)
            
            return result
        
        elif self.name == "generate_response":
            if not input_data or "emails" not in input_data:
                raise ValueError("generate_response requer emails com estoque verificado")
            
            relatorio = []
            for email in input_data["emails"]:
                relatorio.append(f"""## Email Original
- ID: {email.get('email_id', 'N/A')}
- De: {email.get('from', 'N/A')}
- Assunto: {email.get('subject', 'N/A')}
- Data: {email.get('date', 'N/A')}
- Produto Pedido: {email.get('nome_produto_pedido', 'N/A')}
- Quantidade Pedida: {email.get('quantidade_pedido', 'N/A')}
- Produto Disponível: {email.get('produto_escolhido', 'N/A')}
- Quantidade em Estoque: {email.get('quantidade_disponivel', 'N/A')}

### Resposta Enviada
- Para: {email.get('from', 'N/A')}
- Assunto: Resposta ao email: {email.get('subject', 'N/A')}
- Data Envio: {timestamp}
- Conteúdo: {"Prezado cliente. Informamos que seu pedido pode ser atendido. Aguarde retorno de nosso setor de vendas." if email.get('quantidade_disponivel', 0) >= email.get('quantidade_pedido', 0) else "Prezado cliente. Informamos que seu pedido não pode ser atendido no momento."}
""")
            
            return "\n\n".join(relatorio)
        
        else:
            raise ValueError(f"Task {self.name} não implementada")

# Criação dos agentes mock
email_reader_agent = MockAgent("email_reader_agent", "Responsável por ler emails não lidos")
classifier_agent = MockAgent("classifier_agent", "Classifica emails em categorias")
stock_checker_agent = MockAgent("stock_checker_agent", "Verifica disponibilidade em estoque")
response_generator_agent = MockAgent("response_generator_agent", "Gera respostas personalizadas")

# Criação das tasks mock
read_email_task = MockTask("read_email", "Buscar emails não lidos", email_reader_agent)
classify_message_task = MockTask("classify_message", "Classificar emails", classifier_agent)
check_stock_availability_task = MockTask("check_stock_availability", "Verificar estoque", stock_checker_agent)
generate_response_task = MockTask("generate_response", "Gerar respostas", response_generator_agent)

# Registry de tasks individuais para uso na Petri Net
individual_tasks = {
    "read_email": {
        "task": read_email_task,
        "agent": email_reader_agent,
        "tools": []
    },
    "classify_message": {
        "task": classify_message_task,
        "agent": classifier_agent,
        "tools": []
    },
    "check_stock_availability": {
        "task": check_stock_availability_task,
        "agent": stock_checker_agent,
        "tools": []
    },
    "generate_response": {
        "task": generate_response_task,
        "agent": response_generator_agent,
        "tools": []
    }
}

def execute_individual_task(task_name: str, input_data: dict = None, verbose_callback: Callable[[str], None] = None) -> dict:
    """
    Executa uma task individual para uso na Petri Net (versão mock)
    """
    if task_name not in individual_tasks:
        raise ValueError(f"Task {task_name} não encontrada. Tasks disponíveis: {list(individual_tasks.keys())}")
    
    task_info = individual_tasks[task_name]
    
    try:
        if verbose_callback:
            verbose_callback(f"[MOCK] Iniciando execução da task: {task_name}")
            verbose_callback(f"[MOCK] Input data: {json.dumps(input_data, indent=2) if input_data else 'None'}")
            verbose_callback(f"[MOCK] Agent: {task_info['agent'].name}")
        
        # Prepara inputs baseado no tipo de task
        if task_name == "read_email":
            # read_email não precisa de input_data específico
            if verbose_callback:
                verbose_callback("[MOCK] Conectando ao servidor IMAP...")
                verbose_callback("[MOCK] Buscando emails não lidos...")
                verbose_callback("[MOCK] Encontrados 2 emails para processar")
        else:
            # Outras tasks recebem o JSON da task anterior
            if not input_data:
                raise ValueError(f"Task {task_name} requer input_data da task anterior")
        
        if verbose_callback:
            verbose_callback(f"[MOCK] Executando task {task_name}...")
        
        # Executa a task mock
        result = task_info["task"].execute(input_data)
        
        if verbose_callback:
            verbose_callback(f"[MOCK] Task {task_name} executada com sucesso")
            verbose_callback(f"[MOCK] Resultado obtido")
        
        # Processa o resultado baseado no tipo de task
        if task_name == "generate_response":
            # generate_response retorna Markdown, não JSON
            return {
                "task_name": task_name,
                "result_type": "markdown",
                "result": result
            }
        else:
            # Outras tasks retornam JSON
            return {
                "task_name": task_name,
                "result_type": "json", 
                "result": result
            }
                
    except Exception as e:
        error_msg = f"Erro na execução da task {task_name}: {str(e)}"
        if verbose_callback:
            verbose_callback(f"[MOCK ERROR] {error_msg}")
        raise Exception(error_msg)

def get_task_chain_info() -> dict:
    """
    Retorna informações sobre a cadeia de tasks para debugging
    """
    return {
        "task_order": ["read_email", "classify_message", "check_stock_availability", "generate_response"],
        "input_requirements": {
            "read_email": "None ou {max_emails: int}",
            "classify_message": "JSON completo de read_email",
            "check_stock_availability": "JSON completo de classify_message", 
            "generate_response": "JSON completo de check_stock_availability"
        },
        "output_types": {
            "read_email": "JSON com emails brutos",
            "classify_message": "JSON com emails classificados",
            "check_stock_availability": "JSON com estoque verificado (apenas pedidos)",
            "generate_response": "Markdown com relatório final"
        },
        "mock_mode": True,
        "description": "Sistema mock para teste da WebSocket API Tropical"
    }

def test_task_chain():
    """
    Testa a execução das tasks em sequência
    """
    print("=== TESTE DA CADEIA DE TASKS MOCK ===")
    
    try:
        # 1. read_email
        print("\n1. Executando read_email...")
        result1 = execute_individual_task("read_email", {"max_emails": 5})
        print(f"Resultado: {result1['result_type']} com {len(result1['result']['emails'])} emails")
        
        # 2. classify_message
        print("\n2. Executando classify_message...")
        result2 = execute_individual_task("classify_message", result1["result"])
        print(f"Resultado: {result2['result_type']} com emails classificados")
        
        # 3. check_stock_availability
        print("\n3. Executando check_stock_availability...")
        result3 = execute_individual_task("check_stock_availability", result2["result"])
        print(f"Resultado: {result3['result_type']} com {len(result3['result']['emails'])} pedidos verificados")
        
        # 4. generate_response
        print("\n4. Executando generate_response...")
        result4 = execute_individual_task("generate_response", result3["result"])
        print(f"Resultado: {result4['result_type']} - relatório gerado")
        
        print("\n=== TESTE CONCLUÍDO COM SUCESSO ===")
        return True
        
    except Exception as e:
        print(f"\n=== ERRO NO TESTE: {e} ===")
        return False

if __name__ == "__main__":
    # Executa teste se executado diretamente
    test_task_chain()