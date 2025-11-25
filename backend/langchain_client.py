# claude_code_api/langchain_client.py
"""
Cliente LangChain customizado para usar a API Claude Code
Compatível com LangChain e pode ser usado em qualquer chain/agent
"""

from langchain.llms.base import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from typing import Any, List, Optional, Dict
from pydantic import Field
import requests
import logging

logger = logging.getLogger(__name__)


class ClaudeCodeLLM(LLM):
    """
    LLM customizado para LangChain que usa a API Claude Code
    
    Exemplo de uso:
        llm = ClaudeCodeLLM(base_url="http://localhost:8000")
        response = llm("Explique recursão em Python")
    """
    
    base_url: str = Field(
        default="http://localhost:8000",
        description="URL base da API Claude Code"
    )
    
    model: str = Field(
        default="claude-code",
        description="Nome do modelo"
    )
    
    temperature: float = Field(
        default=0.7,
        description="Temperatura para geração (0.0 a 1.0)"
    )
    
    max_tokens: int = Field(
        default=4000,
        description="Máximo de tokens na resposta"
    )
    
    timeout: int = Field(
        default=120,
        description="Timeout em segundos"
    )
    
    @property
    def _llm_type(self) -> str:
        """Retorna tipo do LLM"""
        return "claude-code"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Executa chamada ao LLM
        
        Args:
            prompt: Prompt para enviar
            stop: Tokens de parada (não implementado)
            run_manager: Gerenciador de callbacks
            **kwargs: Argumentos adicionais
            
        Returns:
            Resposta do modelo
        """
        try:
            # Monta request OpenAI-compatible
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # Faz chamada à API
            logger.info(f"Chamando API Claude Code: {self.base_url}")
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            
            # Verifica erros HTTP
            response.raise_for_status()
            
            # Extrai resposta
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            logger.info(f"Resposta recebida: {len(content)} caracteres")
            
            return content
            
        except requests.exceptions.Timeout:
            error_msg = f"Timeout ao chamar API (>{self.timeout}s)"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        except requests.exceptions.ConnectionError:
            error_msg = f"Não foi possível conectar à API em {self.base_url}"
            logger.error(error_msg)
            raise RuntimeError(
                f"{error_msg}. Certifique-se de que a API está rodando."
            )
        
        except requests.exceptions.HTTPError as e:
            error_msg = f"Erro HTTP {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        except Exception as e:
            logger.error(f"Erro inesperado: {e}", exc_info=True)
            raise RuntimeError(f"Erro ao chamar API: {str(e)}")
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Retorna parâmetros identificadores do modelo"""
        return {
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }


# Exemplo de uso direto
if __name__ == "__main__":
    # Configuração de logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Cria instância do LLM
    llm = ClaudeCodeLLM(
        base_url="http://localhost:8000",
        temperature=0.7
    )
    
    # Teste simples
    print("\n" + "="*60)
    print("Testando ClaudeCodeLLM")
    print("="*60 + "\n")
    
    prompt = "Escreva uma função Python para calcular fibonacci recursivamente"
    
    print(f"Prompt: {prompt}\n")
    print("Aguardando resposta...\n")
    
    response = llm(prompt)
    
    print("Resposta:")
    print("-"*60)
    print(response)
    print("-"*60)
