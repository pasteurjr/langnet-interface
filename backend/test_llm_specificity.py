#!/usr/bin/env python3
"""
Test script to verify if gpt-4o-mini can extract specific requirements
Tests the LLM's ability to preserve specificity from documents
"""

import os
from langchain_openai import ChatOpenAI

# Sample document content with specific entities
DOCUMENT_SAMPLE = """
Douglas - Diretor Executivo da Farmac

PERFIL DA EMPRESA - FARMAC
Empresa familiar com quase 19 anos de atuação de Douglas
Foco principal: Distribuição de reagentes e equipamentos para laboratórios de análises clínicas
Atuação geográfica: Bahia, Sergipe e Alagoas (mercado principal)

DORES E DESAFIOS IDENTIFICADOS

4. Complexidade Documental
Registros Anvisa: Aproximadamente 10.000 itens no portfólio
Busca manual individual de cada registro
Impressão e anexação de PDFs um a um
Trabalho preventivo sem garantia de vitória

3. Modalidades de Contrato e Riscos
Impacto financeiro severo em contratos de comodato (equipamentos + reagentes)
"""

INSTRUCTIONS = """
Proposta de Arquitetura do Sistema de IA para Licitações

1. Cadastro Inteligente do Portfólio
Criação de uma máscara de entrada totalmente parametrizável.

2. Agente de IA para Captura e Leitura dos Certames
Um agente autônomo monitora diariamente as fontes públicas.
"""

PROMPT_TEMPLATE = """
Extract functional requirements from the following sources:

DOCUMENTS:
{document_content}

INSTRUCTIONS:
{instructions}

CRITICAL - SPECIFICITY REQUIREMENT:
Every requirement MUST include:
1. Specific entities mentioned in documents (company names, people names, locations)
2. Specific numbers/metrics from documents (volumes, counts, percentages)
3. Domain-specific terminology verbatim from documents

EXAMPLE - WRONG (too generic):
FR-001: System must handle large volumes efficiently
Evidence: "Large market with many companies"

EXAMPLE - CORRECT (specific):
FR-001: System must manage 10,000+ ANVISA product registrations for Farmac
Evidence: "Registros Anvisa: Aproximadamente 10.000 itens no portfólio"

Extract 5 functional requirements in JSON format:
{{
  "functional_requirements": [
    {{
      "id": "FR-001",
      "description": "...",
      "evidence": "verbatim quote from documents",
      "specificity_score": "generic|partial|specific"
    }}
  ]
}}

Return ONLY the JSON, no other text.
"""


def test_gpt4o_mini():
    """Test GPT-4o-mini's ability to preserve specificity"""

    print("="*80)
    print("TESTING GPT-4O-MINI SPECIFICITY")
    print("="*80)

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not set in environment")
        return None, None

    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        max_tokens=2000,
        openai_api_key=api_key
    )

    # Format prompt
    prompt = PROMPT_TEMPLATE.format(
        document_content=DOCUMENT_SAMPLE,
        instructions=INSTRUCTIONS
    )

    print("\n[PROMPT SENT]")
    print(f"Length: {len(prompt)} chars")
    print(f"\nFirst 500 chars of prompt:")
    print(prompt[:500])
    print("\n" + "="*80)

    # Invoke LLM
    print("\n[CALLING LLM...]")
    response = llm.invoke(prompt)

    print("\n[LLM RESPONSE]")
    print("="*80)
    print(response.content)
    print("="*80)

    # Analysis
    print("\n[ANALYSIS]")
    content = response.content.lower()

    checks = {
        "Mentions 'Farmac'": "farmac" in content,
        "Mentions '10.000' or '10,000'": "10.000" in content or "10,000" in content or "10000" in content,
        "Mentions 'ANVISA'": "anvisa" in content,
        "Mentions 'Bahia' or 'Sergipe'": "bahia" in content or "sergipe" in content,
        "Mentions 'Douglas'": "douglas" in content,
        "Mentions 'comodato'": "comodato" in content,
    }

    print("\nSpecificity Checks:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    passed_count = sum(checks.values())
    total_count = len(checks)

    print(f"\nResult: {passed_count}/{total_count} checks passed")

    if passed_count >= 4:
        print("\n✅ CONCLUSION: LLM CAN preserve specificity when given clear instructions")
        print("   Problem is likely elsewhere (prompt formatting, context length, etc.)")
    else:
        print("\n❌ CONCLUSION: LLM is NOT preserving specificity even with explicit instructions")
        print("   Need to either: (a) use stronger model, or (b) simplify prompt drastically")

    return response.content, checks


def test_gpt4_turbo():
    """Test GPT-4-turbo for comparison"""

    print("\n\n")
    print("="*80)
    print("TESTING GPT-4-TURBO SPECIFICITY (for comparison)")
    print("="*80)

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Skipping GPT-4-Turbo test (no API key)")
        return None, None

    try:
        llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3,
            max_tokens=2000,
            openai_api_key=api_key
        )

        prompt = PROMPT_TEMPLATE.format(
            document_content=DOCUMENT_SAMPLE,
            instructions=INSTRUCTIONS
        )

        print("\n[CALLING GPT-4-TURBO...]")
        response = llm.invoke(prompt)

        print("\n[GPT-4-TURBO RESPONSE]")
        print("="*80)
        print(response.content)
        print("="*80)

        # Analysis
        print("\n[ANALYSIS]")
        content = response.content.lower()

        checks = {
            "Mentions 'Farmac'": "farmac" in content,
            "Mentions '10.000' or '10,000'": "10.000" in content or "10,000" in content or "10000" in content,
            "Mentions 'ANVISA'": "anvisa" in content,
            "Mentions 'Bahia' or 'Sergipe'": "bahia" in content or "sergipe" in content,
            "Mentions 'Douglas'": "douglas" in content,
            "Mentions 'comodato'": "comodato" in content,
        }

        print("\nSpecificity Checks:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"{status} {check}")

        passed_count = sum(checks.values())
        print(f"\nResult: {passed_count}/{len(checks)} checks passed")

        return response.content, checks

    except Exception as e:
        print(f"\n❌ GPT-4-Turbo test failed: {e}")
        print("(Might not have access to this model)")
        return None, None


if __name__ == "__main__":
    print("🧪 LLM SPECIFICITY TEST\n")
    print("This script tests if the LLM can preserve specific details from documents")
    print("when extracting requirements.\n")

    # Test gpt-4o-mini
    mini_response, mini_checks = test_gpt4o_mini()

    # Test gpt-4-turbo for comparison (if available)
    turbo_response, turbo_checks = test_gpt4_turbo()

    print("\n\n")
    print("="*80)
    print("FINAL VERDICT")
    print("="*80)

    if mini_checks and sum(mini_checks.values()) >= 4:
        print("✅ GPT-4o-mini CAN handle specificity")
        print("   → Bug is NOT the LLM model")
        print("   → Look for: prompt truncation, context window issues, or parsing errors")
    else:
        print("❌ GPT-4o-mini CANNOT handle specificity reliably")
        print("   → Bug IS the LLM model being too weak")
        print("   → Solution: Use GPT-4 or GPT-4-turbo instead")

    if turbo_checks:
        print(f"\nGPT-4-Turbo comparison: {sum(turbo_checks.values())}/{len(turbo_checks)} checks")
