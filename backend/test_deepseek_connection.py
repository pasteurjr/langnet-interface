"""
Test DeepSeek API connection before switching
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI

# Test parameters
API_KEY = "sk-6bd3d09d2fd441c0a14f767e38d9a3c5"
API_BASE = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-reasoner"

def test_connection():
    """Test basic connection to DeepSeek API"""
    print(f"{'='*60}")
    print(f"🧪 TESTE DE CONEXÃO DeepSeek API")
    print(f"{'='*60}\n")

    print(f"📋 Configuração:")
    print(f"   - Base URL: {API_BASE}")
    print(f"   - Model: {MODEL_NAME}")
    print(f"   - API Key: {API_KEY[:20]}...")
    print()

    try:
        # Create client
        print("🔌 Criando cliente OpenAI-compatible...")
        client = OpenAI(
            api_key=API_KEY,
            base_url=API_BASE
        )
        print("✅ Cliente criado com sucesso\n")

        # Test simple completion
        print("🤖 Testando completion simples...")
        print("   Prompt: 'Olá! Responda apenas: OK'")

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": "Olá! Responda apenas: OK"}
            ],
            max_tokens=100,
            temperature=0.3
        )

        # Extract response
        answer = response.choices[0].message.content.strip()
        print(f"   Resposta: '{answer}'\n")

        # Validate response
        if answer:
            print("✅ SUCESSO: DeepSeek respondeu corretamente!")
            print(f"\n📊 Detalhes da resposta:")
            print(f"   - Modelo usado: {response.model}")
            print(f"   - Tokens (prompt): {response.usage.prompt_tokens}")
            print(f"   - Tokens (completion): {response.usage.completion_tokens}")
            print(f"   - Tokens (total): {response.usage.total_tokens}")
            return True
        else:
            print("❌ ERRO: Resposta vazia do DeepSeek")
            return False

    except Exception as e:
        print(f"❌ ERRO na conexão:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        return False

    finally:
        print(f"\n{'='*60}")

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
