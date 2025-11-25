#!/usr/bin/env python3
"""
Test with FULL actual prompt from the system to find where it breaks
"""

import os
from langchain_openai import ChatOpenAI

# Read actual document content from test
with open('/home/pasteurjr/progreact/langnet-interface/instancias/editais/entrevistas/resumo_Entrevista 251119 171944.pdf', 'rb') as f:
    # Simulate PDF extraction (simplified)
    pass

# Use the ACTUAL content from server logs
FULL_DOCUMENT = """
Douglas - Diretor Executivo da Farmac

PERFIL DA EMPRESA - FARMAC
Empresa familiar com quase 19 anos de atuação de Douglas
Foco principal: Distribuição de reagentes e equipamentos para laboratórios de análises clínicas
Atuação geográfica: Bahia, Sergipe e Alagoas (mercado principal)

Registros Anvisa: Aproximadamente 10.000 itens no portfólio
Busca manual individual de cada registro
Impacto financeiro severo em contratos de comodato (equipamentos + reagentes)
"""

INSTRUCTIONS = """
Proposta de Arquitetura do Sistema de IA para Licitações

1. Cadastro Inteligente do Portfólio
2. Agente de IA para Captura e Leitura dos Certames
3. Sugestão de Participação
4. Geração Automática da Proposta
"""

# This is the ACTUAL prompt template from langnet_tasks.yaml (simplified)
FULL_PROMPT_TEMPLATE = """
[Requirements Extraction] Extract requirements from DOCUMENTS + INSTRUCTIONS, then INFER technical needs.

YOU RECEIVE 3 INPUT SOURCES:

- document_content: {document_content}
- additional_instructions: {instructions}

YOUR TASK HAS 4 PARTS:
PART 1: Extract from DOCUMENTS
PART 2: Extract from INSTRUCTIONS
PART 3: INFER technical requirements
PART 4: Prepare for WEB RESEARCH

═══════════════════════════════════════════════════════════
PART 1: EXTRACT FROM DOCUMENTS (document_content)
═══════════════════════════════════════════════════════════

From ACTUAL TEXT in documents, extract requirements:

FUNCTIONAL REQUIREMENTS from documents:
- MANUAL TASK mentioned → FR to automate it
- PAIN POINT mentioned → FR to solve it
- DATA/ENTITY mentioned → CRUD FRs
- INTEGRATION mentioned → Integration FR
- WORKFLOW described → FRs for each step

For EACH FR from documents:
- Provide VERBATIM QUOTE as evidence
- Mark source: "from_document"

═══════════════════════════════════════════════════════════
FINAL VALIDATION - CHECKLIST BEFORE RETURNING OUTPUT
═══════════════════════════════════════════════════════════

Before generating your output, verify ALL items:

✓ I read and extracted requirements from document_content (not empty/placeholder)
✓ I read and extracted requirements from additional_instructions (not empty/placeholder)
✓ I inferred technical requirements (database, API, security, monitoring)
✓ Each FR from documents has VERBATIM QUOTE as evidence

RED FLAGS - DO NOT do this:
❌ Generic requirements like "user login" without context from documents
❌ Requirements with no source/evidence citation
❌ Invented stakeholders/companies not mentioned in documents

Return JSON with 5 functional requirements.
"""


def test_full_system_prompt():
    """Test with actual system prompt to see if it breaks"""

    print("="*80)
    print("TEST 2: FULL SYSTEM PROMPT (simulating actual workflow)")
    print("="*80)

    api_key = os.getenv("OPENAI_API_KEY", "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")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        max_tokens=4000,
        openai_api_key=api_key
    )

    prompt = FULL_PROMPT_TEMPLATE.format(
        document_content=FULL_DOCUMENT,
        instructions=INSTRUCTIONS
    )

    print(f"\n[PROMPT LENGTH]: {len(prompt)} chars")
    print(f"\n[CALLING LLM...]")

    response = llm.invoke(prompt)

    print("\n[RESPONSE]")
    print("="*80)
    print(response.content)
    print("="*80)

    # Check specificity
    content = response.content.lower()
    checks = {
        "Farmac": "farmac" in content,
        "10.000/10,000": any(x in content for x in ["10.000", "10,000", "10000"]),
        "ANVISA": "anvisa" in content,
        "Bahia/Sergipe": any(x in content for x in ["bahia", "sergipe"]),
        "comodato": "comodato" in content,
    }

    print("\n[SPECIFICITY CHECKS]")
    for name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {name}")

    passed_count = sum(checks.values())
    print(f"\n✅ Result: {passed_count}/{len(checks)} checks passed")

    if passed_count >= 3:
        print("\n✅ SYSTEM PROMPT PRESERVES SPECIFICITY")
        print("   Problem must be in CrewAI framework or output parsing")
    else:
        print("\n❌ SYSTEM PROMPT LOSES SPECIFICITY")
        print("   Prompt is too complex or confusing for LLM")

    return response.content


if __name__ == "__main__":
    test_full_system_prompt()
