"""
Teste Diagnóstico Simples - Verificar funcionamento básico do sistema
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("=" * 80)
print("TESTE DIAGNÓSTICO SIMPLES")
print("=" * 80)

# Test 1: Check API keys
print("\n1. Verificando variáveis de ambiente...")
deepseek_key = os.getenv("DEEPSEEK_API_KEY")
serper_key = os.getenv("SERPER_API_KEY")
print(f"   DEEPSEEK_API_KEY: {'✅ SET' if deepseek_key else '❌ NOT SET'}")
print(f"   SERPER_API_KEY: {'✅ SET' if serper_key else '❌ NOT SET'}")

# Test 2: Import agents module
print("\n2. Importando módulo de agentes...")
try:
    from agents import langnetagents
    print("   ✅ Módulo importado com sucesso")
except Exception as e:
    print(f"   ❌ Erro ao importar: {e}")
    sys.exit(1)

# Test 3: Create a simple LLM instance
print("\n3. Criando instância LLM...")
try:
    llm = langnetagents.get_llm(use_deepseek=True)
    print(f"   ✅ LLM criado: {llm.model_name}")
except Exception as e:
    print(f"   ❌ Erro ao criar LLM: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Create a simple agent
print("\n4. Criando agente de teste...")
try:
    agent = langnetagents.get_agent("document_analyst", use_deepseek=True)
    print(f"   ✅ Agente criado: {agent.role if hasattr(agent, 'role') else 'OK'}")
except Exception as e:
    print(f"   ❌ Erro ao criar agente: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Check task registry
print("\n5. Verificando TASK_REGISTRY...")
try:
    task_count = len(langnetagents.TASK_REGISTRY)
    print(f"   ✅ {task_count} tarefas registradas")
    print(f"   Tarefas: {list(langnetagents.TASK_REGISTRY.keys())}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Test 6: Check agents in TASK_REGISTRY
print("\n6. Verificando agentes no TASK_REGISTRY...")
for task_name, task_config in langnetagents.TASK_REGISTRY.items():
    agent_ref = task_config.get("agent")
    print(f"   {task_name}: agent={agent_ref}")

# Test 7: Execute simple task
print("\n7. Testando execução de tarefa simples...")
print("   Criando state de teste...")
try:
    from agents.langnetstate import init_full_state

    test_state = init_full_state(
        project_id="test-001",
        document_id="doc-001",
        document_path="/tmp/test.pdf",
        project_name="Test Project",
        project_description="Test Description",
        project_domain="Test Domain"
    )
    test_state["use_deepseek"] = True
    test_state["document_content"] = "Test content"

    print("   ✅ State criado")
    print(f"   Chaves do state: {list(test_state.keys())[:10]}...")

except Exception as e:
    print(f"   ❌ Erro ao criar state: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Try to execute extract_requirements task
print("\n8. Testando extração de requisitos...")
try:
    result_state = langnetagents.execute_task_with_context(
        "extract_requirements",
        test_state,
        verbose_callback=lambda msg: print(f"      [TASK] {msg}")
    )

    print("   ✅ Tarefa executada")
    print(f"   Erros no state: {len(result_state.get('errors', []))}")
    if result_state.get('errors'):
        for err in result_state['errors']:
            print(f"      ❌ {err}")

except Exception as e:
    print(f"   ❌ Erro ao executar tarefa: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNÓSTICO COMPLETO")
print("=" * 80)
